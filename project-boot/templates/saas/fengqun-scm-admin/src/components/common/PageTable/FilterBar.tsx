/**
 * FilterBar - 筛选栏组件
 * 
 * 用于表格页面的筛选区域，支持快捷操作按钮
 * 
 * 使用示例：
 * ```tsx
 * <FilterBar>
 *   <Input placeholder="搜索" />
 *   <Button type="primary">搜索</Button>
 *   <Button onClick={handleReset}>重置</Button>
 *   <FilterBar.Action>
 *     <Button type="primary">新增</Button>
 *   </FilterBar.Action>
 * </FilterBar>
 * ```
 */
import type { ReactNode } from 'react';
import { FC, PropsWithChildren } from 'react';
import styles from './FilterBar.module.scss';

export interface FilterBarProps {
  children: ReactNode;
  className?: string;
}

/**
 * 筛选栏组件
 */
const FilterBar: FC<FilterBarProps> & {
  Action: FC<PropsWithChildren<{ className?: string }>>;
} = ({ children, className }) => {
  return <div className={`${styles.filterBar} ${className || ''}`}>{children}</div>;
};

/**
 * 操作区域 - 自动靠右
 */
FilterBar.Action = ({ children, className }) => {
  return <div className={`${styles.action} ${className || ''}`}>{children}</div>;
};

export default FilterBar;
