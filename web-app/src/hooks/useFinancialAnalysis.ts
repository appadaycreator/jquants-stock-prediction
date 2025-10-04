/**
 * 財務指標分析機能のカスタムフック
 * データの取得、更新、計算を管理
 */

import { useState, useEffect, useCallback } from 'react';
import {
  FinancialData,
  FinancialCalculationResult,
  FinancialMetrics,
  FinancialHealthScore,
  IndustryComparison,
  HistoricalAnalysis,
  FinancialValidationResult,
} from '@/lib/financial/types';

interface UseFinancialAnalysisReturn {
  // データ状態
  data: FinancialCalculationResult | null;
  loading: boolean;
  error: string | null;

  // データ操作
  refreshData: (symbol: string) => Promise<void>;
  calculateMetrics: (data: FinancialData) => Promise<FinancialValidationResult>;
  getIndustryComparison: (symbol: string, industry: string) => Promise<IndustryComparison | null>;
  getHistoricalAnalysis: (symbol: string) => Promise<HistoricalAnalysis | null>;

  // 計算結果
  metrics: FinancialMetrics | null;
  healthScore: FinancialHealthScore | null;
  industryComparison: IndustryComparison | null;
  historicalAnalysis: HistoricalAnalysis | null;

  // 統計情報
  statistics: {
    overallScore: number;
    grade: string;
    recommendation: string;
    riskLevel: string;
  };
}

export function useFinancialAnalysis(): UseFinancialAnalysisReturn {
  const [data, setData] = useState<FinancialCalculationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // データを取得
  const fetchData = useCallback(async (symbol: string) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`/api/financial/analysis/${symbol}`);
      const result = await response.json();

      if (!result.success) {
        throw new Error(result.error?.message || 'データの取得に失敗しました');
      }

      setData(result.data);
    } catch (err) {
      console.error('データ取得エラー:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, []);

  // データを更新
  const refreshData = useCallback(async (symbol: string) => {
    await fetchData(symbol);
  }, [fetchData]);

  // 財務指標を計算
  const calculateMetrics = useCallback(async (data: FinancialData): Promise<FinancialValidationResult> => {
    try {
      const response = await fetch('/api/financial/calculate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ data, type: 'metrics' }),
      });

      const result = await response.json();

      if (!result.success) {
        return {
          isValid: false,
          errors: [result.error?.message || '財務指標の計算に失敗しました'],
          warnings: [],
        };
      }

      return {
        isValid: true,
        errors: [],
        warnings: [],
      };
    } catch (err) {
      console.error('財務指標計算エラー:', err);
      return {
        isValid: false,
        errors: [err instanceof Error ? err.message : 'Unknown error'],
        warnings: [],
      };
    }
  }, []);

  // 業界比較分析を取得
  const getIndustryComparison = useCallback(async (
    symbol: string,
    industry: string
  ): Promise<IndustryComparison | null> => {
    try {
      const response = await fetch(`/api/financial/industry/${industry}`);
      const result = await response.json();

      if (!result.success) {
        throw new Error(result.error?.message || '業界比較分析の取得に失敗しました');
      }

      return result.data.industryComparison;
    } catch (err) {
      console.error('業界比較分析取得エラー:', err);
      return null;
    }
  }, []);

  // 時系列分析を取得
  const getHistoricalAnalysis = useCallback(async (symbol: string): Promise<HistoricalAnalysis | null> => {
    try {
      const response = await fetch(`/api/financial/trend/${symbol}`);
      const result = await response.json();

      if (!result.success) {
        throw new Error(result.error?.message || '時系列分析の取得に失敗しました');
      }

      return result.data.historicalAnalysis;
    } catch (err) {
      console.error('時系列分析取得エラー:', err);
      return null;
    }
  }, []);

  // 統計情報を生成
  const statistics = {
    overallScore: data?.healthScore?.overallScore || 0,
    grade: data?.healthScore?.grade || 'F',
    recommendation: data?.healthScore?.recommendation || 'Strong Sell',
    riskLevel: data?.healthScore?.riskLevel || 'High',
  };

  return {
    // データ状態
    data,
    loading,
    error,

    // データ操作
    refreshData,
    calculateMetrics,
    getIndustryComparison,
    getHistoricalAnalysis,

    // 計算結果
    metrics: data?.metrics || null,
    healthScore: data?.healthScore || null,
    industryComparison: data?.industryComparison || null,
    historicalAnalysis: data?.historicalAnalysis || null,

    // 統計情報
    statistics,
  };
}
