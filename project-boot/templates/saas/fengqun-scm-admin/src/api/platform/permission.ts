import { http } from '../http';
import { Permission, PermissionListRespSchema } from '../types/permission.schema';

/**
 * 获取权限列表（分页）
 */
export const listPermissions = async (
  page: number = 1,
  size: number = 100
): Promise<Permission[]> => {
  const response = await http.get('/api/platform/permission/list', {
    params: {
      current: page,
      size,
    },
  });
  const validated = PermissionListRespSchema.parse(response);
  return validated.data.records;
};
