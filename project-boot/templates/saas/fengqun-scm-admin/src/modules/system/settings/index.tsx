import { useAuth } from '@/hooks/useAuth';
import {
    ApiOutlined,
    BellOutlined,
    DatabaseOutlined,
    GlobalOutlined,
    SafetyOutlined,
    UserOutlined,
} from '@ant-design/icons';
import { Button, Input, message } from 'antd';
import { FC, useState } from 'react';
import styles from './index.module.scss';

// 设置菜单项类型
interface SettingsMenuItem {
  key: string;
  label: string;
  icon: React.ReactNode;
}

const settingsMenuItems: SettingsMenuItem[] = [
  { key: 'profile', label: '个人信息', icon: <UserOutlined /> },
  { key: 'notifications', label: '通知设置', icon: <BellOutlined /> },
  { key: 'security', label: '安全设置', icon: <SafetyOutlined /> },
  { key: 'region', label: '区域与语言', icon: <GlobalOutlined /> },
  { key: 'data', label: '数据管理', icon: <DatabaseOutlined /> },
  { key: 'integration', label: '系统集成', icon: <ApiOutlined /> },
];

const SettingsPage: FC = () => {
  const { user } = useAuth();
  const [activeMenu, setActiveMenu] = useState('profile');
  const [formState, setFormState] = useState({
    name: user?.realName || user?.username || '',
    position: '系统管理员',
    email: user?.email || '',
    phone: user?.phone || '',
    department: '供应链事业部',
    employeeId: 'EMP-2019-0042',
  });

  // 获取用户名首字
  const getUserInitial = () => {
    const name = user?.realName || user?.username || '';
    return name.charAt(0);
  };

  // 获取用户类型文本
  const getTenantTypeText = (type?: string) => {
    const map: Record<string, string> = {
      PLATFORM: '超级管理员',
      PLATFORM_USER: '平台用户',
      TENANT_ADMIN: '租户管理员',
      TENANT_USER: '租户用户',
    };
    return type ? (map[type] || type) : '-';
  };

  const handleSave = () => {
    message.success('保存成功');
  };

  const renderContent = () => {
    switch (activeMenu) {
      case 'profile':
        return (
          <div className={styles.contentCard}>
            <h2 className={styles.sectionTitle}>个人信息</h2>
            
            {/* 头像区域 */}
            <div className={styles.avatarSection}>
              <div className={styles.largeAvatar}>
                <span>{getUserInitial()}</span>
              </div>
              <div className={styles.avatarInfo}>
                <div className={styles.avatarName}>{user?.realName || user?.username}</div>
                <div className={styles.avatarRole}>
                  {getTenantTypeText(user?.tenantType)} · {formState.department}
                </div>
                <Button type="link" className={styles.changeAvatarBtn}>
                  更换头像
                </Button>
              </div>
            </div>

            {/* 表单区域 */}
            <div className={styles.formGrid}>
              <div className={styles.formItem}>
                <label className={styles.formLabel}>姓名</label>
                <Input
                  value={formState.name}
                  onChange={(e) => setFormState({ ...formState, name: e.target.value })}
                  className={styles.formInput}
                />
              </div>
              <div className={styles.formItem}>
                <label className={styles.formLabel}>职位</label>
                <Input
                  value={formState.position}
                  onChange={(e) => setFormState({ ...formState, position: e.target.value })}
                  className={styles.formInput}
                />
              </div>
              <div className={styles.formItem}>
                <label className={styles.formLabel}>邮箱</label>
                <Input
                  value={formState.email}
                  onChange={(e) => setFormState({ ...formState, email: e.target.value })}
                  className={styles.formInput}
                />
              </div>
              <div className={styles.formItem}>
                <label className={styles.formLabel}>手机</label>
                <Input
                  value={formState.phone}
                  onChange={(e) => setFormState({ ...formState, phone: e.target.value })}
                  className={styles.formInput}
                />
              </div>
              <div className={styles.formItem}>
                <label className={styles.formLabel}>部门</label>
                <Input
                  value={formState.department}
                  onChange={(e) => setFormState({ ...formState, department: e.target.value })}
                  className={styles.formInput}
                />
              </div>
              <div className={styles.formItem}>
                <label className={styles.formLabel}>工号</label>
                <Input
                  value={formState.employeeId}
                  onChange={(e) => setFormState({ ...formState, employeeId: e.target.value })}
                  className={styles.formInput}
                />
              </div>
            </div>

            {/* 保存按钮 */}
            <div className={styles.formActions}>
              <Button type="primary" className={styles.saveBtn} onClick={handleSave}>
                保存更改
              </Button>
            </div>
          </div>
        );

      case 'notifications':
        return (
          <div className={styles.contentCard}>
            <h2 className={styles.sectionTitle}>通知设置</h2>
            <div className={styles.placeholderContent}>
              通知设置功能开发中...
            </div>
          </div>
        );

      case 'security':
        return (
          <div className={styles.contentCard}>
            <h2 className={styles.sectionTitle}>安全设置</h2>
            <div className={styles.placeholderContent}>
              安全设置功能开发中...
            </div>
          </div>
        );

      case 'region':
        return (
          <div className={styles.contentCard}>
            <h2 className={styles.sectionTitle}>区域与语言</h2>
            <div className={styles.placeholderContent}>
              区域与语言功能开发中...
            </div>
          </div>
        );

      case 'data':
        return (
          <div className={styles.contentCard}>
            <h2 className={styles.sectionTitle}>数据管理</h2>
            <div className={styles.placeholderContent}>
              数据管理功能开发中...
            </div>
          </div>
        );

      case 'integration':
        return (
          <div className={styles.contentCard}>
            <h2 className={styles.sectionTitle}>系统集成</h2>
            <div className={styles.placeholderContent}>
              系统集成功能开发中...
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className={styles.container}>
      {/* Main Content */}
      <div className={styles.mainContent}>
        {/* 左侧菜单 */}
        <div className={styles.menuCard}>
          <div className={styles.menuList}>
            {settingsMenuItems.map((item) => (
              <div
                key={item.key}
                className={`${styles.menuItem} ${activeMenu === item.key ? styles.menuItemActive : ''}`}
                onClick={() => setActiveMenu(item.key)}
              >
                <div className={styles.menuItemIcon}>{item.icon}</div>
                <span className={styles.menuItemLabel}>{item.label}</span>
              </div>
            ))}
          </div>
        </div>

        {/* 右侧内容 */}
        {renderContent()}
      </div>
    </div>
  );
};

export default SettingsPage;
