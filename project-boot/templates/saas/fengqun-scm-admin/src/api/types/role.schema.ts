import { z } from 'zod';
import { RSchema } from './common.schema';

/**
 * 角色基础 Schema
 */
export const RoleSchema = z.object({
  id: z.string(),
  tenantId: z.string().optional(),
  tenantName: z.string().optional(),
  roleCode: z.string(),
  roleName: z.string(),
  status: z.number(),
  createdAt: z.string(),
  updatedAt: z.string(),
});

export type Role = z.infer<typeof RoleSchema>;

/**
 * 创建角色请求 Schema
 */
export const RoleCreateReqSchema = z.object({
  roleCode: z.string().min(1, '角色编码不能为空'),
  roleName: z.string().min(1, '角色名称不能为空'),
  tenantId: z.string().optional(), // 租户ID，超级管理员创建角色时可指定
});

export type RoleCreateReq = z.infer<typeof RoleCreateReqSchema>;

/**
 * 默认权限配置 Schema
 * 用于分配权限时显示禁用勾选和禁止分配
 */
export const DefaultPermissionsSchema = z.object({
  defaultMenuIds: z.array(z.number()),
  defaultPermissionIds: z.array(z.number()),
  forbiddenMenuIds: z.array(z.number()).optional(),
  forbiddenPermissionIds: z.array(z.number()).optional(),
});

export type DefaultPermissions = z.infer<typeof DefaultPermissionsSchema>;

/**
 * 更新角色请求 Schema
 */
export const RoleUpdateReqSchema = z.object({
  id: z.string(),
  roleName: z.string().min(1, '角色名称不能为空').optional(),
});

export type RoleUpdateReq = z.infer<typeof RoleUpdateReqSchema>;

/**
 * 菜单 Schema（来自后端 MenuDTO）
 */
export const MenuSchema = z.object({
  id: z.coerce.string(),
  parentId: z.coerce.string().nullable(),
  name: z.string(),           // 后端返回 name
  path: z.string(),           // 后端返回 path
  component: z.string().optional().nullable(),
  icon: z.string().optional().nullable(),
  sort: z.number(),
  visible: z.number(),
  status: z.number(),
  permissionCode: z.string().optional().nullable(),
});

export type Menu = z.infer<typeof MenuSchema>;

/**
 * 菜单树 Schema（递归结构）
 */
export const MenuTreeSchema: z.ZodType<MenuTree> = z.lazy(() =>
  MenuSchema.extend({
    children: z.array(MenuTreeSchema).optional(),
  })
);

export interface MenuTree extends Menu {
  children?: MenuTree[];
}

/**
 * 权限 Schema
 */
export const PermissionSchema = z.object({
  id: z.string(),
  permissionCode: z.string(),
  permissionName: z.string(),
  description: z.string().optional(),
});

export type Permission = z.infer<typeof PermissionSchema>;

/**
 * 权限树 Schema（用于权限分配对话框）
 */
export const PermissionTreeSchema: z.ZodType<PermissionTree> = z.lazy(() =>
  PermissionSchema.extend({
    children: z.array(PermissionTreeSchema).optional(),
  })
);

export interface PermissionTree extends Permission {
  children?: PermissionTree[];
}

/**
 * 角色列表响应 Schema
 */
export const RoleListRespSchema = RSchema(z.array(RoleSchema));

/**
 * 角色详情响应 Schema
 */
export const RoleDetailRespSchema = RSchema(RoleSchema);

/**
 * 菜单列表响应 Schema
 */
export const MenuListRespSchema = RSchema(z.array(MenuSchema));

/**
 * 权限树响应 Schema
 */
export const PermissionTreeRespSchema = RSchema(z.array(PermissionTreeSchema));
