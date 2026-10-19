# 更新日志 (Changelog)

本项目所有重要变更都会记录在此文件。

格式参考 [Keep a Changelog](https://keepachangelog.com/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

> 当前 PyPI 版本：`0.3.9`（见 `pyproject.toml`）。本文件按功能里程碑汇总，未单独打 git tag。

---

## [0.3.9] — 2026-10-19（自然语言建单：中文→字段/编码 翻译链路）

> 用户诉求："我说要添加一个销售订单，哪些字段匹配哪些中文，查询参数去哪里找"——
> 让 AI 按元数据自动翻译，不需要用户报字段名。

### Added（新增）

- **`kingdee_search_fields`**（第 108 个工具）：**中文字段名 → 字段 key**。按中文名在元数据
  `Fields[].Name[2052]` 里搜（多关键词空格分隔），返回 {key, 中文名, 所在单据体, 是否必填,
  参照对象, 填写方式}。支持 `only_required` / `only_lookup` 过滤。数据来自 QueryBusinessInfo，
  非人工字典，任意 form_id 通用。
- **`kingdee_find_code`**（第 109 个工具）：**中文值 → 编码**。按中文名在参照对象里模糊查
  `{"FNumber": "...", "FName": "..."}`，如 客户"凤集"→CUST0005、物料"原料蛋"→S01。
  字段名不适用时自动带回该对象的建议字段（FStaffNumber/FDataValue 等官方惯例）。
- **SKILL.md 新增「自然语言建单五步流程」提示词**：定对象 → 中文字段翻译 → 中文值翻译
  （多条命中让用户确认）→ 组装+validate → save。AI 依此自动完成"添加销售订单"类请求。

### 树形账表 / 直接SQL账表的结论（真机 + 官方文档 open.kingdee.com/K3Cloud/help/BOS_Account.html）

账表四种类型（简单/树形/分页/直接SQL）的数据源都是**二开插件或 SQL**。实测账套中
`BOS_TreeSysReport`（树形账表模板）、`BOS_SQLReport`（直接SQL账表）是**设计器模板对象**，
**没有统一取数 WebAPI**（GetSysReportData 对二开账表仅在其实现标准协议时可用，且参数各不相同）。
二开账表取数两条路：① 配置 `MCP_SQLSERVER_*` 用 `kingdee_sql_search` 直查底层表；
② 二开封装自定义 API（kapi/v2）后经 HTTP 调用。已写入 SKILL.md「报表取数三分法」。

### 验证（真机 TEST20230518）

| 项 | 结果 |
|---|---|
| search_fields("客户 数量", SAL_SaleOrder) | ✅ 客户→FCustId(lookup=BD_Customer,必填) |
| find_code(BD_Customer,"凤集") | ✅ CUST0005 凤集食品集团有限公司蛋品部 等 5 条 |
| find_code(BD_MATERIAL,"原料蛋") | ✅ S01 商用原料蛋-Y(2021) 等 4 条 |
| 五步流程必填集 | ✅ FDate/FCustId/FLDatetime/FMinPlanDeliveryDate |

---


## [0.3.8] — 2026-10-19（报表专用 API：库存分页报表 StockReportQueryService）

> 用户指正：**报表查询有专门的报表 API，不是单据/基础资料那一套**。
> 依据金蝶社区 kb 527582059091789824（GetSysReportData）与 kb 384025718453622528（库存分页报表）。

### 报表 API 的正确分工（实证）

| 报表种类 | 端点 | 状态 |
|---|---|---|
| 财务总账类账表（科目余额表等） | `DynamicFormService.GetSysReportData`（HTTP 双字段 formid+data，Model 必录，FilterString 数组格式） | ✅ 0.3.4 前已有，本轮真机复验（科目余额表 22 行真实数据） |
| **供应链库存分页账表**（物料收发明细/汇总、库存台账、库存账龄等） | `Kingdee.K3.SCM.WebApi.ServicesStub.StockReportQueryService.GetReportData,Kingdee.K3.SCM.WebApi.ServicesStub`（版本 ≥ PT-146906 [8.0.0.202203]） | ✅ **本轮新增** |
| **财务报表系统模板报表**（资产负债表/利润表/现金流量表等，用户 2026-10-19 指正补充） | `Kingdee.BOS.KDS.ServiceFacade.ServicesStub.KDSReportAPIStub.GetReportData,Kingdee.BOS.KDS.ServiceFacade.ServicesStub` | ✅ **本轮新增** |

**关于 KDS 报表 API 的重要更正**：此前代码注释写「KDSReportAPI 一律 Unknown Error 不可用」——
系**端点名不完整**所致（漏了逗号后的 `Kingdee.BOS.KDS.ServiceFacade.ServicesStub` 组件后缀）。
补全后端点可用。其参数与另两种完全不同：**不用 form_id**，按报表系统「报表模板编码 + 核算维度」取数：

```json
{"parameters":["{\"ReportType\":1,\"ReportNumber\":\"BBMB0001\",\"AcctSystemNumber\":\"KJHSTX01_SYS\",
  \"AcctPolicyNumber\":\"KJZC01_SYS\",\"OrgNumber\":\"100\",\"CurrencyNumber\":\"PRE001\",
  \"CurrUnitNumber\":\"JEDW01_SYS\",\"CycleType\":4,\"Year\":2023,\"Period\":5,
  \"DataType\":\"Json\",\"ResultType\":\"0\"}"]}
```

实测该账套无 `BBMB0001` 模板（报错「未找到对应参数的报表模板」= 参数结构正确、模板不存在）；
ReportNumber 与核算维度编码需从财务报表系统 / 官方「报表API工具」（kb 316988267696445696）获取。

### 库存分页报表接口的三个关键差异（全部实测 2026-10-19）

1. **HTTP 层是 raw JSON body**：`Content-Type: application/json`，
   `body = {"parameters": ["<内层JSON字符串>"]}`。用 form-urlencoded `data=` 一律返回
   「参数错误，请检查！」——这与单据/通用接口完全不同（新增 `_post_parameters_json()`）。
2. **FSCHEMEID 必录且不能用默认方案**：过滤方案从 `BOS_FilterScheme`（表 `T_BAS_FILTERSCHEME`，
   主键即 FSCHEMEID，元数据驱动发现）查得。实测 `STK_StockDetailRpt` 有 55 个方案（1 默认 + 54 可用）。
3. 返回 `{"success":true,"CurQueryId":"...","data":[行对象]}`；**翻页时传回 CurQueryId**，
   此时过滤条件不再应用（从首次查询结果中取指定页）。

### Added（新增）

- **`kingdee_query_kds_report`**（第 107 个工具）：KDS 财务报表系统模板报表取数
  （ReportType/ReportNumber/AcctSystemNumber/AcctPolicyNumber/OrgNumber/CurrencyNumber/
  CurrUnitNumber/ScopeType/ProfitCenter/CycleType/Year/Period/DataType/ResultType 全参支持）。
  内置报错解读（「参数不支持」vs「未找到报表模板」分别指向参数结构与模板缺失）。
- **`kingdee_query_stock_report`**（第 105 个工具）：库存分页报表取数。
  入参 form_id / scheme_id / quickly_condition / more_condition / start_row / limit(≤10000) / field_keys / cur_query_id。
- **`kingdee_list_filter_schemes`**（第 106 个工具）：列出报表的过滤方案（标注 is_default/is_share），
  引导选非默认方案；无需 SQL（官方文档原需 `SELECT ... FROM T_BAS_FILTERSCHEME`，
  现经 `BOS_FilterScheme` 元数据对象直接查询）。
- **`_post_parameters_json()`**：parameters 包装的 raw JSON 调用辅助（带重试 + 会话保活）。
- `_QUERYABLE_MODEL_TYPES` 注释与权威分类 `note` 修正：**报表(900)可取数但必须走报表专用 API**，
  不能用 `kingdee_query_bills`（ExecuteBillQuery）。

### 验证情况（真机 TEST20230518）

| 项 | 结果 |
|---|---|
| `kingdee_list_filter_schemes(STK_StockDetailRpt)` | ✅ 55 个方案（1 默认 + 54 可用：成品蛋/鸡只/原料蛋…） |
| `kingdee_query_stock_report`（成品蛋方案） | ✅ 返回 3 行真实数据（FGUID/FSTOCKORGNAME…）+ CurQueryId |
| form data= 方式对照（反证） | ✅ 失败「参数错误」，证实必须 raw JSON |
| `kingdee_query_report`（科目余额表）复验 | ✅ 22 行（银行存款/集团应收/其他应收款） |

---

## [0.3.7] — 2026-10-19（FBaseObjectId 继承树 + ModelTypeId 全量对照 + 修复"只支持写死 48 个表单"）

### ① 重名对象真相：FBaseObjectId 树形继承（用户指正）

实测拉取 `BOS_ObjectType` 全量并带出 `FBaseObjectId.FID/FName`（该字段 LookUp 指向 BOS_ObjectType 自身）：

- **10545 条对象中 5261 条有父对象、5284 条为根** —— 支持层层扩展，重名是正常的。
- 以「采购订单」6 条为例，继承关系：

```
PUR_BillTemplate（采购业务单据模板）
  └─ PUR_PurchaseOrder（标准单据, 100）
       └─ dadc8800-6084-…（二开扩展, 100）
            └─ 45b97b74-007a-…（再扩展, 100）
BOS_SCMBillTemplate（1.2.5 供应链业务单据模板）
  └─ SCP_PurchaseOrder（供应商协同平台, 100）
BD_PurchaseOrderWarnObject（预警对象, 1300，独立）
Pur_MobPurchaseOrderList（移动列表, 1400，独立）
```

- WebAPI 只认**可读 form_id**（根或可读形态），GUID 扩展对象不认（见 0.3.6 实测）——
  扩展单据的二开字段需要用二开自己的可读 form_id（如 `lyx_gcxm` 这类）访问。

### ② FModelTypeId 全量对照表（从小到大，账套实测 10545 条）

| FModelTypeId | 类型 | 数量 | 样例 |
|---|---|---|---|
| 100 | 单据 | 1909 | 批号调整单、采购订单 |
| 220 | 系统参数 | 305 | 费用报销系统参数 |
| 400 | 基础资料 | 1871 | 物料、工程项目 |
| 500 | 界面/表单 | 4090 | 电子会计档案集成 |
| 600 | 套打模板 | 680 | 物料盘点（盲盘）套打模板 |
| 700 | 转换规则 | 69 | 销售订单-销售退货单 |
| 710 | 状态迁移图 | 20 | 其它入库单状态迁移图 |
| 800 | 弹性域/辅助属性 | 13 | 核算维度 |
| 900 | 报表 | 564 | 赠品统计报表 |
| 1300 | 预警 | 74 | 预警对象演示（帐表） |
| 1400 | 移动界面 | 937 | 移动单据列表 |
| 1600 | 万能报表 | 6 | 交叉数据源类万能报表模板 |
| 2200 | 日志归档 | 7 | 上机操作日志归档 |

> 字段来源：`BOS_ObjectType.FModelTypeId`（领域模型 Id）。中文类型名为按实测样例归纳，
> 非金蝶官方枚举文档。**WebAPI 可查询/操作**的只有 `100/400/900`（`_QUERYABLE_MODEL_TYPES`）。

### ③ 修复「只支持写死 48 个表单」的 bug

**Bug 本体**：本地 `FORM_CATALOG` 仅 48 个表单（单据 ~35 + 基础资料 8 + 其它），而账套实际有
1909 个单据 + 1871 个基础资料 —— **覆盖率不足 5%**。`kingdee_list_forms` 原本只搜这 48 个，
其余 95% 的对象 AI 根本发现不了。

**修复**：`kingdee_list_forms` 新增 `scope` 参数：

- `scope=all`（**默认**）：直接搜 `BOS_ObjectType` 全部可读 form_id（7179 个），
  每条带 `subsystem` / `model_type_name` / `queryable` / `in_catalog` 标注；
  `FORM_CATALOG` 降级为语义补充（desc/别名/推荐字段/业务规则，仅 48 个常用表单有）。
- `scope=queryable`：只搜可查询类型（单据/基础资料/报表）。
- `scope=catalog`：旧行为保留（仅本地 48 个）。
- 新增 `model_type` / `limit` 过滤；返回值带 `source` 说明数据来源。

**验证**（真机 TEST20230518）：`keyword=销售` 返回 10 个表单（`AP_SALOUTSTOCK` 销售出库单、
`BD_SaleGroup` 销售组等），全部不在原 48 个目录里（`in_catalog=False`）——修复前这些对象完全不可见。

---

## [0.3.6] — 2026-10-19（权威对象目录：BOS_ObjectType / T_META_OBJECTTYPE）

> 彻底解决「支持的单据/对象以什么为准」：改为直接读元数据对象注册表 `BOS_ObjectType`。
> 服务端恢复后完成真机验证（账套 `TEST20230518` / Id `6ad5b2e278002b`）。

### 实测证据链

1. `QueryBusinessInfo("BOS_ObjectType")` → `NeedReturnData.Id = "BOS_ObjectType"`（名称「业务对象」）、
   `PkFieldName = FID`、`Entrys[0].TableName = "T_META_OBJECTTYPE"`。**这正是用户指出的那张表。**
2. `ExecuteBillQuery(BOS_ObjectType)` 可查全量数据，字段：
   `FID`(= form_id)、`FName`(中文名)、`FSubSystemId.FNumber/FName`(子系统，如「基础资料」「采购管理」)、
   `FModelTypeId`(领域模型 Id = 元数据类型)、`FModelTypeSubId`、`FDevType`、`FISTEMPLATE`。
3. **账套实测规模**：共 **10545** 条对象，其中标准 form_id 格式 **7179** 条。
   按 `FModelTypeId`：单据(100) 1348、基础资料(400) 1240、界面/表单(500) 3175、
   报表(900) 373、移动界面(1400) 632、套打模板(600) 53、系统参数(220) 257、预警(1300) 66 等。
4. `BD_MATERIAL` → 子系统「基础资料」、`FModelTypeId=400`；`PUR_PurchaseOrder` → 「采购管理」、`100`。
   **与用户说的"BD_Material 为基础资料"完全一致。**

### ⚠️ 重要坑：FID 有两种形态，GUID 形态 WebAPI 不认

账套内**同名对象极多**（实测 635 个名称对应多个 FID；"采购订单"就有 6 条：`PUR_PurchaseOrder`、
两个 GUID、`BD_PurchaseOrderWarnObject`(预警)、`Pur_MobPurchaseOrderList`(移动列表)、`SCP_PurchaseOrder`(供应商协同)）。

实测 GUID 形态**不能用于 WebAPI**：
- `QueryBusinessInfo("45b97b74-007a-4a8f-af22-a52f1ae1b23c")` → `NeedReturnData` 为空；
- `ExecuteBillQuery(同一 GUID)` → 报「在运行时不允许加载标识为"45b97b74-…"」。

因此 `_fid_kind()` 区分 `standard`（可读 form_id，如 `PUR_PurchaseOrder`/`BD_MATERIAL`/`lyx_gcxm`）/
`guid`（36 位 GUID）/ `other`，**默认只返回 standard**，`include_guid=True` 才展开。

### Added（新增）

- **`kingdee_list_object_types`**（第 104 个工具）：列出账套**全部业务对象**，支持
  `keyword`（匹配 form_id/中文名）、`model_type`（中文名或数字，如"单据"/"100"/"基础资料"/"400"）、
  `subsystem`、`queryable_only`（只留单据/基础资料/报表）、`include_guid`、`limit`、`force_refresh`。
  返回 `total_in_ledger` / `standard_form_ids` / `model_type_legend`。
- **`_fetch_object_types()`**：分页拉取 `BOS_ObjectType` 全量（每页 2000），内存 + 磁盘缓存（30 分钟），
  磁盘缓存向后兼容旧格式。
- **`_authoritative_category(form_id)`**：从对象注册表查**权威分类**（`inferred: false`），
  只认可读 form_id（大小写不敏感兜底），查不到返回 None 由调用方降级。
- `_MODEL_TYPE_NAMES` / `_QUERYABLE_MODEL_TYPES`：`FModelTypeId` → 中文类型名映射，
  及"哪些类型可被 WebAPI 查询/操作"（100 单据 / 400 基础资料 / 900 报表）。

### Changed（变更）

- `kingdee_get_fields` / `kingdee_get_bill_template` / `kingdee_list_forms(verify=True)` 的
  `object_category` **升级为权威分类**（来源 `BOS_ObjectType(T_META_OBJECTTYPE)`），
  仅在查不到时才回退到 0.3.5 的结构推断（并保留 `inferred: true` 标注）。
  权威分类额外提供 `subsystem`（所属子系统）、`queryable`（是否适合 WebAPI 操作）。

### 验证情况（真机，TEST20230518）

| 项 | 结果 |
|---|---|
| `list_object_types` 全量拉取 | ✅ 10545 条，standard 7179 条 |
| `keyword=采购` + `queryable_only` | ✅ 65 条，全部为可读 form_id，无 GUID |
| `model_type=100`（单据） | ✅ 1425 条 |
| 权威分类 `BD_MATERIAL` / `PUR_PurchaseOrder` / `STK_InStock` / `BD_Supplier` | ✅ 基础资料 / 单据，subsystem 正确 |
| GUID 排除 + `include_guid` 开关 | ✅ |
| `get_fields` / `get_bill_template` 输出权威分类 | ✅ `inferred: false` |
| 大小写不敏感（`BD_Material`） | ✅ |

---

## [0.3.5] — 2026-10-19（对齐官方 SDK 8.2.0 + 元数据对象分类）

> 依据官方 `SDK_Python3.0_V8.2.0`（`kingdee.cdp.webapi.sdk-8.2.0-py3-none-any.whl`，
> 模块 `k3cloud_webapi_sdk`）核对接口面，并补全「元数据对象分类」。

### 与官方 SDK 的接口面对比（`K3CloudApiSdk` 方法逐一核对）

| 维度 | 官方 SDK | 本工程 |
|---|---|---|
| 认证 | **仅** AppId/AppSecret 签名（`x-api-signature` / `x-kd-signature` / HMAC-SHA256） | ✅ 额外支持账号密码 `ValidateUser`，双模式可切 |
| 数据中心/语言列表 | `GetDataCenters` | ✅ 有，且支持中文名解析、切换 |
| 元数据 | `QueryBusinessInfo` | ✅ 有，且已做缓存 + 中文解析 + 动态模板 |
| 分组信息 | `QueryGroupInfo` | ⚠️ 端点已补，**返回结构未实测**（服务端故障），未写解析 |
| 附件 | `AttachmentUpload` / `AttachmentDownLoad` | ⚠️ 端点已补，工具未加 |
| 异步轮询 | `InvokeMethod.QUERY`（`beginmethod=BeginQueryImpl` + `querymethod=QueryAsyncResult` + TaskId 轮询） | ⚠️ 端点已补，未接入 |

**结论：不整体替换为官方 SDK**（会丢掉账号密码登录与全部中文交互能力），改为把 SDK 暴露的端点补全，
使两种登录方式都能调用。

### Added（新增）

- **补齐 14 个官方 SDK 端点**（`_EP`，逐条注明来源与用途）：
  `bill_query`（BillQuery，JSON 结构返回，SDK 2023-09-14 新增）、`batch_save`、`draft`（暂存）、
  `allocate`（分配）、`cancel_allocate`、`flex_save`（弹性域保存）、`send_msg`、`group_save`、
  `disassembly`（拆单）、`group_delete`、`switch_org`（切换组织，多组织）、`workflow_audit`、
  `attachment_upload` / `attachment_download`、`group_info`（QueryGroupInfo）。
- **`MetadataValidator.object_category()`**：从元数据**结构特征**推断业务对象分类
  （单据 / 基础资料 / 报表 / 动态表单），并给出 `confidence` 与逐条 `evidence`。
  推断依据（均可从元数据直接观察，非猜测）：
  1. `NeedReturnData.Id` 即**业务对象 FID**（对应用户所说 `T_META_ObjectType` 的 FID）；
  2. form_id 命名前缀（`BD_`=基础资料、`PUR_/SAL_/STK_/AR_/AP_/GL_/FA_/PRD_`=业务单据、`GLR_/RPT_`=报表）；
  3. 主表存在 `FBillNo`（单据编号）→ 单据；
  4. 存在 `EntryEntity` 分录体 → 单据（基础资料通常无分录）；
  5. 无分录体且字段较少 → 基础资料。
- `kingdee_get_fields` / `kingdee_get_bill_template` / `kingdee_list_forms(verify=True)` 输出新增
  `object_category`；模板新增 `_pk_field`（元数据主键，如 `FID`）。

### 关于「支持的单据应以元数据为准」

已确认的事实边界（避免误导）：

- `QueryBusinessInfo` 返回 `NeedReturnData.Id` = 业务对象 FID、`Name` = 多语言名、`Entrys[].Key/TableName/Fields` = 结构，
  **但不返回对象分类**（基础资料/单据/报表）。其 `EntityType`（`HeadEntity`/`SubHeadEntity`/`EntryEntity`/`SubEntryEntity`）
  表达的是**单据体结构类型**，不是对象分类——这是两个不同的概念，勿混淆。
- 因此对象分类目前为**结构推断**（已标注 `inferred: true` + 依据）。权威分类的两条路：
  1. SQL 探查 `T_META_ObjectType`（现有 `kingdee_discover_table` 可直接查，需配置 `MCP_SQLSERVER_*`）；
  2. `QueryGroupInfo` —— 端点已补，但**返回结构本环境尚未实测**，服务端恢复后需先探测再写解析，不能凭猜测消费。

### 验证情况

| 项 | 结果 |
|---|---|
| 编译 + 方法归属（防上轮 `validate_and_fix` 被吞的回归复检） | ✅ |
| 对象分类推断 `PUR_PurchaseOrder` | ✅ `单据` / `confidence=high` / 3 条依据 |
| `get_fields` / `get_bill_template` 输出 `object_category`、`_pk_field` | ✅ |
| `validate_bill` 无回归 | ✅ |
| 新增 14 个端点的真机调用 | ⏸ **未验证**：金蝶服务端持续故障（登录返回 `sa 登录失败`），需联网用例全部受阻 |

---

## [0.3.4] — 2026-10-19（元数据驱动：对象/字段/模板不再写死）

> 核心变化：**表单标识、表单名、物理表名、字段清单、必填项、分录体 key 全部改为从金蝶元数据动态读取**，
> 不再依赖本地写死的 `BILL_TEMPLATES` / `FORM_CATALOG` 字段表。本地目录降级为「可搜索索引 + 语义补充」。

### 元数据来源（对应服务端实现）

`DynamicFormService.QueryBusinessInfo` 返回 `Result.NeedReturnData`：

| 返回字段 | 含义 | 用途 |
|---|---|---|
| `Id` / `Name` / `PkFieldName` | 业务对象标识、多语言名、主键 | 表单名、主键字段 |
| `Entrys[].Key` | 单据体 key（`FBillHead` / `FPOOrderEntry` …） | **分录体 key 的权威来源** |
| `Entrys[].TableName` | 物理表名（`t_PUR_POOrder` / `t_PUR_POOrderEntry` …） | `db_tables` |
| `Entrys[].Fields[].Key` / `Name[{Key:2052}]` | 字段标识 / 中文描述 | 字段清单 |
| `Entrys[].Fields[].MustInput` | 是否必录 | 必填项校验 |
| `Entrys[].Fields[].LookUpObjectFormId` | 基础资料/单据参照来源 | 告诉调用方编码该填哪个对象 |

即服务端 `T_META_OBJECTTYPE` + `FKERNELXML` 的结构化输出，等价于内部
`FormMetaDataCache.GetCachedFormMetaData(ctx, formId)` 的 WebAPI 版本。

### Added（新增）

- **`_build_template_from_metadata(validator, form_id)`**：从元数据动态生成「最小可保存 model 骨架」，
  **任意 form_id 都支持**（不再局限于预置的 3 个）。顶层必填 + 主事务分录必填，参照型字段自动给出
  `{"FNumber": "<来源对象 编码>"}` 提示（如 `FPurchaseOrgId → ORG_Organizations`、`FMaterialId → BD_MATERIAL`）。
- **`FieldDef` 扩展** `table_name`（分录物理表名）/ `lookup_form`（字段参照来源）。
- **`MetadataValidator` 扩展** `form_name`（元数据表单名）/ `tables`（全部物理表）/ `entry_bodies()`（过滤子结构噪音后的真实分录体）。
- **`kingdee_list_forms` 新增 `verify` / `verify_limit`**：用 `QueryBusinessInfo` 验证候选 form_id 是否真实存在于本账套，
  并把名称/表名替换为元数据返回值（`name_source=metadata`）。
- **`kingdee_get_bill_template`**：优先元数据动态生成（`source=metadata`），元数据不可达才降级本地模板（`source=hardcoded_fallback` 并明确告警）。

### Fixed（修复）

- **`kingdee_save_bill` / `kingdee_validate_bill` 全线崩溃（本次改造引入的回归）**：在类中部插入模块级函数时，
  `return tpl` 之后的 4 空格缩进代码被 Python 当作同一函数体内的不可达代码，导致
  `_edit_distance` / `find_similar_field` / `validate_and_fix` 三个原类方法被"吞"进模块级函数，
  报 `AttributeError: 'MetadataValidator' object has no attribute 'validate_and_fix'`。已将这三个方法搬回类内，
  大小写自动纠错（`FpurchaseOrgId→FPurchaseOrgId`、`FmaterialId→FMaterialId`）复测恢复。
- **`kingdee_get_fields` 的 `save_template` 含噪音分录体**：旧逻辑把所有有必填子字段的 Entry 都塞进骨架
  （`FPOOrderFinance`/`FIinstallment` 等）。改为与 `get_bill_template` 共用 `_build_template_from_metadata`，只保留主事务分录。

### 验证情况

| 项 | 结果 |
|---|---|
| 元数据动态生成模板（`PUR_PurchaseOrder`，磁盘缓存命中） | ✅ `source=metadata`，7 张物理表、5 个顶层必填、5 个分录必填全部来自元数据 |
| `get_fields` name/db_tables 走元数据 | ✅ `name=采购订单`、7 张表 |
| 分录体 key 错误拦截 | ✅ 报错并列出正确单据体 `FPOOrderEntry` |
| 必填缺失检测 | ✅ `['FDate','FPurchaseOrgId','FPurchaseDeptId','FBillTypeID']` |
| 大小写自动纠错（`validate_and_fix`） | ✅ 回归修复后恢复 |
| 无缓存表单实时拉元数据（`SAL_SaleOrder` 等） | ⏸ **未验证**：金蝶服务端当时持续故障（登录返回 `sa 登录失败`/`GetDataCenterContextByID` 异常），需联网的用例全部受阻 |

> ⚠️ 服务端可用性：测试期间金蝶服务器多次出现间歇性登录失败（管理中心连不上账套数据库，
> 错误含 `用户 'sa' 登录失败`）。走磁盘缓存的用例全部通过；需实时联网的用例待服务端恢复后补验。

---

## [0.3.3] — 2026-10-16（全量 103 工具真机实测）

> 对全部 **103 个工具**逐一直连真实账套执行验证（写操作用不存在的单据号，不产生业务数据）；
> 另做 **save → view → delete 真实闭环**验证写链路，创建后已删除、无残数据。

### Fixed（修复）

- **`kingdee_view_production_order` 必抛 `AttributeError`**：代码调用了 `params.to_view_payload()`，
  但该方法在 `ViewInput` 上**从未定义**（全文件仅此一处调用），导致该工具 100% 不可用。
  改为与 `kingdee_view_bill` 一致的 `_post_raw("view", form_id, {"Id": bill_id})`，并支持 `mode=summary/full`。
- **采购订单模板分录体 key 错误（隐蔽性极高）**：`BILL_TEMPLATES["PUR_PurchaseOrder"]` 给的
  `FPurchaseOrderEntry` 是错的，正确实体名是 **`FPOOrderEntry`**（采购订单实体为 `POOrder`，表 `t_PUR_POOrder`）。
  写错时金蝶收不到整段分录，会误报「物料编码是必填项」「订单数量必须大于0」，而本地校验全过，极难排查。
  模板已按真机实测重写（补齐 `FDate`/`FPurchaseDeptId`/`FUnitId`/`FPriceUnitId`/`FStockUnitID`/交货日期）。
  已核对：`SAL_SaleOrder` 的 `FSaleOrderEntry` 是**正确**的，未改动。
- **`kingdee_validate_bill` 会被误导**：上一条场景下校验报「通过」但保存必失败。
  校验器新增**分录体 key 核对**：顶层数组字段若不在本表单已知单据体中，给出明确告警并列出正确的单据体名。

### 实测结论（TEST20230518）

| 分类 | 数量 | 说明 |
|---|---|---|
| 只读工具正常 | 70 | 返回真实业务数据 |
| 写工具链路正常 | 25 | 端点可达、参数格式正确（以不存在单据号调用，金蝶正常拒绝） |
| 业务级拒绝 | 7 | SQL Server 未配置 2 项；专用服务端点不存在 5 项（已降级为明确提示） |
| 需手工指定 | 1 | `kingdee_switch_data_center`（需传账套标识，已单独验证通过） |
| **代码缺陷** | **0** | — |

写闭环实证：`save` 成功（FID `190511` / 单号 `CGDD088513`）→ `view` 确认存在 → `delete` 成功 → 复查确认已删除。

---

## [0.3.2] — 2026-10-16（真机实测修复）

> 本轮改动全部在真实金蝶服务器 `TEST20230518` 账套上端到端实测验证（11/11 通过）。

### Added（新增）

- **登录信息全量运行时切换**：`kingdee_switch_login` 支持切换 服务器地址 / 账套 / 用户名 / 密码 / 登录方式 / AppID / AppSecret / LCID，
  任意一项可单独改，切换后立即重置会话并在下一次调用自动重连；`persist=True` 可写回 `~/.workbuddy/mcp.json` 永久生效。
- **`kingdee_show_login_info`**：查看当前连接与登录配置，密码 / AppSecret 自动脱敏。
- **`kingdee_test_login`**：立即试登录并报告结果，失败给出明确原因。
- **LCID 语言映射表（412 条）**：`2052=中文(简体)`、`1033=英语(美国)`、`3076=中文(繁體·香港)`、`1028=中文(繁體·台灣)` 等，
  `_LCID_NAMES_ZH` / `_LCID_NAMES_EN` 双表；`kingdee_list_data_centers` 直接从账套 `LocaleValueName` 推导支持的语言（无需额外请求），默认 2052 中文。
- **网络韧性**：`_NET_RETRY`（默认 3 次，`KINGDEE_NET_RETRY` 可调）+ 线性退避，网络超时 / 5xx / 会话失效自动重登重发。

### Fixed（修复）

- **6 个专用服务端点不存在**：真机实测 `UserService` / `RoleService` / `PermissionService` / `SequenceRuleService` /
  `NumberRuleService` / `SystemConfigService` 在部分金蝶版本返回 `...Service no found.`。
  现在自动降级：有可替代业务对象的（`user` → `SEC_User`）改走通用 `ExecuteBillQuery`；无可替代的给出明确中文提示，
  不再把底层 `InnerExWrapper` 堆栈抛给调用方。
- **会话失效误判**：原逻辑用 `"session" in resp.text` 宽松匹配，正常响应只要含 `SessionId` 字段名就会被误判失效，
  导致每次调用白白重登一次。改为只认明确失效措辞（`_SESSION_EXPIRED_MARKERS`）+ 401/419 状态码。
- **账套名解析误判**：`预生产` 账套的 `Number` 与 `Name` 同为「预生产」，旧逻辑「是 Number 就原样返回」会把中文名透传给登录接口。
  改为只有 `raw` 本身就是某账套 `Id` 才透传，其余一律解析为 `Id`。
- **`UserQueryInput` 默认字段不符**：真机实测 `SEC_User` 可用字段为 `FUserId/FName/FEMail`，旧默认值 `FUserID,FNumber,FDepartment.FName,FIsActive` 会报错，已修正。

---

## [Unreleased]

### Added（新增）

- **数据中心（账套）管理与中文交互**：把登录页「账套下拉框」（`AccountService.GetDataCenterList`）抽成 MCP 工具。
  - `kingdee_list_data_centers`：列出所有账套（中文名 / 账套号 / 登录 Id / 数据库类型 / 认证方式），无需登录即可调用。
  - `kingdee_switch_data_center(identifier)`：按中文名 / 账套号 / Id 切换账套并重置会话，下一次 API 调用自动用新账套重新登录。
  - `KINGDEE_ACCT_ID` 支持直接填中文账套名或账套号，登录前自动解析成登录用的 Id（金蝶 WebAPI 登录 `acctID` = 数据中心 `Id`）。

---

## [Unreleased-历史合并工程]

### Added（新增）

- **远程传输支持（HTTP / SSE / Streamable HTTP）**：`main()` 新增 `--transport`（stdio/sse/streamable-http，默认 stdio）、`--host`、`--port` 参数，并支持同名环境变量 `KINGDEE_MCP_TRANSPORT` / `KINGDEE_MCP_HOST` / `KINGDEE_MCP_PORT`。现在可将服务以 SSE（`/sse`）或 Streamable HTTP（`/mcp`）模式运行，便于部署到服务器或网关平台远程调用、免客户端安装。兼容老版本 mcp（<1.9 不支持 streamable-http 时自动回退 sse）。

---

## [0.2.1] - 2026-08-05

### Fixed（修复 · 文档）

- **修正改用账号密码登录的原因说明**：README「从 0.1.0 升级的破坏性变更」与 `server.py` `_login` docstring 原写为「为避免第三方应用授权的 APP 白名单限制、公有云/私有云通用」，该原因有误。正确原因：账号密码(ValidateUser) 以真实用户身份执行 WebAPI、携带该用户自身业务权限（含数据权限控制）；第三方应用授权(LoginByAppSecret) 以应用身份登录、不携带真实用户权限，报表等依赖数据权限的查询会受应用授权范围限制。无功能/行为变更。

---

## [0.2.0] - 2026-08-05

### Changed（变更）

- **版本对齐与重新发版**：本地源码自 2026-07-19 起已包含 86 工具、账号密码登录、SQL Server 探查等大量更新，但 PyPI 上仍停留在 2026-03-25 发布的旧 `0.1.0`（仅 13 工具 + AppSecret 登录）。本版将 PyPI 包与源码对齐，统一为 `0.2.0`。
- **README / 文档同步**：PyPI 展示的 README 已更新为 86 工具 + 账号密码登录的说明（此前 PyPI 长期展示旧版文档）。

### Added（新增 · 相对 PyPI 旧 0.1.0）

- 86 个工具（生产 / 成本 / 资产 / 审计 / 采购 / 销售 / 库存 / 工作流 / 元数据 / 系统 / 统计等 13 大业务域）。
- 4 个 SQL Server 探查工具（`kingdee_discover_tables` / `kingdee_discover_columns` / `kingdee_describe_table` / `kingdee_discover_metadata_candidates`），需配置 `MCP_SQLSERVER_*`。
- 元数据动态查询（`get_bill_template` / `validate_bill` / `refresh_metadata`），元数据本地缓存。
- MCP 使用日志系统、错误自描述、强制 HTTP/1.1 解决金蝶 WebAPI 偶发 502。
- **财务报表查询工具 `kingdee_query_report`**：通过专用 `GetSysReportData`（KDSReportAPIService）端点查询总账/财务报表，与单据查询（ExecuteBillQuery）分属不同服务。已实测确认科目余额表 `GL_RPT_AccountBalance`、总账账龄分析表 `GL_AgingSchedule`（无 `RPT_` 前缀）；其余报表 formId 待逐张查证。内层过滤参数（账簿/年度/期间/科目等）由调用方按账套透传，避免臆造字段名。

### Breaking（破坏性变更）

- **登录方式变更**：移除第三方应用授权登录（`LoginByAppSecret`），改为仅账号密码（`ValidateUser`）。旧环境变量 `KINGDEE_APP_ID` / `KINGDEE_APP_SEC` **已失效**，须改用 `KINGDEE_PASSWORD`。详见 README「从 0.1.0 升级的破坏性变更」。

### Fixed（修复 · 文档）

- README「常见问题」新增 `uvx` 启动报 `No module named 'mcp.server.fastmcp'` 的排查（清缓存或改用 `pip install` + `python -m kingdee_mcp.server`）。

---

## [0.1.0] - 2026-07-19

### Added（新增）

- **13 大业务域、共 86 个工具**，覆盖生产制造、成本核算、固定资产、审计合规、采购、销售、库存、工作流审批、基础资料、元数据探查、系统查询等。
- **生产制造模块**：生产订单查询/保存/提交/审核、MRP 运算结果、生产计划、生产汇报、生产入库、生产领料下推（`kingdee_query_production_*`、`kingdee_save_production_order`、`kingdee_push_production_*` 等 12 个）。
- **成本核算模块**：材料成本、成本计算、成本趋势、实际 vs 标准成本对比、完工产品成本、成本调整单等（`kingdee_query_material_cost`、`kingdee_query_cost_calculation`、`kingdee_save_cost_adjustment` 等 12 个）。
- **固定资产模块**：资产卡片、资产折旧、资产盘点、资产调拨、资产新增（`kingdee_query_fixed_asset`、`kingdee_save_asset` 等 6 个）。
- **审计合规模块**：操作日志、变更日志、审核日志、复合「新建并审核」「下推并审核」工作流（`kingdee_query_operation_logs`、`kingdee_query_change_log`、`kingdee_create_and_audit`、`kingdee_push_and_audit` 等 7 个）。
- **元数据动态查询**：`kingdee_get_bill_template`（取已验证单据骨架）、`kingdee_validate_bill`（保存前校验，不真正落库）、`kingdee_refresh_metadata`（强制刷新），元数据落盘缓存到 `~/.workbuddy/kingdee_metadata_cache/`。
- **SQL Server 探查工具 4 个**：`kingdee_discover_tables`、`kingdee_discover_columns`、`kingdee_describe_table`、`kingdee_discover_metadata_candidates`（配置 `MCP_SQLSERVER_*` 环境变量后可用）。
- **MCP 使用日志系统**：记录工具调用，便于审计与排查。
- **权限架构设计方案**文档（`docs/permission-architecture.md`）。
- **TEST_GUIDE 与生产工作流 e2e** 测试，回归网覆盖核心链路。

### Changed（变更）

- **登录方式改为仅账号密码（ValidateUser）**，移除第三方应用授权（原 `LoginByAppSecret`）。配置只需 `KINGDEE_SERVER_URL`、`KINGDEE_ACCT_ID`、`KINGDEE_USERNAME`、`KINGDEE_PASSWORD` 四项，**不再需要 AppID / AppSecret**。
- `kingdee_view_bill` 返回结果精简，只保留常用字段，降低 token 消耗。
- `kingdee_query_bills` 等查询类工具的过滤与返回结构优化。
- 批量操作（提交/审核/反审核/删除）真正批量化，减少循环请求。
- 错误自描述：接口失败时返回更可读的中文错误，便于 AI 与用户定位。
- 强制使用 HTTP/1.1 解决金蝶 WebAPI 偶发 502 问题。
- 文档/示例/脚本/测试整体同步。

### Fixed（修复）

- **销售报价单（SAL_Quotation）保存报"含税单价不能小于等于0"的真正根因 = 字段顺序**：本二开账套金蝶 Save 对字段顺序敏感，`FQUOTATIONFIN`（财务信息，含结算币别/含税标志）必须排在 `FQUOTATIONENTRY`（分录）之前，否则分录单价被算成 0。`kingdee_save_bill` 新增防御性排序（所有非 ENTRY 键统一前置），`BILL_TEMPLATES` 补 `FQUOTATIONFIN` 并置于 ENTRY 之前。
- 修正 `kingdee_push_bill` API 格式、`_post_raw` 入参与生产下推（`push_production`）参数。
- 补全若干缺失函数，修复批量操作的一致性。

### Removed（移除）

- 第三方应用授权登录（`LoginByAppSecret`）及相关 `APP_ID` / `APP_SEC` 环境变量、配置项。

---

## 历史提交摘要（按时间倒序，供溯源）

| 提交 | 说明 |
|------|------|
| `f58c2a7` | fix: 销售报价单 Save 字段顺序校正 + 新增 API 中心快照 |
| `c3fbaf5` | feat: 登录改为仅账号密码(ValidateUser)，移除第三方应用授权 |
| `a5b17e5` | chore: 忽略运行时日志/工具缓存/记忆目录/临时文件 |
| `6145af1` | test: 新增 TEST_GUIDE 和生产工作流 e2e |
| `a61d845` | chore: 同步文档/示例/脚本/测试 |
| `5c742a0` | feat: 元数据动态查询 + view 结果精简 |
| `6b7b58d` | docs: 添加权限架构设计方案 |
| `529a55e` | feat: 添加 MCP 使用日志系统 |
| `5bbc744` | fix: 批量操作真批量化 + 补全缺失函数 + 修正 push_production 参数 |
| `04d4eba` | feat: 新增 MRP/生产计划/生产汇报查询工具 |
| `96f7f93` | feat: 新增审计合规模块 API |
| `354e339` | feat: 新增生产、成本、资产管理等模块 API |
| `e034152` | feat: 复合工作流工具 + 错误自描述 + e2e 回归网 |
| `6b754c3` | fix: 强制使用 HTTP/1.1 解决金蝶 WebAPI 502 问题 |
| `30b2a19` | feat: 新增 4 个 SQL Server 探查工具 |

完整历史见 [GitHub Commits](https://github.com/WaHaiLong/KingdeeMCP/commits/main)。
