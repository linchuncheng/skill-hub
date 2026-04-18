package com.your_group_name.your_project_name.api;

import com.your_group_name.your_project_name.api.dto.SupplierDTO;

/**
 * 供应商查询 Dubbo 接口。
 *
 * FMS 提供，WMS 通过 Dubbo 调用以获取供应商信息（如风险等级）。
 */
public interface SupplierService {

    /**
     * 按 ID 查询供应商。
     *
     * @param supplierId 供应商 ID
     * @return 供应商 DTO，不存在返回 null
     */
    SupplierDTO getSupplierById(Long supplierId);
}
