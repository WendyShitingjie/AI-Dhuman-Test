# Skill 桥接 Action 说明文档

## 1. 概述

Skill 桥接是 aitestrunner 框架的核心特性之一，它实现了 **测试用例（YAML）与 Claude Code Skill 之间的无缝连接**。通过桥接层，测试用例可以使用声明式的 YAML 语法调用复杂的 Skill 能力，而无需关心底层实现细节。

### 1.1 设计理念

- **统一入口**：提供一致的 Action 接口，屏蔽不同 Skill 的调用差异
- **参数透传**：支持将测试用例中的参数透明传递给 Skill 脚本
- **结果封装**：统一 Skill 的返回格式，便于断言和后续步骤使用
- **上下文共享**：通过 Context 机制实现步骤间数据共享

### 1.2 架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                     YAML 测试用例                                 │
│  action: jdbc_warehouse_test                                    │
│  params:                                                         │
│    instance_name: cjjcommon                                     │
│    db_name: dataops                                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Action Registry                                │
│  jdbc_warehouse_test → JdbcWarehouseTestAction                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Skill Bridge Layer                              │
│  - 参数转换                                                      │
│  - 脚本路径解析                                                  │
│  - subprocess 调用                                               │
│  - 结果封装                                                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Claude Code Skill                             │
│  skills/jdbc-warehouse-test/scripts/template_updater.py         │
└─────────────────────────────────────────────────────────────────┘
```

## 2. 核心组件

### 2.1 ActionRegistry（动作注册表）

采用单例模式管理所有 Action 的注册和获取。

```python
class ActionRegistry:
    _instance = None
    _Actions: Dict[str, ExecutionAction] = {}
    
    def register(self, Action_class: Type[ExecutionAction]):
        """注册动作类"""
        Action = Action_class()
        self._Actions[Action.metadata.name] = Action
        return Action_class
    
    def get(self, name: str) -> ExecutionAction:
        """根据名称获取动作"""
        if name not in self._Actions:
            raise ValueError(f"动作不存在: {name}")
        return self._Actions[name]
```

### 2.2 装饰器注册模式

使用 `@action_registry.register_decorator()` 装饰器自动注册 Action：

```python
@action_registry.register_decorator()
class JdbcWarehouseTestAction(ExecutionAction):
    metadata = ActionMetadata(
        name='jdbc_warehouse_test',  # Action 唯一标识
        category='skill_bridge',      # 分类
        description='生成JDBC入仓测试文件',
        parameters=[...],              # 参数定义
        returns={...}                 # 返回值定义
    )
    
    def execute(self, context, **params) -> Dict[str, Any]:
        # 实现逻辑
        return {'status': 'SUCCESS', 'message': '...'}
```

### 2.3 ExecutionAction 基类

所有 Action 必须继承 `ExecutionAction` 基类：

```python
class ExecutionAction(ABC):
    @property
    @abstractmethod
    def metadata(self) -> ActionMetadata:
        """元数据定义"""
        pass
    
    @abstractmethod
    def execute(self, context, **params) -> Dict[str, Any]:
        """执行逻辑"""
        pass
    
    def validate_parameters(self, params: Dict):
        """参数校验（可选）"""
        for param_def in self.metadata.parameters:
            if param_def.get('required') and param_def['name'] not in params:
                raise ValueError(f"缺少必需参数: {param_def['name']}")
```

## 3. 最佳实践

### 3.1 创建 Skill Bridge Action 的标准流程

#### Step 1: 确定 Skill 路径和入口脚本

```python
SKILLS_DIR = os.path.join(BASE_DIR, 'skills')
skill_dir = os.path.join(SKILLS_DIR, 'skill-name')

# 支持多种脚本位置
main_script = os.path.join(skill_dir, 'scripts', 'index.py')
if not os.path.exists(main_script):
    main_script = os.path.join(skill_dir, 'main.py')
```

#### Step 2: 定义清晰的元数据

```python
metadata = ActionMetadata(
    name='action_name',                    # 唯一标识
    category='skill_bridge',               # 分类：skill_bridge/business/generic
    description='功能描述',                 # 描述
    parameters=[                           # 参数定义
        {
            'name': 'param1',
            'type': 'str',
            'required': True,
            'description': '参数说明'
        },
        {
            'name': 'optional_param',
            'type': 'int',
            'required': False,
            'default': 10,
            'description': '可选参数'
        }
    ],
    returns={                              # 返回值定义
        'status': 'SUCCESS/FAIL',
        'message': '执行结果消息',
        'output_data': '输出数据'
    }
)
```

#### Step 3: 实现参数转换逻辑

```python
def execute(self, context, **params) -> Dict[str, Any]:
    # 从 params 提取参数
    param1 = params.get('param1')
    optional = params.get('optional_param', 10)  # 带默认值
    
    # 从 context 获取前序步骤的数据
    previous_data = context.get('previous_step_key')
    
    # 构造 Skill 脚本需要的参数格式
    skill_args = [...]
    
    # 执行
    result = subprocess.run(...)
    
    # 处理返回结果
    if result.returncode == 0:
        # 成功处理
        return {'status': 'SUCCESS', 'message': '...'}
    else:
        # 失败处理
        return {'status': 'FAIL', 'message': result.stderr}
