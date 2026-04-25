import { PlusOutlined, ReloadOutlined } from '@ant-design/icons';
import type { TablePaginationConfig, TableProps } from 'antd';
import { Button, Card, Empty, Space, Table } from 'antd';
import { ReactNode } from 'react';

export interface ProTableProps<T> extends Omit<TableProps<T>, 'pagination' | 'title'> {
  // 标题
  title?: string;
  // 工具栏
  toolbar?: ReactNode;
  // 加载状态
  loading?: boolean;
  // 分页配置
  pagination?: {
    current: number;
    pageSize: number;
    total: number;
    onChange?: (page: number, pageSize: number) => void;
  } | false;
  // 刷新回调
  onRefresh?: () => void;
  // 新增回调
  onAdd?: () => void;
  // 是否显示新增按钮
  showAddButton?: boolean;
  // 新增按钮文本
  addButtonText?: string;
  // 是否显示刷新按钮
  showRefreshButton?: boolean;
  // 空状态提示
  emptyText?: string;
}

/**
 * 高级表格组件
 */
export const ProTable = <T extends object>({
  title,
  toolbar,
  loading = false,
  pagination,
  onRefresh,
  onAdd,
  showAddButton = false,
  addButtonText = '新增',
  showRefreshButton = true,
  emptyText = '暂无数据',
  columns,
  dataSource,
  ...restProps
}: ProTableProps<T>) => {
  const renderToolbar = () => {
    if (!showRefreshButton && !showAddButton && !toolbar) return null;

    return (
      <Space>
        {toolbar}
        {showRefreshButton && (
          <Button icon={<ReloadOutlined />} onClick={onRefresh}>
            刷新
          </Button>
        )}
        {showAddButton && (
          <Button type="primary" icon={<PlusOutlined />} onClick={onAdd}>
            {addButtonText}
          </Button>
        )}
      </Space>
    );
  };

  const tablePagination: TablePaginationConfig | false = pagination
    ? {
        current: pagination.current,
        pageSize: pagination.pageSize,
        total: pagination.total,
        showSizeChanger: true,
        showQuickJumper: true,
        showTotal: (total) => `共 ${total} 条`,
        onChange: pagination.onChange,
      }
    : false;

  return (
    <Card title={title} extra={renderToolbar()}>
      <Table<T>
        columns={columns}
        dataSource={dataSource}
        loading={loading}
        pagination={tablePagination}
        locale={{ emptyText: <Empty description={emptyText} /> }}
        rowKey={(record) => (record as any).id || JSON.stringify(record)}
        {...restProps}
      />
    </Card>
  );
};

export default ProTable;
