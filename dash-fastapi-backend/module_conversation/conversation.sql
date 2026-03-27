-- ----------------------------
-- 会话管理模块数据库表结构
-- ----------------------------

-- ----------------------------
-- 1、会话表（conversations）
-- ----------------------------


-- ----------------------------
-- 初始化测试数据
-- ----------------------------

-- 插入测试会话数据
insert into conversations (conversation_id, user_id, title, status) values
(1, 1, '测试会话1 - 关于Python编程', 1),
(2, 1, '测试会话2 - 关于数据库设计', 1),
(3, 2, '测试会话3 - 关于前端开发', 1);

-- 插入测试消息数据
insert into messages (message_id, conversation_id, role, seq) values
(1, 1, 'user', 1),
(2, 1, 'assistant', 2),
(3, 1, 'user', 3),
(4, 1, 'assistant', 4),
(5, 2, 'user', 1),
(6, 2, 'assistant', 2),
(7, 3, 'user', 1),
(8, 3, 'assistant', 2);

-- 插入测试消息内容数据
insert into message_contents (message_id, content_type, text, seq) values
(1, 'text', '请帮我写一个Python函数，实现斐波那契数列', 1),
(2, 'text', '当然可以！以下是一个实现斐波那契数列的Python函数：\n\ndef fibonacci(n):\n    if n <= 0:\n        return []\n    elif n == 1:\n        return [0]\n    elif n == 2:\n        return [0, 1]\n    else:\n        fib = [0, 1]\n        for i in range(2, n):\n            fib.append(fib[i-1] + fib[i-2])\n        return fib\n\n# 使用示例\nprint(fibonacci(10))', 1),
(3, 'text', '这个函数很好！能否再添加一个递归版本的实现？', 1),
(4, 'text', '当然可以！以下是递归版本的斐波那契数列实现：\n\ndef fibonacci_recursive(n):\n    if n <= 0:\n        return []\n    elif n == 1:\n        return [0]\n    elif n == 2:\n        return [0, 1]\n    else:\n        result = fibonacci_recursive(n-1)\n        result.append(result[-1] + result[-2])\n        return result\n\n# 使用示例\nprint(fibonacci_recursive(10))\n\n注意：递归版本在处理大数时可能会导致栈溢出，建议使用迭代版本。', 1),
(5, 'text', '如何设计一个高性能的数据库表结构？', 1),
(6, 'text', '设计高性能数据库表结构需要考虑以下几个方面：\n\n1. **选择合适的数据类型**：\n   - 使用最合适的数据类型，避免过大\n   - 使用INT而不是BIGINT，如果可能\n   - 使用VARCHAR而不是TEXT，如果可能\n\n2. **添加适当的索引**：\n   - 为经常查询的列添加索引\n   - 避免过多的索引，影响写入性能\n   - 考虑复合索引的顺序\n\n3. **规范化与反规范化平衡**：\n   - 适当的规范化减少数据冗余\n   - 适度的反规范化提高查询性能\n\n4. **分区表**：\n   - 大表考虑分区\n   - 按时间或ID范围分区\n\n5. **字符集选择**：\n   - 使用utf8mb4而不是utf8\n   - 考虑存储需求', 1),
(7, 'text', 'React和Vue.js哪个更适合大型项目？', 1),
(8, 'text', 'React和Vue.js都是优秀的前端框架，各有优势：\n\n**React的优势：**\n- 更大的生态系统和社区\n- 更多的第三方库和工具\n- 更强的TypeScript支持\n- Facebook支持，稳定性高\n\n**Vue.js的优势：**\n- 学习曲线更平缓\n- 文档更友好\n- 模板语法更直观\n- 体积更小\n\n**大型项目建议：**\n- 如果团队有经验，两者都适合\n- React生态系统更成熟\n- Vue 3的Composition API提供了类似React的灵活性\n- 考虑团队技能栈和项目需求', 1);