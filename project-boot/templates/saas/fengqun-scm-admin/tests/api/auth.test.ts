import { describe, it, expect, vi, beforeEach } from 'vitest';
import { login, refreshToken, logout } from '@/api/auth';
import { http } from '@/api/http';

vi.mock('@/api/http');

describe('Auth API', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should login successfully', async () => {
    // 准备 mock 响应 (符合 R<LoginResp> 格式)
    const mockResponseData = {
      code: '200',
      msg: '操作成功',
      data: {
        access_token: 'mock-access-token-123',
        refresh_token: 'mock-refresh-token-456',
        user_info: {
          user_id: 'user-001',
          username: 'testuser',
          tenant_id: 'tenant-001',
          tenant_type: 'PLATFORM' as const,
        },
        permissions: ['read', 'write'],
        menus: [
          {
            id: 'menu-1',
            name: 'Dashboard',
          },
        ],
      },
    };

    // 设置 http.post mock (http 响应拦截器返回 response.data)
    vi.mocked(http.post).mockResolvedValueOnce(mockResponseData);

    // 调用被测试方法
    const result = await login({
      username: 'testuser',
      password: 'password123',
    });

    // 验证结果
    expect(result).toBeDefined();
    expect(result.access_token).toBe('mock-access-token-123');
    expect(result.refresh_token).toBe('mock-refresh-token-456');
    expect(result.user_info.username).toBe('testuser');
    expect(result.permissions).toContain('read');
    expect(result.permissions).toContain('write');

    // 验证调用
    expect(vi.mocked(http.post)).toHaveBeenCalledWith('/api/auth/login', {
      username: 'testuser',
      password: 'password123',
    });
  });

  it('should refresh token successfully', async () => {
    // 准备 mock 响应 (符合 R<RefreshTokenResp> 格式，只包含 access_token)
    const mockResponseData = {
      code: '200',
      msg: '操作成功',
      data: {
        access_token: 'mock-new-access-token',
      },
    };

    // 设置 http.post mock (http 响应拦截器返回 response.data)
    vi.mocked(http.post).mockResolvedValueOnce(mockResponseData);

    // 调用被测试方法
    const result = await refreshToken('mock-refresh-token-456');

    // 验证结果
    expect(result).toBeDefined();
    expect(result.access_token).toBe('mock-new-access-token');

    // 验证调用
    expect(vi.mocked(http.post)).toHaveBeenCalledWith(
      '/api/auth/refresh-token',
      {
        refresh_token: 'mock-refresh-token-456',
      }
    );
  });

  it('should handle login failure', async () => {
    // 设置 http.post mock 抛出错误
    const mockError = new Error('Invalid credentials');
    vi.mocked(http.post).mockRejectedValueOnce(mockError);

    // 调用被测试方法并验证错误
    await expect(
      login({
        username: 'testuser',
        password: 'wrongpassword',
      })
    ).rejects.toThrow();
  });

  it('should logout successfully', async () => {
    // 设置 http.post mock
    vi.mocked(http.post).mockResolvedValueOnce(undefined);

    // 调用被测试方法
    await logout();

    // 验证调用
    expect(vi.mocked(http.post)).toHaveBeenCalledWith('/api/auth/logout', {});
  });
});
