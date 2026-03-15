"""Skills 注册表：自动从 SKILL.md frontmatter 发现和注册 Skills

每个 Skill 是一个目录，包含 SKILL.md 文件（必需）和可选的 reference/scripts。
SKILL.md 的 YAML frontmatter 定义了 name、description、allowed-tools 等元数据。
"""
from __future__ import annotations

import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

# Skill 目录所在路径
_SKILLS_DIR = Path(__file__).parent

# 每个 skill 都自动包含的通用工具
UTILITY_TOOLS = ["respond", "retrieve_memory"]


def _parse_frontmatter(content: str) -> dict:
    """解析 SKILL.md 中的 YAML frontmatter（简易解析，不依赖 PyYAML）。

    支持格式：
    ---
    name: skill-name
    description: 这个 Skill 做什么
    allowed-tools: tool1,tool2,tool3
    ---
    """
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return {}

    meta = {}
    for line in match.group(1).strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        colon_idx = line.find(":")
        if colon_idx == -1:
            continue
        key = line[:colon_idx].strip()
        value = line[colon_idx + 1:].strip()
        meta[key] = value

    return meta


def _parse_tools(tools_str: str) -> list[str]:
    """将 allowed-tools 字段解析为工具名列表。"""
    return [t.strip() for t in tools_str.split(",") if t.strip()]


def _discover_skills() -> dict[str, dict]:
    """扫描 skills 目录，自动发现并注册所有 Skill。

    返回 {skill_name: {"tools": [...], "description": "...", "skill_dir": Path, ...}}
    """
    registry: dict[str, dict] = {}

    for skill_dir in sorted(_SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir():
            continue

        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue

        content = skill_md.read_text(encoding="utf-8")
        meta = _parse_frontmatter(content)

        name = meta.get("name")
        if not name:
            logger.warning("Skill %s 缺少 name，跳过", skill_dir.name)
            continue

        description = meta.get("description", "")
        tools = _parse_tools(meta.get("allowed-tools", ""))

        registry[name] = {
            "tools": tools,
            "description": description,
            "skill_dir": skill_dir,
            "skill_md": skill_md,
        }
        logger.debug("注册 Skill: %s (tools=%s)", name, tools)

    return registry


# ---------------------------------------------------------------------------
# 模块级注册表（import 时自动发现）
# ---------------------------------------------------------------------------
SKILL_REGISTRY: dict[str, dict] = _discover_skills()

# 所有合法的 skill 名称（含特殊值）
VALID_SKILLS = set(SKILL_REGISTRY.keys()) | {"off_topic", "multi_skill"}


def load_skill_prompt(skill_name: str) -> str:
    """加载指定 skill 的 SKILL.md 内容（去掉 frontmatter 部分）。"""
    if skill_name not in SKILL_REGISTRY:
        return ""
    skill_md = SKILL_REGISTRY[skill_name]["skill_md"]
    if not skill_md.exists():
        return ""

    content = skill_md.read_text(encoding="utf-8")

    # 去掉 frontmatter，只返回正文
    match = re.match(r"^---\s*\n.*?\n---\s*\n", content, re.DOTALL)
    if match:
        return content[match.end():].strip()
    return content.strip()


def list_skills_summary() -> str:
    """返回所有 skill 的简要摘要（供 intent_router 使用）。"""
    lines = []
    for name, info in SKILL_REGISTRY.items():
        lines.append(f"- **{name}**: {info['description']}")
    return "\n".join(lines)
