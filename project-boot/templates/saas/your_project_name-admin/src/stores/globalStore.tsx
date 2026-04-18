import { create } from 'zustand';
import type { ReactNode } from 'react';
import { HomeOutlined } from '@ant-design/icons';

// TAB 项接口
export interface TabItem {
  key: string;
  label: string;
  path: string;
  icon?: ReactNode;
  closable?: boolean;
}

interface GlobalStore {
  sidebarCollapsed: boolean;
  setSidebarCollapsed: (collapsed: boolean) => void;
  currentTheme: 'light' | 'dark';
  setCurrentTheme: (theme: 'light' | 'dark') => void;
  // TAB 相关状态
  tabs: TabItem[];
  activeTabKey: string;
  addTab: (tab: TabItem) => void;
  removeTab: (key: string) => void;
  setActiveTab: (key: string) => void;
  removeOtherTabs: (key: string) => void;
  removeRightTabs: (key: string) => void;
  removeAllTabs: () => void;
}

export const useGlobalStore = create<GlobalStore>((set, get) => ({
  sidebarCollapsed: false,
  setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),
  currentTheme: 'light',
  setCurrentTheme: (theme) => set({ currentTheme: theme }),
  // TAB 默认值
  tabs: [{ key: '/dashboard', label: '首页', path: '/dashboard', icon: <HomeOutlined />, closable: false }],
  activeTabKey: '/dashboard',
  // 添加 TAB
  addTab: (tab) => {
    const { tabs, activeTabKey } = get();
    const exists = tabs.find((t) => t.key === tab.key);
    if (!exists) {
      set({ tabs: [...tabs, tab], activeTabKey: tab.key });
    } else if (activeTabKey !== tab.key) {
      set({ activeTabKey: tab.key });
    }
  },
  // 移除 TAB
  removeTab: (key) => {
    const { tabs, activeTabKey } = get();
    const newTabs = tabs.filter((t) => t.key !== key);
    if (activeTabKey === key && newTabs.length > 0) {
      set({ tabs: newTabs, activeTabKey: newTabs[newTabs.length - 1].key });
    } else {
      set({ tabs: newTabs });
    }
  },
  // 设置当前激活 TAB
  setActiveTab: (key) => set({ activeTabKey: key }),
  // 关闭其他 TAB
  removeOtherTabs: (key) => {
    const { tabs } = get();
    const currentTab = tabs.find((t) => t.key === key);
    const homeTab = tabs.find((t) => t.key === '/dashboard');
    
    // 如果当前标签就是首页，则只保留首页，避免重复
    if (key === '/dashboard') {
      set({ tabs: homeTab ? [homeTab] : [], activeTabKey: '/dashboard' });
    } else {
      // 否则保留首页 + 当前标签
      const newTabs = [homeTab, currentTab].filter(Boolean) as TabItem[];
      set({ tabs: newTabs, activeTabKey: key });
    }
  },
  // 关闭右侧 TAB
  removeRightTabs: (key) => {
    const { tabs } = get();
    const currentIndex = tabs.findIndex((t) => t.key === key);
    if (currentIndex === -1) return;
    
    const newTabs = tabs.slice(0, currentIndex + 1);
    set({ tabs: newTabs });
  },
  // 关闭所有 TAB（保留首页）
  removeAllTabs: () => {
    const { tabs } = get();
    const homeTab = tabs.find((t) => t.key === '/dashboard');
    if (homeTab) {
      set({ tabs: [homeTab], activeTabKey: homeTab.key });
    }
  },
}));
