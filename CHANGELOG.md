# 更新日志 (Changelog)

本项目所有重要变更都会记录在此文件。

格式参考 [Keep a Changelog](https://keepachangelog.com/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

> 当前 PyPI 版本：`0.3.3`（见 `pyproject.toml`）。本文件按功能里程碑汇总，未单独打 git tag。

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
