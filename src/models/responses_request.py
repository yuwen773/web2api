from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Any, Literal, Optional, Union


class ResponseInputItem(BaseModel):
    """Responses API 输入项，支持文本/图像

    Codex 兼容：使用 extra="ignore" 忽略未知字段
    """
    type: str = Field(default="text")  # 移除 pattern 限制，接受任意类型
    text: Optional[str] = None
    image_url: Optional[str] = None

    model_config = ConfigDict(extra="ignore")


class ResponseTool(BaseModel):
    """Responses API 工具定义

    支持的工具类型:
    - function: 函数调用
    - code_interpreter: 代码解释器
    - retrieval: 检索
    - web_search: 网络搜索
    - file_search: 文件搜索
    """
    type: str  # 临时移除 pattern 限制，调试用
    name: Optional[str] = None
    description: Optional[str] = None
    parameters: Optional[dict[str, Any]] = None
    strict: Optional[bool] = None  # OpenAI 2025+ 支持，用于强制模型遵守 schema
    format: Any = None  # 可能是字符串、null 或其他类型

    # 移除 extra="forbid"，使用 ignore 自动忽略未知字段（如 external_web_access 等）
    model_config = ConfigDict(extra="ignore")


class ResponseRequest(BaseModel):
    """Responses API 请求模型

    input 字段支持多种格式:
    - 字符串: "hello"
    - 对象: {"str": "hello"}  (Codex 兼容)
    - 列表: [{"type": "text", "text": "hello"}]
    """
    model: str = Field(..., min_length=1)
    input: Any = ""  # 使用 Any 接受任何格式，在业务逻辑中处理
    instructions: Optional[str] = None
    max_tokens: Optional[int] = Field(default=None, gt=0)
    tools: Optional[list[ResponseTool]] = None
    tool_choice: Optional[Union[str, dict[str, Any]]] = "auto"
    parallel_tool_calls: Optional[bool] = None  # 是否允许并行调用工具
    store: Optional[bool] = None  # 是否存储对话
    stream: bool = False
    temperature: Optional[float] = Field(default=None, ge=0, le=2)
    top_p: Optional[float] = Field(default=None, ge=0, le=1)
    background: bool = False
    previous_response_id: Optional[str] = None
    reasoning: Optional[dict[str, Any]] = None

    # 使用 ignore 自动忽略未知字段，兼容 Codex 扩展字段
    model_config = ConfigDict(extra="ignore")
