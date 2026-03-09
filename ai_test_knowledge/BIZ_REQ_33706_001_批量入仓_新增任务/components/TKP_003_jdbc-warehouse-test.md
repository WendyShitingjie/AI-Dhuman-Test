---
component_id: TKP_003
component_name: "批量入仓Excel文件生成"
component_type: "Primitive"
primitive_category: "文件构造"
associated_skill: "jdbc-warehouse-test"
business_module: "BIZ_JDBC批量入仓"
version: v1.0
created_date: 2026-03-01
---

# 批量入仓Excel文件生成原语

## 原语说明
基于 `template_updater.py` 工具，根据输入的表名动态生成符合 23 列规格的入仓配置文件。

## 输入参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|-----|------|
| tables | Array | 是 | 填入 Excel 的物理表名列表 |
| extract_method | String | 否 | 抽数方式 (ins/all) |
| deal_method | String | 否 | 处理方式 (merge/append) |

## 执行逻辑
1. 框架识别 `associated_skill: jdbc-warehouse-test`。
2. **执行指令**：运行 `python template_updater.py`，将参数映射至脚本输入。
3. 按照 23 列规格填充：1-4列连接信息，13-14列策略，15-18列调度等。

## 返回结果
- `file_path`: 生成的 `batch_test_latest.xlsx` 绝对路径。

## 使用示例
```yaml
- TKP_003:
    tables: ["batch_test_01"]
    extract_method: "ins"
    deal_method: "merge"
```