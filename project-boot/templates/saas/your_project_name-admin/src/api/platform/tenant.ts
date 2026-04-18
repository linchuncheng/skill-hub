import { http } from '../http';
import {
  Tenant,
  TenantCreateReq,
  TenantUpdateReq,
} from '../types/tenant.schema';

/**
 * 查询租户列表
 */
export const listTenants = async (): Promise<Tenant[]> => {
  return http.get<Tenant[]>('/api/platform/tenant/list');
};

/**
 * 根据ID查询租户
 */
export const getTenantById = async (id: string): Promise<Tenant> => {
  return http.get<Tenant>(`/api/platform/tenant/${id}`);
};

/**
 * 创建租户
 */
export const createTenant = async (data: TenantCreateReq): Promise<string> => {
  return http.post<string>('/api/platform/tenant', data);
};

/**
 * 更新租户
 */
export const updateTenant = async (data: TenantUpdateReq): Promise<void> => {
  await http.put('/api/platform/tenant', data);
};

/**
 * 删除租户
 */
export const deleteTenant = async (id: string): Promise<void> => {
  await http.delete(`/api/platform/tenant/${id}`);
};

/**
 * 启用租户
 */
export const enableTenant = async (id: string): Promise<void> => {
  await http.put(`/api/platform/tenant/${id}/enable`);
};

/**
 * 禁用租户
 */
export const disableTenant = async (id: string): Promise<void> => {
  await http.put(`/api/platform/tenant/${id}/disable`);
};
