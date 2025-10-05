/**
 * 財務分析フックのテスト
 */

import { renderHook, act } from "@testing-library/react";
import { useFinancialAnalysis } from "../useFinancialAnalysis";
import { FinancialData } from "@/lib/financial/types";

// モックデータ
const mockFinancialData: FinancialData = {
  symbol: "TEST",
  companyName: "テスト企業",
  industry: "電気機器",
  fiscalYear: 2024,
  incomeStatement: {
    revenue: 1000000000,
    operatingIncome: 100000000,
    netIncome: 80000000,
    eps: 100,
  },
  balanceSheet: {
    totalAssets: 2000000000,
    currentAssets: 800000000,
    quickAssets: 600000000,
    totalLiabilities: 1200000000,
    currentLiabilities: 400000000,
    equity: 800000000,
    bps: 1000,
  },
  marketData: {
    stockPrice: 1500,
    marketCap: 15000000000,
    sharesOutstanding: 10000000,
  },
  previousYear: {
    revenue: 900000000,
    netIncome: 70000000,
    totalAssets: 1800000000,
  },
};

// モックレスポンス
const mockApiResponse = {
  success: true,
  data: {
    metrics: {
      profitability: {
        roe: 10,
        roeRanking: 10,
        roeTrend: "stable",
        roeScore: 80,
        roa: 4,
        roaRanking: 15,
        roaTrend: "stable",
        roaScore: 70,
        profitMargin: 8,
        profitMarginRanking: 12,
        profitMarginTrend: "stable",
        profitMarginScore: 75,
      },
      marketValuation: {
        per: 15,
        perRanking: 20,
        perStatus: "fair",
        perScore: 70,
        pbr: 1.5,
        pbrRanking: 25,
        pbrStatus: "fair",
        pbrScore: 65,
        psr: 15,
        psrRanking: 18,
        psrStatus: "fair",
        psrScore: 70,
      },
      safety: {
        equityRatio: 40,
        equityRatioRanking: 12,
        equityRatioStatus: "good",
        equityRatioScore: 80,
        currentRatio: 200,
        currentRatioRanking: 8,
        currentRatioStatus: "excellent",
        currentRatioScore: 95,
        quickRatio: 150,
        quickRatioRanking: 15,
        quickRatioStatus: "good",
        quickRatioScore: 85,
      },
      growth: {
        revenueGrowthRate: 11.1,
        revenueGrowthRanking: 5,
        revenueGrowthTrend: "stable",
        revenueGrowthScore: 85,
        profitGrowthRate: 14.3,
        profitGrowthRanking: 3,
        profitGrowthTrend: "stable",
        profitGrowthScore: 90,
        assetGrowthRate: 11.1,
        assetGrowthRanking: 7,
        assetGrowthTrend: "stable",
        assetGrowthScore: 88,
      },
    },
    healthScore: {
      overallScore: 80.5,
      profitabilityScore: 75,
      marketScore: 70,
      safetyScore: 85,
      growthScore: 88,
      grade: "B+",
      recommendation: "Buy",
      riskLevel: "Medium",
      strengths: ["高いROE", "安定した収益性"],
      weaknesses: ["成長率の鈍化"],
      opportunities: ["新規事業展開"],
      threats: ["競合他社の参入"],
    },
    industryComparison: {
      industry: "電気機器",
      industryAverage: {} as any,
      industryMedian: {} as any,
      industryTop: {} as any,
      industryBottom: {} as any,
      companyRanking: {
        roe: 10,
        roa: 15,
        per: 20,
        pbr: 25,
        overall: 12,
      },
      percentile: {
        roe: 80,
        roa: 75,
        per: 60,
        pbr: 55,
        overall: 70,
      },
    },
    historicalAnalysis: {
      trends: [],
      volatility: { roe: 0, roa: 0, per: 0, pbr: 0 },
      stability: "medium",
      consistency: "medium",
    },
  },
  metadata: {
    timestamp: new Date().toISOString(),
    version: "1.0.0",
    calculationTime: 0,
  },
};

// グローバルfetchのモック
global.fetch = jest.fn();

