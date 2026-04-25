import { useAuthStore } from '@/stores/authStore';
import { Button, Result, Spin } from 'antd';
import { FC, PropsWithChildren, useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';

interface AuthGuardProps extends PropsWithChildren {
  permission?: string;
}

const AuthGuard: FC<AuthGuardProps> = ({ children, permission }) => {
  const { user, hasPermission } = useAuthStore();
  const [isHydrated, setIsHydrated] = useState(false);

  // 等待 zustand persist 从 localStorage 恢复数据
  useEffect(() => {
    // 检查 localStorage 中是否有 auth-store
    const hasStoredAuth = localStorage.getItem('auth-store');
    if (hasStoredAuth) {
      // 给 zustand 一些时间恢复数据
      const timer = setTimeout(() => {
        setIsHydrated(true);
      }, 100);
      return () => clearTimeout(timer);
    } else {
      // 没有存储的数据，立即完成
      setIsHydrated(true);
    }
  }, []);

  // 等待 hydrate 完成
  if (!isHydrated) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <Spin size="large" tip="加载中..." />
      </div>
    );
  }

  // 未登录
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // 超级管理员和租户管理员拥有默认权限，跳过权限验证
  if (user.tenantType === 'PLATFORM' || user.tenantType === 'TENANT_ADMIN') {
    return <>{children}</>;
  }

  // 需要权限且无权限
  if (permission && !hasPermission(permission)) {
    return (
      <Result
        status="403"
        title="403"
        subTitle="抱歉，您没有权限访问此页面"
        extra={
          <Button type="primary" onClick={() => window.history.back()}>
            返回
          </Button>
        }
      />
    );
  }

  return <>{children}</>;
};

export default AuthGuard;
