---
name: kd-k3cloud-mcp
slug: kd-k3cloud-mcp
displayName: 金蝶云星空 MCP 连接器（双登录版）
description: 连接并配置金蝶云星空 MCP Server 的 WorkBuddy 连接器（第三方开源 kingdee-mcp，非金蝶官方出品）。接入后可用自然语言查询/操作金蝶 ERP 单据；支持两种登录方式——账号密码(ValidateUser) 与 第三方应用授权(LoginByAppSecret)。
author: tery (merged) / WaHaiLong (upstream) / huaangdou-afk (connector)
version: 0.3.0
category: 办公协作
platforms:
  - workbuddy
repository: https://github.com/sclyxnet/kd-k3cloud-mcp
triggers:
  - 连接金蝶
  - 连接金蝶云星空
  - 配置金蝶 MCP
  - 接入金蝶 ERP
  - 用 AI 操作金蝶
  - 在 WorkBuddy 里用金蝶
agent_created: true
---

# 金蝶云星空 MCP 连接器（双登录版）

## Overview

> ⚠️ **第三方开源，非金蝶官方出品。** 本项目由社区维护（上游 GitHub: [WaHaiLong/KingdeeMCP](https://github.com/WaHaiLong/KingdeeMCP)，PyPI: `kingdee-mcp`），与金蝶软件公司无隶属、无授权关系。任何对外文案均**不得**标注"金蝶官方""官方技术号"等表述。

本连接器将金蝶云星空 MCP Server 接入 WorkBuddy。接入后可用自然语言说"查询本月已审核的采购订单""帮我新建一张销售订单""审核这几张入库单"，WorkBuddy 自动调用金蝶 WebAPI 完成操作。

**本版本相对上游新增：两种登录方式可切换**（由 `KINGDEE_AUTH_MODE` 控制）：
- `password`（默认）：账号密码 `ValidateUser`，以真实用户身份执行，携带该用户业务/数据权限，**推荐**。
- `app_secret`：第三方应用授权 `LoginByAppSecret`，以应用身份登录，无需真实用户账号；报表等依赖数据权限的查询会受应用授权范围限制。

完整工具列表、支持的 form_id、环境变量与常见问题见 `references/kingdee_reference.md`；工具总数以 `src/kingdee_mcp/server.py` 中 `@mcp.tool` 为准（**97 个**）。

## 触发场景

当用户说出以下任意意图时启用本技能：
- "连接金蝶" / "连接金蝶云星空" / "配置金蝶 MCP" / "接入金蝶 ERP"
- "让 AI 操作金蝶" / "在 WorkBuddy 里用金蝶" / "对接金蝶云星空"
- 提及需要对接金蝶云星空（Kingdee Cloud Star）系统

## 接入工作流

### 第 1 步：前置检查
- 确认用户机器已安装 `uv`（推荐，用于 `uvx kingdee-mcp` 免安装运行）。未安装时：`pip install kingdee-mcp`，MCP 启动命令改用 `python -m kingdee_mcp.server`。
- Python 3.10+。

### 第 2 步：选择登录方式并收集参数

**方式 A：账号密码（password，推荐）**
1. `KINGDEE_SERVER_URL` — 金蝶服务器地址，**必须包含 `/k3cloud/` 后缀**，如 `http://your-server/k3cloud/`
2. `KINGDEE_ACCT_ID` — 账套 ID
3. `KINGDEE_USERNAME` — 金蝶账号（建议专用集成账号，**不要用 Administrator**）
4. `KINGDEE_PASSWORD` — 金蝶账号密码

**方式 B：应用授权（app_secret）**
1. `KINGDEE_SERVER_URL` — 同上
2. `KINGDEE_ACCT_ID` — 账套 ID
3. `KINGDEE_APP_ID` — 金蝶第三方应用 AppId
4. `KINGDEE_APP_SEC` — 金蝶第三方应用 AppSecret

> 两种方式都需在金蝶后台为对应账号/应用分配所需模块的操作权限。password 方式以真实用户身份执行，权限最完整；app_secret 方式以应用身份执行，报表类依赖数据权限的查询可能受限。
> `KINGDEE_ACCT_ID`（账套 ID）**可直接填中文账套名或账套号**（如 `预生产`），本连接器会在登录前通过 `GetDataCenterList` 自动解析成登录用的 Id；已是 Id 则原样使用。

### 第 3 步：写入 MCP 配置
运行本技能附带的配置脚本（按所选登录方式传参）：

```bash
# 方式 A：账号密码
python3 integrations/workbuddy/scripts/configure_kingdee_mcp.py \
  --server-url "http://your-server/k3cloud/" \
  --acct-id "你的账套ID" \
  --auth-mode password \
  --username "金蝶账号" \
  --password "金蝶账号密码"

# 方式 B：应用授权
python3 integrations/workbuddy/scripts/configure_kingdee_mcp.py \
  --server-url "http://your-server/k3cloud/" \
  --acct-id "你的账套ID" \
  --auth-mode app_secret \
  --app-id "应用AppId" \
  --app-secret "应用AppSecret"
```

脚本会读取（不存在则新建）`~/.workbuddy/mcp.json`，在 `mcpServers` 下写入 `kingdee` 条目，并保留已有其他 server。可选 `--sql-host/--sql-port/--sql-database/--sql-user/--sql-password` 开启 SQL Server 探查工具。

未安装 uv 的用户：脚本默认按 uvx 写入，写完后可用 Edit 工具把 `command` 改为 `"python"`、`args` 改为 `["-m","kingdee_mcp.server"]`。

### 第 4 步：信任与启用
写入配置后，打开 WorkBuddy「连接器管理 / 自定义 MCP」，找到 `kingdee` 点击「信任 / 启用」，重启或重连 MCP。

### 第 5 步：验证
建议测试一句自然语言，例如「查询最近 20 条已审核的采购订单」。认证失败：检查所选登录方式的凭据与账号权限；连接超时：检查 `KINGDEE_SERVER_URL` 是否含 `/k3cloud/` 且服务器可访问。

## 安全提示
- 金蝶凭据属敏感信息，仅写入本地 `~/.workbuddy/mcp.json`，不要外泄或提交到公开仓库。
- 集成账号应使用专用账号/应用，分配最小必要权限，不要用 Administrator。

## Resources
- `integrations/workbuddy/scripts/configure_kingdee_mcp.py` — 合并写入 MCP 配置（支持双登录）。
- `references/kingdee_reference.md` — 完整工具列表（97）、支持的单据类型（form_id）、环境变量、双登录说明与 FAQ。
- `src/kingdee_mcp/server.py` — 上游 MCP Server 源码（97 个 `@mcp.tool`，双登录实现见 `_login()`）。

## 数据中心（账套）管理与中文交互
本连接器把登录页的「账套下拉框」（`GetDataCenterList`）抽成 MCP 工具，让用户/AI 用自然语言切换账套，无需记忆十六进制 Id：

- **`kingdee_list_data_centers`**：列出所有账套（中文名 / 账套号 / 登录 Id / 数据库类型 / 认证方式），无需登录即可调用。当用户问「有哪些账套」「我要切到XX账套」时先调用它。
- **`kingdee_switch_data_center(identifier)`**：切到指定账套并重置会话。`identifier` 支持**中文名 / 账套号 / Id**（如 `预生产`、`TEST20260521`、`6466ccc799e8fb`）。切换后下一次 API 调用自动用新账套重新登录；切换仅对当前 MCP 进程生效。

配合 `KINGDEE_ACCT_ID` 可填中文名/账套号（启动时自动解析为登录 Id），AI 即可直接说「查预生产里的采购订单」「切到 TEST20260521 账套」，无需硬编码 Id。

> 注意：切换是运行时行为，进程重启后回到 mcp.json 里 `KINGDEE_ACCT_ID` 配置的值。若要永久生效，把 `KINGDEE_ACCT_ID` 改成目标账套的 Id（或中文名）。
