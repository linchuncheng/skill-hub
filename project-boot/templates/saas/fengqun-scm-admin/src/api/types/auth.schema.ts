import { z } from 'zod';
import { RSchema, UserInfoSchema } from './common.schema';

/**
 * 登录请求
 */
export const LoginReqSchema = z.object({
  username: z.string().min(1, '用户名不能为空'),
  password: z.string().min(1, '密码不能为空'),
});

export type LoginReq = z.infer<typeof LoginReqSchema>;

/**
 * 登录响应
 */
export const LoginRespSchema = z.object({
  accessToken: z.string(),
  refreshToken: z.string(),
  userInfo: UserInfoSchema,
  permissions: z.array(z.string()),
  menus: z.array(z.any()),
});

export type LoginResp = z.infer<typeof LoginRespSchema>;

/**
 * Token 刷新请求
 */
export const RefreshTokenReqSchema = z.object({
  refreshToken: z.string(),
});

export type RefreshTokenReq = z.infer<typeof RefreshTokenReqSchema>;

/**
 * Token 刷新响应
 */
export const RefreshTokenRespSchema = z.object({
  access_token: z.string(),
});

export type RefreshTokenResp = z.infer<typeof RefreshTokenRespSchema>;

/**
 * 用户信息导出
 */
export type UserInfo = z.infer<typeof UserInfoSchema>;

export const LoginRespDtoSchema = RSchema(LoginRespSchema);
export const RefreshTokenRespDtoSchema = RSchema(RefreshTokenRespSchema);
