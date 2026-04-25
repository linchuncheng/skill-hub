-- migrate:up
-- 1. 租户数据
INSERT INTO sys_tenant (id, tenant_code, tenant_name, logo, contact_name, contact_phone, status, created_at, updated_at)
VALUES
    (0, 'default', '多租户管理平台', '', '超级管理员', '', 1, NOW(), NOW());

-- 2. 菜单数据
INSERT INTO sys_menu (id, parent_id, menu_name, menu_path, component, icon, sort, visible, permission_code, status, created_at)
VALUES
    -- 系统管理 (排序: 100)
    (1, 0, '系统管理', '/system', NULL, 'setting', 100, 1, NULL, 1, NOW()),
    (11, 1, '租户管理', '/system/tenant', 'pages/tenant', 'cluster', 1, 1, 'platform:tenant:list', 1, NOW()),
    (12, 1, '用户管理', '/system/user', 'pages/user', 'user', 2, 1, 'platform:user:list', 1, NOW()),
    (13, 1, '菜单管理', '/system/menu', 'pages/menu', 'menu', 3, 1, 'platform:menu:list', 1, NOW()),
    (21, 1, '角色管理', '/system/role', 'modules/system/role', 'safety-certificate', 4, 1, 'platform:role:list', 1, NOW());

-- 3. 权限数据 - 模块级权限
INSERT INTO sys_permission (id, parent_id, permission_code, permission_name, resource_type, sort, status, created_at)
VALUES
    (100, 0, 'platform:dashboard:view', '首页查看', 'MENU', 0, 1, NOW()),
    (22, 0, 'platform:tenant', '租户管理', 'MENU', 1, 1, NOW()),
    (23, 0, 'platform:user', '用户管理', 'MENU', 2, 1, NOW()),
    (24, 0, 'platform:role', '角色管理', 'MENU', 3, 1, NOW()),
    (25, 0, 'platform:menu', '菜单管理', 'MENU', 4, 1, NOW()),
    (101, 0, 'platform:test:view', '权限测试查看', 'MENU', 999, 1, NOW());

-- 4. 权限数据 - 按钮级权限
INSERT INTO sys_permission (id, parent_id, permission_code, permission_name, resource_type, sort, status, created_at)
VALUES
    -- 租户管理权限
    (1, 22, 'platform:tenant:list', '租户查询', 'MENU', 1, 1, NOW()),
    (2, 22, 'platform:tenant:create', '租户新增', 'BUTTON', 2, 1, NOW()),
    (17, 22, 'platform:tenant:edit', '租户编辑', 'BUTTON', 3, 1, NOW()),
    (18, 22, 'platform:tenant:delete', '租户删除', 'BUTTON', 4, 1, NOW()),
    (19, 22, 'platform:tenant:export', '租户导出', 'BUTTON', 5, 1, NOW()),
    -- 用户管理权限
    (3, 23, 'platform:user:list', '用户查询', 'MENU', 1, 1, NOW()),
    (7, 23, 'platform:user:create', '用户新增', 'BUTTON', 2, 1, NOW()),
    (8, 23, 'platform:user:edit', '用户编辑', 'BUTTON', 3, 1, NOW()),
    (9, 23, 'platform:user:delete', '用户删除', 'BUTTON', 4, 1, NOW()),
    (10, 23, 'platform:user:export', '用户导出', 'BUTTON', 5, 1, NOW()),
    (27, 23, 'platform:user:assign-role', '用户角色分配', 'BUTTON', 6, 1, NOW()),
    (28, 23, 'platform:user:reset-password', '用户重置密码', 'BUTTON', 7, 1, NOW()),
    -- 角色管理权限
    (6, 24, 'platform:role:list', '角色查询', 'MENU', 1, 1, NOW()),
    (14, 24, 'platform:role:create', '角色新增', 'BUTTON', 2, 1, NOW()),
    (15, 24, 'platform:role:edit', '角色编辑', 'BUTTON', 3, 1, NOW()),
    (16, 24, 'platform:role:delete', '角色删除', 'BUTTON', 4, 1, NOW()),
    (20, 24, 'platform:role:assign-permission', '角色权限分配', 'BUTTON', 5, 1, NOW()),
    (21, 24, 'platform:role:assign-menu', '角色菜单分配', 'BUTTON', 6, 1, NOW()),
    -- 菜单管理权限
    (5, 25, 'platform:menu:list', '菜单查询', 'MENU', 1, 1, NOW()),
    (11, 25, 'platform:menu:create', '菜单新增', 'BUTTON', 2, 1, NOW()),
    (12, 25, 'platform:menu:update', '菜单编辑', 'BUTTON', 3, 1, NOW()),
    (13, 25, 'platform:menu:delete', '菜单删除', 'BUTTON', 4, 1, NOW());

