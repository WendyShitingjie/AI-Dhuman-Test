---
document_name: "集成组件规范（TKI）"
component_type: "TKI"
version: v1.0
created_date: 2026-02-10
---

# 集成组件规范（TKI_xxx）

## 📋 基本信息

- **目录**: `components/`
- **文件命名**: `TKI_[序号]_[集成名称].md`
- **职责**: 调用参数 + 返回结果 + 测试知识
- **维护人员**: 开发工程师 + 测试工程师

---

## 📝 元数据规范

```yaml
---
component_id: TKI_[序号]
component_name: "[集成名称]"
component_type: "SDK" | "API" | "RPC" | ...
application: "[所属应用]"  # ⚠️ 必填
provider: "[服务提供方]"
business_module: "[所属业务模块]"
test_type: "真实环境测试（非Mock）" | "Mock测试"
version: v1.0
created_date: YYYY-MM-DD
---
```

**⚠️ 重要**: `application`字段必填！

---

## 📄 必需章节

### 1. 基础信息
表格包含：
- 所属应用
- 调用服务
- 服务提供方
- 测试方式

### 2. 调用参数
- 参数来源（引用数据组件）
- 格式说明

### 3. 返回结果
- 结构说明表格（字段路径、类型、说明）
- 数据保存位置

### 4. 测试要点
- 成功场景断言
- 失败场景断言
- 关键知识

---

## ❌ 禁止内容

- ❌ 完整的JSON/XML示例（只保留结构说明）
- ❌ 详细的字段说明表（只保留字段路径和类型）
- ❌ 测试环境配置（如SQL查询、表结构）
- ❌ 测试数据模板（AI可自行构造）
- ❌ 测试注意事项（通用故障排查知识）

---

## 📋 示例结构

```markdown
---
component_id: TKI_001
component_name: "AI平台SDK集成"
component_type: "SDK"
application: "copilot"  # ⚠️ 必填
provider: "AI智能平台"
business_module: "智能剧本推荐"
test_type: "真实环境测试（非Mock）"
version: v2.0
created_date: 2026-01-15
---

# AI平台SDK集成

## 基础信息
| 属性 | 值 |
|------|-----|
| 所属应用 | copilot |
| 调用服务 | AiPlatformService.generateScript |
| 服务提供方 | AI智能平台 |
| 测试方式 | 真实环境测试（非Mock） |

## 调用参数

### workflow_code（工作流编号）
- **来源**: [TKD_005].agent_workflow_code
- **格式**: 字符串

### input_data（输入数据）
- **来源**: [TKD_001].uid
- **查询条件**: execute_status = 'INIT'
- **格式**: JSON对象

## 返回结果

### 结构说明
| 字段路径 | 类型 | 说明 |
|---------|------|------|
| code | String | 响应码（200=成功） |
| message | String | 响应消息 |
| data | Object | 返回数据 |
| data.script_id | String | 剧本ID |
| data.steps | Array | 剧本步骤列表 |
| data.steps[].step_id | String | 步骤ID |
| data.steps[].content | String | 步骤内容 |

### 数据保存
- [TKD_001].script_content（JSON格式）
- [TKD_002].script_id, script_steps

## 测试要点

### 成功场景断言
```yaml
- field_equals: {field: "code", expected: "200"}
- field_not_null: {field: "data.script_id"}
- array_not_empty: {field: "data.steps"}
```

### 失败场景断言
```yaml
- field_equals: {field: "code", expected: "500"}
- field_not_null: {field: "message"}
```

### 关键知识
- **AI模型特性**: 相同输入可能产生不同输出，测试时只验证结构和必填字段
- **字段映射**: data.steps需要转换为TKD_002的script_steps格式
```

---

## ✅ 质量检查

- [ ] 元数据包含`application`字段
- [ ] 基础信息表完整
- [ ] 调用参数说明参数来源（引用数据组件）
- [ ] 返回结果只包含结构说明（无完整JSON示例）
- [ ] 测试要点包含成功/失败场景断言
- [ ] 无测试环境配置
- [ ] 无测试数据模板

---

**规范版本**: v1.0  
**发布日期**: 2026-02-10

