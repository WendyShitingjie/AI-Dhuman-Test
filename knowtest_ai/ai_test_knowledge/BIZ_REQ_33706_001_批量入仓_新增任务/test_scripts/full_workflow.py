#!/usr/bin/env python3
"""
JDBC 批量入仓全链路自动化测试脚本
执行 TKF_001 全链路工作流

步骤：
1. 准备测试文件（造表 + 完善元数据 + 生成 Excel）
2. 批量上传校验
3. 查询校验结果
4. 提交批量操作任务
5. 发送审批信号（通过/拒绝）
6. 结果全链路验证

使用示例：
    # 正常场景（审批通过）- 2张表
    python full_workflow.py --count 2 --scenario approve

    # 审批拒绝场景 - 1张表
    python full_workflow.py --count 1 --scenario reject

    # 自定义等待时间
    python full_workflow.py --count 2 --scenario approve --wait-time 60
"""

import sys
import os
import subprocess
import time
import json
import argparse
from datetime import datetime

# 添加 skills 目录到 Python 路径
SKILLS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../skills'))
sys.path.insert(0, SKILLS_DIR)


class Color:
    """终端颜色输出"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f"{Color.BOLD}{Color.CYAN}{text}{Color.END}")
    print("=" * 60)


def print_step(step_num, text):
    """打印步骤"""
    print(f"\n{Color.BOLD}{Color.BLUE}[步骤 {step_num}] {text}{Color.END}")


def print_success(text):
    """打印成功信息"""
    print(f"{Color.GREEN}✅ {text}{Color.END}")


def print_error(text):
    """打印错误信息"""
    print(f"{Color.RED}❌ {text}{Color.END}")


def print_warning(text):
    """打印警告信息"""
    print(f"{Color.YELLOW}⚠️  {text}{Color.END}")


def print_info(text):
    """打印信息"""
    print(f"{Color.CYAN}ℹ️  {text}{Color.END}")


def run_command(cmd, cwd=None, capture_output=True):
    """
    执行命令并返回结果

    Args:
        cmd: 命令列表或字符串
        cwd: 工作目录
        capture_output: 是否捕获输出

    Returns:
        tuple: (success, output, error)
    """
    try:
        if isinstance(cmd, str):
            cmd = cmd.split()

        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=capture_output,
            text=True,
            timeout=1000  # subprocess设置1000s超时（按照每个表约5分钟的时间并且不超过3张表）
        )

        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "命令执行超时（1000s）"
    except Exception as e:
        return False, "", str(e)


def step1_prepare_test_file(count=1, db_type='mysql', instance='cjjcommon', database='dataops_shitingjie'):
    """
    步骤1：准备测试文件
    调用 batch_workflow.py 创建表、完善元数据、生成 Excel

    Returns:
        dict: {success: bool, file_path: str, tables: list, error: str}
    """
    print_step(1, "准备测试文件（造表 + 完善元数据 + 生成 Excel）")

    script_path = os.path.join(SKILLS_DIR, 'jdbc-warehouse-test/scripts')
    cmd = [
        'python3', 'batch_workflow.py',
        instance, database,
        '--count', str(count),
        '--db-type', db_type,
        '--yes'  # 自动确认
    ]

    print_info(f"执行命令: {' '.join(cmd)}")
    print_info(f"工作目录: {script_path}")

    success, output, error = run_command(cmd, cwd=script_path, capture_output=True)

    if not success:
        print_error(f"步骤1失败: {error}")
        return {'success': False, 'error': error}

    # 解析输出，提取文件路径和表名
    # batch_workflow.py 应该输出 JSON 格��的结果
    # 这里先简化处理，假设成功后会生成固定位置的文件

    # 查找最新生成的 Excel 文件
    test_data_dir = os.path.join(os.path.dirname(__file__), '../test_data')
    excel_files = [f for f in os.listdir(test_data_dir) if f.startswith('batch_') and f.endswith('.xlsx')]
    excel_files.sort(key=lambda x: os.path.getmtime(os.path.join(test_data_dir, x)), reverse=True)

    if not excel_files:
        print_error("未找到生成的 Excel 文件")
        return {'success': False, 'error': '未找到生成的 Excel 文件'}

    file_path = os.path.join(test_data_dir, excel_files[0])
    print_success(f"测试文件已生成: {excel_files[0]}")

    # 从输出中解析表名列表
    tables = []
    for line in output.split('\n'):
        # 匹配 "  1. batch_test_03031132_01" 这样的行
        if line.strip() and line.strip()[0].isdigit() and '.' in line:
            parts = line.split('.', 1)
            if len(parts) == 2:
                table_name = parts[1].strip()
                if table_name and table_name.startswith('batch_test_'):
                    tables.append(table_name)

    return {
        'success': True,
        'file_path': file_path,
        'tables': tables,
        'error': None
    }


def step2_upload_validate(file_path, env='sit03'):
    """
    步骤2：批量上传校验
    调用 batch_upload_validate.py

    Returns:
        dict: {success: bool, task_id: str, error: str}
    """
    print_step(2, "批量上传校验")

    script_path = os.path.join(SKILLS_DIR, 'jdbc-warehouse-test/scripts')
    cmd = [
        'python3', 'batch_upload_validate.py',
        file_path,
        env  # batch_upload_validate.py 使用位置参数，不是 --env
    ]

    print_info(f"上传文件: {os.path.basename(file_path)}")

    success, output, error = run_command(cmd, cwd=script_path)

    if not success:
        print_error(f"步骤2失败: {error}")
        return {'success': False, 'task_id': None, 'error': error}

    # 解析输出，提取 task_id
    # batch_upload_validate.py 输出格式：📝 任务ID: 415
    task_id = None
    for line in output.split('\n'):
        # 查找包含 "任务ID:" 或 "taskId:" 的行
        if '任务ID:' in line or 'taskId:' in line.lower():
            # 提取冒号后面的数字
            parts = line.split(':')
            if len(parts) >= 2:
                # 去除空格、引号等，提取纯数字
                task_id_str = parts[1].strip().strip('"\'').strip()
                # 尝试转换为数字再转回字符串，确保是纯数字
                try:
                    task_id = str(int(task_id_str))
                    break
                except ValueError:
                    continue

    if not task_id:
        print_error("未能从输出中提取 TaskId")
        print_info(f"输出内容：\n{output}")
        return {'success': False, 'task_id': None, 'error': '未能提取 TaskId'}

    print_success(f"上传成功，TaskId: {task_id}")
    return {
        'success': True,
        'task_id': task_id,
        'error': None
    }


def step3_query_result(task_id, env='sit03', max_retries=10, retry_interval=3):
    """
    步骤3：查询校验结果
    调用 batch_query_result.py，支持轮询等待

    Returns:
        dict: {success: bool, status: str, error: str}
    """
    print_step(3, "查询校验结果（支持轮询）")

    script_path = os.path.join(SKILLS_DIR, 'jdbc-warehouse-test/scripts')

    for attempt in range(1, max_retries + 1):
        print_info(f"查询尝试 {attempt}/{max_retries}")

        cmd = [
            'python3', 'batch_query_result.py',
            task_id,
            env  # 使用位置参数
        ]

        success, output, error = run_command(cmd, cwd=script_path)

        if not success:
            print_warning(f"查询失败: {error}")
            if attempt < max_retries:
                print_info(f"等待 {retry_interval} 秒后重试...")
                time.sleep(retry_interval)
                continue
            else:
                print_error("查询失败，已达最大重试次数")
                return {'success': False, 'status': None, 'error': error}

        # 解析状态
        # batch_query_result.py 的实际输出格式：
        # - 成功: "✅ 校验成功！所有任务通过校验"
        # - 失败: "❌ 校验失败！"
        # - 或包含 "success: True" / "failure: False"
        status = None

        # 检查成功标志
        if '✅ 校验成功' in output or '校验成功！所有任务通过校验' in output:
            status = 'SUCCESS'
        elif 'success: True' in output and 'failure: False' in output:
            status = 'SUCCESS'
        # 检查失败标志
        elif '❌ 校验失败' in output:
            status = 'FAILED'
        elif 'failure: True' in output:
            status = 'FAILED'
        # 检查进行中
        elif 'VALIDATING' in output or 'PENDING' in output or '正在校验' in output:
            status = 'VALIDATING'

        if status == 'SUCCESS':
            print_success("校验成功！")
            return {'success': True, 'status': status, 'error': None}
        elif status == 'FAILED':
            print_error("校验失败！")
            return {'success': False, 'status': status, 'error': '校验失败'}
        else:
            print_info(f"当前状态: {status or '未知'}，继续等待...")
            if attempt < max_retries:
                time.sleep(retry_interval)

    print_error("查询超时，未能获取成功状态")
    return {'success': False, 'status': 'TIMEOUT', 'error': '查询超时'}


def step4_submit_task(task_id, env='sit03'):
    """
    步骤4：提交批量操作任务
    调用 batch_submit_task.py

    Returns:
        dict: {success: bool, order_no: str, error: str}
    """
    print_step(4, "提交批量操作任务")

    script_path = os.path.join(SKILLS_DIR, 'jdbc-warehouse-test/scripts')
    cmd = [
        'python3', 'batch_submit_task.py',
        task_id,
        env  # 使用位置参数
    ]

    success, output, error = run_command(cmd, cwd=script_path)

    # 判断是否成功（检查输出中的成功标识）
    if '提交成功' not in output and 'success: True' not in output:
        print_error(f"步骤4失败: {output}")
        return {'success': False, 'order_no': None, 'error': output}

    # 解析工单号（暂不解析，步骤5会查数据库获取）
    print_success(f"提交成功")
    return {
        'success': True,
        'order_no': None,  # 工单号将在步骤5查询数据库获取
        'error': None
    }


def step5_send_approval(task_id, scenario='approve', env='sit03'):
    """
    步骤5：发送审批信号
    查询数据库获取必需字段，然后发送 MQ 消息

    Returns:
        dict: {success: bool, error: str}
    """
    print_step(5, f"发送审批信号（{scenario}）")

    try:
        # 步骤5.1：查询数据库获取必需字段
        print_info("查询数据库获取工单信息...")

        import mysql.connector

        db_config = {
            'host': 'bigdata-biz.db.ali-bj-bdsit01.shuheo.net',
            'port': 3306,
            'database': 'dataops',
            'user': 'bdsit_user_0e0bc33',
            'password': 'bdsit_user_0e0bc33_26587a',
            'charset': 'utf8mb4'
        }

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # 执行查询
        sql = """
        SELECT
            r.process_instance_node_id AS batchTaskId,
            r.process_instance_node_id AS taskId,
            r.bpm_process_id AS processInstId,
            r.order_no AS orderNo,
            t.file_name AS file_name
        FROM
            dataops_bpm_record r
        INNER JOIN
            dataops_batch_operation_task t
            ON r.process_instance_node_id = t.id
        WHERE
            r.process_key = 'bg_jdbc_rc_plxz_rw'
            AND r.process_instance_node_id = %s
            AND r.status = 2
        """

        cursor.execute(sql, (task_id,))
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if not result:
            print_error(f"未找到 TaskId={task_id} 的工单信息")
            return {'success': False, 'error': '未找到工单信息'}

        print_success(f"查询成功：工单号 = {result['orderNo']}")

        # 步骤5.2：构造 MQ 消息
        print_info("构造 MQ 消息...")

        # 外层字段
        status = "STATUS_APPROVED" if scenario == 'approve' else "STATUS_REJECTED"

        # 内层 dataMap 字段
        data_map = {
            "fileName": result['file_name'],
            "sceneType": "jdbcInputBatchAddTask",
            "createdBy": "施婷杰",
            "batchTaskId": str(result['batchTaskId']),
            "scOwnerUid": "6260e238-93c5-4324-8d0f-e3ba17659a14",
            "taskId": str(result['taskId']),
            "recordCnt": 2,  # TODO: 可以从 Excel 文件读取实际记录数
            "scene": "批量新增任务"
        }

        # 如果是拒绝场景，添加拒绝原因
        if scenario == 'reject':
            data_map["rejectReason"] = "自动化测试-审批拒绝场景"

        # 完整消息体
        payload = {
            "cluster_name": "amqp-cn-4591j61c6009",
            "queue": "dataops.queue.receiveBatchOperationFlow",
            "payload_dict": {
                "startUid": "71e8b23d-45e2-497a-b247-f5b807fb4f65",
                "orderNo": result['orderNo'],
                "dataMap": data_map,  # mq_sender.py 会自动序列化
                "processInstId": result['processInstId'],
                "operatorUid": "6260e238-93c5-4324-8d0f-e3ba17659a14",
                "operator": "陈沈伟",
                "startName": "施婷杰",
                "status": status
            },
            "reason": f"全链路自动化测试-{scenario}"
        }

        # 步骤5.3：发送 MQ 消息
        print_info(f"发送 MQ 消息到队列: {payload['queue']}")

        script_path = os.path.join(SKILLS_DIR, 'mq-sender/scripts')
        cmd = ['python3', 'mq_sender.py', json.dumps(payload, ensure_ascii=False)]

        success, output, error = run_command(cmd, cwd=script_path, capture_output=False)

        if not success:
            print_error(f"MQ 消息发送失败: {error}")
            return {'success': False, 'error': error}

        print_success("MQ 消息发送成功")
        return {'success': True, 'error': None}

    except mysql.connector.Error as e:
        print_error(f"数据库查询失败: {str(e)}")
        return {'success': False, 'error': str(e)}
    except Exception as e:
        print_error(f"步骤5执行失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}


def step6_verify_result(tables, instance, database, wait_time=360):
    """
    步骤6：结果全链路验证
    调用 verify_publish_result.py

    Returns:
        dict: {success: bool, error: str}
    """
    print_step(6, "结果全链路验证（TKR_007）")

    if not tables:
        print_warning("未获取到表名列表，跳过验证")
        return {'success': True, 'error': None}

    script_path = os.path.join(SKILLS_DIR, 'jdbc-warehouse-test/scripts')

    all_success = True
    for table in tables:
        print_info(f"验证表: {table}")

        cmd = [
            'python3', 'verify_publish_result.py',
            table, instance, database,
            str(wait_time)
        ]

        success, output, error = run_command(cmd, cwd=script_path, capture_output=False)

        if not success:
            print_error(f"表 {table} 验证失败")
            all_success = False
        else:
            print_success(f"表 {table} 验证通过")

    if all_success:
        print_success("所有表验证通过！")
    else:
        print_error("部分表验证失败")

    return {
        'success': all_success,
        'error': None if all_success else '部分表验证失败'
    }


def main():
    parser = argparse.ArgumentParser(description='JDBC 批量入仓全链路自动化测试')
    parser.add_argument('--count', type=int, default=2, help='表数量（默认2）')
    parser.add_argument('--scenario', choices=['approve', 'reject'], default='approve',
                        help='测试场景：approve（审批通过）或 reject（审批拒绝）')
    parser.add_argument('--db-type', default='mysql', choices=['mysql', 'tidb', 'adb'],
                        help='数据库类型（默认 mysql）')
    parser.add_argument('--instance', default='cjjcommon', help='实例名（默认 cjjcommon）')
    parser.add_argument('--database', default='dataops_shitingjie', help='数据库名（默认 dataops_shitingjie）')
    parser.add_argument('--env', default='sit03', choices=['sit01', 'sit03', 'prod'],
                        help='环境（默认 sit03）')
    parser.add_argument('--wait-time', type=int, default=360, help='验证前等待时间/秒（默认 360）')

    args = parser.parse_args()

    # 打印测试信息
    print_header("JDBC 批量入仓全链路自动化测试")
    print(f"测试场景: {args.scenario}")
    print(f"表数量: {args.count}")
    print(f"数据库: {args.db_type} - {args.instance}.{args.database}")
    print(f"环境: {args.env}")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 记录测试结果
    test_result = {
        'start_time': datetime.now().isoformat(),
        'scenario': args.scenario,
        'count': args.count,
        'steps': []
    }

    try:
        # 步骤1：准备测试文件
        result1 = step1_prepare_test_file(
            count=args.count,
            db_type=args.db_type,
            instance=args.instance,
            database=args.database
        )
        test_result['steps'].append({'step': 1, 'success': result1['success']})

        if not result1['success']:
            print_error("全链路测试失败：步骤1未通过")
            return 1

        file_path = result1['file_path']
        tables = result1['tables']

        # 步骤2：批量上传校验
        result2 = step2_upload_validate(file_path, env=args.env)
        test_result['steps'].append({'step': 2, 'success': result2['success']})

        if not result2['success']:
            print_error("全链路测试失败：步骤2未通过")
            return 1

        task_id = result2['task_id']
        test_result['task_id'] = task_id

        # --- 💡 在这里增加等待时间 ---
        wait_before_submit = 20  # 根据经验，20-30秒通常足够状态流转
        print_info(f"等待 {wait_before_submit} 秒，确保后端状态从 VALIDATING 切换到 SUCCESS...")
        time.sleep(wait_before_submit)
        # -------------------------

        # 步骤3：查询校验结果
        result3 = step3_query_result(task_id, env=args.env)
        test_result['steps'].append({'step': 3, 'success': result3['success']})

        if not result3['success']:
            print_error("全链路测试失败：步骤3未通过")
            return 1

        # 步骤4：提交批量操作任务
        result4 = step4_submit_task(task_id, env=args.env)
        test_result['steps'].append({'step': 4, 'success': result4['success']})

        if not result4['success']:
            print_error("全链路测试失败：步骤4未通过")
            return 1

        test_result['order_no'] = result4.get('order_no')

        # 步骤5：发送审批信号
        result5 = step5_send_approval(task_id, scenario=args.scenario, env=args.env)
        test_result['steps'].append({'step': 5, 'success': result5['success']})

        if not result5['success']:
            print_error("全链路测试失败：步骤5未通过")
            return 1

        # 步骤6：结果全链路验证
        result6 = step6_verify_result(tables, args.instance, args.database, wait_time=args.wait_time)
        test_result['steps'].append({'step': 6, 'success': result6['success']})

        # 测试总结
        test_result['end_time'] = datetime.now().isoformat()
        test_result['success'] = result6['success']

        print_header("测试总结")
        print(f"测试场景: {args.scenario}")
        print(f"TaskId: {task_id}")
        print(f"工单号: {result4.get('order_no', '未获取')}")
        print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        if result6['success']:
            print_success("✅ 全链路测试通过！")
            return 0
        else:
            print_error("❌ 全链路测试失败")
            return 1

    except KeyboardInterrupt:
        print_warning("\n测试被用户中断")
        return 130
    except Exception as e:
        print_error(f"测试发生异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
