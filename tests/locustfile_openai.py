from __future__ import annotations

import os
import threading
import uuid
from typing import Any

from locust import HttpUser, between, task


def _read_positive_int_env(name: str, default: int) -> int:
    raw_value = os.getenv(name, str(default)).strip()
    try:
        value = int(raw_value)
    except ValueError:
        return default
    if value <= 0:
        return default
    return value


class _RequestLimiter:
    _lock = threading.Lock()
    _issued = 0
    _limit = _read_positive_int_env("WEB2API_STRESS_TOTAL_REQUESTS", 100)

    @classmethod
    def try_acquire_slot(cls) -> bool:
        with cls._lock:
            if cls._issued >= cls._limit:
                return False
            cls._issued += 1
            return True


def _extract_content_text(payload: dict[str, Any]) -> str:
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        return ""

    first_choice = choices[0]
    if not isinstance(first_choice, dict):
        return ""

    message = first_choice.get("message")
    if not isinstance(message, dict):
        return ""

    content = message.get("content")
    if content is None:
        return ""
    if isinstance(content, str):
        return content.strip()
    return str(content).strip()


class OpenAIChatCompletionUser(HttpUser):
    wait_time = between(0.01, 0.05)

    @task
    def create_chat_completion(self) -> None:
        if not _RequestLimiter.try_acquire_slot():
            if self.environment.runner is not None:
                self.environment.runner.quit()
            return

        model = os.getenv("WEB2API_OPENAI_MODEL", "gpt-4.1-mini")
        api_key = os.getenv("WEB2API_API_KEY", "any")
        marker = f"ctx-{uuid.uuid4().hex[:12]}"

        payload = {
            "model": model,
            "temperature": 0,
            "messages": [
                {
                    "role": "user",
                    "content": f"Remember this token exactly: {marker}.",
                },
                {
                    "role": "user",
                    "content": "Reply with only the token from the previous message.",
                },
            ],
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        with self.client.post(
            "/v1/chat/completions",
            name="POST /v1/chat/completions",
            json=payload,
            headers=headers,
            catch_response=True,
            timeout=120,
        ) as response:
            if response.status_code != 200:
                response.failure(f"HTTP {response.status_code}: {response.text[:200]}")
                return

            try:
                body = response.json()
            except ValueError:
                response.failure("Response body is not valid JSON.")
                return

            text = _extract_content_text(body)
            if marker not in text:
                response.failure(
                    "Context marker mismatch. "
                    f"Expected marker={marker!r}, actual_content={text!r}"
                )
                return

            response.success()
