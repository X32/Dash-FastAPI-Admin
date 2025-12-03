#!/bin/bash

# 会话管理模块API测试脚本
# 基础URL
BASE_URL="http://localhost:9019/api/v1"
USER_ID=1

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== 会话管理模块API测试 ===${NC}"
echo "基础URL: $BASE_URL"
echo "用户ID: $USER_ID"
echo ""

# 1. 获取会话列表
echo -e "${GREEN}1. 获取会话列表${NC}"
curl -X GET "$BASE_URL/conversations?user_id=$USER_ID" \
  -H "Content-Type: application/json"
echo -e "\n\n"

# 2. 创建新会话
echo -e "${GREEN}2. 创建新会话${NC}"
curl -X POST "$BASE_URL/conversations?user_id=$USER_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "测试会话"
  }'
echo -e "\n\n"

# 3. 获取会话详情 (替换CONVERSATION_ID为实际ID)
CONVERSATION_ID=1762
echo -e "${GREEN}3. 获取会话详情 - 会话ID: $CONVERSATION_ID${NC}"
curl -X GET "$BASE_URL/conversations/$CONVERSATION_ID?user_id=$USER_ID" \
  -H "Content-Type: application/json"
echo -e "\n\n"

# 4. 更新会话
echo -e "${GREEN}4. 更新会话 - 会话ID: $CONVERSATION_ID${NC}"
curl -X PUT "$BASE_URL/conversations/$CONVERSATION_ID?user_id=$USER_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "更新后的会话标题"
  }'
echo -e "\n\n"

# 5. 创建消息
echo -e "${GREEN}5. 创建消息 - 会话ID: $CONVERSATION_ID${NC}"
curl -X POST "$BASE_URL/conversations/$CONVERSATION_ID/messages?user_id=$USER_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "user",
    "content": "这是一条测试消息"
  }'
echo -e "\n\n"

# 6. 批量创建消息内容
echo -e "${GREEN}6. 批量创建消息内容 - 会话ID: $CONVERSATION_ID${NC}"
curl -X POST "$BASE_URL/conversations/$CONVERSATION_ID/messages/batch?user_id=$USER_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "批量消息1"
      },
      {
        "role": "assistant", 
        "content": "批量消息2"
      }
    ]
  }'
echo -e "\n\n"

# 7. 更新消息 (替换MESSAGE_ID为实际ID)
MESSAGE_ID=302
echo -e "${GREEN}7. 更新消息 - 消息ID: $MESSAGE_ID${NC}"
curl -X PUT "$BASE_URL/conversations/messages/$MESSAGE_ID?user_id=$USER_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "seq": 2
  }'
echo -e "\n\n"

# 8. 删除消息 (替换MESSAGE_ID为实际ID)
echo -e "${GREEN}8. 删除消息 - 消息ID: $MESSAGE_ID${NC}"
curl -X DELETE "$BASE_URL/conversations/messages/$MESSAGE_ID?user_id=$USER_ID" \
  -H "Content-Type: application/json"
echo -e "\n\n"

# 9. 删除会话
echo -e "${GREEN}9. 删除会话 - 会话ID: $CONVERSATION_ID${NC}"
curl -X DELETE "$BASE_URL/conversations/$CONVERSATION_ID?user_id=$USER_ID" \
  -H "Content-Type: application/json"
echo -e "\n\n"

echo -e "${YELLOW}=== 测试完成 ===${NC}"

# 使用方法:
# 1. 保存为 test_conversation_api.sh
# 2. 添加执行权限: chmod +x test_conversation_api.sh  
# 3. 运行脚本: ./test_conversation_api.sh
# 4. 根据需要修改变量值（如CONVERSATION_ID, MESSAGE_ID等）