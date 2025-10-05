/**
 * 新NISA枠状況取得APIのテスト
 */

import { GET } from "../status/route";
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
      alerts: [],
      opportunities: [],
    }),
  })),
}));

describe("/api/nisa/status", () => {
  it("正常なレスポンスを返す", async () => {
    const request = new NextRequest("http://localhost:3000/api/nisa/status");
    const response = await GET(request);
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data.success).toBe(true);
    expect(data.data).toBeDefined();
    expect(data.data.quotas).toBeDefined();
    expect(data.data.portfolio).toBeDefined();
    expect(data.data.alerts).toBeDefined();
    expect(data.data.opportunities).toBeDefined();
  });

  it("データが見つからない場合は404を返す", async () => {
    // モックを変更
    const { NisaManager } = require("@/lib/nisa");
    NisaManager.mockImplementation(() => ({
      initialize: jest.fn().mockResolvedValue(true),
      getCalculationResult: jest.fn().mockResolvedValue(null),
    }));

    const request = new NextRequest("http://localhost:3000/api/nisa/status");
    const response = await GET(request);
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

    const request = new NextRequest("http://localhost:3000/api/nisa/status");
    const response = await GET(request);
    const data = await response.json();

    expect(response.status).toBe(500);
    expect(data.success).toBe(false);
    expect(data.error.code).toBe("INTERNAL_ERROR");
  });
});
