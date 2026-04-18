import { z } from 'zod';
import { RSchema, PageSchema } from './common.schema';

/**
 * 权限 Schema
 */
export const PermissionSchema = z.object({
  id: z.number(),
  permission_code: z.string(),
  permission_name: z.string(),
  description: z.string().optional().nullable(),
  status: z.number(),
});

export type Permission = z.infer<typeof PermissionSchema>;

/**
 * 权限列表响应 Schema（分页）
 */
export const PermissionListRespSchema = RSchema(
  PageSchema(PermissionSchema)
);

export type PermissionListResp = z.infer<typeof PermissionListRespSchema>;
