---
component_id: TKD_001
component_name: "批量操作作业表"
component_type: "MySQL"
database: "dataops"
table_name: "dataops.dataops_batch_operation_task"
business_module: "BIZ_JDBC批量入仓"
version: v1.0
created_date: 2026-02-21
---
# 批量操作作业表

## 基础信息

| 属性   | 值                                    |
|------|--------------------------------------|
| 数据库  | dataops                              |
| 表名   | dataops_batch_operation_task         |
| 完整表名 | dataops.dataops_batch_operation_task |

## 1. 表结构

```sql
CREATE TABLE `dataops_batch_operation_task` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '作业ID',
  `task_type` varchar(50) NOT NULL COMMENT '作业类型：BATCH_ADD_TASK、BATCH_ADD_FIELD、BATCH_MODIFY_TASK、BATCH_OFFLINE_TASK',
  `task_status` varchar(50) NOT NULL COMMENT '任务状态：PENDING、VALIDATING、VALIDATE_SUCCESS、VALIDATE_FAILED、PENDING_APPROVAL、EXECUTING、SUCCESS、FAILED',
  `file_name` varchar(255) DEFAULT NULL COMMENT '文件名称',
  `total_count` int(11) DEFAULT '0' COMMENT '文件总行数',
  `success_count` int(11) DEFAULT '0' COMMENT '成功数量',
  `failed_count` int(11) DEFAULT '0' COMMENT '失败数量',
  `error_message` text COMMENT '错误信息（JSON格式）',
  `file_url` varchar(500) DEFAULT NULL COMMENT '文件OSS地址',
  `bpm_process_id` varchar(100) DEFAULT NULL COMMENT '工作流流程ID（预留字段）',
  `bpm_order_no` varchar(100) DEFAULT NULL COMMENT '工作流工单号',
  `created_by` varchar(100) DEFAULT NULL COMMENT '创建人',
  `created_uid` varchar(100) DEFAULT NULL COMMENT '创建人UID',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `success_message` text COMMENT '成功信息（JSON格式）',
  PRIMARY KEY (`id`),
  KEY `idx_task_type` (`task_type`),
  KEY `idx_task_status` (`task_status`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB AUTO_INCREMENT=368 DEFAULT CHARSET=utf8mb4 COMMENT='批量操作作业表';
```


## 2. 字段说明

| 字段名             | 类型           | 必填 | 说明                         | 测试值示例                                  |
|-----------------|--------------|----|----------------------------|----------------------------------------|
| id              | bigint(20)   | ✅  | 作业唯一标识（自增ID）,也是批量抽数任务的作业ID | 368                                    |
| task_type       | varchar(50)  | ✅  | 作业类型：新增任务、新增字段、修改任务、下线任务   | 见下文2.2结构                               |
| task_status     | varchar(50)  | ✅  | 任务状态（待处理、校验中、成功、失败等）       | 见下文2.2结构                               |
| file_name       | varchar(255) | ❌  | 上传的文件原始名称                  | "batch_config_20231027.xlsx"           |
| total_count     | int(11)      | ✅  | 文件包含的总行数                   | 1000                                   |
| success_count   | int(11)      | ✅  | 执行成功的数量                    | 950                                    |
| failed_count    | int(11)      | ✅  | 执行失败的数量                    | 50                                     |
| error_message   | text         | ❌  | 错误信息（JSON格式）               | 见下文 3.1 结构                             |
| success_message | text         | ❌  | 成功信息（JSON格式）               | 见下文 3.2 结构                             |
| file_url        | varchar(500) | ❌  | 文件在OSS等云端存储的地址             | "https://oss.com/path/to/file.xlsx"    |
| bpm_process_id  | varchar(100) | ❌  | 工作流流程ID（预留）                | "5ab5fda7-e67e-41bb-8a3d-1b46ced33159" |
| bpm_order_no    | varchar(100) | ❌  | 业务审批工单号                    | "RCPLXX-202600000015"                  |
| created_by      | varchar(100) | ❌  | 创建人姓名                      | "张三"                                   |
| created_uid     | varchar(100) | ❌  | 创建人唯一标识UID                 | "0b7cd05f-d01a-41f3-8fa1-a3bd773d96ab" |
| created_at      | timestamp    | ✅  | 记录创建时间                     | "2023-10-27 10:00:00"                  |
| updated_at      | timestamp    | ✅  | 记录最后修改时间                   | "2023-10-27 10:05:00"                  |


