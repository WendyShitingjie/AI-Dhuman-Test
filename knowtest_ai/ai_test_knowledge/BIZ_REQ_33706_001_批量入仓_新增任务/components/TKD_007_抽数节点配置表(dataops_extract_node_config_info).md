---
component_id: TKD_007
component_name: "抽数节点配置表"
component_type: "MySQL"
database: "dataops"  # ⚠️ 必填
table_name: "dataops.dataops_extract_node_config_info"
business_module: "BIZ_JDBC入仓"
version: v1.0
created_date: 2026-02-23
---

# 抽数节点配置表

## 基础信息
| 属性 | 值 |
|------|-----|
| 数据库 | dataops |
| 表名 | dataops_extract_node_config_info |
| 完整表名 | dataops.dataops_extract_node_config_info |
| 数据源 | MySQL |

## 表结构

```sql
CREATE TABLE `dataops_extract_node_config_info` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `extract_schedule_config_id` bigint(20) DEFAULT NULL COMMENT '抽数任务调度配置信息ID',
  `extract_input_datasource_config_id` bigint(20) DEFAULT NULL COMMENT '输入数据源抽数配置ID',
  `extract_type` varchar(50) DEFAULT NULL COMMENT '抽取类型：sqoop、dp、datax等',
  `sub_extract_type` int(11) DEFAULT NULL COMMENT '子抽取类型',
  `task_code_dir` varchar(500) DEFAULT NULL COMMENT '任务代码的全路径',
  `extract_method` varchar(50) DEFAULT NULL COMMENT '抽取方式：ins-增量，all-全量',
  `deal_method` varchar(50) DEFAULT NULL COMMENT '处理方式：ins-增量，all-全量，zip-拉链，merge-合并',
  `split_key` varchar(100) DEFAULT NULL COMMENT '抽数的切分键',
  `batch_count` int(11) DEFAULT 1024 COMMENT '批量条数',
  `input_filter` text COMMENT '输入过滤条件（增量抽取时的WHERE条件）',
  `loading_strategy` varchar(50) DEFAULT 'full_cover' COMMENT '加载策略：full_cover-覆盖数据',
  `partition_by` varchar(255) DEFAULT 'ds=${bizdate}' COMMENT '分区信息（支持参数）',
  `schema_mapping` varchar(50) DEFAULT 'name_mapping' COMMENT '目标表与原表的映射方式',
  `output_db_name` varchar(100) DEFAULT NULL COMMENT '输出表ods_pipeline对应的库名称',
  `output_table_name` varchar(100) DEFAULT NULL COMMENT 'ods_pipeline输出表名称',
  `target_source_type` varchar(50) DEFAULT NULL COMMENT '目标数据源类型',
  `target_db_name` varchar(100) DEFAULT NULL COMMENT 'ods层库名称',
  `target_table_name` varchar(100) DEFAULT NULL COMMENT 'ods层表名称',
  `target_table_ddl` text COMMENT 'ods层表DDL',
  `output_table_ddl` text COMMENT '输出表的DDL',
  `input_node_name` varchar(100) DEFAULT NULL COMMENT '输入组件节点名称',
  `output_node_name` varchar(100) DEFAULT NULL COMMENT '输出组件节点名称',
  `output_datasource` varchar(100) DEFAULT NULL COMMENT '输出的数据源名称',
  `sensitive_key` varchar(500) DEFAULT NULL COMMENT '系统标注的敏感信息',
  `sensitive_manual_key` varchar(500) DEFAULT NULL COMMENT '手工添加的敏感信息',
  `view_project` varchar(100) DEFAULT NULL COMMENT '视图项目名称',
  `param_view` varchar(100) DEFAULT NULL COMMENT 'pdw视图名称',
  `chain_table` varchar(100) DEFAULT NULL COMMENT '拉链表名称',
  `cpus` varchar(20) DEFAULT NULL COMMENT 'CPU资源',
  `memory` int(11) DEFAULT NULL COMMENT '内存资源（MB）',
  `concurrency` int(11) DEFAULT NULL COMMENT '并发数',
  `need_create_view` int(11) DEFAULT NULL COMMENT '是否需要创建视图：0-否，1-是',
  `migration_params` text COMMENT '迁移任务参数（JSON格式）',
  `etlx_fields` text COMMENT '抽数字段配置（JSON格式）',
  `extract_pk_fields` varchar(500) DEFAULT NULL COMMENT '抽数主键字段（逗号分隔）',
  `standard_output_table_name` varchar(100) DEFAULT NULL COMMENT 'ods_pipeline输出表标准名称',
  `standard_target_table_name` varchar(100) DEFAULT NULL COMMENT 'ods层表标准名称',
  `standard_param_view` varchar(100) DEFAULT NULL COMMENT 'pdw视图标准名称',
  `created_by` varchar(100) DEFAULT NULL COMMENT '创建人姓名',
  `updated_by` varchar(100) DEFAULT NULL COMMENT '更新人姓名',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_extract_schedule_config_id` (`extract_schedule_config_id`),
  KEY `idx_extract_input_datasource_config_id` (`extract_input_datasource_config_id`),
  KEY `idx_target_table_name` (`target_table_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='抽数节点配置表';
```

## 字段说明

| 字段名 | 类型 | 必填 | 说明 | 测试值示例 |
|-------|------|-----|------|-----------|
| id | bigint(20) | 是 | 配置记录唯一标识 | 1001 |
| extract_schedule_config_id | bigint(20) | 否 | 关联调度配置表ID | 2001 |
| extract_input_datasource_config_id | bigint(20) | 否 | 关联输入数据源配置表ID | 3001 |
| extract_method | varchar(50) | 否 | 抽取方式：ins(增量)/all(全量) | "ins" |
| deal_method | varchar(50) | 否 | 处理方式：merge(合并)/all(覆盖)/zip(拉链) | "merge" |
| input_filter | text | 否 | 增量抽取的WHERE条件 | "created_at >= '${date}'" |
| output_table_name | varchar(100) | 否 | Pipeline层表名 | "pip_user_info" |
| target_table_name | varchar(100) | 否 | ODS层表名 | "ods_user_info" |
| param_view | varchar(100) | 否 | PDW视图名称 | "pdw_user_info" |
| sensitive_key | varchar(500) | 否 | 系统识别的敏感字段列表 | "phone,id_card" |
| extract_pk_fields | varchar(500) | 否 | 抽数主键字段（逗号分隔） | "id,user_id" |
| created_at | timestamp | 是 | 记录创建时间 | "2026-02-23 10:00:00" |

## 关键字段

- **extract_method & deal_method**: 组合决定了数据入仓的逻辑形态（增量合并、全量覆盖或拉链存储）。
- **input_filter**: 增量抽取的灵魂，决定了从源头读取哪些变化数据。
- **extract_input_datasource_config_id**: 核心外键，指向具体的物理数据库连接配置。
- **sensitive_key / sensitive_manual_key**: 安全合规字段，决定了后续 PDW 视图是否需要自动脱敏。

## 业务规则

- **三层架构逻辑**: 
  - Pipeline层: 结构镜像，暂存区。
  - ODS层: 业务清洗，操作存储区。
  - PDW层: 面向业务，脱敏展示区。
- **抽取处理对应关系**:
  - `ins + merge`: 增量抽取后基于主键合并入全量表。
  - `all + all`: 每天全量抽取并覆盖当日分区。
  - `ins/all + zip`: 构建缓慢变化维（SCD2）历史拉链表。
- **主键依赖**: 在 `merge` 处理模式下，`extract_pk_fields` 必须配置准确，否则会导致数据重复或丢失。

## 关联组件

- `[TKD_009]` 任务调度配置表: 通过 `extract_schedule_config_id` 关联，定义任务何时跑。
- `[TKD_008]` 抽数输入数据源配置表: 通过 `extract_input_datasource_config_id` 关联，定义从哪抽。
- `[TKD_006]` 流程实例表: 任务执行时的动态实例，记录每次抽数的 start/end 时间与状态。

## JSON字段结构

### migration_params / etlx_fields 字段
```json
{
  "key": "string",
  "value": "string/object"
}
```

---
**质量检查**: 
- [x] 元数据包含 `database` 字段
- [x] 包含完整的 `CREATE TABLE` 语句
- [x] 字段说明表包含测试值示例
- [x] 已移除原内容中的 SQL 查询示例（禁止项）
- [x] 无详细数据准备步骤
```