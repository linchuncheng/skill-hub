import { z } from 'zod';

// ========== 品牌相关 ==========

/**
 * 品牌实体
 */
export const BrandSchema = z.object({
  id: z.string(),  // Long 类型后端已转为字符串
  tenantId: z.string(),
  name: z.string().min(1, '品牌名称不能为空'),
  logoUrl: z.string().optional().nullable(),
  originCountry: z.string().optional().nullable(),
  description: z.string().optional().nullable(),
  sortOrder: z.number().optional(),
  createdBy: z.union([z.string(), z.number()]).optional().nullable(),
  createdAt: z.string(),
  updatedBy: z.union([z.string(), z.number()]).optional().nullable(),
  updatedAt: z.string(),
}).passthrough();

export type Brand = z.infer<typeof BrandSchema>;

/**
 * 创建品牌请求
 */
export const BrandCreateReqSchema = z.object({
  name: z.string().min(1, '品牌名称不能为空'),
  logoUrl: z.string().optional(),
  originCountry: z.string().optional(),
  description: z.string().optional(),
  sortOrder: z.number().optional(),
});

export type BrandCreateReq = z.infer<typeof BrandCreateReqSchema>;

/**
 * 更新品牌请求
 */
export const BrandUpdateReqSchema = z.object({
  id: z.string(),  // Long 类型后端已转为字符串
  name: z.string().optional(),
  logoUrl: z.string().optional(),
  originCountry: z.string().optional(),
  description: z.string().optional(),
  sortOrder: z.number().optional(),
});

export type BrandUpdateReq = z.infer<typeof BrandUpdateReqSchema>;

// ========== 分类相关 ==========

/**
 * 分类实体
 */
export const CategorySchema = z.object({
  id: z.string(),  // Long 类型后端已转为字符串
  tenantId: z.string(),
  parentId: z.number(),
  name: z.string().min(1, '分类名称不能为空'),
  level: z.number(),
  sortOrder: z.number().optional(),
  icon: z.string().optional().nullable(),
  description: z.string().optional().nullable(),
  createdBy: z.union([z.string(), z.number()]).optional().nullable(),
  createdAt: z.string(),
  updatedBy: z.union([z.string(), z.number()]).optional().nullable(),
  updatedAt: z.string(),
}).passthrough();

export type Category = z.infer<typeof CategorySchema>;

/**
 * 树形分类节点
 */
export const CategoryTreeNodeSchema = CategorySchema.extend({
  children: z.array(z.lazy(() => CategoryTreeNodeSchema)).optional(),
});

export type CategoryTreeNode = z.infer<typeof CategoryTreeNodeSchema>;

/**
 * 创建分类请求
 */
export const CategoryCreateReqSchema = z.object({
  parentId: z.number().optional(),
  name: z.string().min(1, '分类名称不能为空'),
  level: z.number().optional(),
  sortOrder: z.number().optional(),
  icon: z.string().optional(),
  description: z.string().optional(),
});

export type CategoryCreateReq = z.infer<typeof CategoryCreateReqSchema>;

/**
 * 更新分类请求
 */
export const CategoryUpdateReqSchema = z.object({
  id: z.string(),  // Long 类型后端已转为字符串
  name: z.string().optional(),
  parentId: z.number().optional(),
  sortOrder: z.number().optional(),
  icon: z.string().optional(),
  description: z.string().optional(),
});

export type CategoryUpdateReq = z.infer<typeof CategoryUpdateReqSchema>;

// ========== 商品相关 ==========

/**
 * 商品实体
 */
export const ProductSchema = z.object({
  id: z.string(),  // Long 类型后端已转为字符串
  tenantId: z.string(),
  productCode: z.string(),      // 商品编码
  productName: z.string(),      // 商品名称
  category: z.string().optional().nullable(), // 分类名称
  categoryId: z.string().optional().nullable(), // 分类 ID
  brand: z.string().optional().nullable(),    // 品牌名称
  brandId: z.string().optional().nullable(),  // 品牌 ID
  status: z.string(),             // 状态 ACTIVE/INACTIVE
  createdBy: z.union([z.string(), z.number()]).optional().nullable(),
  createdAt: z.string(),
  updatedBy: z.union([z.string(), z.number()]).optional().nullable(),
  updatedAt: z.string(),
}).passthrough();

export type Product = z.infer<typeof ProductSchema>;

/**
 * 创建商品请求
 */
export const ProductCreateReqSchema = z.object({
  productCode: z.string().min(1, '商品编码不能为空'),
  productName: z.string().min(1, '商品名称不能为空'),
  category: z.string().optional(),
  categoryId: z.number().optional().nullable(),
  brand: z.string().optional(),
  brandId: z.number().optional().nullable(),
});

