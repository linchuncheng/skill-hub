package com.fengqun.scm.common.tenant;

import com.alibaba.ttl.TransmittableThreadLocal;

import java.util.function.Supplier;

/**
 * 租户上下文。
 *
 * 使用 TransmittableThreadLocal 存储当前线程的租户 ID 和租户类型。
 * 支持自动传递到新创建的线程（new Thread()）。
 */
public class TenantContext {

    private static final TransmittableThreadLocal<String> TENANT_ID_HOLDER = new TransmittableThreadLocal<>();
    private static final TransmittableThreadLocal<String> TENANT_TYPE_HOLDER = new TransmittableThreadLocal<>();
    private static final TransmittableThreadLocal<Long> USER_ID_HOLDER = new TransmittableThreadLocal<>();
    private static final TransmittableThreadLocal<Boolean> SKIP_TENANT_INTERCEPTOR = new TransmittableThreadLocal<>();

    /**
     * 设置当前租户 ID。
     *
     * @param tenantId 租户 ID
     */
    public static void setTenantId(String tenantId) {
        TENANT_ID_HOLDER.set(tenantId);
    }

    /**
     * 获取当前租户 ID。
     *
     * @return 租户 ID，若未设置则返回 null
     */
    public static String getTenantId() {
        return TENANT_ID_HOLDER.get();
    }

    /**
     * 设置当前租户类型。
     *
     * @param tenantType 租户类型：PLATFORM=超级管理员, TENANT_ADMIN=租户管理员, TENANT_USER=租户用户
     */
    public static void setTenantType(String tenantType) {
        TENANT_TYPE_HOLDER.set(tenantType);
    }

    /**
     * 获取当前租户类型。
     *
     * @return 租户类型，若未设置则返回 null
     */
    public static String getTenantType() {
        return TENANT_TYPE_HOLDER.get();
    }

    /**
     * 设置当前用户 ID。
     *
     * @param userId 用户 ID
     */
    public static void setUserId(Long userId) {
        USER_ID_HOLDER.set(userId);
    }

    /**
     * 获取当前用户 ID。
     *
     * @return 用户 ID，若未设置则返回 null
     */
    public static Long getUserId() {
        return USER_ID_HOLDER.get();
    }

    /**
     * 跳过租户拦截器执行指定函数。
     * <p>
     * 在函数执行期间临时跳过租户拦截器，执行完成后自动恢复。
     * 适用于定时任务查询所有租户数据的场景。
     *
     * @param supplier 需要跳过租户拦截器执行的函数
     * @param <T>      函数返回值类型
     * @return 函数执行结果
     */
    public static <T> T skip(Supplier<T> supplier) {
        try {
            SKIP_TENANT_INTERCEPTOR.set(true);
            T result = supplier.get();
            SKIP_TENANT_INTERCEPTOR.set(false);
            return result;
        } finally {
            SKIP_TENANT_INTERCEPTOR.remove();
        }
    }

    /**
     * 获取是否跳过租户拦截器。
     *
     * @return true=跳过租户拦截器
     */
    public static boolean isSkipTenantInterceptor() {
        return Boolean.TRUE.equals(SKIP_TENANT_INTERCEPTOR.get());
    }

    /**
     * 清除当前租户上下文（防止内存泄漏）。
     */
    public static void clear() {
        TENANT_ID_HOLDER.remove();
        TENANT_TYPE_HOLDER.remove();
        USER_ID_HOLDER.remove();
        SKIP_TENANT_INTERCEPTOR.remove();
    }
}
