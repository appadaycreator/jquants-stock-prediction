/**
 * 新NISA枠管理機能のカスタムフックテスト
 */

import { renderHook, waitFor } from '@testing-library/react';
import { useNisaData } from '../useNisaData';

// モック
jest.mock('@/lib/nisa', () => ({
  NisaManager: jest.fn().mockImplementation(() => ({
    initialize: jest.fn().mockResolvedValue(true),
    getCalculationResult: jest.fn().mockResolvedValue({
      quotas: {
        growthInvestment: {
          annualLimit: 2_400_000,
          taxFreeLimit: 12_000_000,
          usedAmount: 500_000,
          availableAmount: 1_900_000,
          utilizationRate: 20.83,
        },
        accumulationInvestment: {
          annualLimit: 400_000,
          taxFreeLimit: 2_000_000,
          usedAmount: 100_000,
          availableAmount: 300_000,
          utilizationRate: 25.0,
        },
        quotaReuse: {
          growthAvailable: 0,
          accumulationAvailable: 0,
          nextYearAvailable: 0,
        },
      },
      portfolio: {
        positions: [
          {
            symbol: '7203',
            symbolName: 'トヨタ自動車',
            quantity: 100,
            averagePrice: 2500,
            currentPrice: 2600,
            cost: 250_000,
            currentValue: 260_000,
            unrealizedProfitLoss: 10_000,
            quotaType: 'GROWTH',
            purchaseDate: '2024-01-15',
            lastUpdated: '2024-01-15T10:00:00Z',
          },
        ],
        totalValue: 260_000,
        totalCost: 250_000,
        unrealizedProfitLoss: 10_000,
        realizedProfitLoss: 0,
        taxFreeProfitLoss: 10_000,
        lastUpdated: '2024-01-15T10:00:00Z',
      },
      optimization: {
        recommendations: {
          growthQuota: {
            suggestedAmount: 500_000,
            reason: '成長投資枠の利用率が低いため、積極的な投資を推奨',
            priority: 'HIGH',
          },
          accumulationQuota: {
            suggestedAmount: 100_000,
            reason: 'つみたて投資枠の利用率が低いため、定期的な積立投資を推奨',
            priority: 'HIGH',
          },
        },
        riskAnalysis: {
          diversificationScore: 10,
          sectorConcentration: 100,
          riskLevel: 'HIGH',
        },
        lastCalculated: '2024-01-15T10:00:00Z',
      },
      taxCalculation: {
        currentYear: {
          growthQuotaUsed: 500_000,
          accumulationQuotaUsed: 100_000,
          totalTaxFreeAmount: 600_000,
        },
        nextYear: {
          availableGrowthQuota: 2_400_000,
          availableAccumulationQuota: 400_000,
          reusableQuota: 0,
        },
        taxSavings: {
          estimatedTaxSavings: 120_000,
          taxRate: 0.20,
          effectiveTaxRate: 0.20,
        },
        calculatedAt: '2024-01-15T10:00:00Z',
      },
      alerts: [],
      opportunities: [
        {
          id: 'opp-1',
          symbol: '6758',
          symbolName: 'ソニーグループ',
          reason: '成長投資枠の利用率が低く、投資機会があります',
          expectedReturn: 0.08,
          riskLevel: 'MEDIUM',
          quotaRecommendation: 'GROWTH',
          suggestedAmount: 200_000,
          confidence: 0.75,
          createdAt: '2024-01-15T10:00:00Z',
        },
      ],
    }),
    addTransaction: jest.fn().mockResolvedValue({
      isValid: true,
      errors: [],
      warnings: [],
    }),
    updateTransaction: jest.fn().mockResolvedValue({
      isValid: true,
      errors: [],
      warnings: [],
    }),
    deleteTransaction: jest.fn().mockResolvedValue({
      isValid: true,
      errors: [],
      warnings: [],
    }),
  })),
}));

// グローバルfetchのモック
global.fetch = jest.fn();

