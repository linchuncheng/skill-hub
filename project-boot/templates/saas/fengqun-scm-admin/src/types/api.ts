/**
 * 标准响应体：{code, msg, data}
 */
export interface R<T = any> {
  code: string;
  msg: string;
  data: T;
}

/**
 * 分页响应体
 */
export interface Page<T> {
  records: T[];
  total: number;
  size: number;
  current: number;
  pages: number;
}

/**
 * HTTP 错误响应
 */
export interface ApiError {
  code: string;
  msg: string;
  timestamp: number;
}
