/**
 * TableColumnActions - 表格操作列公共组件
 * 
 * 特性：
 * - 自动固定到右侧
 * - 超过2个操作自动折叠到"..."菜单
 * - 居中对齐
 * - 紧凑间距
 * 
 * 使用示例：
 * ```tsx
 * import { TableColumnActions } from '@/components/common/TableColumnActions';
 * 
 * const columns = [
 *   // ... 其他列
 *   TableColumnActions({
 *     width: 180,
 *     actions: [
 *       { key: 'edit', label: '编辑', icon: <EditOutlined />, onClick: handleEdit },
 *       { key: 'delete', label: '删除', icon: <DeleteOutlined />, onClick: handleDelete, danger: true, needConfirm: true },
 *     ],
 *   }),
 * ];
 * ```
 */
import { EllipsisOutlined } from '@ant-design/icons';
import { Button, Dropdown, Modal, Popconfirm, Space } from 'antd';
import type { ReactNode } from 'react';

export interface ActionItem<T = any> {
  key: string;
  label: string;
  icon: ReactNode;
  onClick: (record: T) => void;
  danger?: boolean;
  needConfirm?: boolean;
  confirmTitle?: string;
}

export interface TableColumnActionsProps<T = any> {
  /** 列宽，默认 180 */
  width?: number;
  /** 操作项列表生成函数 */
  actions: (record: T) => ActionItem<T>[];
  /** 直接显示的最大操作数，默认 2 */
  maxVisible?: number;
  /** 自定义类名 */
  className?: string;
}

/**
 * 创建操作列配置
 */
export function TableColumnActions<T = any>({
  width = 180,
  actions,
  maxVisible = 2,
  className,
}: TableColumnActionsProps<T>) {
  return {
    title: '操作',
    key: 'action',
    width,
    fixed: 'right' as const,
    align: 'center' as const,
    className: className || 'action-column',
    onHeaderCell: () => ({
      style: { textAlign: 'center' as const },
    }),
    render: (_: any, record: T) => <ActionCell actions={actions(record)} maxVisible={maxVisible} />,
  };
}

/**
 * 操作单元格组件（内部使用）
 */
function ActionCell({ actions, maxVisible }: { actions: ActionItem[]; maxVisible: number }) {
  // 如果操作项 <= maxVisible，直接显示
  if (actions.length <= maxVisible) {
    return (
      <div style={{ textAlign: 'center' }}>
        <Space size={4}>
          {actions.map((action) => renderAction(action))}
        </Space>
      </div>
    );
  }

  // 如果操作项 > maxVisible，前 maxVisible 个直接显示，其余收拢到"..."
  const visibleActions = actions.slice(0, maxVisible);
  const moreActions = actions.slice(maxVisible);

  const moreMenuItems = moreActions.map((action) => ({
    key: action.key,
    label: action.label,
    icon: action.icon,
    danger: action.danger,
    onClick: action.needConfirm
      ? () =>
          Modal.confirm({
            title: `确认${action.label}？`,
            onOk: action.onClick,
          })
      : action.onClick,
  }));

  return (
    <div style={{ textAlign: 'center' }}>
      <Space size={4}>
        {visibleActions.map((action) => renderAction(action))}
        <Dropdown menu={{ items: moreMenuItems }} placement="bottomRight">
          <Button type="link" size="small" icon={<EllipsisOutlined />} />
        </Dropdown>
      </Space>
    </div>
  );
}

/**
 * 渲染单个操作按钮
 */
function renderAction(action: ActionItem) {
  if (action.needConfirm) {
    return (
      <Popconfirm key={action.key} title={`确认${action.label}？`} onConfirm={action.onClick}>
        <Button type="link" size="small" danger={action.danger} icon={action.icon}>
          {action.label}
        </Button>
      </Popconfirm>
    );
  }

  return (
    <Button
      key={action.key}
      type="link"
      size="small"
      danger={action.danger}
      icon={action.icon}
      onClick={action.onClick}
    >
      {action.label}
    </Button>
  );
}
