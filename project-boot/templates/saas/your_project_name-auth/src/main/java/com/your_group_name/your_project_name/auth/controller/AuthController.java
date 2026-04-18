package com.your_group_name.your_project_name.auth.controller;

import com.your_group_name.your_project_name.auth.dto.LoginReqDTO;
import com.your_group_name.your_project_name.auth.dto.LoginRespDTO;
import com.your_group_name.your_project_name.auth.dto.RefreshTokenReqDTO;
import com.your_group_name.your_project_name.auth.service.AuthBizService;
import com.your_group_name.your_project_name.common.base.BaseController;
import com.your_group_name.your_project_name.common.exception.BusinessException;
import com.your_group_name.your_project_name.common.response.R;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 认证 Controller
 */
@Slf4j
@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController extends BaseController {

    private final AuthBizService authBizService;

    /**
     * 登录接口
     */
    @PostMapping("/login")
    public R<LoginRespDTO> login(@RequestBody LoginReqDTO req) {
        try {
            LoginRespDTO resp = authBizService.login(req);
            return success(resp);
        } catch (BusinessException e) {
            return fail(e.getCode(), e.getMessage());
        } catch (Exception e) {
            log.error("Login error", e);
            return fail("登录失败");
        }
    }

    /**
     * 刷新 Token 接口
     */
    @PostMapping("/refresh-token")
    public R<LoginRespDTO> refreshToken(@RequestBody RefreshTokenReqDTO req) {
        try {
            LoginRespDTO resp = authBizService.refreshToken(req.getRefreshToken());
            return success(resp);
        } catch (BusinessException e) {
            return fail(e.getCode(), e.getMessage());
        } catch (Exception e) {
            log.error("Refresh token error", e);
            return fail("刷新 Token 失败");
        }
    }

    /**
     * 登出接口
     */
    @PostMapping("/logout")
    public R<Void> logout(@RequestBody RefreshTokenReqDTO req) {
        try {
            authBizService.logout(req.getRefreshToken());
            return success();
        } catch (Exception e) {
            log.error("Logout error", e);
            return fail("登出失败");
        }
    }
}
