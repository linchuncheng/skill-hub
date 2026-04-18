package com.your_group_name.your_project_name.platform.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.your_group_name.your_project_name.platform.entity.SysTenant;

import java.util.List;

/**
 * 租户服务接口
 */
public interface TenantService extends IService<SysTenant> {
    List<SysTenant> listTenants();

    SysTenant getTenantById(Long id);

    Long createTenant(SysTenant tenant);

    void updateTenant(SysTenant tenant);

    void deleteTenant(Long id);

    void enableTenant(Long id);

    void disableTenant(Long id);
}