export type ProductCreateReq = z.infer<typeof ProductCreateReqSchema>;

/**
 * 更新商品请求
 */
export const ProductUpdateReqSchema = z.object({
  id: z.string(),  // Long 类型后端已转为字符串
  productCode: z.string().optional(),
  productName: z.string().optional(),
  category: z.string().optional(),
  categoryId: z.number().optional().nullable(),
  brand: z.string().optional(),
  brandId: z.number().optional().nullable(),
  status: z.string().optional(),
});

export type ProductUpdateReq = z.infer<typeof ProductUpdateReqSchema>;

// ========== SKU 相关 ==========

/**
 * SKU 实体
 */
export const SkuSchema = z.object({
  id: z.string(),  // Long 类型后端已转为字符串
  tenantId: z.string(),
  productId: z.string(),
  skuCode: z.string(),
  skuName: z.string(),
  specAttrs: z.string().optional().nullable(),  // 规格参数 JSON（与后端字段名对齐）
  unit: z.string(),
  cartonQty: z.number().optional().nullable(),   // 箱规（每箱数量）
  palletQty: z.number().optional().nullable(),   // 托盘规格（每托盘箱数）
  status: z.string(),                             // 状态 ACTIVE/INACTIVE（与后端对齐）
  remark: z.string().optional().nullable(),       // 备注
  createdBy: z.union([z.string(), z.number()]).optional().nullable(),
  createdAt: z.string(),
  updatedBy: z.union([z.string(), z.number()]).optional().nullable(),
  updatedAt: z.string(),
}).passthrough();

export type Sku = z.infer<typeof SkuSchema>;

/**
 * 创建 SKU 请求
 */
export const SkuCreateReqSchema = z.object({
  productId: z.string(),
  skuCode: z.string().min(1, 'SKU编码不能为空'),
  skuName: z.string().min(1, 'SKU名称不能为空'),
  specAttrs: z.string().optional(),               // 规格参数 JSON
  unit: z.string().min(1, '单位不能为空'),
  cartonQty: z.number().optional(),               // 箱规
  palletQty: z.number().optional(),               // 托盘规格
  status: z.string().optional(),                   // 状态
  remark: z.string().optional(),                   // 备注
});

export type SkuCreateReq = z.infer<typeof SkuCreateReqSchema>;

/**
 * 更新 SKU 请求
 */
export const SkuUpdateReqSchema = z.object({
  skuName: z.string().optional(),
  specAttrs: z.string().optional(),               // 规格参数 JSON
  unit: z.string().optional(),
  cartonQty: z.number().optional(),               // 箱规
  palletQty: z.number().optional(),               // 托盘规格
  status: z.string().optional(),                   // 状态
  remark: z.string().optional(),                   // 备注
});

export type SkuUpdateReq = z.infer<typeof SkuUpdateReqSchema>;

/**
 * SKU 条码
 */
export const SkuBarcodeSchema = z.object({
  id: z.string(),  // Long 类型后端已转为字符串
  skuId: z.string(),
  barcode: z.string(),
  barcodeType: z.string(), // 'EAN13' | 'INNER'
  isPrimary: z.boolean().optional().nullable(),
  createdBy: z.union([z.string(), z.number()]).optional().nullable(),
  createdAt: z.string().optional().nullable(),
}).passthrough();

export type SkuBarcode = z.infer<typeof SkuBarcodeSchema>;

/**
 * 绑定条码请求
 */
export const BindBarcodeReqSchema = z.object({
  barcode: z.string().min(1, '条码不能为空'),
  barcodeType: z.string().min(1, '条码类型不能为空'),
});

export type BindBarcodeReq = z.infer<typeof BindBarcodeReqSchema>;

/**
 * SKU BOM（组合装）
 */
export const SkuBomSchema = z.object({
  id: z.string(),  // Long 类型后端已转为字符串
  skuId: z.string(),          // 组合装 SKU
  componentskuId: z.string(), // 组成件 SKU
  quantity: z.number(),
}).passthrough();

export type SkuBom = z.infer<typeof SkuBomSchema>;

/**
 * BOM 组件
 */
export const BomComponentSchema = z.object({
  componentskuId: z.string(),
  quantity: z.number().min(1, '数量必须大于0'),
});

export type BomComponent = z.infer<typeof BomComponentSchema>;

/**
 * 配置 BOM 请求
 */
export const ConfigureBomReqSchema = z.object({
  components: z.array(BomComponentSchema),
});

