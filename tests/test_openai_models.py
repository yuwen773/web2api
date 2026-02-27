from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.models.openai_request import ChatCompletionRequest
from src.models.openai_response import ChatCompletionResponse


def test_chat_completion_request_validation_success() -> None:
    request = ChatCompletionRequest(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": "hello"}],
    )
    assert request.model == "gpt-4.1-mini"
    assert request.stream is False
    assert len(request.messages) == 1


def test_chat_completion_request_validation_error() -> None:
    with pytest.raises(ValidationError):
        ChatCompletionRequest(model="gpt-4.1-mini", messages=[])

    with pytest.raises(ValidationError):
        ChatCompletionRequest(
            model="gpt-4.1-mini",
            messages=[{"role": "user"}],
        )


def test_chat_completion_response_validation_success() -> None:
    response = ChatCompletionResponse(
        id="chatcmpl-123",
        created=1_740_000_000,
        model="gpt-4.1-mini",
        choices=[
            {
                "index": 0,
                "message": {"role": "assistant", "content": "hi"},
                "finish_reason": "stop",
            }
        ],
        usage={"prompt_tokens": 3, "completion_tokens": 5, "total_tokens": 8},
    )
    assert response.object == "chat.completion"
    assert response.usage.total_tokens == 8


def test_chat_completion_response_validation_error() -> None:
    with pytest.raises(ValidationError):
        ChatCompletionResponse(
            id="chatcmpl-123",
            created=1_740_000_000,
            model="gpt-4.1-mini",
            choices=[
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": "hi"},
                    "finish_reason": "stop",
                }
            ],
            usage={"prompt_tokens": -1, "completion_tokens": 5, "total_tokens": 4},
        )