### 2.1 任务类型字段的枚举说明 (task_type)
**枚举类：** `BatchOperationTypeEnum`

| 枚举值               | 描述     | 说明              |
|:------------------|:-------|:----------------|
| **UPLOAD**        | 批量新增任务 | 用于执行新任务的批量导入    |
| **FIELDS_UPDATE** | 批量新增字段 | 用于对现有任务批量扩展字段   |
| **TASK_MODIFY**   | 批量修改任务 | 用于批量调整任务的元数据或配置 |
| **TASK_OFFLINE**  | 批量下线任务 | 用于大批量停止或下线任务    |

---

### 2.2 任务状态字段的枚举说明 (task_status)
**枚举类：** `BatchTaskStatusEnum`

| 枚举值                  | 描述   | 备注              |
|:---------------------|:-----|:----------------|
| **PENDING**          | 待处理  | 任务创建后的初始状态      |
| **VALIDATING**       | 校验中  | 系统正在解析文件并进行逻辑校验 |
| **VALIDATE_FAILED**  | 校验失败 | 文件格式或数据内容校验不通过  |
| **VALIDATE_SUCCESS** | 校验成功 | 数据合法，准备进入审批阶段   |
| **PENDING_APPROVAL** | 待审核  | 进入审批工作流（预留状态）   |
| **APPROVING_FAIL**   | 审核失败 | 审批流程被驳回（预留状态）   |
| **EXECUTING**        | 执行中  | 审批通过，系统正在处理业务逻辑 |
| **SUCCESS**          | 成功   | 全部记录处理成功        |
| **PART_SUCCESS**     | 部分成功 | 部分处理成功，部分处理失败   |
| **FAILED**           | 失败   | 整个执行过程发生系统性错误   |


## 3. 字段结构详解

### 3.1 error_message 示例
用于记录校验失败或执行失败的具体行数和原因。
场景1:参数校验失败
```json
[
    {
        "dataSourceType": "mysql",
        "databaseName": "dataops_shitingjie",
        "errorMsg": "参数校验失败",
        "failureType": "PARSE_ERROR",
        "instanceName": "cjjcommon",
        "rowNumber": 9,
        "tableName": "stj_batch_0112_valid_5"
    }
]
```
场景2:元数据缺失，比如数据源类型错误; 表元数据缺失; 抽数主键不存在
```json
{
    "failedRows": [
        {
            "batchUploadParam": {
                "batchCount": 1024,
                "businessOwner": "施婷杰",
                "businessOwnerId": "71e8b23d-45e2-497a-b247-f5b807fb4f65",
                "cpu": "1",
                "createdBy": "施婷杰",
                "createdTime": "created_at",
                "creatorId": "71e8b23d-45e2-497a-b247-f5b807fb4f65",
                "dataSourceType": "oss",
                "databaseName": "dataops_shitingjie",
                "dealMethod": "merge",
                "etlxDataSource": "input_mysql_cjjcommon_dataops_shitingjie",
                "extractMethod": "ins",
                "extractPkFields": "id",
                "instanceName": "cjjcommon",
                "memory": 2048,
                "purpose": "元数据不完整",
                "scheduleCycle": "day",
                "scheduleTime": "00:20",
                "tableName": "stj_batch07_queyuanshuju",
                "techOwner": "施婷杰",
                "techOwnerId": "71e8b23d-45e2-497a-b247-f5b807fb4f65",
                "updatedTime": "updated_at",
                "userJourneyNode": "注册"
            },
            "dataSourceType": "oss",
            "databaseName": "dataops_shitingjie",
            "errorMsg": "数据源类型错误; 表元数据缺失; 抽数主键不存在",
            "failureType": "DATA_SOURCE_NOT_EXIST",
            "instanceName": "cjjcommon",
            "tableName": "stj_batch07_queyuanshuju"
        }
    ],
    "failureStatistics": {
        "DATA_SOURCE_NOT_EXIST": {
            "failedCount": 1,
            "failedTasks": [
                {
                    "databaseName": "dataops_shitingjie",
                    "errorMsg": "数据源类型错误; 表元数据缺失; 抽数主键不存在",
                    "instanceName": "cjjcommon",
                    "tableName": "stj_batch07_queyuanshuju"
                }
            ],
            "failureType": "DATA_SOURCE_NOT_EXIST",
            "failureTypeDesc": "数据源不存在"
        }
    },
    "fileRowCount": 1,
    "parseFailedRows": [

    ],
    "parsedCount": 1,
    "publishFailedCount": 1,
    "publishFailedParams": [
        {
            "$ref": "$.failedRows[0]"
        }
    ]
}
```
场景3:bpm工单流转中断
```string
BPM审批拒绝：未知原因
```
场景4:其他异常
```string
校验失败：
### Error updating database.  Cause: com.mysql.cj.jdbc.exceptions.MysqlDataTruncation: Data truncation: Data too long for column 'error_message' at row 1
```
        
