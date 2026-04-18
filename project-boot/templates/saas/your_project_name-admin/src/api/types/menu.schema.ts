import { z } from 'zod';
import { RSchema } from './common.schema';

/**
 * 菜单基础 Schema（递归树形结构）
 */
export const MenuSchema: z.ZodType<any> = z.lazy(() =>
  z.object({
    id: z.string(),
    parentId: z.string().nullable(),
    name: z.string(),
    path: z.string(),
    component: z.string().optional().nullable(),
    icon: z.string().optional().nullable(),
    sort: z.number(),
    permissionCode: z.string().optional().nullable(),
    status: z.number(),
    children: z.array(MenuSchema).optional().default([]),
  })
);

export type Menu = z.infer<typeof MenuSchema>;

/**
 * 菜单创建请求 Schema
 */
export const MenuCreateReqSchema = z.object({
  parentId: z.string().nullable(),
  name: z.string().min(1, '菜单名称不能为空'),
  path: z.string().min(1, '菜单路径不能为空'),
  component: z.string().optional().nullable(),
  icon: z.string().optional().nullable(),
  sort: z.number().default(0),
  permissionCode: z.string().optional().nullable(),
  status: z.number().default(1),
});

export type MenuCreateReq = z.infer<typeof MenuCreateReqSchema>;

/**
 * 菜单更新请求 Schema
 */
export const MenuUpdateReqSchema = z.object({
  id: z.string(),
  parentId: z.string().nullable(),
  name: z.string().min(1, '菜单名称不能为空'),
  path: z.string().min(1, '菜单路径不能为空'),
  component: z.string().optional().nullable(),
  icon: z.string().optional().nullable(),
  sort: z.number().default(0),
  permissionCode: z.string().optional().nullable(),
  status: z.number().default(1),
});

export type MenuUpdateReq = z.infer<typeof MenuUpdateReqSchema>;

/**
 * 菜单列表响应 Schema
 */
export const MenuListRespSchema = RSchema(z.array(MenuSchema));

export type MenuListResp = z.infer<typeof MenuListRespSchema>;