export type ConfigureBomReq = z.infer<typeof ConfigureBomReqSchema>;

/**
 * 绑定仓库请求
 */
export const BindWarehousesReqSchema = z.object({
  warehouseIds: z.array(z.string()),
});

export type BindWarehousesReq = z.infer<typeof BindWarehousesReqSchema>;

/**
 * SKU BOM 组成件响应（用于列表展示）
 */
export const SkuBomComponentSchema = z.object({
  id: z.string(),  // Long 类型后端已转为字符串
  componentskuId: z.string(),
  componentSkuCode: z.string(),
  componentSkuName: z.string(),
  quantity: z.number(),
  updatedAt: z.string(),
});

export type SkuBomComponent = z.infer<typeof SkuBomComponentSchema>;

// ========== 供应商相关 ==========

/**
 * 供应商实体
 */
export const SupplierSchema = z.object({
  id: z.string(),  // Long 类型后端已转为字符串
  tenantId: z.string(),
  supplierCode: z.string(),
  supplierName: z.string(),
  contactName: z.string().optional().nullable(),
  contactPhone: z.string().optional().nullable(),
  address: z.string().optional().nullable(),
  riskLevel: z.string().optional().nullable(), // 'LOW' | 'MEDIUM' | 'HIGH'
  status: z.number(),
  createdBy: z.union([z.string(), z.number()]).optional().nullable(),
  createdAt: z.string(),
  updatedBy: z.union([z.string(), z.number()]).optional().nullable(),
  updatedAt: z.string(),
}).passthrough();

export type Supplier = z.infer<typeof SupplierSchema>;

/**
 * 创建供应商请求
 */
export const SupplierCreateReqSchema = z.object({
  supplierCode: z.string().min(1, '供应商编码不能为空'),
  supplierName: z.string().min(1, '供应商名称不能为空'),
  contactName: z.string().optional(),
  contactPhone: z.string().optional(),
  address: z.string().optional(),
  riskLevel: z.string().optional(),
});

export type SupplierCreateReq = z.infer<typeof SupplierCreateReqSchema>;

/**
 * 更新供应商请求
 */
export const SupplierUpdateReqSchema = z.object({
  id: z.string(),  // Long 类型后端已转为字符串
  supplierName: z.string().optional(),
  contactName: z.string().optional(),
  contactPhone: z.string().optional(),
  address: z.string().optional(),
  riskLevel: z.string().optional(),
  status: z.number().optional(),
});

export type SupplierUpdateReq = z.infer<typeof SupplierUpdateReqSchema>;

/**
 * 关联商品请求
 */
export const LinkSkusReqSchema = z.object({
  skuIds: z.array(z.string()),
});

export type LinkSkusReq = z.infer<typeof LinkSkusReqSchema>;

/**
 * 已关联的商品 SKU
 */
export const LinkedSkuSchema = z.object({
  id: z.string(),  // Long 类型后端已转为字符串
  skuId: z.string(),
  skuCode: z.string(),
  skuName: z.string(),
  unit: z.string().optional().nullable(),
  createdAt: z.string(),
});

export type LinkedSku = z.infer<typeof LinkedSkuSchema>;

// ========== 订单相关 ==========

/**
 * 订单明细项
 */
export const OrderItemSchema = z.object({
  skuId: z.string(),
  skuCode: z.string().optional(),
  skuName: z.string(),
  quantity: z.number(),
  unitPrice: z.number(),
}).passthrough();

export type OrderItem = z.infer<typeof OrderItemSchema>;

/**
 * SCM 订单实体
 */
export const ErpOrderSchema = z.object({
  id: z.string(),  // Long 类型后端已转为字符串
  tenantId: z.string(),
  orderNo: z.string(),
  orderType: z.string(), // 'B2C' | 'B2B'
  platformOrderNo: z.string(),
  status: z.string(),
  warehouseId: z.string().optional().nullable(),
  warehouseName: z.string().optional().nullable(),
  totalAmount: z.number(),
  items: z.array(OrderItemSchema).optional(),
  createdBy: z.union([z.string(), z.number()]).optional().nullable(),
  createdAt: z.string(),
  updatedBy: z.union([z.string(), z.number()]).optional().nullable(),
  updatedAt: z.string(),
}).passthrough();

export type ErpOrder = z.infer<typeof ErpOrderSchema>;

/**
 * 接收订单请求
 */
export const OrderReceiveReqSchema = z.object({
  platformOrderNo: z.string().min(1, '平台订单号不能为空'),
  orderType: z.string().min(1, '订单类型不能为空'),
  items: z.array(OrderItemSchema).min(1, '订单明细不能为空'),
});

