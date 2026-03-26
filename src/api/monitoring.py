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

    status_color = "#22c55e" if success_rate >= 99 else "#f59e0b" if success_rate >= 95 else "#ef4444"
    status_label = "OPTIMAL" if success_rate >= 99 else "DEGRADED" if success_rate >= 95 else "CRITICAL"

    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>web2api // 监控仪表盘</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-deep: #05080a;
            --bg-panel: #0a1015;
            --bg-card: #0d1820;
            --border: #1a2a38;
            --cyan: #00e5ff;
            --cyan-dim: #00b8cc;
            --cyan-glow: rgba(0, 229, 255, 0.15);
            --green: #22c55e;
            --green-dim: #16a34a;
            --amber: #f59e0b;
            --red: #ef4444;
            --text-primary: #e2e8f0;
            --text-secondary: #64748b;
            --text-dim: #334155;
            --font-mono: 'Share Tech Mono', 'Courier New', monospace;
            --font-display: 'Orbitron', sans-serif;
        }}

        *, *::before, *::after {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        ::selection {{
            background: var(--cyan);
            color: var(--bg-deep);
        }}

        body {{
            font-family: var(--font-mono);
            background: var(--bg-deep);
            color: var(--text-primary);
            min-height: 100vh;
            overflow-x: hidden;
            position: relative;
        }}

        /* Scanline overlay */
        body::before {{
            content: '';
            position: fixed;
            inset: 0;
            background: repeating-linear-gradient(
                0deg,
                transparent,
                transparent 2px,
                rgba(0, 0, 0, 0.08) 2px,
                rgba(0, 0, 0, 0.08) 4px
            );
            pointer-events: none;
            z-index: 999;
        }}

        /* CRT vignette */
        body::after {{
            content: '';
            position: fixed;
            inset: 0;
            background: radial-gradient(ellipse at center, transparent 50%, rgba(0, 0, 0, 0.6) 100%);
            pointer-events: none;
            z-index: 998;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 32px 24px;
            position: relative;
            z-index: 1;
        }}

        /* ── HEADER ─────────────────────────────────── */
        .header {{
            display: flex;
            align-items: flex-end;
            justify-content: space-between;
            margin-bottom: 40px;
            padding-bottom: 24px;
            border-bottom: 1px solid var(--border);
            animation: fadeSlideDown 0.6s ease-out;
        }}

        .header-left .logo {{
            font-family: var(--font-display);
            font-size: 13px;
            font-weight: 700;
            color: var(--cyan);
            letter-spacing: 6px;
            text-transform: uppercase;
            text-shadow: 0 0 20px var(--cyan-glow), 0 0 40px var(--cyan-glow);
            margin-bottom: 8px;
        }}

        .header-left .title {{
            font-family: var(--font-display);
            font-size: 28px;
            font-weight: 900;
            color: var(--text-primary);
            letter-spacing: 3px;
            text-transform: uppercase;
            line-height: 1;
        }}

        .header-left .subtitle {{
            font-size: 11px;
            color: var(--text-secondary);
            letter-spacing: 2px;
            margin-top: 6px;
            text-transform: uppercase;
        }}

        .header-right {{
            text-align: right;
        }}

        .status-badge {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 6px 16px;
            border: 1px solid {status_color};
            border-radius: 2px;
            font-family: var(--font-display);
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 3px;
            color: {status_color};
            text-shadow: 0 0 10px {status_color};
            box-shadow: 0 0 12px rgba({status_color == "#22c55e" and "34, 197, 94" or status_color == "#f59e0b" and "245, 158, 11" or "239, 68, 68"}, 0.3);
            animation: statusPulse 2s ease-in-out infinite;
        }}

        .status-dot {{
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: {status_color};
            box-shadow: 0 0 6px {status_color};
            animation: dotBlink 1.4s ease-in-out infinite;
        }}

        .uptime-display {{
            margin-top: 10px;
            font-size: 11px;
            color: var(--text-dim);
            letter-spacing: 1px;
        }}

        .uptime-display span {{
            color: var(--cyan-dim);
        }}

        /* ── HERO STATS ─────────────────────────────── */
        .hero-grid {{
            display: grid;
            grid-template-columns: 2fr 1fr 1fr 1fr;
            gap: 16px;
            margin-bottom: 32px;
        }}

        .hero-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 4px;
            padding: 28px 24px;
            position: relative;
            overflow: hidden;
            transition: border-color 0.3s, box-shadow 0.3s;
            animation: fadeSlideUp 0.6s ease-out both;
        }}

        .hero-card:nth-child(1) {{ animation-delay: 0.1s; }}
        .hero-card:nth-child(2) {{ animation-delay: 0.2s; }}
        .hero-card:nth-child(3) {{ animation-delay: 0.3s; }}
        .hero-card:nth-child(4) {{ animation-delay: 0.4s; }}

        .hero-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, transparent, var(--cyan), transparent);
            opacity: 0;
            transition: opacity 0.3s;
        }}

        .hero-card:hover::before {{
            opacity: 1;
        }}

        .hero-card:hover {{
            border-color: var(--cyan-dim);
            box-shadow: 0 0 24px rgba(0, 229, 255, 0.08), inset 0 0 60px rgba(0, 229, 255, 0.03);
        }}

        .hero-card.accent::before {{
            opacity: 1;
        }}

        .hero-card.accent {{
            border-color: rgba(0, 229, 255, 0.3);
            box-shadow: 0 0 24px rgba(0, 229, 255, 0.1), inset 0 0 60px rgba(0, 229, 255, 0.04);
        }}

        .hero-card .corner-tl, .hero-card .corner-tr {{
            position: absolute;
            width: 12px;
            height: 12px;
            border-color: var(--cyan-dim);
            border-style: solid;
            opacity: 0.4;
            transition: opacity 0.3s;
        }}

        .hero-card:hover .corner-tl, .hero-card:hover .corner-tr {{
            opacity: 1;
        }}

        .hero-card .corner-tl {{
            top: 6px;
            left: 6px;
            border-width: 1px 0 0 1px;
        }}

        .hero-card .corner-tr {{
            top: 6px;
            right: 6px;
            border-width: 1px 1px 0 0;
        }}

        .hero-card .corner-bl, .hero-card .corner-br {{
            position: absolute;
            width: 12px;
            height: 12px;
            border-color: var(--cyan-dim);
            border-style: solid;
            opacity: 0.4;
            transition: opacity 0.3s;
        }}

        .hero-card:hover .corner-bl, .hero-card:hover .corner-br {{
            opacity: 1;
        }}

        .hero-card .corner-bl {{
            bottom: 6px;
            left: 6px;
            border-width: 0 0 1px 1px;
        }}

        .hero-card .corner-br {{
            bottom: 6px;
            right: 6px;
            border-width: 0 1px 1px 0;
        }}

        .hero-label {{
            font-size: 10px;
            color: var(--text-secondary);
            letter-spacing: 3px;
            text-transform: uppercase;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .hero-label::before {{
            content: '//';
            color: var(--cyan-dim);
            opacity: 0.6;
        }}

        .hero-value {{
            font-family: var(--font-display);
            font-size: 42px;
            font-weight: 900;
            color: var(--text-primary);
            letter-spacing: 2px;
            line-height: 1;
            text-shadow: 0 0 30px rgba(226, 232, 240, 0.1);
        }}

        .hero-value.cyan {{ color: var(--cyan); text-shadow: 0 0 30px var(--cyan-glow); }}
        .hero-value.green {{ color: var(--green); text-shadow: 0 0 30px rgba(34, 197, 94, 0.2); }}
        .hero-value.amber {{ color: var(--amber); text-shadow: 0 0 30px rgba(245, 158, 11, 0.2); }}
        .hero-value.red {{ color: var(--red); text-shadow: 0 0 30px rgba(239, 68, 68, 0.2); }}

        .hero-sub {{
            font-size: 11px;
            color: var(--text-dim);
            margin-top: 8px;
            letter-spacing: 1px;
        }}

        /* ── GRID LAYOUT ─────────────────────────────── */
        .main-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            margin-bottom: 32px;
        }}

        .panel {{
            background: var(--bg-panel);
            border: 1px solid var(--border);
            border-radius: 4px;
            overflow: hidden;
            animation: fadeSlideUp 0.6s ease-out 0.5s both;
        }}

        .panel-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 14px 20px;
            border-bottom: 1px solid var(--border);
            background: rgba(0, 0, 0, 0.3);
        }}

        .panel-title {{
            font-family: var(--font-display);
            font-size: 10px;
            font-weight: 700;
            color: var(--cyan);
            letter-spacing: 4px;
            text-transform: uppercase;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .panel-title::before {{
            content: '';
            display: inline-block;
            width: 6px;
            height: 6px;
            background: var(--cyan);
            box-shadow: 0 0 6px var(--cyan);
            border-radius: 1px;
            animation: dotBlink 2s ease-in-out infinite;
        }}

        .panel-body {{
            padding: 20px;
        }}

        .metric-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid rgba(26, 42, 56, 0.6);
            transition: background 0.2s;
        }}

        .metric-row:last-child {{
            border-bottom: none;
        }}

        .metric-row:hover {{
            background: rgba(0, 229, 255, 0.02);
            padding-left: 8px;
            padding-right: 8px;
            margin: 0 -8px;
        }}

        .metric-name {{
            font-size: 12px;
            color: var(--text-secondary);
            letter-spacing: 1px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .metric-name .pip {{
            width: 4px;
            height: 4px;
            border-radius: 50%;
            background: var(--text-dim);
            flex-shrink: 0;
        }}

        .metric-val {{
            font-family: var(--font-display);
            font-size: 14px;
            font-weight: 700;
            color: var(--text-primary);
            letter-spacing: 1px;
        }}

        .metric-val.highlight {{
            color: var(--cyan);
            text-shadow: 0 0 8px var(--cyan-glow);
        }}

        .metric-bar-wrap {{
            flex: 1;
            margin: 0 16px;
            display: none;
        }}

        /* ── SUCCESS RATE GAUGE ──────────────────────── */
        .gauge-section {{
            display: flex;
            align-items: center;
            gap: 24px;
        }}

        .gauge-svg {{
            flex-shrink: 0;
        }}

        .gauge-info {{
            flex: 1;
        }}

        .gauge-label {{
            font-size: 10px;
            color: var(--text-secondary);
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-bottom: 4px;
        }}

        .gauge-value {{
            font-family: var(--font-display);
            font-size: 36px;
            font-weight: 900;
            color: {status_color};
            letter-spacing: 1px;
            text-shadow: 0 0 20px {status_color}55;
        }}

        .gauge-bar-bg {{
            width: 100%;
            height: 4px;
            background: var(--border);
            border-radius: 2px;
            margin-top: 12px;
            overflow: hidden;
        }}

        .gauge-bar-fill {{
            height: 100%;
            background: {status_color};
            box-shadow: 0 0 8px {status_color};
            border-radius: 2px;
            transition: width 1s ease-out;
            width: {success_rate}%;
        }}

        /* ── REQUESTS PER SECOND ─────────────────────── */
        .rps-display {{
            display: flex;
            align-items: flex-end;
            gap: 8px;
            margin-top: 16px;
        }}

        .rps-value {{
            font-family: var(--font-display);
            font-size: 24px;
            font-weight: 700;
            color: var(--cyan);
            letter-spacing: 2px;
        }}

        .rps-label {{
            font-size: 11px;
            color: var(--text-dim);
            letter-spacing: 1px;
            padding-bottom: 4px;
        }}

        /* ── LIVE PULSE ──────────────────────────────── */
        .live-indicator {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 9px;
            color: var(--green);
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-left: auto;
        }}

        .live-dot {{
            width: 5px;
            height: 5px;
            border-radius: 50%;
            background: var(--green);
            box-shadow: 0 0 4px var(--green);
            animation: dotBlink 1s ease-in-out infinite;
        }}

        /* ── API ENDPOINTS ────────────────────────────── */
        .endpoint-list {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}

        .endpoint-item {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 14px;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 2px;
            text-decoration: none;
            transition: border-color 0.2s, box-shadow 0.2s;
        }}

        .endpoint-item:hover {{
            border-color: var(--cyan-dim);
            box-shadow: 0 0 12px var(--cyan-glow);
        }}

        .endpoint-url {{
            font-size: 11px;
            color: var(--cyan-dim);
            letter-spacing: 1px;
        }}

        .endpoint-method {{
            font-family: var(--font-display);
            font-size: 9px;
            font-weight: 700;
            padding: 2px 8px;
            border: 1px solid;
            border-radius: 2px;
            letter-spacing: 1px;
        }}

        .endpoint-method.get {{
            color: var(--green);
            border-color: var(--green);
        }}

        /* ── MINI CHART (ASCII sparkline) ─────────────── */
        .sparkline {{
            font-size: 11px;
            color: var(--text-dim);
            letter-spacing: 0;
            font-family: var(--font-mono);
        }}

        /* ── FOOTER ─────────────────────────────────── */
        .footer {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding-top: 20px;
            border-top: 1px solid var(--border);
            animation: fadeSlideUp 0.6s ease-out 0.7s both;
        }}

        .footer-left {{
            font-size: 10px;
            color: var(--text-dim);
            letter-spacing: 1px;
        }}

        .footer-right {{
            font-size: 10px;
            color: var(--text-dim);
            letter-spacing: 1px;
        }}

        .footer-right span {{
            color: var(--cyan-dim);
        }}

        /* ── ANIMATIONS ──────────────────────────────── */
        @keyframes fadeSlideDown {{
            from {{ opacity: 0; transform: translateY(-16px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        @keyframes fadeSlideUp {{
            from {{ opacity: 0; transform: translateY(16px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        @keyframes dotBlink {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.3; }}
        }}

        @keyframes statusPulse {{
            0%, 100% {{ box-shadow: 0 0 12px rgba({status_color == "#22c55e" and "34, 197, 94" or status_color == "#f59e0b" and "245, 158, 11" or "239, 68, 68"}, 0.3); }}
            50% {{ box-shadow: 0 0 20px rgba({status_color == "#22c55e" and "34, 197, 94" or status_color == "#f59e0b" and "245, 158, 11" or "239, 68, 68"}, 0.5); }}
        }}

        @keyframes countUp {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}

        .count-reveal {{
            animation: countUp 0.4s ease-out;
        }}

        /* ── RESPONSIVE ───────────────────────────────── */
        @media (max-width: 900px) {{
            .hero-grid {{
                grid-template-columns: 1fr 1fr;
            }}
            .main-grid {{
                grid-template-columns: 1fr;
            }}
            .header {{
                flex-direction: column;
                align-items: flex-start;
                gap: 16px;
            }}
            .header-right {{
                text-align: left;
            }}
        }}

        @media (max-width: 600px) {{
            .hero-grid {{
                grid-template-columns: 1fr;
            }}
            .hero-value {{
                font-size: 32px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- HEADER -->
        <header class="header">
            <div class="header-left">
                <div class="logo">web2api</div>
                <div class="title">MISSION CONTROL</div>
                <div class="subtitle">Taiji AI Proxy Service &mdash; Telemetry Dashboard</div>
            </div>
            <div class="header-right">
                <div class="status-badge">
                    <div class="status-dot"></div>
                    系统 {status_label}
                </div>
                <div class="uptime-display">
                    运行时间 &nbsp;<span>{uptime_formatted}</span>
                </div>
            </div>
        </header>

        <!-- HERO STATS -->
        <div class="hero-grid">
            <div class="hero-card accent">
                <div class="corner-tl"></div>
                <div class="corner-tr"></div>
                <div class="corner-bl"></div>
                <div class="corner-br"></div>
                <div class="hero-label">总请求数</div>
                <div class="hero-value cyan count-reveal">{current_metrics.get("http_requests_total", 0):,}</div>
                <div class="hero-sub">全部时间 &bull; 已运行 {uptime_formatted}</div>
            </div>
            <div class="hero-card">
                <div class="corner-tl"></div>
                <div class="corner-tr"></div>
                <div class="corner-bl"></div>
                <div class="corner-br"></div>
                <div class="hero-label">当前并发</div>
                <div class="hero-value count-reveal">{current_metrics.get("http_requests_in_flight", 0)}</div>
                <div class="hero-sub">并发请求数</div>
            </div>
            <div class="hero-card">
                <div class="corner-tl"></div>
                <div class="corner-tr"></div>
                <div class="corner-bl"></div>
                <div class="corner-br"></div>
                <div class="hero-label">成功率</div>
                <div class="hero-value {status_color == "#22c55e" and "green" or status_color == "#f59e0b" and "amber" or "red"} count-reveal">{success_rate:.1f}%</div>
                <div class="hero-sub">{status_label} 阈值</div>
            </div>
            <div class="hero-card">
                <div class="corner-tl"></div>
                <div class="corner-tr"></div>
                <div class="corner-bl"></div>
                <div class="corner-br"></div>
                <div class="hero-label">错误总数</div>
                <div class="hero-value red count-reveal">{current_metrics.get("http_errors_total", 0):,}</div>
                <div class="hero-sub">全部错误 &bull; 已运行 {uptime_formatted}</div>
            </div>
        </div>

        <!-- MAIN GRID -->
        <div class="main-grid">
            <!-- LEFT: Taiji AI Metrics -->
            <div class="panel">
                <div class="panel-header">
                    <div class="panel-title">太极 AI 业务指标</div>
                    <div class="live-indicator">
                        <div class="live-dot"></div>
                        实时
                    </div>
                </div>
                <div class="panel-body">
                    <div class="metric-row">
                        <div class="metric-name"><span class="pip"></span>Token 总使用量</div>
                        <div class="metric-val highlight">{current_metrics.get("taiji_tokens_total", 0):,}</div>
                    </div>
                    <div class="metric-row">
                        <div class="metric-name"><span class="pip"></span>活跃会话数</div>
                        <div class="metric-val">{current_metrics.get("taiji_session_active", 0)}</div>
                    </div>
                    <div class="metric-row">
                        <div class="metric-name"><span class="pip"></span>重新认证次数</div>
                        <div class="metric-val">{current_metrics.get("taiji_reauth_total", 0):,}</div>
                    </div>
                    <div class="metric-row">
                        <div class="metric-name"><span class="pip"></span>图片生成总数</div>
                        <div class="metric-val highlight">{current_metrics.get("taiji_images_generated_total", 0):,}</div>
                    </div>
                </div>
            </div>

            <!-- RIGHT: System & Health -->
            <div class="panel">
                <div class="panel-header">
                    <div class="panel-title">系统健康状态</div>
                    <div class="live-indicator">
                        <div class="live-dot"></div>
                        实时
                    </div>
                </div>
                <div class="panel-body">
                    <div class="gauge-section">
                        <svg class="gauge-svg" width="100" height="100" viewBox="0 0 100 100">
                            <circle cx="50" cy="50" r="40" fill="none" stroke="#1a2a38" stroke-width="8"/>
                            <circle cx="50" cy="50" r="40" fill="none"
                                stroke="{status_color}"
                                stroke-width="8"
                                stroke-linecap="round"
                                stroke-dasharray="{2 * 3.14159 * 40 * success_rate / 100} {{2 * 3.14159 * 40}}"
                                stroke-dashoffset="{{2 * 3.14159 * 40 * 0.25}}"
                                transform="rotate(-90 50 50)"
                                style="filter: drop-shadow(0 0 6px {status_color}); transition: stroke-dasharray 1s ease-out;"
                            />
                            <text x="50" y="46" text-anchor="middle" font-family="Orbitron, sans-serif" font-size="16" font-weight="900" fill="{status_color}">{success_rate:.0f}</text>
                            <text x="50" y="60" text-anchor="middle" font-family="Share Tech Mono, monospace" font-size="8" fill="#64748b">%</text>
                        </svg>
                        <div class="gauge-info">
                            <div class="gauge-label">成功率</div>
                            <div class="gauge-value">{success_rate:.2f}%</div>
                            <div class="gauge-bar-bg">
                                <div class="gauge-bar-fill"></div>
                            </div>
                        </div>
                    </div>
                    <div class="metric-row" style="margin-top: 20px;">
                        <div class="metric-name"><span class="pip"></span>服务运行时间</div>
                        <div class="metric-val">{uptime_formatted}</div>
                    </div>
                    <div class="metric-row">
                        <div class="metric-name"><span class="pip"></span>运行秒数</div>
                        <div class="metric-val">{uptime:.0f}s</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- API ENDPOINTS -->
        <div class="panel" style="animation-delay: 0.6s;">
            <div class="panel-header">
                <div class="panel-title">API 端点</div>
            </div>
            <div class="panel-body">
                <div class="endpoint-list">
                    <a href="{settings.metrics_endpoint}" class="endpoint-item">
                        <span class="endpoint-url">{settings.metrics_endpoint}</span>
                        <span class="endpoint-method get">GET</span>
                    </a>
                    <a href="{settings.stats_endpoint}/json" class="endpoint-item">
                        <span class="endpoint-url">{settings.stats_endpoint}/json</span>
                        <span class="endpoint-method get">GET</span>
                    </a>
                </div>
            </div>
        </div>

        <!-- FOOTER -->
        <footer class="footer">
            <div class="footer-left">WEB2API v0.1.0</div>
            <div class="footer-right">
                FastAPI + Prometheus &bull; 手动刷新
            </div>
        </footer>
    </div>

    <script>
        // Smooth number counter animation on load
        document.querySelectorAll('.count-reveal').forEach(el => {{
            el.style.opacity = '0';
            el.style.transform = 'translateY(8px)';
            setTimeout(() => {{
                el.style.transition = 'opacity 0.4s ease-out, transform 0.4s ease-out';
                el.style.opacity = '1';
                el.style.transform = 'translateY(0)';
            }}, Math.random() * 400 + 200);
        }});

        // Manual refresh only — no auto-reload
    </script>
</body>
</html>"""

    return HTMLResponse(content=html_content)
