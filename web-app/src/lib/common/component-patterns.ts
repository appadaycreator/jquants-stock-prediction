/**
 * 共通のコンポーネントパターン
 * 再利用可能なコンポーネントロジックを提供
 */

import React, { useState, useEffect, useCallback, useMemo } from "react";

// データ取得パターン
export interface DataFetchState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  lastUpdated: string | null;
}

export interface DataFetchConfig {
  autoFetch: boolean;
  retryOnError: boolean;
  maxRetries: number;
  retryDelay: number;
  cacheTimeout: number;
}

export function useDataFetch<T>(
  fetchFn: () => Promise<T>,
  config: Partial<DataFetchConfig> = {},
) {
  const defaultConfig: DataFetchConfig = {
    autoFetch: true,
    retryOnError: true,
    maxRetries: 3,
    retryDelay: 1000,
    cacheTimeout: 300000, // 5分
  };

  const finalConfig = { ...defaultConfig, ...config };
  const [state, setState] = useState<DataFetchState<T>>({
    data: null,
    loading: false,
    error: null,
    lastUpdated: null,
  });

  const [retryCount, setRetryCount] = useState(0);

  const fetch = useCallback(async (isRetry = false) => {
    if (isRetry) {
      setRetryCount(prev => prev + 1);
    }

    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const data = await fetchFn();
      setState({
        data,
        loading: false,
        error: null,
        lastUpdated: new Date().toISOString(),
      });
      setRetryCount(0);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Unknown error";
      
      if (finalConfig.retryOnError && retryCount < finalConfig.maxRetries) {
        setTimeout(() => {
          fetch(true);
        }, finalConfig.retryDelay);
      } else {
        setState(prev => ({
          ...prev,
          loading: false,
          error: errorMessage,
        }));
      }
    }
  }, [fetchFn, finalConfig, retryCount]);

  useEffect(() => {
    if (finalConfig.autoFetch) {
      fetch();
    }
  }, [fetch, finalConfig.autoFetch]);

  return {
    ...state,
    fetch,
    retry: () => fetch(true),
    clearError: () => setState(prev => ({ ...prev, error: null })),
  };
}

// フォーム管理パターン
export interface FormState<T> {
  values: T;
  errors: Partial<Record<keyof T, string>>;
  touched: Partial<Record<keyof T, boolean>>;
  isSubmitting: boolean;
  isValid: boolean;
}

export interface FormConfig<T> {
  initialValues: T;
  validate?: (values: T) => Partial<Record<keyof T, string>>;
  onSubmit: (values: T) => Promise<void> | void;
}

export function useForm<T extends Record<string, any>>(config: FormConfig<T>) {
  const [state, setState] = useState<FormState<T>>({
    values: config.initialValues,
    errors: {},
    touched: {},
    isSubmitting: false,
    isValid: true,
  });

  const setValue = useCallback((field: keyof T, value: any) => {
    setState(prev => {
      const newValues = { ...prev.values, [field]: value };
      const errors = config.validate ? config.validate(newValues) : {};
      const isValid = Object.keys(errors).length === 0;
      
      return {
        ...prev,
        values: newValues,
        errors,
        isValid,
      };
    });
  }, [config]);

  const setTouched = useCallback((field: keyof T, touched = true) => {
    setState(prev => ({
      ...prev,
      touched: { ...prev.touched, [field]: touched },
    }));
  }, []);

  const setError = useCallback((field: keyof T, error: string) => {
    setState(prev => ({
      ...prev,
      errors: { ...prev.errors, [field]: error },
      isValid: false,
    }));
  }, []);

  const handleSubmit = useCallback(async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    
    setState(prev => ({ ...prev, isSubmitting: true }));
    
    try {
      await config.onSubmit(state.values);
    } catch (error) {
      console.error("Form submission error:", error);
    } finally {
      setState(prev => ({ ...prev, isSubmitting: false }));
    }
  }, [config, state.values]);

  const reset = useCallback(() => {
    setState({
      values: config.initialValues,
      errors: {},
      touched: {},
      isSubmitting: false,
      isValid: true,
    });
  }, [config.initialValues]);

  return {
    ...state,
    setValue,
    setTouched,
    setError,
    handleSubmit,
    reset,
  };
}

// モーダル管理パターン
export interface ModalState {
  isOpen: boolean;
  data: any;
}

export function useModal<T = any>() {
  const [state, setState] = useState<ModalState>({
    isOpen: false,
    data: null,
  });

  const open = useCallback((data?: T) => {
    setState({ isOpen: true, data: data || null });
  }, []);

  const close = useCallback(() => {
    setState({ isOpen: false, data: null });
  }, []);

  const toggle = useCallback(() => {
    setState(prev => ({ ...prev, isOpen: !prev.isOpen }));
  }, []);

  return {
    ...state,
    open,
    close,
    toggle,
  };
}

// ページネーションパターン
export interface PaginationState {
  currentPage: number;
  totalPages: number;
  pageSize: number;
  totalItems: number;
}

export interface PaginationConfig {
  initialPage: number;
  pageSize: number;
  totalItems: number;
}

