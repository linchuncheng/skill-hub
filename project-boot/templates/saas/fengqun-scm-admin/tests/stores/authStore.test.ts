import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { useAuthStore } from '@/stores/authStore';

describe('Auth Store', () => {
  beforeEach(() => {
    // 清除 localStorage
    localStorage.clear();
    // 重置状态
    useAuthStore.setState({
      user: null,
      accessToken: null,
      refreshToken: null,
      permissions: [],
      menus: [],
    });
  });

  afterEach(() => {
    localStorage.clear();
  });

  it('should set user info', () => {
    const store = useAuthStore.getState();
    const mockUser = {
      user_id: 'user-001',
      username: 'testuser',
      tenant_id: 'tenant-001',
      tenant_type: 'PLATFORM' as const,
    };

    store.setUser(mockUser);

    expect(useAuthStore.getState().user).toEqual(mockUser);
    expect(useAuthStore.getState().user?.username).toBe('testuser');
  });

  it('should check permission - has permission', () => {
    const store = useAuthStore.getState();

    // 设置权限
    store.setPermissions(['user:read', 'user:write', 'role:read']);

    // 验证有权限
    expect(store.hasPermission('user:read')).toBe(true);
    expect(store.hasPermission('user:write')).toBe(true);
    expect(store.hasPermission('role:read')).toBe(true);
  });

  it('should check permission - no permission', () => {
    const store = useAuthStore.getState();

    // 设置权限
    store.setPermissions(['user:read', 'user:write']);

    // 验证没有权限
    expect(store.hasPermission('role:delete')).toBe(false);
    expect(store.hasPermission('admin:all')).toBe(false);
  });

  it('should logout and clear state', () => {
    const store = useAuthStore.getState();
    const mockUser = {
      user_id: 'user-001',
      username: 'testuser',
      tenant_id: 'tenant-001',
      tenant_type: 'PLATFORM' as const,
    };

    // 设置初始状态
    store.setUser(mockUser);
    store.setAccessToken('access-token-123');
    store.setRefreshToken('refresh-token-456');
    store.setPermissions(['read', 'write']);
    store.setMenus([{ id: 'menu-1', name: 'Dashboard' }]);

    // 验证状态已设置
    expect(useAuthStore.getState().user).not.toBeNull();
    expect(useAuthStore.getState().accessToken).not.toBeNull();
    expect(useAuthStore.getState().refreshToken).not.toBeNull();
    expect(useAuthStore.getState().permissions.length).toBeGreaterThan(0);

    // 调用 logout
    store.logout();

    // 验证状态已清空
    expect(useAuthStore.getState().user).toBeNull();
    expect(useAuthStore.getState().accessToken).toBeNull();
    expect(useAuthStore.getState().refreshToken).toBeNull();
    expect(useAuthStore.getState().permissions).toEqual([]);
    expect(useAuthStore.getState().menus).toEqual([]);
  });

  it('should set auth data with all fields', () => {
    const store = useAuthStore.getState();
    const mockAuthData = {
      user: {
        user_id: 'user-001',
        username: 'testuser',
        tenant_id: 'tenant-001',
        tenant_type: 'PLATFORM' as const,
      },
      access_token: 'access-token-123',
      refresh_token: 'refresh-token-456',
      permissions: ['read', 'write', 'delete'],
      menus: [
        { id: 'menu-1', name: 'Dashboard' },
        { id: 'menu-2', name: 'Users' },
      ],
    };

    store.setAuthData(mockAuthData);

    const state = useAuthStore.getState();
    expect(state.user).toEqual(mockAuthData.user);
    expect(state.accessToken).toBe('access-token-123');
    expect(state.refreshToken).toBe('refresh-token-456');
    expect(state.permissions).toEqual(['read', 'write', 'delete']);
    expect(state.menus).toEqual(mockAuthData.menus);
  });

  it('should handle empty permissions array', () => {
    const store = useAuthStore.getState();

    store.setPermissions([]);

    expect(useAuthStore.getState().permissions).toEqual([]);
    expect(store.hasPermission('any:permission')).toBe(false);
  });
});
