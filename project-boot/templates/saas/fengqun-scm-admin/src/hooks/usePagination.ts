import { useCallback, useMemo, useState } from 'react';

interface PaginationState {
  current: number;
  pageSize: number;
  total: number;
}

interface UsePaginationOptions {
  defaultCurrent?: number;
  defaultPageSize?: number;
  onChange?: (current: number, pageSize: number) => void;
}

interface UsePaginationReturn extends PaginationState {
  onChange: (current: number, pageSize: number) => void;
  setTotal: (total: number) => void;
  reset: () => void;
  pagination: {
    current: number;
    pageSize: number;
    total: number;
    showSizeChanger: boolean;
    showQuickJumper: boolean;
    showTotal: (total: number) => string;
    onChange: (current: number, pageSize: number) => void;
  };
}

/**
 * 分页 Hook
 */
export const usePagination = (options: UsePaginationOptions = {}): UsePaginationReturn => {
  const { defaultCurrent = 1, defaultPageSize = 10, onChange: onPaginationChange } = options;

  const [current, setCurrent] = useState(defaultCurrent);
  const [pageSize, setPageSize] = useState(defaultPageSize);
  const [total, setTotal] = useState(0);

  const onChange = useCallback(
    (page: number, size: number) => {
      setCurrent(page);
      setPageSize(size);
      onPaginationChange?.(page, size);
    },
    [onPaginationChange]
  );

  const reset = useCallback(() => {
    setCurrent(defaultCurrent);
    setPageSize(defaultPageSize);
  }, [defaultCurrent, defaultPageSize]);

  const pagination = useMemo(
    () => ({
      current,
      pageSize,
      total,
      showSizeChanger: true,
      showQuickJumper: true,
      showTotal: (t: number) => `共 ${t} 条`,
      onChange,
    }),
    [current, pageSize, total, onChange]
  );

  return {
    current,
    pageSize,
    total,
    onChange,
    setTotal,
    reset,
    pagination,
  };
};

export default usePagination;
