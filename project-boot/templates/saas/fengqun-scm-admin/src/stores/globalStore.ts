import { create } from 'zustand';
import { persist, StorageValue } from 'zustand/middleware';

// TAB 项接口
export interface TabItem {
  key: string;
  label: string;
  path: string;
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
  // 展开的菜单 keys
  openKeys: string[];
  setOpenKeys: (keys: string[]) => void;
}

export const useGlobalStore = create<GlobalStore>()(
  persist(
    (set, get) => ({
      sidebarCollapsed: false,
      setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),
      currentTheme: 'light',
      setCurrentTheme: (theme) => set({ currentTheme: theme }),
      // TAB 默认值
      tabs: [{ key: '/dashboard', label: '首页', path: '/dashboard', closable: false }],
      activeTabKey: '/dashboard',
      // 展开的菜单 keys（默认空）
      openKeys: [],
      setOpenKeys: (keys) => set({ openKeys: keys }),
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
        const newTabs = [homeTab, currentTab].filter(Boolean) as TabItem[];
        set({ tabs: newTabs, activeTabKey: key });
      },
      // 关闭右侧 TAB
      removeRightTabs: (key) => {
        const { tabs } = get();
        const currentIndex = tabs.findIndex((t) => t.key === key);
        if (currentIndex >= 0) {
          const newTabs = tabs.slice(0, currentIndex + 1);
          set({ tabs: newTabs });
        }
      },
      // 关闭所有 TAB（保留首页）
      removeAllTabs: () => {
        const { tabs } = get();
        const homeTab = tabs.find((t) => t.key === '/dashboard');
        if (homeTab) {
          set({ tabs: [homeTab], activeTabKey: homeTab.key });
        }
      },
    }),
    {
      name: 'global-store',
      storage: {
        getItem: (name: string): StorageValue<GlobalStore> | null => {
          const value = localStorage.getItem(name);
          return value ? JSON.parse(value) : null;
        },
        setItem: (name: string, value: StorageValue<GlobalStore>) => {
          localStorage.setItem(name, JSON.stringify(value));
        },
        removeItem: (name: string) => {
          localStorage.removeItem(name);
        },
      },
      // 只持久化 tabs、activeTabKey 和 sidebarCollapsed，不持久化 openKeys
      partialize: (state) => ({
        tabs: state.tabs,
        activeTabKey: state.activeTabKey,
        sidebarCollapsed: state.sidebarCollapsed,
      }),
    }
  )
);
