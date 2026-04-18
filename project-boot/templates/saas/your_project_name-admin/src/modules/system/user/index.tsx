import {
    assignRoles,
    createUser,
    deleteUser,
    disableUser,
    enableUser,
    getRoleList,
    getUserRoles,
    listUsers,
    resetPassword,
    updateUser,
} from '@/api/platform/user';
import type { Tenant } from '@/api/types/tenant.schema';
import type { Role, User, UserCreateReq, UserUpdateReq } from '@/api/types/user.schema';
import { FilterBar, PageTable } from '@/components/common/PageTable';
import { TableColumnActions } from '@/components/common/TableColumnActions';
import TenantSelect from '@/components/common/TenantSelect';
import { useAuthStore } from '@/stores/authStore';
import {
    CheckOutlined,
    CloseOutlined,
    DeleteOutlined,
    EditOutlined,
    KeyOutlined,
    PlusOutlined,
    ReloadOutlined,
    SearchOutlined,
    TeamOutlined,
} from '@ant-design/icons';
import {
    Button,
    Checkbox,
    Form,
    Input,
    message,
    Modal,
    Select,
    Tag
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { FC, useCallback, useEffect, useState } from 'react';

const UserPage: FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();
  const { hasPermission, user: currentUser } = useAuthStore();

  // 筛选条件（拆分为独立输入框）
  const [selectedTenantId, setSelectedTenantId] = useState<string | undefined>(undefined);
  const [filterUsername, setFilterUsername] = useState<string>('');
  const [filterEmail, setFilterEmail] = useState<string>('');
  const [filterPhone, setFilterPhone] = useState<string>('');

  // 判断是否是超级管理员
  const isPlatformAdmin = () => {
    return currentUser?.tenantType === 'PLATFORM';
  };

  // 检查权限（超级管理员自动拥有所有权限）
  const checkPermission = (permission: string) => {
    if (isPlatformAdmin()) {
      return true;
    }
    return hasPermission(permission);
  };

  // User CRUD Modal state
  const [editingModalState, setEditingModalState] = useState({
    visible: false,
    editingUser: null as User | null,
  });

  // Role assignment modal state
  const [roleModal, setRoleModal] = useState({
    visible: false,
    loading: false,
    userId: null as string | number | null,
    list: [] as Role[],
    selected: [] as (string | number)[],
  });

  // Password reset modal state
  const [passwordModal, setPasswordModal] = useState({
    visible: false,
    loading: false,
    userId: null as string | number | null,
    newPassword: '',
  });

  // 检查当前租户是否已有租户管理员
  const [hasTenantAdmin, setHasTenantAdmin] = useState(false);
  // 当前选中的租户是否是默认租户（只有默认租户才支持超级管理员）
  const [isDefaultTenant, setIsDefaultTenant] = useState(false);
  
  const checkTenantAdminExists = async (tenantId: string) => {
    try {
      const users = await listUsers(tenantId);
      const exists = users.some((u: User) => u.tenantType === 'TENANT_ADMIN');
      setHasTenantAdmin(exists);
    } catch {
      setHasTenantAdmin(false);
    }
  };
  
  // 处理租户变更，检查是否是默认租户
  const handleTenantSelectChange = (tenant: Tenant | null) => {
    if (tenant) {
      setIsDefaultTenant(tenant.tenantCode === 'default');
      checkTenantAdminExists(String(tenant.id));
    } else {
      setIsDefaultTenant(false);
      setHasTenantAdmin(false);
    }
    // 切换租户时重置用户类型和已选择的角色
    form.setFieldsValue({ tenantType: undefined });
    setSelectedCreateRoles([]);
  };

  const loadUsers = async (tenantId?: string, filters?: { username?: string; email?: string; phone?: string }) => {
    setLoading(true);
    try {
      // 超级管理员可以按租户筛选，租户管理员只能看到当前租户的用户
      const filterTenantId = isPlatformAdmin() ? tenantId : currentUser?.tenantId;
      const data = await listUsers(filterTenantId);
      console.log('加载用户数据:', data); // 调试：检查返回的数据
      // 前端过滤
      let filtered: User[] = data;
      if (filters) {
        if (filters.username?.trim()) {
          const kw = filters.username.trim().toLowerCase();
          filtered = filtered.filter((user: User) =>
            user.username?.toLowerCase().includes(kw)
          );
        }
        if (filters.email?.trim()) {
          const kw = filters.email.trim().toLowerCase();
          filtered = filtered.filter((user: User) =>
            user.email?.toLowerCase().includes(kw)
          );
        }
        if (filters.phone?.trim()) {
          const kw = filters.phone.trim();
          filtered = filtered.filter((user: User) =>
            user.phone?.includes(kw)
          );
        }
      }
      setUsers(filtered);
    } catch (error: any) {
      message.error(error.message || '加载失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  const handleCreate = useCallback(() => {
    setEditingModalState({ visible: true, editingUser: null });
    form.resetFields();
    setSelectedCreateRoles([]);
    setHasTenantAdmin(false);
    
    // 租户管理员默认设置当前租户ID
    if (!isPlatformAdmin() && currentUser?.tenantId) {
      form.setFieldsValue({ tenantId: currentUser.tenantId });
      loadRoleListForCreate(currentUser.tenantId);
      checkTenantAdminExists(currentUser.tenantId);
    } else if (isPlatformAdmin() && selectedTenantId) {
      // 超级管理员如果有筛选租户，默认选中
      form.setFieldsValue({ tenantId: selectedTenantId });
      loadRoleListForCreate(selectedTenantId);
      checkTenantAdminExists(selectedTenantId);
    }
  }, [form, selectedTenantId, currentUser]);

  const [createRoleList, setCreateRoleList] = useState<Role[]>([]);
  const [selectedCreateRoles, setSelectedCreateRoles] = useState<string[]>([]);

  const loadRoleListForCreate = async (tenantId?: string) => {
    try {
      // 超级管理员根据选中的租户加载角色，租户管理员加载当前租户的角色
      const filterTenantId = isPlatformAdmin() ? tenantId : currentUser?.tenantId;
      const roles = await getRoleList(filterTenantId);
      setCreateRoleList(roles);
      setSelectedCreateRoles([]);
    } catch (error) {
      console.error('加载角色列表失败', error);
    }
  };

  const handleEdit = useCallback((record: User) => {
    setEditingModalState({ visible: true, editingUser: record });
    form.setFieldsValue({
      realName: record.realName,
      email: record.email,
      phone: record.phone,
    });
  }, [form]);

  const handleModalOk = useCallback(async () => {
    try {
      const values = await form.validateFields();
      const { editingUser } = editingModalState;

      if (editingUser) {
        await updateUser({ id: editingUser.id, ...values } as UserUpdateReq);
        message.success('更新成功');
      } else {
        // 新增用户时处理租户ID
        const createData: UserCreateReq = { ...values };
        // 保存原始密码用于显示
        const originalPassword = createData.password;
        // 如果是租户管理员，默认使用当前租户ID
        if (!isPlatformAdmin() && currentUser?.tenantId) {
          createData.tenantId = currentUser.tenantId;
        }
        const userId = await createUser(createData);
        // 显示创建成功信息，包含用户名和密码
        Modal.success({
          title: '创建成功',
          content: (
            <div>
              <p><strong>用户名：</strong>{createData.username}</p>
              <p><strong>初始密码：</strong>{originalPassword}</p>
              <p style={{ color: '#999', fontSize: '12px', marginTop: '8px' }}>
                请妥善保存密码，关闭后将无法再次查看
              </p>
            </div>
          ),
          okText: '知道了',
        });
        // 如果有选择角色，分配角色给新用户
        if (selectedCreateRoles.length > 0) {
          await assignRoles(userId, selectedCreateRoles);
        }
      }

      setEditingModalState({ visible: false, editingUser: null });
      setSelectedCreateRoles([]);
      loadUsers(selectedTenantId);
    } catch (error: any) {
      message.error(error.message || '操作失败');
    }
  }, [editingModalState, form, selectedCreateRoles, selectedTenantId, currentUser]);

  const handleDelete = useCallback(async (id: string) => {
    try {
      await deleteUser(id);
      message.success('删除成功');
      loadUsers(selectedTenantId);
    } catch (error: any) {
      message.error(error.message || '删除失败');
    }
  }, [selectedTenantId]);

  const handleToggleStatus = useCallback(async (record: User) => {
    try {
      if (record.status === 1) {
        await disableUser(record.id);
        message.success('已禁用');
      } else {
        await enableUser(record.id);
        message.success('已启用');
      }
      loadUsers(selectedTenantId);
    } catch (error: any) {
      message.error(error.message || '操作失败');
    }
  }, [selectedTenantId]);

  const handleAssignRoles = useCallback(async (userId: string, userTenantId?: string) => {
    try {
      console.log('[分配角色] 接收到的 userId:', userId, '类型:', typeof userId);
      setRoleModal(prev => ({ ...prev, userId, loading: true }));
      // 根据用户的租户ID加载角色列表
      const filterTenantId = isPlatformAdmin() ? userTenantId : currentUser?.tenantId;
      console.log('[分配角色] 调用 getUserRoles, userId:', userId);
      const [roles, userRoles] = await Promise.all([
        getRoleList(filterTenantId),
        getUserRoles(userId),
      ]);
      const assignedRoleIds = userRoles.map((r) => r.id);
      setRoleModal(prev => ({
        ...prev,
        list: roles,
        selected: assignedRoleIds,
        visible: true,
        loading: false,
      }));
    } catch (error: any) {
      message.error(error.message || '加载角色失败');
      setRoleModal(prev => ({ ...prev, loading: false }));
    }
  }, [currentUser]);

  const handleRoleCheckboxChange = useCallback((roleId: string, checked: boolean) => {
    setRoleModal(prev => ({
      ...prev,
      selected: checked
        ? [...prev.selected, roleId]
        : prev.selected.filter(id => id !== roleId),
    }));
  }, []);

  const handleRoleModalOk = useCallback(async () => {
    try {
      if (roleModal.userId === null) return;
      console.log('[提交分配] roleModal.userId:', roleModal.userId, '类型:', typeof roleModal.userId);
      console.log('[提交分配] roleModal.selected:', roleModal.selected);
      await assignRoles(roleModal.userId, roleModal.selected);
      message.success('角色分配成功');
      setRoleModal(prev => ({ ...prev, visible: false }));
      loadUsers(selectedTenantId);
    } catch (error: any) {
      message.error(error.message || '角色分配失败');
    }
  }, [roleModal.userId, roleModal.selected, selectedTenantId]);

  const handleResetPassword = useCallback((userId: string | number) => {
    setPasswordModal(prev => ({ ...prev, userId, visible: true, newPassword: '' }));
  }, []);

  const handlePasswordModalOk = useCallback(async () => {
    try {
      if (!passwordModal.newPassword || passwordModal.newPassword.length < 6) {
        message.error('密码至少6位');
        return;
      }

      setPasswordModal(prev => ({ ...prev, loading: true }));
      await resetPassword(passwordModal.userId as string, passwordModal.newPassword);
      message.success('密码重置成功');
      setPasswordModal(prev => ({ ...prev, visible: false, newPassword: '', loading: false }));
    } catch (error: any) {
      message.error(error.message || '密码重置失败');
      setPasswordModal(prev => ({ ...prev, loading: false }));
    }
  }, [passwordModal]);

  // 处理租户筛选变更
  const handleTenantChange = (tenantId: string | undefined) => {
    setSelectedTenantId(tenantId);
    loadUsers(tenantId, { username: filterUsername, email: filterEmail, phone: filterPhone });
  };

  // 搜索
  const handleSearch = () => {
    loadUsers(selectedTenantId, { username: filterUsername, email: filterEmail, phone: filterPhone });
  };

  // 重置筛选条件
  const handleReset = () => {
    setSelectedTenantId(undefined);
    setFilterUsername('');
    setFilterEmail('');
    setFilterPhone('');
    loadUsers(undefined, {});
  };

  const columns: ColumnsType<User> = [
    {
      title: '用户名',
      dataIndex: 'username',
      key: 'username',
    },
    {
      title: '真实姓名',
      dataIndex: 'realName',
      key: 'realName',
    },
    {
      title: '租户名称',
      dataIndex: 'tenantName',
      key: 'tenantName',
      render: (tenantName: string) => tenantName || '-',
    },
    {
      title: '用户类型',
      dataIndex: 'tenantType',
      key: 'tenantType',
      render: (tenantType: string) => {
        const typeMap: Record<string, string> = {
          PLATFORM: '超级管理员',
          PLATFORM_USER: '平台用户',
          TENANT_ADMIN: '租户管理员',
          TENANT_USER: '租户用户',
        };
        return typeMap[tenantType] || tenantType || '-';
      },
    },
    {
      title: '已分配角色',
      dataIndex: 'roles',
      key: 'roles',
      render: (roles: string) => {
        if (!roles) return '-';
        const roleList = roles.split(',').map(r => r.trim()).filter(r => r);
        return (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
            {roleList.map((role, index) => (
              <Tag key={index} color="blue">{role}</Tag>
            ))}
          </div>
        );
      },
    },
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email',
    },
    {
      title: '电话',
      dataIndex: 'phone',
      key: 'phone',
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
    TableColumnActions<User>({
      width: 280,
      actions: (record) => [
        ...(checkPermission('platform:user:edit') ? [{
          key: 'edit',
          label: '编辑',
          icon: <EditOutlined />,
          onClick: () => handleEdit(record),
        }] : []),
        ...(checkPermission('platform:user:assign-role') ? [{
          key: 'assign',
          label: '分配角色',
          icon: <TeamOutlined />,
          onClick: () => {
            handleAssignRoles(record.id, record.tenantId);
          },
        }] : []),
        ...(checkPermission('platform:user:edit') ? [{
          key: 'toggle',
          label: record.status === 1 ? '禁用' : '启用',
          icon: record.status === 1 ? <CloseOutlined /> : <CheckOutlined />,
          onClick: () => handleToggleStatus(record),
        }] : []),
        ...(checkPermission('platform:user:reset-password') ? [{
          key: 'reset',
          label: '重置密码',
          icon: <KeyOutlined />,
          onClick: () => handleResetPassword(record.id),
        }] : []),
        ...(checkPermission('platform:user:delete') ? [{
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
                style={{ width: 180 }}
                placeholder="选择租户"
                showAll
                value={selectedTenantId}
                onChange={handleTenantChange}
              />
            )}
            {/* 用户名筛选 */}
            <Input
              style={{ width: 140 }}
              placeholder="用户名"
              value={filterUsername}
              onChange={(e) => setFilterUsername(e.target.value)}
              onPressEnter={handleSearch}
              allowClear
            />
            {/* 邮箱筛选 */}
            <Input
              style={{ width: 160 }}
              placeholder="邮箱"
              value={filterEmail}
              onChange={(e) => setFilterEmail(e.target.value)}
              onPressEnter={handleSearch}
              allowClear
            />
            {/* 电话筛选 */}
            <Input
              style={{ width: 130 }}
              placeholder="电话"
              value={filterPhone}
              onChange={(e) => setFilterPhone(e.target.value)}
              onPressEnter={handleSearch}
              allowClear
            />
            <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch}>
              搜索
            </Button>
            <Button icon={<ReloadOutlined />} onClick={handleReset}>
              重置
            </Button>
            {checkPermission('platform:user:create') && (
              <FilterBar.Action>
                <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
                  新增用户
                </Button>
              </FilterBar.Action>
            )}
          </FilterBar>
        }
        columns={columns}
        dataSource={users}
        rowKey="id"
        loading={loading}
        locale={{
          emptyText: users.length === 0 && !loading ? '暂无用户数据' : undefined,
        }}
      />

      {/* User CRUD Modal */}
      <Modal
        title={editingModalState.editingUser ? '编辑用户' : '新增用户'}
        open={editingModalState.visible}
        onOk={handleModalOk}
        onCancel={() => setEditingModalState({ visible: false, editingUser: null })}
        width={600}
      >
        <Form form={form} layout="vertical">
          {/* 超级管理员新增用户时可以选择租户 */}
          {/* 超级管理员显示租户选择，租户管理员隐藏并默认当前租户 */}
          {!editingModalState.editingUser && isPlatformAdmin() && (
            <Form.Item
              name="tenantId"
              label="所属租户"
              rules={[{ required: true, message: '请选择所属租户' }]}
            >
              <TenantSelect
                placeholder="请选择所属租户"
                onTenantChange={handleTenantSelectChange}
                onChange={(tenantId) => {
                  // 切换租户时重新加载角色列表
                  loadRoleListForCreate(tenantId as string);
                  setSelectedCreateRoles([]);
                }}
              />
            </Form.Item>
          )}
          {/* 租户类型选择 - 超级管理员显示选择框，租户管理员隐藏并默认TENANT_USER */}
          {!editingModalState.editingUser && isPlatformAdmin() && (
            <Form.Item
              name="tenantType"
              label="用户类型"
              rules={[{ required: true, message: '请选择用户类型' }]}
            >
              <Select
                placeholder="请选择用户类型"
                options={
                  isDefaultTenant
                    ? // 默认租户可以选择超级管理员和平台用户
                      [
                        { label: '超级管理员', value: 'PLATFORM' },
                        { label: '平台用户', value: 'PLATFORM_USER' },
                      ]
                    : // 非默认租户可以选择租户管理员和租户用户
                      [
                        { label: '租户管理员', value: 'TENANT_ADMIN', disabled: hasTenantAdmin },
                        { label: '租户用户', value: 'TENANT_USER' },
                      ]
                }
              />
            </Form.Item>
          )}
          {/* 租户管理员新增用户时，用户类型默认为 TENANT_USER，不显示选择框 */}
          {!editingModalState.editingUser && !isPlatformAdmin() && (
            <Form.Item name="tenantType" initialValue="TENANT_USER" hidden>
              <Input />
            </Form.Item>
          )}
          {!editingModalState.editingUser && (
            <>
              <Form.Item
                name="username"
                label="用户名"
                rules={[{ required: true, message: '请输入用户名' }]}
              >
                <Input placeholder="请输入用户名" />
              </Form.Item>
              <Form.Item
                name="password"
                label="密码"
                rules={[{ required: true, min: 6, message: '密码至少6位' }]}
              >
                <Input.Password placeholder="请输入密码" />
              </Form.Item>
            </>
          )}
          <Form.Item
            name="realName"
            label="真实姓名"
            rules={[{ required: true, message: '请输入真实姓名' }]}
          >
            <Input placeholder="请输入真实姓名" />
          </Form.Item>
          <Form.Item
            name="email"
            label="邮箱"
            rules={[{ type: 'email', message: '邮箱格式不正确' }]}
          >
            <Input type="email" placeholder="请输入邮箱" />
          </Form.Item>
          <Form.Item
            name="phone"
            label="电话"
            rules={[{ pattern: /^1[3-9]\d{9}$/, message: '请输入有效的手机号' }]}
          >
            <Input placeholder="请输入手机号(11位)" />
          </Form.Item>
          {/* 新增用户时选择角色 */}
          {!editingModalState.editingUser && createRoleList.length > 0 && (
            <Form.Item label="选择角色">
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {createRoleList.map((role) => (
                  <Checkbox
                    key={role.id}
                    checked={selectedCreateRoles.includes(role.id)}
                    onChange={(e) => {
                      setSelectedCreateRoles(
                        e.target.checked
                          ? [...selectedCreateRoles, role.id]
                          : selectedCreateRoles.filter((id) => id !== role.id)
                      );
                    }}
                  >
                    {role.roleName} ({role.roleCode})
                  </Checkbox>
                ))}
              </div>
            </Form.Item>
          )}
        </Form>
      </Modal>

      {/* Role Assignment Modal */}
      <Modal
        title="分配角色"
        open={roleModal.visible}
        onOk={handleRoleModalOk}
        onCancel={() => {
          setRoleModal(prev => ({ ...prev, visible: false }));
        }}
        width={600}
        confirmLoading={roleModal.loading}
      >
        {roleModal.loading ? (
          <div style={{ padding: '20px', textAlign: 'center', color: '#999' }}>
            角色数据加载中...
          </div>
        ) : roleModal.list.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {roleModal.list.map((role) => (
              <Checkbox
                key={role.id}
                checked={roleModal.selected.includes(role.id)}
                onChange={(e) => handleRoleCheckboxChange(role.id, e.target.checked)}
              >
                {role.roleName} ({role.roleCode})
              </Checkbox>
            ))}
          </div>
        ) : (
          <div style={{ padding: '20px', textAlign: 'center', color: '#999' }}>
            该租户下暂无角色，请先创建角色
          </div>
        )}
      </Modal>

      {/* Password Reset Modal */}
      <Modal
        title="重置密码"
        open={passwordModal.visible}
        onOk={handlePasswordModalOk}
        onCancel={() => {
          setPasswordModal(prev => ({ ...prev, visible: false, newPassword: '' }));
        }}
        width={500}
        confirmLoading={passwordModal.loading}
      >
        <Form layout="vertical">
          <Form.Item label="新密码">
            <Input.Password
              placeholder="请输入新密码（至少6位）"
              value={passwordModal.newPassword}
              onChange={(e) => setPasswordModal(prev => ({ ...prev, newPassword: e.target.value }))}
            />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
};

export default UserPage;
