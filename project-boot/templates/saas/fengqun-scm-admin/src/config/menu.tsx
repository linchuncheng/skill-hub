import {
    AppstoreOutlined,
    EnvironmentOutlined,
    FileTextOutlined,
    HomeOutlined,
    InboxOutlined,
    LoginOutlined,
    LogoutOutlined,
    MenuOutlined,
    SafetyOutlined,
    SettingOutlined,
    ShoppingCartOutlined,
    ShopOutlined,
    TagOutlined,
    TeamOutlined,
    UserOutlined,
    UsergroupAddOutlined,
} from '@ant-design/icons';

export interface MenuItem {
  key: string;
  label: string;
  icon?: React.ReactNode;
  path?: string;
  permission?: string;
  children?: MenuItem[];
}

export const menuConfig: MenuItem[] = [
  {
    key: 'dashboard',
    label: '工作台',
    icon: <HomeOutlined />,
    path: '/dashboard',
    permission: 'platform:dashboard:view',
  },
  {
    key: 'system',
    label: '系统管理',
    icon: <SettingOutlined />,
    children: [
      {
        key: 'tenant',
        label: '租户管理',
        icon: <ShopOutlined />,
        path: '/system/tenant',
        permission: 'platform:tenant:list',
      },
      {
        key: 'user',
        label: '用户管理',
        icon: <UserOutlined />,
        path: '/system/user',
        permission: 'platform:user:list',
      },
      {
        key: 'role',
        label: '角色管理',
        icon: <SafetyOutlined />,
        path: '/system/role',
        permission: 'platform:role:list',
      },
      {
        key: 'menu',
        label: '菜单管理',
        icon: <MenuOutlined />,
        path: '/system/menu',
        permission: 'platform:menu:list',
      },
    ],
  },
  {
    key: 'scm',
    label: 'SCM 管理',
    icon: <AppstoreOutlined />,
    children: [
      {
        key: 'scm-overview',
        label: '概览',
        path: '/scm/overview',
        permission: 'scm:overview:view',
      },
      {
        key: 'scm-product',
        label: '商品管理',
        icon: <InboxOutlined />,
        path: '/scm/product',
        permission: 'scm:product:list',
      },
      {
        key: 'scm-brand',
        label: '品牌管理',
        icon: <TagOutlined />,
        path: '/scm/brand',
        permission: 'scm:brand:list',
      },
      {
        key: 'scm-category',
        label: '分类管理',
        icon: <AppstoreOutlined />,
        path: '/scm/category',
        permission: 'scm:category:list',
      },
      {
        key: 'scm-supplier',
        label: '供应商管理',
        icon: <UsergroupAddOutlined />,
        path: '/scm/supplier',
        permission: 'scm:supplier:list',
      },
      {
        key: 'scm-order',
        label: '订单管理',
        icon: <FileTextOutlined />,
        path: '/scm/order',
        permission: 'scm:order:list',
      },
      {
        key: 'scm-purchase',
        label: '采购管理',
        icon: <ShoppingCartOutlined />,
        path: '/scm/purchase',
        permission: 'scm:purchase:list',
      },
    ],
  },
  
      
      
      
      
      
      
    ],
  },
];

export default menuConfig;
