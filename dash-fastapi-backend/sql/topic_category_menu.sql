-- 话题分类管理菜单
insert into sys_menu values('1070', '话题分类管理', '1',   '8', 'topicCategory', 'system.topicCategory', '', '', 1, 0, 'C', '0', '0', 'system:topicCategory:list',        'antd-tags',          'admin', sysdate(), '', null, '话题分类管理菜单');

-- 话题分类管理按钮
insert into sys_menu values('1071', '话题分类查询', '1070', '1',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:topicCategory:query',          '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1072', '话题分类新增', '1070', '2',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:topicCategory:add',            '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1073', '话题分类修改', '1070', '3',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:topicCategory:edit',           '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('1074', '话题分类删除', '1070', '4',  '', '', '', '', 1, 0, 'F', '0', '0', 'system:topicCategory:remove',         '#', 'admin', sysdate(), '', null, '');

-- 为普通角色添加话题分类管理权限
insert into sys_role_menu values ('2', '1070');
insert into sys_role_menu values ('2', '1071');
insert into sys_role_menu values ('2', '1072');
insert into sys_role_menu values ('2', '1073');
insert into sys_role_menu values ('2', '1074');