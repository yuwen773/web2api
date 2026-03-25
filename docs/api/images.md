# 图片生成 API 文档

## 概述

提供两个图片生成接口，分别使用 Nano-banana 系列模型和 GT-4o-image-vip 模型。

## 接口列表

| 接口 | 方法 | 模型 |
|------|------|------|
| `/v1/images/generations` | POST | Nano-banana 绘图模型、Nano-banana 2 绘图 |
| `/v1/images/create` | POST | GT-4o-image-vip（绘图模型） |

---

## Nano-banana 图片生成

**端点:** `POST /v1/images/generations`

### 支持的模型

| 模型名称 | 说明 |
|----------|------|
| `Nano-banana绘图模型` | 单张图片生成 |
| `Nano-banana 2 绘图` | 多张图片生成 |

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `model` | string | 是 | 模型名称，如 `Nano-banana 2 绘图` |
| `prompt` | string | 是 | 图片描述/标题 |
| `n` | integer | 否 | 生成数量，默认 1，最大 10 |
| `ratio` | string | 否 | 图片比例，默认 `1:1` |

### 支持的比例

`1:1`, `3:2`, `3:4`, `4:3`, `9:16`, `16:9`

### 请求示例

```json
{
  "model": "Nano-banana 2 绘图",
  "prompt": "科技感封面图",
  "n": 2,
  "ratio": "16:9"
}
```

### 响应示例

```json
{
  "created": 1743000000,
  "data": [
    {
      "url": "https://cn-nb1.rains3.com/jay/1774434209943376277-dd69151f1d5c.jpg"
    },
    {
      "url": "https://cn-nb1.rains3.com/jay/1774434236312566151-24571fc4b044.jpg"
    }
  ]
}
```

### cURL 示例

```bash
curl http://localhost:8000/v1/images/generations \
  -H "Content-Type: application/json" \
  -d '{"model":"Nano-banana 2 绘图","prompt":"科技感封面图","n":2,"ratio":"16:9"}'
```

---

## GT-4o-image-vip 图片生成

**端点:** `POST /v1/images/create`

### 支持的模型

| 模型名称 | 说明 |
|----------|------|
| `GT-4o-image-vip（绘图模型）` | 高质量图片生成，支持多种比例 |

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `model` | string | 是 | 固定为 `GT-4o-image-vip（绘图模型）` |
| `prompt` | string | 是 | 图片描述/标题 |
| `n` | integer | 否 | 生成数量，默认 1，最大 10 |
| `ratio` | string | 否 | 图片比例，默认 `1:1` |

### 支持的比例

`1:1`, `3:2`, `3:4`, `4:3`, `9:16`, `16:9`

### 请求示例

```json
{
  "model": "GT-4o-image-vip（绘图模型）",
  "prompt": "科技感封面图",
  "n": 2,
  "ratio": "1:1"
}
```

### 响应示例

```json
{
  "created": 1743000000,
  "data": [
    {
      "url": "https://pro.filesystem.site/cdn/20260325/306ae313f2c204bebb6eac02f2a6e1.png"
    },
    {
      "url": "https://pro.filesystem.site/cdn/20260325/76b66c012e503690c92430e7db3f71.png"
    }
  ]
}
```

### cURL 示例

```bash
curl http://localhost:8000/v1/images/create \
  -H "Content-Type: application/json" \
  -d '{"model":"GT-4o-image-vip（绘图模型）","prompt":"科技感封面图","n":2,"ratio":"1:1"}'
```

---

## 错误响应

### 400 Bad Request - 不支持的模型

```json
{
  "detail": "Unsupported model: xxx. Available: ['Nano-banana绘图模型', 'Nano-banana 2 绘图']"
}
```

### 400 Bad Request - 参数验证失败

```json
{
  "detail": [
    {
      "loc": ["body", "ratio"],
      "msg": "unexpected value; permitted: '1:1', '3:2', '3:4', '4:3', '9:16', '16:9'",
      "type": "value_error"
    }
  ]
}
```

### 500 Internal Server Error - 生成失败

```json
{
  "detail": "No images generated"
}
```

---

## 模型对比

| 特性 | Nano-banana | Nano-banana 2 | GT-4o-image-vip |
|------|-------------|---------------|-----------------|
| 图片格式 | JPG | JPG | PNG |
| 生成速度 | 快 | 快 | 较慢 |
| 图片质量 | 良好 | 良好 | 较高 |
| 多图支持 | 单张 | 多张 | 多张 |
| ratio 支持 | 是 | 是 | 是 |

---

## 内部实现

### 请求封装

两个接口均通过 `/api/chat/completions` 调用太极 AI，prompt 格式如下：

**Nano-banana:**
```
帮我生成标题为"{prompt}"的 {n} 张 封面图,比例为 '{ratio}'
```

**GT-4o-image-vip:**
```
帮我生成标题为"{prompt}"的 {n} 张 封面图，比例为 '{ratio}'
```

### 响应解析

- **Nano-banana**: 从 SSE 响应中提取 `![image](url)` 格式的图片链接
- **GT-4o-image-vip**: 从 SSE 响应中提取 `![gen_xxx](url)` 格式的图片链接
