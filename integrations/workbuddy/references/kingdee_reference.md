# 金蝶云星空 MCP 参考（kingdee-mcp >= 0.3.0，双登录版）

> 第三方开源项目（github.com/WaHaiLong/KingdeeMCP，PyPI: `kingdee-mcp`），**非金蝶官方出品**。
> 本参考随 `kd-k3cloud-mcp` 合并工程维护。**工具总数以 `src/kingdee_mcp/server.py` 中 `@mcp.tool` 装饰器为准 = 97 个**（下文清单由脚本从源码自动提取，避免人工过时）。

## 仓库与安装
- GitHub（合并工程）: https://github.com/sclyxnet/kd-k3cloud-mcp
- 上游 GitHub: https://github.com/WaHaiLong/KingdeeMCP
- PyPI: `pip install kingdee-mcp` 或 `uvx kingdee-mcp`（推荐，免安装运行）
- 官网: https://wahailong.github.io/KingdeeMCP/

## 两种登录方式（关键）
由环境变量 `KINGDEE_AUTH_MODE` 切换，默认 `password`。

| AUTH_MODE | 认证端点 | 必需环境变量 | 说明 |
|-----------|----------|--------------|------|
| `password`（默认） | `ValidateUser` 账号密码 | `KINGDEE_USERNAME` + `KINGDEE_PASSWORD` | 以真实用户身份执行 WebAPI，携带该用户业务/数据权限，**推荐** |
| `app_secret` | `LoginByAppSecret` 应用授权 | `KINGDEE_APP_ID` + `KINGDEE_APP_SEC` | 以应用身份登录，无需真实用户账号；报表等依赖数据权限的查询会受限 |

> 历史：0.2.0 曾砍掉 AppSecret 改为仅 ValidateUser；本合并工程在 0.3.0 重新加回，做成可插拔双登录（`server.py` 的 `_login()` 按 `KINGDEE_AUTH_MODE` 分派）。
> 若你的金蝶环境要求 `LoginByAppSecret` 额外传入 `username` 参数，请在 `server.py` 的 `_login()` 中 `payload` 补入（端点入参顺序：`acctId, appId, appSecret, lcid`）。

## 环境变量（必填，取决于登录方式）
| 变量 | 说明 | 示例 |
|------|------|------|
| KINGDEE_SERVER_URL | 金蝶服务器地址，需含 `/k3cloud/` 后缀 | http://your-server/k3cloud/ |
| KINGDEE_ACCT_ID | 账套 ID | your-acct-id |
| KINGDEE_AUTH_MODE | 登录方式：`password`(默认) \| `app_secret` | password |
| KINGDEE_USERNAME | 金蝶账号（password 模式，建议专用集成账号，非 Administrator） | your-username |
| KINGDEE_PASSWORD | 金蝶账号密码（password 模式，ValidateUser 登录） | your-password |
| KINGDEE_APP_ID | 第三方应用 AppId（app_secret 模式） | your-app-id |
| KINGDEE_APP_SEC | 第三方应用 AppSecret（app_secret 模式） | your-app-secret |

## 环境变量（可选，SQL Server 探查）
| 变量 | 说明 | 示例 |
|------|------|------|
| MCP_SQLSERVER_HOST | SQL Server 主机 | localhost |
| MCP_SQLSERVER_PORT | 端口（默认 1433） | 1433 |
| MCP_SQLSERVER_DATABASE | 数据库名 | AIS20260309171043 |
| MCP_SQLSERVER_USER | SQL Server 用户（建议只读） | sa |
| MCP_SQLSERVER_PASSWORD | 密码 | xxxx |

