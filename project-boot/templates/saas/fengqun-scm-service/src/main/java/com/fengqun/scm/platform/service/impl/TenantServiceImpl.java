package com.fengqun.scm.platform.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.fengqun.scm.platform.entity.SysTenant;
import com.fengqun.scm.platform.mapper.SysTenantMapper;
import com.fengqun.scm.platform.service.TenantService;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * 租户服务实现
 */
@Service
public class TenantServiceImpl extends ServiceImpl<SysTenantMapper, SysTenant> implements TenantService {

    @Override
    public List<SysTenant> listTenants() {
        return this.list();
    }

    @Override
    public SysTenant getTenantById(Long id) {
        return this.getById(id);
    }

    @Override
    public Long createTenant(SysTenant tenant) {
        tenant.setStatus(1);
        this.save(tenant);
        return tenant.getId();
    }

    @Override
    public void updateTenant(SysTenant tenant) {
        this.updateById(tenant);
    }

    @Override
    public void deleteTenant(Long id) {
        this.removeById(id);
    }

    @Override
    public void enableTenant(Long id) {
        SysTenant tenant = this.getById(id);
        tenant.setStatus(1);
        this.updateById(tenant);
    }

    @Override
    public void disableTenant(Long id) {
        SysTenant tenant = this.getById(id);
        tenant.setStatus(0);
        this.updateById(tenant);
    }
}
