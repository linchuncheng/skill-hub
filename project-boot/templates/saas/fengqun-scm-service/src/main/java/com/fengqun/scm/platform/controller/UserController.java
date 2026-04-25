package com.fengqun.scm.platform.controller;

import com.fengqun.scm.common.base.BaseController;
import com.fengqun.scm.common.response.R;
import com.fengqun.scm.platform.dto.UserRespDTO;
import com.fengqun.scm.platform.entity.SysRole;
import com.fengqun.scm.platform.entity.SysUser;
import com.fengqun.scm.platform.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/platform/user")
public class UserController extends BaseController {

    @Autowired
    private UserService userService;

    @GetMapping("/list")
    public R<List<UserRespDTO>> listUsers(@RequestParam(required = false) String tenantId) {
        if (tenantId != null && !tenantId.isEmpty()) {
            return success(userService.listUsersByTenantId(tenantId));
        }
        return success(userService.listUsers());
    }

    @PostMapping
    public R<Long> createUser(@RequestBody SysUser user) {
        return success(userService.createUser(user));
    }

    @PutMapping
    public R<Void> updateUser(@RequestBody SysUser user) {
        userService.updateUser(user);
        return success();
    }

    @DeleteMapping("/{id}")
    public R<Void> deleteUser(@PathVariable Long id) {
        userService.deleteUser(id);
        return success();
    }

    @PutMapping("/{id}/enable")
    public R<Void> enableUser(@PathVariable Long id) {
        userService.enableUser(id);
        return success();
    }

    @PutMapping("/{id}/disable")
    public R<Void> disableUser(@PathVariable Long id) {
        userService.disableUser(id);
        return success();
    }

    @PostMapping("/role/assign")
    public R<Void> assignRoles(@RequestBody Map<String, Object> params) {
        Long userId = Long.valueOf(params.get("userId").toString());
        @SuppressWarnings("unchecked")
        List<Long> roleIds = ((List<?>) params.get("roleIds")).stream()
                .map(obj -> Long.valueOf(obj.toString()))
                .toList();
        userService.assignRoles(userId, roleIds);
        return success();
    }

    @GetMapping("/{userId}/roles")
    public R<List<SysRole>> getUserRoles(@PathVariable Long userId) {
        return success(userService.getRolesByUserId(userId));
    }

    @PutMapping("/{userId}/password/reset")
    public R<Void> resetPassword(@PathVariable Long userId, @RequestBody Map<String, String> params) {
        String newPassword = params.get("newPassword");
        userService.resetPassword(userId, newPassword);
        return success();
    }
}