### 3.2 success_message 示例
用于记录任务完成后返回的业务流水号或结果汇总。
```json
    {
        "batchUploadParam": {
            "batchCount": 1024,
            "businessOwner": "施婷杰",
            "businessOwnerId": "71e8b23d-45e2-497a-b247-f5b807fb4f65",
            "cpu": "1",
            "createdBy": "施婷杰",
            "createdTime": "created_at",
            "creatorId": "71e8b23d-45e2-497a-b247-f5b807fb4f65",
            "dataSourceType": "mysql",
            "databaseName": "dataops_shitingjie",
            "dealMethod": "merge",
            "etlxDataSource": "input_mysql_cjjcommon_dataops_shitingjie",
            "extractMethod": "ins",
            "extractPkFields": "id",
            "instanceName": "cjjcommon",
            "memory": 2048,
            "purpose": "tests",
            "scheduleCycle": "day",
            "scheduleTime": "00:20",
            "tableName": "stj_batch_0119_valid_fuce001",
            "techOwner": "施婷杰",
            "techOwnerId": "71e8b23d-45e2-497a-b247-f5b807fb4f65",
            "updatedTime": "updated_at",
            "userJourneyNode": "T00000008"
        },
        "dataSourceType": "mysql",
        "databaseName": "dataops_shitingjie",
        "instanceName": "cjjcommon",
        "rowNumber": 1,
        "tableName": "stj_batch_0119_valid_fuce001",
        "taskId": 3137
    }

```

## 4. 状态详解

### 4.1 状态流转 Mermaid 图
该图展示了任务从创建到终态的完整生命周期：

stateDiagram-v2
    [*] --> PENDING : 创建任务
    
    PENDING --> VALIDATING : 开始校验
    
    state VALIDATING {
        direction lr
        [*] --> 文件解析
        文件解析 --> 数据校验
        数据校验 --> [*]
    }

    VALIDATING --> VALIDATE_FAILED : 校验不通过
    VALIDATING --> VALIDATE_SUCCESS : 校验通过

    VALIDATE_SUCCESS --> PENDING_APPROVAL : 提交审批
    
    PENDING_APPROVAL --> APPROVING_FAIL : 审批拒绝
    PENDING_APPROVAL --> EXECUTING : 审批通过/开始执行

    state EXECUTING {
        direction lr
        [*] --> 业务处理
        业务处理 --> 计数更新
        计数更新 --> [*]
    }

    EXECUTING --> SUCCESS : 全部成功
    EXECUTING --> PART_SUCCESS : 部分成功
    EXECUTING --> FAILED : 执行异常

    VALIDATE_FAILED --> [*]
    APPROVING_FAIL --> [*]
    SUCCESS --> [*]
    PART_SUCCESS --> [*]
    FAILED --> [*]

    note right of EXECUTING
        更新 success_count
        更新 failed_count
        记录 error_message
    end note

