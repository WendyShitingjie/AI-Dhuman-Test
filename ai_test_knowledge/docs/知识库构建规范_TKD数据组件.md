---
document_name: "数据组件规范（TKD）"
component_type: "TKD"
version: v1.0
created_date: 2026-02-10
---

# 数据组件规范（TKD_xxx）

## 📋 基本信息

- **目录**: `components/`
- **文件命名**: `TKD_[序号]_[表名称].md`
- **职责**: 表结构 + 关键字段 + 测试知识
- **维护人员**: 开发工程师

---

## 📝 元数据规范

```yaml
---
component_id: TKD_[序号]
component_name: "[表名称]"
component_type: "MySQL" | "DataPhin" | "Redis" | ...
database: "[数据库名]"  # ⚠️ 必填
table_name: "[完整表名]"
business_module: "[所属业务模块]"
version: v1.0
created_date: YYYY-MM-DD
---
```

**⚠️ 重要**: `database`字段必填！

---

## 📄 必需章节

### 1. 基础信息
表格包含：
- 数据库
- 表名
- 完整表名
- 数据源（MySQL / DataPhin / ...）

### 2. 表结构
- CREATE TABLE语句

### 3. 字段说明
表格包含：
- 字段名
- 类型
- 必填
- 说明
- 测试值示例

### 4. 关键字段
- 列出测试时需要关注的字段

### 5. 业务规则
- 如有字段级别的业务规则

### 6. 关联组件
- 如有外键或关联关系

---

## 📄 可选章节

- 状态流转（如有状态字段）
- JSON字段结构（如有JSON类型字段）
- 索引说明（如有特殊索引要求）

---

## ❌ 禁止内容

- ❌ 完整的JSON示例（只保留结构说明）
- ❌ 详细的数据准备步骤（AI可自行构造）
- ❌ 测试用例

---

## 📋 示例结构

```markdown
---
component_id: TKD_001
component_name: "剧本推荐日志表"
component_type: "MySQL"
database: "copilot"  # ⚠️ 必填
table_name: "copilot.ai_script_recommendation_log"
business_module: "智能剧本推荐"
version: v2.0
created_date: 2026-01-15
---

# 剧本推荐日志表

## 基础信息
| 属性 | 值 |
|------|-----|
| 数据库 | copilot |
| 表名 | ai_script_recommendation_log |
| 完整表名 | copilot.ai_script_recommendation_log |
| 数据源 | MySQL |

## 表结构

```sql
CREATE TABLE `ai_script_recommendation_log` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `uid` varchar(50) NOT NULL COMMENT '案件ID',
  `execute_status` varchar(20) DEFAULT 'INIT' COMMENT '执行状态',
  `script_content` text COMMENT '剧本内容（JSON格式）',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_uid` (`uid`),
  KEY `idx_execute_status` (`execute_status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='剧本推荐日志表';
```

## 字段说明

| 字段名 | 类型 | 必填 | 说明 | 测试值示例 |
|-------|------|-----|------|-----------|
| id | bigint(20) | 是 | 主键ID | 1 |
| uid | varchar(50) | 是 | 案件ID | "CASE_001" |
| execute_status | varchar(20) | 否 | 执行状态 | "INIT" / "SUCCESS" / "FAILURE" |
| script_content | text | 否 | 剧本内容（JSON格式） | {"steps": [...]} |
| create_time | datetime | 否 | 创建时间 | "2026-01-15 10:00:00" |
| update_time | datetime | 否 | 更新时间 | "2026-01-15 10:30:00" |

## 关键字段

- **uid**: 案件唯一标识，关联DataHub的uid字段
- **execute_status**: 执行状态，用于判断剧本生成进度
  - INIT: 初始化，待生成
  - PROCESSING: 生成中
  - SUCCESS: 生成成功
  - FAILURE: 生成失败
- **script_content**: 剧本内容，JSON格式存储

## 业务规则

- **状态流转**: INIT → PROCESSING → SUCCESS/FAILURE
- **重试机制**: FAILURE状态的记录可重新生成

## 关联组件

- [TKD_003] 剧本标准主表：通过uid关联
- [TKD_002] 剧本推荐表：生成成功后写入

## 状态流转

```
INIT（初始化）
  ↓
PROCESSING（生成中）
  ↓
SUCCESS（成功） / FAILURE（失败）
```

## JSON字段结构

### script_content字段
```json
{
  "steps": [
    {
      "step_id": "string",
      "content": "string"
    }
  ]
}
```
```

---

## ✅ 质量检查

- [ ] 元数据包含`database`字段
- [ ] 基础信息表完整
- [ ] 表结构包含CREATE TABLE语句
- [ ] 字段说明表格完整
- [ ] 关键字段列出
- [ ] 无完整JSON示例（只有结构说明）
- [ ] 无详细数据准备步骤

---

**规范版本**: v1.0  
**发布日期**: 2026-02-10

