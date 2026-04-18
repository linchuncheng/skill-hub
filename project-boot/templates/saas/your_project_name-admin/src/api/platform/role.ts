import { http } from '../http';
import {
    DefaultPermissions,
    MenuTree,
    PermissionTree,
    Role,
    RoleCreateReq,
    RoleUpdateReq,
} from '../types/role.schema';

/**
 * 查询角色列表
 * @param tenantId 可选，按租户筛选（超级管理员使用）
 */
export const listRoles = async (tenantId?: string): Promise<Role[]> => {
  const params = tenantId ? { tenantId } : {};
  return http.get<Role[]>('/api/platform/role/list', { params });
};

/**
 * 根据ID查询角色
 */
export const getRoleById = async (id: string): Promise<Role> => {
  return http.get<Role>(`/api/platform/role/${id}`);
};

/**
 * 创建角色
 */
export const createRole = async (data: RoleCreateReq): Promise<number> => {
  return http.post<number>('/api/platform/role', data);
};

/**
 * 更新角色
 */
export const updateRole = async (data: RoleUpdateReq): Promise<void> => {
  await http.put('/api/platform/role', data);
};

/**
 * 删除角色
 */
export const deleteRole = async (id: string): Promise<void> => {
  await http.delete(`/api/platform/role/${id}`);
};

/**
 * 启用角色
 */
export const enableRole = async (id: string): Promise<void> => {
  await http.put(`/api/platform/role/${id}/enable`);
};

/**
 * 禁用角色
 */
export const disableRole = async (id: string): Promise<void> => {
  await http.put(`/api/platform/role/${id}/disable`);
};

/**
 * 分配权限给角色
 */
export const assignPermissions = async (roleId: number, permissionIds: number[]): Promise<void> => {
  await http.post(`/api/platform/role/permission/assign`, {
    roleId,
    permissionIds,
  });
};

/**
 * 获取角色的权限ID列表
 */
export const getRolePermissions = async (roleId: string): Promise<string[]> => {
  return http.get<string[]>(`/api/platform/role/${roleId}/permissions`);
};

/**
 * 获取权限树（用于权限分配对话框）
 */
export const getPermissionTree = async (): Promise<PermissionTree[]> => {
  return http.get<PermissionTree[]>('/api/platform/permission/tree');
};

/**
 * 获取权限树（用于权限分配）
 * 返回所有权限，并标记角色已拥有的权限
 */
export const getPermissionTreeForAssign = async (roleId: string): Promise<PermissionTree[]> => {
  return http.get<PermissionTree[]>('/api/platform/permission/tree/assign', { params: { roleId } });
};

/**
 * 分配菜单给角色
 */
export const assignMenus = async (roleId: number, menuIds: number[]): Promise<void> => {
  await http.post(`/api/platform/role/menu/assign`, {
    roleId,
    menuIds,
  });
};

/**
 * 获取角色的菜单ID列表
 */
export const getRoleMenus = async (roleId: string): Promise<string[]> => {
  return http.get<string[]>(`/api/platform/role/${roleId}/menus`);
};

/**
 * 获取菜单树（用于菜单分配对话框）
 */
export const getMenuTree = async (): Promise<MenuTree[]> => {
  return http.get<MenuTree[]>('/api/platform/menu/tree');
};

/**
 * 获取菜单树（用于菜单分配，根据用户类型过滤）
 * 超级管理员返回所有菜单，租户管理员只返回已拥有的菜单
 */
export const getMenuTreeForAssign = async (): Promise<MenuTree[]> => {
  return http.get<MenuTree[]>('/api/platform/menu/tree/assign');
};

/**
 * 获取角色的默认权限配置
 * 用于分配权限时显示禁用勾选
 */
export const getDefaultPermissions = async (roleId: string): Promise<DefaultPermissions> => {
  return http.get<DefaultPermissions>(`/api/platform/role/${roleId}/default-permissions`);
};
