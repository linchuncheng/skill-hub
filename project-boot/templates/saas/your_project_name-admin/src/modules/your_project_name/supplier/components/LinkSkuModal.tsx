import { listSkus } from '@/api/your_project_name/sku';
import { linkSkus, listLinkedSkus, unlinkSkus } from '@/api/your_project_name/supplier';
import type { LinkedSku, Sku } from '@/api/types/your_project_name.schema';
import { SearchOutlined } from '@ant-design/icons';
import { Button, Input, message, Modal, Popconfirm, Table, Tabs, Tag } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { FC, useCallback, useEffect, useRef, useState } from 'react';

interface LinkSkuModalProps {
  visible: boolean;
  supplierId: string;
  supplierName: string;
  onClose: () => void;
}

/**
 * 商品关联弹窗组件
 */
const LinkSkuModal: FC<LinkSkuModalProps> = ({
  visible,
  supplierId,
  supplierName,
  onClose,
}) => {
  const [loading, setLoading] = useState(false);
  const [skus, setSkus] = useState<Sku[]>([]);
  const [selectedRowKeys, setSelectedRowKeys] = useState<string[]>([]);
  const [keyword, setKeyword] = useState('');
  const [linkedSkus, setLinkedSkus] = useState<LinkedSku[]>([]);
  const [activeTab, setActiveTab] = useState('linked');
  
  // 使用 ref 追踪是否已加载，避免重复请求
  const linkedSkusLoadedRef = useRef(false);
  const skusLoadedRef = useRef(false);

  // 加载 SKU 列表
  const loadSkus = useCallback(async () => {
    setLoading(true);
    try {
      const data = await listSkus({ keyword: keyword.trim() || undefined });
      // 过滤：只显示启用的 SKU，且排除已关联的 SKU
      const linkedSkuIds = new Set(linkedSkus.map(linked => linked.skuId));
      setSkus(data.filter(sku => sku.status === 'ACTIVE' && !linkedSkuIds.has(sku.id)));
    } catch (error: any) {
      message.error(error.message || '加载 SKU 列表失败');
    } finally {
      setLoading(false);
    }
  }, [keyword, linkedSkus]);

  // 加载已关联商品
  const loadLinkedSkus = useCallback(async () => {
    try {
      const data = await listLinkedSkus(supplierId);
      setLinkedSkus(data);
    } catch (error: any) {
      message.error(error.message || '加载已关联商品失败');
    }
  }, [supplierId]);

  useEffect(() => {
    if (visible) {
      // 重置状态
      linkedSkusLoadedRef.current = false;
      skusLoadedRef.current = false;
      setSelectedRowKeys([]);
      setKeyword('');
      setActiveTab('linked');
      
      // 加载已关联列表
      loadLinkedSkus();
      linkedSkusLoadedRef.current = true;
    }
  }, [visible, loadLinkedSkus]);

  // 当 linkedSkus 加载完成后，如果当前在"关联商品" tab，则加载 SKU 列表
  useEffect(() => {
    if (visible && activeTab === 'link' && linkedSkusLoadedRef.current && !skusLoadedRef.current) {
      loadSkus();
      skusLoadedRef.current = true;
    }
  }, [linkedSkus, visible, activeTab, loadSkus]);

  // 搜索
  const handleSearch = () => {
    loadSkus();
  };

  // 保存关联
  const handleOk = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请至少选择一个商品');
      return;
    }
    setLoading(true);
    try {
      await linkSkus(supplierId, { skuIds: selectedRowKeys });
      message.success('关联商品成功');
      // 刷新已关联列表
      await loadLinkedSkus();
      setSelectedRowKeys([]);
      // 切换到已关联 tab
      setActiveTab('linked');
    } catch (error: any) {
      message.error(error.message || '关联商品失败');
    } finally {
      setLoading(false);
    }
  };

  // 解除关联
  const handleUnlink = async (skuId: string) => {
    try {
      await unlinkSkus(supplierId, [skuId]);
      message.success('解除关联成功');
      loadLinkedSkus();
    } catch (error: any) {
      message.error(error.message || '解除关联失败');
    }
  };

  // 可选 SKU 表格列定义
  const skuColumns: ColumnsType<Sku> = [
    {
      title: 'SKU编码',
      dataIndex: 'skuCode',
      key: 'skuCode',
      width: 120,
    },
    {
      title: 'SKU名称',
      dataIndex: 'skuName',
      key: 'skuName',
      width: 180,
    },
    {
      title: '单位',
      dataIndex: 'unit',
      key: 'unit',
      width: 80,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 80,
      render: (status: string) =>
        status === 'ACTIVE' ? <Tag color="green">启用</Tag> : <Tag color="red">停用</Tag>,
    },
  ];

  // 已关联商品表格列定义
  const linkedSkuColumns: ColumnsType<LinkedSku> = [
    {
      title: 'SKU编码',
      dataIndex: 'skuCode',
      key: 'skuCode',
      width: 120,
    },
    {
      title: 'SKU名称',
      dataIndex: 'skuName',
      key: 'skuName',
      width: 180,
    },
    {
      title: '单位',
      dataIndex: 'unit',
      key: 'unit',
      width: 80,
    },
    {
      title: '关联时间',
      dataIndex: 'createdAt',
      key: 'createdAt',
      width: 160,
    },
    {
      title: '操作',
      key: 'action',
      width: 100,
      render: (_, record) => (
        <Popconfirm
          title="确认解除关联？"
          onConfirm={() => handleUnlink(record.skuId)}
        >
          <Button type="link" size="small" danger>解除</Button>
        </Popconfirm>
      ),
    },
  ];

  return (
    <Modal
      title={`关联商品 - ${supplierName}`}
      open={visible}
      onOk={activeTab === 'link' ? handleOk : undefined}
      onCancel={onClose}
      width={800}
      confirmLoading={loading}
      destroyOnClose
      footer={activeTab === 'link' ? undefined : null}
    >
      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <Tabs.TabPane tab={`已关联 (${linkedSkus.length})`} key="linked">
          <Table
            columns={linkedSkuColumns}
            dataSource={linkedSkus}
            rowKey="id"
            loading={loading}
            pagination={{ pageSize: 10 }}
            size="small"
          />
        </Tabs.TabPane>

        <Tabs.TabPane tab="关联商品" key="link">
          <div style={{ marginBottom: 16, display: 'flex', gap: 16 }}>
            <Input
              style={{ width: 250 }}
              placeholder="搜索 SKU 编码或名称"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              onPressEnter={handleSearch}
              allowClear
            />
            <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch}>
              搜索
            </Button>
          </div>

          <Table
            columns={skuColumns}
            dataSource={skus}
            rowKey="id"
            loading={loading}
            pagination={{ pageSize: 10 }}
            rowSelection={{
              type: 'checkbox',
              selectedRowKeys,
              onChange: (keys) => setSelectedRowKeys(keys as string[]),
            }}
            size="small"
          />

          <div style={{ marginTop: 8, color: '#666' }}>
            已选择 {selectedRowKeys.length} 个商品
          </div>
        </Tabs.TabPane>
      </Tabs>
    </Modal>
  );
};

export default LinkSkuModal;
