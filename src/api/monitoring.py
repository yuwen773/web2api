"""
监控 API 端点

提供 Prometheus 指标、JSON 统计和 HTML 仪表盘。
"""

import time
from fastapi import Response
from fastapi.responses import JSONResponse
from starlette.responses import HTMLResponse

from src.utils.metrics_collector import get_metrics_collector
from src.utils.settings import get_settings


# 应用启动时间
_start_time = time.time()


def _format_uptime(seconds: float) -> str:
    """
    格式化运行时间

    Args:
        seconds: 运行秒数

    Returns:
        格式化的时间字符串 (例如: "2d 5h 30m 15s")
    """
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")

    return " ".join(parts)


def _calculate_success_rate(total_requests: int, total_errors: int) -> float:
    """
    计算成功率

    Args:
        total_requests: 总请求数
        total_errors: 总错误数

    Returns:
        成功率 (0-100)
    """
    if total_requests == 0:
        return 100.0
    return round((1 - (total_errors / total_requests)) * 100, 2)


def metrics(request) -> Response:
    """
    Prometheus 格式的指标端点

    Args:
        request: HTTP 请求对象

    Returns:
        Prometheus 文本格式的指标数据
    """
    collector = get_metrics_collector()
    metrics_data = collector.export_metrics()

    return Response(
        content=metrics_data,
        media_type=collector.get_content_type(),
    )


def stats_json(request) -> JSONResponse:
    """
    JSON 格式的统计端点

    Args:
        request: HTTP 请求对象

    Returns:
        包含当前统计信息的 JSON 响应
    """
    collector = get_metrics_collector()
    current_metrics = collector.get_metrics()

    uptime = time.time() - _start_time

    return JSONResponse({
        "uptime_seconds": round(uptime, 2),
        "uptime_formatted": _format_uptime(uptime),
        "http_requests_total": current_metrics.get("http_requests_total", 0),
        "http_requests_in_flight": current_metrics.get("http_requests_in_flight", 0),
        "http_errors_total": current_metrics.get("http_errors_total", 0),
        "success_rate": _calculate_success_rate(
            current_metrics.get("http_requests_total", 0),
            current_metrics.get("http_errors_total", 0)
        ),
        "taiji_tokens_total": current_metrics.get("taiji_tokens_total", 0),
        "taiji_session_active": current_metrics.get("taiji_session_active", 0),
        "taiji_reauth_total": current_metrics.get("taiji_reauth_total", 0),
        "taiji_images_generated_total": current_metrics.get("taiji_images_generated_total", 0),
    })


