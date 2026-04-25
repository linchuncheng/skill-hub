import {
  createTenant,
  deleteTenant,
  disableTenant,
  enableTenant,
  listTenants,
  updateTenant,
} from '@/api/platform/tenant';
import type { Tenant, TenantCreateReq, TenantUpdateReq } from '@/api/types/tenant.schema';
import { FilterBar, PageTable } from '@/components/common/PageTable';
import { TableColumnActions } from '@/components/common/TableColumnActions';
import { useAuthStore } from '@/stores/authStore';
import { CheckOutlined, CloseOutlined, DeleteOutlined, EditOutlined, PlusOutlined, ReloadOutlined, SearchOutlined } from '@ant-design/icons';
import { Button, Form, Input, message, Modal, Tag } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { FC, useCallback, useEffect, useState } from 'react';

const TenantPage: FC = () => {
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingTenant, setEditingTenant] = useState<Tenant | null>(null);
  const [form] = Form.useForm();
  const { hasPermission, user } = useAuthStore();

  // 筛选条件
  const [filterTenantCode, setFilterTenantCode] = useState<string>('');
  const [filterTenantName, setFilterTenantName] = useState<string>('');
  const [filterContactName, setFilterContactName] = useState<string>('');
  const [filterContactPhone, setFilterContactPhone] = useState<string>('');
  const [allTenants, setAllTenants] = useState<Tenant[]>([]); // 原始数据

  // 检查权限（超级管理员自动拥有所有权限）
  const checkPermission = (permission: string) => {
    if (user?.tenantType === 'PLATFORM' && user?.tenantId === '0') {
      return true;
    }
    return hasPermission(permission);
  };

  const loadTenants = async () => {
    setLoading(true);
    try {
      const data = await listTenants();
      setAllTenants(data);
      setTenants(data);
    } catch (error: any) {
      message.error(error.message || '加载失败');
    } finally {
      setLoading(false);
    }
  };

  // 前端筛选
  const applyFilters = useCallback(() => {
    let filtered = allTenants;
    if (filterTenantCode.trim()) {
      const kw = filterTenantCode.trim().toLowerCase();
      filtered = filtered.filter((t: Tenant) => t.tenantCode?.toLowerCase().includes(kw));
    }
    if (filterTenantName.trim()) {
      const kw = filterTenantName.trim().toLowerCase();
      filtered = filtered.filter((t: Tenant) => t.tenantName?.toLowerCase().includes(kw));
    }
    if (filterContactName.trim()) {
      const kw = filterContactName.trim().toLowerCase();
      filtered = filtered.filter((t: Tenant) => t.contactName?.toLowerCase().includes(kw));
    }
    if (filterContactPhone.trim()) {
      const kw = filterContactPhone.trim();
      filtered = filtered.filter((t: Tenant) => t.contactPhone?.includes(kw));
    }
    setTenants(filtered);
  }, [allTenants, filterTenantCode, filterTenantName, filterContactName, filterContactPhone]);

  // 搜索
  const handleSearch = () => {
    applyFilters();
  };

  // 重置
  const handleReset = () => {
    setFilterTenantCode('');
    setFilterTenantName('');
    setFilterContactName('');
    setFilterContactPhone('');
    setTenants(allTenants);
  };

  useEffect(() => {
    loadTenants();
  }, []);

  const handleCreate = () => {
    setEditingTenant(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record: Tenant) => {
    setEditingTenant(record);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  const handleModalOk = async () => {
    try {
      const values = await form.validateFields();

      if (editingTenant) {
        // 更新
        await updateTenant({ id: editingTenant.id, ...values } as TenantUpdateReq);
        message.success('更新成功');
      } else {
        // 创建
        await createTenant(values as TenantCreateReq);
        message.success('创建成功');
      }

      setModalVisible(false);
      loadTenants();
    } catch (error: any) {
      message.error(error.message || '操作失败');
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteTenant(id);
      message.success('删除成功');
      loadTenants();
    } catch (error: any) {
      message.error(error.message || '删除失败');
    }
  };

  const handleToggleStatus = async (record: Tenant) => {
    try {
      if (record.status === 1) {
        await disableTenant(record.id);
        message.success('已禁用');
      } else {
        await enableTenant(record.id);
        message.success('已启用');
      }
      loadTenants();
    } catch (error: any) {
      message.error(error.message || '操作失败');
    }
  };

  const columns: ColumnsType<Tenant> = [
    {
      title: '租户编码',
      dataIndex: 'tenantCode',
      key: 'tenantCode',
    },
    {
      title: '租户名称',
      dataIndex: 'tenantName',
      key: 'tenantName',
    },
    {
      title: '联系人',
      dataIndex: 'contactName',
      key: 'contactName',
    },
    {
      title: '联系电话',
      dataIndex: 'contactPhone',
      key: 'contactPhone',
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
    TableColumnActions<Tenant>({
      width: 180,
      actions: (record) => [
        ...(checkPermission('platform:tenant:edit') ? [{
          key: 'edit',
          label: '编辑',
          icon: <EditOutlined />,
          onClick: () => handleEdit(record),
        }] : []),
        ...(checkPermission('platform:tenant:edit') ? [{
          key: 'toggle',
          label: record.status === 1 ? '禁用' : '启用',
          icon: record.status === 1 ? <CloseOutlined /> : <CheckOutlined />,
          onClick: () => handleToggleStatus(record),
        }] : []),
        ...(checkPermission('platform:tenant:delete') ? [{
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
            <Input
              style={{ width: 150 }}
              placeholder="租户编码"
              value={filterTenantCode}
              onChange={(e) => setFilterTenantCode(e.target.value)}
              onPressEnter={handleSearch}
              allowClear
            />
            <Input
              style={{ width: 150 }}
              placeholder="租户名称"
              value={filterTenantName}
              onChange={(e) => setFilterTenantName(e.target.value)}
              onPressEnter={handleSearch}
              allowClear
            />
            <Input
              style={{ width: 120 }}
              placeholder="联系人"
              value={filterContactName}
              onChange={(e) => setFilterContactName(e.target.value)}
              onPressEnter={handleSearch}
              allowClear
            />
            <Input
              style={{ width: 140 }}
              placeholder="联系电话"
              value={filterContactPhone}
              onChange={(e) => setFilterContactPhone(e.target.value)}
              onPressEnter={handleSearch}
              allowClear
            />
            <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch}>
              搜索
            </Button>
            <Button icon={<ReloadOutlined />} onClick={handleReset}>
              重置
            </Button>
            {checkPermission('platform:tenant:create') && (
              <FilterBar.Action>
                <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
                  新增租户
                </Button>
              </FilterBar.Action>
            )}
          </FilterBar>
        }
        columns={columns}
        dataSource={tenants}
        rowKey="id"
        loading={loading}
      />

      <Modal
        title={editingTenant ? '编辑租户' : '新增租户'}
        open={modalVisible}
        onOk={handleModalOk}
        onCancel={() => setModalVisible(false)}
        width={600}
      >
        <Form form={form} layout="vertical">
          {!editingTenant && (
            <Form.Item
              name="tenantCode"
              label="租户编码"
              rules={[{ required: true, message: '请输入租户编码' }]}
            >
              <Input placeholder="请输入租户编码" />
            </Form.Item>
          )}
          <Form.Item
            name="tenantName"
            label="租户名称"
            rules={[{ required: true, message: '请输入租户名称' }]}
          >
            <Input placeholder="请输入租户名称" />
          </Form.Item>
          <Form.Item name="logo" label="Logo链接">
            <Input placeholder="请输入Logo链接" />
          </Form.Item>
          <Form.Item name="contactName" label="联系人">
            <Input placeholder="请输入联系人" />
          </Form.Item>
          <Form.Item name="contactPhone" label="联系电话">
            <Input placeholder="请输入联系电话" />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
};

export default TenantPage;