describe('useNisaData', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockResolvedValue({
      json: () => Promise.resolve({
        success: true,
        data: {
          quotas: {
            growthInvestment: {
              annualLimit: 2_400_000,
              taxFreeLimit: 12_000_000,
              usedAmount: 500_000,
              availableAmount: 1_900_000,
              utilizationRate: 20.83,
            },
            accumulationInvestment: {
              annualLimit: 400_000,
              taxFreeLimit: 2_000_000,
              usedAmount: 100_000,
              availableAmount: 300_000,
              utilizationRate: 25.0,
            },
            quotaReuse: {
              growthAvailable: 0,
              accumulationAvailable: 0,
              nextYearAvailable: 0,
            },
          },
          portfolio: {
            positions: [],
            totalValue: 260_000,
            totalCost: 250_000,
            unrealizedProfitLoss: 10_000,
            realizedProfitLoss: 0,
            taxFreeProfitLoss: 10_000,
            lastUpdated: '2024-01-15T10:00:00Z',
          },
          alerts: [],
          opportunities: [],
        },
      }),
    });
  });

  it('初期状態でデータを読み込む', async () => {
    const { result } = renderHook(() => useNisaData());

    expect(result.current.loading).toBe(true);
    expect(result.current.data).toBeNull();
    expect(result.current.calculationResult).toBeNull();

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).not.toBeNull();
    expect(result.current.calculationResult).not.toBeNull();
  });

  it('エラー時にエラー状態を設定', async () => {
    (global.fetch as jest.Mock).mockRejectedValue(new Error('Network error'));

    const { result } = renderHook(() => useNisaData());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.error).toBe('Network error');
    expect(result.current.data).toBeNull();
  });

  it('APIエラー時にエラー状態を設定', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      json: () => Promise.resolve({
        success: false,
        error: {
          message: 'API error',
        },
      }),
    });

    const { result } = renderHook(() => useNisaData());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.error).toBe('API error');
  });

  it('データの更新ができる', async () => {
    const { result } = renderHook(() => useNisaData());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    const refreshData = result.current.refreshData;
    expect(typeof refreshData).toBe('function');

    await refreshData();
    expect(global.fetch).toHaveBeenCalledTimes(2); // 初期読み込み + 更新
  });

  it('取引の追加ができる', async () => {
    const { result } = renderHook(() => useNisaData());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    const transaction = {
      type: 'BUY' as const,
      symbol: '7203',
      symbolName: 'トヨタ自動車',
      quantity: 100,
      price: 2500,
      amount: 250_000,
      quotaType: 'GROWTH' as const,
      transactionDate: '2024-01-15',
    };

    const result_add = await result.current.addTransaction(transaction);
    expect(result_add.isValid).toBe(true);
    expect(result_add.errors).toHaveLength(0);
  });

  it('取引の更新ができる', async () => {
    const { result } = renderHook(() => useNisaData());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    const result_update = await result.current.updateTransaction('test-id', {
      quantity: 200,
      amount: 500_000,
    });

    expect(result_update.isValid).toBe(true);
    expect(result_update.errors).toHaveLength(0);
  });

  it('取引の削除ができる', async () => {
    const { result } = renderHook(() => useNisaData());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    const result_delete = await result.current.deleteTransaction('test-id');
    expect(result_delete.isValid).toBe(true);
    expect(result_delete.errors).toHaveLength(0);
  });

  it('統計情報が正しく計算される', async () => {
    const { result } = renderHook(() => useNisaData());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.statistics.totalInvested).toBe(250_000);
    expect(result.current.statistics.totalValue).toBe(260_000);
    expect(result.current.statistics.totalProfitLoss).toBe(10_000);
    expect(result.current.statistics.utilizationRate.growth).toBeCloseTo(20.83, 2);
    expect(result.current.statistics.utilizationRate.accumulation).toBeCloseTo(25.0, 2);
  });

  it('計算結果が正しく提供される', async () => {
    const { result } = renderHook(() => useNisaData());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.quotas).not.toBeNull();
    expect(result.current.portfolio).not.toBeNull();
    expect(result.current.optimization).not.toBeNull();
    expect(result.current.taxCalculation).not.toBeNull();
    expect(result.current.alerts).toEqual([]);
    expect(result.current.opportunities).toHaveLength(1);
  });
});
