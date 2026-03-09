#!/usr/bin/env python3
"""
设置 MySQL 表的敏感字段
为指定字段添加 sensitive: true 和 sensitiveType

使用说明：
1. 修改脚本底部的配置参数（instance, database, table）
2. 在 sensitive_fields_config 字典中配置敏感字段
   格式：{'字段名': 'sensitiveType值'}
3. 当 sensitiveType 不明确或系统不支持特定类型时，统一使用 "OtherType_Sensitive"
4. 运行脚本：python set_sensitive_fields.py

示例：
    sensitive_fields_config = {
        'email': 'Customer_Email',
        'phone': 'OtherType_Sensitive',    # 不明确时使用默认值
        'id_card': 'OtherType_Sensitive'   # 不明确时使用默认值
    }
"""

import sys
import os

# 添加 metadata-complete 脚本路径
sys.path.insert(0, '/cc_free_coder/skills/metadata-complete/scripts')

from metadata_complete import MetadataCompleteManager


def set_sensitive_fields(instance, database, table, sensitive_fields_config):
    """
    设置表的敏感字段

    Args:
        instance: MySQL 实例标识
        database: 数据库名称
        table: 表名
        sensitive_fields_config: 敏感字段配置字典
            格式: {
                '字段名': 'sensitiveType值',
                'email': 'Customer_Email',
                'password': 'Password'
            }
    """
    # 固定的人员信息
    p_n = "施婷杰"
    p_u = "71e8b23d-45e2-497a-b247-f5b807fb4f65"

    # 初始化管理器
    manager = MetadataCompleteManager()

    print('=' * 70)
    print('设置敏感字段')
    print('=' * 70)
    print(f'实例: {instance}')
    print(f'数据库: {database}')
    print(f'表: {table}')
    print(f'敏感字段: {list(sensitive_fields_config.keys())}')
    print('=' * 70)
    print()

    # 步骤1：获取元数据
    print('[步骤1] 获取表元数据...')
    metadata = manager.get_metadata(instance, database, table, p_n, p_u)
    if not metadata:
        print('[错误] 获取元数据失败')
        return False

    table_name = metadata.get('tableName')
    column_metadata = metadata.get('columnMetadata', [])
    print(f'✓ ��功获取，共 {len(column_metadata)} 个字段')
    print('-' * 70)

    # 步骤2：处理字段元数据
    print('[步骤2] 处理字段元数据，设置敏感字段...')

    sensitive_count = 0
    for column in column_metadata:
        col_name = column.get('columnName', '')

        # 补充固定字段
        if 'canNotBeModified' not in column:
            column['canNotBeModified'] = False
        if 'columnEditing' not in column:
            column['columnEditing'] = False
        if 'json' not in column:
            column['json'] = False
        if 'enumerated' not in column:
            column['enumerated'] = False

        # 设置敏感字段标识
        if col_name in sensitive_fields_config:
            column['sensitive'] = True
            column['sensitiveType'] = sensitive_fields_config[col_name]
            sensitive_count += 1
            print(f'  ✓ {col_name}')
            print(f'      sensitive: true')
            print(f'      sensitiveType: "{column["sensitiveType"]}"')
        else:
            column['sensitive'] = False
            # 移除 sensitiveType 字段（如果存在）
            if 'sensitiveType' in column:
                del column['sensitiveType']

    print(f'\n✓ 已设置 {sensitive_count} 个敏感字段')
    print('-' * 70)

    # 步骤3：提交元数据管理
    print('[步骤3] 提交元数据管理到服务器...')
    success = manager.manage_metadata(
        instance=instance,
        database=database,
        p_n=p_n,
        p_u=p_u,
        table_name=table_name,
        exist_update=True,
        exist_delete=True,
        column_metadata=column_metadata
    )

    print('=' * 70)
    if success:
        print('✓ 敏感字段设置请求已发送')
        print()
        print('请验证设置是否生效：')
        for field_name, sensitive_type in sensitive_fields_config.items():
            print(f'  - {field_name}: sensitive=true, sensitiveType="{sensitive_type}"')
    else:
        print('✗ 敏感字段设置失败')
    print('=' * 70)

    return success


if __name__ == '__main__':
    # 配置参数
    instance = 'cjjcommon'
    database = 'dataops_shitingjie'
    table = '0418bugfuxianddd'

    # 敏感字段配置
    # 注意：sensitiveType 不明确或系统不支持特定类型时，统一使用 "OtherType_Sensitive"
    sensitive_fields_config = {
        'email': 'Customer_Email',  # 客户邮箱
        'password': 'OtherType_Sensitive',  # 密码（使用 OtherType_Sensitive 作为默认类型）
    }

    # 执行设置
    success = set_sensitive_fields(
        instance=instance,
        database=database,
        table=table,
        sensitive_fields_config=sensitive_fields_config
    )

    sys.exit(0 if success else 1)
