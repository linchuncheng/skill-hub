import { lazy } from 'react';

export interface RouteConfig {
  path: string;
  component: React.LazyExoticComponent<any>;
  permission?: string;
  name?: string;
}

export const routes: RouteConfig[] = [
  {
    path: '/dashboard',
    component: lazy(() => import('@/pages/dashboard')),
    // 首页不需要权限，所有登录用户都可访问
    name: '首页',
  },
  {
    path: '/system/tenant',
    component: lazy(() => import('@/modules/system/tenant')),
    permission: 'platform:tenant:list',
    name: '租户管理',
  },
  {
    path: '/system/user',
    component: lazy(() => import('@/modules/system/user')),
    permission: 'platform:user:list',
    name: '用户管理',
  },
  {
    path: '/system/role',
    component: lazy(() => import('@/modules/system/role')),
    permission: 'platform:role:list',
    name: '角色管理',
  },
  {
    path: '/system/menu',
    component: lazy(() => import('@/modules/system/menu')),
    permission: 'platform:menu:list',
    name: '菜单管理',
  },
  {
    path: '/test',
    component: lazy(() => import('@/pages/test')),
    permission: 'platform:test:view',
    name: '权限测试',
  },
  {
    path: '/settings',
    component: lazy(() => import('@/modules/system/settings')),
    name: '系统设置',
  }
];
