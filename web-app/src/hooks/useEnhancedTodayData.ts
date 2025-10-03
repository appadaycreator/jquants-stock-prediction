/**
 * 強化された今日の指示データ取得フック
 * 新しいAPIクライアントとエラーハンドリングを使用
 */

"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { unifiedApiClient } from "@/lib/unified-api-client";
import { unifiedCacheManager } from "@/lib/unified-cache-manager";
import { optimizedErrorHandler, ErrorContext } from "@/lib/error-handler";

interface TodaySummary {
  date: string;
  marketStatus: "open" | "closed" | "pre_market" | "after_hours";
  topSignals: Array<{
    symbol: string;
    action: "buy" | "sell" | "hold";
    confidence: number;
    price: number;
    change: number;
    reason: string;
  }>;
  marketInsights: {
    trend: "bullish" | "bearish" | "neutral";
    volatility: "low" | "medium" | "high";
    sentiment: number;
  };
  riskAssessment: {
    level: "low" | "medium" | "high";
    factors: string[];
    recommendations: string[];
  };
  lastUpdated: string;
}

interface UseEnhancedTodayDataReturn {
  data: TodaySummary | null;
  loading: boolean;
  error: string | null;
  fromCache: boolean;
  retry: () => void;
  refresh: () => void;
  lastUpdated: string | null;
}

export function useEnhancedTodayData(): UseEnhancedTodayDataReturn {
  const [data, setData] = useState<TodaySummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fromCache, setFromCache] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);
  
  // 無限ループを防ぐためのref
  const isFetching = useRef(false);
  const retryCount = useRef(0);
  const maxRetries = 3;

  const fetchTodayData = useCallback(async (useCache: boolean = true) => {
    // 既に取得中の場合は重複実行を防ぐ
    if (isFetching.current) {
      return;
    }

    isFetching.current = true;
    setLoading(true);
    setError(null);

    try {
      // キャッシュから取得を試行
      if (useCache) {
        const cachedData = await unifiedCacheManager.get<TodaySummary>("today_summary");
        if (cachedData) {
          setData(cachedData);
          setFromCache(true);
          setLastUpdated(cachedData.lastUpdated);
          return;
        }
      }

      // モックデータを返す（開発環境用）
      const mockData: TodaySummary = {
        date: new Date().toISOString().split("T")[0],
        marketStatus: "open",
        topSignals: [
          {
            symbol: "7203",
            action: "buy",
            confidence: 0.85,
            price: 2500,
            change: 2.5,
            reason: "テクニカル分析で上昇トレンドを確認",
          },
          {
            symbol: "6758",
            action: "sell",
            confidence: 0.72,
            price: 1800,
            change: -1.2,
            reason: "利益確定のタイミング",
          },
        ],
        marketInsights: {
          trend: "bullish",
          volatility: "medium",
          sentiment: 0.7,
        },
        riskAssessment: {
          level: "medium",
          factors: ["市場の不安定性", "金利変動リスク"],
          recommendations: ["分散投資の実施", "リスク管理の徹底"],
        },
        lastUpdated: new Date().toISOString(),
      };

      // モックデータを返す
      setData(mockData);
      setFromCache(false);
      setLastUpdated(mockData.lastUpdated);
      
      // キャッシュに保存
      await unifiedCacheManager.set("today_summary", mockData, {
        ttl: 300000,
        tags: ["today", "summary"],
        priority: 0.9,
      });
      return;

    } catch (err) {
      const error = err as Error;
      const context: ErrorContext = {
        operation: "fetchTodayData",
        component: "TodayPage",
        timestamp: Date.now(),
        userAgent: navigator.userAgent,
        url: window.location.href,
      };

      await optimizedErrorHandler.handleError(error, context);
      setError("データの取得に失敗しました。しばらく待ってから再試行してください。");

      // リトライカウントを増加
      retryCount.current += 1;
    } finally {
      setLoading(false);
      isFetching.current = false;
    }
  }, []);

  const retry = useCallback(() => {
    if (retryCount.current < maxRetries) {
      fetchTodayData(false);
    }
  }, [fetchTodayData]);

  const refresh = useCallback(() => {
    retryCount.current = 0;
    fetchTodayData(false);
  }, [fetchTodayData]);

  // 初回ロード
  useEffect(() => {
    fetchTodayData(true);
  }, []); // 依存配列を空にして初回のみ実行

  return {
    data,
    loading,
    error,
    fromCache,
    retry,
    refresh,
    lastUpdated,
  };
}

// フォールバック用のフック
export function useTodayDataFallback() {
  const [fallbackData, setFallbackData] = useState<TodaySummary | null>(null);
  const [fallbackTimestamp, setFallbackTimestamp] = useState<number | null>(null);

  const saveFallbackData = useCallback((data: TodaySummary) => {
    setFallbackData(data);
    setFallbackTimestamp(Date.now());
    
    // ローカルストレージにも保存
    try {
      localStorage.setItem("today_fallback_data", JSON.stringify(data));
      localStorage.setItem("today_fallback_timestamp", Date.now().toString());
    } catch (error) {
      console.warn("Failed to save fallback data to localStorage:", error);
    }
  }, []);

  const loadFallbackData = useCallback(() => {
    try {
      const storedData = localStorage.getItem("today_fallback_data");
      const storedTimestamp = localStorage.getItem("today_fallback_timestamp");
      
      if (storedData && storedTimestamp) {
        const data = JSON.parse(storedData);
        const timestamp = parseInt(storedTimestamp);
        
        setFallbackData(data);
        setFallbackTimestamp(timestamp);
      }
    } catch (error) {
      console.warn("Failed to load fallback data from localStorage:", error);
    }
  }, []);

  // 初回ロード時にフォールバックデータを読み込み
  useEffect(() => {
    loadFallbackData();
  }, [loadFallbackData]);

  return {
    fallbackData,
    fallbackTimestamp,
    saveFallbackData,
    loadFallbackData,
  };
}