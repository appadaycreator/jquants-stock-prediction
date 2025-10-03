'use client';

import { useState, useEffect, useCallback, useRef } from 'react';

interface ApiOptions {
  retries?: number;
  retryDelay?: number;
  timeout?: number;
  exponentialBackoff?: boolean;
  onError?: (error: Error) => void;
  onSuccess?: (data: any) => void;
}

interface ApiState<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  retryCount: number;
  lastSuccessTime: number | null;
  lastErrorTime: number | null;
}

interface ApiActions {
  retry: () => void;
  reset: () => void;
  setData: (data: any) => void;
}

export function useApi<T = any>(
  apiCall: () => Promise<T>,
  options: ApiOptions = {}
): [ApiState<T>, ApiActions] {
  const {
    retries = 3,
    retryDelay = 1000,
    timeout = 30000,
    exponentialBackoff = true,
    onError,
    onSuccess
  } = options;

  const [state, setState] = useState<ApiState<T>>({
    data: null,
    loading: false,
    error: null,
    retryCount: 0,
    lastSuccessTime: null,
    lastErrorTime: null
  });

  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const retryTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const isMountedRef = useRef(true);

  useEffect(() => {
    return () => {
      isMountedRef.current = false;
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      if (retryTimeoutRef.current) clearTimeout(retryTimeoutRef.current);
    };
  }, []);

  const executeApiCall = useCallback(async (attempt: number = 0): Promise<void> => {
    if (!isMountedRef.current) return;

    setState(prev => ({
      ...prev,
      loading: true,
      error: null
    }));

    try {
      // タイムアウト設定
      const timeoutPromise = new Promise<never>((_, reject) => {
        timeoutRef.current = setTimeout(() => {
          reject(new Error(`Request timeout after ${timeout}ms`));
        }, timeout);
      });

      // API呼び出し実行
      const apiPromise = apiCall();
      const result = await Promise.race([apiPromise, timeoutPromise]);

      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }

      if (!isMountedRef.current) return;

      setState(prev => ({
        ...prev,
        data: result,
        loading: false,
        error: null,
        retryCount: attempt,
        lastSuccessTime: Date.now(),
        lastErrorTime: null
      }));

      if (onSuccess) {
        onSuccess(result);
      }

    } catch (error) {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }

      if (!isMountedRef.current) return;

      const errorObj = error instanceof Error ? error : new Error(String(error));
      
      setState(prev => ({
        ...prev,
        loading: false,
        error: errorObj,
        retryCount: attempt,
        lastErrorTime: Date.now()
      }));

      if (onError) {
        onError(errorObj);
      }

      // 自動再試行
      if (attempt < retries) {
        const delay = exponentialBackoff 
          ? retryDelay * Math.pow(2, attempt)
          : retryDelay;

        retryTimeoutRef.current = setTimeout(() => {
          if (isMountedRef.current) {
            executeApiCall(attempt + 1);
          }
        }, delay);
      }
    }
  }, [apiCall, retries, retryDelay, timeout, exponentialBackoff, onError, onSuccess]);

  const retry = useCallback(() => {
    if (retryTimeoutRef.current) {
      clearTimeout(retryTimeoutRef.current);
      retryTimeoutRef.current = null;
    }
    executeApiCall(0);
  }, [executeApiCall]);

  const reset = useCallback(() => {
    if (retryTimeoutRef.current) {
      clearTimeout(retryTimeoutRef.current);
      retryTimeoutRef.current = null;
    }
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
    
    setState({
      data: null,
      loading: false,
      error: null,
      retryCount: 0,
      lastSuccessTime: null,
      lastErrorTime: null
    });
  }, []);

  const setData = useCallback((data: T) => {
    setState(prev => ({
      ...prev,
      data,
      error: null,
      lastSuccessTime: Date.now()
    }));
  }, []);

  return [state, { retry, reset, setData }];
}

// 特殊化されたAPIフック
export function useStockData() {
  return useApi(
    async () => {
      const response = await fetch('/api/routine/candidates');
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      return response.json();
    },
    {
      retries: 3,
      retryDelay: 2000,
      timeout: 15000,
      exponentialBackoff: true
    }
  );
}

export function useAuthStatus() {
  return useApi(
    async () => {
      const response = await fetch('/api/auth/status');
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      return response.json();
    },
    {
      retries: 2,
      retryDelay: 1000,
      timeout: 10000,
      exponentialBackoff: false
    }
  );
}

export function useRoutineUpdate() {
  return useApi(
    async () => {
      const response = await fetch('/api/routine/update', {
        method: 'POST'
      });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      return response.json();
    },
    {
      retries: 2,
      retryDelay: 3000,
      timeout: 30000,
      exponentialBackoff: true
    }
  );
}
