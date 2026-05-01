"""PassInfinity / graphical-mode 相关的轻量意图判断。"""
from __future__ import annotations

_GRAPHICAL_EXACT_KEYWORDS = (
    "passinfinity",
    "图形口令",
    "图形密码",
    "图片密码",
    "图片选点",
    "图片记忆点",
    "图片因子",
    "图像因子",
    "地图密码",
    "位置密码",
    "地理位置因子",
    "地图位置因子",
    "富文本标记",
    "文本标记",
    "样式标记",
)

_IMAGE_EXACT_KEYWORDS = (
    "图片密码",
    "图片选点",
    "图片记忆点",
    "图片因子",
    "图像因子",
)
_MAP_EXACT_KEYWORDS = (
    "地图密码",
    "位置密码",
    "地理位置因子",
    "地图位置因子",
)
_RICHTEXT_EXACT_KEYWORDS = (
    "富文本标记",
    "文本标记",
    "样式标记",
)

_IMAGE_CONTEXT_ANCHORS = (
    "设密码",
    "设口令",
    "做密码",
    "做口令",
    "作为密码",
    "记忆点",
    "因子",
    "图形口令",
)
_MAP_CONTEXT_ANCHORS = (
    "设密码",
    "设口令",
    "做密码",
    "做口令",
    "作为密码",
    "因子",
    "地理位置",
    "图形口令",
)
_GENERIC_EXCLUSIONS = (
    "上传",
    "解析",
    "识别",
    "分析",
    "提取",
    "ocr",
    "读图",
    "根据图片生成",
    "根据文本生成",
    "分析这段文本",
)


def _normalize_text(text: str) -> str:
    return (text or "").strip().lower()


def _is_generic_image_graphical(text: str) -> bool:
    return (
        ("图片" in text or "图像" in text)
        and any(anchor in text for anchor in _IMAGE_CONTEXT_ANCHORS)
        and not any(keyword in text for keyword in _GENERIC_EXCLUSIONS)
    )


def _is_generic_map_graphical(text: str) -> bool:
    return (
        "地图" in text
        and any(anchor in text for anchor in _MAP_CONTEXT_ANCHORS)
        and not any(keyword in text for keyword in _GENERIC_EXCLUSIONS)
    )


def infer_graphical_mode(text: str) -> str | None:
    """根据文本推断 PassInfinity 具体模式。"""
    lowered = _normalize_text(text)
    if not lowered:
        return None

    if any(keyword in lowered for keyword in _IMAGE_EXACT_KEYWORDS) or _is_generic_image_graphical(lowered):
        return "image"
    if any(keyword in lowered for keyword in _MAP_EXACT_KEYWORDS) or _is_generic_map_graphical(lowered):
        return "map"
    if any(keyword in lowered for keyword in _RICHTEXT_EXACT_KEYWORDS):
        return "richtext"
    return None


def is_graphical_intent_text(text: str) -> bool:
    """判断文本是否明确在谈 PassInfinity / 图形口令体验。"""
    lowered = _normalize_text(text)
    if not lowered:
        return False
    if any(keyword in lowered for keyword in _GRAPHICAL_EXACT_KEYWORDS):
        return True
    return infer_graphical_mode(lowered) is not None
