/**
 * 新NISA枠管理機能のカスタムフック
 * データの取得、更新、計算を管理
 */

import { useState, useEffect, useCallback } from 'react';
import {
  NisaData,
  NisaCalculationResult,
  NisaTransaction,
  NisaQuotaStatus,
  NisaPortfolio,
  QuotaOptimization,
  TaxCalculation,
  QuotaAlert,
  InvestmentOpportunity,
  ValidationResult,
} from '@/lib/nisa/types';

interface UseNisaDataReturn {
  // データ状態
  data: NisaData | null;
  calculationResult: NisaCalculationResult | null;
  loading: boolean;
  error: string | null;

  // データ操作
  refreshData: () => Promise<void>;
  addTransaction: (transaction: Omit<NisaTransaction, 'id' | 'createdAt' | 'updatedAt'>) => Promise<ValidationResult>;
  updateTransaction: (id: string, updates: Partial<NisaTransaction>) => Promise<ValidationResult>;
  deleteTransaction: (id: string) => Promise<ValidationResult>;

  // 計算結果
  quotas: NisaQuotaStatus | null;
  portfolio: NisaPortfolio | null;
  optimization: QuotaOptimization | null;
  taxCalculation: TaxCalculation | null;
  alerts: QuotaAlert[];
  opportunities: InvestmentOpportunity[];

  // 統計情報
  statistics: {
    totalInvested: number;
    totalValue: number;
    totalProfitLoss: number;
    utilizationRate: {
      growth: number;
      accumulation: number;
    };
  };
}

export function useNisaData(): UseNisaDataReturn {
  const [data, setData] = useState<NisaData | null>(null);
  const [calculationResult, setCalculationResult] = useState<NisaCalculationResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // データを取得
  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch('/api/nisa/status');
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

  // 計算結果を取得
  const fetchCalculationResult = useCallback(async () => {
    try {
      const response = await fetch('/api/nisa/calculate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ type: 'all' }),
      });

      const result = await response.json();

      if (!result.success) {
        throw new Error(result.error?.message || '計算結果の取得に失敗しました');
      }

      setCalculationResult(result.data);
    } catch (err) {
      console.error('計算結果取得エラー:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
    }
  }, []);

  // データを更新
  const refreshData = useCallback(async () => {
    await Promise.all([fetchData(), fetchCalculationResult()]);
  }, [fetchData, fetchCalculationResult]);

  // 取引を追加
  const addTransaction = useCallback(async (
    transaction: Omit<NisaTransaction, 'id' | 'createdAt' | 'updatedAt'>
  ): Promise<ValidationResult> => {
    try {
      const response = await fetch('/api/nisa/transaction', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(transaction),
      });

      const result = await response.json();

      if (!result.success) {
        return {
          isValid: false,
          errors: [result.error?.message || '取引の追加に失敗しました'],
          warnings: [],
        };
      }

      // データを再取得
      await refreshData();

      return {
        isValid: true,
        errors: [],
        warnings: result.data?.warnings || [],
      };
    } catch (err) {
      console.error('取引追加エラー:', err);
      return {
        isValid: false,
        errors: [err instanceof Error ? err.message : 'Unknown error'],
        warnings: [],
      };
    }
  }, [refreshData]);

  // 取引を更新
  const updateTransaction = useCallback(async (
    id: string,
    updates: Partial<NisaTransaction>
  ): Promise<ValidationResult> => {
    try {
      const response = await fetch('/api/nisa/transaction', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ id, ...updates }),
      });

      const result = await response.json();

      if (!result.success) {
        return {
          isValid: false,
          errors: [result.error?.message || '取引の更新に失敗しました'],
          warnings: [],
        };
      }

      // データを再取得
      await refreshData();

      return {
        isValid: true,
        errors: [],
        warnings: result.data?.warnings || [],
      };
    } catch (err) {
      console.error('取引更新エラー:', err);
      return {
        isValid: false,
        errors: [err instanceof Error ? err.message : 'Unknown error'],
        warnings: [],
      };
    }
  }, [refreshData]);

  // 取引を削除
  const deleteTransaction = useCallback(async (id: string): Promise<ValidationResult> => {
    try {
      const response = await fetch(`/api/nisa/transaction?id=${id}`, {
        method: 'DELETE',
      });

      const result = await response.json();

      if (!result.success) {
        return {
          isValid: false,
          errors: [result.error?.message || '取引の削除に失敗しました'],
          warnings: [],
        };
      }

      // データを再取得
      await refreshData();

      return {
        isValid: true,
        errors: [],
        warnings: [],
      };
    } catch (err) {
      console.error('取引削除エラー:', err);
      return {
        isValid: false,
        errors: [err instanceof Error ? err.message : 'Unknown error'],
        warnings: [],
      };
    }
  }, [refreshData]);

  // 初期化
  useEffect(() => {
    refreshData();
  }, [refreshData]);

  // 計算結果から統計情報を生成
  const statistics = {
    totalInvested: calculationResult?.portfolio?.totalCost || 0,
    totalValue: calculationResult?.portfolio?.totalValue || 0,
    totalProfitLoss: (calculationResult?.portfolio?.unrealizedProfitLoss || 0) + 
                    (calculationResult?.portfolio?.realizedProfitLoss || 0),
    utilizationRate: {
      growth: calculationResult?.quotas?.growthInvestment?.utilizationRate || 0,
      accumulation: calculationResult?.quotas?.accumulationInvestment?.utilizationRate || 0,
    },
  };

  return {
    // データ状態
    data,
    calculationResult,
    loading,
    error,

    // データ操作
    refreshData,
    addTransaction,
    updateTransaction,
    deleteTransaction,

    // 計算結果
    quotas: calculationResult?.quotas || null,
    portfolio: calculationResult?.portfolio || null,
    optimization: calculationResult?.optimization || null,
    taxCalculation: calculationResult?.taxCalculation || null,
    alerts: calculationResult?.alerts || [],
    opportunities: calculationResult?.opportunities || [],

    // 統計情報
    statistics,
  };
}
