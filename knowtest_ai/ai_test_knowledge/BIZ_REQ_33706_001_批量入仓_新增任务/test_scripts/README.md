# JDBC 批量入仓全链路测试脚本

## 概述

本目录包含 JDBC 批量入仓全链路自动化测试的执行脚本，实现了测试用例 `TC_TKF001_001` 的自动化执行。

## 文件说明

| 文件 | 说明 | 对应测试用例 |
|------|------|-------------|
| `full_workflow.py` | 全链路自动化测试主脚本 | TC_TKF001_001, TC_TKF001_002 |

## 测试用例映射

### TC_TKF001_001: JDBC批量新增入仓任务_全链路成功场景

**YAML 声明式用例**：`ai_test_framework/test_cases/TC_TKF001_001_JDBC批量新增入仓任务_全链路成功场景.yaml`

**Python 命令式实现**：`full_workflow.py --scenario approve`

#### 步骤映射

| YAML 意图 | Python 实现 | 原语/接口 |
|-----------|------------|----------|
| **前置条件1**: 物理表创建 | `step1_prepare_test_file()` 调用 `batch_workflow.py` | TKP_001 |
| **前置条件2**: 元数据完善 | ↑ 同上（batch_workflow 内部调用） | TKP_002 |
| **前置条件3**: Excel 文件构造 | ↑ 同上（batch_workflow 内部调用） | TKP_003 |
| **步骤2**: 批量上传校验 | `step2_upload_validate()` | TKI_003 |
| **步骤3**: 确认校验结果 [TKR_001] | `step3_query_result()` | TKI_004 |
| **步骤4**: 提交批量操作任务 [TKR_002] | `step4_submit_task()` | TKI_005 |
| **步骤5**: 发送审批通过信号 | `step5_send_approval()` | TKP_004 |
| **步骤6**: 结果全链路验证 [TKR_007] | `step6_verify_result()` | verify_publish_result.py |

#### 断言映射

| YAML 断言 | Python 实现 |
|-----------|------------|
| 任务状态 = VALIDATE_SUCCESS | `step3_query_result()` 检查 `success: True` |
| 任务状态 = PENDING_APPROVAL | `step4_submit_task()` 检查响应 success |
| BPM 记录状态 = 4 | 未显式验证（可扩展） |
| 流程实例状态 = 0 | `verify_publish_result.py` SQL 查询验证 |

### TC_TKF001_002: JDBC批量新增入仓任务_审批拒绝场景

**YAML 声明式用例**：`ai_test_framework/test_cases/TC_TKF001_002_JDBC批量新增入仓任务_审批拒绝场景.yaml`

**Python 命令式实现**：`full_workflow.py --scenario reject`

#### 差异点

| 场景 | 步骤5行为 | 预期结果 |
|------|----------|---------|
| 审批通过 | `status: STATUS_APPROVED` | 流程状态 = 0，配置表生成 |
| 审批拒绝 | `status: STATUS_REJECTED` | 任务状态 = VALIDATE_FAILED |

## 使用方法

### 基本用法

```bash
cd /Users/wendy/PycharmProjects/cc_free_coder/JBDC入仓/BIZ_REQ_33706_001_批量入仓_新增任务/test_scripts

# 正常场景（审批通过）- 默认 2 张表
python3 full_workflow.py

# 明确指定场景
python3 full_workflow.py --count 2 --scenario approve

# 审批拒绝场景
python3 full_workflow.py --count 1 --scenario reject
```

### 高级参数

```bash
# 完整参数示例
python3 full_workflow.py \
  --count 2 \
  --scenario approve \
  --db-type mysql \
  --instance cjjcommon \
  --database dataops_shitingjie \
  --env sit03 \
  --wait-time 60

# TiDB 环境测试
python3 full_workflow.py \
  --count 2 \
  --db-type tidb \
  --instance tidb-ares \
  --database ares
```

### 参数说明

| 参数 | 必需 | 默认值 | 说明 |
|------|------|--------|------|
| `--count` | 否 | 2 | 表数量（1-3） |
| `--scenario` | 否 | approve | 测试场景：approve（审批通过）或 reject（审批拒绝） |
| `--db-type` | 否 | mysql | 数据库类型：mysql/tidb/adb |
| `--instance` | 否 | cjjcommon | 实例名 |
| `--database` | 否 | dataops_shitingjie | 数据库名 |
| `--env` | 否 | sit03 | 环境：sit03/sit01/prod |
| `--wait-time` | 否 | 60 | 验证前等待时间（秒） |

## 执行流程

