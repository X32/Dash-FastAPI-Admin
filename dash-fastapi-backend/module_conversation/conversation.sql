-- ----------------------------
-- 会话管理模块数据库表结构
-- ----------------------------

-- ----------------------------
-- 1、会话表（conversations）
-- ----------------------------
drop table if exists conversations;
create table conversations (
    conversation_id bigint(20) not null auto_increment comment '会话ID',
    user_id bigint(20) not null comment '用户ID（外键）',
    title varchar(200) default '' comment '会话标题',
    status tinyint(1) default 1 comment '状态（1-有效 0-已删除）',
    create_time datetime default current_timestamp comment '创建时间',
    update_time datetime default current_timestamp on update current_timestamp comment '更新时间',
    primary key (conversation_id),
    key idx_user_id (user_id),
    key idx_status (status),
    key idx_update_time (update_time),
    constraint fk_conversations_user_id foreign key (user_id) references sys_user(user_id) on delete cascade
) engine=innodb comment='会话表';

-- ----------------------------
-- 2、消息表（messages）
-- ----------------------------
drop table if exists messages;
create table messages (
    message_id bigint(20) not null auto_increment comment '消息ID',
    conversation_id bigint(20) not null comment '会话ID（外键）',
    role varchar(20) not null comment '消息角色（user/assistant/examiner等）',
    seq int(11) not null default 0 comment '消息序号（用于排序）',
    create_time datetime default current_timestamp comment '创建时间',
    primary key (message_id),
    key idx_conversation_id (conversation_id),
    key idx_role (role),
    key idx_seq (seq),
    constraint fk_messages_conversation_id foreign key (conversation_id) references conversations(conversation_id) on delete cascade
) engine=innodb comment='消息表';

-- ----------------------------
-- 3、消息内容表（message_contents）
-- ----------------------------
drop table if exists message_contents;
create table message_contents (
    content_id bigint(20) not null auto_increment comment '内容ID',
    message_id bigint(20) not null comment '消息ID（外键）',
    content_type varchar(20) not null comment '内容类型（text/image_url）',
    text text comment '文本内容（当content_type=text时使用）',
    image_url varchar(500) default null comment '图片URL（当content_type=image_url时使用）',
    seq int(11) not null default 0 comment '内容序号（同一消息的多部分内容排序）',
    create_time datetime default current_timestamp comment '创建时间',
    primary key (content_id),
    key idx_message_id (message_id),
    key idx_content_type (content_type),
    constraint fk_message_contents_message_id foreign key (message_id) references messages(message_id) on delete cascade
) engine=innodb comment='消息内容表';

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