# Skill 桥接快速入门指南

## 一分钟快速开始

### 1. 在测试用例中使用 Skill

```yaml
- action: jdbc_warehouse_test
  params:
    instance_name: cjjcommon
    db_name: dataops_shitingjie
```

执行命令：
```bash
cd aitestrunner
python run_test.py cases/你的测试用例.yaml
```

---

## 快速参考

### 常用 Skill Bridge Action

| Action 名称 | 功能 | 关键参数 |
|------------|------|----------|
| `test_create_jdbc_table` | 创建测试表 | `instruction` |
| `metadata_complete` | 完善元数据 | `instance_name`, `db_name`, `tables` |
| `jdbc_warehouse_test` | 生成测试 Excel | `instance_name`, `db_name`, `output_file` |
| `mq_sender` | 发送 MQ 消息 | `taskId`, `instruction` |

### 业务 API Action

| Action 名称 | 功能 |
|------------|------|
| `batch_upload_validate` | 批量上传校验 |
| `query_batch_result` | 查询校验结果 |
| `submit_batch_task` | 提交批量任务 |
| `cancel_batch_task` | 取消批量任务 |

### 断言 Action

| Action 名称 | 功能 |
|------------|------|
| `assert_field_equals` | 断言字段值相等 |
| `assert_record_count` | 断言记录数量 |
| `assert_database_record` | 断言数据库记录 |

---

## YAML 语法速查

### 基本结构
```yaml
- intent: "步骤描述"
  action: action_name
  params:
    key1: value1
    key2: value2
```

### 引用上下文数据
```yaml
params:
  taskId: "${context.taskId}"
  # 引用上一步的结果
  status: "${context.previous_action.status}"
```

### 添加断言
```yaml
- action: batch_upload_validate
  params:
    fileName: "test.xlsx"
  assertions:
    - intent: "验证任务状态"
      action: assert_field_equals
      params:
        table: "dataops_batch_operation_task"
        where: "id = ${context.taskId}"
        field: "task_status"
        expected: "VALIDATE_SUCCESS"
```

### 轮询等待（等待异步结果）
```yaml
- intent: "验证最终状态"
  wait: 300          # 总等待时间（秒）
  poll_interval: 20  # 轮询间隔（秒）
  assertions:
    - intent: "任务执行成功"
      action: assert_field_equals
      params:
        table: "dataops_batch_operation_task"
        where: "id = ${context.taskId}"
        field: "task_status"
        expected: "SUCCESS"
```

---

## 完整示例

### JDBC 入仓全流程测试
```yaml
test_id: TC_TKF001_001
test_name: JDBC批量新增入仓任务_全链路成功场景

preconditions:
  - intent: "创建测试表"
    action: test_create_jdbc_table
    params:
      instruction: "创建 JDBC 测试表"
  - intent: "完善元数据"
    action: metadata_complete
    params:
      instance_name: cjjcommon
      db_name: dataops_shitingjie
      tables: "${context.created_tables}"
  - intent: "生成测试文件"
    action: jdbc_warehouse_test

steps:
  - intent: "批量上传校验"
    action: batch_upload_validate
    params:
      fileName: "${context.created_excel_file}"
    assertions:
      - action: assert_field_equals
        params:
          table: "dataops_batch_operation_task"
          where: "id = ${context.taskId}"
          field: "task_status"
          expected: "VALIDATE_SUCCESS"

  - intent: "提交任务"
    action: submit_batch_task
    params:
      taskId: "${context.taskId}"
    assertions:
      - action: assert_field_equals
        params:
          table: "dataops_batch_operation_task"
          where: "id = ${context.taskId}"
          field: "task_status"
          expected: "PENDING_APPROVAL"

  - intent: "发送审批通过"
    action: mq_sender
    params:
      taskId: "${context.taskId}"
      instruction: "审批通过"

  - intent: "验证最终状态"
    wait: 300
    poll_interval: 30
    assertions:
      - action: assert_field_equals
        params:
          table: "dataops_batch_operation_task"
          where: "id = ${context.taskId}"
          field: "task_status"
          expected: "SUCCESS"
```

---

## 常见问题

### Q: 如何查看可用的 Action 列表？
```bash
cd aitestrunner
python -c "from actions.action_registry import action_registry; action_registry.discover(); print(action_registry.list_all())"
```

### Q: 如何调试参数传递？
在测试执行时查看 DEBUG 日志，会打印：
- `params['xxx']` 接收的参数
- `context.get('xxx')` 上下文数据

### Q: 断言失败怎么办？
1. 检查数据库字段名是否正确
2. 增加 `wait` 时间等待异步处理
3. 查看 HTML 报告中的详细错误信息

### Q: Skill 脚本找不到？
确保 skills 目录结构正确：
```
skills/
├── skill-name/
│   ├── main.py        # 或
│   └── scripts/
│       └── index.py
```

---

## 执行命令汇总

```bash
# 进入测试框架目录
cd aitestrunner

# 运行单个测试用例
python run_test.py cases/TC_xxx.yaml

# 运行所有测试用例
python run_test.py

# 查看测试报告
# 报告生成在 reports/ 目录下
```

---

## 下一步

- 想深入了解实现细节？查看 [docs/Skill_Bridge_Best_Practices.md](./Skill_Bridge_Best_Practices.md)
- 想创建新的 Skill Bridge Action？参考最佳实践文档
