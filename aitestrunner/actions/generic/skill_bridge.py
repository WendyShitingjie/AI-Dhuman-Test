"""Skill 桥接动作 - 将 Claude Code skill 桥接到 aitestrunner 框架

设计理念:
- 提供统一的桥接层，连接 Claude Code skill 和 aitestrunner action 系统
- 支持所有已注册的全局 skill
- 自动处理参数传递和结果返回
- 保持测试用例的可读性和一致性
"""

import subprocess
import json
import os
from typing import Any, Dict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SKILLS_DIR = os.path.join(BASE_DIR, 'skills')

from actions.action_registry import action_registry
from actions.base import ExecutionAction, ActionMetadata


@action_registry.register_decorator()
class JdbcWarehouseTestAction(ExecutionAction):
    """
    JDBC 批量入仓测试文件生成动作

    桥接到全局 skill: jdbc-warehouse-test
    功能: 生成符合 JDBC 批量入仓接口规范的 xlsx 测试文件，支持成功场景和多种异常场景
    """

    metadata = ActionMetadata(
        name='jdbc_warehouse_test',
        category='skill_bridge',
        description='生成符合 JDBC 批量入仓接口规范的 xlsx 测试文件（桥接 jdbc-warehouse-test skill）',
        parameters=[
            {
                'name': 'skill_args',
                'type': 'str',
                'required': False,
                'description': '传递给 skill 的参数字符串'
            },
            {
                'name': 'output_path',
                'type': 'str',
                'required': False,
                'description': '输出文件路径（可选）'
            }
        ],
        returns={
            'status': 'SUCCESS/FAIL',
            'message': '执行结果消息',
            'skill_output': 'skill 执行输出'
        },
        examples=[
            {
                'intent': '生成 JDBC 入仓测试文件',
                'yaml': """
                action: jdbc_warehouse_test
                params:
                  skill_args: "表名=test_table 场景=成功"
                  output_path: "/tmp/test.xlsx"
                """
            }
        ]
    )

    def execute(self, context, **params) -> Dict[str, Any]:
        """
        执行 jdbc-warehouse-test skill
        """
        import subprocess
        import shutil

        instance_name = params.get('instance_name')
        db_name = params.get('db_name')
        tables = params.get('tables', [])
        output_file = params.get('output_file', 'batch_test_latest.xlsx')

        skill_dir = os.path.join(SKILLS_DIR, 'jdbc-warehouse-test')

        if os.path.exists(skill_dir):
            script_path = os.path.join(skill_dir, 'scripts', 'template_updater.py')

            if os.path.exists(script_path):
                try:
                    if not tables:
                        tables = []

                    args = ['/usr/local/bin/python3', script_path,
                            instance_name or 'cjjcommon',
                            db_name or 'dataops_shitingjie',
                            *tables]

                    env = os.environ.copy()
                    env['PYTHONUTF8'] = '1'

                    result = subprocess.run(
                        args,
                        capture_output=True,
                        text=True,
                        timeout=120,
                        cwd=skill_dir,
                        env=env
                    )

                    generated_file = os.path.join(skill_dir, 'test_excel', 'batch_test_latest.xlsx')
                    
                    test_excel_dir = os.path.join(skill_dir, 'test_excel')
                    os.makedirs(test_excel_dir, exist_ok=True)
                    final_output = os.path.join(test_excel_dir, output_file)

                    if os.path.exists(generated_file) and generated_file != final_output:
                        shutil.copy(generated_file, final_output)

                    if result.returncode == 0:
                        context.set('test_file_path', final_output)
                        context.set('created_excel_file', os.path.basename(final_output))

                        return {
                            'status': 'SUCCESS',
                            'message': f'JDBC 入仓测试文件生成成功: {output_file}',
                            'skill_output': result.stdout,
                            'output_file': final_output
                        }
                    else:
                        return {
                            'status': 'FAIL',
                            'message': f'Skill 执行失败: {result.stderr}',
                            'skill_output': result.stderr
                        }
                except Exception as e:
                    return {
                        'status': 'FAIL',
                        'message': f'调用 skill 时出错: {str(e)}',
                        'error': str(e)
                    }

        return {
            'status': 'FAIL',
            'message': f'未找到 skill 脚本: {skill_dir}',
            'hint': '请确保 skill 已正确安装'
        }


