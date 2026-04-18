-- migrate:up
-- 租户表(平台级)
CREATE TABLE IF NOT EXISTS sys_tenant (
    id BIGINT NOT NULL PRIMARY KEY COMMENT '主键(雪花ID)',
    tenant_code VARCHAR(32) NOT NULL UNIQUE COMMENT '租户编码',
    tenant_name VARCHAR(100) NOT NULL COMMENT '租户名称',
    logo VARCHAR(255) COMMENT '租户Logo图片链接',
    contact_name VARCHAR(50) COMMENT '联系人',
    contact_phone VARCHAR(20) COMMENT '联系电话',
    status TINYINT(1) NOT NULL DEFAULT 1 COMMENT '状态:1=启用,0=禁用',
    created_by BIGINT COMMENT '创建人',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by BIGINT COMMENT '更新人',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted TINYINT(1) NOT NULL DEFAULT 0 COMMENT '逻辑删除:0=未删除,1=已删除',
    INDEX idx_tenant_code (tenant_code),
    INDEX idx_status (status)
) ENGINE=InnoDB COMMENT='租户表';

-- 用户表(平台级和租户级)
CREATE TABLE IF NOT EXISTS sys_user (
    id BIGINT NOT NULL PRIMARY KEY COMMENT '主键(雪花ID)',
    tenant_id VARCHAR(32) NOT NULL COMMENT '租户ID:0=平台用户',
    username VARCHAR(50) NOT NULL COMMENT '用户名',
    password VARCHAR(100) NOT NULL COMMENT '密码(BCrypt)',
    real_name VARCHAR(50) COMMENT '真实姓名',
    avatar VARCHAR(255) COMMENT '头像图片链接',
    phone VARCHAR(20) COMMENT '手机号',
    email VARCHAR(100) COMMENT '邮箱',
    remark VARCHAR(500) COMMENT '备注',
    status TINYINT(1) NOT NULL DEFAULT 1 COMMENT '状态:1=启用,0=禁用',
    tenant_type VARCHAR(20) NOT NULL COMMENT '用户类型:PLATFORM/TENANT_ADMIN/TENANT_USER',
    created_by BIGINT COMMENT '创建人',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by BIGINT COMMENT '更新人',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted TINYINT(1) NOT NULL DEFAULT 0 COMMENT '逻辑删除:0=未删除,1=已删除',
    UNIQUE KEY uk_tenant_username (tenant_id, username),
    INDEX idx_tenant_id (tenant_id),
    INDEX idx_username (username)
) ENGINE=InnoDB COMMENT='用户表';

-- 角色表(平台角色 tenant_id='0',租户角色按 tenant_id 隔离)
CREATE TABLE IF NOT EXISTS sys_role (
    id BIGINT NOT NULL PRIMARY KEY COMMENT '主键(雪花ID)',
    tenant_id VARCHAR(32) NOT NULL COMMENT '租户ID:0=平台角色',
    role_code VARCHAR(50) NOT NULL COMMENT '角色编码',
    role_name VARCHAR(100) NOT NULL COMMENT '角色名称',
    sort INT NOT NULL DEFAULT 0 COMMENT '排序',
    status TINYINT(1) NOT NULL DEFAULT 1 COMMENT '状态:1=启用,0=禁用',
    remark VARCHAR(500) COMMENT '备注',
    created_by BIGINT COMMENT '创建人',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by BIGINT COMMENT '更新人',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted TINYINT(1) NOT NULL DEFAULT 0 COMMENT '逻辑删除:0=未删除,1=已删除',
    UNIQUE KEY uk_tenant_role_code (tenant_id, role_code),
    INDEX idx_tenant_id (tenant_id)
) ENGINE=InnoDB COMMENT='角色表';

-- 用户角色关联表
CREATE TABLE IF NOT EXISTS sys_user_role (
    id BIGINT NOT NULL PRIMARY KEY COMMENT '主键(雪花ID)',
    tenant_id VARCHAR(32) NOT NULL DEFAULT '0' COMMENT '租户ID',
    user_id BIGINT NOT NULL COMMENT '用户ID',
    role_id BIGINT NOT NULL COMMENT '角色ID',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_tenant_id (tenant_id),
    INDEX idx_user_id (user_id),
    INDEX idx_role_id (role_id)
) ENGINE=InnoDB COMMENT='用户角色关联表';

