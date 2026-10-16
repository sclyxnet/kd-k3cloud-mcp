#!/usr/bin/env python3
"""将金蝶云星空 MCP Server 配置合并写入 WorkBuddy 的 MCP 配置文件。

支持两种登录方式（与 kingdee-mcp >= 0.3.0 对齐）：
  - password   （默认）：账号密码(ValidateUser)，需 --username / --password
  - app_secret ：第三方应用授权(LoginByAppSecret)，需 --app-id / --app-secret

启动方式：优先 uvx（若已安装），否则回退到 `python -m kingdee_mcp.server`
（需已 `pip install kingdee-mcp`，默认探测 WorkBuddy 隔离 venv）。
脚本会保留 mcp.json 中已有的其他 server 配置，仅新增/覆盖 "kingdee" 条目。
"""
import argparse
import json
import os
import shutil

CONFIG_PATH = os.path.expanduser("~/.workbuddy/mcp.json")
DEFAULT_VENV_PYTHON = os.path.expanduser(
    "~/.workbuddy/binaries/python/envs/default/bin/python"
)


def detect_launch():
    """优先 uvx；否则用已安装的 python -m kingdee_mcp.server。"""
    if shutil.which("uvx"):
        return {"command": "uvx", "args": ["kingdee-mcp"]}
    py = (
        DEFAULT_VENV_PYTHON
        if os.path.exists(DEFAULT_VENV_PYTHON)
        else (shutil.which("python3") or "python")
    )
    return {"command": py, "args": ["-m", "kingdee_mcp.server"]}


def main():
    p = argparse.ArgumentParser(description="配置金蝶云星空 MCP 到 WorkBuddy (>=0.3.0, 支持双登录)")
    p.add_argument("--server-url", required=True, help="金蝶服务器地址，需含 /k3cloud/ 后缀")
    p.add_argument("--acct-id", required=True, help="账套ID")
    p.add_argument("--auth-mode", default="password", choices=["password", "app_secret"],
                   help="登录方式：password(账号密码,默认) | app_secret(应用授权)")
    # password 模式
    p.add_argument("--username", default=None, help="金蝶账号（password 模式，建议专用集成账号，非 Administrator）")
    p.add_argument("--password", default=None, help="金蝶账号密码（ValidateUser 登录，password 模式）")
    # app_secret 模式
    p.add_argument("--app-id", default=None, help="第三方应用 AppId（app_secret 模式）")
    p.add_argument("--app-secret", default=None, help="第三方应用 AppSecret（app_secret 模式）")
    # SQL Server 探查（可选）
    p.add_argument("--sql-host", default=None, help="SQL Server 主机（可选，数据库探查）")
    p.add_argument("--sql-port", default=None, help="SQL Server 端口（默认 1433）")
    p.add_argument("--sql-database", default=None, help="数据库名，如 AIS20260128142522")
    p.add_argument("--sql-user", default=None, help="SQL Server 用户（建议只读）")
    p.add_argument("--sql-password", default=None, help="SQL Server 密码")
    args = p.parse_args()

    env = {
        "KINGDEE_SERVER_URL": args.server_url,
        "KINGDEE_ACCT_ID": args.acct_id,
        "KINGDEE_AUTH_MODE": args.auth_mode,
    }

    if args.auth_mode == "app_secret":
        if not (args.app_id and args.app_secret):
            p.error("app_secret 模式必须同时提供 --app-id 与 --app-secret")
        env["KINGDEE_APP_ID"] = args.app_id
        env["KINGDEE_APP_SEC"] = args.app_secret
    else:
        if not (args.username and args.password):
            p.error("password 模式必须同时提供 --username 与 --password")
        env["KINGDEE_USERNAME"] = args.username
        env["KINGDEE_PASSWORD"] = args.password

    if args.sql_host:
        env["MCP_SQLSERVER_HOST"] = args.sql_host
    if args.sql_port:
        env["MCP_SQLSERVER_PORT"] = args.sql_port
    if args.sql_database:
        env["MCP_SQLSERVER_DATABASE"] = args.sql_database
    if args.sql_user:
        env["MCP_SQLSERVER_USER"] = args.sql_user
    if args.sql_password:
        env["MCP_SQLSERVER_PASSWORD"] = args.sql_password

    launch = detect_launch()

    config = {}
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            try:
                config = json.load(f)
            except json.JSONDecodeError:
                config = {}
    config.setdefault("mcpServers", {})
    config["mcpServers"]["kingdee"] = {
        "command": launch["command"],
        "args": launch["args"],
        "env": env,
    }
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print(f"已将金蝶 MCP 写入: {CONFIG_PATH}")
    print(f"登录方式: {args.auth_mode}  启动方式: {launch['command']} {' '.join(launch['args'])}")
    print("下一步：在 WorkBuddy 连接器管理中对 'kingdee' 点击「信任/启用」，并重启或重连 MCP。")


if __name__ == "__main__":
    main()
