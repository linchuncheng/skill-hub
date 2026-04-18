package com.your_group_name.your_project_name.common.tenant;

/**
 * 租户相关常量定义
 */
public final class TenantConstants {

    private TenantConstants() {
        // 防止实例化
    }

    /**
     * 平台租户编码（通过 tenant_code 判断是否为平台租户）
     */
    public static final String PLATFORM_TENANT_CODE = "default";

    /**
     * 租户类型：超级管理员
     */
    public static final String TENANT_TYPE_PLATFORM = "PLATFORM";

    /**
     * 租户类型：平台普通用户
     */
    public static final String TENANT_TYPE_PLATFORM_USER = "PLATFORM_USER";

    /**
     * 租户类型：租户管理员
     */
    public static final String TENANT_TYPE_TENANT_ADMIN = "TENANT_ADMIN";

    /**
     * 租户类型：租户普通用户
     */
    public static final String TENANT_TYPE_TENANT_USER = "TENANT_USER";

    /**
     * 判断是否为平台租户（通过 tenant_code 判断）
     */
    public static boolean isPlatformTenant(String tenantCode) {
        return PLATFORM_TENANT_CODE.equals(tenantCode);
    }

    /**
     * 判断是否为平台类型用户（包括 PLATFORM 和 PLATFORM_USER）
     */
    public static boolean isPlatformType(String tenantType) {
        return TENANT_TYPE_PLATFORM.equals(tenantType) || TENANT_TYPE_PLATFORM_USER.equals(tenantType);
    }

    /**
     * 判断是否为租户类型用户（包括 TENANT_ADMIN 和 TENANT_USER）
     */
    public static boolean isTenantType(String tenantType) {
        return TENANT_TYPE_TENANT_ADMIN.equals(tenantType) || TENANT_TYPE_TENANT_USER.equals(tenantType);
    }
}
