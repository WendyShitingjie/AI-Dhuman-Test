"""
JDBC 批量入仓 API 原语

包含 TKI_003 到 TKI_006 的所有接口调用原语。
用于实现从文件上传校验到任务提交的全链路自动化。
"""
import os
from typing import Any, Dict
import requests
from actions.base import ExecutionAction, ActionMetadata
from config.settings import settings
from urllib.parse import quote
import time
from actions.action_registry import action_registry


def _get_common_params() -> Dict[str, str]:
    """获取通用的身份参数，并进行安全编码"""
    p_n_raw = settings.get('jdbc_ingestion.api.p_n', '施婷杰')
    p_u = settings.get('jdbc_ingestion.api.p_u', '71e8b23d-45e2-497a-b247-f5b807fb4f65')

    # ⭐ 核心修改：在这里直接对中文名进行 URL 编码
    # 这样无论是拼 URL 还是放 Header，都不会再报 latin-1 错误
    return {
        'p_n': quote(p_n_raw),
        'p_u': p_u
    }


def _build_url(path: str) -> str:
    """
    修改前
    构建 API 请求 URL，自动附加身份参数
    base_url = settings.get('jdbc_ingestion.api.base_url')
    common = _get_common_params()
    # 保证 URL 中包含 p_n 和 p_u 以满足某些接口的 Query 参数要求
    return f"{base_url}{path}?p_n={common['p_n']}&p_u={common['p_u']}"
    """
    """构建 API 请求 URL，自动处理中文编码"""
    base_url = settings.get('jdbc_ingestion.api.base_url')
    if not base_url:
        base_url = "http://dataops.apps01.ali-bj-sit03.shuheo.net"

    base_url = base_url.rstrip('/')
    common = _get_common_params()

    # 2. ⭐ 对中文参数进行 URL 编码
    p_n_encoded = quote(common['p_n'])
    p_u = common['p_u']

    # return f"{base_url}{path}?p_n={p_n_encoded}&p_u={p_u}"
    # 直接拼接转换后的参数，不要再用 quote()
    return f"{base_url}{path}?p_n={common['p_n']}&p_u={common['p_u']}"


