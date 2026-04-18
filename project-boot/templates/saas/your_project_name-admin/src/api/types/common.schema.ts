import { z } from 'zod';

/**
 * 标准响应 Schema
 */
export function RSchema<T extends z.ZodTypeAny>(schema: T) {
  return z.object({
    code: z.string(),
    msg: z.string(),
    data: schema,
    success: z.boolean().optional(),
  }).passthrough();
}

/**
 * 分页响应 Schema
 */
export function PageSchema<T extends z.ZodTypeAny>(schema: T) {
  return z.object({
    records: z.array(schema),
    total: z.number(),
    size: z.number(),
    current: z.number(),
    pages: z.number(),
  });
}

/**
 * 用户信息 Schema
 */
export const UserInfoSchema = z.object({
  userId: z.string(),
  username: z.string(),
  realName: z.string().optional(),
  avatar: z.string().optional(),
  phone: z.string().optional(),
  email: z.string().optional(),
  tenantId: z.string(),
  tenantType: z.enum(['PLATFORM', 'PLATFORM_USER', 'TENANT_ADMIN', 'TENANT_USER']),
  roles: z.array(z.string()).optional(),
});

export type UserInfo = z.infer<typeof UserInfoSchema>;
