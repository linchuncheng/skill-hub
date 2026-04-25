import { create } from 'zustand';
import { persist, StorageValue } from 'zustand/middleware';

interface TenantInfo {
  id: number;
  name: string;
  code: string;
  status: number;
  logo?: string;  // 租户 Logo URL
  [key: string]: any;
}

interface TenantStore {
  // State
  currentTenant: TenantInfo | null;
  tenantList: TenantInfo[];

  // Actions
  setCurrentTenant: (tenant: TenantInfo | null) => void;
  setTenantList: (list: TenantInfo[]) => void;
  clearTenant: () => void;
}

export const useTenantStore = create<TenantStore>()(
  persist(
    (set) => ({
      currentTenant: null,
      tenantList: [],

      setCurrentTenant: (tenant) => set({ currentTenant: tenant }),
      setTenantList: (list) => set({ tenantList: list }),

      clearTenant: () => {
        set({
          currentTenant: null,
          tenantList: [],
        });
      },
    }),
    {
      name: 'tenant-store',
      storage: {
        getItem: (name: string): StorageValue<TenantStore> | null => {
          const value = localStorage.getItem(name);
          return value ? JSON.parse(value) : null;
        },
        setItem: (name: string, value: StorageValue<TenantStore>) => {
          localStorage.setItem(name, JSON.stringify(value));
        },
        removeItem: (name: string) => {
          localStorage.removeItem(name);
        },
      },
    }
  )
);

export type { TenantInfo };
