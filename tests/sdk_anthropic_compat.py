from __future__ import annotations

import os
from typing import Any

from anthropic import Anthropic


def _normalize_anthropic_base_url(raw_base_url: str) -> str:
    base_url = raw_base_url.strip().rstrip("/")
    if not base_url:
        raise ValueError("WEB2API_BASE_URL is empty.")
    return base_url


def _extract_text_from_message(message: Any) -> str:
    content_blocks = getattr(message, "content", None) or []
    texts: list[str] = []
    for block in content_blocks:
        if getattr(block, "type", "") != "text":
            continue
        text = getattr(block, "text", "")
        if text:
            texts.append(str(text))
    return "".join(texts).strip()


def main() -> None:
    base_url = _normalize_anthropic_base_url(
        os.getenv("WEB2API_BASE_URL", "http://localhost:8000")
    )
    api_key = os.getenv("WEB2API_API_KEY", "any")
    model = os.getenv("WEB2API_ANTHROPIC_MODEL", "claude-opus-4-6")
    max_tokens = int(os.getenv("WEB2API_ANTHROPIC_MAX_TOKENS", "1024"))

    client = Anthropic(base_url=base_url, api_key=api_key)
    message = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": "hello"}],
    )

    text = _extract_text_from_message(message)
    if not text:
        raise RuntimeError("Anthropic SDK response is empty.")

    import sys
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
    print(f"[anthropic] {text}")
    print("Anthropic SDK compatibility checks passed.")


if __name__ == "__main__":
    main()
