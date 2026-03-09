---
component_id: TKP_004
component_name: "MQ审批信号模拟"
component_type: "Primitive"
associated_skill: "mq-sender"
business_module: "BIZ_JDBC批量入仓"
version: v1.8
created_date: 2026-03-01
---

# MQ 审批信号模拟原语

## 原语说明
模拟审批中心（BPM）发送回调消息。该原语所需的 `taskId` **必须取自 `TKI_003` (批量上传校验接口) 响应结果中的 `data.taskId`**。AI 需识别业务意图并按照关联协议组装 Payload。

## 输入参数

| 参数名         | 类型      | 必填 | 说明                                                                     |
|-------------|---------|----|------------------------------------------------------------------------|
| instruction | String  | 是  | 自然语言描述（如：“taskid={TaskId}发送审批通过的mq消息”）                                 |
| taskId      | Integer | 否  | 任务 ID。**来源：TKI_003 接口返回的 `data.taskId`**。若不填，将从 `instruction` 中自动识别提取。 |

## 执行逻辑
1. **数据源关联**：
   - 识别由上游步骤 `TKI_003` 产生的动态变量 `{TaskId}`（取自其 `data.taskId` 字段）。
   - **获取优先级**：优先使用显式传入的 `taskId` 参数；若缺失，则从 `instruction` 文本中正则提取。
2. **意图解析**：根据 `instruction` 识别 `status`（通过/拒绝）及 `sceneType`（新增/修改等）。
3. **协议对齐与数据补全**：
   - 以识别出的 `taskId` 为主键，按照 **[消息构造协议]** 中的 SQL 逻辑反查 DB 补全 `orderNo`、`processInstId` 等核心字段。
4. **消息下发**：严格执行协议中的 JSON 嵌套规则构造 Payload，并调用 `mq-sender` 技能发送至目标队列。

## 使用示例

### 示例 1：全链路变量关联（标准用法）
```yaml
- TKP_004:
    taskId: "{TaskId}"  # 引用自上游 TKI_003 返回的 data.taskId
    instruction: "JDBC批量入仓-新增任务，发送审批通过消息"
```

### 示例 2：仅使用自然语言提取 ID
```yaml
- TKP_004:
    instruction: "批量入仓-新增任务，taskid={TaskId}发送审批通过的mq消息"
    # Skill 将自动从字符串中解析动态变量 {TaskId} 的实际值
```

## 关联参考
- **核心构造协议**: `skills/mq-sender/references/JDBC批量入仓_新增任务审批_消息构造协议.md`
- **上游依赖接口**: `TKI_003` (批量上传校验接口)，需获取其返回的 `data.taskId`
- **目标队列**: `dataops.queue.receiveBatchOperationFlow`
```
