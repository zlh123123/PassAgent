"""Markdown 记忆档案：解析、渲染与存储辅助。"""
from __future__ import annotations

import re
from collections.abc import Iterable, Mapping

from sqlalchemy.orm import Session as DBSession

from database.models import UserMemoryProfile

MEMORY_SECTION_ORDER = ("PREFERENCE", "FACT", "CONSTRAINT")
MEMORY_SECTION_LABELS = {
    "PREFERENCE": "偏好",
    "FACT": "事实",
    "CONSTRAINT": "约束",
}
MEMORY_LABEL_TO_TYPE = {label: key for key, label in MEMORY_SECTION_LABELS.items()}
MAX_ITEMS_PER_SECTION = 8


def _now_iso() -> str:
    from utils.timezone import beijing_now_iso
    return beijing_now_iso()


def empty_memory_sections() -> dict[str, list[str]]:
    return {memory_type: [] for memory_type in MEMORY_SECTION_ORDER}


def _clean_item(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", (text or "").strip())
    if cleaned.startswith("- "):
        cleaned = cleaned[2:].strip()
    return cleaned


def normalize_memory_sections(
    sections: Mapping[str, Iterable[str]] | None,
) -> dict[str, list[str]]:
    normalized = empty_memory_sections()

    for memory_type in MEMORY_SECTION_ORDER:
        seen: set[str] = set()
        for raw_item in (sections or {}).get(memory_type, []):
            item = _clean_item(str(raw_item))
            if not item or item in seen:
                continue
            normalized[memory_type].append(item)
            seen.add(item)
            if len(normalized[memory_type]) >= MAX_ITEMS_PER_SECTION:
                break

    return normalized


def parse_memory_profile(content_md: str | None) -> tuple[dict[str, list[str]], bool]:
    """将 markdown 文本解析成固定的三段式结构。"""
    sections = empty_memory_sections()
    current_type: str | None = None
    saw_known_heading = False

    for raw_line in (content_md or "").splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if line.startswith("#"):
            heading = line.lstrip("#").strip()
            heading_upper = heading.upper()
            if heading_upper in MEMORY_SECTION_ORDER:
                current_type = heading_upper
                saw_known_heading = True
            elif heading in MEMORY_LABEL_TO_TYPE:
                current_type = MEMORY_LABEL_TO_TYPE[heading]
                saw_known_heading = True
            else:
                current_type = None
            continue

        if current_type and line.startswith("- "):
            sections[current_type].append(_clean_item(line[2:]))

    return normalize_memory_sections(sections), saw_known_heading


def render_memory_profile(sections: Mapping[str, Iterable[str]] | None = None) -> str:
    """将结构化记忆渲染成规范 markdown。"""
    normalized = normalize_memory_sections(sections)
    lines = [
        "# 用户记忆",
        "",
        "以下内容仅保留稳定、长期有用且尽量简短的个人信息。",
        "",
    ]

    for memory_type in MEMORY_SECTION_ORDER:
        lines.append(f"## {MEMORY_SECTION_LABELS[memory_type]}")
        for item in normalized[memory_type]:
            lines.append(f"- {item}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def normalize_memory_profile_content(content_md: str | None) -> str:
    """校验并规范化记忆 markdown。"""
    if not content_md or not content_md.strip():
        return render_memory_profile()

    sections, saw_heading = parse_memory_profile(content_md)
    if not saw_heading:
        raise ValueError("记忆文档格式无效，请保留“偏好 / 事实 / 约束”标题")

    return render_memory_profile(sections)


def memory_sections_to_payload(sections: Mapping[str, Iterable[str]]) -> list[dict]:
    normalized = normalize_memory_sections(sections)
    return [
        {
            "memory_type": memory_type,
            "label": MEMORY_SECTION_LABELS[memory_type],
            "items": normalized[memory_type],
        }
        for memory_type in MEMORY_SECTION_ORDER
    ]


def ensure_memory_profile(db: DBSession, user_id: str) -> UserMemoryProfile:
    profile = (
        db.query(UserMemoryProfile)
        .filter(UserMemoryProfile.user_id == user_id)
        .first()
    )
    if profile is not None:
        return profile

    now = _now_iso()
    profile = UserMemoryProfile(
        user_id=user_id,
        content_md=render_memory_profile(),
        created_at=now,
        updated_at=now,
        last_used_at=None,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def save_memory_profile_content(
    db: DBSession,
    profile: UserMemoryProfile,
    content_md: str,
) -> tuple[UserMemoryProfile, bool]:
    normalized = normalize_memory_profile_content(content_md)
    changed = normalized != (profile.content_md or "")
    if not changed:
        return profile, False

    profile.content_md = normalized
    profile.updated_at = _now_iso()
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile, True


def touch_memory_profile(db: DBSession, profile: UserMemoryProfile) -> None:
    profile.last_used_at = _now_iso()
    db.add(profile)
    db.commit()