@action_registry.register_decorator()
class BatchUploadValidateAction(ExecutionAction):
    """
    TKI_003: 批量上传校验接口
    """
    metadata = ActionMetadata(
        name='batch_upload_validate',
        category='api',
        description='上传 Excel 文件并触发后端校验（TKI_003）',
        parameters=[
            {'name': 'fileName', 'type': 'str', 'required': True, 'description': '测试数据文件名'},
            {'name': 'optionType', 'type': 'str', 'required': False, 'description': '操作类型'},
            {'name': 'taskId', 'type': 'int', 'required': False, 'description': '任务ID（修改场景使用）'}
        ],
        returns={
            'status': 'SUCCESS/FAIL',
            'taskId': '生成的任务唯一标识',
            'fileName': '服务端保存的文件名'
        }
    )

    def execute(self, context, **params) -> Dict[str, Any]:
        self.validate_parameters(params)

        url = _build_url('/dataops/etlx/batch/v2/validate')
        common = _get_common_params()

        # --- ⭐ 修改后的路径获取逻辑 ⭐ ---

        # 1. 优先尝试从上下文获取上一步生成的绝对路径
        file_path = context.get('test_file_path')
        print(f"    [DEBUG] context.get('test_file_path') = {file_path}, type = {type(file_path)}")
        print(f"    [DEBUG] params['fileName'] = {params['fileName']}")
        # 2. 如果上下文中没有，或者文件名不匹配，再 fallback 到默认路径
        if not file_path or params['fileName'] not in (file_path or ''):
            project_root = settings.get('project_root', os.getcwd())
            file_path = os.path.join(project_root, 'test_data', params['fileName'])
        print(f"    🚀 调用批量上传校验接口 (TKI_003)")
        print(f"       实际使用文件路径: {file_path}")
        if not os.path.exists(file_path):
            return {'status': 'FAIL', 'message': f'本地测试文件不存在: {file_path}'}
        # 1. 准备文件路径
        # project_root = settings.get('project_root', os.getcwd())
        # file_path = os.path.join(project_root, 'test_data', params['fileName'])

        # if not os.path.exists(file_path):
            # return {'status': 'FAIL', 'message': f'本地测试文件不存在: {file_path}'}

        # 2. 准备请求数据
        data = {
            'optionType': params.get('optionType', 'UPLOAD'),
            'p_n': common['p_n'],
            'p_u': common['p_u']
        }
        if params.get('taskId'):
            data['taskId'] = params['taskId']

        print(f"    🚀 调用批量上传校验接口 (TKI_003)")
        print(f"       待上传文件: {params['fileName']}")

        try:
            # 3. 发送请求
            with open(file_path, 'rb') as f:
                files = {
                    'file': (params['fileName'], f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                }
                headers = {
                    'p_n': quote(common['p_n']),
                    'p_u': common['p_u']
                }

                response = requests.post(url, data=data, files=files, headers=headers, timeout=60)
                result = response.json()

            # 4. 处理响应并存入上下文 (Context)
            if result.get('success') is True:
                resp_data = result.get('data', {})

                # ⭐ 关键修改：从接口响应结果 data 节点中提取信息
                task_id = resp_data.get('taskId')
                server_file_name = resp_data.get('fileName')

                # 存入全链路上下文
                context.set('taskId', task_id)
                context.set('upload_file_name', server_file_name)

                print(f"    ✅ 上传成功：")
                print(f"       [Context] taskId = {task_id}")
                print(f"       [Context] upload_file_name = {server_file_name}")

                return {
                    'status': 'SUCCESS',
                    'taskId': task_id,
                    'fileName': server_file_name,
                    'message': result.get('message', '成功')
                }
            else:
                print(f"    ❌ 上传失败：{result.get('message')}")
                return {'status': 'FAIL', 'message': result.get('message', '接口返回失败')}

        except Exception as e:
            print(f"    ❌ 请求异常: {str(e)}")
            return {'status': 'FAIL', 'message': f'请求异常: {str(e)}'}


@action_registry.register_decorator()
class QueryBatchResultAction(ExecutionAction):
    """
    TKI_004: 查询批量操作校验结果接口
    """
    metadata = ActionMetadata(
        name='query_batch_result',
        category='api',
        description='轮询获取异步校验的结果详情（TKI_004）',
        parameters=[
            {'name': 'taskId', 'type': 'int', 'required': True, 'description': '任务唯一标识'}
        ],
        returns={
            'status': 'SUCCESS/FAIL',
            'message': '业务判定结论'
        }
    )

    def execute(self, context, **params) -> Dict[str, Any]:
        self.validate_parameters(params)
        print(f"    ⏳ 正在等待后端异步校验完成 (强制等待 5s)...")
        time.sleep(5)
        task_id = params['taskId']
        url = _build_url(f'/dataops/etlx/batch/v2/task/{task_id}/result')
        headers = _get_common_params()

        print(f"    🚀 调用查询校验结果接口 (TKI_004)")
        print(f"       查询任务ID: {task_id}")

        try:

            response = requests.get(url, headers=headers, timeout=30)
            result = response.json()

            # 1. 提取基础判定字段
            code = result.get('code')
            success = result.get('success')
            data = result.get('data', {})
            failed_rows = data.get('failedRows', [])
            publish_failed_count = data.get('publishFailedCount', 0)

            # ⭐ 2. 核心逻辑判定（四项必须全部达标）
            is_passed = (
                    code == 0 and  # 响应码为0
                    success is True and  # success标志为true
                    len(failed_rows) == 0 and  # 失败行列表为空
                    publish_failed_count == 0  # 失败计数为0
            )

            # 3. 处理成功与失败的输出
            if is_passed:
                print(f"    ✅ 业务校验完全通过 (无错误记录)")
                return {
                    'status': 'SUCCESS',
                    'message': '校验成功',
                    'data': data
                }
            else:
                # ❌ 校验失败：打印详细的错误摘要
                print(f"    ❌ 业务校验未通过！共发现 {publish_failed_count} 项错误：")

                error_details = []
                # 遍历 failedRows，打印每一张表的失败详情
                for idx, row in enumerate(failed_rows, 1):
                    table_name = row.get('tableName', '未知表名')
                    error_msg = row.get('errorMsg', '未提供错误信息')
                    failure_type = row.get('failureType', 'N/A')

                    # 打印到控制台，方便实时观察
                    detail_line = f"       [{idx}] 表名: {table_name} -> 错误原因: {error_msg} ({failure_type})"
                    print(detail_line)
                    error_details.append(detail_line)

                # 将错误汇总到 message 中返回给执行引擎
                summary_message = f"校验失败({publish_failed_count}个表): " + "; ".join(
                    [f"{r.get('tableName')}:{r.get('errorMsg')}" for r in failed_rows])

                return {
                    'status': 'FAIL',
                    'message': summary_message,
                    'data': data
                }

        except Exception as e:
            print(f"    ❌ 请求异常: {str(e)}")
            return {'status': 'FAIL', 'message': str(e)}


@action_registry.register_decorator()
class SubmitBatchTaskAction(ExecutionAction):
    """
    TKI_005: 提交批量操作任务接口
    """

    metadata = ActionMetadata(
        name='submit_batch_task',
        category='api',
        description='正式提交校验通过的任务，进入BPM审批流（TKI_005）',
        parameters=[
            {
                'name': 'taskId',
                'type': 'int',
                'required': True,
                'description': '任务唯一标识'
            }
        ],
        returns={
            'status': 'SUCCESS/FAIL',
            'message': '响应消息'
        }
    )

    def execute(self, context, **params) -> Dict[str, Any]:
        """提交任务"""
        self.validate_parameters(params)

        task_id = params['taskId']
        url = _build_url(f'/dataops/etlx/batch/v2/submit/{task_id}')
        headers = _get_common_params()

        print(f"    🚀 调用提交批量任务接口 (TKI_005), taskId: {task_id}")

        try:
            # 该接口需要同时在 URL(Query) 和 Header 中传参，_build_url 已处理 Query 部分
            response = requests.post(url, headers=headers, timeout=30)
            result = response.json()

            if result.get('code') == 0 and result.get('data') == "提交成功":
                print(f"    ✅ 任务提交成功，进入待审批状态")
                # 提示：下一步通常需要使用 mq-sender 发送审批信号
                return {'status': 'SUCCESS', 'message': '提交成功'}
            else:
                return {'status': 'FAIL', 'message': result.get('message', '提交失败')}
        except Exception as e:
            return {'status': 'FAIL', 'message': str(e)}


@action_registry.register_decorator()
class CancelBatchTaskAction(ExecutionAction):
    """
    TKI_006: 取消批量操作任务接口
    """

    metadata = ActionMetadata(
        name='cancel_batch_task',
        category='api',
        description='撤回或清理未发布的批量任务记录（TKI_006）',
        parameters=[
            {
                'name': 'taskId',
                'type': 'int',
                'required': True,
                'description': '任务唯一标识'
            }
        ],
        returns={
            'status': 'SUCCESS/FAIL',
            'data': '取消结果(True/False)'
        }
    )

    def execute(self, context, **params) -> Dict[str, Any]:
        """取消任务"""
        self.validate_parameters(params)

        task_id = params['taskId']
        base_url = settings.get('jdbc_ingestion.api.base_url')
        if not base_url:
            base_url = "http://dataops.apps01.ali-bj-sit03.shuheo.net"
        common = _get_common_params()
        url = f"{base_url}/dataops/etlx/batch/v2/task/cancel?taskId={task_id}&p_n={common['p_n']}&p_u={common['p_u']}"
        headers = _get_common_params()

        print(f"    🚀 调用取消批量任务接口 (TKI_006), taskId: {task_id}")

        try:
            response = requests.post(url, headers=headers, timeout=30)
            result = response.json()

            if result.get('success') is True and result.get('data') is True:
                print(f"    ✅ 任务已成功取消并清理")
                return {'status': 'SUCCESS', 'data': True}
            else:
                return {'status': 'FAIL', 'data': False, 'message': result.get('message')}
        except Exception as e:
            return {'status': 'FAIL', 'message': str(e)}