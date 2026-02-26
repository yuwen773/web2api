from __future__ import annotations

import base64

import httpx
import pytest

from src.utils.message_converter import convert_openai_messages


@pytest.mark.asyncio
async def test_convert_single_user_message_fast_path() -> None:
    result = await convert_openai_messages(
        messages=[{"role": "user", "content": "hello"}],
        model="gpt-4.1-mini",
    )
    assert result == {"text": "hello", "files": []}


@pytest.mark.asyncio
async def test_convert_multi_turn_messages_to_prefixed_prompt() -> None:
    result = await convert_openai_messages(
        messages=[
            {"role": "system", "content": "你是助手"},
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好，我在"},
            {"role": "user", "content": "继续"},
        ],
        model="gpt-4.1-mini",
    )
    assert result["files"] == []
    assert result["text"] == "系统提示：你是助手\n用户：你好\n助手：你好，我在\n用户：继续"


@pytest.mark.asyncio
async def test_convert_message_with_data_url_image() -> None:
    data_url = "data:image/png;base64,aGVsbG8="
    result = await convert_openai_messages(
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "看图"},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            }
        ],
        model="gpt-4.1-mini",
    )

    assert result["text"] == "看图"
    files = result["files"]
    assert isinstance(files, list)
    assert len(files) == 1
    assert files[0]["data"] == data_url
    assert files[0]["name"].endswith(".png")


@pytest.mark.asyncio
async def test_convert_message_with_http_image_url() -> None:
    image_bytes = b"\x89PNG\r\n\x1a\nmock"

    def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == "https://example.com/cat.png"
        return httpx.Response(
            status_code=200,
            content=image_bytes,
            headers={"content-type": "image/png"},
        )

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
    ) as mock_client:
        result = await convert_openai_messages(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "识别图片"},
                        {"type": "image_url", "image_url": {"url": "https://example.com/cat.png"}},
                    ],
                }
            ],
            model="gpt-4.1-mini",
            http_client=mock_client,
        )

    files = result["files"]
    assert isinstance(files, list)
    assert len(files) == 1
    assert result["text"] == "识别图片"
    assert files[0]["name"] == "cat.png"
    assert files[0]["data"] == f"data:image/png;base64,{base64.b64encode(image_bytes).decode('ascii')}"


@pytest.mark.asyncio
async def test_convert_message_rejects_non_http_image_url() -> None:
    with pytest.raises(ValueError):
        await convert_openai_messages(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": "ftp://example.com/cat.png"}},
                    ],
                }
            ],
            model="gpt-4.1-mini",
        )
