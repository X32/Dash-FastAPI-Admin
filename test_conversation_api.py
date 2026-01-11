import requests
import json

# Base URL of the API
BASE_URL = "http://0.0.0.0:9089/dev-api"

def test_create_conversation():
    """测试创建会话"""
    url = f"{BASE_URL}/conversation/create"
    headers = {"Content-Type": "application/json"}
    
    # 测试数据 - user_id现在从认证信息获取，请求体不需要传
    payload = {
        "title": "测试会话标题",
        "remark": "这是一条测试会话的备注"
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    print("=== 创建会话测试 ===")
    print(f"状态码: {response.status_code}")
    try:
        response_data = response.json()
        print(f"响应内容: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
        return response_data.get("data", {}).get("conversation_id")
    except json.JSONDecodeError:
        print(f"响应内容: {response.text}")
        return None

def test_create_message(conversation_id):
    """测试创建消息"""
    if not conversation_id:
        print("=== 创建消息测试 ===")
        print("跳过，没有有效的会话ID")
        return None
    
    url = f"{BASE_URL}/conversation/{conversation_id}/message/create"
    headers = {"Content-Type": "application/json"}
    
    # 测试数据 - 后端定义的MessageCreateRequest结构
    payload = {
        "role": "user",
        "contents": [
            {
                "content_type": "text",
                "text": "你好，这是一条测试消息"
            }
        ]
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    print("\n=== 创建消息测试 ===")
    print(f"状态码: {response.status_code}")
    try:
        response_data = response.json()
        print(f"响应内容: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
        return response_data.get("data", {}).get("message_id")
    except json.JSONDecodeError:
        print(f"响应内容: {response.text}")
        return None

def test_get_conversation_list():
    """测试获取会话列表"""
    url = f"{BASE_URL}/conversation/list"
    
    response = requests.get(url)
    print("\n=== 获取会话列表测试 ===")
    print(f"状态码: {response.status_code}")
    try:
        response_data = response.json()
        print(f"响应内容: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
    except json.JSONDecodeError:
        print(f"响应内容: {response.text}")

def test_get_conversation_detail(conversation_id):
    """测试获取会话详情"""
    if not conversation_id:
        print("\n=== 获取会话详情测试 ===")
        print("跳过，没有有效的会话ID")
        return
    
    url = f"{BASE_URL}/conversation/detail/{conversation_id}"
    
    response = requests.get(url)
    print("\n=== 获取会话详情测试 ===")
    print(f"状态码: {response.status_code}")
    try:
        response_data = response.json()
        print(f"响应内容: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
    except json.JSONDecodeError:
        print(f"响应内容: {response.text}")

def test_delete_conversation(conversation_id):
    """测试删除会话"""
    if not conversation_id:
        print("\n=== 删除会话测试 ===")
        print("跳过，没有有效的会话ID")
        return
    
    url = f"{BASE_URL}/conversation/delete/{conversation_id}"
    
    response = requests.delete(url)
    print("\n=== 删除会话测试 ===")
    print(f"状态码: {response.status_code}")
    try:
        response_data = response.json()
        print(f"响应内容: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
    except json.JSONDecodeError:
        print(f"响应内容: {response.text}")

if __name__ == "__main__":
    print("=== 会话管理API测试 ===")
    print(f"API基础URL: {BASE_URL}")
    
    # 按顺序执行测试
    conversation_id = test_create_conversation()
    message_id = test_create_message(conversation_id)
    test_get_conversation_list()
    test_get_conversation_detail(conversation_id)
    test_delete_conversation(conversation_id)
    
    print("\n=== 所有测试完成 ===")