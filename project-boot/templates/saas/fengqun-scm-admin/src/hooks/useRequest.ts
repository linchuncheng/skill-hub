import { useCallback, useEffect, useRef, useState } from 'react';

interface UseRequestOptions<T, P extends any[]> {
  // 是否手动触发
  manual?: boolean;
  // 默认参数
  defaultParams?: P;
  // 成功回调
  onSuccess?: (data: T, params: P) => void;
  // 失败回调
  onError?: (error: Error, params: P) => void;
  // 请求完成回调
  onFinally?: () => void;
  // 防抖延迟（毫秒）
  debounceWait?: number;
  // 是否在依赖变化时重新请求
  refreshDeps?: any[];
}

interface UseRequestReturn<T, P extends any[]> {
  data: T | undefined;
  error: Error | undefined;
  loading: boolean;
  run: (...params: P) => Promise<T | undefined>;
  runAsync: (...params: P) => Promise<T>;
  refresh: () => Promise<T | undefined>;
  mutate: (data: T | undefined) => void;
}

/**
 * 请求 Hook
 */
export const useRequest = <T, P extends any[] = any[]>(
  service: (...params: P) => Promise<T>,
  options: UseRequestOptions<T, P> = {}
): UseRequestReturn<T, P> => {
  const {
    manual = false,
    defaultParams,
    onSuccess,
    onError,
    onFinally,
    debounceWait,
    refreshDeps = [],
  } = options;

  const [data, setData] = useState<T | undefined>(undefined);
  const [error, setError] = useState<Error | undefined>(undefined);
  const [loading, setLoading] = useState(!manual);

  const debounceTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const paramsRef = useRef<P>(defaultParams || ([] as unknown as P));

  const runAsync = useCallback(
    async (...params: P): Promise<T> => {
      paramsRef.current = params;
      setLoading(true);
      setError(undefined);

      try {
        const result = await service(...params);
        setData(result);
        onSuccess?.(result, params);
        return result;
      } catch (e) {
        const err = e instanceof Error ? e : new Error(String(e));
        setError(err);
        onError?.(err, params);
        throw err;
      } finally {
        setLoading(false);
        onFinally?.();
      }
    },
    [service, onSuccess, onError, onFinally]
  );

  const run = useCallback(
    async (...params: P): Promise<T | undefined> => {
      try {
        return await runAsync(...params);
      } catch {
        return undefined;
      }
    },
    [runAsync]
  );

  const refresh = useCallback(() => {
    return run(...paramsRef.current);
  }, [run]);

  const mutate = useCallback((newData: T | undefined) => {
    setData(newData);
  }, []);

  // 防抖执行
  const debouncedRun = useCallback(
    (...params: P) => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }

      return new Promise<T | undefined>((resolve) => {
        debounceTimerRef.current = setTimeout(() => {
          run(...params).then(resolve);
        }, debounceWait);
      });
    },
    [run, debounceWait]
  );

  // 自动执行
  useEffect(() => {
    if (!manual && defaultParams) {
      run(...defaultParams);
    } else if (!manual) {
      run(...([] as unknown as P));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [manual, ...refreshDeps]);

  // 清理防抖定时器
  useEffect(() => {
    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, []);

  return {
    data,
    error,
    loading,
    run: debounceWait ? debouncedRun : run,
    runAsync,
    refresh,
    mutate,
  };
};

export default useRequest;
