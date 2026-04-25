import type { UserInfo } from '@/api/types/common.schema';
import { create } from 'zustand';
import { persist, StorageValue } from 'zustand/middleware';

interface AuthStore {
  // State
  user: UserInfo | null;
  accessToken: string | null;
  refreshToken: string | null;
  permissions: string[];
  menus: any[];

  // Actions
  setUser: (user: UserInfo) => void;
  setAccessToken: (token: string) => void;
  setRefreshToken: (token: string) => void;
  setPermissions: (permissions: string[]) => void;
  setMenus: (menus: any[]) => void;
  setAuthData: (data: {
    user: UserInfo;
    accessToken: string;
    refreshToken: string;
    permissions: string[];
    menus: any[];
  }) => void;
  hasPermission: (permission: string) => boolean;
  logout: () => void;
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      permissions: [],
      menus: [],

      setUser: (user) => set({ user }),
      setAccessToken: (token) => set({ accessToken: token }),
      setRefreshToken: (token) => set({ refreshToken: token }),
      setPermissions: (permissions) => set({ permissions }),
      setMenus: (menus) => set({ menus }),

      setAuthData: (data) =>
        set({
          user: data.user,
          accessToken: data.accessToken,
          refreshToken: data.refreshToken,
          permissions: data.permissions,
          menus: data.menus,
        }),

      hasPermission: (permission: string) => {
        return get().permissions.includes(permission);
      },

      logout: () => {
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          permissions: [],
          menus: [],
        });
        localStorage.removeItem('auth-store');
      },
    }),
    {
      name: 'auth-store',
      storage: {
        getItem: (name: string): StorageValue<AuthStore> | null => {
          const value = localStorage.getItem(name);
          return value ? JSON.parse(value) : null;
        },
        setItem: (name: string, value: StorageValue<AuthStore>) => {
          localStorage.setItem(name, JSON.stringify(value));
        },
        removeItem: (name: string) => {
          localStorage.removeItem(name);
        },
      },
    }
  )
);
