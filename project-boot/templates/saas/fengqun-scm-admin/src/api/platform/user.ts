import { http } from '../http';
import {
    Role,
    User,
    UserCreateReq,
    UserUpdateReq,
} from '../types/user.schema';

/**
 * 查询用户列表
 * @param tenantId 可选，按租户筛选（超级管理员使用）
 */
export const listUsers = async (tenantId?: string): Promise<User[]> => {
  const params = tenantId ? { tenantId } : {};
  return http.get<User[]>('/api/platform/user/list', { params });
};

/**
 * 根据ID查询用户
 */
export const getUserById = async (id: string): Promise<User> => {
  return http.get<User>(`/api/platform/user/${id}`);
};

/**
 * 创建用户
 */
export const createUser = async (data: UserCreateReq): Promise<number> => {
  return http.post<number>('/api/platform/user', data);
};

/**
 * 更新用户
 */
export const updateUser = async (data: UserUpdateReq): Promise<void> => {
  await http.put('/api/platform/user', data);
};

/**
 * 删除用户
 */
export const deleteUser = async (id: string): Promise<void> => {
  await http.delete(`/api/platform/user/${id}`);
};

/**
 * 启用用户
 */
export const enableUser = async (id: string): Promise<void> => {
  await http.put(`/api/platform/user/${id}/enable`);
};

/**
 * 禁用用户
 */
export const disableUser = async (id: string): Promise<void> => {
  await http.put(`/api/platform/user/${id}/disable`);
};

/**
 * 分配角色给用户
 */
export const assignRoles = async (userId: string | number, roleIds: (string | number)[]): Promise<void> => {
  await http.post(`/api/platform/user/role/assign`, {
    userId: userId,  // 保持字符串类型,避免精度丢失
    roleIds: roleIds,  // 保持字符串类型,避免精度丢失
  });
};

/**
 * 获取用户的角色列表
 */
export const getUserRoles = async (userId: string): Promise<Role[]> => {
  return http.get<Role[]>(`/api/platform/user/${userId}/roles`);
};

/**
 * 获取角色列表
 * @param tenantId 可选，按租户筛选（超级管理员使用）
 */
export const getRoleList = async (tenantId?: string): Promise<Role[]> => {
  const params = tenantId ? { tenantId } : {};
  return http.get<Role[]>('/api/platform/role/list', { params });
};

/**
 * 重置用户密码
 */
export const resetPassword = async (userId: string | number, newPassword: string): Promise<void> => {
  await http.put(`/api/platform/user/${userId}/password/reset`, {
    newPassword,
  });
};
