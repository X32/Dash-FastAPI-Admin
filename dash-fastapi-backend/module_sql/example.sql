-- 示例SQL文件
-- 用于测试批量执行功能

-- 创建测试表
CREATE TABLE IF NOT EXISTS example_table (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL COMMENT '名称',
    description TEXT COMMENT '描述',
    status TINYINT DEFAULT 1 COMMENT '状态：1-启用，0-禁用',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='示例表';

-- 插入测试数据
INSERT INTO example_table (name, description, status) VALUES 
('测试项目1', '这是第一个测试项目', 1),
('测试项目2', '这是第二个测试项目', 1),
('测试项目3', '这是第三个测试项目', 0);

-- 查询数据
SELECT * FROM example_table WHERE status = 1;

-- 更新数据
UPDATE example_table SET description = '更新后的描述' WHERE name = '测试项目1';

-- 创建索引
CREATE INDEX idx_status ON example_table(status);
CREATE INDEX idx_created_at ON example_table(created_at);