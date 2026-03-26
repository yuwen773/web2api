#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Taiji AI Image Generator

Usage:
    python taiji_image.py generate --model "Nano-banana 2 绘图" --prompt "封面图" --n 2 --ratio "16:9"
    python taiji_image.py --help
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sys
from typing import Any

# 优先使用本地独立客户端
from taiji_client import TaijiClient, TaijiAPIError

# 模型映射
NANO_BANANA_MODELS = {
    "Nano-banana绘图模型": "gemini-2.5-flash-image",
    "Nano-banana 2 绘图": "gemini-3.1-flash-image-preview",
}

GT4O_MODEL = "GT-4o-image-vip（绘图模型）"
GT4O_MODEL_VALUE = "gpt-4o-image-vip"

ALL_MODELS = list(NANO_BANANA_MODELS.keys()) + [GT4O_MODEL]

# URL 提取正则
NANO_BANANA_PATTERN = r'!\[image\]\((https?://[^\s)]+)\)'
GT4O_PATTERN = r'!\[gen_[^\]]*\]\((https?://[^\s)]+)\)'


def get_credentials(skill_dir: str) -> dict[str, Any]:
    """从 assets/credentials.json 读取配置"""
    cred_path = os.path.join(skill_dir, "assets", "credentials.json")
    if not os.path.exists(cred_path):
        raise RuntimeError(f"credentials.json not found at {cred_path}")

    with open(cred_path, encoding="utf-8") as f:
        cred = json.load(f)

    base_url = cred.get("base_url", "https://ai.aurod.cn").rstrip("/")
    account = cred.get("account", "")
    password = cred.get("password", "")
    app_version = cred.get("app_version", "2.14.0")

    if not account or not password:
        raise RuntimeError("credentials.json 中 account 和 password 不能为空")

    return {
        "base_url": base_url,
        "account": account,
        "password": password,
        "app_version": app_version,
    }


def resolve_model_value(model_name: str) -> str:
    """解析模型名称为实际模型值"""
    if model_name in NANO_BANANA_MODELS:
        return NANO_BANANA_MODELS[model_name]
    if model_name == GT4O_MODEL:
        return GT4O_MODEL_VALUE
    raise RuntimeError(
        f"不支持的模型: {model_name}。可用模型: {ALL_MODELS}"
    )


def get_url_pattern(model_name: str) -> str:
    """获取模型对应的 URL 提取正则"""
    if model_name in NANO_BANANA_MODELS:
        return NANO_BANANA_PATTERN
    if model_name == GT4O_MODEL:
        return GT4O_PATTERN
    raise RuntimeError(f"不支持的模型: {model_name}")


async def generate_images(
    model: str,
    prompt: str,
    n: int = 1,
    ratio: str = "1:1",
    skill_dir: str | None = None,
) -> list[str]:
    """
    生成图片并返回 URL 列表

    Args:
        model: 模型名称
        prompt: 图片描述
        n: 生成数量
        ratio: 图片比例
        skill_dir: skill 目录路径

    Returns:
        图片 URL 列表
    """
    if skill_dir is None:
        skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    cred = get_credentials(skill_dir)

    model_value = resolve_model_value(model)
    url_pattern = get_url_pattern(model)

    prompt_text = f'帮我生成标题为"{prompt}"的 {n} 张封面图，比例为 \'{ratio}\''

    async with TaijiClient(
        base_url=cred["base_url"],
        app_version=cred["app_version"],
    ) as client:
        await client.login(cred["account"], cred["password"])
        session_id = await client.create_session(model_value)
        try:
            images: list[str] = []
            stream = client.send_message(session_id, prompt_text, stream=True)
            async for chunk in stream:
                chunk_type = chunk.get("type")
                if chunk_type == "string":
                    chunk_data = chunk.get("data")
                    if isinstance(chunk_data, str):
                        found = re.findall(url_pattern, chunk_data)
                        images.extend(found)

            if not images:
                raise RuntimeError("未生成任何图片")

            return images
        finally:
            await client.delete_session(session_id)


async def main_async(args: argparse.Namespace) -> None:
    """异步主函数"""
    try:
        images = await generate_images(
            model=args.model,
            prompt=args.prompt,
            n=args.n,
            ratio=args.ratio,
        )
        for url in images:
            print(url)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Taiji AI 图片生成工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
可用模型:
  Nano-banana绘图模型     gemini-2.5-flash-image
  Nano-banana 2 绘图      gemini-3.1-flash-image-preview
  GT-4o-image-vip（绘图模型）  gpt-4o-image-vip

可用比例: 1:1, 3:2, 3:4, 4:3, 9:16, 16:9

示例:
  python taiji_image.py generate --model "Nano-banana 2 绘图" --prompt "每日AI资讯封面图" --n 2 --ratio "16:9"
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="子命令")

    gen_parser = subparsers.add_parser("generate", help="生成图片")
    gen_parser.add_argument("--model", required=True, help="模型名称")
    gen_parser.add_argument("--prompt", required=True, help="图片描述")
    gen_parser.add_argument("--n", type=int, default=1, help="生成数量 (1-10)")
    gen_parser.add_argument(
        "--ratio",
        default="1:1",
        choices=["1:1", "3:2", "3:4", "4:3", "9:16", "16:9"],
        help="图片比例",
    )

    args = parser.parse_args()

    if args.command == "generate":
        asyncio.run(main_async(args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
