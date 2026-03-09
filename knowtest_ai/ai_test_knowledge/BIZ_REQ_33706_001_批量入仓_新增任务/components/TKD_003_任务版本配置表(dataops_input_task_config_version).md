---
component_id: TKD_003
component_name: "任务版本配置表"
component_type: "MySQL"
database: "dataops"
table_name: "dataops.dataops_input_task_config_version"
business_module: "BIZ_入仓任务(新)"
version: v1.2
created_date: 2026-02-21
---

# 任务版本配置表

## 基础信息
| 属性 | 值 |
|------|-----|
| 数据库 | dataops |
| 表名 | dataops_input_task_config_version |
| 完整表名 | dataops.dataops_input_task_config_version |
| 数据源 | MySQL |

## 表结构

```sql
CREATE TABLE `dataops_input_task_config_version` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `task_id` bigint(20) NOT NULL COMMENT '任务ID，关联dataops_input_task.id',
  `version` int(11) NOT NULL COMMENT '版本号，从1开始递增',
  `oss_env` varchar(50) DEFAULT NULL COMMENT 'OSS环境',
  `sync_mode` varchar(20) DEFAULT NULL COMMENT '同步方式：all-全量同步，diff-增量同步',
  `bucket_name` varchar(255) DEFAULT NULL COMMENT 'OSS桶名称',
  `oss_path` varchar(500) DEFAULT NULL COMMENT 'OSS文件路径',
  `ods_columns` text COMMENT 'ODS层同步字段信息（JSON格式）',
  `view_columns` text COMMENT 'View层同步字段信息（JSON格式）',
  `extra_content` text COMMENT '附加信息（存放调度配置信息，JSON格式）',
  `status` int(11) DEFAULT NULL COMMENT '任务状态',
  `state` int(11) NOT NULL DEFAULT '0' COMMENT '有效状态：0-有效，1-无效',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_task_id_version` (`task_id`, `version`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='入仓任务版本配置表';
```

## 字段说明

| 字段名 | 类型 | 必填 | 说明 | 测试值示例 |
|-------|------|-----|------|-----------|
| id | bigint(20) | 是 | 配置记录唯一标识 | 1001 |
| task_id | bigint(20) | 是 | 关联任务主表ID | 3137 |
| version | int(11) | 是 | 版本号，从1递增 | 2 |
| sync_mode | varchar(20) | 否 | 同步方式：all(全量)/diff(增量) | "all" |
| status | int(11) | 否 | 任务生命周期状态 | 0 |
| state | int(11) | 是 | 0-有效，1-无效 | 0 |
| ods_columns | text | 否 | ODS字段映射结构(JSON) | [{"name":"id",...}] |
| view_columns | text | 否 | View层字段过滤结构(JSON) | [{"name":"id",...}] |

## 关键字段

- **task_id & version**: 联合唯一标识，用于追溯特定版本的任务配置。
- **status**: 驱动任务生命周期的核心字段，控制审核、试运行、发布等逻辑。
- **ods_columns / view_columns**: 存储结构化字段定义，是生成底层数据库 Schema 的核心依据。

## 业务规则

- **版本不可变性**: 已发布的版本记录不可修改。配置变更时必须生成 `version + 1` 的新记录。
- **版本状态自动切换**: 当新版本发布成功（status=0）时，同 task_id 下的旧版本状态需自动标记为“历史发布（10）”。
- **三层架构一致性**: 必须保证 Pip层(OSS路径)、ODS层(全量表)、View层(敏感过滤)的字段映射关系在同一版本中逻辑自洽。

## 关联组件

- **[TKD_002] 入仓任务主表**: 通过 `task_id` 关联。主表维护任务基础信息，并始终记录当前最新的 `version`。
- **[TKD_004] 任务操作记录表**: 通过 `task_id` 和 `version` 关联。记录该特定配置版本在执行过程中的操作轨迹（如：谁在何时点击了“试运行”）。
- **[TKD_005] 任务实例信息表**: 通过 `task_id` 关联。将本表的配置（如调度时间）同步至 DataPhin 平台后，记录返回的节点实例 ID。
- **[外部组件] OSS 对象存储**: 本表中的 `bucket_name` 和 `oss_path` 决定了任务的数据来源。

## 状态流转

### 任务状态枚举 (TaskStatusEnum)

| 枚举值 | 枚举常量 | 描述 | 说明 |
|:---|:---|:---|:---|
| **11** | BUSINESS_DEVELOP_INIT | 业务研发初始化 | 初始阶段 |
| **1** | TASK_DBA_AUDIT_RUNNING | DBA审核 | DBA正在审核SQL或配置 |
| **12** | DATASOURCE_PERMISSION_AUDIT | 数据源授权 | 申请底层数据源权限 |
| **2** | DATA_WAREHOUSE_INIT | 数仓初始化 | 创建数仓目标表 |
| **3** | INFO_SECURITY_AUDIT_RUNNING | 信安审核中 | 信息安全合规性检查 |
| **4** | TASK_RERUN_RUNNING | 试运行中 | 任务全流程调度测试 |
| **5** | TASK_RERUN_FAIL | 试运行失败 | 测试未通过 |
| **6** | TASK_RERUN_SUCCESS | 试运行成功 | **具备发布条件** |
| **8** | TASK_PUBLIC_RUNNING | 发布中 | 正在部署到生产系统 |
| **9** | TASK_PUBLIC_FAIL | 发布失败 | 生产部署过程异常 |
| **0** | TASK_PUBLIC_SUCCESS | 发布成功 | **最终态**，任务上线 |
| **7** | TASK_AUDIT_REFUSE | 审核被拒 | 在审核阶段被驳回 |
| **10** | HISTORY_PUBLISH | 历史发布 | 已被新版本替代的旧记录 |
| **100** | TASK_OFFLINE | 任务下线 | 任务已移除 |

## JSON字段结构

### ods_columns / view_columns 结构说明
```json
[
  {
    "name": "string",       // 字段名
    "type": "string",       // 字段类型
    "desc": "string",       // 字段注释
    "isPublished": "boolean" // 是否正式发布
  }
]
```

---
**规范检查**: 
- [x] 已包含 `database` 字段
- [x] 已包含 `CREATE TABLE` 语句
- [x] 已补充「关联组件」章节
- [x] 已补充完整的「任务状态」枚举及说明
- [x] 符合「AI数据组件规范」要求
```