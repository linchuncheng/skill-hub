import {
    createMenu,
    deleteMenu,
    listMenus,
    updateMenu,
} from '@/api/platform/menu';
import type { Menu, MenuCreateReq, MenuUpdateReq } from '@/api/types/menu.schema';
import { FilterBar, PageTable } from '@/components/common/PageTable';
import { TableColumnActions } from '@/components/common/TableColumnActions';
import { useAuthStore } from '@/stores/authStore';
import {
    DeleteOutlined,
    EditOutlined,
    PlusOutlined,
    ReloadOutlined,
    SearchOutlined,
} from '@ant-design/icons';
import {
    Button,
    Form,
    Input,
    InputNumber,
    message,
    Modal,
    Select,
    Tag
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { FC, useCallback, useEffect, useState } from 'react';

interface MenuTreeNode extends Menu {
  children?: MenuTreeNode[];
}

const MenuPage: FC = () => {
  const [menus, setMenus] = useState<MenuTreeNode[]>([]);
  const [allMenus, setAllMenus] = useState<MenuTreeNode[]>([]); // 原始数据
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingMenu, setEditingMenu] = useState<MenuTreeNode | null>(null);
  const [form] = Form.useForm();
  const { hasPermission, user } = useAuthStore();

  // 筛选条件
  const [filterMenuName, setFilterMenuName] = useState<string>('');
  const [filterMenuPath, setFilterMenuPath] = useState<string>('');
  const [filterStatus, setFilterStatus] = useState<number | undefined>(undefined);

  // 检查权限（超级管理员自动拥有所有权限）
  const checkPermission = (permission: string) => {
    if (user?.tenantType === 'PLATFORM' && user?.tenantId === '0') {
      return true;
    }
    return hasPermission(permission);
  };

  // 按 sort 排序菜单
  const sortMenus = (menus: MenuTreeNode[]): MenuTreeNode[] => {
    return menus
      .sort((a, b) => (a.sort || 0) - (b.sort || 0))
      .map((menu) => {
        if (menu.children && menu.children.length > 0) {
          return { ...menu, children: sortMenus(menu.children) };
        }
        return menu;
      });
  };

  // 清理菜单数据，将空 children 数组转为 undefined
  const cleanMenuData = (menus: MenuTreeNode[]): MenuTreeNode[] => {
    return menus.map((menu) => {
      const cleaned: MenuTreeNode = { ...menu };
      if (cleaned.children && cleaned.children.length === 0) {
        delete cleaned.children;
      } else if (cleaned.children) {
        cleaned.children = cleanMenuData(cleaned.children);
      }
      return cleaned;
    });
  };

  const loadMenus = async () => {
    setLoading(true);
    try {
      const data = await listMenus();
      const sortedData = sortMenus(data as MenuTreeNode[]);
      const cleanedData = cleanMenuData(sortedData);
      setAllMenus(cleanedData);
      setMenus(cleanedData);
    } catch (error: any) {
      message.error(error.message || '加载失败');
    } finally {
      setLoading(false);
    }
  };

  // 递归搜索菜单树
  const filterMenuTree = (menus: MenuTreeNode[], predicate: (menu: MenuTreeNode) => boolean): MenuTreeNode[] => {
    const result: MenuTreeNode[] = [];
    
    for (const menu of menus) {
      const children = menu.children ? filterMenuTree(menu.children, predicate) : [];
      const matches = predicate(menu);
      
      if (matches || children.length > 0) {
        result.push({
          ...menu,
          children: children.length > 0 ? children : undefined,
        });
      }
    }
    
    return result;
  };

  // 前端筛选
  const applyFilters = useCallback(() => {
    if (!filterMenuName.trim() && !filterMenuPath.trim() && filterStatus === undefined) {
      setMenus(allMenus);
      return;
    }

    const filtered = filterMenuTree(allMenus, (menu) => {
      // 名称筛选
      if (filterMenuName.trim()) {
        const kw = filterMenuName.trim().toLowerCase();
        if (!menu.name?.toLowerCase().includes(kw)) {
          return false;
        }
      }
      // 路径筛选
      if (filterMenuPath.trim()) {
        const kw = filterMenuPath.trim().toLowerCase();
        if (!menu.path?.toLowerCase().includes(kw)) {
          return false;
        }
      }
      // 状态筛选
      if (filterStatus !== undefined) {
        if (menu.status !== filterStatus) {
          return false;
        }
      }
      return true;
    });

    setMenus(filtered);
  }, [allMenus, filterMenuName, filterMenuPath, filterStatus]);

  // 搜索
  const handleSearch = () => {
    applyFilters();
  };

  // 重置
  const handleReset = () => {
    setFilterMenuName('');
    setFilterMenuPath('');
    setFilterStatus(undefined);
    setMenus(allMenus);
  };

  useEffect(() => {
    loadMenus();
  }, []);

  const handleCreate = () => {
    setEditingMenu(null);
    form.resetFields();
    form.setFieldsValue({ parentId: null, sort: 0, status: 1 });
    setModalVisible(true);
  };

  const handleEdit = (record: MenuTreeNode) => {
    setEditingMenu(record);
    form.setFieldsValue({
      parentId: record.parentId,
      name: record.name,
      path: record.path,
      component: record.component,
      icon: record.icon,
      sort: record.sort,
      permissionCode: record.permissionCode,
      status: record.status,
    });
    setModalVisible(true);
  };

  const handleModalOk = async () => {
    try {
      const values = await form.validateFields();

      if (editingMenu) {
        await updateMenu({ id: editingMenu.id, ...values } as MenuUpdateReq);
        message.success('更新成功');
      } else {
        await createMenu(values as MenuCreateReq);
        message.success('创建成功');
      }

      setModalVisible(false);
      loadMenus();
    } catch (error: any) {
      message.error(error.message || '操作失败');
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteMenu(id);
      message.success('删除成功');
      loadMenus();
    } catch (error: any) {
      message.error(error.message || '删除失败');
    }
  };

  const columns: ColumnsType<MenuTreeNode> = [
    {
      title: '菜单名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '路径',
      dataIndex: 'path',
      key: 'path',
    },
    {
      title: '组件',
      dataIndex: 'component',
      key: 'component',
      render: (text: string) => text || '-',
    },
    {
      title: '图标',
      dataIndex: 'icon',
      key: 'icon',
      render: (text: string) => text || '-',
    },
    {
      title: '排序',
      dataIndex: 'sort',
      key: 'sort',
      width: 80,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 80,
      render: (status: number) =>
        status === 1 ? <Tag color="green">启用</Tag> : <Tag color="red">禁用</Tag>,
    },
    TableColumnActions<Menu>({
      width: 150,
      actions: (record) => [
        ...(checkPermission('platform:menu:edit') ? [{
          key: 'edit',
          label: '编辑',
          icon: <EditOutlined />,
          onClick: () => handleEdit(record),
        }] : []),
        ...(checkPermission('platform:menu:delete') ? [{
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
              placeholder="菜单名称"
              value={filterMenuName}
              onChange={(e) => setFilterMenuName(e.target.value)}
              onPressEnter={handleSearch}
              allowClear
            />
            <Input
              style={{ width: 180 }}
              placeholder="菜单路径"
              value={filterMenuPath}
              onChange={(e) => setFilterMenuPath(e.target.value)}
              onPressEnter={handleSearch}
              allowClear
            />
            <Select
              style={{ width: 120 }}
              placeholder="状态"
              value={filterStatus}
              onChange={(value) => setFilterStatus(value)}
              allowClear
              options={[
                { label: '全部', value: undefined },
                { label: '启用', value: 1 },
                { label: '禁用', value: 0 },
              ]}
            />
            <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch}>
              搜索
            </Button>
            <Button icon={<ReloadOutlined />} onClick={handleReset}>
              重置
            </Button>
            {checkPermission('platform:menu:create') && (
              <FilterBar.Action>
                <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
                  新增菜单
                </Button>
              </FilterBar.Action>
            )}
          </FilterBar>
        }
        columns={columns}
        dataSource={menus}
        rowKey="id"
        loading={loading}
        pagination={false}
        defaultExpandAllRows
        indentSize={20}
        childrenColumnName="children"
        expandable={{
          rowExpandable: (record: MenuTreeNode) => {
            const hasChildren = record.children && Array.isArray(record.children) && record.children.length > 0;
            return hasChildren;
          },
        }}
      />

      <Modal
        title={editingMenu ? '编辑菜单' : '新增菜单'}
        open={modalVisible}
        onOk={handleModalOk}
        onCancel={() => setModalVisible(false)}
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="parentId" label="父级菜单">
            <Select
              placeholder="请选择父级菜单，留空表示顶级菜单"
              allowClear
              showSearch
              optionFilterProp="label"
              options={[
                { label: '顶级菜单（无父级）', value: '' },
                ...allMenus.map((menu) => ({
                  label: `${menu.name} (${menu.path})`,
                  value: menu.id,
                })),
              ]}
            />
          </Form.Item>
          <Form.Item
            name="name"
            label="菜单名称"
            rules={[{ required: true, message: '请输入菜单名称' }]}
          >
            <Input placeholder="请输入菜单名称" />
          </Form.Item>
          <Form.Item
            name="path"
            label="菜单路径"
            rules={[{ required: true, message: '请输入菜单路径' }]}
          >
            <Select
              placeholder="请选择或输入菜单路径"
              showSearch
              allowClear
              mode="tags"
              maxCount={1}
              options={[
                { label: '/dashboard', value: '/dashboard' },
                { label: '/test', value: '/test' },
                { label: '/system', value: '/system' },
                { label: '/system/tenant', value: '/system/tenant' },
                { label: '/system/user', value: '/system/user' },
                { label: '/system/menu', value: '/system/menu' },
                { label: '/system/role', value: '/system/role' },
              ]}
            />
          </Form.Item>
          <Form.Item name="component" label="组件路径">
            <Input placeholder="请输入组件路径，如 pages/user" />
          </Form.Item>
          <Form.Item name="icon" label="图标">
            <Input placeholder="请输入图标名称" />
          </Form.Item>
          <Form.Item name="sort" label="排序" initialValue={0}>
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="permissionCode" label="权限码">
            <Input placeholder="请输入权限码，如 platform:user:list" />
          </Form.Item>
          <Form.Item name="status" label="状态" initialValue={1}>
            <InputNumber min={0} max={1} style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
};

export default MenuPage;
