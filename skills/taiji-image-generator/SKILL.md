---
name: taiji-image-generator
description: Taiji AI 图片生成工具。通过 Taiji AI 原生 API 生成图片，支持 Nano-banana 和 GT-4o-image-vip 模型。使用场景: (1) 生成封面图、海报、插图等, (2) 需要调用 Taiji AI 生成图片时, (3) 提供图片 URL 给其他工具使用
---

# Taiji Image Generator

通过 Taiji AI 原生 API 直接生成图片，无需启动 web2api 服务。

## 配置

首次使用需要配置 `assets/credentials.json`:

```json
{
  "base_url": "https://ai.aurod.cn",
  "account": "your@email.com",
  "password": "your_password",
  "app_version": "2.14.0"
}
```

## 命令行使用

```bash
python scripts/taiji_image.py generate \
  --model "Nano-banana 2 绘图" \
  --prompt "每日AI资讯封面图" \
  --n 2 \
  --ratio "16:9"
```

**参数说明:**

| 参数 | 必填 | 默认值 | 说明 |
|-----|------|--------|------|
| --model | 是 | - | 模型名称 |
| --prompt | 是 | - | 图片描述 |
| --n | 否 | 1 | 生成数量 (1-10) |
| --ratio | 否 | 1:1 | 图片比例 |

**可用比例:** 1:1, 3:2, 3:4, 4:3, 9:16, 16:9

## 支持的模型

| 模型名称 | 特点 |
|---------|------|
| Nano-banana绘图模型 | gemini-2.5-flash-image |
| Nano-banana 2 绘图 | gemini-3.1-flash-image-preview |
| GT-4o-image-vip（绘图模型） | GPT-4o 图片生成 |

## Python API

```python
import asyncio
from taiji_image import generate_images

async def main():
    images = await generate_images(
        model="Nano-banana 2 绘图",
        prompt="每日AI资讯封面图",
        n=2,
        ratio="16:9"
    )
    for url in images:
        print(url)

asyncio.run(main())
```

## 安装依赖

```bash
pip install -r requirements.txt
```

**依赖:** httpx >= 0.25.0 | Python 3.10+

## 跨平台使用

### Claude Code
```bash
python scripts/taiji_image.py generate --model "Nano-banana 2 绘图" --prompt "每日AI资讯封面图" --n 2 --ratio "16:9"
```

### Codex / OpenClaw / 其他 CLI
同上，脚本完全独立，不依赖任何外部项目。

### Unix-like 系统 (Linux/macOS)
```bash
# 设置执行权限
chmod +x scripts/taiji_image.py

# 直接运行
./scripts/taiji_image.py generate --model "Nano-banana 2 绘图" --prompt "每日AI资讯封面图"

# 或使用 python3
python3 scripts/taiji_image.py generate --model "Nano-banana 2 绘图" --prompt "每日AI资讯封面图"
```

### Windows
```bash
# 使用 python
python scripts/taiji_image.py generate --model "Nano-banana 2 绘图" --prompt "每日AI资讯封面图"
```

## 输出格式

每个图片 URL 一行，直接打印到 stdout:

```
https://cn-nb1.rains3.com/jay/xxx.jpg
https://cn-nb1.rains3.com/jay/yyy.png
```
