from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class RichTextPayload(BaseModel):
    content: str = ""
    styles: list[Literal["bold", "italic", "underline", "strikethrough"]] = Field(
        default_factory=list
    )


class ImagePointPayload(BaseModel):
    x: float
    y: float
    kind: Literal["passpoint", "grid"] = "passpoint"


class ImageFactorPayload(BaseModel):
    image_id: str
    title: str = ""
    src: str
    tags: list[str] = Field(default_factory=list)
    use_grid: bool = False
    points: list[ImagePointPayload] = Field(default_factory=list)


class LocationFactorPayload(BaseModel):
    location_id: str
    label: str = ""
    lat: float
    lng: float


class PassInfinityDraftRequest(BaseModel):
    title: str = "未命名体验"
    text: str = ""
    rich_text: RichTextPayload = Field(default_factory=RichTextPayload)
    images: list[ImageFactorPayload] = Field(default_factory=list)
    locations: list[LocationFactorPayload] = Field(default_factory=list)


class PassInfinityPolicyResponse(BaseModel):
    policy: dict


class PassInfinityAnalyzeResponse(BaseModel):
    normalized_content: dict
    encoded_text: str
    policy_result: dict


class PassInfinityArtifactResponse(BaseModel):
    artifact_id: str
    title: str
    normalized_content: dict
    encoded_text: str
    policy_result: dict
    created_at: str | None = None
    updated_at: str | None = None


class PassInfinityArtifactListResponse(BaseModel):
    artifacts: list[PassInfinityArtifactResponse]