```

#### Step 4: 将关键数据存入 Context

```python
# 将需要后续步骤使用的数据存入 context
context.set('key_name', value)
context.set('task_id', task_id)
context.set('created_tables', table_list)

return {
    'status': 'SUCCESS',
    'message': f'操作成功',
    'output_key': output_value  # 也会存入 context
}
```

### 3.2 参数传递规范

#### YAML 测试用例中的参数

```yaml
- action: action_name
  params:
    param1: value1
    param2: value2
    # 引用上下文中的值
    taskId: "${context.taskId}"
```

#### Skill 脚本的参数接收

```python
# 方式1: 命令行参数
args = ['python', 'script.py', param1, param2]

# 方式2: JSON 字符串参数
import json
skill_args = json.dumps({'param1': param1, 'param2': param2})
args = ['python', 'script.py', skill_args]

# 方式3: 环境变量
env = os.environ.copy()
env['PARAM1'] = param1
result = subprocess.run(args, env=env)
```

### 3.3 错误处理最佳实践

```python
def execute(self, context, **params) -> Dict[str, Any]:
    try:
        # 1. 参数校验
        self.validate_parameters(params)
        
        # 2. 路径检查
        skill_dir = os.path.join(SKILLS_DIR, self.skill_name)
        if not os.path.exists(skill_dir):
            return {
                'status': 'FAIL',
                'message': f'Skill 目录不存在: {skill_dir}',
                'hint': '请确保 skill 已正确安装'
            }
        
        # 3. 脚本存在性检查
        script_path = os.path.join(skill_dir, 'main.py')
        if not os.path.exists(script_path):
            # 尝试备用路径
            script_path = os.path.join(skill_dir, 'scripts', 'index.py')
        
        # 4. subprocess 调用
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=120,  # 设置超时
            env=env
        )
        
        # 5. 结果检查
        if result.returncode == 0:
            return {'status': 'SUCCESS', 'message': '...'}
        else:
            return {
                'status': 'FAIL',
                'message': f'Skill 执行失败',
                'error': result.stderr,
                'stdout': result.stdout
            }
            
    except subprocess.TimeoutExpired:
        return {'status': 'FAIL', 'message': 'Skill 执行超时'}
    except Exception as e:
        return {'status': 'FAIL', 'message': f'调用 Skill 时出错: {str(e)}'}
```

### 3.4 日志和调试

```python
import logging

def execute(self, context, **params) -> Dict[str, Any]:
    # 使用 print 进行调试输出
    print(f"[DEBUG] 接收参数: {params}")
    print(f"[DEBUG] Context 数据: {context.get_all()}")
    
    # 打印 Skill 调用信息
    print(f"🚀 调用 Skill: {self.skill_name}")
    print(f"   脚本路径: {script_path}")
    print(f"   执行参数: {args}")
    
    # 打印返回结果
    if result.returncode == 0:
        print(f"✅ Skill 执行成功")
    else:
        print(f"❌ Skill 执行失败: {result.stderr}")
```

### 3.5 Context 使用规范

```python
# 存入数据
context.set('task_id', 123)
context.set('created_tables', ['table1', 'table2'])

# 获取数据（带默认值）
task_id = context.get('task_id', 0)

# 获取前序步骤的返回值
previous_result = context.get('previous_action_output')

# 在 YAML 中引用
# taskId: "${context.task_id}"
```

## 4. 完整示例

### 4.1 Skill Bridge Action 示例

```python
@action_registry.register_decorator()
class ExampleSkillBridgeAction(ExecutionAction):
    """示例 Skill 桥接动作"""
    
    metadata = ActionMetadata(
        name='example_bridge',
        category='skill_bridge',
        description='示例 Skill 桥接动作',
        parameters=[
            {'name': 'input_param', 'type': 'str', 'required': True, 'description': '输入参数'},
            {'name': 'output_file', 'type': 'str', 'required': False, 'description': '输出文件路径'}
        ],
        returns={
            'status': 'SUCCESS/FAIL',
            'message': '执行结果',
            'output_path': '输出文件路径'
        }
    )
    
    def execute(self, context, **params) -> Dict[str, Any]:
        import subprocess
        import shutil
        
        # 1. 获取参数
        input_param = params.get('input_param')
        output_file = params.get('output_file', 'default_output.txt')
        
        # 2. 确定 Skill 路径
        skill_dir = os.path.join(SKILLS_DIR, 'example-skill')
        script_path = os.path.join(skill_dir, 'main.py')
        
        if not os.path.exists(script_path):
            return {
                'status': 'FAIL',
                'message': f'Skill 脚本不存在: {script_path}'
            }
        
        # 3. 构造执行参数
        args = ['/usr/local/bin/python3', script_path, '--input', input_param]
        
        # 4. 设置环境变量
        env = os.environ.copy()
        env['PYTHONUTF8'] = '1'
        
        # 5. 执行 Skill
        try:
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=120,
                env=env
            )
            
            if result.returncode == 0:
                # 6. 存入 Context 供后续使用
                context.set('example_output', result.stdout)
                context.set('example_param', input_param)
                
                return {
                    'status': 'SUCCESS',
                    'message': 'Skill 执行成功',
                    'output_path': output_file
                }
            else:
                return {
                    'status': 'FAIL',
                    'message': f'Skill 执行失败: {result.stderr}'
                }
                
        except subprocess.TimeoutExpired:
            return {'status': 'FAIL', 'message': 'Skill 执行超时'}
        except Exception as e:
            return {'status': 'FAIL', 'message': f'执行错误: {str(e)}'}
