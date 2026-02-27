from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from .openai_request import ChatMessage


class Usage(BaseModel):
    prompt_tokens: int = Field(..., ge=0)
    completion_tokens: int = Field(..., ge=0)
    total_tokens: int = Field(..., ge=0)

    model_config = ConfigDict(extra="forbid")


class Choice(BaseModel):
    index: int = 0
    message: ChatMessage
    finish_reason: str

    model_config = ConfigDict(extra="forbid")


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int = Field(..., ge=0)
    model: str
    choices: list[Choice] = Field(..., min_length=1)
    usage: Usage

    model_config = ConfigDict(extra="forbid")
