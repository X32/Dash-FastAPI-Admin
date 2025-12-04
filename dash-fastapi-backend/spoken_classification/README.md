# 话题分类管理模块

## 功能概述

话题分类管理模块用于管理话题的分类信息，支持一级分类和二级分类的管理。

## 数据库表结构

### topic_category 表

| 字段名 | 类型 | 长度 | 允许空 | 默认值 | 注释 |
| ---- | ---- | ---- | ---- | ---- | ---- |
| id | BIGINT | - | 否 | - | 分类ID |
| category_name | VARCHAR | 50 | 否 | - | 分类名称 |
| category_desc | VARCHAR | 200 | 是 | '' | 分类描述 |
| parent_id | BIGINT | - | 是 | 0 | 父分类ID，0表示一级分类 |
| sort_order | INT | - | 是 | 0 | 排序 |
| is_deleted | TINYINT | - | 是 | 0 | 是否删除，0未删除，1已删除 |
| created_time | DATETIME | - | 是 | CURRENT_TIMESTAMP | 创建时间 |
| updated_time | DATETIME | - | 是 | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

**唯一约束**：`uk_name_parent` (category_name, parent_id, is_deleted) - 同层级分类名称唯一

## 接口列表

### 1. 获取所有一级分类

**接口地址**：`GET /topic-category/first-level`

**接口描述**：获取所有一级分类信息

**请求参数**：无

**返回结果**：
```json
{
  "code": 0,
  "message": "成功",
  "data": [
    {
      "id": 1,
      "category_name": "科技",
      "category_desc": "科技相关话题",
      "parent_id": 0,
      "sort_order": 1,
      "is_deleted": false,
      "created_time": "2023-01-01T00:00:00",
      "updated_time": "2023-01-01T00:00:00"
    }
  ]
}
```

### 2. 获取指定一级分类下的所有二级分类

**接口地址**：`GET /topic-category/second-level/{parent_id}`

**接口描述**：获取指定一级分类下的所有二级分类信息

**请求参数**：
| 参数名 | 类型 | 位置 | 必须 | 描述 |
| ---- | ---- | ---- | ---- | ---- |
| parent_id | INT | 路径 | 是 | 一级分类ID |

**返回结果**：
```json
{
  "code": 0,
  "message": "成功",
  "data": [
    {
      "id": 2,
      "category_name": "人工智能",
      "category_desc": "人工智能相关话题",
      "parent_id": 1,
      "sort_order": 1,
      "is_deleted": false,
      "created_time": "2023-01-01T00:00:00",
      "updated_time": "2023-01-01T00:00:00"
    }
  ]
}
```

### 3. 根据ID获取分类

**接口地址**：`GET /topic-category/{id}`

**接口描述**：根据分类ID获取分类信息

**请求参数**：
| 参数名 | 类型 | 位置 | 必须 | 描述 |
| ---- | ---- | ---- | ---- | ---- |
| id | INT | 路径 | 是 | 分类ID |

**返回结果**：
```json
{
  "code": 0,
  "message": "成功",
  "data": {
    "id": 1,
    "category_name": "科技",
    "category_desc": "科技相关话题",
    "parent_id": 0,
    "sort_order": 1,
    "is_deleted": false,
    "created_time": "2023-01-01T00:00:00",
    "updated_time": "2023-01-01T00:00:00"
  }
}
```

### 4. 创建分类

**接口地址**：`POST /topic-category/`

**接口描述**：创建新的分类

**请求参数**：
| 参数名 | 类型 | 位置 | 必须 | 描述 |
| ---- | ---- | ---- | ---- | ---- |
| category_name | STRING | 请求体 | 是 | 分类名称 |
| category_desc | STRING | 请求体 | 否 | 分类描述 |
| parent_id | INT | 请求体 | 否 | 父分类ID，0表示一级分类 |
| sort_order | INT | 请求体 | 否 | 排序 |

**请求示例**：
```json
{
  "category_name": "人工智能",
  "category_desc": "人工智能相关话题",
  "parent_id": 1,
  "sort_order": 1
}
```

**返回结果**：
```json
{
  "code": 0,
  "message": "分类创建成功",
  "data": {
    "id": 2,
    "category_name": "人工智能",
    "category_desc": "人工智能相关话题",
    "parent_id": 1,
    "sort_order": 1,
    "is_deleted": false,
    "created_time": "2023-01-01T00:00:00",
    "updated_time": "2023-01-01T00:00:00"
  }
}
```

### 5. 更新分类

**接口地址**：`PUT /topic-category/{id}`

**接口描述**：更新分类信息

**请求参数**：
| 参数名 | 类型 | 位置 | 必须 | 描述 |
| ---- | ---- | ---- | ---- | ---- |
| id | INT | 路径 | 是 | 分类ID |
| category_name | STRING | 请求体 | 否 | 分类名称 |
| category_desc | STRING | 请求体 | 否 | 分类描述 |
| parent_id | INT | 请求体 | 否 | 父分类ID |
| sort_order | INT | 请求体 | 否 | 排序 |

**请求示例**：
```json
{
  "category_name": "人工智能技术",
  "category_desc": "人工智能技术相关话题",
  "sort_order": 2
}
```

**返回结果**：
```json
{
  "code": 0,
  "message": "分类更新成功",
  "data": {
    "id": 2,
    "category_name": "人工智能技术",
    "category_desc": "人工智能技术相关话题",
    "parent_id": 1,
    "sort_order": 2,
    "is_deleted": false,
    "created_time": "2023-01-01T00:00:00",
    "updated_time": "2023-01-02T00:00:00"
  }
}
```

### 6. 删除分类

**接口地址**：`DELETE /topic-category/{id}`

**接口描述**：删除分类（软删除）

**请求参数**：
| 参数名 | 类型 | 位置 | 必须 | 描述 |
| ---- | ---- | ---- | ---- | ---- |
| id | INT | 路径 | 是 | 分类ID |

**返回结果**：
```json
{
  "code": 0,
  "message": "分类删除成功"
}
```

## 测试程序

### 测试脚本

测试脚本 `test_topic_category_api.sh` 用于测试话题分类管理模块的所有接口。

### 运行测试

```bash
chmod +x test_topic_category_api.sh
./test_topic_category_api.sh
```

### 测试说明

测试脚本将按照以下顺序测试接口：
1. 获取所有一级分类
2. 获取指定一级分类下的所有二级分类
3. 根据ID获取分类
4. 创建分类
5. 更新分类
6. 删除分类

测试脚本将输出每个接口的测试结果，包括响应码、响应消息和响应数据。