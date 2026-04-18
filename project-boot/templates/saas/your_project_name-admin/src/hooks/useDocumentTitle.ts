import { useAuthStore } from '@/stores/authStore';
import { useTenantStore } from '@/stores/tenantStore';
import { useEffect } from 'react';

const DEFAULT_TITLE = '企业运营管理平台';
const DEFAULT_FAVICON = '/default-favicon.svg';

/**
 * 动态页面标题和 Favicon Hook
 * 
 * 功能：
 * - 根据租户信息自动更新 document.title
 * - 根据租户 Logo 自动更新浏览器 favicon
 * - 未登录或租户信息未加载时显示默认标题和图标
 * - 租户切换时自动更新
 */
export function useDocumentTitle() {
  const currentTenant = useTenantStore((state) => state.currentTenant);
  const user = useAuthStore((state) => state.user);

  useEffect(() => {
    // 1. 更新页面标题
    const title = (user && currentTenant?.name)
      ? `${currentTenant.name} - ${DEFAULT_TITLE}`
      : DEFAULT_TITLE;
    document.title = title;

    // 2. 更新 favicon
    updateFavicon(currentTenant?.logo);

    // 3. 清理函数：组件卸载时恢复默认状态
    return () => {
      document.title = DEFAULT_TITLE;
      updateFavicon(DEFAULT_FAVICON);
    };
  }, [currentTenant?.name, currentTenant?.logo, user]);
}

/**
 * 更新浏览器 favicon
 * @param logoUrl 租户 Logo URL，如果为空则使用默认 favicon
 */
function updateFavicon(logoUrl?: string) {
  const href = logoUrl || DEFAULT_FAVICON;
  
  // 查找现有的 favicon link 元素
  let link = document.querySelector("link[rel~='icon']") as HTMLLinkElement;
  
  // 如果不存在则创建新的
  if (!link) {
    link = document.createElement('link');
    link.rel = 'icon';
    document.head.appendChild(link);
  }
  
  // 更新 href
  link.href = href;
}
