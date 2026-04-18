import { listTenants } from '@/api/platform/tenant';
import type { Tenant } from '@/api/types/tenant.schema';
import { Select, message } from 'antd';
import type { SelectProps } from 'antd';
import { FC, useEffect, useState, useMemo, useCallback } from 'react';

export interface TenantSelectProps extends Omit<SelectProps, 'options' | 'loading' | 'showSearch' | 'filterOption'> {
  /** 是否显示"全部租户"选项，默认 false */
  showAll?: boolean;
  /** "全部租户"选项的标签文本，默认"全部租户" */
  allLabel?: string;
  /** "全部租户"选项的值，默认 undefined */
  allValue?: string | undefined;
  /** 租户变更回调，返回完整的租户对象 */
  onTenantChange?: (tenant: Tenant | null) => void;
}

/**
 * 租户选择器公共组件
 * - 支持搜索筛选（按租户名称、编码搜索）
 * - 支持"全部租户"选项
 * - 可作为 Form.Item 控件使用
 */
const TenantSelect: FC<TenantSelectProps> = ({
  showAll = false,
  allLabel = '全部租户',
  allValue = undefined,
  placeholder = '请选择租户',
  onTenantChange,
  onChange,
  value,
  ...restProps
}) => {
  const [tenantList, setTenantList] = useState<Tenant[]>([]);
  const [loading, setLoading] = useState(false);

  // 加载租户列表
  const loadTenants = useCallback(async () => {
    setLoading(true);
    try {
      const data = await listTenants();
      setTenantList(data);
    } catch (error: any) {
      message.error(error.message || '加载租户列表失败');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadTenants();
  }, [loadTenants]);

  // 构建选项列表
  const options = useMemo(() => {
    const tenantOptions = tenantList.map((tenant) => ({
      label: tenant.tenantName,
      value: String(tenant.id),
      tenant, // 保存完整租户对象用于回调
    }));

    if (showAll) {
      return [
        { label: allLabel, value: allValue, tenant: null },
        ...tenantOptions,
      ];
    }

    return tenantOptions;
  }, [tenantList, showAll, allLabel, allValue]);

  // 搜索过滤函数：支持按租户名称和编码搜索
  const filterOption = useCallback(
    (input: string, option?: { label?: string; value?: string | undefined; tenant?: Tenant | null }) => {
      if (!option) return false;
      const searchText = input.toLowerCase();
      const tenant = option.tenant;
      
      // "全部租户"选项始终显示
      if (!tenant) return true;
      
      // 按租户名称或编码匹配
      return (
        tenant.tenantName.toLowerCase().includes(searchText) ||
        tenant.tenantCode.toLowerCase().includes(searchText)
      );
    },
    []
  );

  // 处理变更
  const handleChange = useCallback(
    (newValue: string | undefined, option: any) => {
      // 触发原始 onChange（兼容 Form.Item）
      onChange?.(newValue, option);
      
      // 触发 onTenantChange 回调
      if (onTenantChange) {
        const selectedTenant = option?.tenant || null;
        onTenantChange(selectedTenant);
      }
    },
    [onChange, onTenantChange]
  );

  return (
    <Select
      {...restProps}
      value={value}
      placeholder={placeholder}
      loading={loading}
      showSearch
      allowClear
      filterOption={filterOption}
      options={options}
      onChange={handleChange}
      optionFilterProp="label"
    />
  );
};

export default TenantSelect;
