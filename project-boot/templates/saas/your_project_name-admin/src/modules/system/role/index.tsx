import {
    assignMenus,
    assignPermissions,
    createRole,
    deleteRole,
    disableRole,
    enableRole,
    getDefaultPermissions,
    getMenuTreeForAssign,
    getPermissionTreeForAssign,
    getRoleMenus,
    getRolePermissions,
    listRoles,
    updateRole,
} from '@/api/platform/role';
import type { MenuTree, PermissionTree, Role, RoleCreateReq, RoleUpdateReq } from '@/api/types/role.schema';
import { FilterBar, PageTable } from '@/components/common/PageTable';
import { TableColumnActions } from '@/components/common/TableColumnActions';
import TenantSelect from '@/components/common/TenantSelect';
import { useAuthStore } from '@/stores/authStore';
import {
    CheckOutlined,
    CloseOutlined,
    DeleteOutlined,
    EditOutlined,
    PlusOutlined,
    ReloadOutlined,
    SearchOutlined,
    SettingOutlined,
} from '@ant-design/icons';
import {
    Button,
    Checkbox,
    Form,
    Input,
    message,
    Modal,
    Tag,
    Tree
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import type { DataNode } from 'antd/es/tree';
import { FC, useEffect, useMemo, useState } from 'react';

const RolePage: FC = () => {
  const [roles, setRoles] = useState<Role[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingRole, setEditingRole] = useState<Role | null>(null);
  const [form] = Form.useForm();
  const { hasPermission, user } = useAuthStore();

  // 筛选条件
  const [selectedTenantId, setSelectedTenantId] = useState<string | undefined>(undefined);
  const [searchKeyword, setSearchKeyword] = useState<string>('');

  // 判断是否是超级管理员
  const isPlatformAdmin = () => {
    return user?.tenantType === 'PLATFORM' && user?.tenantId === '0';
  };

  // 检查权限（超级管理员拥有所有权限）
  const checkPermission = (permission: string) => {
    return isPlatformAdmin() || hasPermission(permission);
  };

  // 合并的菜单+权限分配弹窗状态
  const [assignModalVisible, setAssignModalVisible] = useState(false);
  const [assignLoading, setAssignLoading] = useState(false);
  const [assigningRoleId, setAssigningRoleId] = useState<any>(null);
  const [_assigningRole, setAssigningRole] = useState<Role | null>(null); // 当前分配的角色信息

  // 菜单树数据
  const [menuTree, setMenuTree] = useState<MenuTree[]>([]);
  const [selectedMenus, setSelectedMenus] = useState<any[]>([]);

  // 权限树数据
  const [rawPermissionTree, setRawPermissionTree] = useState<PermissionTree[]>([]);
  const [selectedPermissions, setSelectedPermissions] = useState<any[]>([]);

  // 默认禁用的菜单和权限（从后端获取）
  const [defaultMenuIds, setDefaultMenuIds] = useState<Set<string>>(new Set());
  const [defaultPermissionIds, setDefaultPermissionIds] = useState<Set<string>>(new Set());
  // 禁止分配的菜单和权限（从后端获取，不显示在树中）
  const [forbiddenMenuIds, setForbiddenMenuIds] = useState<Set<string>>(new Set());
  const [forbiddenPermissionIds, setForbiddenPermissionIds] = useState<Set<string>>(new Set());

  // 当前选中的菜单节点（已不需要，保留以兼容关闭弹窗时清空）
  const [_activeMenuKey, setActiveMenuKey] = useState<string | null>(null);

  const loadRoles = async (tenantId?: string, keyword?: string) => {
    setLoading(true);
    try {
      // 超级管理员可以按租户筛选，租户管理员只能看到当前租户的角色
      const filterTenantId = isPlatformAdmin() ? tenantId : user?.tenantId;
      const data = await listRoles(filterTenantId);
      // 前端过滤关键词（角色编码、角色名称）
      let filtered: Role[] = data;
      if (keyword && keyword.trim()) {
        const kw = keyword.trim().toLowerCase();
        filtered = data.filter((role: Role) =>
          role.roleCode?.toLowerCase().includes(kw) ||
          role.roleName?.toLowerCase().includes(kw)
        );
      }
      setRoles(filtered);
    } catch (error: any) {
      message.error(error.message || '加载失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRoles();
  }, []);

  const handleCreate = () => {
    setEditingRole(null);
    form.resetFields();
    // 如果超级管理员已选择租户，默认带上租户ID
    if (isPlatformAdmin() && selectedTenantId) {
      form.setFieldsValue({ tenantId: selectedTenantId });
    }
    setModalVisible(true);
  };

  const handleEdit = (record: Role) => {
    setEditingRole(record);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  const handleModalOk = async () => {
    try {
      const values = await form.validateFields();

      if (editingRole) {
        // Update
        await updateRole({ id: editingRole.id, ...values } as RoleUpdateReq);
        message.success('更新成功');
      } else {
        // Create - 处理租户ID
        const createData: RoleCreateReq = { ...values };
        // 如果是租户管理员，默认使用当前租户ID
        if (!isPlatformAdmin() && user?.tenantId) {
          createData.tenantId = user.tenantId;
        }
        // 如果是超级管理员且没有选择租户，使用当前筛选的租户
        if (isPlatformAdmin() && !createData.tenantId && selectedTenantId) {
          createData.tenantId = selectedTenantId;
        }
        await createRole(createData);
        message.success('创建成功');
      }

      setModalVisible(false);
      loadRoles(selectedTenantId);
    } catch (error: any) {
      message.error(error.message || '操作失败');
    }
  };

  const handleDelete = async (id: any) => {
    try {
      await deleteRole(id);
      message.success('删除成功');
      loadRoles(selectedTenantId);
    } catch (error: any) {
      message.error(error.message || '删除失败');
    }
  };

  const handleToggleStatus = async (record: Role) => {
    try {
      if (record.status === 1) {
        await disableRole(record.id);
        message.success('已禁用');
      } else {
        await enableRole(record.id);
        message.success('已启用');
      }
      loadRoles(selectedTenantId);
    } catch (error: any) {
      message.error(error.message || '操作失败');
    }
  };

  // 将菜单和权限合并构建一棵树（支持默认禁用和禁止分配）
  const buildMergedTree = (
    menus: MenuTree[],
    permTree: PermissionTree[],
    disabledMenuIds: Set<string>,
    disabledPermIds: Set<string>,
    hiddenMenuIds: Set<string>,     // 禁止分配的菜单
    hiddenPermIds: Set<string>      // 禁止分配的权限
  ): DataNode[] => {
    // 构建两种索引：
    // 1. 按 code 分组（有子节点的权限组）： { "platform:tenant": [child1, child2, ...] }
    // 2. 按 code 单个权限（无子节点的单个权限）： { "platform:dashboard:view": permNode }
    const permGroups: Record<string, PermissionTree[]> = {};
    const permLeaves: Record<string, PermissionTree> = {};
    const walkPerms = (nodes: PermissionTree[]) => {
      nodes.forEach((p) => {
        if (p.children?.length) {
          permGroups[p.permissionCode] = p.children;
        } else {
          permLeaves[p.permissionCode] = p;
        }
      });
    };
    walkPerms(permTree);

    const convertMenu = (menuNodes: MenuTree[]): DataNode[] => {
      // 过滤掉禁止分配的菜单
      const filteredMenus = menuNodes.filter(menu => !hiddenMenuIds.has(String(menu.id)));
      
      return filteredMenus.map((menu) => {
        const menuKey = `menu_${menu.id}`;
        const isMenuDisabled = disabledMenuIds.has(String(menu.id));
        
        // 根据菜单的 permissionCode 找匹配的权限分组
        const menuPermCode = menu.permissionCode;
        let permChildren: DataNode[] = [];
        if (menuPermCode) {
          // 菜单 permissionCode 格式为 "platform:tenant:list"
          // 权限分组 code 格式为 "platform:tenant"
          // 去掉最后一个 ":xxx" 就是对应的权限分组 code
          const parts = menuPermCode.split(':');
          const groupCode = parts.length >= 3 ? parts.slice(0, -1).join(':') : menuPermCode;
          const group = permGroups[groupCode];
          if (group?.length) {
            // 匹配到权限分组（如租户管理、用户管理等）
            // 过滤掉禁止分配的权限
            const filteredGroup = group.filter(p => !hiddenPermIds.has(String(p.id)));
            permChildren = filteredGroup.map((p) => {
              const isPermDisabled = disabledPermIds.has(String(p.id));
              return {
                title: (
                  <span style={{ color: isPermDisabled ? '#999' : '#1677ff', fontSize: 13 }}>
                    {p.permissionName}{isPermDisabled ? '（默认）' : ''}
                  </span>
                ),
                key: `perm_${p.id}`,
                disableCheckbox: isPermDisabled,
              };
            });
          } else if (permLeaves[menuPermCode]) {
            // 匹配到单个权限（如首页、权限测试）
            const leaf = permLeaves[menuPermCode];
            // 过滤掉禁止分配的权限
            if (!hiddenPermIds.has(String(leaf.id))) {
            const isPermDisabled = disabledPermIds.has(String(leaf.id));
            permChildren = [{
              title: (
                <span style={{ color: isPermDisabled ? '#999' : '#1677ff', fontSize: 13 }}>
                  {leaf.permissionName}{isPermDisabled ? '（默认）' : ''}
                </span>
              ),
              key: `perm_${leaf.id}`,
              disableCheckbox: isPermDisabled,
            }];
            }
          }
        }

        // 子菜单递归转换
        const subMenuChildren = menu.children?.length ? convertMenu(menu.children) : [];
        const allChildren = [...subMenuChildren, ...permChildren];

        return {
          title: (
            <span style={{ fontWeight: 500, color: isMenuDisabled ? '#999' : undefined }}>
              {menu.name}{isMenuDisabled ? '（默认）' : ''}
            </span>
          ),
          key: menuKey,
          disableCheckbox: isMenuDisabled,
          children: allChildren.length > 0 ? allChildren : undefined,
        };
      });
    };

    return convertMenu(menus);
  };

  // 打平合并树（获取所有 key）
  const flattenMergedTree = (nodes: DataNode[]): string[] => {
    const keys: string[] = [];
    const walk = (ns: DataNode[]) => {
      ns.forEach((n) => {
        keys.push(n.key as string);
        if (n.children?.length) walk(n.children as DataNode[]);
      });
    };
    walk(nodes);
    return keys;
  };

  // 打开合并弹窗
  const handleOpenAssignModal = async (roleId: any) => {
    try {
      setAssigningRoleId(roleId);
      setAssignLoading(true);
      setActiveMenuKey(null);

      // 找到当前角色信息
      const currentRole = roles.find((r) => String(r.id) === String(roleId)) || null;
      setAssigningRole(currentRole);

      const [menus, permTree, assignedMenuIds, assignedPermIds, defaultPerms] = await Promise.all([
        getMenuTreeForAssign(),
        getPermissionTreeForAssign(roleId),  // 传入 roleId
        getRoleMenus(roleId),
        getRolePermissions(roleId),
        getDefaultPermissions(roleId),  // 从后端获取默认权限配置
      ]);

      setMenuTree(menus);
      setRawPermissionTree(permTree);
      setSelectedMenus(assignedMenuIds);
      setSelectedPermissions(assignedPermIds);
      // 设置默认禁用的菜单和权限（从后端获取）
      setDefaultMenuIds(new Set(defaultPerms.defaultMenuIds.map(String)));
      setDefaultPermissionIds(new Set(defaultPerms.defaultPermissionIds.map(String)));
      // 设置禁止分配的菜单和权限（从后端获取）
      setForbiddenMenuIds(new Set((defaultPerms.forbiddenMenuIds || []).map(String)));
      setForbiddenPermissionIds(new Set((defaultPerms.forbiddenPermissionIds || []).map(String)));
      setAssignModalVisible(true);
    } catch (error: any) {
      message.error(error.message || '加载失败');
    } finally {
      setAssignLoading(false);
    }
  };

  // 保存分配（菜单 + 权限同时保存）
  const handleAssignModalOk = async () => {
    try {
      if (!assigningRoleId) return;
      setAssignLoading(true);

      // 确保包含默认禁用的菜单和权限（从 state 获取）
      const finalMenus = new Set<any>([...selectedMenus, ...Array.from(defaultMenuIds)]);
      const finalPerms = new Set<any>([...selectedPermissions, ...Array.from(defaultPermissionIds)]);

      await Promise.all([
        assignMenus(assigningRoleId, Array.from(finalMenus)),
        assignPermissions(assigningRoleId, Array.from(finalPerms)),
      ]);

      message.success('分配成功');
      setAssignModalVisible(false);
      setAssigningRole(null);
      // 清空默认权限和禁止分配 state
      setDefaultMenuIds(new Set());
      setDefaultPermissionIds(new Set());
      setForbiddenMenuIds(new Set());
      setForbiddenPermissionIds(new Set());
      loadRoles(selectedTenantId);
    } catch (error: any) {
      message.error(error.message || '分配失败');
    } finally {
      setAssignLoading(false);
    }
  };

  // 当前弹窗的合并树（菜单+权限）
  const mergedTree = useMemo(
    () => buildMergedTree(menuTree, rawPermissionTree, defaultMenuIds, defaultPermissionIds, forbiddenMenuIds, forbiddenPermissionIds),
    [menuTree, rawPermissionTree, defaultMenuIds, defaultPermissionIds, forbiddenMenuIds, forbiddenPermissionIds]
  );
  const allMergedKeys = useMemo(() => flattenMergedTree(mergedTree), [mergedTree]);
  
  // 计算默认禁用的 key 列表（用于保存时自动添加，保留备用）
  useMemo(() => {
    const keys: string[] = [];
    // 菜单 keys
    defaultMenuIds.forEach((id) => keys.push(`menu_${id}`));
    // 权限 keys
    defaultPermissionIds.forEach((id) => keys.push(`perm_${id}`));
    return keys;
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
  }, [defaultMenuIds, defaultPermissionIds]);

  const checkedMergedKeys = useMemo(
    () => {
      // 默认权限不勾选（显示为未选中+禁止），保存时后端会自动添加
      const keys = new Set<string>([
        ...selectedMenus.map((id: any) => `menu_${id}`),
        ...selectedPermissions.map((id: any) => `perm_${id}`),
      ]);
      return Array.from(keys);
    },
    [selectedMenus, selectedPermissions]
  );

  // 处理租户筛选变更
  const handleTenantChange = (tenantId: string | undefined) => {
    setSelectedTenantId(tenantId);
    loadRoles(tenantId, searchKeyword);
  };

  // 搜索
  const handleSearch = () => {
    loadRoles(selectedTenantId, searchKeyword);
  };

  // 重置筛选条件
  const handleReset = () => {
    setSelectedTenantId(undefined);
    setSearchKeyword('');
    loadRoles(undefined, '');
  };

  const columns: ColumnsType<Role> = [
    {
      title: '角色编码',
      dataIndex: 'roleCode',
      key: 'roleCode',
    },
    {
      title: '角色名称',
      dataIndex: 'roleName',
      key: 'roleName',
    },
    {
      title: '租户名称',
      dataIndex: 'tenantName',
      key: 'tenantName',
      render: (tenantName: string) => tenantName || '-',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: number) =>
        status === 1 ? <Tag color="green">启用</Tag> : <Tag color="red">禁用</Tag>,
    },
    {
      title: '创建时间',
      dataIndex: 'createdAt',
      key: 'createdAt',
    },
    TableColumnActions<Role>({
      width: 240,
      actions: (record) => [
        ...(checkPermission('platform:role:edit') ? [{
          key: 'edit',
          label: '编辑',
          icon: <EditOutlined />,
          onClick: () => handleEdit(record),
        }] : []),
        ...((checkPermission('platform:role:assign-permission') || checkPermission('platform:role:assign-menu')) ? [{
          key: 'assign',
          label: '权限分配',
          icon: <SettingOutlined />,
          onClick: () => handleOpenAssignModal(record.id),
        }] : []),
        ...(checkPermission('platform:role:edit') ? [{
          key: 'toggle',
          label: record.status === 1 ? '禁用' : '启用',
          icon: record.status === 1 ? <CloseOutlined /> : <CheckOutlined />,
          onClick: () => handleToggleStatus(record),
        }] : []),
        ...(checkPermission('platform:role:delete') ? [{
          key: 'delete',
          label: '删除',
          icon: <DeleteOutlined />,
          onClick: () => handleDelete(record.id),
          danger: true,
          needConfirm: true,
        }] : []),
      ],
    }),
  ];

  return (
    <>
      <PageTable
        filterBar={
          <FilterBar>
            {/* 超级管理员可见的租户筛选 */}
            {isPlatformAdmin() && (
              <TenantSelect
                style={{ width: 200 }}
                placeholder="选择租户进行筛选"
                showAll
                value={selectedTenantId}
                onChange={handleTenantChange}
              />
            )}
            {/* 搜索输入框 */}
            <Input
              style={{ width: 200 }}
              placeholder="角色编码/名称"
              value={searchKeyword}
              onChange={(e) => setSearchKeyword(e.target.value)}
              onPressEnter={handleSearch}
              allowClear
            />
            <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch}>
              搜索
            </Button>
            <Button icon={<ReloadOutlined />} onClick={handleReset}>
              重置
            </Button>
            {checkPermission('platform:role:create') && (
              <FilterBar.Action>
                <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
                  新增角色
                </Button>
              </FilterBar.Action>
            )}
          </FilterBar>
        }
        columns={columns}
        dataSource={roles}
        rowKey="id"
        loading={loading}
      />

      {/* Role CRUD Modal */}
      <Modal
        title={editingRole ? '编辑角色' : '新增角色'}
        open={modalVisible}
        onOk={handleModalOk}
        onCancel={() => setModalVisible(false)}
        width={600}
      >
        <Form form={form} layout="vertical">
          {/* 超级管理员新增/编辑角色时可以选择租户 */}
          {isPlatformAdmin() && (
            <Form.Item
              name="tenantId"
              label="所属租户"
              rules={[{ required: true, message: '请选择所属租户' }]}
            >
              <TenantSelect placeholder="请选择所属租户" />
            </Form.Item>
          )}
          <Form.Item
            name="roleCode"
            label="角色编码"
            rules={[{ required: true, message: '请输入角色编码' }]}
          >
            <Input
              placeholder="请输入角色编码"
              disabled={!!editingRole}  // 编辑模式下禁用
            />
          </Form.Item>
          <Form.Item
            name="roleName"
            label="角色名称"
            rules={[{ required: true, message: '请输入角色名称' }]}
          >
            <Input placeholder="请输入角色名称" />
          </Form.Item>
        </Form>
      </Modal>

      {/* 合并的菜单+权限分配弹窗 - 单棵合并树 */}
      <Modal
        title="分配菜单与权限"
        open={assignModalVisible}
        onOk={handleAssignModalOk}
        onCancel={() => {
          setAssignModalVisible(false);
          setSelectedMenus([]);
          setSelectedPermissions([]);
          setActiveMenuKey(null);
          setAssigningRole(null);
        }}
        width={520}
        confirmLoading={assignLoading}
        okText="确 定"
        cancelText="取 消"
      >
        {menuTree.length > 0 ? (
          <div style={{ maxHeight: 480, overflowY: 'auto' }}>
            <div style={{ marginBottom: 8 }}>
              <Checkbox
                checked={checkedMergedKeys.length > 0 && checkedMergedKeys.length === allMergedKeys.length}
                indeterminate={checkedMergedKeys.length > 0 && checkedMergedKeys.length < allMergedKeys.length}
                onChange={(e) => {
                  if (e.target.checked) {
                    const menuIds = allMergedKeys.filter((k: string) => k.startsWith('menu_')).map((k: string) => k.replace('menu_', ''));
                    const permIds = allMergedKeys.filter((k: string) => k.startsWith('perm_')).map((k: string) => k.replace('perm_', ''));
                    setSelectedMenus(menuIds);
                    setSelectedPermissions(permIds);
                  } else {
                    setSelectedMenus([]);
                    setSelectedPermissions([]);
                  }
                }}
              >
                全选
              </Checkbox>
            </div>
            <Tree
              checkable
              defaultExpandAll
              checkedKeys={checkedMergedKeys}
              onCheck={(checked) => {
                const checkedArr = checked as string[];
                const menuIds = checkedArr.filter((k) => k.startsWith('menu_')).map((k) => k.replace('menu_', ''));
                const permIds = checkedArr.filter((k) => k.startsWith('perm_')).map((k) => k.replace('perm_', ''));
                setSelectedMenus(menuIds);
                setSelectedPermissions(permIds);
              }}
              treeData={mergedTree}
            />
          </div>
        ) : (
          <div style={{ padding: '40px', textAlign: 'center', color: '#999' }}>加载中...</div>
        )}
      </Modal>
    </>
  );
};

export default RolePage;
