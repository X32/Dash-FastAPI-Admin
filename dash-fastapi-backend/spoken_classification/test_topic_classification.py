import requests
import json

# 基础URL
BASE_URL = "http://localhost:8000/api/topic-classification"


class TopicClassificationTest:
    """话题分类管理模块测试类"""

    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        


    def test_create_classification(self, name, description="", parent_id=0, sort_order=0):
        """测试创建分类"""
        url = f"{self.base_url}/create"
        data = {
            "name": name,
            "description": description,
            "parent_id": parent_id,
            "sort_order": sort_order
        }
        response = self.session.post(url, json=data)
        print(f"创建分类 {name} 响应:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        print()
        return response.json()

    def test_update_classification(self, id, name, description="", parent_id=0, sort_order=0):
        """测试更新分类"""
        url = f"{self.base_url}/update"
        data = {
            "id": id,
            "name": name,
            "description": description,
            "parent_id": parent_id,
            "sort_order": sort_order
        }
        response = self.session.put(url, json=data)
        print(f"更新分类 {id} 响应:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        print()
        return response.json()

    def test_get_classification_by_id(self, id):
        """测试根据ID获取分类"""
        url = f"{self.base_url}/get/{id}"
        response = self.session.get(url)
        print(f"根据ID {id} 获取分类响应:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        print()
        return response.json()

    def test_get_first_level_classifications(self, page=1, page_size=10):
        """测试获取一级分类列表"""
        url = f"{self.base_url}/first-level?page={page}&page_size={page_size}"
        response = self.session.get(url)
        print(f"获取一级分类列表响应 (第{page}页, 每页{page_size}条):")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        print()
        return response.json()

    def test_get_second_level_classifications(self, parent_id, page=1, page_size=10):
        """测试获取指定一级分类下的二级分类列表"""
        url = f"{self.base_url}/second-level/{parent_id}?page={page}&page_size={page_size}"
        response = self.session.get(url)
        print(f"获取一级分类 {parent_id} 下的二级分类列表响应 (第{page}页, 每页{page_size}条):")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        print()
        return response.json()

    def test_get_classifications_by_parent_id(self, parent_id=0, page=1, page_size=10):
        """测试根据父ID获取分类列表"""
        url = f"{self.base_url}/list"
        data = {
            "parent_id": parent_id,
            "page": page,
            "page_size": page_size
        }
        response = self.session.post(url, json=data)
        print(f"根据父ID {parent_id} 获取分类列表响应 (第{page}页, 每页{page_size}条):")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        print()
        return response.json()

    def test_delete_classification(self, id):
        """测试删除分类"""
        url = f"{self.base_url}/delete/{id}"
        response = self.session.delete(url)
        print(f"删除分类 {id} 响应:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        print()
        return response.json()

    def test_batch_delete_classification(self, ids):
        """测试批量删除分类"""
        url = f"{self.base_url}/batch-delete"
        response = self.session.delete(url, json=ids)
        print(f"批量删除分类 {ids} 响应:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        print()
        return response.json()

    def run_all_tests(self):
        """运行所有测试用例"""
        print("=" * 50)
        print("开始测试话题分类管理模块")
        print("=" * 50)
        print()

        # 测试创建一级分类
        print("1. 测试创建一级分类")
        create_result1 = self.test_create_classification(
            name="测试一级分类7",
            description="这是测试一级分类7的描述",
            parent_id=0,
            sort_order=1
        )
        create_result2 = self.test_create_classification(
            name="测试一级分类8",
            description="这是测试一级分类8的描述",
            parent_id=0,
            sort_order=2
        )

        if create_result1.get("code") == 200 and create_result2.get("code") == 200:
            class1_id = create_result1.get("data", {}).get("id")
            class2_id = create_result2.get("data", {}).get("id")

            # 测试创建二级分类
            print("2. 测试创建二级分类")
            self.test_create_classification(
                name="测试二级分类1-1",
                description="这是测试二级分类1-1的描述",
                parent_id=class1_id,
                sort_order=1
            )
            self.test_create_classification(
                name="测试二级分类1-2",
                description="这是测试二级分类1-2的描述",
                parent_id=class1_id,
                sort_order=2
            )

            # 测试根据ID获取分类
            print("3. 测试根据ID获取分类")
            self.test_get_classification_by_id(class1_id)

            # 测试更新分类
            print("4. 测试更新分类")
            self.test_update_classification(
                id=class1_id,
                name="更新后的测试一级分类1",
                description="这是更新后的测试一级分类1的描述",
                parent_id=0,
                sort_order=3
            )

            # 测试获取一级分类列表
            print("5. 测试获取一级分类列表")
            self.test_get_first_level_classifications(page=1, page_size=10)

            # 测试获取指定一级分类下的二级分类列表
            print("6. 测试获取指定一级分类下的二级分类列表")
            self.test_get_second_level_classifications(parent_id=class1_id, page=1, page_size=10)

            # 测试根据父ID获取分类列表
            print("7. 测试根据父ID获取分类列表")
            self.test_get_classifications_by_parent_id(parent_id=0, page=1, page_size=10)
            self.test_get_classifications_by_parent_id(parent_id=class1_id, page=1, page_size=10)

            # 测试批量删除分类
            print("8. 测试批量删除分类")
            self.test_batch_delete_classification([class1_id, class2_id])
        else:
            print("创建分类失败，跳过后续测试")

        print("=" * 50)
        print("话题分类管理模块测试结束")
        print("=" * 50)


if __name__ == "__main__":
    # 创建测试实例
    test = TopicClassificationTest()
    
    # 运行所有测试用例
    test.run_all_tests()