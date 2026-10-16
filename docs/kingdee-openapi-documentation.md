# 金蝶云星空 OpenAPI 接口文档

> 基于 https://openapi.open.kingdee.com/ApiDoc 网站探索整理

## 一、业务领域分类

| 序号 | 业务领域 | 说明 |
|------|----------|------|
| 1 | 员工服务 | 人人报销、差旅费等 |
| 2 | 财务会计 | 总账、应收/应付、出纳等 |
| 3 | 税务管理 | 税务相关 |
| 4 | 成本管理 | 成本核算 |
| 5 | 资产管理 | 固定资产管理 |
| 6 | 管理会计 | 内部管理报表 |
| 7 | 供应链 | 采购、销售、库存等 |
| 8 | 电商与分销 | 电商集成 |
| 9 | 零售管理 | 零售门店 |
| 10 | 生产制造 | 生产计划、工序等 |
| 11 | 质量管理 | 质量检验 |
| 12 | 星空云服务 | 云服务集成 |
| 13 | 基础管理 | 基础资料 |
| 14 | BOS | 业务对象扩展 |
| 15 | 移动应用 | 移动端功能 |
| 16 | PLM | 产品生命周期管理 |

## 二、供应链模块详细接口

### 2.1 供应链基础管理
- 基础资料维护

### 2.2 采购管理
| 单据类型 | FormId | 说明 |
|----------|--------|------|
| 联系人 | - | 供应商联系人 |
| 采购条款 | - | 采购条款设置 |
| 采购折扣表 | - | 采购折扣管理 |
| 采购评估指标 | - | 供应商评估 |
| 采购评估方案 | - | 评估方案 |
| 货源清单 | - | 供应商货源 |
| 采购合同 | PUR_Contract | 采购合同 |
| 采购合同变更单 | - | 合同变更 |
| 采购合同执行明细表 | - | 执行查询 |
| 采购追料交货报表 | - | 报表 |
| 期初采购退料单 | - | 期初数据 |
| 退料申请单 | - | 退料申请 |
| 采购退料单 | - | 退料单 |
| 采购调价表 | - | 价格调整 |
| 采购计划方案 | - | 计划方案 |
| 采购订单变更单 | - | 订单变更 |
| 采购订单新变更单 | - | 新版变更 |
| 预计供应量查询 | - | 供应查询 |
| 采购价目表 | - | 价格表 |
| 采购价目表分发方案 | - | 分发方案 |
| 采购订单 | PUR_PurchaseOrder | 采购订单 |
| 采购订单执行明细表 | - | 执行报表 |
| 采购价格分析表 | - | 价格分析 |
| 采购业务汇总表 | - | 业务汇总 |
| 采购申请执行明细表 | - | 申请执行 |
| 收料通知单 | - | 收料通知 |
| 收料待检库存查询 | - | 待检查询 |
| 采购申请单 | PUR_Requisition | 采购申请 |
| 定时智能采购 | - | 智能采购 |
| 定时创建消耗汇总 | - | 消耗汇总 |
| 供应商到货及时率报表 | - | 及时率 |
| VMI物料消耗明细表 | - | VMI报表 |
| VMI物料消耗结算明细表 | - | 结算报表 |
| 期初采购入库单 | - | 期初入库 |
| 采购入库单 | STK_InStock | 采购入库 |

### 2.3 销售管理
| 单据类型 | FormId | 说明 |
|----------|--------|------|
| 销售合同 | - | 销售合同 |
| 销售订单 | SAL_SaleOrder | 销售订单 |
| 销售报价单 | - | 销售报价 |
| 销售出库单 | - | 销售出库 |
| 退货单 | - | 销售退货 |
| 信用管理 | - | 客户信用 |

### 2.4 库存管理
| 单据类型 | FormId | 说明 |
|----------|--------|------|
| 其它入库单 | - | 其他入库 |
| 其它出库单 | - | 其他出库 |
| 调拨单 | - | 库存调拨 |
| 盘点单 | - | 库存盘点 |
| 组装拆分单 | - | 组装拆分 |
| 即时库存查询 | - | 库存查询 |

### 2.5 供应商管理
| 单据类型 | FormId | 说明 |
|----------|--------|------|
| 供应商 | - | 供应商档案 |
| 供应商协同平台 | - | 协同门户 |

## 三、通用操作接口

每个单据类型都支持以下操作：

