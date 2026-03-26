from __future__ import annotations

import time
from typing import Any

from fastapi import APIRouter, HTTPException, Request

from src.client.taiji_client import TaijiAPIError
from src.models.images_request import ImageGenerationsRequest, ImageCreateRequest
from src.utils.image_converter import extract_nano_banana_images, extract_gt4o_images
from src.utils.concurrency import get_semaphore
from src.utils.metrics_collector import get_metrics_collector
from src.utils.logging_config import get_logger


logger = get_logger(__name__)

router = APIRouter(prefix="/v1/images", tags=["images"])

# Nano-banana 模型映射 (label -> value)
NANO_BANANA_MODELS = {
    "Nano-banana绘图模型": "gemini-2.5-flash-image",
    "Nano-banana 2 绘图": "gemini-3.1-flash-image-preview",
}

# GT-4o-image-vip 模型 (label -> value)
GT4O_MODEL = "GT-4o-image-vip（绘图模型）"
GT4O_MODEL_VALUE = "gpt-4o-image-vip"


def _get_taiji_client(request: Request) -> Any:
    taiji_client = getattr(request.app.state, "taiji_client", None)
    if taiji_client is None:
        raise HTTPException(status_code=503, detail="Taiji client is not initialized.")
    return taiji_client


def _http_exception_from_taiji_error(error: TaijiAPIError) -> HTTPException:
    status_code = error.status_code or 502
    if status_code < 400 or status_code > 599:
        status_code = 502
    message = str(error) or "Taiji upstream request failed."
    return HTTPException(status_code=status_code, detail=message)


async def _create_session_or_raise(taiji_client: Any, model: str) -> int:
    try:
        return await taiji_client.create_session(model)
    except TaijiAPIError as exc:
        raise _http_exception_from_taiji_error(exc) from exc


async def _safe_delete_session(taiji_client: Any, session_id: int) -> None:
    try:
        await taiji_client.delete_session(session_id)
    except TaijiAPIError as exc:
        logger.warning("session_delete_failed", session_id=session_id, error=str(exc))


async def _generate_images(
    taiji_client: Any,
    model_value: str,
    prompt: str,
    n: int,
    ratio: str,
    extract_fn: Any,
) -> dict[str, Any]:
    """共享的图片生成逻辑"""
    session_id = await _create_session_or_raise(taiji_client, model_value)

    try:
        text = f"帮我生成标题为\"{prompt}\"的 {n} 张 封面图，比例为 '{ratio}'"

        images = []
        async with get_semaphore():
            async for chunk in taiji_client.send_message(session_id, text, files=[], stream=True):
                if isinstance(chunk, dict) and chunk.get("type") == "string":
                    chunk_data = chunk.get("data")
                    if isinstance(chunk_data, str):
                        extracted = extract_fn(chunk_data)
                        images.extend(extracted)

        if not images:
            raise HTTPException(status_code=500, detail="No images generated")

        # 记录图片生成指标
        get_metrics_collector().record_image_generated(
            model=model_value,
            count=len(images),
        )

        return {
            "created": int(time.time()),
            "data": [{"url": url} for url in images],
        }
    except TaijiAPIError as exc:
        raise _http_exception_from_taiji_error(exc) from exc
    finally:
        await _safe_delete_session(taiji_client, session_id)


@router.post("/generations", response_model=None)
async def create_image_generation(
    request: ImageGenerationsRequest,
    http_request: Request,
) -> Any:
    """Nano-banana 绘图接口"""
    if request.model not in NANO_BANANA_MODELS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported model: {request.model}. Available: {list(NANO_BANANA_MODELS.keys())}",
        )

    taiji_client = _get_taiji_client(http_request)
    model_value = NANO_BANANA_MODELS[request.model]

    return await _generate_images(
        taiji_client=taiji_client,
        model_value=model_value,
        prompt=request.prompt,
        n=request.n,
        ratio=request.ratio,
        extract_fn=extract_nano_banana_images,
    )


@router.post("/create", response_model=None)
async def create_image(
    request: ImageCreateRequest,
    http_request: Request,
) -> Any:
    """GT-4o-image-vip 绘图接口"""
    if request.model != GT4O_MODEL:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported model: {request.model}. Available: {GT4O_MODEL}",
        )

    taiji_client = _get_taiji_client(http_request)

    return await _generate_images(
        taiji_client=taiji_client,
        model_value=GT4O_MODEL_VALUE,
        prompt=request.prompt,
        n=request.n,
        ratio=request.ratio,
        extract_fn=extract_gt4o_images,
    )
