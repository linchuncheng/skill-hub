package com.your_group_name.your_project_name.api.dto;

import java.io.Serializable;

import lombok.Data;

/**
 * 供应商查询结果 DTO
 */
@Data
public class SupplierDTO implements Serializable {

    /**
     * 供应商 ID
     */
    private Long id;

    /**
     * 供应商编码
     */
    private String supplierCode;

    /**
     * 供应商名称
     */
    private String supplierName;

    /**
     * 风险等级（HIGH: 高风险, MEDIUM: 中风险, LOW: 低风险）
     */
    private String riskLevel;

    /**
     * 状态（ACTIVE: 启用, INACTIVE: 停用）
     */
    private String status;
}