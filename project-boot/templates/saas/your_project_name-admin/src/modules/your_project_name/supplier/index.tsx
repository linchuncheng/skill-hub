import {
  createSupplier,
  deleteSupplier,
  listSuppliers,
  updateSupplier,
} from '@/api/your_project_name/supplier';
import type { Supplier } from '@/api/types/your_project_name.schema';
import { FilterBar, PageTable } from '@/components/common/PageTable';
import { TableColumnActions } from '@/components/common/TableColumnActions';
import { useAuthStore } from '@/stores/authStore';
import {
  DeleteOutlined,
  EditOutlined,
  LinkOutlined,
  PlusOutlined,
  ReloadOutlined,
  SearchOutlined,
} from '@ant-design/icons';
import { Button, Form, Input, message, Select, Tag } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { FC, useCallback, useEffect, useState } from 'react';
import LinkSkuModal from './components/LinkSkuModal';
import SupplierModal from './components/SupplierModal';

/**
 * 风险等级颜色映射
 */
const riskLevelColors: Record<string, string> = {
  LOW: 'green',
  MEDIUM: 'orange',
  HIGH: 'red',
};

/**
 * 风险等级文本映射
 */
const riskLevelTexts: Record<string, string> = {
  LOW: '低风险',
  MEDIUM: '中风险',
  HIGH: '高风险',
};

/**
 * YOUR_PROJECT_NAME 供应商管理页面
 */
