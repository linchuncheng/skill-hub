import { z } from 'zod';
import { RSchema } from './common.schema';

export const TenantSchema = z.object({
  id: z.union([z.string(), z.number()]).transform(String),
  tenantId: z.string().nullable().optional(),
  tenantCode: z.string(),
  tenantName: z.string(),
  logo: z.string().optional().nullable(),
  contactName: z.string().optional().nullable(),
  contactPhone: z.string().optional().nullable(),
  status: z.number(),
  createdBy: z.union([z.string(), z.number()]).optional().nullable(),
  createdAt: z.string(),
  updatedBy: z.union([z.string(), z.number()]).optional().nullable(),
  updatedAt: z.string(),
  deleted: z.boolean().optional(),
}).passthrough();

export type Tenant = z.infer<typeof TenantSchema>;

export const TenantCreateReqSchema = z.object({
  tenantCode: z.string().min(1, '租户编码不能为空'),
  tenantName: z.string().min(1, '租户名称不能为空'),
  logo: z.string().optional(),
  contactName: z.string().optional(),
  contactPhone: z.string().optional(),
});

export type TenantCreateReq = z.infer<typeof TenantCreateReqSchema>;

export const TenantUpdateReqSchema = z.object({
  id: z.union([z.string(), z.number()]),
  tenantName: z.string().optional(),
  logo: z.string().optional(),
  contactName: z.string().optional(),
  contactPhone: z.string().optional(),
});

export type TenantUpdateReq = z.infer<typeof TenantUpdateReqSchema>;

export const TenantListRespSchema = RSchema(z.array(TenantSchema));
export const TenantDetailRespSchema = RSchema(TenantSchema);
