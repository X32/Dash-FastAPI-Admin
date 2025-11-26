-- ----------------------------
-- 口语考试话题分类表
-- ----------------------------
drop table if exists sys_topic_category;
create table sys_topic_category (
  category_id       bigint(20)      not null auto_increment    comment '分类id',
  parent_id         bigint(20)      default 0                    comment '父分类id',
  category_name     varchar(50)     not null                     comment '分类名称',
  category_desc     varchar(500)    default ''                   comment '分类描述',
  order_num         int(4)          default 0                    comment '显示顺序',
  status            char(1)         default '0'                  comment '分类状态（0正常 1停用）',
  del_flag          char(1)         default '0'                  comment '删除标志（0代表存在 2代表删除）',
  create_by         varchar(64)     default ''                   comment '创建者',
  create_time       datetime                                     comment '创建时间',
  update_by         varchar(64)     default ''                   comment '更新者',
  update_time       datetime                                     comment '更新时间',
  remark            varchar(500)    default ''                   comment '备注',
  primary key (category_id)
) engine=innodb auto_increment=1 comment = '口语考试话题分类表';

-- ----------------------------
-- 初始化-话题分类表数据
-- ----------------------------
insert into sys_topic_category values(1, 0, '日常交流', '日常生活相关的话题，如购物、问路、点餐等', 1, '0', '0', 'admin', sysdate(), '', null, '');
insert into sys_topic_category values(2, 0, '学习教育', '学习和教育相关的话题，如课程讨论、学习方法等', 2, '0', '0', 'admin', sysdate(), '', null, '');
insert into sys_topic_category values(3, 0, '工作职场', '工作和职场相关的话题，如面试、工作汇报等', 3, '0', '0', 'admin', sysdate(), '', null, '');
insert into sys_topic_category values(4, 1, '购物消费', '购物、消费相关话题', 1, '0', '0', 'admin', sysdate(), '', null, '');
insert into sys_topic_category values(5, 1, '交通出行', '交通、出行相关话题', 2, '0', '0', 'admin', sysdate(), '', null, '');
insert into sys_topic_category values(6, 2, '课程学习', '课程内容讨论', 1, '0', '0', 'admin', sysdate(), '', null, '');

-- ----------------------------
-- 口语考试话题表（用于验证分类删除时的关联检查）
-- ----------------------------
drop table if exists sys_speaking_topic;
create table sys_speaking_topic (
  topic_id          bigint(20)      not null auto_increment    comment '话题id',
  category_id       bigint(20)      not null                     comment '分类id',
  topic_title       varchar(100)    not null                     comment '话题标题',
  topic_content     text                                         comment '话题内容',
  difficulty_level  char(1)         default '1'                  comment '难度等级（1简单 2中等 3困难）',
  status            char(1)         default '0'                  comment '话题状态（0正常 1停用）',
  del_flag          char(1)         default '0'                  comment '删除标志（0代表存在 2代表删除）',
  create_by         varchar(64)     default ''                   comment '创建者',
  create_time       datetime                                     comment '创建时间',
  update_by         varchar(64)     default ''                   comment '更新者',
  update_time       datetime                                     comment '更新时间',
  remark            varchar(500)    default ''                   comment '备注',
  primary key (topic_id),
  key idx_category_id (category_id)
) engine=innodb auto_increment=1 comment = '口语考试话题表';

-- ----------------------------
-- 初始化-话题表数据（用于测试）
-- ----------------------------
insert into sys_speaking_topic values(1, 4, '超市购物经历', '请描述一次你在超市购物的经历', '超市购物、消费体验', '1', '0', '0', 'admin', sysdate(), '', null, '');
insert into sys_speaking_topic values(2, 5, '问路指路', '请描述如何向陌生人问路', '交通出行、问路', '1', '0', '0', 'admin', sysdate(), '', null, '');
insert into sys_speaking_topic values(3, 6, '最喜欢的课程', '请介绍你最喜欢的一门课程', '课程学习、教育', '1', '0', '0', 'admin', sysdate(), '', null, '');