| 操作 | 说明 | HTTP方法 |
|------|------|----------|
| 删除 (Delete) | 删除单据 | POST |
| 暂存 (Save) | 暂存单据 | POST |
| 保存 (Save) | 保存单据 | POST |
| 查看 (View) | 查看单据详情 | POST |
| 提交 (Submit) | 提交单据 | POST |
| 审核 (Audit) | 审核单据 | POST |
| 反审核 (UnAudit) | 取消审核 | POST |
| 禁用 (Forbid) | 基础资料禁用 | POST |
| 反禁用 (Enable) | 基础资料反禁用 | POST |
| 撤销 (CancelAssign) | 撤销操作 | POST |
| 下推 (Push) | 下推到下游单据 | POST |
| 作废 (Cancel) | 作废单据 | POST |
| 反作废 (UnInvalid) | 取消作废 | POST |
| 业务关闭 (Close) | 关闭业务 | POST |
| 反业务关闭 (UnClose) | 取消关闭 | POST |
| 业务终止 (Terminate) | 终止业务 | POST |
| 反业务终止 (UnTerminate) | 取消终止 | POST |
| 整单关闭 (YLBillClose/BillClose) | 整单关闭 | POST |
| 整单反关闭 (YLUnBillClose/Unclose) | 取消整单关闭 | POST |
| 批量保存 (BatchSave) | 批量保存 | POST |
| 单据查询 (ExecuteBillQuery) | 查询单据列表 | POST |

> **2026-08-07 真机修正，依据：元数据 OperationNumber + OperationNumberConst.cs 反编译 + ExecuteOperation 实测**：撤销=CancelAssign（非 Cancel）、作废=Cancel（非 Invalid，全库无 Invalid 常量）、整单关闭=YLBillClose/BillClose（非 BatchClose）、反关闭=YLUnBillClose/Unclose（非 BatchUnClose）、禁用=Forbid、反禁用=Enable（非 UnForbid；Disable 已废弃）。端点正确拼写为 `ExecuteOperation`（`Kingdee.BOS.WebApi.ServicesStub.DynamicFormService.ExecuteOperation.common.kdsvc`），`ExcuteOperation` 为官方论坛拼写错误。

## 四、接口调用方式

### 4.1 认证方式
使用 AppSecret 签名认证：
```
POST /k3cloud/{{acctId}}/Api
Headers:
  - Content-Type: application/json
  - X-Auth-Token: {{session_id}}
```

### 4.2 通用请求参数

| 参数名 | 类型 | 必须 | 说明 |
|--------|------|------|------|
| formid | String | 是 | 业务对象表单ID，如 "PUR_Contract" |
| data | Object | 是 | JSON格式的业务数据包 |
| CreateOrgId | Integer | 否 | 创建者组织内码 |
| Numbers | Array | 否 | 单据编码集合，格式：[No1,No2,...] |
| Ids | String | 否 | 单据内码集合，格式："Id1,Id2,..." |
| NetworkCtrl | String | 否 | 是否启用网控，默认 false |

### 4.3 保存操作额外参数

| 参数名 | 类型 | 必须 | 说明 |
|--------|------|------|------|
| NeedUpDateFields | Array | 否 | 需要更新的字段 |
| NeedReturnFields | Array | 否 | 需返回的字段集合 |
| IsDeleteEntry | bool | 否 | 是否删除已存在分录，默认 true |
| SubSystemId | String | 否 | 子系统内码 |
| IsVerifyBaseDataField | bool | 否 | 是否验证基础资料有效性，默认 false |
| IsEntryBatchFill | bool | 否 | 是否批量填充分录，默认 true |
| ValidateFlag | bool | 否 | 是否验证数据合法性，默认 true |
| NumberSearch | bool | 否 | 是否用编码搜索基础资料，默认 true |
| IsAutoAdjustField | bool | 否 | 是否自动调整JSON字段顺序，默认 false |
| InterationFlags | String | 否 | 交互标志集合 |
| IgnoreInterationFlag | String | 否 | 是否允许忽略交互，默认 true |
| IsControlPrecision | bool | 否 | 是否控制精度，默认 false |
| ValidateRepeatJson | bool | 否 | 校验Json是否重复传入，默认 false |
| Model | Object | 是 | 表单数据包，JSON类型 |

### 4.4 响应参数结构

```json
{
  "Result": {
    "Id": "内码",
    "Number": "编码",
    "NeedReturnData": [],
    "ResponseStatus": {
      "ErrorCode": "",
      "Errors": [],
      "IsSuccess": false,
      "MsgCode": "",
      "SuccessEntitys": [],
      "SuccessMessages": []
    }
  }
}
```

### 4.5 请求示例（保存采购合同）

