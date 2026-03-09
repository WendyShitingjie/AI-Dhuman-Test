---
component_id: TKP_001
component_name: "自动化物理表造数"
component_type: "Primitive"
primitive_category: "数据构造"
# 明确标注关联的自动化工具
associated_skill: "test-table" 
business_module: "BIZ_JDBC批量入仓"
version: v1.0
created_date: 2026-03-01
---

# 自动化物理表造数原语

## 原语说明
调用自动化工具在指定 MySQL 实例中创建物理表并填充模拟数据。

## 输入参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|-----|------|
| instance_name | String | 是 | 实例名 (如: cjjcommon) |
| db_name | String | 是 | 数据库名 (如: dataops_shitingjie) |
| table_count | Integer | 否 | 创建表的数量 |
| row_count | Integer | 否 | 每张表生成的数据行数 |

## 执行逻辑
1. 框架识别 `associated_skill: test-table`。
2. **执行指令**：`use skill: test-table` 并传入参数。
3. Skill 内部执行 DDL 创建表结构，并执行 DML 插入随机混合数据。

## 返回结果
- `created_tables`: 字符串数组，包含新生成的表名。

## 使用示例
```yaml
- TKP_001:
    instance_name: "cjjcommon"
    db_name: "dataops_shitingjie"
    table_count: 2
    row_count: 10
```