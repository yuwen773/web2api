from __future__ import annotations

import base64
import mimetypes
from pathlib import PurePosixPath
from urllib.parse import unquote, urlparse

import httpx


ROLE_PREFIX = {
    "system": "系统提示",
    "user": "用户",
    "assistant": "助手",
}


async def convert_openai_messages(
    messages: list[dict[str, object]],
    model: str,
    *,
    http_client: httpx.AsyncClient | None = None,
    timeout: float = 20.0,
) -> dict[str, object]:
    """Convert OpenAI-style messages to Taiji prompt text and upload files."""
    _ = model  # Phase 1.5 requires this argument; reserved for model-specific behavior.

    if not isinstance(messages, list):
        raise ValueError("messages must be a list.")

    own_client = http_client is None
    client = http_client or httpx.AsyncClient(timeout=timeout, follow_redirects=True)

    try:
        prompt_lines: list[str] = []
        files: list[dict[str, str]] = []
        processed: list[tuple[str, str, bool]] = []

        for raw_message in messages:
            if not isinstance(raw_message, dict):
                raise ValueError("Each message must be a dictionary.")

            role = str(raw_message.get("role") or "user").strip().lower()
            content = raw_message.get("content")
            message_text, message_files = await _extract_message_parts(
                content,
                client=client,
                start_index=len(files) + 1,
            )
            files.extend(message_files)
            processed.append((role, message_text, bool(message_files)))

        # Fast path: if request is a single user message, send plain text directly.
        if len(processed) == 1:
            role, text, _ = processed[0]
            if role == "user":
                return {"text": text, "files": files}

        for role, text, has_images in processed:
            prefix = ROLE_PREFIX.get(role, role or "消息")
            if text:
                prompt_lines.append(f"{prefix}：{text}")
            elif has_images:
                prompt_lines.append(f"{prefix}：[图片]")

        return {
            "text": "\n".join(prompt_lines).strip(),
            "files": files,
        }
    finally:
        if own_client:
            await client.aclose()


async def _extract_message_parts(
    content: object,
    *,
    client: httpx.AsyncClient,
    start_index: int,
) -> tuple[str, list[dict[str, str]]]:
    if isinstance(content, str):
        return content.strip(), []

    if isinstance(content, list):
        text_parts: list[str] = []
        files: list[dict[str, str]] = []
        file_index = start_index

        for part in content:
            if isinstance(part, str):
                stripped = part.strip()
                if stripped:
                    text_parts.append(stripped)
                continue

            if not isinstance(part, dict):
                continue

            part_type = str(part.get("type") or "").strip().lower()
            if part_type == "text":
                text = part.get("text")
                if isinstance(text, str) and text.strip():
                    text_parts.append(text.strip())
                continue

            if part_type == "image_url":
                image_url = _extract_image_url(part.get("image_url"))
                if not image_url:
                    continue
                files.append(
                    await _image_url_to_file(
                        image_url=image_url,
                        file_index=file_index,
                        client=client,
                    )
                )
                file_index += 1

        return "\n".join(text_parts).strip(), files

    return "", []


def _extract_image_url(value: object) -> str | None:
    if isinstance(value, str):
        return value.strip() or None

    if isinstance(value, dict):
        url = value.get("url")
        if isinstance(url, str) and url.strip():
            return url.strip()

    return None


async def _image_url_to_file(
    *,
    image_url: str,
    file_index: int,
    client: httpx.AsyncClient,
) -> dict[str, str]:
    if image_url.startswith("data:image/"):
        mime_type = _mime_from_data_url(image_url)
        extension = mimetypes.guess_extension(mime_type) or ".png"
        return {
            "name": f"image_{file_index}{extension}",
            "data": image_url,
        }

    parsed = urlparse(image_url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError(f"Unsupported image URL scheme: {parsed.scheme!r}")

    response = await client.get(image_url)
    response.raise_for_status()

    mime_type = _resolve_mime_type(response.headers.get("content-type"), parsed.path)
    if not mime_type.startswith("image/"):
        raise ValueError(f"Image URL did not return an image content type: {mime_type!r}")

    filename = _build_filename(parsed.path, mime_type, file_index)
    encoded = base64.b64encode(response.content).decode("ascii")
    return {
        "name": filename,
        "data": f"data:{mime_type};base64,{encoded}",
    }


def _mime_from_data_url(data_url: str) -> str:
    if "," not in data_url:
        raise ValueError("Invalid data URL: missing payload separator.")

    header, _ = data_url.split(",", 1)
    mime_type = header[5:].split(";", 1)[0].strip().lower()
    if not mime_type.startswith("image/"):
        raise ValueError(f"Data URL is not an image: {mime_type!r}")
    return mime_type


def _resolve_mime_type(content_type: str | None, path: str) -> str:
    header_mime = ""
    if content_type:
        header_mime = content_type.split(";", 1)[0].strip().lower()
        if header_mime.startswith("image/"):
            return header_mime

    guessed, _ = mimetypes.guess_type(path)
    if isinstance(guessed, str):
        return guessed.lower()

    if header_mime:
        return header_mime
    return "image/png"


def _build_filename(path: str, mime_type: str, file_index: int) -> str:
    candidate = unquote(PurePosixPath(path).name)
    if not candidate:
        extension = mimetypes.guess_extension(mime_type) or ".png"
        return f"image_{file_index}{extension}"

    if "." in candidate:
        return candidate

    extension = mimetypes.guess_extension(mime_type) or ".png"
    return f"{candidate}{extension}"
