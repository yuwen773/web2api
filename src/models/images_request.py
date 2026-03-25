from pydantic import BaseModel, Field
from typing import Literal

# 共享的 ratio 类型
RatioLiteral = Literal["1:1", "3:2", "3:4", "4:3", "9:16", "16:9"]


class ImageGenerationsRequest(BaseModel):
    """Nano-banana 绘图请求 /v1/images/generations"""
    model: str = Field(..., description="模型名称，如 'Nano-banana 2 绘图'")
    prompt: str = Field(..., description="图片描述")
    n: int = Field(default=1, ge=1, le=10, description="生成数量")
    ratio: RatioLiteral = Field(default="1:1", description="图片比例")


class ImageCreateRequest(ImageGenerationsRequest):
    """GT-4o-image-vip 绘图请求 /v1/images/create"""
    pass
