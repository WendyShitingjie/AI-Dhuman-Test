---
component_id: TKD_004
component_name: "任务操作记录表"
component_type: "MySQL"
database: "dataops"  # ⚠️ 必填
table_name: "dataops.dataops_input_task_operation"
business_module: "BIZ_入仓任务(新)"
version: v1.0
created_date: 2026-02-21
---

# 任务操作记录表

## 基础信息
| 属性 | 值 |
|------|-----|
| 数据库 | dataops |
| 表名 | dataops_input_task_operation |
| 完整表名 | dataops.dataops_input_task_operation |
| 数据源 | MySQL |

## 表结构

```sql
CREATE TABLE `dataops_input_task_operation` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `task_id` bigint(20) NOT NULL COMMENT '任务ID，关联dataops_input_task.id',
  `operation_name` varchar(50) DEFAULT NULL COMMENT '操作类型：init-初始化，publish-发布，test_run-试运行，manual_run-手工执行，rename-目标表重命名，offline_task-下线任务，delete_version-版本删除，rollback_table-数据回滚，terminal-终止执行',
  `status` int(11) DEFAULT NULL COMMENT '操作状态：0-运行成功，1-运行中，2-运行失败',
  `duration` varchar(50) DEFAULT NULL COMMENT '持续时长',
  `fail_msg` text COMMENT '失败信息',
  `version` int(11) DEFAULT NULL COMMENT '版本号',
  `flow_id` varchar(100) DEFAULT NULL COMMENT 'DP节点运行的flowId',
  `created_by` varchar(100) DEFAULT NULL COMMENT '创建人姓名',
  `updated_by` varchar(100) DEFAULT NULL COMMENT '更新人姓名',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_task_id` (`task_id`),
  KEY `idx_operation_name` (`operation_name`),
  KEY `idx_status` (`status`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='入仓任务操作记录表';
```

## 字段说明

| 字段名 | 类型 | 必填 | 说明 | 测试值示例 |
|-------|------|-----|------|-----------|
| id | bigint(20) | 是 | 操作记录唯一标识 | 1001 |
| task_id | bigint(20) | 是 | 关联任务主表ID | 3137 |
| operation_name | varchar(50) | 否 | 操作类型枚举（见下文关键字段） | "publish" |
| status | int(11) | 否 | 操作执行状态：0-成功，1-运行中，2-失败 | 0 |
| duration | varchar(50) | 否 | 操作持续时长（HH:mm:ss） | "00:05:23" |
| fail_msg | text | 否 | 失败时的堆栈或错误信息 | "节点执行超时" |
| version | int(11) | 否 | 关联的任务版本号 | 1 |
| flow_id | varchar(100) | 否 | DataPhin平台运行流程ID | "flow_12345678" |
| created_by | varchar(100) | 否 | 操作发起人姓名 | "张三" |
| created_at | timestamp | 是 | 操作开始时间 | "2026-02-21 10:00:00" |
| updated_at | timestamp | 是 | 操作结束/更新时间 | "2026-02-21 10:05:23" |

## 关键字段

- **operation_name**: 定义了任务的动作类型。
  - `init`: 任务初始化
  - `publish`: 发布至生产（含Schema创建、调度配置、同步启动）
  - `test_run`: 试运行（验证路径、格式及映射配置）
  - `offline_task`: 下线任务
  - `delete_version`: 删除特定版本配置
- **status**: 标识操作的生命周期。
  - `1 (RUNNING)`: 正在执行异步任务（如DP平台作业中）
  - `0 (SUCCESS)`: 执行完毕且结果符合预期
  - `2 (FAIL)`: 执行异常，需结合 `fail_msg` 排查
- **flow_id**: 与DataPhin平台打通的关键凭证，用于实时查询外部平台的执行进度。

## 业务规则

- **操作不可篡改**: 操作记录一旦产生，原则上仅允许更新状态和时长，不允许删除，用于合规审计。
- **状态同步机制**: 针对 `publish` 和 `test_run` 操作，系统需根据 `flow_id` 轮询外部状态，并最终反向更新本表的 `status`。
- **时长计算**: `duration` 字段通常在状态流转至 0 或 2 时，通过 `updated_at` 与 `created_at` 的差值计算得出。
- **失败排查**: 任何 `status=2` 的记录，`fail_msg` 必须捕获并存储详细的异常原因。

## 关联组件

- `[TKD_002]` 入仓任务主表: 通过 `task_id` 关联，属于该任务的操作流水。
- `[TKD_003]` 任务版本配置表: 通过 `task_id` 和 `version` 关联，确定该操作是基于哪一个配置版本触发的。

## 状态流转

```
1 (运行中)
  ↓
0 (运行成功) / 2 (运行失败)
```

---
**质量检查**: 
- [x] 元数据包含 `database` 字段
- [x] 包含完整的 `CREATE TABLE` 语句
- [x] 字段说明表包含测试值示例
- [x] 移除了原内容中的 SQL 查询示例（测试用例）
- [x] 无完整JSON示例
```