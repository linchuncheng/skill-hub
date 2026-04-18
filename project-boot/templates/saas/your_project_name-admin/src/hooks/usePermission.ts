import { useAuthStore } from '@/stores/authStore';

/**
 * 权限判断 Hook
 */
export const usePermission = () => {
  const { permissions, hasPermission } = useAuthStore();

  /**
   * 检查是否拥有指定权限
   */
  const checkPermission = (permission: string): boolean => {
    return hasPermission(permission);
  };

  /**
   * 检查是否拥有任一权限
   */
  const hasAnyPermission = (permissionList: string[]): boolean => {
    return permissionList.some((p) => hasPermission(p));
  };

  /**
   * 检查是否拥有全部权限
   */
  const hasAllPermissions = (permissionList: string[]): boolean => {
    return permissionList.every((p) => hasPermission(p));
  };

  /**
   * 过滤出拥有的权限
   */
  const filterPermissions = (permissionList: string[]): string[] => {
    return permissionList.filter((p) => hasPermission(p));
  };

  return {
    permissions,
    checkPermission,
    hasAnyPermission,
    hasAllPermissions,
    filterPermissions,
  };
};

export default usePermission;