@action_registry.register_decorator()
class MetadataCompleteAction(ExecutionAction):
    """
    MySQL 库表元数据完整性管理动作

    桥接到全局 skill: metadata-complete
    功能: 自动化执行 MySQL 库表元数据完整性管理，串联调用 GET 和 POST 接口
    """

    metadata = ActionMetadata(
        name='metadata_complete',
        category='skill_bridge',
        description='自动化执行 MySQL 库表元数据完整性管理（桥接 metadata-complete skill）',
        parameters=[
            {
                'name': 'database',
                'type': 'str',
                'required': True,
                'description': '目标数据库名称'
            },
            {
                'name': 'table',
                'type': 'str',
                'required': False,
                'description': '目标表名（可选，不填则处理整个数据库）'
            },
            {
                'name': 'skill_args',
                'type': 'str',
                'required': False,
                'description': '额外的 skill 参数'
            }
        ],
        returns={
            'status': 'SUCCESS/FAIL',
            'message': '执行结果消息',
            'skill_output': 'skill 执行输出'
        }
    )

    def execute(self, context, **params) -> Dict[str, Any]:
        """执行 metadata-complete skill"""
        import subprocess

        instance_name = params.get('instance_name')
        db_name = params.get('db_name')
        tables = params.get('tables', [])

        print(f"[DEBUG MetadataComplete] instance_name={instance_name}, db_name={db_name}, tables={tables}")

        owner_id = context.get('owner_id', '71e8b23d-45e2-497a-b247-f5b807fb4f65')
        owner_name = context.get('owner_name', '施婷杰')

        skill_dir = os.path.join(SKILLS_DIR, 'metadata-complete')

        if os.path.exists(skill_dir):
            main_script = os.path.join(skill_dir, 'main.py')
            if not os.path.exists(main_script):
                main_script = os.path.join(skill_dir, 'scripts', 'metadata_complete.py')

            if os.path.exists(main_script):
                try:
                    if not tables:
                        tables = []

                    all_results = []
                    for table_name in tables:
                        args = [
                            '/usr/local/bin/python3',
                            main_script,
                            '--instance', instance_name,
                            '--database', db_name,
                            '--table', table_name,
                            '--owner-name', owner_name,
                            '--owner-id', owner_id
                        ]

                        env = os.environ.copy()
                        env['PYTHONUTF8'] = '1'

                        result = subprocess.run(
                            args,
                            capture_output=True,
                            text=True,
                            timeout=120,
                            env=env
                        )

                        all_results.append({
                            'table': table_name,
                            'returncode': result.returncode,
                            'stdout': result.stdout,
                            'stderr': result.stderr
                        })

                    failed = [r for r in all_results if r['returncode'] != 0]
                    if failed:
                        return {
                            'status': 'FAIL',
                            'message': f'Skill 执行失败: {failed[0]["stderr"]}',
                            'skill_output': '\n'.join([r['stderr'] for r in failed])
                        }

                    return {
                        'status': 'SUCCESS',
                        'message': f'元数据完善成功: {[r["table"] for r in all_results]}',
                        'skill_output': '\n'.join([r['stdout'] for r in all_results])
                    }
                except Exception as e:
                    return {
                        'status': 'FAIL',
                        'message': f'调用 skill 时出错: {str(e)}',
                        'error': str(e)
                    }

        return {
            'status': 'FAIL',
            'message': f'未找到 skill 脚本: {skill_dir}',
            'hint': '请确保 skill 已正确安装'
        }


