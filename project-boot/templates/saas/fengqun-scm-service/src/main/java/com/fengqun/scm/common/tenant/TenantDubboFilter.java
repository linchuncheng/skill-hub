package com.fengqun.scm.common.tenant;

import lombok.extern.slf4j.Slf4j;
import org.apache.dubbo.common.constants.CommonConstants;
import org.apache.dubbo.common.extension.Activate;
import org.apache.dubbo.rpc.Filter;
import org.apache.dubbo.rpc.Invocation;
import org.apache.dubbo.rpc.Invoker;
import org.apache.dubbo.rpc.Result;
import org.apache.dubbo.rpc.RpcContext;
import org.apache.dubbo.rpc.RpcException;

/**
 * Dubbo 租户 ID 透传过滤器。
 *
 * Consumer 端：从 TenantContext 读取 tenant_id，写入 Dubbo 隐式参数
 * Provider 端：从 Dubbo 隐式参数读取 tenant_id，注入 TenantContext
 */
@Slf4j
@Activate(group = { CommonConstants.PROVIDER, CommonConstants.CONSUMER }, order = -10000)
public class TenantDubboFilter implements Filter {

    /**
     * Dubbo 隐式参数 Key。
     */
    public static final String TENANT_ID_KEY = "tenant_id";

    @Override
    public Result invoke(Invoker<?> invoker, Invocation invocation) throws RpcException {
        // Consumer 端：将 TenantContext 中的 tenant_id 写入 Dubbo 隐式参数
        String tenantId = TenantContext.getTenantId();
        if (tenantId != null) {
            RpcContext.getClientAttachment().setAttachment(TENANT_ID_KEY, tenantId);
        }

        // Provider 端：从 Dubbo 隐式参数读取 tenant_id，注入 TenantContext
        String receivedTenantId = RpcContext.getServerAttachment().getAttachment(TENANT_ID_KEY);
        if (receivedTenantId != null) {
            TenantContext.setTenantId(receivedTenantId);
        }

        try {
            return invoker.invoke(invocation);
        } finally {
            // Provider 端：调用结束后清理上下文
            if (receivedTenantId != null) {
                TenantContext.clear();
            }
        }
    }
}
