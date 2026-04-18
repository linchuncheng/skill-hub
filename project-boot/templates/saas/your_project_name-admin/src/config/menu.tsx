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
    key: 'your_project_name',
    label: 'YOUR_PROJECT_NAME 管理',
    icon: <AppstoreOutlined />,
    children: [
      {
        key: 'your_project_name-overview',
        label: '概览',
        path: '/your_project_name/overview',
        permission: 'your_project_name:overview:view',
      },
      {
        key: 'your_project_name-product',
        label: '商品管理',
        icon: <InboxOutlined />,
        path: '/your_project_name/product',
        permission: 'your_project_name:product:list',
      },
      {
        key: 'your_project_name-brand',
        label: '品牌管理',
        icon: <TagOutlined />,
        path: '/your_project_name/brand',
        permission: 'your_project_name:brand:list',
      },
      {
        key: 'your_project_name-category',
        label: '分类管理',
        icon: <AppstoreOutlined />,
        path: '/your_project_name/category',
        permission: 'your_project_name:category:list',
      },
      {
        key: 'your_project_name-supplier',
        label: '供应商管理',
        icon: <UsergroupAddOutlined />,
        path: '/your_project_name/supplier',
        permission: 'your_project_name:supplier:list',
      },
      {
        key: 'your_project_name-order',
        label: '订单管理',
        icon: <FileTextOutlined />,
        path: '/your_project_name/order',
        permission: 'your_project_name:order:list',
      },
      {
        key: 'your_project_name-purchase',
        label: '采购管理',
        icon: <ShoppingCartOutlined />,
        path: '/your_project_name/purchase',
        permission: 'your_project_name:purchase:list',
      },
    ],
  },
  
      
      
      
      
      
      
    ],
  },
];

export default menuConfig;
