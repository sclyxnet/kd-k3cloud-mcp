# Kingdee MCP Unified（金蝶云星空 MCP · 双登录合并版）

> ⚠️ **第三方开源，非金蝶官方出品。** 与金蝶软件（Kingdee）无任何隶属或授权关系。任何对外文案**不得**标注"金蝶官方""官方技术号"。

**Kingdee MCP Unified** 是把两个社区项目**合并成一个工程**的结果：

| 组成 | 来源 | 作用 |
|------|------|------|
| `src/kingdee_mcp/` | [WaHaiLong/KingdeeMCP](https://github.com/WaHaiLong/KingdeeMCP)（PyPI `kingdee-mcp`） | 真正的 MCP Server，**97 个工具** |
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

## 功能特性

- **97 个工具**：覆盖生产、成本、资产、审计、采购、销售、库存、财务报表等 13+ 业务域（清单见下文，权威来源 `server.py`）。
- **双登录**：账号密码 / 应用授权，一键切换。
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

## 工具列表（共 97 个，由 `server.py` 自动提取）

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
