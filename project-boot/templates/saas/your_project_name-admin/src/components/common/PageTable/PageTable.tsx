/**
 * PageTable - 统一的表格页面组件
 * 
 * 封装了：
 * - 全屏布局（表格撑满、表头固定、内容滚动、分页固定底部）
 * - 统一的分页配置
 * - 统一的滚动配置
 * 
 * 使用示例：
 * ```tsx
 * <PageTable
 *   filterBar={<FilterBar>...</FilterBar>}
 *   columns={columns}
 *   dataSource={data}
 *   loading={loading}
 *   rowKey="id"
 * />
 * ```
 */
import type { TableProps } from 'antd';
import { Table } from 'antd';
import type { ReactNode } from 'react';
import { useMemo } from 'react';
import styles from './PageTable.module.scss';

export interface PageTableProps<T> extends Omit<TableProps<T>, 'pagination' | 'scroll'> {
  /** 筛选区域内容 */
  filterBar?: ReactNode;
  /** 分页配置，传 false 禁用分页 */
  pagination?: TableProps<T>['pagination'] | false;
  /** 滚动配置，默认自适应 */
  scroll?: TableProps<T>['scroll'];
}

/**
 * 默认分页配置
 */
const DEFAULT_PAGINATION = {
  pageSize: 10,
  showSizeChanger: true,
  showTotal: (total: number) => `共 ${total} 条`,
};

/**
 * 默认滚动配置
 */
const DEFAULT_SCROLL = {
  x: true as const,
  y: 'calc(100vh - 320px)',
};

function PageTable<T extends object>({
  filterBar,
  pagination = DEFAULT_PAGINATION,
  scroll = DEFAULT_SCROLL,
  dataSource: dataSourceProp,
  ...tableProps
}: PageTableProps<T>) {
  // 获取 dataSource（优先使用 props 中的，其次使用 tableProps 中的）
  const dataSource = (dataSourceProp || (tableProps as any).dataSource) as T[] | undefined;
  
  // 移除 dataSource 从 tableProps 避免重复传递
  const { dataSource: _, ...restTableProps } = tableProps as any;

  // 合并分页配置
  const mergedPagination = useMemo(() => {
    if (pagination === false) return false;
    return { ...DEFAULT_PAGINATION, ...pagination };
  }, [pagination]);

  // 合并滚动配置 - 数据为空时禁用横向滚动
  const mergedScroll = useMemo(() => {
    const baseScroll = { ...DEFAULT_SCROLL, ...scroll };
    // 数据为空时，设置 x 为 'max-content' 避免显示空白滚动条
    const isEmpty = !dataSource || (Array.isArray(dataSource) && dataSource.length === 0);
    if (isEmpty) {
      return { ...baseScroll, x: 'max-content' as const };
    }
    return baseScroll;
  }, [scroll, dataSource]);

  return (
    <div className={styles.container}>
      {filterBar && <div className={styles.filterBar}>{filterBar}</div>}
      <div className={styles.tableWrapper}>
        <Table<T>
          {...restTableProps}
          dataSource={dataSource}
          pagination={mergedPagination}
          scroll={mergedScroll}
        />
      </div>
    </div>
  );
}

export default PageTable;
