/**
 * 強化された個人投資データ取得フック
 * 新しいAPIクライアントとエラーハンドリングを使用
 */

import { useState, useEffect, useCallback } from 'react';
import apiClient from '@/lib/enhanced-api-client';
import cacheManager from '@/lib/enhanced-cache-manager';
import errorHandler, { ErrorContext } from '@/lib/enhanced-error-handler';
import { useLoadingState } from '@/components/EnhancedLoadingSpinner';

interface PersonalInvestmentData {
  date: string;
  portfolio: {
    totalValue: number;
    totalReturn: number;
    totalReturnPercent: number;
    positions: Array<{
      symbol: string;
      name: string;
      shares: number;
      currentPrice: number;
      marketValue: number;
      costBasis: number;
      gainLoss: number;
      gainLossPercent: number;
      weight: number;
    }>;
  };
  recommendations: Array<{
    symbol: string;
    action: 'buy' | 'sell' | 'hold';
    confidence: number;
    targetPrice: number;
    currentPrice: number;
    potentialReturn: number;
    riskLevel: 'low' | 'medium' | 'high';
    reasoning: string;
  }>;
  riskAssessment: {
    overallRisk: 'low' | 'medium' | 'high';
    diversificationScore: number;
    concentrationRisk: number;
    volatilityRisk: number;
    recommendations: string[];
  };
  performance: {
    dailyReturn: number;
    weeklyReturn: number;
    monthlyReturn: number;
    quarterlyReturn: number;
    yearlyReturn: number;
    sharpeRatio: number;
    maxDrawdown: number;
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
  const [error, setError] = useState<string | null>(null);
  const [fromCache, setFromCache] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);
  
  const { state: loadingState, startLoading, setError: setLoadingError, setSuccess, retry: retryLoading } = useLoadingState('個人投資データを取得中...');

  const fetchPersonalInvestmentData = useCallback(async (useCache: boolean = true) => {
    try {
      startLoading('個人投資データを取得中...');
      setError(null);

      // キャッシュから取得を試行
      if (useCache) {
        const cachedData = await cacheManager.get<PersonalInvestmentData>('personal_investment');
        if (cachedData) {
          setData(cachedData);
          setFromCache(true);
          setLastUpdated(cachedData.lastUpdated);
          setSuccess('キャッシュからデータを取得しました');
          return;
        }
      }

      // APIから取得
      const response = await apiClient.get<PersonalInvestmentData>(
        'markets/daily_quotes',
        { 
          date: new Date().toISOString().split('T')[0],
          type: 'personal_investment'
        },
        {
          cache: {
            key: 'personal_investment',
            ttl: 600000, // 10分
            tags: ['personal', 'investment', 'portfolio'],
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
        await cacheManager.set('personal_investment', response.data, {
          ttl: 600000,
          tags: ['personal', 'investment', 'portfolio'],
          priority: 0.9,
        });
        
        setSuccess('個人投資データを取得しました');
      } else {
        throw new Error('データが取得できませんでした');
      }

    } catch (err) {
      const error = err as Error;
      const context: ErrorContext = {
        operation: 'fetchPersonalInvestmentData',
        component: 'PersonalInvestmentPage',
        timestamp: Date.now(),
        userAgent: navigator.userAgent,
        url: window.location.href,
      };

      const classification = errorHandler.handleError(error, context);
      setError(classification.userMessage);
      setLoadingError(classification.userMessage);

      // 自動復旧の試行
      if (classification.recovery?.autoRetry) {
        const canRetry = await errorHandler.attemptRecovery(classification, context);
        if (canRetry) {
          setTimeout(() => fetchPersonalInvestmentData(false), classification.recovery?.retryDelay || 2000);
        }
      }
    }
  }, [startLoading, setSuccess, setLoadingError]);

  const retry = useCallback(() => {
    retryLoading();
    fetchPersonalInvestmentData(false);
  }, [retryLoading, fetchPersonalInvestmentData]);

  const refresh = useCallback(() => {
    fetchPersonalInvestmentData(false);
  }, [fetchPersonalInvestmentData]);

  useEffect(() => {
    fetchPersonalInvestmentData();
  }, [fetchPersonalInvestmentData]);

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
 * 個人投資データの前回結果表示フック
 */
export function usePersonalInvestmentFallback() {
  const [fallbackData, setFallbackData] = useState<PersonalInvestmentData | null>(null);
  const [fallbackTimestamp, setFallbackTimestamp] = useState<string | null>(null);

  useEffect(() => {
    // ローカルストレージから前回の結果を取得
    const loadFallbackData = async () => {
      try {
        const cached = localStorage.getItem('personal_investment_fallback');
        const timestamp = localStorage.getItem('personal_investment_timestamp');
        
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

  const saveFallbackData = useCallback((data: PersonalInvestmentData) => {
    try {
      localStorage.setItem('personal_investment_fallback', JSON.stringify(data));
      localStorage.setItem('personal_investment_timestamp', new Date().toISOString());
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
