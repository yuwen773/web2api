from __future__ import annotations

import os
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


def _run_non_stream_test(client: OpenAI, model: str) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "hello"}],
    )
    text = _extract_message_text(response)
    if not text:
        raise RuntimeError("Non-stream response is empty.")
    print(f"[non-stream] {text}")
    return text


def _run_stream_test(client: OpenAI, model: str) -> str:
    stream = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "hello"}],
        stream=True,
    )

    fragments: list[str] = []
    for chunk in stream:
        choices = getattr(chunk, "choices", None) or []
        if not choices:
            continue
        content = choices[0].delta.content
        if content:
            fragments.append(content)

    text = "".join(fragments).strip()
    if not text:
        raise RuntimeError("Stream response is empty.")
    print(f"[stream] {text}")
    return text


def _run_multi_turn_test(client: OpenAI, model: str) -> str:
    response = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {"role": "system", "content": "You are a precise assistant."},
            {"role": "user", "content": "Remember this: my codename is atlas."},
            {"role": "assistant", "content": "Understood. Your codename is atlas."},
            {
                "role": "user",
                "content": "What is my codename? Reply with one word only.",
            },
        ],
    )
    text = _extract_message_text(response)
    if "atlas" not in text.lower():
        raise RuntimeError(f"Multi-turn context check failed, got: {text!r}")
    print(f"[multi-turn] {text}")
    return text


def main() -> None:
    base_url = _normalize_openai_base_url(
        os.getenv("WEB2API_BASE_URL", "http://localhost:8000/v1")
    )
    api_key = os.getenv("WEB2API_API_KEY", "any")
    model = os.getenv("WEB2API_OPENAI_MODEL", "gpt-4.1-mini")

    client = OpenAI(base_url=base_url, api_key=api_key)
    _run_non_stream_test(client, model)
    _run_stream_test(client, model)
    _run_multi_turn_test(client, model)

    print("OpenAI SDK compatibility checks passed.")


if __name__ == "__main__":
    main()
