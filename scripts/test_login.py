"""独立登录测试：用 mcp.json 里的 kingdee env 实机验证 _login()。
绕过 WorkBuddy 里可能过期的子进程，直接从源码调用。
"""
import asyncio
import json
import os
import sys

# 1) 载入 mcp.json 的 env 到当前进程
CFG = r"C:\Users\ZnL\.workbuddy\mcp.json"
with open(CFG, "r", encoding="utf-8") as f:
    env = json.load(f)["mcpServers"]["kingdee"]["env"]
for k, v in env.items():
    os.environ[k] = v

# 2) 导入源码模块（src 在 editable 安装下已被识别，但显式加一下更稳）
sys.path.insert(0, r"D:\AI\projects\kingdee-mcp\src")

import kingdee_mcp.server as s  # noqa: E402


async def main():
    print(f"[INFO] SERVER   = {s.SERVER_URL}")
    print(f"[INFO] ACCT_ID  = {s.ACCT_ID}")
    print(f"[INFO] USERNAME = {s.USERNAME}")
    print(f"[INFO] PASSWORD = {'***已配置***' if s.PASSWORD else '(空，账号密码登录模式，必须填写)'}")
    try:
        sid = await s._login()
        print(f"[OK] 登录成功，SessionId 前缀: {sid[:12]}...")
    except RuntimeError as e:
        print(f"[EXPECTED] 缺少密码时的报错: {e}")
    except Exception as e:  # noqa: BLE001
        print(f"[FAIL] 登录失败: {type(e).__name__}: {e}")


if __name__ == "__main__":
    asyncio.run(main())
