import { useThemeContext } from '@/providers/ThemeProvider';
import { useAuthStore } from '@/stores/authStore';
import {
    CheckCircleOutlined,
    CrownOutlined,
    MenuOutlined,
    SafetyCertificateOutlined,
    TeamOutlined,
    UserOutlined,
} from '@ant-design/icons';
import { Avatar, Card, Col, Divider, Row, Tag } from 'antd';
import styles from './dashboard.module.scss';

const Dashboard = () => {
  const { user, permissions, menus } = useAuthStore();
  const { themeMode } = useThemeContext();
  const isDark = themeMode === 'dark';

  const getTenantTypeText = (type: string) => {
    const map: Record<string, string> = {
      PLATFORM: '超级管理员',
      PLATFORM_USER: '平台用户',
      TENANT_ADMIN: '租户管理员',
      TENANT_USER: '租户用户',
    };
    return map[type] || type;
  };

  const getTenantTypeColor = (type: string) => {
    const map: Record<string, string> = {
      PLATFORM: '#EF4444',
      PLATFORM_USER: '#F59E0B',
      TENANT_ADMIN: '#2563EB',
      TENANT_USER: '#10B981',
    };
    return map[type] || '#64748B';
  };

  const getTenantTypeBg = (type: string) => {
    // Dark mode uses semi-transparent backgrounds
    if (isDark) {
      const darkMap: Record<string, string> = {
        PLATFORM: 'rgba(239, 68, 68, 0.15)',
        PLATFORM_USER: 'rgba(245, 158, 11, 0.15)',
        TENANT_ADMIN: 'rgba(37, 99, 235, 0.15)',
        TENANT_USER: 'rgba(16, 185, 129, 0.15)',
      };
      return darkMap[type] || 'rgba(255, 255, 255, 0.07)';
    }
    const map: Record<string, string> = {
      PLATFORM: '#FEF2F2',
      PLATFORM_USER: '#FFFBEB',
      TENANT_ADMIN: '#EFF6FF',
      TENANT_USER: '#ECFDF5',
    };
    return map[type] || '#F8FAFC';
  };

  const roleCards = [
    {
      type: 'PLATFORM',
      title: '超级管理员',
      icon: <CrownOutlined />,
      desc: '拥有所有权限，无需角色分配',
      color: '#EF4444',
      bgColor: isDark ? 'rgba(239, 68, 68, 0.15)' : '#FEF2F2',
    },
    {
      type: 'PLATFORM_USER',
      title: '平台用户',
      icon: <TeamOutlined />,
      desc: '由超级管理员分配角色获取权限',
      color: '#F59E0B',
      bgColor: isDark ? 'rgba(245, 158, 11, 0.15)' : '#FFFBEB',
    },
    {
      type: 'TENANT_ADMIN',
      title: '租户管理员',
      icon: <SafetyCertificateOutlined />,
      desc: '默认权限 + 平台分配的角色权限',
      color: '#2563EB',
      bgColor: isDark ? 'rgba(37, 99, 235, 0.15)' : '#EFF6FF',
    },
    {
      type: 'TENANT_USER',
      title: '租户用户',
      icon: <UserOutlined />,
      desc: '由租户管理员分配角色获取权限',
      color: '#10B981',
      bgColor: isDark ? 'rgba(16, 185, 129, 0.15)' : '#ECFDF5',
    },
  ];

  return (
    <div className={styles.dashboard}>
      {/* 页面标题 */}
      <div className={styles.header}>
        <h1>控制台</h1>
        <p>欢迎回来，{user?.realName || user?.username}</p>
      </div>

      {/* 统计卡片行 */}
      <Row gutter={[24, 24]} className={styles.statsRow}>
        <Col xs={24} sm={12} lg={8}>
          <Card className={styles.statCard} bordered={false}>
            <div className={styles.statContent}>
              <div
                className={styles.statIcon}
                style={{ background: isDark ? 'rgba(37, 99, 235, 0.15)' : '#EFF6FF', color: '#2563EB' }}
              >
                <SafetyCertificateOutlined />
              </div>
              <div className={styles.statInfo}>
                <span className={styles.statLabel}>权限数量</span>
                <span className={styles.statValue}>{permissions?.length || 0}</span>
              </div>
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={8}>
          <Card className={styles.statCard} bordered={false}>
            <div className={styles.statContent}>
              <div
                className={styles.statIcon}
                style={{ background: isDark ? 'rgba(16, 185, 129, 0.15)' : '#F0FDF4', color: '#10B981' }}
              >
                <MenuOutlined />
              </div>
              <div className={styles.statInfo}>
                <span className={styles.statLabel}>菜单数量</span>
                <span className={styles.statValue}>{menus?.length || 0}</span>
              </div>
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={8}>
          <Card className={styles.statCard} bordered={false}>
            <div className={styles.statContent}>
              <div
                className={styles.statIcon}
                style={{
                  background: getTenantTypeBg(user?.tenantType),
                  color: getTenantTypeColor(user?.tenantType),
                }}
              >
                <UserOutlined />
              </div>
              <div className={styles.statInfo}>
                <span className={styles.statLabel}>用户类型</span>
                <span className={styles.statValue}>
                  {getTenantTypeText(user?.tenantType)}
                </span>
              </div>
            </div>
          </Card>
        </Col>
      </Row>

      {/* 内容区域 */}
      <Row gutter={[24, 24]}>
        {/* 用户权限模型 */}
        <Col xs={24} lg={16}>
          <Card className={styles.infoCard} title="用户权限模型" bordered={false}>
            <Row gutter={[16, 16]}>
              {roleCards.map((role) => (
                <Col xs={24} sm={12} key={role.type}>
                  <div
                    className={styles.roleCard}
                    style={{
                      background: role.bgColor,
                      borderColor: role.color,
                    }}
                  >
                    <div className={styles.roleIcon} style={{ color: role.color }}>
                      {role.icon}
                    </div>
                    <div className={styles.roleInfo}>
                      <h4 style={{ color: role.color }}>{role.title}</h4>
                      <p>{role.desc}</p>
                    </div>
                    {user?.tenantType === role.type && (
                      <div className={styles.currentBadge}>
                        <CheckCircleOutlined />
                      </div>
                    )}
                  </div>
                </Col>
              ))}
            </Row>
          </Card>
        </Col>

        {/* 个人信息 */}
        <Col xs={24} lg={8}>
          <Card className={styles.profileCard} title="个人信息" bordered={false}>
            <div className={styles.profileHeader}>
              <Avatar
                size={64}
                icon={<UserOutlined />}
                style={{
                  background: getTenantTypeColor(user?.tenantType),
                }}
              />
              <div className={styles.profileInfo}>
                <h3>{user?.realName || user?.username}</h3>
                <Tag
                  style={{
                    color: getTenantTypeColor(user?.tenantType),
                    background: getTenantTypeBg(user?.tenantType),
                    border: 'none',
                    fontWeight: 500,
                  }}
                >
                  {getTenantTypeText(user?.tenantType)}
                </Tag>
              </div>
            </div>
            <Divider style={{ margin: '16px 0' }} />
            <div className={styles.profileDetails}>
              <div className={styles.detailItem}>
                <span className={styles.label}>用户名</span>
                <span className={styles.value}>{user?.username}</span>
              </div>
              <div className={styles.detailItem}>
                <span className={styles.label}>租户ID</span>
                <span className={styles.value}>{user?.tenantId}</span>
              </div>
            </div>
          </Card>
        </Col>
      </Row>

      {/* 快捷操作 */}
      <Row gutter={[24, 24]} style={{ marginTop: 24 }}>
        <Col xs={24}>
          <Card className={styles.quickCard} title="快捷操作" bordered={false}>
            <div className={styles.quickActions}>
              <div className={styles.quickItem}>
                <div
                  className={styles.quickIcon}
                  style={{ background: isDark ? 'rgba(37, 99, 235, 0.15)' : '#EFF6FF', color: '#2563EB' }}
                >
                  <TeamOutlined />
                </div>
                <span>用户管理</span>
              </div>
              <div className={styles.quickItem}>
                <div
                  className={styles.quickIcon}
                  style={{ background: isDark ? 'rgba(16, 185, 129, 0.15)' : '#F0FDF4', color: '#10B981' }}
                >
                  <SafetyCertificateOutlined />
                </div>
                <span>角色权限</span>
              </div>
              <div className={styles.quickItem}>
                <div
                  className={styles.quickIcon}
                  style={{ background: isDark ? 'rgba(245, 158, 11, 0.15)' : '#FFFBEB', color: '#F59E0B' }}
                >
                  <MenuOutlined />
                </div>
                <span>菜单配置</span>
              </div>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
