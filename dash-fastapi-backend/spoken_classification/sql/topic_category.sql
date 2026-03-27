-- ----------------------------
-- 话题分类表
-- ----------------------------
drop table if exists topic_category;
create table topic_category (
  category_id       bigint(20)      not null auto_increment    comment '分类ID',
  parent_id         bigint(20)      default 0                  comment '父分类ID',
  category_name     varchar(50)     not null                   comment '分类名称',
  description       varchar(200)    default ''                 comment '分类描述',
  order_num         int(4)          default 0                  comment '显示顺序',
  del_flag          char(1)         default '0'                comment '删除标志（0代表存在 2代表删除）',
  create_by         varchar(64)     default ''                 comment '创建者',
  create_time       datetime                                   comment '创建时间',
  update_by         varchar(64)     default ''                 comment '更新者',
  update_time       datetime                                   comment '更新时间',
  primary key (category_id),
  unique key uk_parent_name (parent_id, category_name) comment '同一父分类下名称唯一'
) engine=innodb auto_increment=100 comment = '话题分类表';

-- ----------------------------
-- 初始化-话题分类表数据
-- ----------------------------
insert into topic_category values(100,  0, '科技', '科技相关话题分类', 1, '0', 'admin', sysdate(), '', null);
insert into topic_category values(101,  0, '生活', '生活相关话题分类', 2, '0', 'admin', sysdate(), '', null);
insert into topic_category values(102,  0, '娱乐', '娱乐相关话题分类', 3, '0', 'admin', sysdate(), '', null);
insert into topic_category values(103,  100, '人工智能', 'AI相关话题', 1, '0', 'admin', sysdate(), '', null);
insert into topic_category values(104,  100, '互联网', '互联网技术话题', 2, '0', 'admin', sysdate(), '', null);
insert into topic_category values(105,  101, '美食', '美食相关话题', 1, '0', 'admin', sysdate(), '', null);
insert into topic_category values(106,  101, '旅游', '旅游相关话题', 2, '0', 'admin', sysdate(), '', null);
insert into topic_category values(107,  102, '电影', '电影相关话题', 1, '0', 'admin', sysdate(), '', null);
insert into topic_category values(108,  102, '音乐', '音乐相关话题', 2, '0', 'admin', sysdate(), '', null);