# 话题分类管理模块

## 功能介绍

话题分类管理模块用于管理话题的一二级分类，支持分类的增删改查操作，并提供了完善的业务逻辑校验。

## 数据库表结构

### topic_classification 表

```sql
CREATE TABLE IF NOT EXISTS topic_classification (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    name VARCHAR(50) NOT NULL COMMENT '分类名称',
    description VARCHAR(200) DEFAULT '' COMMENT '分类描述',
    parent_id BIGINT DEFAULT 0 COMMENT '父分类ID，0表示一级分类',
    sort_order INT DEFAULT 0 COMMENT '排序序号，越小越靠前',
    is_deleted TINYINT DEFAULT 0 COMMENT '是否删除，0-未删除，1-已删除',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    -- 同层级分类名称唯一约束
    UNIQUE KEY uk_name_parent_id (name, parent_id, is_deleted) COMMENT '同层级分类名称唯一'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='话题分类表';
```

## 接口文档

### 1. 创建话题分类

**接口地址**: POST /api/topic-classification/create

**请求参数**:
```json
{
  "name": "分类名称",
  "description": "分类描述",
  "parent_id": 0,
  "sort_order": 1
}
```

**参数说明**:
- `name`: 分类名称（必填，最大长度50）
- `description`: 分类描述（可选，最大长度200）
- `parent_id`: 父分类ID（可选，默认0表示一级分类）
- `sort_order`: 排序序号（可选，默认0，越小越靠前）

**返回示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "id": 1,
    "name": "科技",
    "description": "科技相关话题",
    "parent_id": 0,
    "sort_order": 1,
    "is_deleted": 0,
    "create_time": "2023-05-20T12:00:00",
    "update_time": "2023-05-20T12:00:00"
  }
}
```

### 2. 更新话题分类

**接口地址**: PUT /api/topic-classification/update

**请求参数**:
```json
{
  "id": 1,
  "name": "分类名称",
  "description": "分类描述",
  "parent_id": 0,
  "sort_order": 1
}
```

**参数说明**:
- `id`: 分类ID（必填）
- `name`: 分类名称（必填，最大长度50）
- `description`: 分类描述（可选，最大长度200）
- `parent_id`: 父分类ID（可选，默认0表示一级分类）
- `sort_order`: 排序序号（可选，默认0，越小越靠前）

**返回示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "id": 1,
    "name": "科技",
    "description": "科技相关话题",
    "parent_id": 0,
    "sort_order": 1,
    "is_deleted": 0,
    "create_time": "2023-05-20T12:00:00",
    "update_time": "2023-05-20T12:00:00"
  }
}
```

### 3. 删除话题分类

**接口地址**: DELETE /api/topic-classification/delete/{id}

**路径参数**:
- `id`: 分类ID（必填）

**返回示例**:
```json
{
  "code": 200,
  "message": "删除成功",
  "data": null
}
```

### 4. 批量删除话题分类

**接口地址**: DELETE /api/topic-classification/batch-delete

**请求参数**:
```json
[1, 2, 3]
```

**参数说明**:
- `ids`: 分类ID列表（必填）

**返回示例**:
```json
{
  "code": 200,
  "message": "成功删除3个分类",
  "data": {
    "success_count": 3,
    "failed_count": 0,
    "failed_ids": []
  }
}
```

### 5. 根据ID获取话题分类

**接口地址**: GET /api/topic-classification/get/{id}

**路径参数**:
- `id`: 分类ID（必填）

**返回示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "id": 1,
    "name": "科技",
    "description": "科技相关话题",
    "parent_id": 0,
    "sort_order": 1,
    "is_deleted": 0,
    "create_time": "2023-05-20T12:00:00",
    "update_time": "2023-05-20T12:00:00"
  }
}
```

### 6. 获取一级话题分类列表

**接口地址**: GET /api/topic-classification/first-level

**查询参数**:
- `page`: 页码（可选，默认1）
- `page_size`: 每页大小（可选，默认10，最大100）

**返回示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "list": [
      {
        "id": 1,
        "name": "科技",
        "description": "科技相关话题",
        "parent_id": 0,
        "sort_order": 1,
        "is_deleted": 0,
        "create_time": "2023-05-20T12:00:00",
        "update_time": "2023-05-20T12:00:00"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 10
  }
}
```

### 7. 获取指定一级分类下的二级话题分类列表

**接口地址**: GET /api/topic-classification/second-level/{parent_id}

**路径参数**:
- `parent_id`: 一级分类ID（必填）

**查询参数**:
- `page`: 页码（可选，默认1）
- `page_size`: 每页大小（可选，默认10，最大100）

**返回示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "list": [
      {
        "id": 4,
        "name": "人工智能",
        "description": "人工智能技术话题",
        "parent_id": 1,
        "sort_order": 1,
        "is_deleted": 0,
        "create_time": "2023-05-20T12:00:00",
        "update_time": "2023-05-20T12:00:00"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 10
  }
}
```

### 8. 根据父ID获取话题分类列表

**接口地址**: POST /api/topic-classification/list

**请求参数**:
```json
{
  "parent_id": 0,
  "page": 1,
  "page_size": 10
}
```

**参数说明**:
- `parent_id`: 父分类ID（可选，默认0表示一级分类）
- `page`: 页码（可选，默认1）
- `page_size`: 每页大小（可选，默认10，最大100）

**返回示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "list": [
      {
        "id": 1,
        "name": "科技",
        "description": "科技相关话题",
        "parent_id": 0,
        "sort_order": 1,
        "is_deleted": 0,
        "create_time": "2023-05-20T12:00:00",
        "update_time": "2023-05-20T12:00:00"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 10
  }
}
```

## 测试程序

### 测试脚本

```python
import requests

# 基础URL
BASE_URL = "http://localhost:8000/api/topic-classification"


def test_create_classification():
    """测试创建分类"""
    data = {
        "name": "测试分类",
        "description": "测试分类描述",
        "parent_id": 0,
        "sort_order": 1
    }
    response = requests.post(f"{BASE_URL}/create", json=data)
    print("创建分类响应:", response.json())
    return response.json().get("data", {}).get("id")


def test_update_classification(id):
    """测试更新分类"""
    data = {
        "id": id,
        "name": "更新后的测试分类",
        "description": "更新后的测试分类描述",
        "parent_id": 0,
        "sort_order": 2
    }
    response = requests.put(f"{BASE_URL}/update", json=data)
    print("更新分类响应:", response.json())


def test_get_classification(id):
    """测试根据ID获取分类"""
    response = requests.get(f"{BASE_URL}/get/{id}")
    print("根据ID获取分类响应:", response.json())


def test_get_first_level_classifications():
    """测试获取一级分类列表"""
    response = requests.get(f"{BASE_URL}/first-level?page=1&page_size=10")
    print("获取一级分类列表响应:", response.json())


def test_delete_classification(id):
    """测试删除分类"""
    response = requests.delete(f"{BASE_URL}/delete/{id}")
    print("删除分类响应:", response.json())


if __name__ == "__main__":
    # 测试创建分类
    classification_id = test_create_classification()
    if classification_id:
        # 测试根据ID获取分类
        test_get_classification(classification_id)
        # 测试更新分类
        test_update_classification(classification_id)
        # 测试获取一级分类列表
        test_get_first_level_classifications()
        # 测试删除分类
        test_delete_classification(classification_id)