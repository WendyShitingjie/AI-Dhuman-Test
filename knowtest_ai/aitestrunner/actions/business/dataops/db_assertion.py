"""
数据库断言动作 - 简化版本

提供 assert_field_equals 等简化版数据库断言动作。
"""
from typing import Any, Dict
from actions.base import ExecutionAction, ActionMetadata
from actions.action_registry import action_registry


@action_registry.register_decorator()
class AssertFieldEqualsAction(ExecutionAction):
    """数据库字段断言动作 - 简化版本"""

    metadata = ActionMetadata(
        name='assert_field_equals',
        category='assertion',
        description='断言数据库指定记录的字段等于期望值（简化版断言）',
        parameters=[
            {'name': 'table', 'type': 'str', 'required': True, 'description': '表名（支持 database.table 格式）'},
            {'name': 'field', 'type': 'str', 'required': True, 'description': '字段名'},
            {'name': 'where', 'type': 'str', 'required': True, 'description': 'WHERE 条件'},
            {'name': 'expected', 'type': 'any', 'required': True, 'description': '期望值'}
        ],
        returns={
            'status': 'PASS/FAIL',
            'reason': '结果描述',
            'actual_value': '实际值'
        }
    )

    def execute(self, context, **params) -> Dict[str, Any]:
        self.validate_parameters(params)

        table = params['table']
        field = params['field']
        where = params['where']
        expected = params['expected']

        if '.' in table:
            database, table = table.split('.', 1)
        else:
            from config.settings import settings
            database = settings.get('jdbc_ingestion.database', 'dataops')

        sql = f"SELECT {field} FROM {database}.{table} WHERE {where} LIMIT 1"

        try:
            import pymysql
            from config.settings import settings

            db_config = {
                'host': settings.get('database.dataops.host', 'bigdata-biz.db.ali-bj-bdsit01.shuheo.net'),
                'port': int(settings.get('database.dataops.port', 3306)),
                'user': settings.get('database.dataops.user', 'bdsit_user_0e0bc33'),
                'password': settings.get('database.dataops.password', 'bdsit_user_0e0bc33_26587a'),
                'database': database,
                'charset': 'utf8mb4'
            }

            conn = pymysql.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute(sql)
            result = cursor.fetchone()
            cursor.close()
            conn.close()

            if result is None:
                return {
                    'status': 'FAIL',
                    'reason': f'未找到匹配的记录: {where}',
                    'actual_value': None
                }

            actual_value = result[0]
            actual_str = str(actual_value)
            expected_str = str(expected)

            if actual_str == expected_str:
                return {
                    'status': 'PASS',
                    'reason': f'字段 {field} 值匹配: {actual_value}',
                    'actual_value': actual_value
                }
            else:
                return {
                    'status': 'FAIL',
                    'reason': f'字段 {field} 值不匹配: 期望 {expected_str}, 实际 {actual_str}',
                    'actual_value': actual_value
                }

        except Exception as e:
            return {
                'status': 'FAIL',
                'reason': f'数据库查询失败: {str(e)}',
                'actual_value': None
            }


@action_registry.register_decorator()
class AssertRecordCountAction(ExecutionAction):
    """数据库记录数量断言动作"""

    metadata = ActionMetadata(
        name='assert_record_count',
        category='assertion',
        description='断言数据库查询的记录数量等于期望值',
        parameters=[
            {'name': 'table', 'type': 'str', 'required': True, 'description': '表名（支持 database.table 格式）'},
            {'name': 'where', 'type': 'str', 'required': True, 'description': 'WHERE 条件'},
            {'name': 'expected', 'type': 'int', 'required': True, 'description': '期望记录数'}
        ],
        returns={
            'status': 'PASS/FAIL',
            'reason': '结果描述',
            'actual_count': '实际记录数'
        }
    )

    def execute(self, context, **params) -> Dict[str, Any]:
        self.validate_parameters(params)

        table = params['table']
        where = params['where']
        expected = params['expected']

        if '.' in table:
            database, table = table.split('.', 1)
        else:
            from config.settings import settings
            database = settings.get('jdbc_ingestion.database', 'dataops')

        sql = f"SELECT COUNT(*) FROM {database}.{table} WHERE {where}"

        try:
            import pymysql
            from config.settings import settings

            db_config = {
                'host': settings.get('database.dataops.host', 'bigdata-biz.db.ali-bj-bdsit01.shuheo.net'),
                'port': int(settings.get('database.dataops.port', 3306)),
                'user': settings.get('database.dataops.user', 'bdsit_user_0e0bc33'),
                'password': settings.get('database.dataops.password', 'bdsit_user_0e0bc33_26587a'),
                'database': database,
                'charset': 'utf8mb4'
            }

            conn = pymysql.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute(sql)
            result = cursor.fetchone()
            cursor.close()
            conn.close()

            actual_count = result[0] if result else 0

            if actual_count == expected:
                return {
                    'status': 'PASS',
                    'reason': f'记录数匹配: {actual_count}',
                    'actual_count': actual_count
                }
            else:
                return {
                    'status': 'FAIL',
                    'reason': f'记录数不匹配: 期望 {expected}, 实际 {actual_count}',
                    'actual_count': actual_count
                }

        except Exception as e:
            return {
                'status': 'FAIL',
                'reason': f'数据库查询失败: {str(e)}',
                'actual_count': None
            }


@action_registry.register_decorator()
class AssertDatabaseRecordAction(ExecutionAction):
    """数据库多表关联断言动作 - 支持 JOIN 查询"""

    metadata = ActionMetadata(
        name='assert_database_record',
        category='assertion',
        description='断言数据库多表关联查询的字段等于期望值',
        parameters=[
            {'name': 'table', 'type': 'str', 'required': True, 'description': '表名（支持多表 JOIN 格式）'},
            {'name': 'field', 'type': 'str', 'required': True, 'description': '字段名（支持别名.字段格式，如 ds.status）'},
            {'name': 'where', 'type': 'str', 'required': True, 'description': 'WHERE 条件'},
            {'name': 'expected', 'type': 'any', 'required': True, 'description': '期望值'}
        ],
        returns={
            'status': 'PASS/FAIL',
            'reason': '结果描述',
            'actual_value': '实际值'
        }
    )

    def execute(self, context, **params) -> Dict[str, Any]:
        self.validate_parameters(params)

        table = params['table']
        field = params['field']
        where = params['where']
        expected = params['expected']

        table_sql = table.strip()
        if '\n' in table_sql:
            table_sql = ' '.join(table_sql.split())

        sql = f"SELECT {field} FROM {table_sql} WHERE {where} LIMIT 1"

        try:
            import pymysql
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
            cursor.execute(sql)
            result = cursor.fetchone()
            cursor.close()
            conn.close()

            if result is None:
                return {
                    'status': 'FAIL',
                    'reason': f'未找到匹配的记录: {where}',
                    'actual_value': None
                }

            actual_value = result[0]
            actual_str = str(actual_value)
            expected_str = str(expected)

            if actual_str == expected_str:
                return {
                    'status': 'PASS',
                    'reason': f'字段 {field} 值匹配: {actual_value}',
                    'actual_value': actual_value
                }
            else:
                return {
                    'status': 'FAIL',
                    'reason': f'字段 {field} 值不匹配: 期望 {expected_str}, 实际 {actual_str}',
                    'actual_value': actual_value
                }

        except Exception as e:
            return {
                'status': 'FAIL',
                'reason': f'数据库查询失败: {str(e)}',
                'actual_value': None
            }
