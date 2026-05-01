import asyncio
import unittest
from types import SimpleNamespace

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from agent.memory.profile import (
    ensure_memory_profile,
    normalize_memory_profile_content,
    parse_memory_profile,
    render_memory_profile,
    save_memory_profile_content,
)
from agent.memory.reader import retrieve_memory
from database.models import Base
from routers.memory import (
    add_memory_item,
    clear_memory_profile,
    promote_memory_item,
)
from schemas.memory import MemoryItemRequest, PromoteMemoryItemRequest


class MemorySystemTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
        )
        Base.metadata.create_all(bind=self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.db = self.SessionLocal()
        self.user = SimpleNamespace(user_id="user-test")

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def test_legacy_profile_normalizes_into_manual_source(self):
        legacy_content = """# 用户记忆

## 偏好
- 偏好 14-16 位口令

## 事实
- 常用昵称是 Ling

## 约束
- 学校系统不接受空格
"""

        sections, saw_heading = parse_memory_profile(legacy_content)
        self.assertTrue(saw_heading)
        self.assertEqual(sections["MANUAL"]["PREFERENCE"], ["偏好 14-16 位口令"])
        self.assertEqual(sections["MANUAL"]["FACT"], ["常用昵称是 Ling"])
        self.assertEqual(sections["MANUAL"]["CONSTRAINT"], ["学校系统不接受空格"])
        self.assertEqual(sections["AUTO"]["PREFERENCE"], [])

        normalized = normalize_memory_profile_content(legacy_content)
        self.assertIn("## 用户手动添加", normalized)
        self.assertIn("## Agent 自动提炼", normalized)

    def test_manual_duplicate_removes_auto_copy(self):
        content = render_memory_profile(
            {
                "MANUAL": {
                    "PREFERENCE": [],
                    "FACT": ["宠物叫哈吉米"],
                    "CONSTRAINT": [],
                },
                "AUTO": {
                    "PREFERENCE": [],
                    "FACT": ["宠物叫哈吉米", "常把宠物名当记忆线索"],
                    "CONSTRAINT": [],
                },
            }
        )
        sections, _ = parse_memory_profile(content)

        self.assertEqual(sections["AUTO"]["FACT"], ["常把宠物名当记忆线索"])

    def test_add_and_retrieve_manual_memory_returns_manual_source(self):
        add_memory_item(
            MemoryItemRequest(
                content="偏好 14-16 位口令",
                memory_type="PREFERENCE",
                source="MANUAL",
            ),
            user=self.user,
            db=self.db,
        )

        memories = asyncio.run(retrieve_memory(self.db, self.user.user_id, "生成 GitHub 密码"))
        self.assertTrue(any(m["source"] == "MANUAL" for m in memories))
        self.assertTrue(
            any(
                m["memory_type"] == "PREFERENCE"
                and m["content"] == "偏好 14-16 位口令"
                for m in memories
            )
        )

    def test_retrieve_facts_prioritizes_manual_and_skips_irrelevant_query(self):
        profile_content = render_memory_profile(
            {
                "MANUAL": {
                    "PREFERENCE": [],
                    "FACT": ["宠物叫哈吉米"],
                    "CONSTRAINT": [],
                },
                "AUTO": {
                    "PREFERENCE": [],
                    "FACT": ["宠物叫哈吉米的名字经常被用来记忆", "常用平台是 GitHub"],
                    "CONSTRAINT": [],
                },
            }
        )
        profile = ensure_memory_profile(self.db, self.user.user_id)
        save_memory_profile_content(self.db, profile, profile_content)

        matched = asyncio.run(retrieve_memory(self.db, self.user.user_id, "哈吉米"))
        fact_memories = [m for m in matched if m["memory_type"] == "FACT"]
        self.assertTrue(fact_memories)
        self.assertEqual(fact_memories[0]["source"], "MANUAL")

        irrelevant = asyncio.run(retrieve_memory(self.db, self.user.user_id, "企业邮箱策略"))
        self.assertEqual([m for m in irrelevant if m["memory_type"] == "FACT"], [])

    def test_promote_and_clear_scope_keep_manual_and_auto_separate(self):
        add_memory_item(
            MemoryItemRequest(
                content="经常把宠物名字当记忆线索",
                memory_type="FACT",
                source="AUTO",
            ),
            user=self.user,
            db=self.db,
        )
        add_memory_item(
            MemoryItemRequest(
                content="偏好 14-16 位口令",
                memory_type="PREFERENCE",
                source="MANUAL",
            ),
            user=self.user,
            db=self.db,
        )

        promote_memory_item(
            PromoteMemoryItemRequest(
                content="经常把宠物名字当记忆线索",
                memory_type="FACT",
            ),
            user=self.user,
            db=self.db,
        )

        profile = ensure_memory_profile(self.db, self.user.user_id)
        sections, _ = parse_memory_profile(profile.content_md)
        self.assertIn("经常把宠物名字当记忆线索", sections["MANUAL"]["FACT"])
        self.assertNotIn("经常把宠物名字当记忆线索", sections["AUTO"]["FACT"])

        add_memory_item(
            MemoryItemRequest(
                content="更接受容易手输的口令",
                memory_type="PREFERENCE",
                source="AUTO",
            ),
            user=self.user,
            db=self.db,
        )

        clear_memory_profile(scope="auto", user=self.user, db=self.db)
        profile = ensure_memory_profile(self.db, self.user.user_id)
        sections, _ = parse_memory_profile(profile.content_md)
        self.assertEqual(sections["AUTO"]["PREFERENCE"], [])
        self.assertIn("偏好 14-16 位口令", sections["MANUAL"]["PREFERENCE"])


if __name__ == "__main__":
    unittest.main()
