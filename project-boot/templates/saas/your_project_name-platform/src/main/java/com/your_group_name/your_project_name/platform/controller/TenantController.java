package com.your_group_name.your_project_name.platform.controller;

import com.your_group_name.your_project_name.common.base.BaseController;
import com.your_group_name.your_project_name.common.response.R;
import com.your_group_name.your_project_name.platform.entity.SysTenant;
import com.your_group_name.your_project_name.platform.service.TenantService;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

/**
 * 租户 API 控制器
 */
@RestController
@RequestMapping("/api/platform/tenant")
public class TenantController extends BaseController {

    @Autowired
    private TenantService tenantService;

    @GetMapping("/list")
    public R<List<SysTenant>> listTenants() {
        return success(tenantService.listTenants());
    }

    @GetMapping("/{id}")
    public R<SysTenant> getTenantById(@PathVariable Long id) {
        return success(tenantService.getTenantById(id));
    }

    @PostMapping
    public R<Long> createTenant(@RequestBody SysTenant tenant) {
        Long tenantId = tenantService.createTenant(tenant);
        return success(tenantId);
    }

    @PutMapping
    public R<Void> updateTenant(@RequestBody SysTenant tenant) {
        tenantService.updateTenant(tenant);
        return success();
    }

    @DeleteMapping("/{id}")
    public R<Void> deleteTenant(@PathVariable Long id) {
        tenantService.deleteTenant(id);
        return success();
    }

    @PutMapping("/{id}/enable")
    public R<Void> enableTenant(@PathVariable Long id) {
        tenantService.enableTenant(id);
        return success();
    }

    @PutMapping("/{id}/disable")
    public R<Void> disableTenant(@PathVariable Long id) {
        tenantService.disableTenant(id);
        return success();
    }
}