export type OrderReceiveReq = z.infer<typeof OrderReceiveReqSchema>;

/**
 * 手工创建订单请求
 */
export const OrderCreateReqSchema = z.object({
  orderType: z.string().min(1, '订单类型不能为空'),
  buyerName: z.string().min(1, '买家姓名不能为空'),
  buyerPhone: z.string().min(1, '买家电话不能为空'),
  province: z.string().min(1, '省份不能为空'),
  city: z.string().min(1, '城市不能为空'),
  district: z.string().min(1, '区县不能为空'),
  address: z.string().min(1, '详细地址不能为空'),
  totalAmount: z.number().min(0, '订单金额不能为负'),
  urgent: z.boolean().optional(),
  remark: z.string().optional(),
  items: z.array(OrderItemSchema).min(1, '订单明细不能为空'),
});

export type OrderCreateReq = z.infer<typeof OrderCreateReqSchema>;

/**
 * 人工审核请求
 */
export const ManualAuditReqSchema = z.object({
  approved: z.boolean(),
  reason: z.string().optional(),
});

export type ManualAuditReq = z.infer<typeof ManualAuditReqSchema>;

// ========== 采购单相关 ==========

/**
 * 采购单明细项
 */
export const PurchaseOrderItemSchema = z.object({
  skuId: z.string(),  // Long类型后端已转为字符串
  skuCode: z.string().optional(),
  skuName: z.string(),
  quantity: z.number(),
  receivedQty: z.number().optional(),
  unitPrice: z.number().optional(),
}).passthrough();

export type PurchaseOrderItem = z.infer<typeof PurchaseOrderItemSchema>;

/**
 * 采购单实体
 */
export const PurchaseOrderSchema = z.object({
  id: z.string(),  // Long 类型后端已转为字符串
  tenantId: z.string(),
  orderNo: z.string(),
  supplierId: z.string(),
  supplierName: z.string().optional().nullable(),
  status: z.string(), // 'DRAFT' | 'CONFIRMED' | 'ARRIVING' | 'COMPLETED' | 'CANCELLED'
  warehouseId: z.string().optional().nullable(),
  warehouseName: z.string().optional().nullable(),
  expectedArriveTime: z.string().optional().nullable(),
  totalAmount: z.number().optional(),
  items: z.array(PurchaseOrderItemSchema).optional(),
  createdBy: z.union([z.string(), z.number()]).optional().nullable(),
  createdAt: z.string(),
  updatedBy: z.union([z.string(), z.number()]).optional().nullable(),
  updatedAt: z.string(),
}).passthrough();

export type PurchaseOrder = z.infer<typeof PurchaseOrderSchema>;

/**
 * 创建采购单请求
 */
export const PurchaseOrderCreateReqSchema = z.object({
  supplierId: z.string(),
  warehouseId: z.string(),
  expectedArrivalDate: z.string().optional(),
  items: z.array(PurchaseOrderItemSchema).min(1, '采购明细不能为空'),
});

export type PurchaseOrderCreateReq = z.infer<typeof PurchaseOrderCreateReqSchema>;

/**
 * 到货确认请求
 */
export const ArriveReqSchema = z.object({
  expectedArriveTime: z.string().optional(),
});

export type ArriveReq = z.infer<typeof ArriveReqSchema>;

/**
 * 取消采购单请求
 */
export const CancelPurchaseReqSchema = z.object({
  reason: z.string().optional(),
});

export type CancelPurchaseReq = z.infer<typeof CancelPurchaseReqSchema>;

// ========== 异常工单 ==========

/**
 * 异常工单实体
 */
export const ExceptionTicketSchema = z.object({
  id: z.string(),  // Long 类型后端已转为字符串
  tenantId: z.string(),
  ticketType: z.string(),
  relatedOrderId: z.number().optional().nullable(),
  description: z.string(),
  status: z.string(), // 'OPEN' | 'RESOLVED'
  resolution: z.string().optional().nullable(),
  resolvedAt: z.string().optional().nullable(),
  createdBy: z.union([z.string(), z.number()]).optional().nullable(),
  createdAt: z.string(),
}).passthrough();

export type ExceptionTicket = z.infer<typeof ExceptionTicketSchema>;

/**
 * 解决工单请求
 */
export const ResolveTicketReqSchema = z.object({
  resolution: z.string().min(1, '解决方案不能为空'),
});

export type ResolveTicketReq = z.infer<typeof ResolveTicketReqSchema>;
