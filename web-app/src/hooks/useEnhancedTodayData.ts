/**
 * 強化された今日の指示データ取得フック
 * 新しいAPIクライアントとエラーハンドリングを使用
 */

"use client";

import { useState, useEffect, useCallback } from 'react';
import apiClient from '@/lib/enhanced-api-client';
import cacheManager from '@/lib/enhanced-cache-manager';
import errorHandler, { ErrorContext } from '@/lib/enhanced-error-handler';
import { useLoadingState } from '@/components/EnhancedLoadingSpinner';

interface TodaySummary {
  date: string;
  marketStatus: 'open' | 'closed' | 'pre_market' | 'after_hours';
  topSignals: Array<{
    symbol: string;
    action: 'buy' | 'sell' | 'hold';
    confidence: number;
    price: number;
    change: number;
    reason: string;
  }>;
  marketInsights: {
    trend: 'bullish' | 'bearish' | 'neutral';
    volatility: 'low' | 'medium' | 'high';
    sentiment: number;
  };
  riskAssessment: {
    level: 'low' | 'medium' | 'high';
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
  const [error, setError] = useState<string | null>(null);
  const [fromCache, setFromCache] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);
  
  const { state: loadingState, startLoading, setError: setLoadingError, setSuccess, retry: retryLoading } = useLoadingState('今日の指示を取得中...');

  const fetchTodayData = useCallback(async (useCache: boolean = true) => {
    try {
      startLoading('今日の指示を取得中...');
      setError(null);

      // キャッシュから取得を試行
      if (useCache) {
        const cachedData = await cacheManager.get<TodaySummary>('today_summary');
        if (cachedData) {
          setData(cachedData);
          setFromCache(true);
          setLastUpdated(cachedData.lastUpdated);
          setSuccess('キャッシュからデータを取得しました');
          return;
        }
      }

      // APIから取得
      const response = await apiClient.get<TodaySummary>(
        'markets/daily_quotes',
        { date: new Date().toISOString().split('T')[0] },
        {
          cache: {
            key: 'today_summary',
            ttl: 300000, // 5分
            tags: ['today', 'summary'],
          },
          retry: {
            maxRetries: 3,
            retryDelay: 1000,
            backoffMultiplier: 2,
            retryCondition: (error) => {
              return error.message.includes('timeout') || 
                     error.message.includes('network') || 
                     error.message.includes('5');
            },
          },
        }
      );

      if (response.data) {
        setData(response.data);
        setFromCache(response.fromCache);
        setLastUpdated(response.data.lastUpdated);
        
        // キャッシュに保存
        await cacheManager.set('today_summary', response.data, {
          ttl: 300000,
          tags: ['today', 'summary'],
          priority: 0.9,
        });
        
        setSuccess('今日の指示を取得しました');
      } else {
        throw new Error('データが取得できませんでした');
      }

    } catch (err) {
      const error = err as Error;
      const context: ErrorContext = {
        operation: 'fetchTodayData',
        component: 'TodayPage',
        timestamp: Date.now(),
        userAgent: navigator.userAgent,
        url: window.location.href,
      };

      const classification = errorHandler.handleError(error, context);
      setError(classification.userMessage);
      setLoadingError(classification.userMessage);

      // 自動復旧は無効化（無限ループを防ぐ）
      // if (classification.recovery?.autoRetry) {
      //   const canRetry = await errorHandler.attemptRecovery(classification, context);
      //   if (canRetry) {
      //     setTimeout(() => fetchTodayData(false), classification.recovery?.retryDelay || 2000);
      //   }
      // }
    }
  }, [startLoading, setSuccess, setLoadingError]);

  const retry = useCallback(() => {
    retryLoading();
    fetchTodayData(false);
  }, [retryLoading, fetchTodayData]);

  const refresh = useCallback(() => {
    fetchTodayData(false);
  }, [fetchTodayData]);

  useEffect(() => {
    fetchTodayData();
  }, [fetchTodayData]);

  return {
    data,
    loading: loadingState.isLoading,
    error,
    fromCache,
    retry,
    refresh,
    lastUpdated,
  };
}

/**
 * 今日の指示データの前回結果表示フック
 */
export function useTodayDataFallback() {
  const [fallbackData, setFallbackData] = useState<TodaySummary | null>(null);
  const [fallbackTimestamp, setFallbackTimestamp] = useState<string | null>(null);

  useEffect(() => {
    // ローカルストレージから前回の結果を取得
    const loadFallbackData = async () => {
      try {
        const cached = localStorage.getItem('today_summary_fallback');
        const timestamp = localStorage.getItem('today_summary_timestamp');
        
        if (cached && timestamp) {
          const data = JSON.parse(cached);
          const age = Date.now() - new Date(timestamp).getTime();
          
          // 24時間以内のデータのみ使用
          if (age < 24 * 60 * 60 * 1000) {
            setFallbackData(data);
            setFallbackTimestamp(timestamp);
          }
        }
      } catch (error) {
        console.warn('フォールバックデータの読み込みに失敗:', error);
      }
    };

    loadFallbackData();
  }, []);

  const saveFallbackData = useCallback((data: TodaySummary) => {
    try {
      localStorage.setItem('today_summary_fallback', JSON.stringify(data));
      localStorage.setItem('today_summary_timestamp', new Date().toISOString());
    } catch (error) {
      console.warn('フォールバックデータの保存に失敗:', error);
    }
  }, []);

  return {
    fallbackData,
    fallbackTimestamp,
    saveFallbackData,
  };
}
