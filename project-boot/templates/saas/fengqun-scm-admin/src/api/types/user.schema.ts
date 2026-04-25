import { z } from 'zod';
import { RSchema } from './common.schema';

/**
 * 用户基础 Schema
 */
export const UserSchema = z.object({
  id: z.string(),  // Long 类型后端已转为字符串,避免 JS 精度丢失
  tenantId: z.string(),
  tenantName: z.string().optional(),
  username: z.string(),
  password: z.string().optional(),
  realName: z.string().optional(),
  email: z.string().optional(),
  phone: z.string().optional(),
  avatar: z.string().optional(),
  remark: z.string().optional(),
  tenantType: z.string(),
  status: z.number(),
  roles: z.string().optional(), // 已分配角色名称，逗号分隔
  createdBy: z.string().nullable().optional(),
  createdAt: z.string(),
  updatedBy: z.string().nullable().optional(),
  updatedAt: z.string(),
  deleted: z.boolean().optional(),
}).passthrough();

export type User = z.infer<typeof UserSchema>;

/**
 * 创建用户请求 Schema
 */
export const UserCreateReqSchema = z.object({
  username: z.string().min(1, '用户名不能为空'),
  password: z.string().min(6, '密码至少6位'),
  realName: z.string().min(1, '真实姓名不能为空'),
  email: z.string().optional(),
  phone: z.string().optional(),
  tenantId: z.string().optional(), // 租户ID，超级管理员创建用户时可指定
  tenantType: z.string().optional(), // 用户类型：PLATFORM/TENANT_ADMIN/TENANT_USER
});

export type UserCreateReq = z.infer<typeof UserCreateReqSchema>;

/**
 * 更新用户请求 Schema
 */
export const UserUpdateReqSchema = z.object({
  id: z.string(),
  realName: z.string().min(1, '真实姓名不能为空').optional(),
  email: z.string().optional(),
  phone: z.string().optional(),
});

export type UserUpdateReq = z.infer<typeof UserUpdateReqSchema>;

/**
 * 角色基础 Schema（简化版，用于用户角色关联）
 */
export const RoleSchema = z.object({
  id: z.string(),  // Long 类型后端已转为字符串,避免 JS 精度丢失
  tenantId: z.string().optional(),
  roleCode: z.string(),
  roleName: z.string(),
  sort: z.number().optional(),
  status: z.number(),
  createdBy: z.string().nullable().optional(),
  createdAt: z.string().optional(),
  updatedBy: z.string().nullable().optional(),
  updatedAt: z.string().optional(),
  deleted: z.boolean().optional(),
}).passthrough();

export type Role = z.infer<typeof RoleSchema>;

/**
 * 用户列表响应 Schema
 */
export const UserListRespSchema = RSchema(z.array(UserSchema));

/**
 * 用户详情响应 Schema
 */
export const UserDetailRespSchema = RSchema(UserSchema);

/**
 * 角色列表响应 Schema
 */
export const RoleListRespSchema = RSchema(z.array(RoleSchema));
