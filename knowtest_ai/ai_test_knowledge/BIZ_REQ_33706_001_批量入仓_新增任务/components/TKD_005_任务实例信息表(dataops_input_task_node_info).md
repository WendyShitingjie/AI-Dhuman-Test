---
component_id: TKD_005
component_name: "任务实例信息表"
component_type: "MySQL"
database: "dataops"  # ⚠️ 必填
table_name: "dataops.dataops_input_task_node_info"
business_module: "BIZ_入仓任务(新)"
version: v1.0
created_date: 2026-02-21
---

# 任务实例信息表

## 基础信息
| 属性 | 值 |
|------|-----|
| 数据库 | dataops |
| 表名 | dataops_input_task_node_info |
| 完整表名 | dataops.dataops_input_task_node_info |
| 数据源 | MySQL |

## 表结构

```sql
CREATE TABLE `dataops_input_task_node_info` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `task_id` bigint(20) NOT NULL COMMENT '任务ID，关联dataops_input_task.id',
  `node_id` varchar(100) DEFAULT NULL COMMENT 'DP平台节点ID',
  `pipeline_id` bigint(20) DEFAULT NULL COMMENT 'DP平台管道ID',
  `file_id` bigint(20) DEFAULT NULL COMMENT 'DP平台文件ID',
  `schedule_type` int(11) DEFAULT NULL COMMENT '调度类型：1-周期任务，3-手动任务',
  `node_name` varchar(100) DEFAULT NULL COMMENT '节点任务名称：试运行、发布',
  `node_type` int(11) DEFAULT NULL COMMENT '节点任务类型：0-DATA_PROCESS计算任务，1-PIPELINE_COMPUTE管道任务',
  `status` int(11) DEFAULT NULL COMMENT '节点状态：0-成功，1-运行中，2-失败',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `created_by` varchar(100) DEFAULT NULL COMMENT '创建人姓名',
  `updated_by` varchar(100) DEFAULT NULL COMMENT '更新人姓名',
  PRIMARY KEY (`id`),
  KEY `idx_task_id` (`task_id`),
  KEY `idx_node_id` (`node_id`),
  KEY `idx_pipeline_id` (`pipeline_id`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='入仓任务实例信息表';
```

## 字段说明

| 字段名 | 类型 | 必填 | 说明 | 测试值示例 |
|-------|------|-----|------|-----------|
| id | bigint(20) | 是 | 实例记录唯一标识 | 1001 |
| task_id | bigint(20) | 是 | 关联任务主表ID | 3137 |
| node_id | varchar(100) | 否 | DP平台节点唯一ID | "n_4924230067033669632" |
| pipeline_id | bigint(20) | 否 | DP平台管道ID | 67890 |
| file_id | bigint(20) | 否 | DP平台文件ID | 11223 |
| schedule_type | int(11) | 否 | 1-周期任务，3-手动任务 | 1 |
| node_name | varchar(100) | 否 | 节点名称（试运行/发布） | "试运行" |
| node_type | int(11) | 否 | 0-计算任务，1-管道任务 | 0 |
| status | int(11) | 否 | 运行状态：0-成功，1-运行中，2-失败 | 0 |
| created_at | timestamp | 是 | 实例创建时间 | "2026-02-21 10:00:00" |
| updated_at | timestamp | 是 | 实例更新时间 | "2026-02-21 10:05:00" |

## 关键字段

- **node_id**: 外部平台（DataPhin/DP）的节点句柄，是远程调用的核心参数。
- **status**: 实时反映计算节点在外部平台的执行情况。
- **node_type**: 区分任务是属于逻辑处理（DATA_PROCESS）还是单纯的数据搬运（PIPELINE_COMPUTE）。
- **schedule_type**: 决定了该实例是定时触发还是人为干预触发。

## 业务规则

- **多节点关联**: 一个 `task_id` 允许对应多个实例（如“试运行节点”和“正式发布节点”共存）。
- **状态同步优先级**: 本表 `status` 需通过定时任务轮询 DP 平台 API 进行强向同步，以外部平台状态为准。
- **不可手动修改**: `node_id`、`pipeline_id` 等外部标识由系统自动维护，禁止人工干预以防关联失效。

## 关联组件

- `[TKD_002]` 入仓任务主表: 通过 `task_id` 关联，标识实例所属的业务任务。
- `[TKD_003]` 任务版本配置表: 实例的执行参数（如调度时间）来源于该表的特定版本配置。
- `[TKD_004]` 任务操作记录表: 操作记录中的 `flow_id` 通常与本表的执行实例存在逻辑对应关系。

## 状态流转

```
1 (运行中)
  ↓
0 (成功) / 2 (失败)
```

---
**质量检查**: 
- [x] 元数据包含 `database` 字段
- [x] 包含完整的 `CREATE TABLE` 语句
- [x] 字段说明表包含测试值示例
- [x] 移除了原内容中的 SQL 查询示例（测试用例）
- [x] 核心业务流程已简化为业务规则说明
```