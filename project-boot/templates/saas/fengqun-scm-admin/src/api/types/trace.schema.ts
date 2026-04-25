import { z } from 'zod';

/**
 * 流转节点 Schema
 */
export const TraceFlowNodeSchema = z.object({
  nodeName: z.string(),
  nodeTime: z.string().optional().nullable(),
  operator: z.string().optional().nullable(),
  status: z.string().optional().nullable(),
  description: z.string().optional().nullable(),
}).passthrough();

export type TraceFlowNode = z.infer<typeof TraceFlowNodeSchema>;

/**
 * 关联订单 Schema
 */
export const TraceOrderSchema = z.object({
  orderNo: z.string(),
  outboundNo: z.string(),
  outboundType: z.string().optional().nullable(),
  outboundStatus: z.string().optional().nullable(),
  buyerName: z.string().optional().nullable(),
  buyerPhone: z.string().optional().nullable(),
  receiverName: z.string().optional().nullable(),
  receiverPhone: z.string().optional().nullable(),
  waybillNo: z.string().optional().nullable(),
  waybillStatus: z.string().optional().nullable(),
  signTime: z.string().optional().nullable(),
}).passthrough();

export type TraceOrder = z.infer<typeof TraceOrderSchema>;

/**
 * 批次追溯结果 Schema
 */
export const BatchTraceSchema = z.object({
  batchNo: z.string(),
  skuCode: z.string().optional().nullable(),
  skuName: z.string().optional().nullable(),
  productionDate: z.string().optional().nullable(),
  expiryDate: z.string().optional().nullable(),
  flowNodes: z.array(TraceFlowNodeSchema).optional().nullable(),
  orders: z.array(TraceOrderSchema).optional().nullable(),
}).passthrough();

export type BatchTrace = z.infer<typeof BatchTraceSchema>;