-- 权限表(操作级权限码,全局数据,无 tenant_id)
CREATE TABLE IF NOT EXISTS sys_permission (
    id BIGINT NOT NULL PRIMARY KEY COMMENT '主键(雪花ID)',
    parent_id BIGINT NOT NULL DEFAULT 0 COMMENT '父权限ID:0=顶级权限',
    permission_code VARCHAR(100) NOT NULL UNIQUE COMMENT '权限码',
    permission_name VARCHAR(100) NOT NULL COMMENT '权限名称',
    resource_type VARCHAR(20) NOT NULL COMMENT '资源类型:MENU/BUTTON',
    sort INT NOT NULL DEFAULT 0 COMMENT '排序',
    status TINYINT(1) NOT NULL DEFAULT 1 COMMENT '状态:1=启用,0=禁用',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted TINYINT(1) NOT NULL DEFAULT 0 COMMENT '逻辑删除:0=未删除,1=已删除',
    INDEX idx_parent_id (parent_id),
    INDEX idx_permission_code (permission_code)
) ENGINE=InnoDB COMMENT='权限表';

-- 角色权限关联表
CREATE TABLE IF NOT EXISTS sys_role_permission (
    id BIGINT NOT NULL PRIMARY KEY COMMENT '主键(雪花ID)',
    tenant_id VARCHAR(32) NOT NULL DEFAULT '0' COMMENT '租户ID',
    role_id BIGINT NOT NULL COMMENT '角色ID',
    permission_id BIGINT NOT NULL COMMENT '权限ID',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_tenant_id (tenant_id),
    INDEX idx_role_id (role_id),
    INDEX idx_permission_id (permission_id)
) ENGINE=InnoDB COMMENT='角色权限关联表';

-- 菜单表(树形结构,全局数据,无 tenant_id)
CREATE TABLE IF NOT EXISTS sys_menu (
    id BIGINT NOT NULL PRIMARY KEY COMMENT '主键(雪花ID)',
    parent_id BIGINT NOT NULL DEFAULT 0 COMMENT '父菜单ID:0=顶级菜单',
    menu_name VARCHAR(100) NOT NULL COMMENT '菜单名称',
    menu_path VARCHAR(200) COMMENT '路由路径',
    component VARCHAR(200) COMMENT '前端组件路径',
    icon VARCHAR(50) COMMENT '图标',
    sort INT NOT NULL DEFAULT 0 COMMENT '排序',
    visible TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否可见:1=可见,0=隐藏',
    permission_code VARCHAR(100) COMMENT '权限码(可选)',
    status TINYINT(1) NOT NULL DEFAULT 1 COMMENT '状态:1=启用,0=禁用',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted TINYINT(1) NOT NULL DEFAULT 0 COMMENT '逻辑删除:0=未删除,1=已删除',
    INDEX idx_parent_id (parent_id),
    INDEX idx_sort (sort)
) ENGINE=InnoDB COMMENT='菜单表';

-- 角色菜单关联表
CREATE TABLE IF NOT EXISTS sys_role_menu (
    id BIGINT NOT NULL PRIMARY KEY COMMENT '主键(雪花ID)',
    tenant_id VARCHAR(32) NOT NULL DEFAULT '0' COMMENT '租户ID',
    role_id BIGINT NOT NULL COMMENT '角色ID',
    menu_id BIGINT NOT NULL COMMENT '菜单ID',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_tenant_id (tenant_id),
    INDEX idx_role_id (role_id),
    INDEX idx_menu_id (menu_id)
) ENGINE=InnoDB COMMENT='角色菜单关联表';

-- 登录日志表
CREATE TABLE IF NOT EXISTS sys_login_log (
    id BIGINT NOT NULL PRIMARY KEY COMMENT '主键(雪花ID)',
    tenant_id VARCHAR(32) NOT NULL COMMENT '租户ID',
    user_id BIGINT COMMENT '用户ID(登录成功时记录)',
    username VARCHAR(50) NOT NULL COMMENT '用户名',
    login_ip VARCHAR(50) COMMENT '登录IP',
    login_location VARCHAR(100) COMMENT '登录地点',
    browser VARCHAR(50) COMMENT '浏览器',
    os VARCHAR(50) COMMENT '操作系统',
    status TINYINT(1) NOT NULL COMMENT '登录状态:1=成功,0=失败',
    message VARCHAR(255) COMMENT '提示消息',
    login_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '登录时间',
    created_by BIGINT COMMENT '创建人',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_by BIGINT COMMENT '更新人',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    deleted TINYINT(1) NOT NULL DEFAULT 0 COMMENT '逻辑删除:0=未删除,1=已删除',
    INDEX idx_tenant_id (tenant_id),
    INDEX idx_user_id (user_id),
    INDEX idx_username (username),
    INDEX idx_login_time (login_time)
) ENGINE=InnoDB COMMENT='登录日志表';


-- migrate:down
-- TODO: 添加回滚 SQL（如 DROP TABLE、ALTER TABLE DROP COLUMN 等）