def stats(request) -> HTMLResponse:
    """
    HTML 统计仪表盘

    Args:
        request: HTTP 请求对象

    Returns:
        包含统计信息的 HTML 页面
    """
    settings = get_settings()
    collector = get_metrics_collector()
    current_metrics = collector.get_metrics()

    uptime = time.time() - _start_time
    uptime_formatted = _format_uptime(uptime)
    success_rate = _calculate_success_rate(
        current_metrics.get("http_requests_total", 0),
        current_metrics.get("http_errors_total", 0)
    )

    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>web2api 统计仪表盘</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        .header {{
            background: white;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}

        .header h1 {{
            color: #333;
            font-size: 28px;
            margin-bottom: 8px;
        }}

        .header .subtitle {{
            color: #666;
            font-size: 14px;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 24px;
        }}

        .stat-card {{
            background: white;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }}

        .stat-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 12px rgba(0, 0, 0, 0.15);
        }}

        .stat-card .label {{
            color: #666;
            font-size: 14px;
            font-weight: 500;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .stat-card .value {{
            color: #333;
            font-size: 36px;
            font-weight: 700;
            margin-bottom: 4px;
        }}

        .stat-card .unit {{
            color: #999;
            font-size: 16px;
            font-weight: 400;
        }}

        .stat-card.success .value {{
            color: #10b981;
        }}

        .stat-card.warning .value {{
            color: #f59e0b;
        }}

        .stat-card.error .value {{
            color: #ef4444;
        }}

        .stat-card.info .value {{
            color: #3b82f6;
        }}

        .section {{
            background: white;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}

        .section h2 {{
            color: #333;
            font-size: 20px;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 2px solid #f0f0f0;
        }}

        .metrics-list {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
        }}

        .metric-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 16px;
            background: #f8f9fa;
            border-radius: 8px;
        }}

        .metric-item .name {{
            color: #666;
            font-size: 14px;
        }}

        .metric-item .value {{
            color: #333;
            font-size: 18px;
            font-weight: 600;
        }}

        .footer {{
            text-align: center;
            color: white;
            font-size: 14px;
            opacity: 0.8;
            margin-top: 24px;
        }}

        .refresh-info {{
            background: #e0f2fe;
            color: #0369a1;
            padding: 12px 16px;
            border-radius: 8px;
            font-size: 14px;
            margin-bottom: 20px;
            text-align: center;
        }}
    </style>
    <script>
        // 自动刷新
        setTimeout(function() {{
            location.reload();
        }}, {settings.stats_refresh_sec * 1000});
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>web2api 统计仪表盘</h1>
            <p class="subtitle">太极 AI API 代理服务监控</p>
        </div>

        <div class="refresh-info">
            页面每 {settings.stats_refresh_sec} 秒自动刷新
        </div>

        <div class="stats-grid">
            <div class="stat-card success">
                <div class="label">总请求数</div>
                <div class="value">{current_metrics.get("http_requests_total", 0):,}</div>
            </div>

            <div class="stat-card info">
                <div class="label">当前并发</div>
                <div class="value">{current_metrics.get("http_requests_in_flight", 0)}</div>
            </div>

            <div class="stat-card {'success' if success_rate >= 99 else 'warning' if success_rate >= 95 else 'error'}">
                <div class="label">成功率</div>
                <div class="value">{success_rate:.1f}<span class="unit">%</span></div>
            </div>

            <div class="stat-card {'success' if success_rate >= 99 else 'warning' if success_rate >= 95 else 'error'}">
                <div class="label">错误总数</div>
                <div class="value">{current_metrics.get("http_errors_total", 0):,}</div>
            </div>
        </div>

        <div class="section">
            <h2>系统信息</h2>
            <div class="metrics-list">
                <div class="metric-item">
                    <span class="name">运行时间</span>
                    <span class="value">{uptime_formatted}</span>
                </div>
                <div class="metric-item">
                    <span class="name">运行秒数</span>
                    <span class="value">{uptime:.0f}s</span>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>Taiji AI 业务指标</h2>
            <div class="metrics-list">
                <div class="metric-item">
                    <span class="name">Token 总使用量</span>
                    <span class="value">{current_metrics.get("taiji_tokens_total", 0):,}</span>
                </div>
                <div class="metric-item">
                    <span class="name">活跃会话数</span>
                    <span class="value">{current_metrics.get("taiji_session_active", 0)}</span>
                </div>
                <div class="metric-item">
                    <span class="name">重新认证次数</span>
                    <span class="value">{current_metrics.get("taiji_reauth_total", 0):,}</span>
                </div>
                <div class="metric-item">
                    <span class="name">图片生成总数</span>
                    <span class="value">{current_metrics.get("taiji_images_generated_total", 0):,}</span>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>API 端点</h2>
            <div class="metrics-list">
                <div class="metric-item">
                    <span class="name">Prometheus 指标</span>
                    <span class="value">
                        <a href="{settings.metrics_endpoint}" style="color: #3b82f6; text-decoration: none;">{settings.metrics_endpoint}</a>
                    </span>
                </div>
                <div class="metric-item">
                    <span class="name">JSON 统计</span>
                    <span class="value">
                        <a href="{settings.stats_endpoint}/json" style="color: #3b82f6; text-decoration: none;">{settings.stats_endpoint}/json</a>
                    </span>
                </div>
            </div>
        </div>

        <div class="footer">
            web2api v0.1.0 | Powered by FastAPI & Prometheus
        </div>
    </div>
</body>
</html>"""

    return HTMLResponse(content=html_content)
