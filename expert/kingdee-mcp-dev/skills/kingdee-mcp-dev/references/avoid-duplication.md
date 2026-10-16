# 防止重复开发（必读红线）

> 适用：主理人排期、范探源出映射、寇豆码写工具、严过关回归时都要遵守。
> 现状：kingdee-mcp 已有 **97 个 `@mcp.tool`**（2026-08-07 实测 97：87 → 91 为 4 个查询类新增 `kingdee_query_loan_balance` / `kingdee_query_sales_outstock` / `kingdee_query_delivery_notice` / `kingdee_query_stock_in`；91 → 97 为 6 个标准动作通用工具新增 `kingdee_cancel_bills` / `kingdee_void_bills` / `kingdee_close_bill` / `kingdee_unclose_bill` / `kingdee_forbid_bills` / `kingdee_enable_bills`），覆盖 13 大业务域。盲目按 ApiDoc 模块逐个新建工具会大量重复。

## 核心认知：通用工具是 FormId 参数化的

下面这些工具**接收 FormId 参数**，单个就能服务任意单据的标准动作，**不要为每个模块再各建一个**：

| 标准动作 | 复用工具 |
|----------|----------|
| 保存 | `kingdee_save_bill` |
| 提交 | `kingdee_submit_bills` |
| 审核 | `kingdee_audit_bills` |
| 反审核 | `kingdee_unaudit_bills` |
| 查看 | `kingdee_view_bill` |
| 删除 | `kingdee_delete_bills` |
| 下推 | `kingdee_push_bill` |
| 单据查询 | `kingdee_query_bills` |
| 保存前校验 | `kingdee_validate_bill` |
| 保存并审核 | `kingdee_create_and_audit` |
| 下推并审核 | `kingdee_push_and_audit` |
| 撤销 | `kingdee_cancel_bills` |
| 作废 | `kingdee_void_bills` |
| 整单关闭 | `kingdee_close_bill` |
| 反关闭 | `kingdee_unclose_bill` |
| 禁用 | `kingdee_forbid_bills` |
| 反禁用 | `kingdee_enable_bills` |

> 例：采购订单保存 = `kingdee_save_bill(FormId="PUR_PurchaseOrder", ...)`，无需新建 `kingdee_save_purchase_order`。

## 标准动作通用工具（6 个新增，含关键格式要点）

2026-08-07 新增的 6 个 FormId 参数化通用工具（标准动作，非某单专用；QA 真机复测通过）：

| 工具 | server.py def 行号 | action | 端点 | 适用 |
|------|--------------------|--------|------|------|
| `kingdee_cancel_bills` | ~L3365 | CancelAssign（撤销） | **独立端点** CancelAssign.common.kdsvc | 单据 + 基础资料 |
| `kingdee_void_bills` | ~L3395 | Cancel（作废） | ExecuteOperation.common.kdsvc | 单据 |
| `kingdee_close_bill` | ~L3420 | 随表单动态解析（YLBillClose/BillClose） | ExecuteOperation | 单据 |
| `kingdee_unclose_bill` | ~L3459 | 随表单动态解析（YLUnBillClose/Unclose） | ExecuteOperation | 单据 |
| `kingdee_forbid_bills` | ~L3498 | Forbid（禁用） | ExecuteOperation | 基础资料 |
| `kingdee_enable_bills` | ~L3522 | Enable（反禁用） | ExecuteOperation | 基础资料 |

**关键格式要点（踩坑教训，勿再犯）**：
1. **端点正确拼写 = `ExecuteOperation`**（`Kingdee.BOS.WebApi.ServicesStub.DynamicFormService.ExecuteOperation.common.kdsvc`）；`ExcuteOperation` 是官方论坛的拼写错误——用错拼写会全线返回 .NET NullReferenceException「未将对象引用设置到对象的实例」。
2. **请求格式**：操作编码必须放**顶层 `opNumber` 字段**（与 formid 平级），`data` 只放业务参数 JSON 字符串（`{"Ids":"1,2,3"}` 或 `{"Numbers":[...]}`）。把操作名塞进 data 内部同样触发空引用。
3. **撤销走独立端点 CancelAssign**（无需 opNumber）；作废/禁用/反禁用/整单关闭/反关闭**无独立端点**，必须走 ExecuteOperation（金蝶标准设计）。
4. **action 命名**：禁用=Forbid、反禁用=Enable（**不是 UnForbid**；Disable 已废弃）；作废=Cancel（**不是 Invalid**，全库无 Invalid 常量）；整单关闭/反关闭 action 随表单变化（SAL_SaleOrder=YLBillClose/YLUnBillClose、PUR_PurchaseOrder=BillClose/BillUnClose），工具内部按表单元数据 Operations 中文名动态解析。
5. **标准动作覆盖现状**：删除/暂存/保存/查看/提交/审核/反审核/下推/批量保存/单据查询（原有 10 个）+ 撤销/作废/整单关闭/反关闭/禁用/反禁用（新增 6 个）→ **核心标准动作 14/15 全覆盖**（15 个中仅「申请单退款」为人人报销专属动作不走通用工具）；报表查询已由 `kingdee_query_report`（GetSysReportData，~L7177）覆盖。

## 专用工具（已存在，须扩展而非新建）

以下模块已有**专用**工具，新需求优先扩展它们（加参数/分支），不要并行再建同名逻辑的。
（全部带 `kingdee_` 前缀，与 `bin/kmcp tools` 输出、源码 `@mcp.tool(name=...)` 完全一致）

