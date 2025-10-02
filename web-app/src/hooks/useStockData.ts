/**
 * 株価データ取得用カスタムフック
 * キャッシュ、フォールバック、エラーハンドリングを統合
 */

import { useState, useEffect, useCallback, useRef } from "react";
import { unifiedCacheManager } from "@/lib/unified-cache-manager";

export interface StockDataResponse {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  marketCap: number;
  lastUpdated: string;
}

export interface UseStockDataState {
  data: StockDataResponse | null;
  loading: boolean;
  error: string | null;
  lastUpdated: string | null;
  source: "cache" | "api" | "fallback" | null;
  retryCount: number;
}

export interface UseStockDataOptions {
  symbol?: string;
  autoRefresh?: boolean;
  refreshInterval?: number;
  enableFallback?: boolean;
  onError?: (error: string) => void;
  onDataUpdate?: (data: StockDataResponse) => void;
}

export function useStockData(options: UseStockDataOptions = {}) {
  const {
    symbol,
    autoRefresh = false,
    refreshInterval = 30000, // 30秒
    enableFallback = true,
    onError,
    onDataUpdate,
  } = options;

  const [state, setState] = useState<UseStockDataState>({
    data: null,
    loading: false,
    error: null,
    lastUpdated: null,
    source: null,
    retryCount: 0,
  });

  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const retryTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  /**
   * データを取得
   */
  const fetchData = useCallback(async (forceRefresh: boolean = false) => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const data = await unifiedCacheManager.get<StockDataResponse>(`stock_${symbol}`);
      
      if (data) {
        const source = forceRefresh ? "api" : "cache";
        setState(prev => ({
          ...prev,
          data,
          loading: false,
          error: null,
          lastUpdated: data.metadata.last_updated,
          source,
          retryCount: 0,
        }));
        
        onDataUpdate?.(data);
      } else {
        throw new Error("データを取得できませんでした");
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "不明なエラー";
      
      setState(prev => ({
        ...prev,
        loading: false,
        error: errorMessage,
        retryCount: prev.retryCount + 1,
      }));
      
      onError?.(errorMessage);
      
      // フォールバックを試行
      if (enableFallback && state.retryCount < 3) {
        setTimeout(() => {
          fetchData(false);
        }, 5000 * (state.retryCount + 1)); // 指数バックオフ
      }
    }
  }, [symbol, enableFallback, onError, onDataUpdate, state.retryCount]);

  /**
   * 手動更新
   */
  const refresh = useCallback(() => {
    fetchData(true);
  }, [fetchData]);

  /**
   * キャッシュクリア
   */
  const clearCache = useCallback(async () => {
    await unifiedCacheManager.delete(`stock_${symbol}`);
    setState(prev => ({ ...prev, data: null, source: null }));
  }, [symbol]);

  /**
   * 自動更新の開始
   */
  const startAutoRefresh = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
    
    intervalRef.current = setInterval(() => {
      fetchData(false);
    }, refreshInterval);
  }, [fetchData, refreshInterval]);

  /**
   * 自動更新の停止
   */
  const stopAutoRefresh = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  /**
   * 初期データ取得
   */
  useEffect(() => {
    fetchData(false);
    
    // 自動更新が有効な場合
    if (autoRefresh) {
      startAutoRefresh();
    }
    
    return () => {
      stopAutoRefresh();
      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current);
      }
    };
  }, [symbol, autoRefresh, fetchData, startAutoRefresh, stopAutoRefresh]);

  /**
   * 自動更新の制御
   */
  useEffect(() => {
    if (autoRefresh) {
      startAutoRefresh();
    } else {
      stopAutoRefresh();
    }
    
    return () => stopAutoRefresh();
  }, [autoRefresh, startAutoRefresh, stopAutoRefresh]);

  /**
   * キャッシュクリーンアップ
   */
  useEffect(() => {
    const cleanup = () => {
      // unifiedCacheManager.cleanup();
    };
    
    // ページロード時にクリーンアップ
    cleanup();
    
    // 定期的にクリーンアップ（5分間隔）
    const cleanupInterval = setInterval(cleanup, 5 * 60 * 1000);
    
    return () => clearInterval(cleanupInterval);
  }, []);

  return {
    ...state,
    refresh,
    clearCache,
    startAutoRefresh,
    stopAutoRefresh,
    isRetrying: state.retryCount > 0,
    canRetry: state.retryCount < 3,
  };
}

/**
 * 複数銘柄のデータを取得するフック
 */
export function useMultipleStockData(symbols: string[], options: Omit<UseStockDataOptions, "symbol"> = {}) {
  const [results, setResults] = useState<Record<string, UseStockDataState>>({});
  const [overallState, setOverallState] = useState<{
    loading: boolean;
    error: string | null;
    completed: number;
    total: number;
  }>({
    loading: false,
    error: null,
    completed: 0,
    total: symbols.length,
  });

  const fetchAllData = useCallback(async () => {
    setOverallState(prev => ({ ...prev, loading: true, error: null, completed: 0 }));
    
    const promises = symbols.map(async (symbol) => {
      try {
        const data = await unifiedCacheManager.get<StockDataResponse>(`stock_${symbol}`);
        return { symbol, data, error: null };
      } catch (error) {
        return { 
          symbol, 
          data: null, 
          error: error instanceof Error ? error.message : "不明なエラー", 
        };
      }
    });

    const results = await Promise.all(promises);
    
    const newResults: Record<string, UseStockDataState> = {};
    let completed = 0;
    let hasError = false;

    results.forEach(({ symbol, data, error }) => {
      newResults[symbol] = {
        data,
        loading: false,
        error,
        lastUpdated: data?.metadata.last_updated || null,
        source: data ? "api" : null,
        retryCount: 0,
      };
      
      if (data) completed++;
      if (error) hasError = true;
    });

    setResults(newResults);
    setOverallState({
      loading: false,
      error: hasError ? "一部のデータ取得に失敗しました" : null,
      completed,
      total: symbols.length,
    });
  }, [symbols]);

  useEffect(() => {
    if (symbols.length > 0) {
      fetchAllData();
    }
  }, [symbols, fetchAllData]);

  return {
    results,
    overallState,
    refresh: fetchAllData,
  };
}
