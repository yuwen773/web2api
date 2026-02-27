from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AnthropicImageSource(BaseModel):
    type: str = Field(..., min_length=1)
    media_type: str | None = None
    data: str | None = None
    url: str | None = None

    model_config = ConfigDict(extra="allow")


class AnthropicContentBlock(BaseModel):
    type: str = Field(..., min_length=1)
    text: str | None = None
    source: AnthropicImageSource | None = None
    image_url: str | dict[str, Any] | None = None

    model_config = ConfigDict(extra="allow")


class AnthropicMessage(BaseModel):
    role: str = Field(..., min_length=1)
    content: str | list[AnthropicContentBlock]

    model_config = ConfigDict(extra="allow")


class AnthropicRequest(BaseModel):
    model: str = Field(..., min_length=1)
    max_tokens: int = Field(default=4096, gt=0)
    messages: list[AnthropicMessage] = Field(..., min_length=1)
    system: str | list[AnthropicContentBlock] | None = None
    stream: bool = False

    model_config = ConfigDict(extra="allow")
