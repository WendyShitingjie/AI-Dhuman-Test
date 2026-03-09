# Skill 桥接固定套路（5步完成）

## 快速模板

把下面的代码复制到 `aitestrunner/actions/generic/skill_bridge.py` 文件末尾，然后按注释修改即可。

```python
# ========== 第1步：复制以下模板 ==========
@action_registry.register_decorator()
class YourSkillNameAction(ExecutionAction):
    """你的 Skill 名称"""

    metadata = ActionMetadata(
        name='your_action_name',           # ⚠️ 修改：Action 唯一名称
        category='skill_bridge',            # 固定：skill_bridge
        description='功能描述',              # ⚠️ 修改：描述
        parameters=[                        # ⚠️ 修改：你的参数
            {'name': 'param1', 'type': 'str', 'required': True, 'description': '参数1说明'},
            {'name': 'param2', 'type': 'int', 'required': False, 'default': 10, 'description': '参数2说明'}
        ],
        returns={
            'status': 'SUCCESS/FAIL',
            'message': '执行结果',
            'output_key': '输出值'          # ⚠️ 修改：你的返回值
        }
    )

    def execute(self, context, **params) -> Dict[str, Any]:
        import subprocess
        
        # ========== 第2步：提取参数 ==========
        param1 = params.get('param1')
        param2 = params.get('param2', 10)
        
        # ========== 第3步：找 Skill 脚本路径 ==========
        skill_dir = os.path.join(SKILLS_DIR, '你的skill目录名')
        
        if not os.path.exists(skill_dir):
            return {'status': 'FAIL', 'message': f'Skill目录不存在: {skill_dir}'}
        
        # 支持多种脚本名
        script_path = os.path.join(skill_dir, 'main.py')
        if not os.path.exists(script_path):
            script_path = os.path.join(skill_dir, 'scripts', 'index.py')
        if not os.path.exists(script_path):
            return {'status': 'FAIL', 'message': f'找不到脚本: {skill_dir}'}
        
        # ========== 第4步：构造执行命令 ==========
        # 方式A：命令行参数
        args = ['/usr/local/bin/python3', script_path, param1, str(param2)]
        
        # 方式B：JSON 参数（复杂参数用这个）
        # import json
        # skill_args = json.dumps(params, ensure_ascii=False)
        # args = ['/usr/local/bin/python3', script_path, skill_args]
        
        env = os.environ.copy()
        env['PYTHONUTF8'] = '1'
        
        try:
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=120,          # 超时时间
                env=env
            )
            
            # ========== 第5步：处理结果 ==========
            if result.returncode == 0:
                # 成功：存入 context 供后续使用
                context.set('my_output', result.stdout)
                
                return {
                    'status': 'SUCCESS',
                    'message': '执行成功',
                    'output_key': result.stdout
                }
            else:
                return {
                    'status': 'FAIL',
                    'message': f'Skill执行失败: {result.stderr}'
                }
                
        except subprocess.TimeoutExpired:
            return {'status': 'FAIL', 'message': '执行超时'}
        except Exception as e:
            return {'status': 'FAIL', 'message': f'错误: {str(e)}'}


# ========== 在 YAML 中使用 ==========
# - action: your_action_name
#   params:
#     param1: "值1"
#     param2: 20
```

---

## 完整例子：把 "hello-skill" 桥接到 Action

假设你有一个 Skill 目录：`skills/hello-skill/main.py`

### Skill 脚本内容（参考）
```python
# skills/hello-skill/main.py
import sys

name = sys.argv[1] if len(sys.argv) > 1 else "World"
print(f"Hello, {name}!")
```

### 桥接后的 Action
```python
@action_registry.register_decorator()
class HelloSkillAction(ExecutionAction):
    """Hello Skill 桥接"""

    metadata = ActionMetadata(
        name='hello_skill',
        category='skill_bridge',
        description='打印 Hello',
        parameters=[
            {'name': 'name', 'type': 'str', 'required': True, 'description': '姓名'}
        ],
        returns={
            'status': 'SUCCESS/FAIL',
            'message': '执行结果',
            'output': '输出内容'
        }
    )

    def execute(self, context, **params) -> Dict[str, Any]:
        import subprocess
        
        name = params.get('name', 'World')
        
        skill_dir = os.path.join(SKILLS_DIR, 'hello-skill')
        script_path = os.path.join(skill_dir, 'main.py')
        
        if not os.path.exists(script_path):
            return {'status': 'FAIL', 'message': f'脚本不存在: {script_path}'}
        
        args = ['/usr/local/bin/python3', script_path, name]
        
        try:
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                context.set('hello_output', result.stdout)
                return {'status': 'SUCCESS', 'message': '执行成功', 'output': result.stdout}
            else:
                return {'status': 'FAIL', 'message': result.stderr}
                
        except Exception as e:
            return {'status': 'FAIL', 'message': str(e)}
```

### YAML 测试用例
```yaml
test_id: TC_HELLO_001
test_name: Hello Skill 测试

steps:
  - intent: "打招呼"
    action: hello_skill
    params:
      name: "张三"
```

---

## 常见调用方式

### 方式1：命令行参数（简单参数）
```python
args = ['python', 'script.py', arg1, arg2, '--flag']
```

### 方式2：JSON 参数（复杂参数）
```python
import json
skill_args = json.dumps(params, ensure_ascii=False)
args = ['python', 'script.py', skill_args]
```

### 方式3：环境变量
```python
env = os.environ.copy()
env['PARAM1'] = param1
env['PARAM2'] = str(param2)
result = subprocess.run(['python', 'script.py'], env=env)
```

---

## 一图看懂

```
YAML 测试用例
┌─────────────────────┐
│ action: hello_skill │
│ params:             │
│   name: "张三"      │
└─────────────────────┘
          │
          ▼
ActionRegistry 查找
┌─────────────────────┐
│ hello_skill →       │
│ HelloSkillAction    │
└─────────────────────┘
          │
          ▼
skill_bridge.py 执行
┌─────────────────────┐
│ 1. 提取参数         │
│ 2. 找脚本路径       │
│ 3. subprocess 调用 │
│ 4. 返回结果         │
└─────────────────────┘
          │
          ▼
Skill 脚本执行
┌─────────────────────┐
│ python main.py 张三 │
└─────────────────────┘
```

---

## 快速检查清单

- [ ] Skill 脚本放在 `skills/你的skill名/` 目录下
- [ ] Action 的 `name` 唯一不重复
- [ ] 参数 `type` 正确（str/int/bool/dict）
- [ ] 必要时设置 `timeout` 防止卡死
- [ ] 成功时调用 `context.set()` 存入数据
- [ ] 测试运行：`python run_test.py cases/test.yaml`
