"""
阶段 1.1~1.3 测试脚本
测试登录、获取模型列表、创建会话功能
"""
import asyncio
import os
from dotenv import load_dotenv
import pytest

# 加载环境变量
load_dotenv()


@pytest.mark.asyncio
async def test_phase1():
    """测试阶段 1.1~1.3"""

    # ========================================
    # 配置：请在这里填写你的账号密码
    # ========================================
    ACCOUNT = os.getenv("TAIJI_ACCOUNT", "")
    PASSWORD = os.getenv("TAIJI_PASSWORD", "")
    API_BASE = os.getenv("TAIJI_API_BASE", "https://ai.aurod.cn")

    if not ACCOUNT or not PASSWORD:
        print("❌ 错误: 请在 .env 文件中配置 TAIJI_ACCOUNT 和 TAIJI_PASSWORD")
        return

    print("=" * 50)
    print("阶段 1.1~1.3 测试")
    print("=" * 50)

    # ========================================
    # 步骤 1.1: 测试登录
    # ========================================
    print("\n📝 步骤 1.1: 测试登录功能")
    print("-" * 30)

    import httpx

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
        "content-type": "application/json",
        "x-app-version": "2.14.0",
        "origin": "https://ai.aurod.cn",
        "referer": "https://ai.aurod.cn/auth",
        "sec-ch-ua": '"Not:A-Brand";v="99", "Microsoft Edge";v="145", "Chromium";v="145"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
        "priority": "u=1, i",
    }

    login_data = {
        "account": ACCOUNT,
        "password": PASSWORD,
        "code": "",
        "captcha": "",
        "invite": "",
        "agreement": True
    }

    async with httpx.AsyncClient(base_url=API_BASE) as client:
        response = await client.post("/api/user/login", json=login_data, headers=headers)
        result = response.json()

        print(f"响应状态码: {response.status_code}")
        print(f"响应 code: {result.get('code')}")
        print(f"响应 msg: {result.get('msg')}")

        if result.get("code") != 0:
            print(f"❌ 登录失败: {result}")
            return

        token = result.get("data", {}).get("token")
        print(f"✅ 登录成功!")
        print(f"   Token (前20字符): {token[:20]}...")
        print(f"   Token 格式检查: {'JWT格式正确' if token.count('.') == 2 else '格式异常'}")

        # 保存 cookie (server_name_session)
        cookies = dict(response.cookies)
        print(f"   登录响应 Cookies: {cookies}")

        # 验证 client 是否保存了 cookies
        print(f"   Client cookies: {dict(client.cookies)}")

        # ========================================
        # 步骤 1.2: 测试获取模型列表
        # ========================================
        print("\n📝 步骤 1.2: 测试获取模型列表")
        print("-" * 30)

        # 太极AI 的 authorization 不需要 Bearer 前缀！
        headers["authorization"] = token
        headers["referer"] = "https://ai.aurod.cn/chat"

        # 调试：打印即将发送的请求头和 cookies
        print(f"   请求头: {headers}")
        print(f"   发送时的 Cookies: {dict(client.cookies)}")

        models_response = await client.get("/api/chat/tmpl", headers=headers)
        models_result = models_response.json()

        if models_result.get("code") != 0:
            print(f"❌ 获取模型失败: {models_result}")
            return

        raw_data = models_result.get("data")
        if isinstance(raw_data, dict) and "models" in raw_data:
            models = raw_data.get("models", [])
        elif isinstance(raw_data, list):
            models = raw_data
        else:
            models = []

        print(f"✅ 获取模型成功!")
        print(f"   data 字段类型: {type(raw_data)}")
        print(f"   models 字段类型: {type(models)}")
        print(f"   models 数量: {len(models) if isinstance(models, list) else 0}")

        # 检查关键模型
        if isinstance(models, list):
            if len(models) > 0 and isinstance(models[0], str):
                # 如果是字符串列表
                model_values = models
                has_mini = any("gpt-4.1-mini" in v for v in model_values)
                has_claude = any("claude-opus-4-6" in v for v in model_values)
                print(f"   包含 gpt-4.1-mini: {'✅' if has_mini else '❌'}")
                print(f"   包含 claude-opus-4-6: {'✅' if has_claude else '❌'}")
                # 显示前5个模型
                print(f"\n   前5个模型:")
                for m in models[:5]:
                    print(f"   - {m}")
            elif len(models) > 0 and isinstance(models[0], dict):
                # 如果是字典列表
                model_values = [m.get("value") for m in models]
                has_mini = "gpt-4.1-mini" in model_values
                has_claude = any("claude-opus-4-6" in v for v in model_values)
                print(f"   包含 gpt-4.1-mini: {'✅' if has_mini else '❌'}")
                print(f"   包含 claude-opus-4-6: {'✅' if has_claude else '❌'}")
                # 显示前5个模型
                print(f"\n   前5个模型:")
                for m in models[:5]:
                    print(f"   - {m.get('label')} ({m.get('value')})")

        # ========================================
        # 步骤 1.3: 测试创建会话
        # ========================================
        print("\n📝 步骤 1.3: 测试创建会话")
        print("-" * 30)

        headers["content-type"] = "application/json"
        headers["origin"] = "https://ai.aurod.cn"

        session_data = {
            "model": "gpt-4.1-mini",
            "plugins": [],
            "mcp": []
        }

        # 创建3个会话，验证 id 不同
        session_ids = []
        for i in range(3):
            session_response = await client.post("/api/chat/session", json=session_data, headers=headers)
            session_result = session_response.json()

            if session_result.get("code") != 0:
                print(f"❌ 创建会话 {i+1} 失败: {session_result}")
                continue

            session_id = session_result.get("data", {}).get("id")
            session_ids.append(session_id)
            print(f"   会话 {i+1}: ID = {session_id} (类型: {type(session_id).__name__})")

        if len(session_ids) == 3:
            if len(set(session_ids)) == 3:
                print(f"✅ 创建会话成功! 3个会话ID均不同")
            else:
                print(f"⚠️  警告: 会话ID有重复")
        else:
            print(f"❌ 创建会话失败")

    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(test_phase1())
