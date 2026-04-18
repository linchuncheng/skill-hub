package com.your_group_name.your_project_name.server.controller;

import com.your_group_name.your_project_name.common.base.BaseController;
import com.your_group_name.your_project_name.common.response.R;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 示例控制器 - 用于验证服务是否正常运行
 */
@RestController
@RequestMapping("/api/fms")
public class HelloController extends BaseController {

    /**
     * 健康检查接口
     */
    @GetMapping("/health")
    public R<Map<String, Object>> health() {
        Map<String, Object> result = new HashMap<>();
        result.put("service", "fengqun-fms");
        result.put("status", "UP");
        result.put("timestamp", LocalDateTime.now());
        return success(result);
    }

    /**
     * 示例接口
     */
    @GetMapping("/hello")
    public R<String> hello() {
        return success("Hello from Fengqun FMS Server!");
    }
}
