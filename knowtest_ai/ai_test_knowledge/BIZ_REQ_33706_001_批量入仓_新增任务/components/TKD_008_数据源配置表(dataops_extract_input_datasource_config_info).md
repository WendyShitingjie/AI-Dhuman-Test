---
component_id: TKD_008
component_name: "数据源配置表"
component_type: "MySQL"
database: "dataops"  # ⚠️ 必填
table_name: "dataops.dataops_extract_input_datasource_config_info"
business_module: "BIZ_JDBC入仓"
version: v1.0
created_date: 2026-02-23
---

# 数据源配置表

## 基础信息
| 属性   | 值                                                    |
|------|------------------------------------------------------|
| 数据库  | dataops                                              |
| 表名   | dataops_extract_input_datasource_config_info         |
| 完整表名 | dataops.dataops_extract_input_datasource_config_info |
| 数据源  | MySQL                                                |

## 表结构

```sql
CREATE TABLE `dataops_extract_input_datasource_config_info` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '数据源配置ID',
  `datasource_type` varchar(50) NOT NULL COMMENT '数据源类型：mysql/oracle/kafka/sls/oss',
  `instance_name` varchar(100) DEFAULT NULL COMMENT '数据源实例名称',
  `db_name` varchar(100) DEFAULT NULL COMMENT '库名称',
  `table_name` varchar(255) DEFAULT NULL COMMENT '表名称',
  `business_owner` varchar(100) DEFAULT NULL COMMENT '业务负责人',
  `business_owner_dept` varchar(200) DEFAULT NULL COMMENT '业务负责人所在部门',
  `business_owner_uid` varchar(100) DEFAULT NULL COMMENT '业务负责人UID',
  `business_scene` varchar(500) DEFAULT NULL COMMENT '业务场景',
  `user_journey` varchar(200) DEFAULT NULL COMMENT '用户旅程节点',
  `technical_owner` varchar(100) DEFAULT NULL COMMENT '技术负责人',
  `technical_owner_dept` varchar(200) DEFAULT NULL COMMENT '技术负责人部门',
  `technical_owner_uid` varchar(100) DEFAULT NULL COMMENT '技术负责人UID',
  `is_exist_update` tinyint(1) DEFAULT '0' COMMENT '是否存在更新字段',
  `is_exist_delete` tinyint(1) DEFAULT '0' COMMENT '是否存在删除字段',
  `has_id_pk` tinyint(1) DEFAULT '0' COMMENT 'id是否为主键',
  `is_slave` tinyint(1) DEFAULT '0' COMMENT '库是否为从库',
  `is_primary_system` tinyint(1) DEFAULT '0' COMMENT '是否有私有化系统',
  `daily_data_cnt` bigint(20) DEFAULT '0' COMMENT '每日新增数据量',
  `data_cnt` bigint(20) DEFAULT '0' COMMENT '表总数据量',
  `data_size` bigint(20) DEFAULT '0' COMMENT '表数据大小（字节）',
  `source_table_count` varchar(20) DEFAULT 'single' COMMENT '来源表量：single(单表)/multi(多表)',
  `data_type` int(11) DEFAULT '0' COMMENT '数据类型：0(非资信数据)/1(资信数据)',
  `file_format` varchar(50) DEFAULT NULL COMMENT '文件格式：JSONArray/JSONObject/CSV/TXT',
  `field_split` varchar(10) DEFAULT NULL COMMENT '字段分隔符',
  `skip_line_num` int(11) DEFAULT '0' COMMENT '跳过行数',
  `date_partition_field_format` varchar(200) DEFAULT NULL COMMENT 'OSS分区路径格式',
  `created_time_column` varchar(100) DEFAULT NULL COMMENT '创建时间字段名',
  `updated_time_column` varchar(100) DEFAULT NULL COMMENT '更新时间字段名',
  `etlx_datasource` varchar(255) DEFAULT NULL COMMENT '抽数系统数据源名称',
  `etlx_config_oss_location` varchar(500) DEFAULT NULL COMMENT 'ETLx配置文件OSS路径',
  `env` varchar(50) DEFAULT NULL COMMENT 'SLS环境：prod/test',
  `sls_project` varchar(200) DEFAULT NULL COMMENT 'SLS项目名称',
  `sls_log_store` varchar(200) DEFAULT NULL COMMENT 'SLS日志库名称',
  `cluster_name` varchar(200) DEFAULT NULL COMMENT 'Kafka集群名称',
  `topic` varchar(255) DEFAULT NULL COMMENT 'Kafka Topic名称',
  `format` varchar(50) DEFAULT NULL COMMENT 'Kafka数据格式',
  `extract_start_time` varchar(50) DEFAULT NULL COMMENT '抽取开始时间',
  `write_table_type` varchar(50) DEFAULT NULL COMMENT '写入表方式',
  `version_field_name` varchar(100) DEFAULT NULL COMMENT '版本字段名称',
  `source_extra` text COMMENT '来源额外配置信息（JSON）',
  `sink_extra` text COMMENT '去向额外配置信息（JSON）',
  `lineage_info` text COMMENT '血缘信息（JSON）',
  `status` int(11) DEFAULT '0' COMMENT '数据源状态：0(正常)/1(已删除)',
  `created_by` varchar(100) DEFAULT NULL COMMENT '创建人',
  `updated_by` varchar(100) DEFAULT NULL COMMENT '更新人',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_datasource` (`datasource_type`, `instance_name`, `db_name`, `table_name`),
  KEY `idx_status` (`status`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='抽数输入数据源配置表';
```

## 字段说明

| 字段名 | 类型 | 必填 | 说明 | 测试值示例 |
|-------|------|-----|------|-----------|
| id | bigint(20) | 是 | 数据源配置唯一标识 | 1001 |
| datasource_type | varchar(50) | 是 | 类型：mysql/tidb/kafka/sls/oss | "mysql" |
| etlx_datasource | varchar(255) | 否 | 抽数系统标识：input_类型_实例_库 | "input_mysql_db1_ot" |
| instance_name | varchar(100) | 否 | 数据库实例名 | "cjjcommon" |
| db_name | varchar(100) | 否 | 数据库名 | "dataops_test" |
| table_name | varchar(255) | 否 | 表名 | "user_info" |
| status | int(11) | 否 | 状态：0-正常，1-已删除 | 0 |
| data_type | int(11) | 否 | 0-非资信数据，1-资信数据 | 0 |
| topic | varchar(255) | 否 | Kafka Topic（仅Kafka类型） | "user_events" |
| created_at | timestamp | 是 | 创建时间 | "2023-10-27 10:00:00" |

## 关键字段

- **datasource_type**: 核心路由字段，决定了哪些附属字段（如 Topic 或 DbName）必须有效。
- **etlx_datasource**: 内部系统生成的唯一标识，格式为 `input_{type}_{instance}_{db}`，用于在组件间传递配置。
- **status**: 逻辑删除标记。查询时必须过滤 `status=0`。
- **data_type**: 安全分级字段。资信数据（1）在后续 ODS/PDW 层会有更严格的访问控制。

## 业务规则

- **唯一性约束**: 同一组合 `(type, instance, db, table)` 在有效状态（status=0）下应保持唯一。
- **逻辑删除策略**: 删除操作仅将 `status` 置为 1，不执行物理删除，以保证执行历史的可追溯性。
- **级联影响**: 修改此表配置会同步影响关联的 `TKD_007` (节点配置) 和调度配置。
- **类型字段依赖**: 
  - MySQL/Tidb 必须提供 `instance_name`, `db_name`, `table_name`。
  - Kafka 必须提供 `cluster_name`, `topic`。
  - OSS 必须提供 `file_format`, `date_partition_field_format`。

## 关联组件

- `[TKD_007]` 抽数节点配置表: 通过 `input_datasource_id` 关联，定义该数据源的具体抽取逻辑。
- `[TKD_006]` 流程实例表: 间接关联。每次抽取任务执行时，会根据此表的配置创建执行实例。

## 状态流转

```
0 (正常/ACTIVE)
  ↓
1 (已删除/DELETED)
```

## JSON 字段结构

### source_extra / sink_extra
```json
{
  "key": "string",
  "value": "string/object"
}
```

### lineage_info (血缘信息)
```json
{
  "upstream": ["string"],
  "downstream": ["string"]
}
```

---
**质量检查**: 
- [x] 元数据包含 `database` 字段
- [x] 包含完整的 `CREATE TABLE` 语句
- [x] 字段说明表包含测试值示例
- [x] 移除了原内容中的 SQL 查询示例（禁止项）
- [x] 无详细数据准备步骤
```