## 启动方式（MCP 客户端配置）
**方式 A（推荐，需 uv）：**
```json
{ "command": "uvx", "args": ["kingdee-mcp"], "env": { "KINGDEE_SERVER_URL":"...", "KINGDEE_ACCT_ID":"...", "KINGDEE_AUTH_MODE":"password", "KINGDEE_USERNAME":"...", "KINGDEE_PASSWORD":"..." } }
```
**方式 B（无 uv，生产更稳）：** pip 安装后改用模块启动
```json
{ "command": "python", "args": ["-m", "kingdee_mcp.server"], "env": { "KINGDEE_SERVER_URL":"...", "KINGDEE_ACCT_ID":"...", "KINGDEE_AUTH_MODE":"app_secret", "KINGDEE_APP_ID":"...", "KINGDEE_APP_SEC":"..." } }
```
> 若 `uvx` 偶发报 `No module named 'mcp.server.fastmcp'`，清缓存 `uv cache clean` 重试，或直接用方式 B。
> 远程部署：`uvx kingdee-mcp --transport sse|streamable-http --host 0.0.0.0 --port 8000`（HTTP 仅作传输，金蝶认证不变）。

## 金蝶后台准备步骤
1. 准备金蝶云星空账号（password 模式）或第三方应用（app_secret 模式）。
2. 为对应账号/应用分配所需模块的操作权限。
3. `KINGDEE_SERVER_URL` 必须包含 `/k3cloud/` 后缀。

## 工具列表（共 97 个，由 server.py 自动提取）
按业务域分组（代表性工具，完整清单见 `src/kingdee_mcp/server.py`）：

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
- **财务报表 (1)**：`kingdee_query_report`（GetSysReportData：科目余额表 `GL_RPT_AccountBalance`、账龄分析表 `GL_AgingSchedule` 等总账报表）
- **其他 (2)**：`kingdee_refresh_metadata` · `kingdee_query_quality_inspections`

### 核心常用工具
- 元数据：`kingdee_list_forms`（搜表单）、`kingdee_get_fields`（字段列表）、`kingdee_get_bill_template`（套打/模板）
- 查询：`kingdee_query_bills`（通用，任意 form_id）、`kingdee_view_bill`（详情）、`kingdee_query_purchase_orders`、`kingdee_query_sale_orders`、`kingdee_query_stock_bills`、`kingdee_query_inventory`、`kingdee_query_materials`、`kingdee_query_partners`、`kingdee_query_report`
- 写操作：`kingdee_save_bill`、`kingdee_submit_bills`、`kingdee_audit_bills`、`kingdee_unaudit_bills`、`kingdee_delete_bills`、`kingdee_validate_bill`

## SQL Server 探查工具（可选，配置 MCP_SQLSERVER_* 后可用，4 个）
- `kingdee_discover_tables`：按关键字搜索数据库表名
- `kingdee_discover_columns`：按关键字搜索字段名（含所在表）
- `kingdee_describe_table`：查看表完整结构（字段、类型、主键、外键）
- `kingdee_discover_metadata_candidates`：根据 form_id 发现对应的数据库表名

## 支持的单据类型（form_id）
`form_id` 来自 `src/kingdee_mcp/server.py` 内硬编码字典 **`FORM_CATALOG`（57 条）**，每条含 `name/alias/desc/fields/business_rules/db_tables`。
下方为代表性 11 条；**工具对 form_id 是开放参数，任意金蝶 form_id 理论上均可使用**，不限于此表：

| form_id | 说明 |
|---------|------|
| PUR_PurchaseOrder | 采购订单 |
| SAL_SaleOrder | 销售订单 |
| STK_InStock | 采购入库单 |
| SAL_OUTSTOCK | 销售出库单 |
| STK_MisDelivery | 其他出库单 |
| STK_Miscellaneous | 其他入库单 |
| STK_TransferDirect | 直接调拨单 |
| BD_Material | 物料档案 |
| BD_Customer | 客户档案 |
| BD_Supplier | 供应商档案 |
| STK_Inventory | 即时库存 |

## 常见问题
- **认证失败**：检查所选登录方式的凭据是否正确，该账号/应用是否有对应模块的操作权限。
- **连接超时**：检查 `KINGDEE_SERVER_URL` 是否正确（需包含 `/k3cloud/` 后缀），确保服务器可访问。
- **公有云/私有云**：均支持，配置完全一致。
- **自定义工具**：基于 FastMCP 框架，在 `server.py` 中添加 `@mcp.tool()` 装饰器方法即可扩展。
