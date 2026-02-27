from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Literal, Optional, Union


class ResponseInputItem(BaseModel):
    """Responses API 输入项，支持文本/图像"""
    type: str = Field(default="text", pattern="^(text|image)$")
    text: Optional[str] = None
    image_url: Optional[str] = None

    model_config = ConfigDict(extra="forbid")


class ResponseTool(BaseModel):
    """Responses API 工具定义"""
    type: str = Field(..., pattern="^(function|web_search|file_search)$")
    name: Optional[str] = None
    description: Optional[str] = None
    parameters: Optional[dict[str, Any]] = None

    model_config = ConfigDict(extra="forbid")


class ResponseRequest(BaseModel):
    """Responses API 请求模型"""
    model: str = Field(..., min_length=1)
    input: Union[str, list[ResponseInputItem]] = Field(default="")
    instructions: Optional[str] = Field(default=None, max_length=8000)
    max_tokens: Optional[int] = Field(default=None, gt=0)
    tools: Optional[list[ResponseTool]] = None
    tool_choice: Optional[Union[str, dict[str, Any]]] = "auto"
    stream: bool = False
    temperature: Optional[float] = Field(default=None, ge=0, le=2)
    top_p: Optional[float] = Field(default=None, ge=0, le=1)
    background: bool = False
    previous_response_id: Optional[str] = None
    reasoning: Optional[dict[str, Any]] = None

    model_config = ConfigDict(extra="forbid")
