"""PassInfinity 体验页服务：规范化、编码、策略校验和存储转换。"""
from __future__ import annotations

import json
import uuid

from database.models import PassInfinityArtifact


DEFAULT_POLICY = {
    "GLOBAL": {
        "enable": False,
        "minTypeNum": 2,
        "excludeType": ["text"],
    },
    "insertImage": {
        "enable": True,
        "minNum": 1,
        "minPassPoint": 1,
    },
    "location": {
        "enable": True,
        "minNum": 1,
    },
    "richText": {
        "enable": True,
        "minTypeNum": 1,
    },
    "text": {
        "enable": True,
        "minNum": 1,
    },
}

STYLE_TAGS = {
    "bold": ("<strong>", "</strong>"),
    "italic": ("<i>", "</i>"),
    "underline": ("<u>", "</u>"),
    "strikethrough": ("<s>", "</s>"),
}


def get_default_policy() -> dict:
    return DEFAULT_POLICY


def _clamp_ratio(value: float) -> float:
    return max(0.0, min(1.0, round(value, 4)))


def _normalize_title(title: str) -> str:
    clean = title.strip()
    return clean or "未命名体验"


def normalize_draft(payload: dict) -> dict:
    text = str(payload.get("text", "")).strip()
    rich_text = payload.get("rich_text", {}) or {}
    rich_content = str(rich_text.get("content", "")).strip()
    rich_styles = [
        style for style in rich_text.get("styles", [])
        if style in STYLE_TAGS
    ]

    images: list[dict] = []
    for raw_image in payload.get("images", []) or []:
        points: list[dict] = []
        for raw_point in raw_image.get("points", []) or []:
            points.append({
                "x": _clamp_ratio(float(raw_point.get("x", 0))),
                "y": _clamp_ratio(float(raw_point.get("y", 0))),
                "kind": "grid" if raw_point.get("kind") == "grid" else "passpoint",
            })

        images.append({
            "image_id": str(raw_image.get("image_id", uuid.uuid4().hex)),
            "title": str(raw_image.get("title", "")).strip(),
            "src": str(raw_image.get("src", "")).strip(),
            "tags": [str(tag).strip() for tag in raw_image.get("tags", []) if str(tag).strip()],
            "use_grid": bool(raw_image.get("use_grid", False)),
            "points": points,
        })

    locations: list[dict] = []
    for raw_location in payload.get("locations", []) or []:
        locations.append({
            "location_id": str(raw_location.get("location_id", uuid.uuid4().hex)),
            "label": str(raw_location.get("label", "")).strip(),
            "lat": round(float(raw_location.get("lat", 0)), 4),
            "lng": round(float(raw_location.get("lng", 0)), 4),
        })

    return {
        "title": _normalize_title(str(payload.get("title", ""))),
        "text": text,
        "rich_text": {
            "content": rich_content,
            "styles": rich_styles,
        },
        "images": images,
        "locations": locations,
    }


def encode_draft(normalized: dict) -> str:
    parts: list[str] = []

    if normalized["text"]:
        parts.append(normalized["text"])

    rich_content = normalized["rich_text"]["content"]
    if rich_content:
        wrapped = rich_content
        for style in normalized["rich_text"]["styles"]:
            opening, closing = STYLE_TAGS[style]
            wrapped = f"{opening}{wrapped}{closing}"
        parts.append(wrapped)

    for image in normalized["images"]:
        if not image["src"]:
            continue
        point_chunks = []
        for point in image["points"]:
            point_type = "gp" if image["use_grid"] or point["kind"] == "grid" else "pp"
            x = int(point["x"] * 1000)
            y = int(point["y"] * 1000)
            point_chunks.append([point_type, 1 if image["src"].startswith("http") else 0, x, y])
        tag_suffix = f"#tags{{{','.join(image['tags'])}}}" if image["tags"] else ""
        title_attr = f' data-title="{image["title"]}"' if image["title"] else ""
        encoded_points = f"#insertimage{json.dumps(point_chunks, ensure_ascii=False)}"
        parts.append(
            f'<img src="{image["src"]}" class="passinfinity-image"{title_attr}>'
            f"{encoded_points}{tag_suffix}"
        )

    for location in normalized["locations"]:
        label_suffix = f":{location['label']}" if location["label"] else ""
        parts.append(
            f"#location[{location['lat']},{location['lng']}]{label_suffix}"
        )

    return "\n".join(parts).strip()


def validate_draft(normalized: dict) -> dict:
    warnings: list[str] = []
    factors_used: list[str] = []

    text = normalized["text"]
    rich_content = normalized["rich_text"]["content"]
    rich_styles = normalized["rich_text"]["styles"]
    images = normalized["images"]
    locations = normalized["locations"]

    if text:
        factors_used.append("text")
    if rich_content:
        factors_used.append("richText")
        if not rich_styles:
            warnings.append("富文本内容已填写，但尚未使用样式标记。")

    valid_images = 0
    total_image_points = 0
    for image in images:
        if image["src"]:
            valid_images += 1
            total_image_points += len(image["points"])
            if len(image["points"]) == 0:
                warnings.append(
                    f"图片因子「{image['title'] or image['image_id']}」还没有选点。"
                )
        else:
            warnings.append("存在未配置图片源的图片因子。")

    if valid_images:
        factors_used.append("insertImage")

    if locations:
        factors_used.append("location")

    valid = bool(factors_used)
    if not valid:
        warnings.append("至少添加一种认证因子后才能生成体验结果。")

    if valid_images and total_image_points == 0:
        valid = False

    if locations and len(locations) < DEFAULT_POLICY["location"]["minNum"]:
        valid = False
        warnings.append("至少需要保留一个地图位置因子。")

    factor_counts = {
        "text": 1 if text else 0,
        "richText": 1 if rich_content else 0,
        "insertImage": valid_images,
        "imagePoints": total_image_points,
        "location": len(locations),
    }

    summary = "体验方案已满足基础要求。" if valid else "体验方案还不完整，建议补充后再保存。"

    return {
        "valid": valid,
        "summary": summary,
        "warnings": warnings,
        "factors_used": factors_used,
        "factor_counts": factor_counts,
    }


def analyze_draft(payload: dict) -> dict:
    normalized = normalize_draft(payload)
    encoded_text = encode_draft(normalized)
    policy_result = validate_draft(normalized)
    return {
        "normalized_content": normalized,
        "encoded_text": encoded_text,
        "policy_result": policy_result,
    }


def infer_builder_mode(normalized: dict) -> str:
    if normalized.get("images"):
        return "image"
    if normalized.get("locations"):
        return "map"
    return "richtext"


def artifact_to_response(artifact: PassInfinityArtifact) -> dict:
    normalized = json.loads(artifact.content_json)
    return {
        "artifact_id": artifact.artifact_id,
        "title": artifact.title,
        "normalized_content": normalized,
        "encoded_text": artifact.encoded_text,
        "policy_result": json.loads(artifact.policy_result_json),
        "created_at": artifact.created_at,
        "updated_at": artifact.updated_at,
    }
