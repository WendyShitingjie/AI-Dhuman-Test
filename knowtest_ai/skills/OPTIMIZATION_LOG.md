# Skills 优化改进记录

## 改进日期
2026-02-27

## 改进内容

### 1. test-create-jdbctable Skill 优化

#### 改进点：自动生成目标表名

**问题**：
在使用 `copy-table` 命令克隆表时，每次都需要手动指定目标表名。

**解决方案**：
- `--targetTable` 参数改为可选
- 当不提供目标表名时，自动生成：`源表名_MMDD_序号`
- 自动检测同名表，避免冲突

**命名规则**：
- 基础格式：`源表名_MMDD`（如：`adb_json_batch_01_0227`）
- 如果当天已有重复，添加序号：`源表名_MMDD_01`、`源表名_MMDD_02`...

**使用示例**：
```bash
# 旧方式（仍然支持）
python index.py copy-table --sourceTable adb_json_batch_01 --targetTable my_new_table --env adb-realtime

# 新方式（自动生成表名）
python index.py copy-table --sourceTable adb_json_batch_01 --env adb-realtime
# 输出：✓ 自动生成目标表名: adb_json_batch_01_0227
```

**修改文件**：
- `/Users/wendy/PycharmProjects/cc_free_coder/skills/test-table/scripts/index.py`

---

### 2. metadata-complete Skill 优化

#### 改进点：自动推断实例名

**问题**：
每次使用 metadata-complete 时都需要同时提供实例名和数据库名，但实际上很多数据库名是唯一的。

**解决方案**：
- `--instance` 参数改为可选
- 建立数据库名到实例名的映射表
- 当不提供实例名时，根据数据库名自动推断

**映射表**：
```python
DATABASE_TO_INSTANCE_MAP = {
    'dataops_shitingjie': ['cjjcommon'],
    'dataops': ['bigdata-biz'],
    'datagovernor': ['bigdata-biz'],
    'datahub': ['cjjloan'],
    'stjtestadb': ['sitadbrealtimedw'],
    'ares': ['tidb-ares'],
}
```

**使用示例**：
```bash
# 旧方式（仍然支持）
python index.py --instance sitadbrealtimedw --database stjtestadb --table adb_json_batch_test_0227

# 新方式（自动推断实例）
python index.py --database stjtestadb --table adb_json_batch_test_0227
# 输出：✓ 根据数据库名 'stjtestadb' 自动推断实例: sitadbrealtimedw
```

**冲突���理**：
如果一个数据库名存在于多个实例中，会报错提示用户明确指定：
```
✗ 错误: 数据库 'xxx' 存在于多个实例中: instance1, instance2
请使用 --instance 参数明确指定实例
```

**修改文件**：
- `/Users/wendy/PycharmProjects/cc_free_coder/skills/metadata-complete/scripts/index.py`

---

## 优化效果

### 减少用户输入
- **test-create-jdbctable**：从需要提供源表名+目标表名，减少到只需提供源表名
- **metadata-complete**：从需要提供实例名+数据库名，减少到只需提供数据库名

### 提升用户体验
- 自动化命名，避免重复思考表名
- 自动推断实例，减少记忆负担
- 智能检测冲突，避免错误

### 向后兼容
- 所有旧的使用方式仍然完全支持
- 新增功能不影响现有脚本和工作流

---

## 添加新数据库映射

如果需要添加新的数据库到映射表，请编辑：
```
/Users/wendy/PycharmProjects/cc_free_coder/skills/metadata-complete/scripts/index.py
```

在 `DATABASE_TO_INSTANCE_MAP` 字典中添加：
```python
'新数据库名': ['实例名'],
```

---

## 测试验证

### test-create-jdbctable
✅ 自动生成表名功能正常
✅ 重复检测功能正常
✅ 向后兼容性正常

### metadata-complete
✅ 自动推断实例功能正常
✅ 映射表查找正常
✅ 向后兼容性正常

---

## 总结

通过这次优化，两个 skill 都变得更加智能和易用：
1. **减少了不必要的询问**，提升了工作效率
2. **保持了灵活性**，用户仍可明确指定参数
3. **增强了自动化**，让工具更加聪明

这些改进遵循了"约定优于配置"的设计原则，在保证灵活性的同时，为常见场景提供了更便捷的使用方式。
