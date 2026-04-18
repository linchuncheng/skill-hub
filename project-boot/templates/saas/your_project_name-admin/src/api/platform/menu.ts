import { http } from '../http';
import {
    Menu,
    MenuCreateReq,
    MenuUpdateReq,
} from '../types/menu.schema';

/**
 * 获取菜单列表（树形结构）
 */
export const listMenus = async (): Promise<Menu[]> => {
  return http.get<Menu[]>('/api/platform/menu/tree');
};

/**
 * 获取菜单树（用于权限分配）
 * 超级管理员返回所有菜单，租户管理员只返回已拥有的菜单
 */
export const getMenuTreeForAssign = async (): Promise<Menu[]> => {
  return http.get<Menu[]>('/api/platform/menu/tree/assign');
};

/**
 * 创建菜单
 */
export const createMenu = async (data: MenuCreateReq): Promise<string> => {
  return http.post<string>('/api/platform/menu', {
    parentId: data.parentId,
    menuName: data.name,
    menuPath: data.path,
    component: data.component,
    icon: data.icon,
    sort: data.sort,
    permissionCode: data.permissionCode,
    status: data.status,
  });
};

/**
 * 更新菜单
 */
export const updateMenu = async (data: MenuUpdateReq): Promise<void> => {
  await http.put(`/api/platform/menu`, {
    id: data.id,
    parentId: data.parentId,
    menuName: data.name,
    menuPath: data.path,
    component: data.component,
    icon: data.icon,
    sort: data.sort,
    permissionCode: data.permissionCode,
    status: data.status,
  });
};

/**
 * 删除菜单
 */
export const deleteMenu = async (id: string): Promise<void> => {
  await http.delete(`/api/platform/menu/${id}`);
};