@action_registry.register_decorator()
class MqSenderAction(ExecutionAction):
    """
    MQ 消息发送动作

    桥接到全局 skill: mq-sender
    功能: 通过 mqplus 统一网关向不同业务队列投递消息，支持自动化双重序列化
    """

    metadata = ActionMetadata(
        name='mq_sender',
        category='skill_bridge',
        description='通过 mqplus 统一网关向业务队列投递消息（桥接 mq-sender skill）',
        parameters=[
            {
                'name': 'queue',
                'type': 'str',
                'required': True,
                'description': '目标队列名称'
            },
            {
                'name': 'message',
                'type': 'dict',
                'required': True,
                'description': '消息内容（字典格式）'
            },
            {
                'name': 'skill_args',
                'type': 'str',
                'required': False,
                'description': '额外的 skill 参数'
            }
        ],
        returns={
            'status': 'SUCCESS/FAIL',
            'message': '执行结果消息',
            'skill_output': 'skill 执行输出'
        },
        examples=[
            {
                'intent': '向 MQ 队列发送测试消息',
                'yaml': """
                action: mq_sender
                params:
                  queue: "test_queue"
                  message:
                    uid: "test_user_001"
                    action: "process"
                """
            }
        ]
    )

    def execute(self, context, **params) -> Dict[str, Any]:
        """执行 mq-sender skill"""
        import re
        import pymysql

        task_id = params.get('taskId', '')
        instruction = params.get('instruction', '')

        skill_dir = os.path.join(SKILLS_DIR, 'mq-sender')

        if os.path.exists(skill_dir):
            main_script = os.path.join(skill_dir, 'scripts', 'mq_sender.py')
            if not os.path.exists(main_script):
                main_script = os.path.join(skill_dir, 'mq_sender.py')
            if os.path.exists(main_script):
                try:
                    match = re.search(r'taskid=(\d+)', instruction or '')
                    if match:
                        task_id = match.group(1)

                    from config.settings import settings
                    db_config = {
                        'host': settings.get('database.dataops.host', 'bigdata-biz.db.ali-bj-bdsit01.shuheo.net'),
                        'port': int(settings.get('database.dataops.port', 3306)),
                        'user': settings.get('database.dataops.user', 'bdsit_user_0e0bc33'),
                        'password': settings.get('database.dataops.password', 'bdsit_user_0e0bc33_26587a'),
                        'database': 'dataops',
                        'charset': 'utf8mb4'
                    }

                    conn = pymysql.connect(**db_config)
                    cursor = conn.cursor()

                    cursor.execute(
                        "SELECT bpm_order_no, bpm_process_id, file_name, created_by, created_uid FROM dataops_batch_operation_task WHERE id = %s LIMIT 1",
                        (task_id,)
                    )
                    task_info = cursor.fetchone()

                    cursor.execute(
                        "SELECT order_no, created_uid, created_by FROM dataops_bpm_record WHERE process_instance_node_id = %s AND process_key = 'bg_jdbc_rc_plxz_rw' LIMIT 1",
                        (task_id,)
                    )
                    bpm_info = cursor.fetchone()

                    cursor.close()
                    conn.close()

                    bpm_order_no = str(task_info[0]) if task_info and task_info[0] else ''
                    bpm_process_id = task_info[1] if task_info else ''
                    file_name = task_info[2] if task_info else ''
                    created_by = task_info[3] if task_info else '施婷杰'
                    created_uid = task_info[4] if task_info else '71e8b23d-45e2-497a-b247-f5b807fb4f65'

                    order_no = str(bpm_info[0]) if bpm_info and bpm_info[0] else ''
                    bpm_created_uid = bpm_info[1] if bpm_info else '71e8b23d-45e2-497a-b247-f5b807fb4f65'
                    bpm_created_by = bpm_info[2] if bpm_info else '施婷杰'

                    instruction_lower = instruction.lower() if instruction else ''
                    is_reject = '拒绝' in instruction or '驳回' in instruction or 'reject' in instruction_lower

                    status_value = "STATUS_REJECTED" if is_reject else "STATUS_APPROVED"
                    reason_value = "Test-Auto-Reject" if is_reject else "Test-Auto-Approve"

                    data_map = {
                        "fileName": file_name,
                        "sceneType": "jdbcInputBatchAddTask",
                        "createdBy": created_by,
                        "batchTaskId": int(task_id) if task_id else 0,
                        "scOwnerUid": "71e8b23d-45e2-497a-b247-f5b807fb4f65",
                        "taskId": int(task_id) if task_id else 0,
                        "recordCnt": 10,
                        "scene": "批量新增任务"
                    }

                    payload_dict = {
                        "startUid": created_uid,
                        "orderNo": order_no,
                        "dataMap": json.dumps(data_map, ensure_ascii=False),
                        "processInstId": bpm_process_id,
                        "operatorUid": "6260e238-93c5-4324-8d0f-e3ba17659a14",
                        "operator": "陈沈伟",
                        "startName": bpm_created_by,
                        "status": status_value
                    }

                    cluster_name = "amqp-cn-4591j61c6009"
                    queue = "dataops.queue.receiveBatchOperationFlow"

                    skill_args = json.dumps({
                        "cluster_name": cluster_name,
                        "queue": queue,
                        "payload_dict": payload_dict,
                        "reason": reason_value
                    }, ensure_ascii=False)

                    print(f"[DEBUG MQ] 构造消息: order_no={order_no}, bpm_process_id={bpm_process_id}")
                    print(f"[DEBUG MQ] status={status_value}, instruction={instruction}")
                    print(f"[DEBUG MQ] payload_dict={payload_dict}")

                    args = ['/usr/local/bin/python3', main_script, skill_args]

                    result = subprocess.run(
                        args,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )

                    if result.returncode == 0:
                        return {
                            'status': 'SUCCESS',
                            'message': f'MQ 消息发送成功: taskId={task_id}',
                            'skill_output': result.stdout,
                            'queue': queue
                        }
                    else:
                        return {
                            'status': 'FAIL',
                            'message': f'Skill 执行失败: {result.stderr}',
                            'skill_output': result.stderr
                        }
                except Exception as e:
                    return {
                        'status': 'FAIL',
                        'message': f'调用 skill 时出错: {str(e)}',
                        'error': str(e)
                    }

        return {
            'status': 'FAIL',
            'message': f'未找到 skill 脚本: {skill_dir}',
            'hint': '请确保 skill 已正确安装'
        }


