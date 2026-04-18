import type { Supplier } from '@/api/types/your_project_name.schema';
import { Form, Input, Modal, Select } from 'antd';
import type { FormInstance } from 'antd/es/form';
import { FC, useEffect } from 'react';

interface SupplierModalProps {
  visible: boolean;
  editingSupplier: Supplier | null;
  form: FormInstance;
  onOk: () => void;
  onCancel: () => void;
}

/**
 * 风险等级选项
 */
const riskLevelOptions = [
  { label: '低风险', value: 'LOW' },
  { label: '中风险', value: 'MEDIUM' },
  { label: '高风险', value: 'HIGH' },
];

/**
 * 供应商表单弹窗组件
 */
const SupplierModal: FC<SupplierModalProps> = ({
  visible,
  editingSupplier,
  form,
  onOk,
  onCancel,
}) => {
  // 初始化表单数据
  useEffect(() => {
    if (visible) {
      if (editingSupplier) {
        // 后端返回的 status 可能是 "ACTIVE"/"INACTIVE" 或数字，统一转换为前端的 1/0
        const rawStatus = editingSupplier.status as string | number;
        const statusValue = rawStatus === 'ACTIVE' || rawStatus === 1 ? 1 : 0;
        form.setFieldsValue({
          supplierName: editingSupplier.supplierName,
          contactName: editingSupplier.contactName,
          contactPhone: editingSupplier.contactPhone,
          address: editingSupplier.address,
          riskLevel: editingSupplier.riskLevel,
          status: statusValue,
        });
      } else {
        form.resetFields();
      }
    }
  }, [visible, editingSupplier, form]);

  return (
    <Modal
      title={editingSupplier ? '编辑供应商' : '新增供应商'}
      open={visible}
      onOk={onOk}
      onCancel={onCancel}
      width={600}
    >
      <Form form={form} layout="vertical">
        {!editingSupplier && (
          <Form.Item
            name="supplierCode"
            label="供应商编码"
            rules={[{ required: true, message: '请输入供应商编码' }]}
          >
            <Input placeholder="请输入供应商编码" maxLength={50} />
          </Form.Item>
        )}
        <Form.Item
          name="supplierName"
          label="供应商名称"
          rules={[{ required: true, message: '请输入供应商名称' }]}
        >
          <Input placeholder="请输入供应商名称" maxLength={100} />
        </Form.Item>
        <Form.Item name="contactName" label="联系人">
          <Input placeholder="请输入联系人姓名" maxLength={50} />
        </Form.Item>
        <Form.Item name="contactPhone" label="联系电话">
          <Input placeholder="请输入联系电话" maxLength={20} />
        </Form.Item>
        <Form.Item name="address" label="地址">
          <Input.TextArea placeholder="请输入供应商地址" rows={2} maxLength={200} />
        </Form.Item>
        <Form.Item name="riskLevel" label="风险等级" initialValue="LOW">
          <Select placeholder="请选择风险等级" options={riskLevelOptions} />
        </Form.Item>
        {editingSupplier && (
          <Form.Item name="status" label="状态" initialValue={1}>
            <Select
              options={[
                { label: '启用', value: 1 },
                { label: '禁用', value: 0 },
              ]}
            />
          </Form.Item>
        )}
      </Form>
    </Modal>
  );
};

export default SupplierModal;