```

### 4.2 YAML 测试用例使用示例

```yaml
- intent: "步骤1：调用 Skill Bridge Action"
  action: example_bridge
  params:
    input_param: "test_value"
    output_file: "/tmp/output.txt"
  assertions:
    - intent: "验证执行成功"
      action: assert_result_equals
      params:
        expected: "SUCCESS"
        actual: "${context.example_bridge.status}"
```

## 5. 常见问题与解决方案

### 5.1 Skill 脚本路径找不到

**问题**: `未找到 skill 脚本`

**解决**:
```python
# 支持多种路径查找
possible_paths = [
    os.path.join(SKILLS_DIR, skill_name, 'main.py'),
    os.path.join(SKILLS_DIR, skill_name, 'scripts', 'index.py'),
    os.path.join(SKILLS_DIR, skill_name, 'scripts', f'{skill_name}.py'),
]

for path in possible_paths:
    if os.path.exists(path):
        script_path = path
        break
```

### 5.2 参数传递失败

**问题**: Skill 脚本接收不到参数

**解决**:
```python
# 使用 json.dumps 传递复杂参数
skill_args = json.dumps(params, ensure_ascii=False)
args = ['python', 'script.py', skill_args]

# 或使用 --key value 格式
args = ['python', 'script.py']
for key, value in params.items():
    args.extend([f'--{key}', str(value)])
```

### 5.3 编码问题

**问题**: 中文参数或输出出现乱码

**解决**:
```python
# 设置环境变量
env = os.environ.copy()
env['PYTHONUTF8'] = '1'

# subprocess 使用 text=True
result = subprocess.run(
    args,
    capture_output=True,
    text=True,  # 自动解码
    encoding='utf-8'  # 指定编码
)
```

### 5.4 超时处理

**问题**: Skill 执行时间过长导致测试卡住

**解决**:
```python
result = subprocess.run(
    args,
    capture_output=True,
    text=True,
    timeout=120  # 2分钟超时
)

# 捕获超时异常
except subprocess.TimeoutExpired:
    return {'status': 'FAIL', 'message': 'Skill 执行超时'}
```

### 5.5 相对路径问题

**问题**: Skill 脚本中使用相对路径导致文件找不到

**解决**:
```python
# 在执行时指定 cwd
result = subprocess.run(
    args,
    capture_output=True,
    text=True,
    cwd=skill_dir  # 在 Skill 目录下执行
)
```

## 6. 目录结构规范

```
aitestrunner/
├── actions/
│   ├── action_registry.py       # 注册中心
│   ├── base.py                  # 基类定义
│   ├── generic/                 # 通用 Action
│   │   ├── skill_bridge.py      # Skill 桥接（重点）
│   │   ├── api_operation.py
│   │   └── ...
│   └── business/                # 业务 Action
│       └── dataops/
│           ├── api.py           # 业务 API
│           └── db_assertion.py  # 数据库断言
├── cases/                       # 测试用例
│   └── TC_xxx.yaml
├── config/
│   └── config.yaml
└── skills/                      # 技能目录（软链接或复制）
    ├── skill-a/
    │   ├── main.py
    │   └── scripts/
    └── skill-b/
```

## 7. 总结

Skill 桥接是实现 **声明式测试** 的关键技术。通过遵循本文档的最佳实践，可以：

1. **解耦测试用例与实现**：测试用例只需声明式描述，无需关心 Skill 内部实现
2. **复用 Skill 能力**：一次开发，多处复用
3. **统一错误处理**：标准化的错误返回格式
4. **便于调试**：清晰的日志输出和问题定位
5. **可扩展**：新增 Skill 只需编写对应的 Bridge Action

> **提示**：在实际项目中，建议为每个 Skill 创建独立的 Bridge Action 类，保持代码组织清晰。
