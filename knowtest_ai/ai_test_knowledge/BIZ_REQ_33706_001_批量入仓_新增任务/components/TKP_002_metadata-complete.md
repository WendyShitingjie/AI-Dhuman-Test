---
component_id: TKP_002
component_name: "表元数据属性补全"
component_type: "Primitive"
primitive_category: "元数据操作"
associated_skill: "metadata-complete"
business_module: "BIZ_JDBC批量入仓"
version: v1.0
created_date: 2026-03-01
---

# 表元数据属性补全原语

## 原语说明
为已存在的数据库表补充入仓业务所需的 5 个关键元数据属性（敏感性、可编辑性等）。

## 输入参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|-----|------|
| tables | Array | 是 | 需要补全属性的表名列表 |

## 执行逻辑
1. 框架识别 `associated_skill: metadata-complete`。
2. **执行指令**：针对 `tables` 列表，循环调用 Skill 指令。
3. Skill 内部先调用 GET 接口获取字段，再调用 POST 接口 `/firekylin/mysql-metadata/mysql/table/metadata:manage` 提交属性。

## 返回结果
- `status`: SUCCESS/FAILURE。

## 使用示例
```yaml
- TKP_002:
    tables: ["batch_test_0301_01", "batch_test_0301_02"]
```