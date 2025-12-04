-- 话题分类表
CREATE TABLE IF NOT EXISTS topic_category (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '分类ID',
    category_name VARCHAR(50) NOT NULL COMMENT '分类名称',
    category_desc VARCHAR(200) DEFAULT '' COMMENT '分类描述',
    parent_id BIGINT DEFAULT 0 COMMENT '父分类ID，0表示一级分类',
    sort_order INT DEFAULT 0 COMMENT '排序',
    is_deleted TINYINT DEFAULT 0 COMMENT '是否删除，0未删除，1已删除',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_name_parent (category_name, parent_id, is_deleted) COMMENT '同层级分类名称唯一'
) COMMENT '话题分类表';

-- 插入一级分类示例数据
INSERT INTO topic_category (category_name, category_desc, parent_id, sort_order) VALUES
('科技', '科技相关话题', 0, 1),
('娱乐', '娱乐相关话题', 0, 2),
('体育', '体育相关话题', 0, 3),
('财经', '财经相关话题', 0, 4),
('教育', '教育相关话题', 0, 5);

-- 插入二级分类示例数据
INSERT INTO topic_category (category_name, category_desc, parent_id, sort_order) VALUES
('人工智能', '人工智能相关话题', 1, 1),
('云计算', '云计算相关话题', 1, 2),
('大数据', '大数据相关话题', 1, 3),
('电影', '电影相关话题', 2, 1),
('音乐', '音乐相关话题', 2, 2),
('综艺', '综艺相关话题', 2, 3),
('足球', '足球相关话题', 3, 1),
('篮球', '篮球相关话题', 3, 2),
('网球', '网球相关话题', 3, 3),
('股票', '股票相关话题', 4, 1),
('基金', '基金相关话题', 4, 2),
('债券', '债券相关话题', 4, 3),
('基础教育', '基础教育相关话题', 5, 1),
('高等教育', '高等教育相关话题', 5, 2),
('职业教育', '职业教育相关话题', 5, 3);