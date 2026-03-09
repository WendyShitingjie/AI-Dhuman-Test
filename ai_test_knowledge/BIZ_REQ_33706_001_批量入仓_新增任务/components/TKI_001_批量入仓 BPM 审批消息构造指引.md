---
component_id: TKD_001
component_name: "批量入仓BPM审批消息构造"
component_type: "RabbitMQ"
cluster_name: "amqp-cn-4591j61c6009"
queue: "dataops.queue.receiveBatchOperationFlow"
business_module: "BIZ_JDBC批量入仓"
version: v1.0
created_date: 2026-02-25
---

---

# 批量入仓 BPM 审批消息构造指引 (Payload Guide)

## 1. 消息发送上下文
在使用 `mq-sender` 技能发布消息时，请确保参数指向以下环境配置：
*   **cluster_name**: `amqp-cn-4591j61c6009`
*   **queue**: `dataops.queue.receiveBatchOperationFlow`
*   **业务作用**: 模拟 BPM 流程中心回调，驱动“待审批”的任务进入执行（通过）或失败（拒绝）流程。

---

## 2. 核心字段造数映射 (Source Mapping)

在构造消息前，请执行以下 SQL 获取当前环境的实时数据，确保字段间的**物理关联性**。

| 字段名               | 造数逻辑 / 获取来源 | 获取方式 (SQL)                                                                                 |
|:------------------|:------------|:-------------------------------------------------------------------------------------------|
| **taskId**        | **业务主键**    | `/v2/validate` 接口返回的 `data.taskId`，或查表获取最新的 ID。                                            |
| **orderNo**       | **关联工单号**   | `SELECT order_no FROM dataops_bpm_record WHERE process_instance_node_id = {taskId};`       |
| **processInstId** | **流程实例 ID** | `SELECT bpm_process_id FROM dataops_bpm_record WHERE process_instance_node_id = {taskId};` |
| **status**        | **审批判定**    | **通过**: `STATUS_APPROVED` \| **拒绝**: `STATUS_REJECTED`                                     |
| **scene**         | **处理器路由**   | **枚举值**: 见下文 [3. 场景枚举表] ，注意填写的是业务场景中文名称，不是code枚举值或task_type值                               |
| **fileName**         | **处理器路由**   | **枚举值**: 见下文 [3. 场景枚举表] ，注意填写的是业务场景中文名称，不是code枚举值或task_type值                               |

---

## 3. 场景枚举表 (Scene Mapping)
`dataMap` 中的 `scene` 字段决定了系统由哪一个 Handler 处理，必须严格匹配：
注意scene在消息体内是中文名称，比如“批量新增任务”，而不是jdbcInputBatchAddTask这个code

| `scene` 枚举值 | 业务场景                        | 后台任务类型 (task_type) |
|:------------|:----------------------------|:-------------------|
| **批量新增任务**  | `jdbcInputBatchAddTask`     | UPLOAD             |
| **批量新增字段**  | `jdbcInputBatchAddField`    | FIELDS_UPDATE      |
| **批量修改任务**  | `jdbcInputBatchModifyTask`  | TASK_MODIFY        |
| **批量下线任务**  | `jdbcInputBatchOfflineTask` | TASK_OFFLINE       |

---

## 4. 报文构造模板 (Payload Structure)

### 示例 A：审批通过 (Positive Workflow)
#### 以上传文件是一行记录为例，展示审批通过的完整payload_data消息体
```json
{
                "startUid": "71e8b23d-45e2-497a-b247-f5b807fb4f65",
                "orderNo": "RCPLXZRW-202600000024",
                "dataMap": "{\"fileName\":\"批量新增任务_测试模板1条.xlsx\",\"sceneType\":\"jdbcInputBatchAddTask\",\"createdBy\":\"施婷杰\",\"batchTaskId\":379,\"scOwnerUid\":\"6260e238-93c5-4324-8d0f-e3ba17659a14\",\"taskId\":379,\"recordCnt\":1,\"scene\":\"批量新增任务\"}",
                "processInstId": "c153fac3-841f-4920-91ed-1b8409e3eff9",
                "operatorUid": "6260e238-93c5-4324-8d0f-e3ba17659a14",
                "operator": "陈沈伟",
                "startName": "施婷杰",
                "status": "STATUS_APPROVED"
                 }
```

### 示例 B：审批拒绝 (Negative Workflow)
```json
        {
            "startUid": "71e8b23d-45e2-497a-b247-f5b807fb4f65",
            "orderNo": "RCPLXZRW-202600000028",
            "processInstId": "67b85e3e-4b18-4a3d-8cda-629a580fa4ee",
            "dataMap": "{\"fileName\":\"批量新增任务_测试模板1条.xlsx\",\"sceneType\":\"jdbcInputBatchAddTask\",\"createdBy\":\"施婷杰\",\"batchTaskId\":384,\"scOwnerUid\":\"6260e238-93c5-4324-8d0f-e3ba17659a14\",\"taskId\":384,\"recordCnt\":1,\"scene\":\"批量新增任务\"}",
            "operatorUid": "6260e238-93c5-4324-8d0f-e3ba17659a14",
            "operator": "陈沈伟",
            "startName": "施婷杰",
            "status": "STATUS_REJECTED"

        }
```

---

## 5. ✅ 验证造数结果 (Checklist)

发送消息后，请通过数据库观察表的状态流转，确保造数成功。

### 5.1 批量操作作业表的状态机流转检查
*   [ ] **初始状态确认**：发送消息前，任务的 `dataops_batch_operation_task.task_status` 必须为 **`PENDING_APPROVAL`** (待审批)。
*   [ ] **审批通过验证**：发送后，`dataops_batch_operation_task.task_status` 是否成功变更为 **`EXECUTING`** （审批通过，发布中) 或等待发布成功后更新成**`SUCCESS`** 发布成功) 。
*   [ ] **审批拒绝验证**：发送后，`dataops_batch_operation_task.task_status` 是否变更为 **`APPROVING_FAIL`** （审批拒绝）

### 5.1 bpm记录表的状态机流转检查
*   [ ] **初始状态确认**：发送消息前，任务的 `dataops_bpm_record.status` 必须为 **`2`** (审核中)。
*   [ ] **审批通过验证**：发送后，`dataops_bpm_record.status` 是否成功变更为 **`4`** （审批通过) 。
*   [ ] **审批拒绝验证**：发送后，`dataops_bpm_record.status` 是否变更为 **`3`** （审批拒绝）

---

## 6. 避坑指南

1.  **环境隔离**：确保 `orderNo` 属于当前测试环境。使用生产环境的单号在 SIT 发送将导致消息因找不到记录而被丢弃。
2.  **转义处理**：手动 Mock 时 `dataMap` 引号需转义（`\"`）。**使用 `mq-sender` 脚本会自动处理此逻辑，推荐使用脚本发送。**
3.  **幂等性**：同一个 `taskId` 若状态已非 `PENDING_APPROVAL`，后续重复发送的消息将被静默丢弃，不会触发二次执行。
4.  **异步延时**：系统接收消息后会有 **100ms** 的保护性延时，请在点击发送 1 秒后再刷新数据库查看结果。

---
**维护人**: DataOps QA 团队  
**文档版本**: v1.2  
**更新日期**: 2026-02-23