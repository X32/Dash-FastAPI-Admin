#!/bin/bash

# 话题分类管理模块接口测试脚本

# 基础URL
BASE_URL="http://localhost:9019"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试结果统计
PASSED=0
FAILED=0

# 打印测试结果
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((FAILED++))
    fi
}

# 测试接口
# 参数：1-接口名称，2-HTTP方法，3-接口路径，4-请求体（可选）
test_api() {
    local api_name=$1
    local method=$2
    local path=$3
    local request_body=$4

    echo -e "\n${YELLOW}测试接口：${api_name}${NC}"
    echo -e "方法：${method}"
    echo -e "路径：${path}"
    
    if [ "${method}" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "${BASE_URL}${path}")
    elif [ "${method}" = "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST -H "Content-Type: application/json" -d "${request_body}" "${BASE_URL}${path}")
    elif [ "${method}" = "PUT" ]; then
        response=$(curl -s -w "\n%{http_code}" -X PUT -H "Content-Type: application/json" -d "${request_body}" "${BASE_URL}${path}")
    elif [ "${method}" = "DELETE" ]; then
        response=$(curl -s -w "\n%{http_code}" -X DELETE "${BASE_URL}${path}")
    fi

    # 分离响应数据和状态码
    http_code=$(echo "${response}" | tail -n 1)
    response_data=$(echo "${response}" | head -n -1)

    echo -e "响应码：${http_code}"
    echo -e "响应数据：${response_data}"

    # 检查响应码是否为200
    if [ "${http_code}" -eq 200 ]; then
        # 检查响应数据中的code是否为0
        if echo "${response_data}" | grep -q "\"code\": 0"; then
            print_result 0
        else
            print_result 1
        fi
    else
        print_result 1
    fi
}

# 主函数
main() {
    echo -e "${YELLOW}开始测试话题分类管理模块接口${NC}"
    echo -e "基础URL：${BASE_URL}"

    # 1. 获取所有一级分类
    test_api "获取所有一级分类" "GET" "/topic-category/first-level"

    # 2. 获取指定一级分类下的所有二级分类（假设一级分类ID为1）
    test_api "获取指定一级分类下的所有二级分类" "GET" "/topic-category/second-level/1"

    # 3. 根据ID获取分类（假设分类ID为1）
    test_api "根据ID获取分类" "GET" "/topic-category/1"

    # 4. 创建分类（创建一个新的二级分类，父分类ID为1）
    request_body='{"category_name": "测试分类", "category_desc": "测试分类描述", "parent_id": 1, "sort_order": 1}'
    test_api "创建分类" "POST" "/topic-category/" "${request_body}"

    # 5. 更新分类（假设新创建的分类ID为100）
    request_body='{"category_name": "更新后的测试分类", "category_desc": "更新后的测试分类描述", "sort_order": 2}'
    test_api "更新分类" "PUT" "/topic-category/100" "${request_body}"

    # 6. 删除分类（假设要删除的分类ID为100）
    test_api "删除分类" "DELETE" "/topic-category/100"

    # 打印测试结果统计
    echo -e "\n${YELLOW}测试结果统计${NC}"
    echo -e "通过：${PASSED}"
    echo -e "失败：${FAILED}"

    if [ ${FAILED} -eq 0 ]; then
        echo -e "${GREEN}所有测试通过！${NC}"
    else
        echo -e "${RED}有 ${FAILED} 个测试失败！${NC}"
    fi
}

# 执行主函数
main