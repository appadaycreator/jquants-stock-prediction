/**
 * 新NISA税務計算・最適化APIのテスト
 */

import { POST } from "../calculate/route";
import { NextRequest } from "next/server";

// モック
jest.mock("@/lib/nisa", () => ({
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
        positions: [],
        totalValue: 260_000,
        totalCost: 250_000,
        unrealizedProfitLoss: 10_000,
        realizedProfitLoss: 0,
        taxFreeProfitLoss: 10_000,
        lastUpdated: "2024-01-15T10:00:00Z",
      },
      optimization: {
        recommendations: {
          growthQuota: {
            suggestedAmount: 500_000,
            reason: "成長投資枠の利用率が低いため、積極的な投資を推奨",
            priority: "HIGH",
          },
          accumulationQuota: {
            suggestedAmount: 100_000,
            reason: "つみたて投資枠の利用率が低いため、定期的な積立投資を推奨",
            priority: "HIGH",
          },
        },
        riskAnalysis: {
          diversificationScore: 10,
          sectorConcentration: 100,
          riskLevel: "HIGH",
        },
        lastCalculated: "2024-01-15T10:00:00Z",
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
        calculatedAt: "2024-01-15T10:00:00Z",
      },
      alerts: [],
      opportunities: [],
    }),
  })),
}));

describe("/api/nisa/calculate", () => {
  it("全ての計算結果を返す", async () => {
    const request = new NextRequest("http://localhost:3000/api/nisa/calculate", {
      method: "POST",
      body: JSON.stringify({ type: "all" }),
      headers: {
        "Content-Type": "application/json",
      },
    });

    const response = await POST(request);
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data.success).toBe(true);
    expect(data.data.quotas).toBeDefined();
    expect(data.data.portfolio).toBeDefined();
    expect(data.data.optimization).toBeDefined();
    expect(data.data.taxCalculation).toBeDefined();
    expect(data.data.alerts).toBeDefined();
    expect(data.data.opportunities).toBeDefined();
  });

  it("特定の計算タイプのみを返す", async () => {
    const request = new NextRequest("http://localhost:3000/api/nisa/calculate", {
      method: "POST",
      body: JSON.stringify({ type: "quotas" }),
      headers: {
        "Content-Type": "application/json",
      },
    });

    const response = await POST(request);
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data.success).toBe(true);
    expect(data.data.quotas).toBeDefined();
    expect(data.data.portfolio).toBeUndefined();
    expect(data.metadata.calculationType).toBe("quotas");
  });

  it("データが見つからない場合は404を返す", async () => {
    // モックを変更
    const { NisaManager } = require("@/lib/nisa");
    NisaManager.mockImplementation(() => ({
      initialize: jest.fn().mockResolvedValue(true),
      getCalculationResult: jest.fn().mockResolvedValue(null),
    }));

    const request = new NextRequest("http://localhost:3000/api/nisa/calculate", {
      method: "POST",
      body: JSON.stringify({ type: "all" }),
      headers: {
        "Content-Type": "application/json",
      },
    });

    const response = await POST(request);
    const data = await response.json();

    expect(response.status).toBe(404);
    expect(data.success).toBe(false);
    expect(data.error.code).toBe("DATA_NOT_FOUND");
  });

  it("エラー時は500を返す", async () => {
    // モックを変更
    const { NisaManager } = require("@/lib/nisa");
    NisaManager.mockImplementation(() => ({
      initialize: jest.fn().mockRejectedValue(new Error("Test error")),
      getCalculationResult: jest.fn().mockRejectedValue(new Error("Test error")),
    }));

    const request = new NextRequest("http://localhost:3000/api/nisa/calculate", {
      method: "POST",
      body: JSON.stringify({ type: "all" }),
      headers: {
        "Content-Type": "application/json",
      },
    });

    const response = await POST(request);
    const data = await response.json();

    expect(response.status).toBe(500);
    expect(data.success).toBe(false);
    expect(data.error.code).toBe("CALCULATION_ERROR");
  });
});
