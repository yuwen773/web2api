from __future__ import annotations

import asyncio
import os
import sys
from typing import Any

from openai import OpenAI


def _normalize_openai_base_url(raw_base_url: str) -> str:
    base_url = raw_base_url.strip().rstrip("/")
    if not base_url:
        raise ValueError("WEB2API_BASE_URL is empty.")
    if not base_url.endswith("/v1"):
        base_url = f"{base_url}/v1"
    return base_url


def _extract_message_text(response: Any) -> str:
    choices = getattr(response, "choices", None) or []
    if not choices:
        raise RuntimeError("OpenAI SDK response has no choices.")

    message = choices[0].message
    content = message.content
    if content is None:
        return ""
    if isinstance(content, str):
        return content.strip()
    return str(content).strip()


def _build_client(base_url: str, api_key: str) -> OpenAI:
    return OpenAI(base_url=base_url, api_key=api_key)


async def _create_completion(
    client: OpenAI,
    *,
    model: str,
    messages: list[dict[str, str]],
) -> str:
    response = await asyncio.to_thread(
        client.chat.completions.create,
        model=model,
        temperature=0,
        messages=messages,
    )
    text = _extract_message_text(response)
    if not text:
        raise RuntimeError("Completion is empty.")
    return text


async def _conversation_a(base_url: str, api_key: str, model: str) -> str:
    client = _build_client(base_url, api_key)

    first_user_message = "我叫小红，我喜欢编程。请只回答“收到”。"
    acknowledge = await _create_completion(
        client,
        model=model,
        messages=[{"role": "user", "content": first_user_message}],
    )

    final_answer = await _create_completion(
        client,
        model=model,
        messages=[
            {"role": "user", "content": first_user_message},
            {"role": "assistant", "content": acknowledge},
            {"role": "user", "content": "我叫什么名字？请只回复名字。"},
        ],
    )
    return final_answer


async def _conversation_b(base_url: str, api_key: str, model: str) -> str:
    client = _build_client(base_url, api_key)

    first_user_message = "我想学做菜。请只回答“收到”。"
    acknowledge = await _create_completion(
        client,
        model=model,
        messages=[{"role": "user", "content": first_user_message}],
    )

    final_answer = await _create_completion(
        client,
        model=model,
        messages=[
            {"role": "user", "content": first_user_message},
            {"role": "assistant", "content": acknowledge},
            {"role": "user", "content": "我想学什么？请只回复答案。"},
        ],
    )
    return final_answer


def _assert_context_isolation(answer_a: str, answer_b: str) -> None:
    errors: list[str] = []

    if "小红" not in answer_a:
        errors.append(f'Conversation A should include "小红", got: {answer_a!r}')
    if "做菜" in answer_a:
        errors.append(f'Conversation A should not include "做菜", got: {answer_a!r}')

    if "做菜" not in answer_b:
        errors.append(f'Conversation B should include "做菜", got: {answer_b!r}')
    if "小红" in answer_b:
        errors.append(f'Conversation B should not include "小红", got: {answer_b!r}')

    if errors:
        raise RuntimeError("Context isolation check failed:\n- " + "\n- ".join(errors))


async def _run(base_url: str, api_key: str, model: str) -> None:
    answer_a, answer_b = await asyncio.gather(
        _conversation_a(base_url, api_key, model),
        _conversation_b(base_url, api_key, model),
    )

    print(f"[conversation-a] {answer_a}")
    print(f"[conversation-b] {answer_b}")
    _assert_context_isolation(answer_a, answer_b)
    print("Context isolation check passed.")


def main() -> None:
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")

    base_url = _normalize_openai_base_url(
        os.getenv("WEB2API_BASE_URL", "http://localhost:8000/v1")
    )
    api_key = os.getenv("WEB2API_API_KEY", "any")
    model = os.getenv("WEB2API_OPENAI_MODEL", "gpt-4.1-mini")

    asyncio.run(_run(base_url, api_key, model))


if __name__ == "__main__":
    main()
