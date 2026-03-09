---
document_name: "原语组件规范（TKP）"
component_type: "TKP"
version: v1.0
created_date: 2026-02-10
---

# 原语组件规范（TKP_xxx）

## 📋 基本信息

- **目录**: `components/`
- **文件命名**: `TKP_[序号]_[原语名称].md`
- **职责**: 原语功能 + 参数 + 测试知识
- **维护人员**: 测试工程师

---

## 📝 元数据规范

```yaml
---
component_id: TKP_[序号]
component_name: "[原语名称]"
component_type: "Primitive"
primitive_category: "数据库操作" | "API调用" | "断言验证" | ...
business_module: "[所属业务模块]"
version: v1.0
created_date: YYYY-MM-DD
---
```

---

## 📄 必需章节

### 1. 原语说明
- 功能描述

### 2. 输入参数
- 参数说明表格

### 3. 执行逻辑
- 步骤化描述

### 4. 返回结果
- 返回值说明

### 5. 使用示例
- YAML格式

### 6. 测试要点
- 关键测试知识

---

## ❌ 禁止内容

- ❌ 详细的代码实现
- ❌ 完整的测试用例
- ❌ 环境配置

---

## 📋 示例结构

```markdown
---
component_id: TKP_001
component_name: "数据库查询原语"
component_type: "Primitive"
primitive_category: "数据库操作"
business_module: "通用"
version: v1.0
created_date: 2026-01-15
---

# 数据库查询原语

## 原语说明
执行SQL查询并返回结果集

## 输入参数

| 参数名 | 类型 | 必填 | 说明 | 默认值 |
|--------|------|-----|------|--------|
| database | String | 是 | 数据库名称 | - |
| sql | String | 是 | SQL查询语句 | - |
| timeout | Integer | 否 | 超时时间（秒） | 30 |

## 执行逻辑

1. 连接指定数据库
2. 执行SQL查询
3. 返回查询结果
4. 关闭数据库连接

## 返回结果

| 字段 | 类型 | 说明 |
|------|------|------|
| status | String | 执行状态（SUCCESS/FAILURE） |
| rows | Array | 查询结果行列表 |
| row_count | Integer | 结果行数 |
| error_message | String | 错误信息（如有） |

## 使用示例

```yaml
- database_query:
    database: "copilot"
    sql: "SELECT * FROM ai_script_recommendation_log WHERE uid = 'CASE_001'"
    timeout: 30
```

## 测试要点

- **连接池管理**: 确保数据库连接正确释放
- **SQL注入防护**: 参数化查询，避免SQL注入
- **超时处理**: 超时后正确抛出异常
```

---

## ✅ 质量检查

- [ ] 元数据完整
- [ ] 原语说明清晰
- [ ] 输入参数表格完整
- [ ] 执行逻辑步骤化
- [ ] 返回结果说明完整
- [ ] 使用示例为YAML格式
- [ ] 测试要点突出关键知识
- [ ] 无详细代码实现
- [ ] 无完整测试用例

---

**规范版本**: v1.0  
**发布日期**: 2026-02-10

