import { ReloadOutlined, SearchOutlined } from '@ant-design/icons';
import type { FormInstance, FormProps } from 'antd';
import { Button, Col, Form, Row, Space } from 'antd';
import { FC, ReactNode } from 'react';

export interface SearchFormProps extends Omit<FormProps, 'children'> {
  // 是否显示展开/收起按钮
  collapsible?: boolean;
  // 默认是否展开
  defaultCollapsed?: boolean;
  // 搜索回调
  onSearch?: (values: any) => void;
  // 重置回调
  onReset?: () => void;
  // 加载状态
  loading?: boolean;
  // 表单项数量，用于计算布局
  itemsCount?: number;
  // 表单实例
  form?: FormInstance;
  // 子元素
  children?: ReactNode;
}

/**
 * 搜索表单组件
 */
export const SearchForm: FC<SearchFormProps> = ({
  collapsible = false,
  defaultCollapsed = true,
  onSearch,
  onReset,
  loading = false,
  itemsCount = 3,
  form,
  children,
  ...restProps
}) => {
  const handleSearch = (values: any) => {
    onSearch?.(values);
  };

  const handleReset = () => {
    form?.resetFields();
    onReset?.();
  };

  return (
    <Form form={form} layout="inline" onFinish={handleSearch} {...restProps}>
      <Row gutter={[16, 16]} style={{ width: '100%' }}>
        {children}
        <Col>
          <Space>
            <Button
              type="primary"
              htmlType="submit"
              icon={<SearchOutlined />}
              loading={loading}
            >
              查询
            </Button>
            <Button icon={<ReloadOutlined />} onClick={handleReset}>
              重置
            </Button>
          </Space>
        </Col>
      </Row>
    </Form>
  );
};

export default SearchForm;
