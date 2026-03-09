---
component_id: TKD_009
component_name: "任务调度配置表"
component_type: "MySQL"
database: "dataops"  # ⚠️ 必填
table_name: "dataops.dataops_task_schedule_config_info"
business_module: "BIZ_JDBC入仓"
version: v1.0
created_date: 2026-02-24
---

# 任务调度配置表

## 基础信息
| 属性 | 值 |
|------|-----|
| 数据库 | dataops |
| 表名 | dataops_task_schedule_config_info |
| 完整表名 | dataops.dataops_task_schedule_config_info |
| 数据源 | MySQL |

## 表结构

```sql
CREATE TABLE `dataops_task_schedule_config_info` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '调度配置ID',
  `task_code_dir` varchar(255) DEFAULT NULL COMMENT '任务代码路径',
  `schedule_type` varchar(50) DEFAULT 'normal' COMMENT '调度类型：normal(正常调度)/empty(空跑调度)',
  `stop_scheduling` tinyint(1) DEFAULT '0' COMMENT '调度是否停止：0(运行)/1(停止)',
  `schedule_desc` varchar(500) DEFAULT NULL COMMENT '调度描述',
  `start_date` varchar(50) DEFAULT NULL COMMENT '调度开始日期',
  `end_date` varchar(50) DEFAULT NULL COMMENT '调度结束日期',
  `scheduling_cycle` varchar(50) DEFAULT 'day' COMMENT '调度周期：day(日)/week(周)/month(月)/hour(小时)/min(分钟)',
  `scheduling_time` varchar(100) DEFAULT NULL COMMENT '调度时间或crontab表达式',
  `upstream` varchar(500) DEFAULT NULL COMMENT '上游依赖节点',
  `session_output` varchar(500) DEFAULT NULL COMMENT '输出节点',
  `concurrency` int(11) DEFAULT '1' COMMENT '调度并发数',
  `schedule_status` varchar(50) DEFAULT NULL COMMENT '调度状态',
  `schedule_owner` varchar(100) DEFAULT NULL COMMENT '调度运维Owner',
  `cpus` int(11) DEFAULT '1' COMMENT 'CPU数',
  `mem` int(11) DEFAULT '2048' COMMENT '内存（MB）',
  `limit_type` int(11) DEFAULT NULL COMMENT '限速类型',
  `limit_val` int(11) DEFAULT NULL COMMENT '限速值',
  `created_by` varchar(100) DEFAULT NULL COMMENT '创建人',
  `updated_by` varchar(100) DEFAULT NULL COMMENT '更新人',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_schedule_status` (`schedule_status`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='任务调度配置表';
```

## 字段说明

| 字段名 | 类型 | 必填 | 说明 | 测试值示例 |
|-------|------|-----|------|-----------|
| id | bigint(20) | 是 | 调度配置唯一标识 | 1001 |
| task_code_dir | varchar(255) | 否 | 任务脚本/代码存储路径 | "/dataops/task/user" |
| schedule_type | varchar(50) | 否 | 调度类型：normal(正常)/empty(空跑) | "normal" |
| stop_scheduling | tinyint(1) | 否 | 0-运行，1-停止 | 0 |
| scheduling_cycle | varchar(50) | 否 | 周期：day/week/month/hour/min | "day" |
| scheduling_time | varchar(100) | 否 | 定时时间或Crontab表达式 | "02:00" |
| upstream | varchar(500) | 否 | 上游依赖节点（逗号分隔） | "node_start_01" |
| session_output | varchar(500) | 否 | 任务输出标识 | "out_user_sync" |
| schedule_status | varchar(50) | 否 | 调度引擎中的实时状态 | "RUNNING" |
| cpus | int(11) | 否 | CPU资源配额（核） | 1 |
| mem | int(11) | 否 | 内存资源配额（MB） | 2048 |
| created_at | timestamp | 是 | 配置创建时间 | "2023-10-27 10:00:00" |

## 关键字段

- **stop_scheduling**: 调度开关。测试时需验证置为 `1` 后，调度引擎是否停止触发该任务。
- **scheduling_cycle & scheduling_time**: 定义任务的执行频次。必须成对校验，如周期为 `day` 时，时间格式通常为 `HH:mm`。
- **upstream**: 血缘依赖核心。定义了任务执行的前置条件，若上游未完成，该任务应处于等待状态。
- **schedule_type**: 区分执行逻辑。`empty` 类型通常用于测试流程链路，而不实际搬运数据。

## 业务规则

- **依赖不闭环**: `upstream` 配置不能形成循环依赖，否则会导致死锁。
- **时间窗冲突**: 同一 `task_code_dir` 下的并发任务受 `concurrency` 限制，默认单并发以保证数据序。
- **资源隔离**: `cpus` 和 `mem` 限制了执行容器的资源边界，超限会导致任务被调度器终止（OOM）。
- **默认周期**: 未指定周期时，系统默认按 `day` (每日一次) 处理。

## 关联组件

- `[TKD_007]` 抽数节点配置表: 通过其 `extract_schedule_config_id` 字段关联本表，定义该抽数节点何时运行。
- `[TKD_006]` 流程实例表: 调度每次成功触发后，会向该表写入一条执行实例记录。

## 状态流转

```
0 (运行/ACTIVE)
  ↓
1 (停止/STOPPED)
```

---
**质量检查**: 
- [x] 元数据包含 `database` 字段
- [x] 包含完整的 `CREATE TABLE` 语句
- [x] 字段说明表包含测试值示例
- [x] 已移除原内容中的 SQL 查询示例（禁止项）
- [x] 无详细数据准备步骤
```