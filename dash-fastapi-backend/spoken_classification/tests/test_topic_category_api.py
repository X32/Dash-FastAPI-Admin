import pytest
import asyncio
import aiohttp
import json

# 测试配置
BASE_URL = "http://localhost:9019"
TOKEN = "your_jwt_token_here"  # 需要替换为实际的JWT token

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}


@pytest.mark.asyncio
async def test_get_first_level_categories():
    """测试获取一级分类列表"""
    url = f"{BASE_URL}/spoken_classification/topic_category/first_level"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            print(f"\n=== 测试获取一级分类列表 ===")
            print(f"状态码: {response.status}")
            result = await response.json()
            print(f"响应结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return result


@pytest.mark.asyncio
async def test_get_second_level_categories():
    """测试获取二级分类列表"""
    parent_id = 1  # 使用默认的一级分类ID
    url = f"{BASE_URL}/spoken_classification/topic_category/second_level/{parent_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            print(f"\n=== 测试获取一级分类 {parent_id} 下的二级分类列表 ===")
            print(f"状态码: {response.status}")
            result = await response.json()
            print(f"响应结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return result


@pytest.mark.asyncio
async def test_get_category_tree():
    """测试获取分类树结构"""
    url = f"{BASE_URL}/spoken_classification/topic_category/tree"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            print(f"\n=== 测试获取分类树结构 ===")
            print(f"状态码: {response.status}")
            result = await response.json()
            print(f"响应结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return result


@pytest.mark.asyncio
async def test_add_category():
    """测试新增分类"""
    url = f"{BASE_URL}/spoken_classification/topic_category"
    data = {
        "parent_id": 0,
        "category_name": "教育",
        "description": "教育相关话题分类",
        "order_num": 4
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            print(f"\n=== 测试新增分类 ===")
            print(f"状态码: {response.status}")
            result = await response.json()
            print(f"响应结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return result


@pytest.mark.asyncio
async def test_edit_category():
    """测试编辑分类"""
    category_id = 1  # 使用默认的分类ID
    url = f"{BASE_URL}/spoken_classification/topic_category"
    data = {
        "category_id": category_id,
        "category_name": "教育类",
        "description": "教育相关话题分类",
        "order_num": 4
    }
    async with aiohttp.ClientSession() as session:
        async with session.put(url, headers=headers, json=data) as response:
            print(f"\n=== 测试编辑分类 {category_id} ===")
            print(f"状态码: {response.status}")
            result = await response.json()
            print(f"响应结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return result


@pytest.mark.asyncio
async def test_delete_category():
    """测试删除分类"""
    category_id = 1  # 使用默认的分类ID
    url = f"{BASE_URL}/spoken_classification/topic_category/{category_id}"
    async with aiohttp.ClientSession() as session:
        async with session.delete(url, headers=headers) as response:
            print(f"\n=== 测试删除分类 {category_id} ===")
            print(f"状态码: {response.status}")
            result = await response.json()
            print(f"响应结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return result


@pytest.mark.asyncio
async def test_batch_delete_category():
    """测试批量删除分类"""
    category_ids = "1,2,3"  # 使用默认的分类ID列表
    url = f"{BASE_URL}/spoken_classification/topic_category/{category_ids}"
    async with aiohttp.ClientSession() as session:
        async with session.delete(url, headers=headers) as response:
            print(f"\n=== 测试批量删除分类 {category_ids} ===")
            print(f"状态码: {response.status}")
            result = await response.json()
            print(f"响应结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return result


async def main():
    """主测试函数"""
    print("=== 开始测试话题分类管理API ===")

    # 1. 获取一级分类列表
    first_level_result = await test_get_first_level_categories()
    if first_level_result.get("code") == 200 and first_level_result.get("data"):
        first_category = first_level_result["data"][0]
        parent_id = first_category["category_id"]
    else:
        parent_id = 100  # 使用默认的一级分类ID

    # 2. 获取二级分类列表
    await test_get_second_level_categories(parent_id)

    # 3. 获取分类树结构
    await test_get_category_tree()

    # 4. 新增分类
    add_result = await test_add_category()
    if add_result.get("code") == 200 and add_result.get("data", {}).get("is_success"):
        # 这里需要根据实际情况获取新增的分类ID
        # 由于API没有返回新增的ID，这里暂时跳过编辑和删除测试
        pass

    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    asyncio.run(main())