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

完整工具列表、支持的 form_id、环境变量与常见问题见 `references/kingdee_reference.md`；工具总数以 `src/kingdee_mcp/server.py` 中 `@mcp.tool` 为准（**103 个**）。

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
- `references/kingdee_reference.md` — 完整工具列表、支持的单据类型（form_id）、环境变量、双登录说明与 FAQ。
- `src/kingdee_mcp/server.py` — 上游 MCP Server 源码（双登录实现见 `_login()`）。

## 连接 / 登录信息管理（切换账套、账号、密码、语言等）
登录相关的信息全部支持运行时切换，切换后下一次 API 调用自动用新配置重新登录（即重连）。

- **`kingdee_switch_login(...)`**（推荐）：一次可切换**任意组合**——
  `server_url`(连接地址，裸主机自动补 `/k3cloud/`)、`data_center`(账套，中文名/账套号/Id)、
  `username`、`password`、`auth_mode`(password/app_secret)、`app_id`、`app_secret`、`lcid`(登录语言)。
  参数均可选，只改传了的项；切换后默认立即试登录一次并报告结果（`verify`），
  加 `persist=True` 可写回 `~/.workbuddy/mcp.json` 使重启后仍生效。
- **`kingdee_switch_data_center(identifier)`**：只切换账套的便捷包装（等价 `switch_login(data_center=...)`）。
- **`kingdee_show_login_info()`**：查看当前连接/登录配置（密码与 AppSecret 一律脱敏）+ 会话状态。
- **`kingdee_test_login()`**：用当前配置立即登录一次，验证并重连。
- **`kingdee_list_data_centers()`**：列出所有账套（含各自支持的登录语言）。
- **`kingdee_list_login_languages()`**：按需查询当前账套支持的登录语言（默认中文 2052，一般不用调）。

**登录语言（LCID）**：默认 `2052` 中文(简体)，不需额外请求——账套数据里的 `LocaleValueName` 的 Key 即
各语言 LCID，内置映射（412 个 LCID≈144 种语言含地区变体）已在代码中，切换时会把"该账套支持哪些语言"
列出来并询问用户是否需要切换（如 `2052=中文(简体)`、`1033=英语(美国)`、`3076=中文(繁體·香港)`）。

> 切换仅对当前 MCP 进程生效；重启后回到 `mcp.json` 的 `env` 配置值。要永久生效请 `persist=True` 或改配置。

## 自然语言建单（中文 → 字段/编码 自动翻译，0.3.9）

用户说"添加一张销售订单，客户是凤集蛋品部，物料用原料蛋，数量 10"，按**五步流程**翻译执行，不要让用户报字段名：

1. **定对象**：`kingdee_list_object_types(keyword="销售订单", queryable_only=True)` 或 `kingdee_list_forms(keyword="销售")` 找到 form_id（如 `SAL_SaleOrder`）。
2. **中文字段翻译**：`kingdee_search_fields(form_id, keyword="客户 数量 日期")` —— 返回每个字段的 key / 中文名 / 所在单据体 / 是否必填 / 参照对象 / 填写方式。参照字段（`lookup_form` 非空）需填 `{"FNumber": 编码}`，普通字段直接填值。
3. **中文值翻译**：对每个参照字段调 `kingdee_find_code(lookup_form, name=中文名)`，如 客户"凤集"→`CUST0005`、物料"原料蛋"→`S01`。**结果多于一条时让用户确认，不要替用户拍板。**
4. **组装 + 校验**：按 `kingdee_get_bill_template(form_id)` 的骨架（元数据生成的必填项）填入翻译好的值，先 `kingdee_validate_bill` 校验（分录体 key 写错会被拦下并给出正确单据体名）。
5. **保存**：`kingdee_save_bill`；确认无误后按需 `kingdee_submit_bills` / `kingdee_audit_bills`。

注意事项：
- 分录字段在对应单据体（entity ≠ FBillHead）下，填进 model 的**分录体 key**（如 `FSaleOrderEntry`）里，不是顶层。
- `kingdee_find_code` 模糊命中多条时把列表给用户选；命中一条且名称完全一致才可直接用。
- 保存报「字段是必填项」时回第 2 步用 `only_required=True` 复查缺失字段。

## 报表取数三分法（0.3.8）

报表（ModelTypeId=900）**不能**用 `kingdee_query_bills`（ExecuteBillQuery），按报表种类选接口：

| 报表种类 | 工具 | 要点 |
|---|---|---|
| 账表（科目余额表 GL_RPT_AccountBalance 等） | `kingdee_query_report` | data 内 FieldKeys + Model（账簿/期间/级次）；FieldKeys 必须是报表真实列 key |
| 供应链库存分页账表（物料收发明细 STK_StockDetailRpt、库存台账 STK_StockBookRpt 等） | `kingdee_query_stock_report` | 必须先 `kingdee_list_filter_schemes` 拿非默认方案 FSCHEMEID；raw JSON body；CurQueryId 翻页 |
| 财务报表系统模板报表（资产负债表/利润表） | `kingdee_query_kds_report` | 不用 form_id，用报表模板编码 ReportNumber + 核算维度（编码用官方「报表API工具」生成参数核对） |

树形账表（`BOS_TreeSysReport`）与直接SQL账表（`BOS_SQLReport`）是 **BOS 设计器模板对象**，数据源为二开插件/SQL，
**没有统一取数 WebAPI**。二开账表取数两条路：① 配置 `MCP_SQLSERVER_*` 后用 `kingdee_sql_search` 直查底层表；
② 二开封装自定义 API 后经通用 HTTP 调用。
