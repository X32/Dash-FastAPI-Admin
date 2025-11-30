# 会话管理系统模块文档

## 模块概述
会话管理系统模块提供了完整的会话和消息管理功能，支持按用户ID查询会话列表、会话详情查询，以及会话和消息的完整CRUD操作。

## 核心功能
1. **会话管理**：创建、查询、更新、删除会话
2. **消息管理**：创建、更新、删除消息及其内容
3. **权限控制**：用户只能操作自己的会话和消息
4. **分页查询**：支持会话列表的分页查询
5. **事务处理**：确保数据一致性

## API接口文档

### 会话相关接口

#### 1. 创建会话
- **URL**: `POST /conversations/`
- **描述**: 创建新的会话
- **请求参数**:
  - `user_id` (query): 用户ID
  - `title` (body): 会话标题
- **响应**: 创建的会话信息
- **示例**:
```json
请求：
POST /conversations/?user_id=1
{
  "title": "新会话"
}

响应：
{
  "conversation_id": 1,
  "user_id": 1,
  "title": "新会话",
  "status": 1,
  "create_time": "2024-01-01 10:00:00",
  "update_time": "2024-01-01 10:00:00"
}
```

#### 2. 获取会话列表
- **URL**: `GET /conversations/list`
- **描述**: 获取用户的会话列表（分页）
- **请求参数**:
  - `user_id` (query): 用户ID（必填）
  - `status` (query): 会话状态，1-有效，0-已删除（默认1）
  - `page` (query): 页码（默认1）
  - `page_size` (query): 每页条数（默认20，最大100）
- **响应**: 会话列表和分页信息
- **示例**:
```json
请求：
GET /conversations/list?user_id=1&status=1&page=1&page_size=20

响应：
{
  "total": 50,
  "page": 1,
  "page_size": 20,
  "conversations": [
    {
      "conversation_id": 1,
      "user_id": 1,
      "title": "会话1",
      "status": 1,
      "create_time": "2024-01-01 10:00:00",
      "update_time": "2024-01-01 11:00:00"
    }
  ]
}
```

#### 3. 获取会话详情
- **URL**: `GET /conversations/{conversation_id}`
- **描述**: 获取会话详情，包含所有消息和内容
- **请求参数**:
  - `conversation_id` (path): 会话ID
  - `user_id` (query): 用户ID
- **响应**: 会话详情，包含消息列表
- **示例**:
```json
请求：
GET /conversations/1?user_id=1

响应：
{
  "conversation": {
    "conversation_id": 1,
    "user_id": 1,
    "title": "会话1",
    "status": 1,
    "create_time": "2024-01-01 10:00:00",
    "update_time": "2024-01-01 11:00:00"
  },
  "messages": [
    {
      "message_id": 1,
      "conversation_id": 1,
      "role": "user",
      "seq": 1,
      "create_time": "2024-01-01 10:00:00",
      "contents": [
        {
          "content_id": 1,
          "message_id": 1,
          "content_type": "text",
          "text": "你好",
          "seq": 1
        }
      ]
    }
  ]
}
```

#### 4. 更新会话
- **URL**: `PUT /conversations/{conversation_id}`
- **描述**: 更新会话信息
- **请求参数**:
  - `conversation_id` (path): 会话ID
  - `user_id` (query): 用户ID
  - `title` (body): 新标题（可选）
  - `status` (body): 新状态（可选）
- **响应**: 更新后的会话信息
- **示例**:
```json
请求：
PUT /conversations/1?user_id=1
{
  "title": "更新后的标题"
}

响应：
{
  "conversation_id": 1,
  "user_id": 1,
  "title": "更新后的标题",
  "status": 1,
  "create_time": "2024-01-01 10:00:00",
  "update_time": "2024-01-01 12:00:00"
}
```

#### 5. 删除会话
- **URL**: `DELETE /conversations/{conversation_id}`
- **描述**: 删除会话（软删除）
- **请求参数**:
  - `conversation_id` (path): 会话ID
  - `user_id` (query): 用户ID
- **响应**: 无内容（204）

### 消息相关接口

#### 6. 创建消息
- **URL**: `POST /conversations/{conversation_id}/messages`
- **描述**: 创建消息及其内容
- **请求参数**:
  - `conversation_id` (path): 会话ID
  - `user_id` (query): 用户ID
  - `role` (body): 消息角色（user/assistant/examiner）
  - `seq` (body): 消息序号
  - `contents` (body): 消息内容列表
- **响应**: 创建的消息信息
- **示例**:
```json
请求：
POST /conversations/1/messages?user_id=1
{
  "role": "user",
  "seq": 1,
  "contents": [
    {
      "content_type": "text",
      "text": "你好，这是一个测试消息",
      "seq": 1
    }
  ]
}

响应：
{
  "message_id": 1,
  "conversation_id": 1,
  "role": "user",
  "seq": 1,
  "create_time": "2024-01-01 10:00:00",
  "contents": [
    {
      "content_id": 1,
      "message_id": 1,
      "content_type": "text",
      "text": "你好，这是一个测试消息",
      "seq": 1
    }
  ]
}
```

#### 7. 更新消息
- **URL**: `PUT /conversations/messages/{message_id}`
- **描述**: 更新消息信息
- **请求参数**:
  - `message_id` (path): 消息ID
  - `user_id` (query): 用户ID
  - `role` (body): 新角色（可选）
  - `seq` (body): 新序号（可选）
- **响应**: 更新后的消息信息

#### 8. 删除消息
- **URL**: `DELETE /conversations/messages/{message_id}`
- **描述**: 删除消息（级联删除内容）
- **请求参数**:
  - `message_id` (path): 消息ID
  - `user_id` (query): 用户ID
- **响应**: 无内容（204）

## 错误码说明

| 错误码 | 错误描述 | 说明 |
|--------|----------|------|
| 400 | 参数不合法 | 请求参数格式错误或缺少必填参数 |
| 403 | 无权限访问 | 用户无权访问该资源 |
| 404 | 资源不存在 | 会话或消息不存在 |
| 500 | 服务器错误 | 数据库操作失败等内部错误 |

## 使用说明

### 1. 数据库配置
确保数据库连接配置正确，在 `config/database.py` 中配置数据库连接信息。

### 2. 注册路由
在主应用文件中注册会话管理模块的路由：

```python
from module_conversation.controller import router as conversation_router
from module_conversation.exception import conversation_exception_handler
from module_conversation.exception.conversation_exception import ConversationException

# 注册异常处理器
app.add_exception_handler(ConversationException, conversation_exception_handler)

# 注册路由
app.include_router(conversation_router)
```

### 3. 权限验证
所有接口都需要通过 `user_id` 参数进行权限验证，确保用户只能访问自己的会话和消息。

### 4. 事务处理
所有涉及多个数据库操作的功能都使用事务处理，确保数据一致性。例如创建消息时，消息和内容必须同时插入成功。

### 5. 性能优化
- 使用索引字段进行查询（user_id、conversation_id、message_id）
- 批量操作优化（如批量插入消息内容）
- 分页查询避免全表扫描

## 数据库设计

### 表结构
1. **conversations**: 会话表
2. **messages**: 消息表
3. **message_contents**: 消息内容表

### 索引建议
- conversations 表：在 user_id 和 status 字段上创建联合索引
- messages 表：在 conversation_id 字段上创建索引
- message_contents 表：在 message_id 字段上创建索引

### 外键约束
- conversations.user_id -> users.user_id（ON DELETE CASCADE）
- messages.conversation_id -> conversations.conversation_id（ON DELETE CASCADE）
- message_contents.message_id -> messages.message_id（ON DELETE CASCADE）