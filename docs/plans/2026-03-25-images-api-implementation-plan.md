# 图片生成 API 实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 为 web2api 新增两个图片生成接口 `/v1/images/generations` 和 `/v1/images/create`

**Architecture:** 新增 `src/api/images.py` 处理图片生成请求，使用现有 TaijiClient 发送请求，解析 SSE 响应提取图片 URL

**Tech Stack:** FastAPI, Pydantic, httpx, 正则表达式

---

## Task 1: 创建图片请求数据模型

**Files:**
- Create: `src/models/images_request.py`
- Modify: `src/models/__init__.py`

**Step 1: 创建数据模型**

```python
from pydantic import BaseModel, Field
from typing import Literal

class ImageGenerationsRequest(BaseModel):
    """Nano-banana 绘图请求 /v1/images/generations"""
    model: str = Field(..., description="模型名称，如 'Nano-banana 2 绘图'")
    prompt: str = Field(..., description="图片描述")
    n: int = Field(default=1, ge=1, le=10, description="生成数量")
    ratio: Literal["1:1", "3:2", "3:4", "4:3", "9:16", "16:9"] = Field(
        default="1:1", description="图片比例"
    )

class ImageCreateRequest(BaseModel):
    """GT-4o-image-vip 绘图请求 /v1/images/create"""
    model: str = Field(..., description="模型名称，如 'GT-4o-image-vip（绘图模型）'")
    prompt: str = Field(..., description="图片描述")
    n: int = Field(default=1, ge=1, le=10, description="生成数量")
    ratio: Literal["1:1", "3:2", "3:4", "4:3", "9:16", "16:9"] = Field(
        default="1:1", description="图片比例"
    )
```

**Step 2: 更新 __init__.py**

在 `src/models/__init__.py` 中添加导出：
```python
from .images_request import ImageGenerationsRequest, ImageCreateRequest
```

**Step 3: 提交**

```bash
git add src/models/images_request.py src/models/__init__.py
git commit -m "feat: add image generation request models"
```

---

## Task 2: 创建图片转换工具

**Files:**
- Create: `src/utils/image_converter.py`

**Step 1: 创建响应解析工具**

```python
import re
from typing import List

def extract_nano_banana_images(sse_data: str) -> List[str]:
    """从 Nano-banana SSE 响应中提取图片 URL"""
    # 匹配 ![image](url) 格式
    pattern = r'!\[image\]\((https?://[^\s)]+)\)'
    return re.findall(pattern, sse_data)

def extract_gt4o_images(sse_data: str) -> List[str]:
    """从 GT-4o-image-vip SSE 响应中提取图片 URL"""
    # 匹配 ![gen_xxx](url) 格式
    pattern = r'!\[gen_[^\]]*\]\((https?://[^\s)]+)\)'
    return re.findall(pattern, sse_data)
```

**Step 2: 提交**

```bash
git add src/utils/image_converter.py
git commit -m "feat: add image response converter utilities"
```

---

## Task 3: 创建图片 API 端点

**Files:**
- Create: `src/api/images.py`
- Modify: `main.py`

**Step 1: 创建 images.py**

```python
from fastapi import APIRouter, HTTPException
from src.models.images_request import ImageGenerationsRequest, ImageCreateRequest
from src.utils.image_converter import extract_nano_banana_images, extract_gt4o_images
from src.client.taiji_client import TaijiClient
from src.utils.settings import get_settings
import time

router = APIRouter(prefix="/v1/images", tags=["images"])

# Nano-banana 模型映射
NANO_BANANA_MODELS = {
    "Nano-banana绘图模型": "gemini-2.5-flash-image",
    "Nano-banana 2 绘图": "gemini-3.1-flash-image-preview",
}

# GT-4o-image-vip 模型
GT4O_MODEL = "GT-4o-image-vip（绘图模型）"

@router.post("/generations")
async def create_image_generation(request: ImageGenerationsRequest):
    """Nano-banana 绘图接口"""
    if request.model not in NANO_BANANA_MODELS:
        raise HTTPException(status_code=400, detail=f"Unsupported model: {request.model}")

    client: TaijiClient = app.state.taiji_client

    # 构建 prompt
    text = f"帮我生成标题为\"{request.prompt}\"的 {request.n} 张 封面图,比例为 '{request.ratio}'"

    # 创建会话
    model_value = NANO_BANANA_MODELS[request.model]
    session = await client.create_session(model_value)
    session_id = session.get("session_id")

    try:
        # 发送请求
        async with client._semaphore:
            async for chunk in client.send_message(session_id, text, files=[]):
                # 解析 SSE chunk，提取图片 URL
                images = extract_nano_banana_images(chunk)
                if images:
                    return {
                        "created": int(time.time()),
                        "data": [{"url": url} for url in images]
                    }
    finally:
        await client.delete_session(session_id)

@router.post("/create")
async def create_image(request: ImageCreateRequest):
    """GT-4o-image-vip 绘图接口"""
    if request.model != GT4O_MODEL:
        raise HTTPException(status_code=400, detail=f"Unsupported model: {request.model}")

    client: TaijiClient = app.state.taiji_client

    # 构建 prompt
    text = f"帮我生成标题为\"{request.prompt}\"的 {request.n} 张 封面图，比例为 '{request.ratio}'"

    # 创建会话
    session = await client.create_session(GT4O_MODEL)
    session_id = session.get("session_id")

    try:
        async with client._semaphore:
            async for chunk in client.send_message(session_id, text, files=[]):
                # 解析 SSE chunk，提取图片 URL
                images = extract_gt4o_images(chunk)
                if images:
                    return {
                        "created": int(time.time()),
                        "data": [{"url": url} for url in images]
                    }
    finally:
        await client.delete_session(session_id)
```

**Step 2: 在 main.py 注册路由**

在 `main.py` 中添加：
```python
from src.api.images import router as images_router
app.include_router(images_router)
```

**Step 3: 提交**

```bash
git add src/api/images.py main.py
git commit -m "feat: add images API endpoints (generations, create)"
```

---

## Task 4: 添加测试

**Files:**
- Create: `tests/test_images_api.py`

**Step 1: 编写测试**

```python
import pytest
from src.utils.image_converter import extract_nano_banana_images, extract_gt4o_images

def test_extract_nano_banana_images():
    sse_data = '''
    data: {"id":"...","type":"string","data":"\\n\\n![image](https://cn-nb1.rains3.com/jay/xxx.jpg)\\n","code":0}
    '''
    images = extract_nano_banana_images(sse_data)
    assert len(images) == 1
    assert "cn-nb1.rains3.com" in images[0]

def test_extract_gt4o_images():
    sse_data = '''
    data: {"id":"...","type":"string","data":"\\n\\n![gen_01kmjacvgnfwx8zbnfm28amn46](https://pro.filesystem.site/cdn/xxx.png)\\n","code":0}
    '''
    images = extract_gt4o_images(sse_data)
    assert len(images) == 1
    assert "pro.filesystem.site" in images[0]
```

**Step 2: 运行测试**

```bash
pytest tests/test_images_api.py -v
```

**Step 3: 提交**

```bash
git add tests/test_images_api.py
git commit -m "test: add images API tests"
```

---

## 执行方式

**Plan complete and saved to `docs/plans/2026-03-25-images-api-implementation-plan.md`**

两个执行选项：

**1. Subagent-Driven (this session)** - 我dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

**Which approach?**
