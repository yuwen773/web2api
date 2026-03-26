# Taiji 图片生成 Skill 设计

## 概述

将 web2api 中调用 Taiji AI 生成图片的逻辑提取为独立的 Agent Skill，让 Claude Code 能够直接调用 Taiji AI 生成图片，无需启动 web2api 服务。

## 技能定位

- **名称**: `taiji-image-generator`
- **用途**: 通过 Taiji AI 原生 API 生成图片
- **认证**: 读取 `assets/credentials.json` 登录，支持自动 token 续期

## 支持的模型

| 模型名称 | 模型值 | URL 提取正则 |
|---------|--------|------------|
| Nano-banana绘图模型 | `gemini-2.5-flash-image` | `!\[image\]\((https?://[^\s)]+)\)` |
| Nano-banana 2 绘图 | `gemini-3.1-flash-image-preview` | 同上 |
| GT-4o-image-vip（绘图模型） | `gpt-4o-image-vip` | `!\[gen_[^\]]*\]\((https?://[^\s)]+)\)` |

## 文件结构

```
taiji-image-generator/
├── SKILL.md              # 技能说明和使用指南
├── scripts/
│   └── taiji_image.py    # 核心逻辑
└── assets/
    └── credentials.json   # 配置文件
```

## assets/credentials.json

```json
{
  "base_url": "https://ai.aurod.cn",
  "account": "your@email.com",
  "password": "your_password",
  "app_version": "2.14.0"
}
```

- `app_version` 可选，默认为 `2.14.0`
- 凭证文件存储在 skill 目录下，便于管理
- SKILL.md 不加载 assets 目录，凭证不会泄露到对话上下文

## 核心流程

1. 读取 `assets/credentials.json`
2. 登录 Taiji API 获取 token（自动续期，存内存）
3. 创建 session
4. SSE 流发送生成请求，prompt 格式: `帮我生成标题为"{prompt}"的 {n} 张封面图，比例为 '{ratio}'`
5. 从 markdown SSE 流中提取图片 URL
6. 删除 session
7. 打印 URL 列表（每行一个）

## 核心参数

| 参数 | 类型 | 默认值 | 说明 |
|-----|------|--------|------|
| model | str | 必填 | 模型名称 |
| prompt | str | 必填 | 图片描述 |
| n | int | 1 | 生成数量，1-10 |
| ratio | str | "1:1" | 图片比例，支持: 1:1, 3:2, 3:4, 4:3, 9:16, 16:9 |

## 调用方式

### 命令行

```bash
python taiji_image.py generate \
  --model "Nano-banana 2 绘图" \
  --prompt "每日AI资讯封面图" \
  --n 2 \
  --ratio "16:9"
```

### Python API

```python
from taiji_image import generate_images

images = await generate_images(
    model="Nano-banana 2 绘图",
    prompt="每日AI资讯封面图",
    n=2,
    ratio="16:9"
)
# images: ["https://xxx.jpg", "https://yyy.png"]
```

### 异步上下文管理器

```python
from taiji_image import TaijiImageClient

async with TaijiImageClient() as client:
    images = await client.generate(model="...", prompt="...", n=1)
```

## 输出格式

每个 URL 一行，直接打印到 stdout：

```
https://cn-nb1.rains3.com/jay/xxx.jpg
https://cn-nb1.rains3.com/jay/yyy.png
```

## 错误处理

- 登录失败: 打印错误信息并退出
- 无图片生成: 抛出异常
- Session 清理: 在 finally 块中执行，确保资源释放
- Token 过期: 自动重新登录

## SKILL.md 内容

- frontmatter: name + description
- 触发条件说明
- 安装配置步骤（创建 credentials.json）
- 命令行调用示例
- Python API 调用示例
- 模型列表和参数说明
