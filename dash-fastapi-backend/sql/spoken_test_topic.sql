-- ----------------------------
-- 口语考试话题分类表
-- ----------------------------
drop table if exists sys_spoken_topic;
drop table if exists sys_topic_category;
create table sys_topic_category (
  category_id       bigint(20)      not null auto_increment    comment '分类ID',
  parent_id         bigint(20)      default 0                  comment '父分类ID',
  category_name     varchar(100)    not null                   comment '分类名称',
  category_desc     varchar(500)    default ''                 comment '分类描述',
  order_num         int(4)          default 0                  comment '显示顺序',
  status            char(1)         default '0'                comment '分类状态（0正常 1停用）',
  del_flag          char(1)         default '0'                comment '删除标志（0代表存在 2代表删除）',
  create_by         varchar(64)     default ''                 comment '创建者',
  create_time       datetime                                   comment '创建时间',
  update_by         varchar(64)     default ''                 comment '更新者',
  update_time       datetime                                   comment '更新时间',
  remark            varchar(500)    default ''                 comment '备注',
  primary key (category_id)
) engine=innodb auto_increment=1000 comment = '口语考试话题分类表';

-- ----------------------------
-- 口语考试话题表
-- ----------------------------
create table sys_spoken_topic (
  topic_id          bigint(20)      not null auto_increment    comment '话题ID',
  category_id       bigint(20)      not null                   comment '分类ID',
  topic_name        varchar(200)    not null                   comment '话题名称',
  topic_content     text            not null                   comment '话题内容',
  difficulty_level  varchar(20)     default '中等'             comment '难度级别（简单、中等、困难）',
  status            char(1)         default '0'                comment '话题状态（0正常 1停用）',
  del_flag          char(1)         default '0'                comment '删除标志（0代表存在 2代表删除）',
  create_by         varchar(64)     default ''                 comment '创建者',
  create_time       datetime                                   comment '创建时间',
  update_by         varchar(64)     default ''                 comment '更新者',
  update_time       datetime                                   comment '更新时间',
  remark            varchar(500)    default ''                 comment '备注',
  primary key (topic_id),
  foreign key (category_id) references sys_topic_category(category_id) on delete restrict
) engine=innodb auto_increment=1000 comment = '口语考试话题表';

-- ----------------------------
-- 初始化菜单数据
-- ----------------------------
-- 二级菜单：话题分类管理
insert ignore into sys_menu values('118', '话题分类管理', '1',   '9', 'topicCategory', 'system.topicCategory', '', '', 1, 0, 'C', '0', '0', 'system:topicCategory:list', 'antd-book', 'admin', sysdate(), '', null, '话题分类管理菜单');

-- 话题分类管理按钮
insert ignore into sys_menu values('1100', '分类查询', '118', '1',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:topicCategory:query', '#', 'admin', sysdate(), '', null, '');
insert ignore into sys_menu values('1101', '分类新增', '118', '2',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:topicCategory:add', '#', 'admin', sysdate(), '', null, '');
insert ignore into sys_menu values('1102', '分类修改', '118', '3',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:topicCategory:edit', '#', 'admin', sysdate(), '', null, '');
insert ignore into sys_menu values('1103', '分类删除', '118', '4',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:topicCategory:remove', '#', 'admin', sysdate(), '', null, '');

-- 二级菜单：话题管理
insert ignore into sys_menu values('119', '话题管理', '1',   '10', 'spokenTopic', 'system.spokenTopic', '', '', 1, 0, 'C', '0', '0', 'system:spokenTopic:list', 'antd-file-text', 'admin', sysdate(), '', null, '话题管理菜单');

-- 话题管理按钮
insert ignore into sys_menu values('1104', '话题查询', '119', '1',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:spokenTopic:query', '#', 'admin', sysdate(), '', null, '');
insert ignore into sys_menu values('1105', '话题新增', '119', '2',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:spokenTopic:add', '#', 'admin', sysdate(), '', null, '');
insert ignore into sys_menu values('1106', '话题修改', '119', '3',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:spokenTopic:edit', '#', 'admin', sysdate(), '', null, '');
insert ignore into sys_menu values('1107', '话题删除', '119', '4',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:spokenTopic:remove', '#', 'admin', sysdate(), '', null, '');
