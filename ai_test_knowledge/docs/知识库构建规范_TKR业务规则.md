---
document_name: "业务规则规范（TKR）"
component_type: "TKR"
version: v1.0
created_date: 2026-02-10
---

# 业务规则规范（TKR_xxx）

## 📋 基本信息

- **目录**: `rules/`
- **文件命名**: `TKR_[序号]_[规则名称].md`
- **职责**: 定义业务判断规则和验证方法
- **维护人员**: 业务分析师 + 测试工程师

---

## 📝 元数据规范

```yaml
---
rule_id: TKR_[序号]
rule_name: "[规则名称]"
related_flows: [TKF_001, ...]  # 关联的业务流程
related_components: [TKD_001, ...]  # 关联的组件
version: v1.0
created_date: YYYY-MM-DD
---
```

---

## 📄 必需章节

### 1. 规则说明
- **内容**: 1-2句话描述规则
- **包含**: 判断依据（字段或条件）

### 2. 验证方法
- **YAML格式的验证断言**
- **SQL查询**
- **预期结果**

### 3. 测试数据准备
- **YAML格式的数据准备**

---

## 📄 可选章节

- 规则详细说明（如有复杂逻辑）
- 状态对照表（如有多状态）

---

## ❌ 禁止内容

- ❌ 冗余的场景说明
- ❌ Mock配置（已有独立Mock平台）
- ❌ 详细的业务背景（应在业务流程中说明）

---

## 📋 示例结构

```markdown
---
rule_id: TKR_001
rule_name: "DP数据产出状态判断"
related_flows: [TKF_001]
related_components: [TKD_006]
version: v1.0
created_date: 2026-01-15
---

# DP数据产出状态判断

## 规则说明
判断DataHub中的批次数据是否已产出完成。
**判断依据**: `ads_app_collect_script_result_df.status = 'SUCCESS'`

## 验证方法

```yaml
- field_equals:
    table: "datahub.ads_app_collect_script_result_df"
    field: "status"
    where: "dt = '${batch_date}' AND source = '${source}'"
    expected: "SUCCESS"
```

**SQL查询**:
```sql
SELECT status
FROM datahub.ads_app_collect_script_result_df
WHERE dt = '2026-01-15'
  AND source = 'offline_batch';
```

**预期结果**: `status = 'SUCCESS'`

## 测试数据准备

```yaml
datahub.ads_app_collect_script_result_df:
  - dt: "2026-01-15"
    source: "offline_batch"
    status: "SUCCESS"
    update_time: "2026-01-15 10:00:00"
```

## 状态对照表

| 状态值 | 含义 | 是否可拉取 |
|--------|------|-----------|
| SUCCESS | 数据产出成功 | 是 |
| PROCESSING | 数据产出中 | 否 |
| FAILURE | 数据产出失败 | 否 |
```

---

## ✅ 质量检查

- [ ] 元数据完整
- [ ] 规则说明清晰（1-2句话）
- [ ] 判断依据明确
- [ ] 验证方法包含YAML断言和SQL查询
- [ ] 测试数据准备完整
- [ ] 无冗余场景说明
- [ ] 无Mock配置

---

**规范版本**: v1.0  
**发布日期**: 2026-02-10

