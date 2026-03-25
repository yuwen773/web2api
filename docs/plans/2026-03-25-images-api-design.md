# 图片生成 API 设计文档

## 概述

为 web2api 项目新增两个图片生成接口，兼容 OpenAI Images API 格式，内部调用太极 AI 的 Nano-banana 和 GT-4o-image-vip 绘图模型。

## 接口设计

### 1. `/v1/images/generations`（Nano-banana 绘图）

**用途**：Nano-banana 系列图片生成

#### 请求格式
```json
{
  "model": "Nano-banana 2 绘图",
  "prompt": "帮我生成标题为\"每日AI资讯\"的封面图",
  "n": 3,
  "ratio": "3:4"
}
```

#### 内部封装
```json
{
  "text": "帮我生成标题为\"每日AI资讯\"的 3 张 封面图,比例为 '3:4'",
  "sessionId": <自动创建>,
  "files": []
}
```

#### 响应格式
```json
{
  "created": 1743000000,
  "data": [
    {"url": "https://cn-nb1.rains3.com/jay/xxx.jpg"},
    {"url": "https://cn-nb1.rains3.com/jay/xxx.jpg"},
    {"url": "https://cn-nb1.rains3.com/jay/xxx.jpg"}
  ]
}
```

### 2. `/v1/images/create`（GT-4o-image-vip）

**用途**：GT-4o-image-vip 图片生成

#### 请求格式
```json
{
  "model": "GT-4o-image-vip（绘图模型）",
  "prompt": "帮我生成标题为\"每日AI资讯\"的封面图",
  "n": 2,
  "ratio": "1:1"
}
```

#### 内部封装
```json
{
  "text": "帮我生成标题为\"每日AI资讯\"的 2 张 封面图，比例为 '1:1'",
  "sessionId": <自动创建>,
  "files": []
}
```

#### 响应格式
```json
{
  "created": 1743000000,
  "data": [
    {"url": "https://pro.filesystem.site/cdn/20260325/xxx.png"},
    {"url": "https://pro.filesystem.site/cdn/20260325/xxx.png"}
  ]
}
```

## 模型映射

| 接口 | label（请求值） | value（内部模型） |
|------|----------------|------------------|
| generations | `Nano-banana绘图模型` | `gemini-2.5-flash-image` |
| generations | `Nano-banana 2 绘图` | `gemini-3.1-flash-image-preview` |
| create | `GT-4o-image-vip（绘图模型）` | `gpt-4o-image-vip` |

## 支持的 ratio 参数

两个接口均支持以下比例：
- `1:1`, `3:2`, `3:4`, `4:3`, `9:16`, `16:9`

## 架构设计

```
src/
├── api/
│   └── images.py          # 新增图片生成 API 端点
├── models/
│   └── images_request.py  # 新增图片请求数据模型
└── utils/
    └── image_converter.py # 新增图片响应解析工具
```

## 响应解析逻辑

### Nano-banana（generations）
- 从 SSE 流式响应中提取 `type="string"` 的 `data` 字段
- 使用正则提取 `![image](url)` 格式的图片链接

### GT-4o-image-vip（create）
- 从 SSE 流式响应中提取最终 `type="object"` 的 `data` 字段
- 解析 JSON 获取下载链接数组

## 错误处理

- 模型不支持：返回 400 Bad Request
- 绘图失败：返回 500 Internal Server Error
- 超时：返回 504 Gateway Timeout