describe("useFinancialAnalysis", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("初期状態を正しく設定する", () => {
    const { result } = renderHook(() => useFinancialAnalysis());
    
    expect(result.current.data).toBeNull();
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();
    expect(result.current.metrics).toBeNull();
    expect(result.current.healthScore).toBeNull();
    expect(result.current.industryComparison).toBeNull();
    expect(result.current.historicalAnalysis).toBeNull();
  });

  it("データを正しく取得する", async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      json: () => Promise.resolve(mockApiResponse),
    });

    const { result } = renderHook(() => useFinancialAnalysis());
    
    await act(async () => {
      await result.current.refreshData("TEST");
    });

    expect(result.current.data).toEqual(mockApiResponse.data);
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it("エラーを正しく処理する", async () => {
    (global.fetch as jest.Mock).mockRejectedValueOnce(new Error("API Error"));

    const { result } = renderHook(() => useFinancialAnalysis());
    
    await act(async () => {
      await result.current.refreshData("TEST");
    });

    expect(result.current.data).toBeNull();
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBe("API Error");
  });

  it("財務指標を正しく計算する", async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      json: () => Promise.resolve({ success: true }),
    });

    const { result } = renderHook(() => useFinancialAnalysis());
    
    let validationResult;
    await act(async () => {
      validationResult = await result.current.calculateMetrics(mockFinancialData);
    });

    expect(validationResult.isValid).toBe(true);
    expect(validationResult.errors).toHaveLength(0);
  });

  it("業界比較分析を正しく取得する", async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      json: () => Promise.resolve(mockApiResponse),
    });

    const { result } = renderHook(() => useFinancialAnalysis());
    
    let industryComparison;
    await act(async () => {
      industryComparison = await result.current.getIndustryComparison("TEST", "電気機器");
    });

    expect(industryComparison).toEqual(mockApiResponse.data.industryComparison);
  });

  it("時系列分析を正しく取得する", async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      json: () => Promise.resolve(mockApiResponse),
    });

    const { result } = renderHook(() => useFinancialAnalysis());
    
    let historicalAnalysis;
    await act(async () => {
      historicalAnalysis = await result.current.getHistoricalAnalysis("TEST");
    });

    expect(historicalAnalysis).toEqual(mockApiResponse.data.historicalAnalysis);
  });

  it("統計情報を正しく生成する", async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      json: () => Promise.resolve(mockApiResponse),
    });

    const { result } = renderHook(() => useFinancialAnalysis());
    
    await act(async () => {
      await result.current.refreshData("TEST");
    });

    expect(result.current.statistics.overallScore).toBe(80.5);
    expect(result.current.statistics.grade).toBe("B+");
    expect(result.current.statistics.recommendation).toBe("Buy");
    expect(result.current.statistics.riskLevel).toBe("Medium");
  });

  it("データがない場合の統計情報を正しく処理する", () => {
    const { result } = renderHook(() => useFinancialAnalysis());
    
    expect(result.current.statistics.overallScore).toBe(0);
    expect(result.current.statistics.grade).toBe("F");
    expect(result.current.statistics.recommendation).toBe("Strong Sell");
    expect(result.current.statistics.riskLevel).toBe("High");
  });

  it("APIエラーを正しく処理する", async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      json: () => Promise.resolve({
        success: false,
        error: { message: "API Error" },
      }),
    });

    const { result } = renderHook(() => useFinancialAnalysis());
    
    await act(async () => {
      await result.current.refreshData("TEST");
    });

    expect(result.current.error).toBe("API Error");
  });

  it("業界比較分析のエラーを正しく処理する", async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      json: () => Promise.resolve({
        success: false,
        error: { message: "Industry not found" },
      }),
    });

    const { result } = renderHook(() => useFinancialAnalysis());
    
    let industryComparison;
    await act(async () => {
      industryComparison = await result.current.getIndustryComparison("TEST", "電気機器");
    });

    expect(industryComparison).toBeNull();
  });

  it("時系列分析のエラーを正しく処理する", async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      json: () => Promise.resolve({
        success: false,
        error: { message: "Historical data not found" },
      }),
    });

    const { result } = renderHook(() => useFinancialAnalysis());
    
    let historicalAnalysis;
    await act(async () => {
      historicalAnalysis = await result.current.getHistoricalAnalysis("TEST");
    });

    expect(historicalAnalysis).toBeNull();
  });
});