```
┌─────────────────────────────────────────────────────────────┐
│ 步骤1: 准备测试文件                                          │
│   ├─ 创建 N 个测试表 (test-table skill)                     │
│   ├─ 完善元数据 (metadata-complete skill)                    │
│   └─ 生成 Excel 文件 (template_updater.py)                   │
├─────────────────────────────────────────────────────────────┤
│ 步骤2: 批量上传校验                                          │
│   └─ POST /dataops/etlx/batch/v2/validate → TaskId          │
├─────────────────────────────────────────────────────────────┤
│ 步骤3: 查询校验结果（轮询）                                   │
│   └─ GET /dataops/etlx/batch/v2/task/{taskId}/result         │
├─────────────────────────────────────────────────────────────┤
│ 步骤4: 提交批量操作任务                                       │
│   └─ POST /dataops/etlx/batch/v2/submit/{taskId}             │
├─────────────────────────────────────────────────────────────┤
│ 步骤5: 发送审批信号                                          │
│   ├─ 查询数据库获取工单信息                                   │
│   └─ 发送 MQ 消息 (mq-sender skill)                          │
├─────────────────────────────────────���───────────────────────┤
│ 步骤6: 结果全链路验证（等待 60 秒）                           │
│   └─ 验证 4 张配置表数据完整性 (TKR_007)                      │
└─────────────────────────────────────────────────────────────┘
```

## 验证规则

### TKR_001: 校验成功判断

- ✅ `failedRows = 0`
- ✅ `success = True`

### TKR_002: 提交状态判断

- ✅ `task_status = PENDING_APPROVAL`
- ✅ 工单号已生成

### TKR_007: 发布成功判断

验证以下 4 张配置表记录完整性：

| 表 | 字段验证 |
|----|---------|
| TKD_008: 数据源配置表 | `status = 0` |
| TKD_007: 抽数节点配置表 | `extract_method`, `deal_method` 正确 |
| TKD_009: 任务调度配置表 | `scheduling_cycle`, `scheduling_time` 正确 |
| TKD_006: 流程实例表 | `status = 0`（最关键） |

## 输出示例

### 成功场景

```
============================================================
JDBC 批量入仓全链路自动化测试
============================================================
测试场景: approve
表数量: 2
数据库: mysql - cjjcommon.dataops_shitingjie
环境: sit03
开始时间: 2026-03-03 11:00:47

[步骤 1] 准备���试文件（造表 + 完善元数据 + 生成 Excel）
✅ 测试文件已生成: batch_test_latest.xlsx

[步骤 2] 批量上传校验
✅ 上传成功，TaskId: 417

[步骤 3] 查询校验结果（支持轮询）
✅ 校验成功！

[步骤 4] 提交批量操作任务
✅ 提交成功，工单号: RCPLXZRW-202600000039

[步骤 5] 发送审批信号（approve）
✅ MQ 消息发送成功

[步骤 6] 结果全链路验证（TKR_007）
✅ 验证成功！所有记录都已完整发布

============================================================
测试总结
============================================================
测试场景: approve
TaskId: 417
工单号: RCPLXZRW-202600000039
结束时间: 2026-03-03 11:02:30
✅ 全链路测试通过！
```

## 依赖

### Python 依赖

```bash
pip3 install mysql-connector-python pandas openpyxl
```

### Skills 依赖

- `test-table`: 创建测试表
- `metadata-complete`: 完善元数据
- `jdbc-warehouse-test`: 生成测试文件和接口调用
- `mq-sender`: 发送 MQ 消息

### 数据库访问

- **TiDB (cjjcommon)**: 创建测试表
- **MySQL (bigdata-biz)**: 查询工单信息和验证配置表

## 注意事项

1. **等待时间**：步骤6的验证需要等待 MQ 消息处理，默认 60 秒通常足够
2. **表名冲突**：脚本会自动生成带时间戳的表名，避免冲突
3. **环境隔离**：默认使用 sit03 环境，确保不影响生产
4. **清理数据**：测试完成后可能需要手动清理测试表和配置记录

## 扩展阅读

- **业务流程文档**: `../flows/TKF_001_批量入仓_新增任务_全链路工作流.md`
- **业务规则文档**: `../rules/TKR_*.md`
- **接口文档**: `../components/TKI_*.md`
- **YAML 测试用例**: `/ai_test_framework/test_cases/TC_TKF001_*.yaml`

## 维护日志

| 日期 | 版本 | 修改内容 |
|------|------|---------|
| 2026-03-03 | v1.0 | 初始版本，支持审批通过/拒绝两种场景 |
| 2026-03-03 | v1.1 | 修复步骤3状态解析逻辑 |
| 2026-03-03 | v1.2 | 调整默认等待时间为 60 秒 |
