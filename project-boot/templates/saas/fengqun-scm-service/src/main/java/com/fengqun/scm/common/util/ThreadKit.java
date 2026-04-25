package com.fengqun.scm.common.util;

import com.fengqun.scm.common.tenant.TenantContext;

import lombok.extern.slf4j.Slf4j;

/**
 * 线程工具类。
 *
 * 提供异步任务执行功能,自动传递租户上下文。
 */
@Slf4j
public class ThreadKit {

    /**
     * 异步执行任务,自动传递租户上下文。
     *
     * <p>
     * 使用示例:
     * </p>
     * 
     * <pre>
     * ThreadKit.async(() -> {
     *     // 业务逻辑,自动拥有租户上下文
     *     orderService.assignWarehouse(orderId);
     * });
     * </pre>
     *
     * <p>
     * 带延迟执行:
     * </p>
     * 
     * <pre>
     * ThreadKit.async(() -> {
     *     // 业务逻辑
     * }, 1000); // 延迟1秒执行
     * </pre>
     *
     * @param task 异步任务
     */
    public static void async(Runnable task) {
        async(task, 0);
    }

    /**
     * 异步执行任务,自动传递租户上下文。
     *
     * @param task        异步任务
     * @param delayMillis 延迟时间(毫秒)
     */
    public static void async(Runnable task, long delayMillis) {
        // 在主线程中捕获租户上下文
        String tenantId = TenantContext.getTenantId();
        String tenantType = TenantContext.getTenantType();
        Long userId = TenantContext.getUserId();

        // 创建新线程执行任务
        new Thread(() -> {
            try {
                // 延迟执行(如果需要)
                if (delayMillis > 0) {
                    Thread.sleep(delayMillis);
                }

                // 在工作线程中恢复租户上下文
                TenantContext.setTenantId(tenantId);
                TenantContext.setTenantType(tenantType);
                TenantContext.setUserId(userId);

                // 执行实际任务
                task.run();

            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                log.warn("异步任务被中断", e);
            } catch (Exception e) {
                log.error("异步任务执行失败", e);
            } finally {
                // 清理线程上下文,防止内存泄漏
                TenantContext.clear();
            }
        }).start();
    }

    /**
     * 异步执行任务,自动传递租户上下文,支持自定义线程名。
     *
     * @param task       异步任务
     * @param threadName 线程名称
     */
    public static void async(Runnable task, String threadName) {
        async(task, 0, threadName);
    }

    /**
     * 异步执行任务,自动传递租户上下文,支持自定义线程名和延迟。
     *
     * @param task        异步任务
     * @param delayMillis 延迟时间(毫秒)
     * @param threadName  线程名称
     */
    public static void async(Runnable task, long delayMillis, String threadName) {
        // 在主线程中捕获租户上下文
        String tenantId = TenantContext.getTenantId();
        String tenantType = TenantContext.getTenantType();
        Long userId = TenantContext.getUserId();

        // 创建新线程执行任务
        Thread thread = new Thread(() -> {
            try {
                // 延迟执行(如果需要)
                if (delayMillis > 0) {
                    Thread.sleep(delayMillis);
                }

                // 在工作线程中恢复租户上下文
                TenantContext.setTenantId(tenantId);
                TenantContext.setTenantType(tenantType);
                TenantContext.setUserId(userId);

                // 执行实际任务
                task.run();

            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                log.warn("异步任务被中断: {}", threadName, e);
            } catch (Exception e) {
                log.error("异步任务执行失败: {}", threadName, e);
            } finally {
                // 清理线程上下文,防止内存泄漏
                TenantContext.clear();
            }
        });

        // 设置线程名
        if (threadName != null && !threadName.isEmpty()) {
            thread.setName(threadName);
        }

        thread.start();
    }
}
