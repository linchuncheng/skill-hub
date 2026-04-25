/**
 * 时间格式化工具
 * 
 * 统一将时间字符串格式化为 yyyy-MM-dd HH:mm:ss 格式
 */

/**
 * 格式化时间字符串
 * @param time 时间字符串（ISO格式或其他可解析格式）
 * @returns 格式化后的时间字符串 yyyy-MM-dd HH:mm:ss，如果输入为空则返回 '-'
 */
export function formatDateTime(time: string | number | Date | null | undefined): string {
  if (!time) return '-';
  
  const date = new Date(time);
  
  // 检查日期是否有效
  if (isNaN(date.getTime())) return '-';
  
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  const seconds = String(date.getSeconds()).padStart(2, '0');
  
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}

/**
 * 格式化日期字符串（仅日期部分）
 * @param time 时间字符串
 * @returns 格式化后的日期字符串 yyyy-MM-dd，如果输入为空则返回 '-'
 */
export function formatDate(time: string | number | Date | null | undefined): string {
  if (!time) return '-';
  
  const date = new Date(time);
  
  if (isNaN(date.getTime())) return '-';
  
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  
  return `${year}-${month}-${day}`;
}
