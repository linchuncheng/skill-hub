import { ExclamationCircleOutlined } from '@ant-design/icons';
import { Modal } from 'antd';
import { FC, useState } from 'react';

export interface ConfirmModalProps {
  // 标题
  title?: string;
  // 内容
  content?: string;
  // 确认按钮文本
  okText?: string;
  // 取消按钮文本
  cancelText?: string;
  // 确认按钮类型
  okType?: 'primary' | 'default' | 'dashed' | 'link' | 'text';
  // 确认回调
  onOk?: () => Promise<void> | void;
  // 取消回调
  onCancel?: () => void;
  // 是否显示
  visible?: boolean;
  // 加载状态
  loading?: boolean;
  // 危险操作
  danger?: boolean;
}

/**
 * 确认弹窗组件
 */
export const ConfirmModal: FC<ConfirmModalProps> = ({
  title = '确认操作',
  content = '确定要执行此操作吗？',
  okText = '确定',
  cancelText = '取消',
  okType = 'primary',
  onOk,
  onCancel,
  visible = false,
  loading = false,
  danger = false,
}) => {
  const [confirmLoading, setConfirmLoading] = useState(false);

  const handleOk = async () => {
    if (onOk) {
      setConfirmLoading(true);
      try {
        await onOk();
      } finally {
        setConfirmLoading(false);
      }
    }
  };

  return (
    <Modal
      title={
        <span>
          {danger && <ExclamationCircleOutlined style={{ color: '#ff4d4f', marginRight: 8 }} />}
          {title}
        </span>
      }
      open={visible}
      onOk={handleOk}
      onCancel={onCancel}
      okText={okText}
      cancelText={cancelText}
      okType={danger ? 'primary' : okType}
      okButtonProps={{ danger: danger, loading: loading || confirmLoading }}
      cancelButtonProps={{ disabled: loading || confirmLoading }}
    >
      <p>{content}</p>
    </Modal>
  );
};

/**
 * 快捷确认方法
 */
export const showConfirm = (
  title: string,
  content: string,
  onOk?: () => Promise<void> | void,
  options?: Partial<ConfirmModalProps>
) => {
  Modal.confirm({
    title: (
      <span>
        {options?.danger && (
          <ExclamationCircleOutlined style={{ color: '#ff4d4f', marginRight: 8 }} />
        )}
        {title}
      </span>
    ),
    content,
    okText: options?.okText || '确定',
    cancelText: options?.cancelText || '取消',
    okType: options?.danger ? 'primary' : options?.okType || 'primary',
    okButtonProps: { danger: options?.danger },
    onOk: onOk,
    onCancel: options?.onCancel,
  });
};

export default ConfirmModal;
