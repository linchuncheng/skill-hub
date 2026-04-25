import { message } from 'antd';
import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import { useAuthStore } from '../stores/authStore';

const baseURL = import.meta.env.VITE_API_BASE_URL || '';

const axiosInstance: AxiosInstance = axios.create({
  baseURL,
  timeout: 30000,
});

// 导出带正确类型的 http 客户端
// 注意：响应拦截器已提取 response.data，所以返回类型是 T 而不是 R<T>
export const http = {
  get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return axiosInstance.get(url, config) as Promise<T>;
  },
  post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return axiosInstance.post(url, data, config) as Promise<T>;
  },
  put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return axiosInstance.put(url, data, config) as Promise<T>;
  },
  delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return axiosInstance.delete(url, config) as Promise<T>;
  },
};

// 请求拦截器：注入 Authorization 和 X-Tenant-Id header
axiosInstance.interceptors.request.use(
  (config) => {
    try {
      const { accessToken, user } = useAuthStore.getState();
      if (accessToken) {
        config.headers.Authorization = `Bearer ${accessToken}`;
      }
      // 注入租户 ID（从 user 对象中获取）
      if (user?.tenantId) {
        config.headers['X-Tenant-Id'] = user.tenantId;
      }
    } catch (error) {
      // authStore 还未加载，继续执行请求
      console.debug('authStore not yet loaded, proceeding without token');
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器：提取 response.data.data（后端标准响应格式 {code, msg, data}）
axiosInstance.interceptors.response.use(
  (response) => {
    const data = response.data;
    // 检查后端响应格式
    if (data && typeof data === 'object' && 'code' in data && 'data' in data) {
      // 标准响应格式 {code, msg, data}，提取 data 字段
      if (data.code === '200') {
        return data.data;
      } else {
        // 业务错误
        message.error(data.msg || '请求失败');
        return Promise.reject(new Error(data.msg || '请求失败'));
      }
    }
    // 非标准格式，直接返回
    return data;
  },
  async (error) => {
    const response = error.response;
    const status = response?.status;
    const data = response?.data as any;

    if (status === 401) {
      // Token 过期，尝试刷新
      try {
        const { refreshToken } = useAuthStore.getState();

        if (refreshToken) {
          const refreshResponse = await axios.post(
            `${baseURL}/api/auth/refresh-token`,
            { refresh_token: refreshToken }
          );
          const responseData = refreshResponse.data.data;

          // 更新 token（后端返回驼峰命名 accessToken, refreshToken）
          useAuthStore.getState().setAccessToken(responseData.accessToken);
          if (responseData.refreshToken) {
            useAuthStore.getState().setRefreshToken(responseData.refreshToken);
          }

          // 重试原始请求
          return axiosInstance(error.config);
        } else {
          // 无 refresh token，需要重新登录
          useAuthStore.getState().logout();
          window.location.href = '/login';
        }
      } catch (refreshError) {
        // 刷新失败，跳转登录
        useAuthStore.getState().logout();
        window.location.href = '/login';
      }
    }

    // 统一错误提示
    const errorMsg = data?.msg || error.message || '请求失败';
    message.error(errorMsg);
    return Promise.reject(error);
  }
);