```json
{
  "formid": "PUR_Contract",
  "data": {
    "NeedUpDateFields": [],
    "NeedReturnFields": [],
    "IsDeleteEntry": "true",
    "SubSystemId": "",
    "IsVerifyBaseDataField": "false",
    "IsEntryBatchFill": "true",
    "ValidateFlag": "true",
    "NumberSearch": "true",
    "IsAutoAdjustField": "false",
    "InterationFlags": "",
    "IgnoreInterationFlag": "",
    "IsControlPrecision": "false",
    "ValidateRepeatJson": "false",
    "Model": {
      "FID": 0,
      "FBillNo": "",
      "FBillTypeID": {"FNUMBER": ""},
      "FSupplierId": {"FNumber": ""},
      "FPurchaseOrgId": {"FNumber": ""},
      "FDate": "1900-01-01",
      "FContractEntry": [
        {
          "FMaterialId": {"FNumber": ""},
          "FQty": 0,
          "FPrice": 0
        }
      ]
    }
  }
}
```

## 五、Python调用示例

```python
import httpx
import json
import time
import hashlib
import base64
from typing import Optional

class KingdeeClient:
    def __init__(self, server_url: str, acct_id: str, app_id: str, app_secret: str, username: str = None, lcid: int = 2052):
        self.server_url = server_url.rstrip('/')
        self.acct_id = acct_id
        self.app_id = app_id
        self.app_secret = app_secret
        self.username = username
        self.lcid = lcid
        self.session_id: Optional[str] = None

    def _generate_signature(self) -> str:
        """生成签名"""
        timestamp = str(int(time.time()))
        signature_str = f"{self.app_id}{timestamp}{self.app_secret}"
        signature = hashlib.sha256(signature_str.encode()).digest()
        return base64.b64encode(signature).decode()

    def login(self) -> dict:
        """登录认证"""
        url = f"{self.server_url}/K3Cloud/LoginByAppSecret"
        data = {
            "acctId": self.acct_id,
            "appId": self.app_id,
            "appSecret": self.app_secret,
            "lcid": self.lcid
        }
        with httpx.Client(http1=True) as client:
            resp = client.post(url, json=data, timeout=30)
            resp.raise_for_status()
            result = resp.json()
            if result.get("Result", {}).get("LoginResultType") == 1:
                self.session_id = resp.headers.get("kdservice-sessionid")
            return result

    def execute(self, form_id: str, action: str, data: dict) -> dict:
        """执行API操作"""
        if not self.session_id:
            self.login()

        url = f"{self.server_url}/K3Cloud/{self.acct_id}/Api"
        payload = [[form_id, action, json.dumps(data)]]

        headers = {
            "Content-Type": "application/json",
            "kdservice-sessionid": self.session_id
        }

        with httpx.Client(http1=True) as client:
            resp = client.post(url, json=payload, headers=headers, timeout=60)
            resp.raise_for_status()
            return resp.json()[0]

    def view(self, form_id: str, data: dict) -> dict:
        """查看单据"""
        return self.execute(form_id, "View", data)

    def save(self, form_id: str, data: dict) -> dict:
        """保存单据"""
        return self.execute(form_id, "Save", data)

    def submit(self, form_id: str, data: dict) -> dict:
        """提交单据"""
        return self.execute(form_id, "Submit", data)

    def audit(self, form_id: str, data: dict) -> dict:
        """审核单据"""
        return self.execute(form_id, "Audit", data)

# 使用示例
client = KingdeeClient(
    server_url="http://your-server/k3cloud",
    acct_id="your_acct_id",
    app_id="your_app_id",
    app_secret="your_app_secret"
)

# 查看采购合同
result = client.view("PUR_Contract", {"Number": "CONTRACT001"})

# 保存采购订单
save_data = {
    "Model": {
        "FBillNo": "",
        "FSupplierId": {"FNumber": "SUP001"},
        "FPurchaseOrgId": {"FNumber": "100"},
        "FDate": "2026-04-30",
        "FContractEntry": [
            {"FMaterialId": {"FNumber": "M001"}, "FQty": 100, "FPrice": 10}
        ]
    }
}
result = client.save("PUR_Contract", save_data)

# 提交审核
if result.get("Result", {}).get("Id"):
    submit_data = {"Ids": result["Result"]["Id"]}
    client.submit("PUR_Contract", submit_data)
```

## 六、常用FormId对照表

| 模块 | FormId | 说明 |
|------|--------|------|
| 采购 | PUR_Contract | 采购合同 |
| 采购 | PUR_PurchaseOrder | 采购订单 |
| 采购 | PUR_Requisition | 采购申请单 |
| 采购 | STK_InStock | 采购入库单 |
| 销售 | SAL_SaleOrder | 销售订单 |
| 库存 | STK_Inventory | 即时库存 |
| 财务 | AR_receivable | 应收单 |
| 财务 | AP_Payable | 应付单 |

---

*文档生成时间：2026-04-30*
*来源：https://openapi.open.kingdee.com/ApiDoc*