- 销售：`kingdee_query_sale_orders` / `kingdee_query_sale_quotations` / `kingdee_query_sales_outstock`（2026-08-07 新增，对应 ApiDoc 销售出库 SAL_OUTSTOCK；本环境客户字段 Key 为 `FCustomerID` 非 `FCustId`）/ `kingdee_query_delivery_notice`（发货通知单，FormId=SAL_DELIVERYNOTICE，默认字段含 FCustomerID.FName）
- 人人报销：`kingdee_query_expense_reimburse` / `kingdee_query_loan_balance`（后者 2026-08-07 新增，对应 ApiDoc「历史借款余额」FormId=ER_HistoricalLoanBalance；**注意目标账套若未启用该模块则查不到数据**）
- 采购：`kingdee_query_purchase_orders` / `kingdee_query_purchase_requisitions` / `kingdee_query_purchase_inquiry` / `kingdee_query_purchase_order_progress` / `kingdee_query_supplier_quotes`
- 库存/库存单据：`kingdee_query_inventory` / `kingdee_query_stock_bills` / `kingdee_query_stock_transfer_apply` / `kingdee_query_transfer_apply` / `kingdee_query_transfer_direct` / `kingdee_query_transfer_pending_detail` / `kingdee_push_stock_transfer` / `kingdee_query_misc_movement_detail` / `kingdee_query_stock_in`（采购入库单，FormId=STK_InStock，默认字段含 FSupplierId.FName）
- 生产：`kingdee_query_production_orders` / `kingdee_query_production_plan` / `kingdee_query_production_report` / `kingdee_query_production_stock_in` / `kingdee_query_production_pick_materials` / `kingdee_query_mrp_result` / `kingdee_save_production_order` / `kingdee_submit_production_orders` / `kingdee_audit_production_orders` / `kingdee_push_production_pick` / `kingdee_push_production_stock_in` / `kingdee_view_production_order`
- 成本：`kingdee_query_cost_adjustments` / `kingdee_query_cost_calculation` / `kingdee_query_cost_centers` / `kingdee_query_cost_items` / `kingdee_query_cost_trend` / `kingdee_query_finished_product_cost` / `kingdee_query_instant_cost_compare` / `kingdee_query_material_cost` / `kingdee_query_material_cost_usage` / `kingdee_query_material_target_cost` / `kingdee_query_product_standard_cost` / `kingdee_save_cost_adjustment`
- 资产：`kingdee_query_asset_card` / `kingdee_query_asset_depreciation` / `kingdee_query_asset_scrape` / `kingdee_query_asset_transfer` / `kingdee_query_fixed_asset` / `kingdee_save_asset`
- 其他：`kingdee_query_partners` / `kingdee_query_user` / `kingdee_query_role` / `kingdee_query_permission` / `kingdee_query_workflow_status` / `kingdee_query_approval_flow` / `kingdee_query_audit_log` / `kingdee_query_change_log` / `kingdee_query_operation_logs` / `kingdee_query_pending_approvals` / `kingdee_query_system_config` / `kingdee_query_number_rule` / `kingdee_query_sequence` / `kingdee_query_report` / `kingdee_query_data_backup` / `kingdee_query_quality_inspections` / `kingdee_create_lx_billing` / `kingdee_workflow_approve`
- 元数据/探查：`kingdee_get_fields` / `kingdee_get_bill_template` / `kingdee_discover_metadata_candidates` / `kingdee_discover_tables` / `kingdee_discover_columns` / `kingdee_describe_table` / `kingdee_list_forms` / `kingdee_refresh_metadata`

> ⚠️ **已知历史重复（勿处理）**：`kingdee_query_permission` 在源码中被注册了两次（启动有 WARNING，无害）。
> QA 回归时把它当作「既有重复」忽略，不要为「消除重复」而新增第三个或改动既有注册。

## 决策树（动手前必走）

```
目标：把 ApiDoc {领域→模块→操作} 集成进来
  │
  ├─ 操作 ∈ 标准单据动作（保存/提交/审核/反审核/查看/删除/下推/单据查询）？
  │     ├─ 是 → 查通用工具（见上表）是否已存在？
  │     │        ├─ 是 → REUSE（传 FormId），【禁止新建】
  │     │        └─ 否 → 先确认不是历史遗漏；一般不应出现
  │     └─ 否（专属动作，如 申请单退款 / 报表导出 / 暂存特殊逻辑）？
  │              ├─ 该模块已有专用 `kingdee_<动作>_<模块>` 工具？
  │              │     ├─ 是 → EXTEND 既有工具（加参数/分支），【禁止并行新建】
  │              │     └─ 否 → 仅在「需要二开字段/复杂拼包/通用工具服务不好」时
  │              │              新建专用工具，并在工具 docstring 注明 FormId 与为何不复用通用工具
  │
  └─ 任何新建/扩展后，跑 `bin/kmcp tools <模块关键字>` 复核无同名/同 FormId 的重复工具
```

## 落地手段

- **查重命令**：`python bin/kmcp tools <关键字>`（如 `python bin/kmcp tools purchase` / `python bin/kmcp tools save`）会扫描 `server.py` 的 `@mcp.tool` 名，列出已覆盖的工具，立刻判断是否重复。
- **统计**：`python bin/kmcp list-tools` 看总数变化（新增应是有理由的净增，而非批量重复）。
- **回归**：严过关回归时把「是否引入了与既有工具同 FormId/同语义的重复工具」列为检查项。

## 判重口诀

> 先查通用（FormId 参数化）→ 再查专用（模块已建）→ 都无且确需特殊处理，才新建，并写明为什么不复用。

> 💡 **查重搜索陷阱**：`bin/kmcp tools` 按**子串匹配**工具名。注册名带下划线（如 `kingdee_query_stock_in`），用 `stockin` 会**漏匹配**；搜「采购入库单」请用 `stock_in`（含下划线）。同理 `deliverynotice` 漏匹配，用 `delivery_notice`。
