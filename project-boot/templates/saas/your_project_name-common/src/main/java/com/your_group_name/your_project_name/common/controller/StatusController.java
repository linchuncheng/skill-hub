package com.your_group_name.your_project_name.common.controller;

import java.util.HashMap;
import java.util.Map;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 健康检查探针 Controller
 * 提供 Kubernetes 就绪探针和存活探针接口
 *
 * <p>
 * 探针路径约定：
 * <ul>
 * <li>/api/status/ready - 就绪探针，检查服务是否准备好接收流量</li>
 * <li>/api/status/live - 存活探针，检查服务是否存活</li>
 * </ul>
 */
@RestController
@RequestMapping("/api/status")
public class StatusController {

    /**
     * 就绪探针 (Readiness Probe)
     * Kubernetes 检查此接口，只有返回 200 时才将流量导入该 Pod
     *
     * @return 就绪状态
     */
    @GetMapping("/ready")
    public ResponseEntity<Map<String, Object>> ready() {
        Map<String, Object> result = new HashMap<>();
        result.put("status", "READY");
        result.put("timestamp", System.currentTimeMillis());
        return ResponseEntity.ok(result);
    }

    /**
     * 存活探针 (Liveness Probe)
     * Kubernetes 检查此接口，如果返回非 200 则重启 Pod
     *
     * @return 存活状态
     */
    @GetMapping("/live")
    public ResponseEntity<Map<String, Object>> live() {
        Map<String, Object> result = new HashMap<>();
        result.put("status", "ALIVE");
        result.put("timestamp", System.currentTimeMillis());
        return ResponseEntity.ok(result);
    }
}
