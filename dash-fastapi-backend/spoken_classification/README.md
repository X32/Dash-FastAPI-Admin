# 话题分类管理模块接口文档

## 模块概述
话题分类管理模块用于管理话题的一二级分类，支持分类的增删改查操作，并提供分类树结构展示。

## 数据库表结构

### topic_category 表

| 字段名 | 类型 | 长度 | 允许空 | 默认值 | 描述 |
|--------|------|------|--------|--------|------|
| category_id | bigint | 20 | 否 |  | 分类ID（主键） |
| parent_id | bigint | 20 | 是 | 0 | 父分类ID |
| category_name | varchar | 50 | 否 |  | 分类名称 |
| description | varchar | 200 | 是 | '' | 分类描述 |
| order_num | int | 4 | 是 | 0 | 显示顺序 |
| del_flag | char | 1 | 是 | '0' | 删除标志（0代表存在 2代表删除） |
| create_by | varchar | 64 | 是 | '' | 创建者 |
| create_time | datetime |  | 是 |  | 创建时间 |
| update_by | varchar | 64 | 是 | '' | 更新者 |
| update_time | datetime |  | 是 |  | 更新时间 |

**索引：**
- 主键索引：category_id
- 唯一索引：uk_parent_name (parent_id, category_name) - 同一父分类下名称唯一

## API接口

### 1. 获取一级话题分类列表

**接口地址：** GET /spoken_classification/topic_category/first_level

**接口描述：** 获取所有一级话题分类（parent_id=0）

**请求参数：** 无

**响应示例：**
```json
{
  "code": 200,
  "message": "操作成功",
  "data": [
    {
      "category_id": 100,
      "parent_id": 0,
      "category_name": "科技",
      "description": "科技相关话题分类",
      "order_num": 1,
      "del_flag": "0",
      "create_by": "admin",
      "create_time": "2024-01-01 12:00:00",
      "update_by": "",
      "update_time": null
    },
    {
      "category_id": 101,
      "parent_id": 0,
      "category_name": "生活",
      "description": "生活相关话题分类",
      "order_num": 2,
      "del_flag": "0",
      "create_by": "admin",
      "create_time": "2024-01-01 12:00:00",
      "update_by": "",
      "update_time": null
    }
  ]
}
```

### 2. 获取指定一级分类下的二级话题分类列表

**接口地址：** GET /spoken_classification/topic_category/second_level/{parent_id}

**接口描述：** 获取指定一级分类下的所有二级话题分类

**请求参数：**
- parent_id: 父分类ID（路径参数）

**响应示例：**
```json
{
  "code": 200,
  "message": "操作成功",
  "data": [
    {
      "category_id": 103,
      "parent_id": 100,
      "category_name": "人工智能",
      "description": "AI相关话题",
      "order_num": 1,
      "del_flag": "0",
      "create_by": "admin",
      "create_time": "2024-01-01 12:00:00",
      "update_by": "",
      "update_time": null
    },
    {
      "category_id": 104,
      "parent_id": 100,
      "category_name": "互联网",
      "description": "互联网技术话题",
      "order_num": 2,
      "del_flag": "0",
      "create_by": "admin",
      "create_time": "2024-01-01 12:00:00",
      "update_by": "",
      "update_time": null
    }
  ]
}
```

### 3. 获取话题分类树结构

**接口地址：** GET /spoken_classification/topic_category/tree

**接口描述：** 获取完整的话题分类树结构

**请求参数：** 无

**响应示例：**
```json
{
  "code": 200,
  "message": "操作成功",
  "data": [
    {
      "category_id": 100,
      "parent_id": 0,
      "category_name": "科技",
      "description": "科技相关话题分类",
      "order_num": 1,
      "del_flag": "0",
      "create_by": "admin",
      "create_time": "2024-01-01 12:00:00",
      "update_by": "",
      "update_time": null,
      "children": [
        {
          "category_id": 103,
          "parent_id": 100,
          "category_name": "人工智能",
          "description": "AI相关话题",
          "order_num": 1,
          "del_flag": "0",
          "create_by": "admin",
          "create_time": "2024-01-01 12:00:00",
          "update_by": "",
          "update_time": null,
          "children": []
        }
      ]
    }
  ]
}
```

### 4. 新增话题分类

**接口地址：** POST /spoken_classification/topic_category

**接口描述：** 新增话题分类

**请求参数：**
```json
{
  "parent_id": 0,
  "category_name": "教育",
  "description": "教育相关话题分类",
  "order_num": 4
}
```

**参数说明：**
- parent_id: 父分类ID（0表示一级分类）
- category_name: 分类名称（必填，同一父分类下唯一）
- description: 分类描述
- order_num: 显示顺序（必填）

**响应示例：**
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "is_success": true,
    "message": "新增成功",
    "data": null
  }
}
```

### 5. 编辑话题分类

**接口地址：** PUT /spoken_classification/topic_category

**接口描述：** 编辑话题分类

**请求参数：**
```json
{
  "category_id": 100,
  "category_name": "科技类",
  "description": "科技相关话题分类",
  "order_num": 1
}
```

**参数说明：**
- category_id: 分类ID（必填）
- category_name: 分类名称（同一父分类下唯一）
- description: 分类描述
- order_num: 显示顺序

**响应示例：**
```json
{
  "code": 200,
  "message": "更新成功",
  "data": null
}
```

### 6. 删除话题分类

**接口地址：** DELETE /spoken_classification/topic_category/{category_ids}

**接口描述：** 删除话题分类（支持批量删除）

**请求参数：**
- category_ids: 分类ID列表（路径参数，多个ID用逗号分隔）

**响应示例：**
```json
{
  "code": 200,
  "message": "删除成功",
  "data": null
}
```

**删除规则：**
- 分类必须存在
- 分类不能有子分类
- 分类不能有关联话题（待实现）

## 权限说明

所有接口需要登录后访问，并需要以下权限：
- 列表查询：spoken_classification:topic_category:list
- 新增：spoken_classification:topic_category:add
- 编辑：spoken_classification:topic_category:edit
- 删除：spoken_classification:topic_category:remove

## 错误码说明

| 错误码 | 描述 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 未登录或登录已过期 |
| 403 | 没有权限访问 |
| 500 | 服务器内部错误 |

## 业务错误信息

- "同一父分类下分类名称不能重复": 新增或编辑时分类名称在同一父分类下已存在
- "父分类不存在": 新增或编辑时指定的父分类不存在
- "只能查询一级分类下的二级分类": 查询二级分类时父分类不是一级分类
- "分类不存在": 编辑或删除时分类ID不存在
- "分类ID {id} 下存在子分类，无法删除": 删除的分类下存在子分类
- "分类ID {id} 下存在关联话题，无法删除": 删除的分类下存在关联话题（待实现）