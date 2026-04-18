import { HomeOutlined } from '@ant-design/icons';
import type { BreadcrumbProps } from 'antd';
import { Breadcrumb, Typography } from 'antd';
import { FC, ReactNode } from 'react';

const { Title } = Typography;

export interface PageContainerProps {
  // 页面标题
  title?: string;
  // 面包屑
  breadcrumb?: BreadcrumbProps['items'];
  // 额外操作区
  extra?: ReactNode;
  // 内容区
  children?: ReactNode;
  // 是否显示面包屑
  showBreadcrumb?: boolean;
  // 是否显示标题
  showTitle?: boolean;
}

/**
 * 页面容器组件
 */
export const PageContainer: FC<PageContainerProps> = ({
  title,
  breadcrumb,
  extra,
  children,
  showBreadcrumb = true,
  showTitle = true,
}) => {
  const defaultBreadcrumb: BreadcrumbProps['items'] = [
    {
      title: <HomeOutlined />,
      href: '/',
    },
  ];

  return (
    <div className="page-container">
      {showBreadcrumb && (
        <Breadcrumb
          items={defaultBreadcrumb?.concat(breadcrumb || [])}
          style={{ marginBottom: 16 }}
        />
      )}

      {(showTitle || extra) && (
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: 16,
          }}
        >
          {showTitle && title && <Title level={4} style={{ margin: 0 }}>{title}</Title>}
          {extra && <div className="page-extra">{extra}</div>}
        </div>
      )}

      <div className="page-content">{children}</div>
    </div>
  );
};

export default PageContainer;
