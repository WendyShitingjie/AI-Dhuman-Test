---
component_id: TKD_002
component_name: "入仓任务主表"
component_type: "MySQL"
database: "dataops"  # ⚠️ 必填
table_name: "dataops.dataops_input_task"
business_module: "BIZ_入仓任务(新)"
version: v1.0
created_date: 2026-02-21
---

# 入仓任务主表

## 基础信息
| 属性   | 值                          |
|------|----------------------------|
| 数据库  | dataops                    |
| 表名   | dataops_input_task         |
| 完整表名 | dataops.dataops_input_task |
| 数据源  | MySQL                      |

## 表结构

```sql
CREATE TABLE `dataops_input_task` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `state` int(11) NOT NULL DEFAULT '0' COMMENT '有效状态：0-有效，1-无效',
  `version` int(11) NOT NULL DEFAULT '1' COMMENT '当前最新版本号',
  `created_by` varchar(100) DEFAULT NULL COMMENT '创建人姓名',
  `updated_by` varchar(100) DEFAULT NULL COMMENT '更新人姓名',
  `created_uid` varchar(100) DEFAULT NULL COMMENT '创建人UID',
  `updated_uid` varchar(100) DEFAULT NULL COMMENT '更新人UID',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_state` (`state`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='入仓任务主表';
```

## 字段说明

| 字段名         | 类型           | 必填 | 说明             | 测试值示例                                  |
|-------------|--------------|----|----------------|----------------------------------------|
| id          | bigint(20)   | 是  | 任务唯一标识（自增ID）   | 3137                                   |
| state       | int(11)      | 是  | 有效状态：0-有效，1-无效 | 0                                      |
| version     | int(11)      | 是  | 当前最新版本号，从1开始递增 | 1                                      |
| created_by  | varchar(100) | 否  | 创建人姓名          | "张三"                                   |
| updated_by  | varchar(100) | 否  | 更新人姓名          | "李四"                                   |
| created_uid | varchar(100) | 否  | 创建人唯一标识UID     | "71e8b23d-45e2-497a-b247-f5b807fb4f65" |
| updated_uid | varchar(100) | 否  | 更新人唯一标识UID     | "0b7cd05f-d01a-41f3-8fa1-a3bd773d96ab" |
| created_at  | timestamp    | 是  | 记录创建时间         | "2026-02-21 10:00:00"                  |
| updated_at  | timestamp    | 是  | 记录最后修改时间       | "2026-02-21 10:05:00"                  |

## 关键字段

- **id**: 任务全局唯一标识，是所有关联表的外键基准。
- **state**: 控制任务的逻辑生命周期。
  - 0 (VALID): 有效，前端可见并可执行。
  - 1 (INVALID): 无效/逻辑删除，历史追溯用。
- **version**: 版本控制核心字段。始终指向该任务在 `dataops_input_task_config_version` 表中的最新版本记录。

## 业务规则

- **版本递增机制**: 首次创建 `version=1`；后续任何配置变更均需在关联表生成新记录，并将此字段 `+1`。
- **逻辑删除策略**: 任务删除时不物理删除 `dataops_input_task` 的记录，仅将 `state` 置为 1。
- **数据分层映射**: 任务涉及 Pipeline层(OSS映射)、ODS层(全量存储)及 View层(非敏感展示)。
- **一致性要求**: 主表的 `version` 必须与配置表（TKD_CONFIG）中最新的版本号保持强一致。

## 关联组件

- `[TKD_002]` 任务版本配置表: 通过 `task_id` (对应本表id) 关联，存储详细OSS路径及字段映射。
- `[TKD_004]` 任务操作记录表: 通过 `task_id` 关联，记录试运行、发布、下线等历史。
- `[TKD_005]` 任务实例信息表: 通过 `task_id` 关联，对应DataPhin平台的调度节点ID。

## 状态流转

```
0 (VALID/有效) 
  ↓
1 (INVALID/无效/删除)
```

---
**规范检查**: 
- [x] 元数据包含 `database`
- [x] 包含 `CREATE TABLE`
- [x] 无完整JSON示例
- [x] 字段说明表包含测试值示例
```