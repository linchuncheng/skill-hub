import AuthGuard from '@/components/common/AuthGuard';
import BasicLayout from '@/components/layout/BasicLayout';
import { routes } from '@/config/routes';
import LoginPage from '@/modules/login';
import { Spin } from 'antd';
import { Suspense } from 'react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';

const Router = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* 登录路由 */}
        <Route path="/login" element={<LoginPage />} />

        {/* 受保护的路由 */}
        <Route
          path="/"
          element={
            <AuthGuard>
              <BasicLayout />
            </AuthGuard>
          }
        >
          {routes.map((route) => (
            <Route
              key={route.path}
              path={route.path}
              element={
                <AuthGuard permission={route.permission}>
                  <Suspense
                    fallback={
                      <Spin
                        size="large"
                        style={{ display: 'block', margin: '100px auto' }}
                      />
                    }
                  >
                    <route.component />
                  </Suspense>
                </AuthGuard>
              }
            />
          ))}
          <Route index element={<Navigate to="/dashboard" replace />} />
        </Route>

        {/* 404 路由 */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  );
};

export default Router;
