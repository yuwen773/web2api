# 日志目录

此目录用于存储 web2api 服务的日志文件。

## 日志文件

| 文件 | 说明 |
|------|------|
| `app.log` | 主日志文件，包含所有级别的日志（JSON 格式） |
| `app-error.log` | 错误日志，仅包含 ERROR 及以上级别的日志 |
| `app.log.*` | 轮转后的历史日志文件（自动压缩） |

## 日志轮转

- 单个日志文件最大 100MB
- 最多保留 30 个历史文件
- 超过 7 天的旧日志自动压缩为 .gz

## 查看 JSON 日志

使用 `jq` 工具可以方便地查看 JSON 格式的日志：

```bash
# 查看最近的日志
tail -f logs/app.log | jq

# 过滤特定级别的日志
cat logs/app.log | jq 'select(.level == "ERROR")'

# 查看特定请求的所有日志
grep "request-abc123" logs/app.log | jq
```

## 配置

日志配置在 `config/config.yaml` 中：

```yaml
logging:
  level: INFO
  format: both
  directory: ./logs
  rotation:
    max_size_mb: 100
    backup_count: 30
    compress_days: 7
```
