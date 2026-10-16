# 金蝶 WebAPI 登录机制与元数据缓存

> 适用：范探源（WebAPI 集成）、寇豆码（工具开发）。本文描述 kingdee-mcp 连接金蝶云星空的核心机制，全部来自已实证环境，勿凭印象。

## 1. 登录方式（2026-07-16 起生效）

仅 **账号密码（ValidateUser）**，**无第三方应用授权**。不再有 `APP_ID` / `APP_SEC`。

环境变量（WorkBuddy 连接器 `kingdee` 的 `mcp.json` 中配置）：

| 变量 | 说明 |
|------|------|
| `KINGDEE_SERVER_URL` | ERP 地址，本环境 `http://<K3Cloud-Server>/k3cloud/` |
| `KINGDEE_ACCT_ID` | 账套 ID，本环境 `<ACCT_ID>` |
| `KINGDEE_USERNAME` | 账号，本环境 `<USERNAME>` |
| `KINGDEE_PASSWORD` | 密码 |

> ⚠️ **配置热重载坑**：若运行中的 MCP 进程是 WorkBuddy 更早启动时派生的旧进程（如曾用 `demo` 账号），改 `mcp.json` 不会热生效。需在 WorkBuddy 连接器管理中对 kingdee「重新信任 / 重启」强制重载。

## 2. WebAPI 标准动作集

| 动作 | 说明 | 常见于 ApiDoc 操作 |
|------|------|-------------------|
| `Save` | 保存单据 | 保存 / 批量保存 / 暂存 |
| `Submit` | 提交 | 提交 |
| `Audit` | 审核 | 审核 |
| `UnAudit` | 反审核 | 反审核 |
| `CancelAssign` / `Cancel` | 撤销 | 撤销 |
| `Push` | 下推 | 下推 |
| `Delete` | 删除 | 删除 |
| `ExecuteBillQuery` | 单据查询 | 单据查询 / 查看 |
| `CloseBill` / `UnCloseBill` | 整单关闭 / 反关闭 | 整单关闭、反关闭 |
| 领域专属 | 如费用退款 | 申请单退款 |

`_result_status` 返回的是 `fid` / `ids`（**不是** `id`）—— submit/audit 取 `id` 会得到 `None`。

## 3. 元数据缓存机制

- 元数据落盘缓存目录：`~/.workbuddy/kingdee_metadata_cache/`。
- 探字段工具：`kingdee_get_fields`（查字段 Key）、`kingdee_discover_metadata_candidates`（模糊候选）。
- 强制刷新：`kingdee_refresh_metadata`（当二开单据字段变更、或探到的字段与实测不符时调用）。
- 实战建议：先查缓存，缓存缺失或过期再 `refresh_metadata`，避免每次请求都打金蝶元数据接口拖慢速度。

## 4. 直连金蝶 WebAPI 的排查技巧（绕过 MCP 统计）

当 MCP 故障或需独立验证时，可用 Python `urllib + http.cookiejar` 直连金蝶 WebAPI：
1. `LoginByAppSecret` 拿 Session（或 `ValidateUser`）。
2. 后续请求**必须带 cookie**（Session 绑定在 cookie 上）。
3. 返回结构区分见「项目事实」：权限拒绝是 `[[{'Result':{报错}}]]`，正常数据是 `[[值,...]]`。
