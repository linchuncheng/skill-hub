import { routes } from '@/config/routes';
import { useAuth } from '@/hooks/useAuth';
import { useDocumentTitle } from '@/hooks/useDocumentTitle';
import { useThemeContext } from '@/providers/ThemeProvider';
import { useGlobalStore } from '@/stores/globalStore';
import { useTenantStore } from '@/stores/tenantStore';
import {
  AlertOutlined,
  AppstoreOutlined,
  ArrowDownOutlined,
  ArrowUpOutlined,
  AuditOutlined,
  BankOutlined,
  BarChartOutlined,
  BlockOutlined,
  CarOutlined,
  CheckSquareOutlined,
  CloseCircleOutlined,
  CloseOutlined,
  ClusterOutlined,
  ContactsOutlined,
  ContainerOutlined,
  ControlOutlined,
  CustomerServiceOutlined,
  DashboardOutlined,
  DatabaseOutlined,
  DownOutlined,
  DragOutlined,
  EnvironmentOutlined,
  ExperimentOutlined,
  ExportOutlined,
  FileDoneOutlined,
  FileTextOutlined,
  FilterOutlined,
  GiftOutlined,
  HomeOutlined,
  ImportOutlined,
  // WMS/FMS 业务图标
  InboxOutlined,
  LayoutOutlined,
  LineChartOutlined,
  LoginOutlined,
  LogoutOutlined,
  MailOutlined,
  MenuFoldOutlined,
  MenuOutlined,
  MenuUnfoldOutlined,
  MoonOutlined,
  MoreOutlined,
  NodeIndexOutlined,
  OrderedListOutlined,
  PhoneOutlined,
  ProfileOutlined,
  ReconciliationOutlined,
  RetweetOutlined,
  RollbackOutlined,
  SafetyCertificateOutlined,
  SafetyOutlined,
  ScheduleOutlined,
  SearchOutlined,
  SettingOutlined,
  ShopOutlined,
  ShoppingCartOutlined,
  ShoppingOutlined,
  SolutionOutlined,
  SunOutlined,
  SwapLeftOutlined,
  SwapOutlined,
  TagOutlined,
  TagsOutlined,
  TeamOutlined,
  ThunderboltOutlined,
  ToolOutlined,
  UsergroupAddOutlined,
  UserOutlined,
  VerticalRightOutlined
} from '@ant-design/icons';
import type { MenuProps } from 'antd';
import { Button, Descriptions, Dropdown, Layout, Menu, Modal, Spin, Tabs, Tag, Tooltip } from 'antd';
import { FC, ReactNode, Suspense, useEffect, useMemo, useState } from 'react';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import styles from './index.module.scss';

const { Header, Sider, Content } = Layout;

// 图标映射表
const iconMapping: Record<string, ReactNode> = {
  // 基础图标
  home: <HomeOutlined />,
  dashboard: <DashboardOutlined />,
  setting: <SettingOutlined />,
  shop: <ShopOutlined />,
  safety: <SafetyOutlined />,
  menu: <MenuOutlined />,
  appstore: <AppstoreOutlined />,
  team: <TeamOutlined />,
  user: <UserOutlined />,
  experiment: <ExperimentOutlined />,
  // 角色权限相关
  'usergroup-add': <UsergroupAddOutlined />,
  usergroup: <ClusterOutlined />,
  role: <SafetyOutlined />,
  permission: <SafetyOutlined />,
  // 业务图标
  file: <FileTextOutlined />,
  'file-text': <FileTextOutlined />,
  database: <DatabaseOutlined />,
  audit: <AuditOutlined />,
  container: <ContainerOutlined />,
  list: <OrderedListOutlined />,
  profile: <ProfileOutlined />,
  tool: <ToolOutlined />,
  // WMS 仓储管理图标
  warehouse: <InboxOutlined />,
  inbox: <InboxOutlined />,
  shopping: <ShoppingOutlined />,
  'shopping-cart': <ShoppingCartOutlined />,
  block: <BlockOutlined />,
  apartment: <BlockOutlined />,
  tag: <TagOutlined />,
  tags: <TagsOutlined />,
  login: <LoginOutlined />,
  logout: <LogoutOutlined />,
  import: <ImportOutlined />,
  export: <ExportOutlined />,
  thunderbolt: <ThunderboltOutlined />,
  search: <SearchOutlined />,
  swap: <SwapOutlined />,
  drag: <DragOutlined />,
  bank: <BankOutlined />,
  environment: <EnvironmentOutlined />,
  'bar-chart': <BarChartOutlined />,
  'safety-certificate': <SafetyCertificateOutlined />,
  alert: <AlertOutlined />,
  reconciliation: <ReconciliationOutlined />,
  retweet: <RetweetOutlined />,
  contacts: <ContactsOutlined />,
  solution: <SolutionOutlined />,
  gift: <GiftOutlined />,
  // 新增图标
  cluster: <ClusterOutlined />,
  filter: <FilterOutlined />,
  'arrow-down': <ArrowDownOutlined />,
  'arrow-up': <ArrowUpOutlined />,
  'line-chart': <LineChartOutlined />,
  shield: <SafetyOutlined />,
  'check-square': <CheckSquareOutlined />,
  'swap-left': <SwapLeftOutlined />,
  layout: <LayoutOutlined />,
  control: <ControlOutlined />,
  // TMS 运输管理图标
  car: <CarOutlined />,
  'node-index': <NodeIndexOutlined />,
  schedule: <ScheduleOutlined />,
  'file-done': <FileDoneOutlined />,
  rollback: <RollbackOutlined />,
  'customer-service': <CustomerServiceOutlined />,
};

