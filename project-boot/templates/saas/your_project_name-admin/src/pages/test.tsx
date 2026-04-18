import { Card, Alert, Tag, Descriptions } from 'antd';
import { useAuthStore } from '@/stores/authStore';

const TestPage = () => {
  const { user, permissions, menus } = useAuthStore();

  return (
    <div style={{ padding: '24px' }}>
      <h1>权限测试页面</h1>
      
      <Alert
        message="此页面用于测试权限分配功能"
        description="如果您能看到此页面，说明您拥有 platform:test:view 权限。"
        type="info"
        showIcon
        style={{ marginBottom: '24px' }}
      />

      <Card title="当前用户信息" style={{ marginBottom: '24px' }}>
        <Descriptions bordered column={2}>
          <Descriptions.Item label="用户名">{user?.username}</Descriptions.Item>
          <Descriptions.Item label="真实姓名">{user?.realName || '-'}</Descriptions.Item>
          <Descriptions.Item label="用户类型">
            <Tag color="blue">{user?.tenantType}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="租户ID">{user?.tenantId}</Descriptions.Item>
        </Descriptions>
      </Card>

      <Card title="权限列表" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
          {permissions?.map((perm: string) => (
            <Tag key={perm} color={perm.includes('test') ? 'green' : 'default'}>
              {perm}
            </Tag>
          ))}
        </div>
        {permissions?.length === 0 && (
          <Alert message="暂无权限" type="warning" />
        )}
      </Card>

      <Card title="菜单列表">
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
          {menus?.map((menu: any) => (
            <Tag key={menu.id} color="blue">
              {menu.name}
            </Tag>
          ))}
        </div>
        {menus?.length === 0 && (
          <Alert message="暂无菜单" type="warning" />
        )}
      </Card>
    </div>
  );
};

export default TestPage;