-- 5. 角色数据
INSERT INTO sys_role (id, tenant_id, role_code, role_name, sort, status, remark, created_at, updated_at)
VALUES
    (1, '0', 'SUPER_ADMIN', '超级管理员', 1, 1, '平台最高权限角色,拥有所有菜单和权限', NOW(), NOW());

-- 6. 用户数据(super密码: 123456)
INSERT INTO sys_user (id, tenant_id, username, password, real_name, avatar, phone, email, remark, status, tenant_type, created_at, updated_at)
VALUES
    (1, '0', 'super', '$2a$10$ldCOp30.Vefq5fGWWlrpDeSHBNLR0HG.zBoUMsgUsHuM1WtndHVF2', '超级管理员', '', '13800000001', 'super@fengqun.com', '超级管理员账号', 1, 'PLATFORM', NOW(), NOW());

-- 7. 用户角色关联
INSERT INTO sys_user_role (id, tenant_id, user_id, role_id, created_at)
VALUES
    (1, '0', 1, 1, NOW());

-- 8. 角色菜单关联(SUPER_ADMIN 拥有所有菜单)
INSERT INTO sys_role_menu (id, tenant_id, role_id, menu_id, created_at)
VALUES
    -- 系统管理菜单
    (1, '0', 1, 1, NOW()),
    (2, '0', 1, 11, NOW()),
    (3, '0', 1, 12, NOW()),
    (4, '0', 1, 13, NOW()),
    (5, '0', 1, 21, NOW());

-- 9. 角色权限关联(SUPER_ADMIN 拥有所有权限)
INSERT INTO sys_role_permission (id, tenant_id, role_id, permission_id, created_at)
VALUES
    -- 平台基础权限
    (1, '0', 1, 100, NOW()),
    (2, '0', 1, 22, NOW()),
    (3, '0', 1, 1, NOW()),
    (4, '0', 1, 2, NOW()),
    (5, '0', 1, 17, NOW()),
    (6, '0', 1, 18, NOW()),
    (7, '0', 1, 19, NOW()),
    (8, '0', 1, 23, NOW()),
    (9, '0', 1, 3, NOW()),
    (10, '0', 1, 7, NOW()),
    (11, '0', 1, 8, NOW()),
    (12, '0', 1, 9, NOW()),
    (13, '0', 1, 10, NOW()),
    (14, '0', 1, 27, NOW()),
    (15, '0', 1, 28, NOW()),
    (16, '0', 1, 24, NOW()),
    (17, '0', 1, 6, NOW()),
    (18, '0', 1, 14, NOW()),
    (19, '0', 1, 15, NOW()),
    (20, '0', 1, 16, NOW()),
    (21, '0', 1, 20, NOW()),
    (22, '0', 1, 21, NOW()),
    (23, '0', 1, 25, NOW()),
    (24, '0', 1, 5, NOW()),
    (25, '0', 1, 11, NOW()),
    (26, '0', 1, 12, NOW()),
    (27, '0', 1, 13, NOW()),
    (28, '0', 1, 101, NOW());

-- migrate:down
-- TODO: 添加回滚 SQL（如 DROP TABLE、ALTER TABLE DROP COLUMN 等）
