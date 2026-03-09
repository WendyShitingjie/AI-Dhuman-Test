"""
批量执行脚本：批量处理多个表的元数据完整性管理

使用场景：
- 需要对同一数据库下的多个表执行元数据管理
- 需要对多个数据库的多个表执行元数据管理

使用方法：
1. 在 TABLE_LIST 中配置要处理的表信息
2. 根据需要调整 EXIST_UPDATE 和 EXIST_DELETE（默认：True 和 False）
3. 运行脚本

注意：
- p_n 和 p_u 已固定为"施婷杰"和对应的 UUID
- 默认 existUpdate=True, existDelete=False
- 如果需要支持删除操作，将 EXIST_DELETE 改为 True
"""

import sys
import os
from typing import List, Dict, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from metadata_complete import MetadataCompleteManager


def batch_process():
    """批量处理多个表的元数据完整性管理"""

    # ==================== 配置区 ====================

    # 人员信息（所有表使用相同的人员信息）
    P_N = "施婷杰"
    P_U = "71e8b23d-45e2-497a-b247-f5b807fb4f65"

    # 操作设置（默认值：更新=True，删除=False）
    # 如需支持删除操作，将 EXIST_DELETE 改为 True
    EXIST_UPDATE = True
    EXIST_DELETE = False

    # 表列表：每个元素是一个元组 (instance, database, table)
    TABLE_LIST = [
        ("cjjcommon", "dataops_shitingjie", "0418bugfuxianccc"),
        # 添加更多表
        # ("cjjcommon", "dataops_shitingjie", "table2"),
        # ("cjjcommon", "another_database", "table3"),
    ]

    # ================================================

    print("="*70)
    print("批量执行：元数据完整性管理")
    print(f"总共 {len(TABLE_LIST)} 个表待处理")
    print("="*70)
    print()

    # 创建管理器
    manager = MetadataCompleteManager()

    # 记录结果
    success_count = 0
    fail_count = 0
    results: List[Tuple[str, str, str, bool]] = []

    # 逐个处理
    for idx, (instance, database, table) in enumerate(TABLE_LIST, 1):
        print(f"\n{'='*70}")
        print(f"处理进度: {idx}/{len(TABLE_LIST)}")
        print(f"{'='*70}")

        success = manager.complete_metadata(
            instance=instance,
            database=database,
            table=table,
            p_n=P_N,
            p_u=P_U,
            exist_update=EXIST_UPDATE,
            exist_delete=EXIST_DELETE
        )

        results.append((instance, database, table, success))

        if success:
            success_count += 1
        else:
            fail_count += 1

    # 打印汇总报告
    print("\n" + "="*70)
    print("批量处理完成 - 汇总报告")
    print("="*70)
    print(f"总计: {len(TABLE_LIST)} 个表")
    print(f"成功: {success_count} 个")
    print(f"失败: {fail_count} 个")
    print("-"*70)

    # 打印详细结果
    print("详细结果：")
    for instance, database, table, success in results:
        status = "✓ 成功" if success else "✗ 失败"
        print(f"  {status}  {instance}.{database}.{table}")

    print("="*70)

    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    exit_code = batch_process()
    sys.exit(exit_code)
