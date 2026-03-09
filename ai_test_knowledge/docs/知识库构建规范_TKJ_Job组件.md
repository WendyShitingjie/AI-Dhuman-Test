---
document_name: "Job组件规范（TKJ）"
component_type: "TKJ"
version: v1.0
created_date: 2026-02-10
---

# Job组件规范（TKJ_xxx）

## 📋 基本信息

- **目录**: `components/`
- **文件命名**: `TKJ_[序号]_[Job名称].md`
- **职责**: Job执行逻辑 + 测试知识
- **维护人员**: 开发工程师 + 测试工程师

---

## 📝 元数据规范

```yaml
---
component_id: TKJ_[序号]
component_name: "[Job名称]"
component_type: "Job"
business_module: "[所属业务模块]"
version: v1.0
created_date: YYYY-MM-DD
---
```

---

## 📄 必需章节

### 1. 组件说明
- 1-2句话描述
- 业务价值

### 2. 基础信息
表格包含：
- 所属应用
- Job名称
- JOB描述
- 是否分片

### 3. 输入参数
- 参数规范（YAML格式）
- 参数说明表格

### 4. 执行逻辑
- 步骤化描述
- 引用数据组件和业务规则

### 5. 输出结果
- 成功输出
- 失败输出

### 6. 涉及的数据组件
表格包含：
- 组件ID
- 组件名称
- 用途

### 7. 涉及的业务规则
表格包含：
- 规则ID
- 规则名称

### 8. 测试要点
- 关键测试知识

---

## ❌ 禁止内容

- ❌ "执行方式：异步"（Job本身就是异步，无需说明）
- ❌ "执行时长：XX秒"（取决于数据量，不应固定）
- ❌ 完整的测试用例
- ❌ 详细的环境配置

---

## 📋 示例结构

```markdown
---
component_id: TKJ_001
component_name: "AiScriptUidPullJob"
component_type: "Job"
business_module: "智能剧本推荐"
version: v2.0
created_date: 2026-01-15
---

# AiScriptUidPullJob

## 组件说明
从DataHub拉取待生成剧本的案件名单，并初始化剧本推荐日志记录。
**业务价值**：为批量剧本生成提供数据源

## 基础信息
| 属性 | 值 |
|------|-----|
| 所属应用 | copilot |
| Job名称 | AiScriptUidPullJob |
| JOB描述 | 拉取待生成剧本的案件名单 |
| 是否分片 | 否 |

## 输入参数

### 参数规范
```yaml
external_data:
  source: "offline_batch"
```

### 参数说明
| 参数名 | 类型 | 必填 | 说明 | 示例值 |
|--------|------|-----|------|--------|
| source | String | 是 | 数据源标识 | offline_batch |

## 执行逻辑

```
1. 验证DP数据产出状态（规则TKR_001）
   └─ 查询 datahub.ads_app_collect_script_result_df
   └─ 条件：status = 'SUCCESS'

2. 拉取剧本标准数据
   └─ 查询 datahub.ads_app_collect_script_base_df
   └─ 条件：dt = 当前批次日期

3. 初始化剧本推荐日志
   └─ 插入 copilot.ai_script_recommendation_log
   └─ 状态：INIT

4. 更新Job状态表
   └─ 更新 copilot.ai_script_job_status
   └─ 状态：SUCCESS
```

## 输出结果

### 成功输出
| 表 | 操作 | 说明 |
|----|------|------|
| ai_script_recommendation_log | INSERT | 插入待生成剧本的记录 |
| ai_script_job_status | UPDATE | 更新Job执行状态为SUCCESS |

### 失败输出
| 表 | 操作 | 说明 |
|----|------|------|
| ai_script_job_status | UPDATE | 更新Job执行状态为FAILURE |

## 涉及的数据组件

| 组件ID | 组件名称 | 用途 |
|--------|---------|------|
| TKD_006 | 批次状态表 | 验证DP数据产出状态 |
| TKD_003 | 剧本标准主表 | 拉取剧本标准数据 |
| TKD_001 | 剧本推荐日志表 | 初始化推荐记录 |
| TKD_004 | Job状态表 | 记录Job执行状态 |

## 涉及的业务规则

| 规则ID | 规则名称 |
|--------|---------|
| TKR_001 | DP数据产出状态判断 |

## 测试要点

- **结果验证需轮询等待**：Job是异步执行，需要轮询ai_script_job_status表等待状态变为SUCCESS
- **字段映射关系**：DataHub字段 → copilot字段的映射关系需验证
- **触发方式**：通过公司统一Job调度平台触发
```

---

## ✅ 质量检查

- [ ] 元数据完整
- [ ] 基础信息表包含"所属应用"
- [ ] 输入参数包含参数规范和参数说明
- [ ] 执行逻辑引用了数据组件和业务规则
- [ ] 涉及的数据组件表格完整
- [ ] 测试要点突出关键知识
- [ ] 无"执行方式：异步"说明
- [ ] 无"执行时长"说明

---

**规范版本**: v1.0  
**发布日期**: 2026-02-10

