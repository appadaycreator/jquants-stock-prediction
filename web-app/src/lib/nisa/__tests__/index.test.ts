/**
 * 新NISA枠管理機能の統合テスト
 */

import { NisaManager } from "../index";

describe("NisaManager", () => {
  let nisaManager: NisaManager;

  beforeEach(() => {
    nisaManager = new NisaManager();
  });

  it("初期化ができる", async () => {
    const result = await nisaManager.initialize();
    expect(result).toBe(true);
  });

  it("計算結果を取得できる", async () => {
    await nisaManager.initialize();
    const result = await nisaManager.getCalculationResult();
    expect(result).not.toBeNull();
  });

  it("取引を追加できる", async () => {
    await nisaManager.initialize();
    
    const transaction = {
      type: "BUY" as const,
      symbol: "7203",
      symbolName: "トヨタ自動車",
      quantity: 100,
      price: 2500,
      amount: 250_000,
      quotaType: "GROWTH" as const,
      transactionDate: "2024-01-15",
    };

    const result = await nisaManager.addTransaction(transaction);
    expect(result.isValid).toBe(true);
  });

  it("データを保存できる", async () => {
    const mockData = {
      userProfile: {
        userId: "test-user",
        startDate: "2024-01-01",
        taxYear: 2024,
        preferences: {
          autoRebalancing: false,
          alertThresholds: {
            growthWarning: 70,
            accumulationWarning: 70,
          },
          notifications: {
            email: false,
            browser: true,
            push: false,
          },
        },
        createdAt: "2024-01-01T00:00:00Z",
        updatedAt: "2024-01-01T00:00:00Z",
      },
      quotas: {
        growthInvestment: {
          annualLimit: 2_400_000,
          taxFreeLimit: 12_000_000,
          usedAmount: 0,
          availableAmount: 2_400_000,
          utilizationRate: 0,
        },
        accumulationInvestment: {
          annualLimit: 400_000,
          taxFreeLimit: 2_000_000,
          usedAmount: 0,
          availableAmount: 400_000,
          utilizationRate: 0,
        },
        quotaReuse: {
          growthAvailable: 0,
          accumulationAvailable: 0,
          nextYearAvailable: 0,
        },
      },
      transactions: [],
      portfolio: {
        positions: [],
        totalValue: 0,
        totalCost: 0,
        unrealizedProfitLoss: 0,
        realizedProfitLoss: 0,
        taxFreeProfitLoss: 0,
        lastUpdated: "2024-01-01T00:00:00Z",
      },
      settings: {
        autoRebalancing: false,
        alertThresholds: {
          growthWarning: 70,
          accumulationWarning: 70,
        },
        notifications: {
          email: false,
          browser: true,
          push: false,
        },
      },
      lastUpdated: "2024-01-01T00:00:00Z",
    };

    const result = await nisaManager.saveData(mockData);
    expect(result).toBe(true);
  });

  it("データを読み込める", async () => {
    const result = await nisaManager.loadData();
    expect(result).toBeDefined();
  });
});
