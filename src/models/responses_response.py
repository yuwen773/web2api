from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Optional


class ResponseOutputItem(BaseModel):
    """Responses API 输出项"""
    type: str = Field(..., pattern="^(text|tool_call|image)$")
    text: Optional[str] = None
    tool_use_id: Optional[str] = None
    name: Optional[str] = None
    arguments: Optional[str] = None

    model_config = ConfigDict(extra="forbid")


class ResponseUsage(BaseModel):
    """Responses API 使用量统计"""
    prompt_tokens: int = Field(..., ge=0)
    completion_tokens: int = Field(..., ge=0)
    total_tokens: int = Field(..., ge=0)

    model_config = ConfigDict(extra="forbid")


class ResponseObject(BaseModel):
    """Responses API 响应对象"""
    id: str
    object: str = Field(default="response", pattern="^response$")
    created: int = Field(..., ge=0)
    model: str
    status: str = Field(..., pattern="^(completed|failed|in_progress)$")
    output: list[ResponseOutputItem] = Field(default_factory=list)
    usage: ResponseUsage
    error: Optional[dict[str, Any]] = None

    model_config = ConfigDict(extra="forbid")
