# kd-k3cloud-mcp（金蝶云星空 MCP · 双登录合并版）

> ⚠️ **第三方开源，非金蝶官方出品。** 与金蝶软件（Kingdee）无任何隶属或授权关系。任何对外文案**不得**标注"金蝶官方""官方技术号"。

**kd-k3cloud-mcp** 是把两个社区项目**合并成一个工程**的结果：

| 组成 | 来源 | 作用 |
|------|------|------|
| `src/kingdee_mcp/` | [WaHaiLong/KingdeeMCP](https://github.com/WaHaiLong/KingdeeMCP)（PyPI `kingdee-mcp`） | 真正的 MCP Server，上游 **97 个工具**（本工程扩充至 **103 个**） |
| `integrations/workbuddy/` | [huaangdou-afk/kingdee-mcp-connector](https://github.com/huaangdou-afk/kingdee-mcp-connector) | WorkBuddy 技能壳（一键配置、触发器、参考文档） |

官网：https://wahailong.github.io/KingdeeMCP/

## 为什么合并

- 壳与包分离会导致文档漂移（上游 README 曾写"87 个工具"，实际 `server.py` 已是 **97 个** `@mcp.tool`）。
- 合并后**一份源码 = PyPI 包 + WorkBuddy 技能**，版本号一致，工具清单可由脚本从 `server.py` 自动提取，根治人工过期。

## 本版本相对上游新增：双登录

由环境变量 `KINGDEE_AUTH_MODE` 切换（默认 `password`）：

| AUTH_MODE | 认证端点 | 必需变量 | 说明 |
|-----------|----------|----------|------|
| `password`（默认） | `ValidateUser` 账号密码 | `KINGDEE_USERNAME` + `KINGDEE_PASSWORD` | 真实用户身份，携带其业务/数据权限，**推荐** |
| `app_secret` | `LoginByAppSecret` 应用授权 | `KINGDEE_APP_ID` + `KINGDEE_APP_SEC` | 应用身份登录，无需真实用户；报表类依赖数据权限的查询可能受限 |

> 上游 0.2.0 砍掉了 AppSecret，本工程在 0.3.0 重新加回，做成可插拔（`src/kingdee_mcp/server.py` 的 `_login()` 按 `KINGDEE_AUTH_MODE` 分派）。

## 本版本相对上游新增：登录信息与账套的全量运行时切换（0.3.2）

把登录页的「账套下拉框」（`AccountService.GetDataCenterList`）抽成 MCP 工具，并让**所有登录信息都能在运行时切换并自动重连**：

### 登录信息切换（`kingdee_switch_login`，推荐）

一个工具切换**任意组合**，切换后立即重置会话、下一次 API 调用自动用新配置重登：

| 参数 | 说明 |
|---|---|
| `server_url` | 金蝶服务器地址（可传裸地址，自动补 `/k3cloud/`） |
| `data_center` | 账套：**中文名 / 账套号 / Id** 均可（如 `预生产`、`TEST20230518`） |
| `username` / `password` | 账号密码（password 模式） |
| `auth_mode` | `password` 账号密码 \| `app_secret` 应用授权 |
| `app_id` / `app_secret` | 应用授权凭据 |
| `lcid` | 登录语言，**默认 2052 中文(简体)** |
| `persist` | `True` 时写回 `~/.workbuddy/mcp.json`，重启后仍生效 |
| `verify` | `True`（默认）时立即试登录一次并报告结果 |

配套工具：

- **`kingdee_show_login_info`**：查看当前连接/登录配置，密码与 AppSecret 一律脱敏。
- **`kingdee_test_login`**：用当前配置立即登录一次，验证并重连。
- **`kingdee_list_data_centers`**：列出服务器上所有账套（中文名 / 账套号 / 登录 Id / 数据库类型 / 认证方式 / 支持语言），**无需登录**即可调用。
- **`kingdee_switch_data_center(identifier)`**：只切换账套的便捷包装（等价 `switch_login(data_center=...)`）。
- **`kingdee_list_login_languages`**：按需查询当前账套支持的登录语言（默认中文 2052，一般不用调）。

`KINGDEE_ACCT_ID` 支持直接填**中文账套名 / 账套号**，登录前自动解析成登录用的 `Id`（金蝶 WebAPI 登录 `acctID` = 数据中心 `Id`），已是 Id 则原样透传。

### 语言（LCID）映射

内置 **412 条 LCID 映射**（`_LCID_NAMES_ZH` / `_LCID_NAMES_EN`），常用：`2052=中文(简体)`（默认）、`1033=英语(美国)`、`3076=中文(繁體·香港)`、`1028=中文(繁體·台灣)`。
账套支持哪些语言**直接从 `GetDataCenterList` 返回的 `LocaleValueName` 推导**，无需额外请求。

### 网络韧性（保证会话不中断）

`_NET_RETRY`（默认 3 次，可用 `KINGDEE_NET_RETRY` 调整）+ 线性退避：网络超时 / 5xx / 会话失效时自动重登并重发。
会话失效采用**精确判定**（明确失效措辞 + 401/419），不会因正常响应里出现 `SessionId` 字样就白白重登。

## 功能特性

- **103 个工具**：覆盖生产、成本、资产、审计、采购、销售、库存、财务报表等 13+ 业务域（清单见下文，权威来源 `server.py`）。
- **登录信息全量运行时切换**：服务器 / 账套 / 账号 / 密码 / 登录方式 / AppID / AppSecret / 语言，切换即重连。
- **双登录**：账号密码 / 应用授权，一键切换。
- **账套（数据中心）管理**：列表 + 中文名/账套号切换，AI 可直接说「切到预生产账套」。
- **元数据动态查询**：`get_bill_template` / `validate_bill` / `refresh_metadata`，本地缓存。
- **4 个 SQL Server 探查工具**：搜索表/字段、看表结构、form_id→表名映射。
- **自然语言操作**：中文描述需求，AI 自动转 API 调用。
- **异步高性能** + **自动重试** + **Session 过期自动重登**。
- **类型安全**（Pydantic）+ **易于扩展**（FastMCP）。
- **多传输**：stdio（本地）/ sse / streamable-http（远程免装客户端）。
- **多客户端**：Claude Desktop、Cursor、Windsurf、Cline、Continue、Claude Code、OpenClaw，以及 **WorkBuddy**（通过 `integrations/workbuddy/` 技能壳）。

## 快速安装

```bash
pip install kingdee-mcp        # 或
uvx kingdee-mcp                # 推荐，免安装运行
```

Python 要求 `>=3.10`。

## 配置（两种登录方式）

```jsonc
// password 模式（默认）
{
  "mcpServers": {
    "kingdee": {
      "command": "uvx", "args": ["kingdee-mcp"],
      "env": {
        "KINGDEE_SERVER_URL": "http://your-server/k3cloud/",
        "KINGDEE_ACCT_ID": "你的账套ID",
        "KINGDEE_AUTH_MODE": "password",
        "KINGDEE_USERNAME": "金蝶账号",
        "KINGDEE_PASSWORD": "金蝶账号密码"
      }
    }
  }
}

// app_secret 模式
{
  "mcpServers": {
    "kingdee": {
      "command": "uvx", "args": ["kingdee-mcp"],
      "env": {
        "KINGDEE_SERVER_URL": "http://your-server/k3cloud/",
        "KINGDEE_ACCT_ID": "你的账套ID",
        "KINGDEE_AUTH_MODE": "app_secret",
        "KINGDEE_APP_ID": "应用AppId",
        "KINGDEE_APP_SEC": "应用AppSecret"
      }
    }
  }
}
```

`KINGDEE_SERVER_URL` **必须包含 `/k3cloud/` 后缀**。无 uv 时把 `command` 改为 `python`、`args` 改为 `["-m","kingdee_mcp.server"]`。

### 远程部署（HTTP / SSE）

```bash
uvx kingdee-mcp --transport sse --host 0.0.0.0 --port 8000
# 或
uvx kingdee-mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

SSE 端点 `/sse`，Streamable HTTP 端点 `/mcp`。HTTP 仅作传输，金蝶认证不变。

## WorkBuddy 接入（合并工程独有）

对话里说 **"连接金蝶"** 即可触发 `integrations/workbuddy/` 技能；或用脚本直接写配置（自动探测 uvx / python 启动方式，并保留已有其他 server）：

```bash
# 账号密码
python3 integrations/workbuddy/scripts/configure_kingdee_mcp.py \
  --server-url "http://your-server/k3cloud/" --acct-id "账套ID" \
  --auth-mode password --username "账号" --password "密码"

# 应用授权
python3 integrations/workbuddy/scripts/configure_kingdee_mcp.py \
  --server-url "http://your-server/k3cloud/" --acct-id "账套ID" \
  --auth-mode app_secret --app-id "AppId" --app-secret "AppSecret"
```

然后在 WorkBuddy「连接器管理 / 自定义 MCP」对 `kingdee` 点「信任/启用」，重启或重连 MCP。

## 工具列表（共 103 个，由 `server.py` 自动提取）

> 权威计数 = `server.py` 中 `@mcp.tool` 装饰器数量 = **97**。下文按业务域分组，完整定义见 `src/kingdee_mcp/server.py`。

- **通用单据/查询 (16)**：`kingdee_save_bill` · `kingdee_validate_bill` · `kingdee_submit_bills` · `kingdee_audit_bills` · `kingdee_unaudit_bills` · `kingdee_delete_bills` · `kingdee_cancel_bills` · `kingdee_void_bills` · `kingdee_close_bill` · `kingdee_unclose_bill` · `kingdee_forbid_bills` · `kingdee_enable_bills` · `kingdee_push_bill` · `kingdee_create_lx_billing` · `kingdee_query_bills` · `kingdee_view_bill`
- **审计合规/工作流/权限 (14)**：`kingdee_query_permission` · `kingdee_query_pending_approvals` · `kingdee_query_workflow_status` · `kingdee_workflow_approve` · `kingdee_query_audit_log` · `kingdee_query_operation_logs` · `kingdee_query_change_log` · `kingdee_query_approval_flow` · `kingdee_query_permission_changes` · `kingdee_query_data_backup` · `kingdee_create_and_audit` · `kingdee_push_and_audit`
- **成本核算 (12)**：`kingdee_query_material_cost` · `kingdee_query_cost_calculation` · `kingdee_save_cost_adjustment` · `kingdee_query_finished_product_cost` 等
- **生产制造 (12)**：`kingdee_query_production_orders` · `kingdee_save_production_order` · `kingdee_query_mrp_result` · `kingdee_push_production_pick` 等
- **库存 (11)**：`kingdee_query_inventory` · `kingdee_query_stock_bills` · `kingdee_push_stock_transfer` · `kingdee_query_transfer_direct` 等
- **元数据/SQL 探查 (7)**：`kingdee_get_fields` · `kingdee_list_forms` · `kingdee_get_bill_template` · `kingdee_discover_tables` 等
- **固定资产 (6)**：`kingdee_query_fixed_asset` · `kingdee_save_asset` · `kingdee_query_asset_depreciation` 等
- **采购 (5)**：`kingdee_query_purchase_orders` · `kingdee_query_purchase_requisitions` · `kingdee_query_purchase_inquiry` 等
- **基础资料/系统 (5)**：`kingdee_query_materials` · `kingdee_query_partners` · `kingdee_query_user` · `kingdee_query_role` · `kingdee_query_system_config`
- **销售/费用 (4)**：`kingdee_query_sale_orders` · `kingdee_query_sale_quotations` · `kingdee_query_expense_reimburse` · `kingdee_query_loan_balance`
- **统计 (2)**：`kingdee_usage_stats` · `kingdee_usage_report`
- **财务报表 (1)**：`kingdee_query_report`（科目余额表/账龄分析表等总账报表）
- **其他 (2)**：`kingdee_refresh_metadata` · `kingdee_query_quality_inspections`

## 支持的单据类型（form_id）

`form_id` 来自 `src/kingdee_mcp/server.py` 内硬编码字典 **`FORM_CATALOG`（57 条）**，每条含 `name/alias/desc/fields/business_rules/db_tables`。工具对 `form_id` 是**开放参数，任意金蝶 form_id 均可使用**，不限于下表（代表性 11 条）：

`PUR_PurchaseOrder`(采购订单) · `SAL_SaleOrder`(销售订单) · `STK_InStock`(采购入库单) · `SAL_OUTSTOCK`(销售出库单) · `STK_MisDelivery`(其他出库单) · `STK_Miscellaneous`(其他入库单) · `STK_TransferDirect`(直接调拨单) · `BD_Material`(物料) · `BD_Customer`(客户) · `BD_Supplier`(供应商) · `STK_Inventory`(即时库存)

## 开发 / 自定义

基于 FastMCP，在 `server.py` 加 `@mcp.tool()` 即可扩展；`FORM_CATALOG` 增加条目即可扩充对象识别。

## License

MIT。原始代码版权归各自原作者（见 `NOTICE`）。本工程与金蝶软件公司无任何隶属或授权关系。
