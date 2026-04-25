import { http } from '../http';
import type {
  LinkSkusReq,
  LinkedSku,
  Supplier,
  SupplierCreateReq,
  SupplierUpdateReq,
} from '../types/scm.schema';

/**
 * 查询供应商列表
 */
export const listSuppliers = async (params?: {
  keyword?: string;
}): Promise<Supplier[]> => {
  return http.get<Supplier[]>('/api/scm/suppliers', { params });
};

/**
 * 查询供应商详情
 */
export const getSupplier = async (id: string): Promise<Supplier> => {
  return http.get<Supplier>(`/api/scm/suppliers/${id}`);
};

/**
 * 创建供应商
 */
export const createSupplier = async (data: SupplierCreateReq): Promise<number> => {
  return http.post<number>('/api/scm/suppliers', data);
};

/**
 * 更新供应商
 */
export const updateSupplier = async (data: SupplierUpdateReq): Promise<void> => {
  await http.put(`/api/scm/suppliers/${data.id}`, data);
};

/**
 * 删除供应商
 */
export const deleteSupplier = async (id: string): Promise<void> => {
  await http.delete(`/api/scm/suppliers/${id}`);
};

/**
 * 关联商品
 */
export const linkSkus = async (
  supplierId: string,
  data: LinkSkusReq
): Promise<void> => {
  await http.post(`/api/scm/suppliers/${supplierId}/skus`, data);
};

/**
 * 查询供应商已关联的商品列表
 */
export const listLinkedSkus = async (supplierId: string): Promise<LinkedSku[]> => {
  return http.get<LinkedSku[]>(`/api/scm/suppliers/${supplierId}/skus`);
};

/**
 * 批量解除商品关联
 */
export const unlinkSkus = async (
  supplierId: string,
  skuIds: string[]
): Promise<void> => {
  await http.delete(`/api/scm/suppliers/${supplierId}/skus`, { data: { skuIds } });
};
