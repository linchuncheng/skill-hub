import { http } from '../http';
import {
    LoginReq,
    LoginResp,
    RefreshTokenResp,
} from '../types/auth.schema';

/**
 * 登录
 */
export const login = async (data: LoginReq): Promise<LoginResp> => {
  return http.post<LoginResp>('/api/auth/login', data);
};

/**
 * 刷新 Token
 */
export const refreshToken = async (
  refreshToken: string
): Promise<RefreshTokenResp> => {
  return http.post<RefreshTokenResp>('/api/auth/refresh-token', {
    refresh_token: refreshToken,
  });
};

/**
 * 登出
 */
export const logout = async (): Promise<void> => {
  await http.post('/api/auth/logout', {});
};
