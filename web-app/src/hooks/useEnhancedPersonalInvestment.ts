/**
 * 強化された個人投資データ取得フック
 * 新しいAPIクライアントとエラーハンドリングを使用
 */

"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import apiClient from "@/lib/enhanced-api-client";
import optimizedCacheManager from "@/lib/optimized-cache-manager";
import optimizedErrorHandler, { ErrorContext } from "@/lib/optimized-error-handler";

interface PersonalInvestmentData {
  portfolio: {
    totalValue: number;
    totalReturn: number;
    totalReturnPercentage: number;
    positions: Array<{
      symbol: string;
      shares: number;
      currentPrice: number;
      totalValue: number;
      return: number;
      returnPercentage: number;
    }>;
  };
  recommendations: Array<{
    symbol: string;
    action: "buy" | "sell" | "hold";
    confidence: number;
    targetPrice: number;
    currentPrice: number;
    reason: string;
  }>;
  riskAnalysis: {
    level: "low" | "medium" | "high";
    factors: string[];
    recommendations: string[];
  };
  lastUpdated: string;
}

interface UseEnhancedPersonalInvestmentReturn {
  data: PersonalInvestmentData | null;
  loading: boolean;
  error: string | null;
  fromCache: boolean;
  retry: () => void;
  refresh: () => void;
  lastUpdated: string | null;
}

export function useEnhancedPersonalInvestment(): UseEnhancedPersonalInvestmentReturn {
  const [data, setData] = useState<PersonalInvestmentData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fromCache, setFromCache] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);
  
  // 無限ループを防ぐためのref
  const isFetching = useRef(false);
  const retryCount = useRef(0);
  const maxRetries = 3;

  const fetchPersonalInvestmentData = useCallback(async (useCache: boolean = true) => {
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
        const cachedData = await optimizedCacheManager.get<PersonalInvestmentData>("personal_investment");
        if (cachedData) {
          setData(cachedData);
          setFromCache(true);
          setLastUpdated(cachedData.lastUpdated);
          return;
        }
      }

      // モックデータを返す（開発環境用）
      const mockData: PersonalInvestmentData = {
        portfolio: {
          totalValue: 1500000,
          totalReturn: 150000,
          totalReturnPercentage: 11.1,
          positions: [
            {
              symbol: "7203",
              shares: 100,
              currentPrice: 2500,
              totalValue: 250000,
              return: 25000,
              returnPercentage: 11.1,
            },
            {
              symbol: "6758",
              shares: 50,
              currentPrice: 1800,
              totalValue: 90000,
              return: 9000,
              returnPercentage: 11.1,
            },
          ],
        },
        recommendations: [
          {
            symbol: "7203",
            action: "buy",
            confidence: 0.85,
            targetPrice: 2600,
            currentPrice: 2500,
            reason: "テクニカル分析で上昇トレンドを確認",
          },
        ],
        riskAnalysis: {
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
      await optimizedCacheManager.set("personal_investment", mockData, {
        ttl: 600000,
        tags: ["personal", "investment", "portfolio"],
        priority: 0.9,
      });
      return;

    } catch (err) {
      const error = err as Error;
      const context: ErrorContext = {
        operation: "fetchPersonalInvestmentData",
        component: "PersonalInvestmentPage",
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
      fetchPersonalInvestmentData(false);
    }
  }, [fetchPersonalInvestmentData]);

  const refresh = useCallback(() => {
    retryCount.current = 0;
    fetchPersonalInvestmentData(false);
  }, [fetchPersonalInvestmentData]);

  // 初回ロード
  useEffect(() => {
    fetchPersonalInvestmentData(true);
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
export function usePersonalInvestmentFallback() {
  const [fallbackData, setFallbackData] = useState<PersonalInvestmentData | null>(null);
  const [fallbackTimestamp, setFallbackTimestamp] = useState<number | null>(null);

  const saveFallbackData = useCallback((data: PersonalInvestmentData) => {
    setFallbackData(data);
    setFallbackTimestamp(Date.now());
    
    // ローカルストレージにも保存
    try {
      localStorage.setItem("personal_investment_fallback_data", JSON.stringify(data));
      localStorage.setItem("personal_investment_fallback_timestamp", Date.now().toString());
    } catch (error) {
      console.warn("Failed to save fallback data to localStorage:", error);
    }
  }, []);

  const loadFallbackData = useCallback(() => {
    try {
      const storedData = localStorage.getItem("personal_investment_fallback_data");
      const storedTimestamp = localStorage.getItem("personal_investment_fallback_timestamp");
      
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