export function usePagination(config: PaginationConfig) {
  const [state, setState] = useState<PaginationState>({
    currentPage: config.initialPage,
    totalPages: Math.ceil(config.totalItems / config.pageSize),
    pageSize: config.pageSize,
    totalItems: config.totalItems,
  });

  const setPage = useCallback((page: number) => {
    setState(prev => ({
      ...prev,
      currentPage: Math.max(1, Math.min(page, prev.totalPages)),
    }));
  }, []);

  const nextPage = useCallback(() => {
    setState(prev => ({
      ...prev,
      currentPage: Math.min(prev.currentPage + 1, prev.totalPages),
    }));
  }, []);

  const prevPage = useCallback(() => {
    setState(prev => ({
      ...prev,
      currentPage: Math.max(prev.currentPage - 1, 1),
    }));
  }, []);

  const setPageSize = useCallback((size: number) => {
    setState(prev => ({
      ...prev,
      pageSize: size,
      totalPages: Math.ceil(prev.totalItems / size),
      currentPage: 1,
    }));
  }, []);

  const setTotalItems = useCallback((total: number) => {
    setState(prev => ({
      ...prev,
      totalItems: total,
      totalPages: Math.ceil(total / prev.pageSize),
      currentPage: Math.min(prev.currentPage, Math.ceil(total / prev.pageSize)),
    }));
  }, []);

  const paginatedData = useCallback(<T>(data: T[]): T[] => {
    const start = (state.currentPage - 1) * state.pageSize;
    const end = start + state.pageSize;
    return data.slice(start, end);
  }, [state.currentPage, state.pageSize]);

  return {
    ...state,
    setPage,
    nextPage,
    prevPage,
    setPageSize,
    setTotalItems,
    paginatedData,
  };
}

// 検索パターン
export interface SearchState {
  query: string;
  results: any[];
  isSearching: boolean;
  hasSearched: boolean;
}

export interface SearchConfig<T> {
  searchFn: (query: string) => Promise<T[]>;
  debounceMs: number;
  minQueryLength: number;
}

export function useSearch<T>(config: SearchConfig<T>) {
  const [state, setState] = useState<SearchState>({
    query: "",
    results: [],
    isSearching: false,
    hasSearched: false,
  });

  const [debounceTimer, setDebounceTimer] = useState<NodeJS.Timeout | null>(null);

  const search = useCallback(async (query: string) => {
    if (query.length < config.minQueryLength) {
      setState(prev => ({ ...prev, query, results: [], hasSearched: false }));
      return;
    }

    setState(prev => ({ ...prev, query, isSearching: true }));

    try {
      const results = await config.searchFn(query);
      setState(prev => ({
        ...prev,
        results,
        isSearching: false,
        hasSearched: true,
      }));
    } catch (error) {
      console.error("Search error:", error);
      setState(prev => ({
        ...prev,
        isSearching: false,
        hasSearched: true,
      }));
    }
  }, [config]);

  const handleQueryChange = useCallback((query: string) => {
    if (debounceTimer) {
      clearTimeout(debounceTimer);
    }

    const timer = setTimeout(() => {
      search(query);
    }, config.debounceMs);

    setDebounceTimer(timer);
  }, [search, config.debounceMs, debounceTimer]);

  const clearSearch = useCallback(() => {
    setState({
      query: "",
      results: [],
      isSearching: false,
      hasSearched: false,
    });
  }, []);

  useEffect(() => {
    return () => {
      if (debounceTimer) {
        clearTimeout(debounceTimer);
      }
    };
  }, [debounceTimer]);

  return {
    ...state,
    search,
    handleQueryChange,
    clearSearch,
  };
}

// キャッシュパターン
export interface CacheState<T> {
  data: T | null;
  isLoading: boolean;
  error: string | null;
  lastFetched: string | null;
  isStale: boolean;
}

export interface CacheConfig {
  ttl: number; // Time to live in milliseconds
  staleWhileRevalidate: boolean;
}

export function useCache<T>(
  key: string,
  fetchFn: () => Promise<T>,
  config: Partial<CacheConfig> = {},
) {
  const defaultConfig: CacheConfig = {
    ttl: 300000, // 5分
    staleWhileRevalidate: true,
  };

  const finalConfig = { ...defaultConfig, ...config };
  const [state, setState] = useState<CacheState<T>>({
    data: null,
    isLoading: false,
    error: null,
    lastFetched: null,
    isStale: false,
  });

  const isStale = useCallback(() => {
    if (!state.lastFetched) return true;
    return Date.now() - new Date(state.lastFetched).getTime() > finalConfig.ttl;
  }, [state.lastFetched, finalConfig.ttl]);

  const fetch = useCallback(async (force = false) => {
    if (!force && state.data && !isStale()) {
      return state.data;
    }

    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const data = await fetchFn();
      setState({
        data,
        isLoading: false,
        error: null,
        lastFetched: new Date().toISOString(),
        isStale: false,
      });
      return data;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Unknown error";
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
      }));
      throw error;
    }
  }, [fetchFn, state.data, isStale]);

  const invalidate = useCallback(() => {
    setState(prev => ({ ...prev, isStale: true }));
  }, []);

  const clear = useCallback(() => {
    setState({
      data: null,
      isLoading: false,
      error: null,
      lastFetched: null,
      isStale: false,
    });
  }, []);

  useEffect(() => {
    if (isStale() && finalConfig.staleWhileRevalidate) {
      fetch();
    }
  }, [isStale, fetch, finalConfig.staleWhileRevalidate]);

  return {
    ...state,
    fetch,
    invalidate,
    clear,
    isStale: isStale(),
  };
}