const SupplierPage: FC = () => {
  // 供应商列表相关状态
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [loading, setLoading] = useState(false);
  const [allSuppliers, setAllSuppliers] = useState<Supplier[]>([]);

  // 筛选条件
  const [filterCode, setFilterCode] = useState('');
  const [filterName, setFilterName] = useState('');
  const [filterContact, setFilterContact] = useState('');
  const [filterRiskLevel, setFilterRiskLevel] = useState<string>('');

  // 弹窗状态
  const [modalVisible, setModalVisible] = useState(false);
  const [editingSupplier, setEditingSupplier] = useState<Supplier | null>(null);
  const [linkSkuModalVisible, setLinkSkuModalVisible] = useState(false);
  const [currentSupplier, setCurrentSupplier] = useState<Supplier | null>(null);

  const [form] = Form.useForm();
  const { hasPermission, user } = useAuthStore();

  // 检查权限（超级管理员自动拥有所有权限）
  const checkPermission = (permission: string) => {
    if (user?.tenantType === 'PLATFORM' && user?.tenantId === '0') {
      return true;
    }
    return hasPermission(permission);
  };

  // 加载供应商列表
  const loadSuppliers = async () => {
    setLoading(true);
    try {
      const data = await listSuppliers();
      setAllSuppliers(data);
      setSuppliers(data);
    } catch (error: any) {
      message.error(error.message || '加载供应商列表失败');
    } finally {
      setLoading(false);
    }
  };

  // 前端筛选
  const applyFilters = useCallback(() => {
    let filtered = allSuppliers;
    if (filterCode.trim()) {
      const kw = filterCode.trim().toLowerCase();
      filtered = filtered.filter((s) => s.supplierCode?.toLowerCase().includes(kw));
    }
    if (filterName.trim()) {
      const kw = filterName.trim().toLowerCase();
      filtered = filtered.filter((s) => s.supplierName?.toLowerCase().includes(kw));
    }
    if (filterContact.trim()) {
      const kw = filterContact.trim().toLowerCase();
      filtered = filtered.filter(
        (s) =>
          s.contactName?.toLowerCase().includes(kw) ||
          s.contactPhone?.includes(kw)
      );
    }
    if (filterRiskLevel) {
      filtered = filtered.filter((s) => s.riskLevel === filterRiskLevel);
    }
    setSuppliers(filtered);
  }, [allSuppliers, filterCode, filterName, filterContact, filterRiskLevel]);

  // 搜索
  const handleSearch = () => {
    applyFilters();
  };

  // 重置
  const handleReset = () => {
    setFilterCode('');
    setFilterName('');
    setFilterContact('');
    setFilterRiskLevel('');
    setSuppliers(allSuppliers);
  };

  useEffect(() => {
    loadSuppliers();
  }, []);

  // 新增供应商
  const handleCreate = () => {
    setEditingSupplier(null);
    form.resetFields();
    setModalVisible(true);
  };

  // 编辑供应商
  const handleEdit = (record: Supplier) => {
    setEditingSupplier(record);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  // 保存供应商
  const handleModalOk = async () => {
    try {
      const values = await form.validateFields();

      // 转换 status：前端 1/0 -> 后端 "ACTIVE"/"INACTIVE"
      const statusValue = values.status === 1 || values.status === undefined ? 'ACTIVE' : 'INACTIVE';

      if (editingSupplier) {
        // 更新
        await updateSupplier({
          id: editingSupplier.id,
          supplierName: values.supplierName,
          contactName: values.contactName,
          contactPhone: values.contactPhone,
          address: values.address,
          riskLevel: values.riskLevel,
          status: statusValue,
        } as any);
        message.success('更新成功');
      } else {
        // 创建
        await createSupplier({
          supplierCode: values.supplierCode,
          supplierName: values.supplierName,
          contactName: values.contactName,
          contactPhone: values.contactPhone,
          address: values.address,
          riskLevel: values.riskLevel,
          status: statusValue,
        } as any);
        message.success('创建成功');
      }

      setModalVisible(false);
      loadSuppliers();
    } catch (error: any) {
      message.error(error.message || '操作失败');
    }
  };

  // 删除供应商
  const handleDelete = async (id: string) => {
    try {
      await deleteSupplier(id);
      message.success('删除成功');
      loadSuppliers();
    } catch (error: any) {
      message.error(error.message || '删除失败');
    }
  };

  // 打开关联商品弹窗
  const handleOpenLinkSkuModal = (record: Supplier) => {
    setCurrentSupplier(record);
    setLinkSkuModalVisible(true);
  };

  // 表格列定义
  const columns: ColumnsType<Supplier> = [
    {
      title: '供应商编码',
      dataIndex: 'supplierCode',
      key: 'supplierCode',
      width: 120,
    },
    {
      title: '供应商名称',
      dataIndex: 'supplierName',
      key: 'supplierName',
      width: 150,
    },
    {
      title: '联系人',
      dataIndex: 'contactName',
      key: 'contactName',
      width: 100,
      render: (text: string) => text || '-',
    },
    {
      title: '联系电话',
      dataIndex: 'contactPhone',
      key: 'contactPhone',
      width: 120,
      render: (text: string) => text || '-',
    },
    {
      title: '风险等级',
      dataIndex: 'riskLevel',
      key: 'riskLevel',
      width: 100,
      render: (level: string) =>
        level ? (
          <Tag color={riskLevelColors[level] || 'default'}>
            {riskLevelTexts[level] || level}
          </Tag>
        ) : (
          '-'
        ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 80,
      render: (status: string) =>
        status === 'ACTIVE' ? <Tag color="green">启用</Tag> : <Tag color="red">禁用</Tag>,
    },
    {
      title: '创建时间',
      dataIndex: 'createdAt',
      key: 'createdAt',
      width: 180,
    },
    TableColumnActions<Supplier>({
      width: 220,
      actions: (record) => [
        {
          key: 'link',
          label: '关联商品',
          icon: <LinkOutlined />,
          onClick: () => handleOpenLinkSkuModal(record),
        },
        ...(checkPermission('your_project_name:supplier:edit') ? [{
          key: 'edit',
          label: '编辑',
          icon: <EditOutlined />,
          onClick: () => handleEdit(record),
        }] : []),
        ...(checkPermission('your_project_name:supplier:delete') ? [{
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
              style={{ width: 140 }}
              placeholder="供应商编码"
              value={filterCode}
              onChange={(e) => setFilterCode(e.target.value)}
              onPressEnter={handleSearch}
              allowClear
            />
            <Input
              style={{ width: 140 }}
              placeholder="供应商名称"
              value={filterName}
              onChange={(e) => setFilterName(e.target.value)}
              onPressEnter={handleSearch}
              allowClear
            />
            <Input
              style={{ width: 140 }}
              placeholder="联系人/电话"
              value={filterContact}
              onChange={(e) => setFilterContact(e.target.value)}
              onPressEnter={handleSearch}
              allowClear
            />
            <Select
              style={{ width: 120 }}
              placeholder="风险等级"
              value={filterRiskLevel || undefined}
              onChange={(v) => setFilterRiskLevel(v || '')}
              allowClear
              options={[
                { value: 'LOW', label: '低风险' },
                { value: 'MEDIUM', label: '中风险' },
                { value: 'HIGH', label: '高风险' },
              ]}
            />
            <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch}>
              搜索
            </Button>
            <Button icon={<ReloadOutlined />} onClick={handleReset}>
              重置
            </Button>
            {checkPermission('your_project_name:supplier:create') && (
              <FilterBar.Action>
                <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
                  新增供应商
                </Button>
              </FilterBar.Action>
            )}
          </FilterBar>
        }
        columns={columns}
        dataSource={suppliers}
        rowKey="id"
        loading={loading}
      />

      {/* 供应商表单弹窗 */}
      <SupplierModal
        visible={modalVisible}
        editingSupplier={editingSupplier}
        form={form}
        onOk={handleModalOk}
        onCancel={() => setModalVisible(false)}
      />

      {/* 商品关联弹窗 */}
      {currentSupplier && (
        <LinkSkuModal
          visible={linkSkuModalVisible}
          supplierId={currentSupplier.id}
          supplierName={currentSupplier.supplierName}
          onClose={() => setLinkSkuModalVisible(false)}
        />
      )}
    </>
  );
};

export default SupplierPage;
