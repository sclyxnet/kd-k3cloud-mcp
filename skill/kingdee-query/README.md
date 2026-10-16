# kingdee-query —— 金蝶云星空 查询与操作助手（WorkBuddy Skill）

> 一个 WorkBuddy 技能骨架，用于把"查金蝶 / 操作金蝶 ERP"的自然语言需求，路由到已连接的 **kingdee-mcp** MCP 服务器。

## 它做什么

- 识别用户对金蝶 ERP 的查询 / 操作意图（销售/采购订单、库存、物料、客户/供应商、单据审核下推等）。
- 引导 WorkBuddy 调用 `kingdee-mcp` 暴露的 86 个工具，用中文结构化返回结果。
- **不**直接连接金蝶——连接由 kingdee-mcp 负责，本技能只做"语义路由 + 使用约定"。

## 前置依赖

必须先让 **kingdee-mcp** 在 WorkBuddy 中作为 MCP 服务器连接。配置方式见仓库根目录：

- `README.md` —— 安装、配置、`KINGDEE_*` 环境变量说明
- `PUBLISH.md` —— 上架到 ClawHub / 官方市场的清单
- `examples/workbuddy-mcp-config.example.json` —— WorkBuddy 接入用的 mcp.json 模板

最小配置（用户级 `~/.workbuddy/mcp.json`）：

```json
{
  "mcpServers": {
    "kingdee": {
      "command": "uvx",
      "args": ["kingdee-mcp"],
      "env": {
        "KINGDEE_SERVER_URL": "http://你的服务器/k3cloud/",
        "KINGDEE_ACCT_ID": "你的账套ID",
        "KINGDEE_USERNAME": "金蝶账号",
        "KINGDEE_PASSWORD": "金蝶账号密码"
      }
    }
  }
}
```

## 触发词示例

- "查一下本月已审核的销售订单"
- "物料 MAT001 的即时库存是多少"
- "帮我新建一张采购订单…"
- "审核这几张采购入库单：12345, 12346"

## 目录结构

```
skill/kingdee-query/
├── SKILL.md   # 技能主体（frontmatter 元数据 + 指令/工具表/约定）
└── README.md  # 本文件
```

## 发布

参见仓库根目录 `PUBLISH.md`：可发布到 ClawHub 技能市场、WorkBuddy 官方推荐市场，或通过 GitHub 仓库地址"URL 导入"。

## License

MIT © WaHaiLong
