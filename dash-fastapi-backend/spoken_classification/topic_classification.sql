-- 话题分类表
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

-- 插入示例数据
INSERT INTO topic_classification (name, description, parent_id, sort_order) VALUES
('科技', '科技相关话题', 0, 1),
('体育', '体育相关话题', 0, 2),
('娱乐', '娱乐相关话题', 0, 3),
('人工智能', '人工智能技术话题', 1, 1),
('互联网', '互联网行业话题', 1, 2),
('足球', '足球相关话题', 2, 1),
('篮球', '篮球相关话题', 2, 2),
('电影', '电影相关话题', 3, 1),
('音乐', '音乐相关话题', 3, 2);