@action_registry.register_decorator()
class TestCreateJdbcTableAction(ExecutionAction):
    """
    JDBC 测试表生成动作

    桥接到全局 skill: test-create-jdbctable
    功能: 生成 JDBC 测试表
    """

    metadata = ActionMetadata(
        name='test_create_jdbc_table',
        category='skill_bridge',
        description='生成 JDBC 测试表（桥接 test-create-jdbctable skill）',
        parameters=[
            {
                'name': 'table_name',
                'type': 'str',
                'required': True,
                'description': '表名称'
            },
            {
                'name': 'database',
                'type': 'str',
                'required': False,
                'description': '目标数据库'
            },
            {
                'name': 'skill_args',
                'type': 'str',
                'required': False,
                'description': '额外的 skill 参数'
            }
        ],
        returns={
            'status': 'SUCCESS/FAIL',
            'message': '执行结果消息',
            'skill_output': 'skill 执行输出'
        }
    )

    def execute(self, context, **params) -> Dict[str, Any]:
        """执行 test-create-jdbctable skill"""
        import re

        instruction = params.get('instruction', '')
        default_instance = params.get('default_instance', 'cjjcommon')
        default_db = params.get('default_db', '')

        skill_dir = os.path.join(SKILLS_DIR, 'test-table')

        if os.path.exists(skill_dir):
            main_script = os.path.join(skill_dir, 'main.py')
            if not os.path.exists(main_script):
                main_script = os.path.join(skill_dir, 'scripts', 'index.py')

            if os.path.exists(main_script):
                try:
                    import re
                    english_words = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*', instruction)
                    filtered_words = ['test', 'table', 'create', 'instance', 'database', 'db',
                                      'mysql', 'tidb', 'adb', 'jdbc', 'warehouse', 'batch',
                                      'cjjcommon', 'dataops', 'shitingjie', 'bigdata',
                                      default_instance, default_db]
                    tables = [t for t in english_words if t not in filtered_words and len(t) >= 5]

                    if not tables:
                        from datetime import datetime
                        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                        tables = [f'test_table_{timestamp}_1', f'test_table_{timestamp}_2']

                    all_results = []
                    for table_name in tables:
                        args = ['/usr/local/bin/python3', main_script, 'generate',
                                '--tableName', table_name,
                                '--env', default_instance,
                                '--execute']

                        if default_db:
                            args.extend(['--database', default_db])

                        env = os.environ.copy()
                        env['PYTHONUTF8'] = '1'

                        result = subprocess.run(
                            args,
                            capture_output=True,
                            text=True,
                            timeout=120,
                            cwd=os.path.join(skill_dir, 'scripts'),
                            env=env
                        )

                        all_results.append({
                            'table': table_name,
                            'returncode': result.returncode,
                            'stdout': result.stdout,
                            'stderr': result.stderr
                        })

                    failed = [r for r in all_results if r['returncode'] != 0]
                    if failed:
                        return {
                            'status': 'FAIL',
                            'message': f'Skill 执行失败: {failed[0]["stderr"]}',
                            'skill_output': '\n'.join([r['stderr'] for r in failed])
                        }

                    created_tables = [r['table'] for r in all_results]
                    context.set('instance_name', default_instance)
                    context.set('db_name', default_db)
                    context.set('created_tables', created_tables)

                    return {
                        'status': 'SUCCESS',
                        'message': f'JDBC 测试表生成成功: {created_tables}',
                        'skill_output': '\n'.join([r['stdout'] for r in all_results])
                    }
                except Exception as e:
                    return {
                        'status': 'FAIL',
                        'message': f'调用 skill 时出错: {str(e)}',
                        'error': str(e)
                    }

        return {
            'status': 'FAIL',
            'message': f'未找到 skill 脚本: {skill_dir}',
            'hint': '请确保 skill 已正确安装'
        }