// 获取图标组件
const getIcon = (iconName?: string): ReactNode => {
  if (!iconName) return null;
  return iconMapping[iconName.toLowerCase()] || null;
};

const BasicLayout: FC = () => {
  // 启用动态页面标题和 favicon
  useDocumentTitle();

  const navigate = useNavigate();
  const location = useLocation();
  const { user, menus, logout } = useAuth();
  const { currentTenant } = useTenantStore();
  const { 
    sidebarCollapsed, 
    setSidebarCollapsed,
    tabs,
    activeTabKey,
    addTab,
    removeTab,
    setActiveTab,
    removeOtherTabs,
    removeRightTabs,
    removeAllTabs,
  } = useGlobalStore();
  // openKeys 使用本地状态，不持久化
  const [openKeys, setOpenKeys] = useState<string[]>([]);
  const { themeMode, toggleTheme, setThemeMode } = useThemeContext();
  // 计算实际的主题模式（system 模式下需要根据系统偏好判断）
  const getEffectiveTheme = () => {
    if (themeMode === 'system') {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    return themeMode;
  };
  const isDark = getEffectiveTheme() === 'dark';

  // 个人信息弹窗状态
  const [profileModalVisible, setProfileModalVisible] = useState(false);

  // 菜单搜索状态
  const [menuSearchKeyword, setMenuSearchKeyword] = useState('');
  // openKeys 已从 globalStore 获取，不需要本地状态

  // 根据当前路由自动展开菜单
  useEffect(() => {
    // 等待 menus 数据加载完成
    if (!menus || menus.length === 0) {
      return;
    }

    const currentPath = location.pathname;
    
    // 扁平化查找所有菜单及其父级 key
    const findParentKeys = (menuList: any[], targetPath: string, parentKey?: string): string[] => {
      for (const menu of menuList) {
        const menuKey = menu.key || menu.path;
        // 找到目标菜单（匹配 path 或 key）
        if (menu.path === targetPath || menuKey === targetPath) {
          return parentKey ? [parentKey] : [];
        }
        // 递归查找子菜单
        if (menu.children) {
          const found = findParentKeys(menu.children, targetPath, menuKey);
          if (found.length > 0) {
            return found;
          }
        }
      }
      return [];
    };
    
    const parentKeys = findParentKeys(menus, currentPath);
    setOpenKeys(parentKeys);
  }, [location.pathname, menus]);

  // 用户类型文本映射
  const getTenantTypeText = (type?: string) => {
    const map: Record<string, string> = {
      PLATFORM: '超级管理员',
      PLATFORM_USER: '平台用户',
      TENANT_ADMIN: '租户管理员',
      TENANT_USER: '租户用户',
    };
    return type ? (map[type] || type) : '-';
  };

  // 用户类型颜色映射
  const getTenantTypeColor = (type?: string) => {
    const map: Record<string, string> = {
      PLATFORM: 'red',
      PLATFORM_USER: 'orange',
      TENANT_ADMIN: 'blue',
      TENANT_USER: 'green',
    };
    return type ? (map[type] || 'default') : 'default';
  };

  // 获取用户名首字
  const getUserInitial = () => {
    const name = user?.realName || user?.username || '';
    return name.charAt(0);
  };

  // 获取当前页面标题
  const getPageTitle = () => {
    const currentPath = location.pathname;
    const findMenuLabel = (menuList: any[]): string | null => {
      for (const menu of menuList) {
        if (menu.path === currentPath) return menu.name || menu.label;
        if (menu.children) {
          const childLabel = findMenuLabel(menu.children);
          if (childLabel) return childLabel;
        }
      }
      return null;
    };
    return findMenuLabel(menus) || '概览';
  };

  // 根据路由自动添加 TAB
  useEffect(() => {
    const currentPath = location.pathname;
    
    // 排除根路径（会被重定向到 /dashboard）
    if (currentPath === '/' || currentPath === '') {
      return;
    }
    
    // 先从菜单中查找
    const findMenuLabel = (menuList: any[]): string | null => {
      for (const menu of menuList) {
        if (menu.path === currentPath) return menu.name;
        if (menu.children) {
          const childLabel = findMenuLabel(menu.children);
          if (childLabel) return childLabel;
        }
      }
      return null;
    };
    
    // 如果菜单中找不到，从路由配置中查找
    let label = findMenuLabel(menus);
    if (!label) {
      const route = routes.find((r: any) => r.path === currentPath);
      label = route?.name || '未知页面';
    }
    
    // 如果不在 tabs 中，添加新 tab
    const exists = tabs.find((t) => t.key === currentPath);
    if (!exists && currentPath !== '/dashboard') {
      addTab({
        key: currentPath,
        label,
        path: currentPath,
        closable: true,
      });
    } else if (exists) {
      setActiveTab(currentPath);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.pathname]);

  // 切换 TAB
  const handleTabChange = (key: string) => {
    setActiveTab(key);
    navigate(key);
  };

  // 关闭 TAB
  const handleTabClose = (key: string) => {
    const currentIndex = tabs.findIndex((t) => t.key === key);
    removeTab(key);
    
    // 如果关闭的是当前激活的 tab，跳转到前一个 tab
    if (key === activeTabKey && tabs.length > 1) {
      const newTab = tabs[currentIndex - 1] || tabs[currentIndex + 1];
      if (newTab) {
        navigate(newTab.key);
      }
    }
  };

  // 关闭其他 TAB
  const handleCloseOtherTabs = (key: string) => {
    removeOtherTabs(key);
    navigate(key);
  };

  // 关闭右侧 TAB
  const handleCloseRightTabs = (key: string) => {
    const clickedIndex = tabs.findIndex((t) => t.key === key);
    const activeIndex = tabs.findIndex((t) => t.key === activeTabKey);
    
    removeRightTabs(key);
    
    // 如果当前激活的标签在关闭范围内（索引 > 点击的索引），需要跳转
    if (activeIndex > clickedIndex) {
      setActiveTab(key);  // 更新激活标签
      navigate(key);       // 导航到点击的标签
    }
  };

  // 关闭全部 TAB（保留首页）
  const handleRemoveAllTabs = () => {
    removeAllTabs();
    navigate('/dashboard');
  };

  // 获取 TAB 右键菜单项
  const getTabContextMenuItems = (tabKey: string, closable?: boolean) => {
    const tabIndex = tabs.findIndex((t) => t.key === tabKey);
    const hasRightTabs = tabIndex >= 0 && tabIndex < tabs.length - 1;
    const hasOtherTabs = tabs.filter((t) => t.key !== tabKey && t.closable).length > 0;
    
    const menuItems: MenuProps['items'] = [
      {
        key: 'close',
        label: '关闭当前标签',
        icon: <CloseOutlined />,
        disabled: !closable,
      },
      {
        key: 'closeOther',
        label: '关闭其他标签',
        icon: <CloseCircleOutlined />,
        disabled: !hasOtherTabs,
      },
      {
        key: 'closeRight',
        label: '关闭右侧标签',
        icon: <VerticalRightOutlined />,
        disabled: !hasRightTabs,
      },
    ];
    
    return menuItems;
  };

  // 处理 TAB 右键菜单点击
  const handleTabContextMenuClick = (tabKey: string) => ({ key }: { key: string }) => {
    switch (key) {
      case 'close':
        handleTabClose(tabKey);
        break;
      case 'closeOther':
        handleCloseOtherTabs(tabKey);
        break;
      case 'closeRight':
        handleCloseRightTabs(tabKey);
        break;
    }
  };

  // 渲染 TAB 标签（带右键菜单）
  const renderTabLabel = (tab: { key: string; label: string; closable?: boolean }) => {
    return (
      <Dropdown
        menu={{ 
          items: getTabContextMenuItems(tab.key, tab.closable),
          onClick: handleTabContextMenuClick(tab.key),
        }}
        trigger={['contextMenu']}
      >
        <span>{tab.label}</span>
      </Dropdown>
    );
  };

  // 过滤菜单项
  const { filteredMenuItems, matchedParentKeys } = useMemo(() => {
    // 首页菜单项（固定显示在第一位）
    const homeMenuItem = {
      key: '/dashboard',
      label: '首页',
      icon: getIcon('dashboard'),
    };
    
    if (!menuSearchKeyword.trim()) {
      return {
        filteredMenuItems: [
          homeMenuItem,
          ...menus.map((menu) => ({
            key: menu.path,
            label: menu.name,
            icon: getIcon(menu.icon),
            children: menu.children?.map((child: any) => ({
              key: child.path,
              label: child.name,
              icon: getIcon(child.icon),
            })),
          }))
        ],
        matchedParentKeys: [],
      };
    }

    const keyword = menuSearchKeyword.toLowerCase();
    const parentKeys: string[] = [];

    const items = menus
      .map((menu) => {
        const matchedChildren =
          menu.children?.filter((child: any) => child.name?.toLowerCase().includes(keyword)) || [];

        const menuMatch = menu.name?.toLowerCase().includes(keyword);

        if (menuMatch) {
          parentKeys.push(menu.path);
          return {
            key: menu.path,
            label: menu.name,
            icon: getIcon(menu.icon),
            children: menu.children?.map((child: any) => ({
              key: child.path,
              label: child.name,
              icon: getIcon(child.icon),
            })),
          };
        }

        if (matchedChildren.length > 0) {
          parentKeys.push(menu.path);
          return {
            key: menu.path,
            label: menu.name,
            icon: getIcon(menu.icon),
            children: matchedChildren.map((child: any) => ({
              key: child.path,
              label: child.name,
              icon: getIcon(child.icon),
            })),
          };
        }

        return null;
      })
      .filter(Boolean);

    return { filteredMenuItems: items, matchedParentKeys: parentKeys };
  }, [menus, menuSearchKeyword]);

  // 搜索时自动展开匹配的父菜单
  useEffect(() => {
    if (menuSearchKeyword.trim()) {
      setOpenKeys(matchedParentKeys);
    } else {
      setOpenKeys([]);
    }
  }, [menuSearchKeyword, matchedParentKeys]);

  const userMenuItems: MenuProps['items'] = [
    {
      key: 'profile',
      label: '个人信息',
      icon: <UserOutlined />,
      onClick: () => setProfileModalVisible(true),
    },
    {
      key: 'settings',
      label: '系统设置',
      icon: <SettingOutlined />,
      onClick: () => navigate('/settings'),
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      label: '退出登录',
      icon: <LogoutOutlined />,
      onClick: logout,
    },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        width={240}
        collapsedWidth={60}
        theme={isDark ? 'dark' : 'light'}
        collapsed={sidebarCollapsed}
        onCollapse={(collapsed) => setSidebarCollapsed(collapsed)}
        className={styles.sider}
        collapsible
        trigger={null}
      >
        {/* Logo 区域 */}
        <div className={`${styles.logo} ${sidebarCollapsed ? styles.logoCollapsed : ''}`}>
          <div className={styles.logoLeft} onClick={() => navigate('/')} style={{ cursor: 'pointer' }}>
            <div className={styles.logoIcon}>
              {currentTenant?.logo && currentTenant.logo.trim() ? (
                <img 
                  src={currentTenant.logo} 
                  alt="Logo" 
                  style={{ 
                    width: '32px', 
                    height: '32px', 
                    borderRadius: '8px',
                    objectFit: 'contain'
                  }} 
                  onError={(e) => {
                    // 图片加载失败时隐藏 img，显示默认 SVG
                    (e.target as HTMLImageElement).style.display = 'none';
                  }}
                />
              ) : (
                <svg width="32" height="32" viewBox="0 0 265 265" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path 
                    fillRule="evenodd" 
                    clipRule="evenodd" 
                    d="M246.36 72.2596C250.337 78.1538 253.726 84.4239 256.479 90.9801C261.858 104.164 264.65 118.26 264.706 132.5C264.643 146.716 261.85 160.787 256.479 173.947C253.727 180.527 250.338 186.822 246.36 192.741C239.348 203.374 231.353 213.324 222.481 222.46C213.345 231.617 203.239 239.751 192.341 246.717C186.442 250.618 180.204 253.983 173.704 256.769C160.574 262.135 146.536 264.93 132.353 265C118.146 264.937 104.083 262.143 90.9294 256.769C84.4458 253.996 78.2314 250.631 72.3652 246.717C61.4584 239.733 51.3298 231.601 42.1528 222.46C33.3264 213.303 25.3577 203.354 18.3469 192.741C6.34321 174.95 -0.0477668 153.965 0.00111086 132.5C-0.0928676 111.029 6.30189 90.0303 18.3469 72.2596C25.3204 61.6187 33.2917 51.6674 42.1528 42.5401C51.3289 33.3768 61.4572 25.2207 72.3652 18.2108C90.0982 6.28967 110.989 -0.0524621 132.353 0.000222297C146.554 0 160.605 2.79716 173.704 8.23143C180.218 10.9595 186.459 14.301 192.341 18.2108C203.241 25.2016 213.347 33.3597 222.481 42.5401C231.388 51.646 239.385 61.5996 246.36 72.2596ZM153.538 244.677C154.433 244.789 155.338 244.789 156.232 244.677C160.139 243.798 163.982 242.654 167.735 241.254C173.381 238.878 178.793 235.975 183.897 232.586C193.462 226.433 202.345 219.278 210.396 211.243C218.206 203.219 225.227 194.461 231.363 185.093C234.825 179.993 237.752 174.549 240.099 168.849C249.608 145.828 249.608 119.974 240.099 96.9535C237.751 91.2767 234.823 85.8578 231.363 80.7825C225.227 71.414 218.206 62.6568 210.396 54.6321C202.363 46.5766 193.478 39.4201 183.897 33.2894C178.792 29.88 173.381 26.9537 167.735 24.5483C156.382 19.8147 144.215 17.3403 131.916 17.264C119.595 17.3474 107.406 19.8211 96.0256 24.5483C90.4028 26.956 85.0167 29.8823 79.9366 33.2894C70.3552 39.4204 61.4697 46.5768 53.4369 54.6321C45.6016 62.6535 38.5558 71.4105 32.3972 80.7825C28.9918 85.8911 26.0674 91.3047 23.661 96.9535C14.1519 119.974 14.1519 145.828 23.661 168.849C26.066 174.522 28.9905 179.959 32.3972 185.093C38.5558 194.465 45.6016 203.222 53.4369 211.243C61.4879 219.278 70.3712 226.433 79.9366 232.586C85.0163 235.973 90.4031 238.875 96.0256 241.254C99.93 242.872 103.944 244.211 108.038 245.26C108.932 245.372 109.837 245.372 110.731 245.26C117.072 245.26 122.201 240.096 122.161 233.751V173.802C122.161 155.233 109.111 139.223 90.9294 135.487C89.084 135.207 87.2767 134.718 85.5422 134.03C84.0034 133.373 83.0221 131.842 83.067 130.169V115.091C99.6927 114.946 115.588 121.917 126.748 134.248C127.175 134.771 127.82 135.067 128.495 135.05C129.371 135.046 130.166 134.535 130.533 133.739C143.727 106.977 170.963 90.0329 200.786 90.0332V104.602C200.94 106.713 199.508 108.613 197.437 109.045C195.775 109.548 194.069 109.889 192.341 110.065C165.275 113.949 144.491 136.045 142.254 163.312C142.253 164.589 143.309 165.612 144.584 165.571C145.045 165.563 145.496 165.438 145.894 165.206C154.417 159.545 164.421 156.529 174.651 156.538V171.325C174.688 172.976 173.745 174.491 172.248 175.186C170.618 175.794 168.937 176.257 167.225 176.57C152.571 180.025 142.171 193.048 142.036 208.111V233.168C142.036 239.525 147.186 244.677 153.538 244.677Z" 
                    fill={isDark ? "white" : "#007AFF"}
                  />
                </svg>
              )}
            </div>
            {!sidebarCollapsed && (
              <div className={styles.logoText}>
                <span className={styles.logoTitle}>{currentTenant?.name || '多租户SaaS系统'}</span>
                <span className={styles.logoSubtitle}>Enterprise</span>
              </div>
            )}
          </div>
        </div>

        {/* 搜索框 */}
        {!sidebarCollapsed && (
          <div className={styles.searchBox}>
            <SearchOutlined />
            <input
              type="text"
              className={styles.searchInput}
              placeholder="搜索菜单..."
              value={menuSearchKeyword}
              onChange={(e) => setMenuSearchKeyword(e.target.value)}
            />
          </div>
        )}

        {/* 主菜单标题 */}
        {!sidebarCollapsed && (
          <div className={styles.menuGroupTitle}>主菜单</div>
        )}

        {/* 菜单 */}
        <Menu
          theme={isDark ? 'dark' : 'light'}
          mode="inline"
          selectedKeys={[location.pathname]}
          openKeys={openKeys}
          onOpenChange={(keys) => {
            // 只保留最后展开的菜单项，实现手风琴效果
            const latestOpenKey = keys.find(key => !openKeys.includes(key));
            if (latestOpenKey) {
              setOpenKeys([latestOpenKey]);
            } else {
              setOpenKeys(keys);
            }
          }}
          items={filteredMenuItems}
          onClick={({ key }) => {
            // 首页直接导航
            if (key === '/dashboard') {
              navigate(key);
              return;
            }
            // 其他菜单判断是否为叶子节点
            const isLeafMenu = (items: any[], targetKey: string): boolean => {
              for (const item of items) {
                if (item.path === targetKey && (!item.children || item.children.length === 0)) {
                  return true;
                }
                if (item.children) {
                  if (isLeafMenu(item.children, targetKey)) return true;
                }
              }
              return false;
            };
            if (isLeafMenu(menus, key)) {
              navigate(key);
            }
          }}
        />

        {/* 底部区域 */}
        <div className={`${styles.sidebarFooter} ${sidebarCollapsed ? styles.sidebarFooterCollapsed : ''}`}>
          {/* 收缩/展开按钮 */}
          <Tooltip title={sidebarCollapsed ? '展开侧边栏' : '收起侧边栏'} placement="right">
            <div
              className={`${styles.collapseToggle} ${sidebarCollapsed ? styles.collapseToggleCollapsed : ''}`}
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            >
              {sidebarCollapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              {!sidebarCollapsed && <span className={styles.collapseToggleText}>收起</span>}
            </div>
          </Tooltip>
        </div>
      </Sider>

      <Layout style={{ marginLeft: sidebarCollapsed ? 80 : 240, transition: 'margin-left 0.2s', overflow: 'hidden' }}>
        <Header className={styles.header}>
          {/* 左侧页面标题 */}
          <h1 className={styles.headerTitle}>{getPageTitle()}</h1>

          {/* 右侧操作区 */}
          <div className={styles.headerRight}>
            {/* 主题切换按钮 */}
            <div className={styles.themeSwitcher}>
              <button 
                className={`${styles.themeBtn} ${themeMode === 'system' ? styles.themeBtnActive : ''}`}
                onClick={() => setThemeMode('system')}
                title="跟随系统"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="2" y="3" width="20" height="14" rx="2" ry="2" />
                  <line x1="8" y1="21" x2="16" y2="21" />
                  <line x1="12" y1="17" x2="12" y2="21" />
                </svg>
              </button>
              <button 
                className={`${styles.themeBtn} ${themeMode === 'light' ? styles.themeBtnActive : ''}`}
                onClick={() => setThemeMode('light')}
                title="白天模式"
              >
                <SunOutlined />
              </button>
              <button 
                className={`${styles.themeBtn} ${themeMode === 'dark' ? styles.themeBtnActive : ''}`}
                onClick={() => setThemeMode('dark')}
                title="深色模式"
              >
                <MoonOutlined />
              </button>
            </div>
            
            {/* 用户信息 */}
            <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
              <div className={styles.headerUserInfo}>
                <div className={styles.headerUserAvatar}>
                  <span>{getUserInitial()}</span>
                </div>
                <span className={styles.headerUserName}>{user?.realName || user?.username}</span>
                <DownOutlined className={styles.headerDropdownIcon} />
              </div>
            </Dropdown>
            
            {/* 搜索按钮 - 暂时隐藏 */}
            {/* <div className={styles.headerIconBtn}>
              <SearchOutlined className={styles.headerIconInner} />
            </div> */}
            
            {/* 通知按钮 - 暂时隐藏 */}
            {/* <div className={styles.headerIconBtn}>
              <BellOutlined className={styles.headerIconInner} />
              <span className={styles.headerNotificationDot} />
            </div> */}
          </div>
        </Header>

        {/* TAB 栏 */}
        <div className={styles.tabBar}>
          <Tabs
            type="editable-card"
            activeKey={activeTabKey}
            onChange={handleTabChange}
            onEdit={(key, action) => {
              if (action === 'remove') {
                handleTabClose(key as string);
              }
            }}
            hideAdd
            tabBarStyle={{ marginBottom: 0, flex: 1, minWidth: 0 }}
            items={tabs.map((tab) => ({
              key: tab.key,
              label: renderTabLabel({ key: tab.key, label: tab.label, closable: tab.closable }),
              closable: tab.closable,
            }))}
          />
          
          {/* TAB 快捷操作 */}
          {tabs.length > 1 && (
            <div className={styles.tabActions}>
              <Dropdown
                menu={{
                  items: [
                    {
                      key: 'closeOther',
                      label: '关闭其他标签',
                      icon: <CloseCircleOutlined />,
                      onClick: () => handleCloseOtherTabs(activeTabKey),
                    },
                    {
                      key: 'closeRight',
                      label: '关闭右侧标签',
                      icon: <VerticalRightOutlined />,
                      onClick: () => handleCloseRightTabs(activeTabKey),
                    },
                    {
                      type: 'divider',
                    },
                    {
                      key: 'closeAll',
                      label: '关闭全部标签',
                      icon: <CloseOutlined />,
                      onClick: () => handleRemoveAllTabs(),
                      danger: true,
                    },
                  ],
                }}
                placement="bottomRight"
              >
                <Button type="text" size="small" icon={<MoreOutlined />} />
              </Dropdown>
            </div>
          )}
        </div>

        <Content className={styles.content}>
          <Suspense
            fallback={
              <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />
            }
          >
            <Outlet />
          </Suspense>
        </Content>
      </Layout>

      {/* 个人信息弹窗 */}
      <Modal
        title="个人信息"
        open={profileModalVisible}
        onCancel={() => setProfileModalVisible(false)}
        footer={null}
        width={500}
      >
        <Descriptions column={1} bordered size="middle" style={{ marginTop: 16 }}>
          <Descriptions.Item label={<><UserOutlined style={{ marginRight: 8 }} />用户名</>}>
            {user?.username || '-'}
          </Descriptions.Item>
          <Descriptions.Item label={<><UserOutlined style={{ marginRight: 8 }} />真实姓名</>}>
            {user?.realName || '-'}
          </Descriptions.Item>
          <Descriptions.Item label={<><PhoneOutlined style={{ marginRight: 8 }} />手机号</>}>
            {user?.phone || '-'}
          </Descriptions.Item>
          <Descriptions.Item label={<><MailOutlined style={{ marginRight: 8 }} />邮箱</>}>
            {user?.email || '-'}
          </Descriptions.Item>
          <Descriptions.Item label={<><SafetyOutlined style={{ marginRight: 8 }} />用户类型</>}>
            <Tag color={getTenantTypeColor(user?.tenantType)}>
              {getTenantTypeText(user?.tenantType)}
            </Tag>
          </Descriptions.Item>
          <Descriptions.Item label={<><TeamOutlined style={{ marginRight: 8 }} />角色组</>}>
            {user?.roles && user.roles.length > 0 ? (
              user.roles.map((role, index) => (
                <Tag key={index} color="blue" style={{ marginBottom: 4 }}>
                  {role}
                </Tag>
              ))
            ) : (
              <span style={{ color: '#999' }}>暂无角色</span>
            )}
          </Descriptions.Item>
        </Descriptions>
      </Modal>
    </Layout>
  );
};

export default BasicLayout;
