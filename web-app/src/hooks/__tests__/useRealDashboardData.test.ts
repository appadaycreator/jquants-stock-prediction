import { renderHook, act } from "@testing-library/react";
import { useRealDashboardData } from "../useRealDashboardData";

// Mock the testConnection function
jest.mock("@/lib/jquants-adapter", () => ({
  testConnection: jest.fn(),
}));

// Mock the generateMarketSummary function
jest.mock("@/lib/stock-analysis", () => ({
  generateMarketSummary: jest.fn(),
}));

describe("useRealDashboardData", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("initializes with loading state", () => {
    const { result } = renderHook(() => useRealDashboardData());
    
    expect(result.current.isLoading).toBe(true);
    expect(result.current.error).toBe(null);
    expect(result.current.connectionStatus).toBe(null);
    expect(result.current.marketSummary).toBe(null);
    expect(result.current.lastUpdated).toBe(null);
    expect(result.current.analysisResults).toEqual([]);
  });

  it("provides refresh function", () => {
    const { result } = renderHook(() => useRealDashboardData());
    
    expect(typeof result.current.actions.refresh).toBe("function");
  });

  it("handles successful connection test", async () => {
    const { testConnection } = require("@/lib/jquants-adapter");
    const { generateMarketSummary } = require("@/lib/stock-analysis");
    
    testConnection.mockResolvedValue({ success: true, message: "Connected" });
    generateMarketSummary.mockResolvedValue({
      analyzedSymbols: ["7203", "6758"],
      recommendations: { BUY: 2, SELL: 0 },
      topGainers: [],
      topLosers: [],
    });

    const { result } = renderHook(() => useRealDashboardData());
    
    await act(async () => {
      await result.current.actions.refresh();
    });

    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBe(null);
    expect(result.current.connectionStatus).toEqual({ success: true, message: "Connected" });
    expect(result.current.marketSummary).toBeDefined();
  });

  it("handles connection failure", async () => {
    const { testConnection } = require("@/lib/jquants-adapter");
    
    testConnection.mockResolvedValue({ success: false, message: "Connection failed" });

    const { result } = renderHook(() => useRealDashboardData());
    
    await act(async () => {
      await result.current.actions.refresh();
    });

    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBe("API接続失敗: Connection failed");
  });

  it("handles market summary generation failure", async () => {
    const { testConnection } = require("@/lib/jquants-adapter");
    const { generateMarketSummary } = require("@/lib/stock-analysis");
    
    testConnection.mockResolvedValue({ success: true, message: "Connected" });
    generateMarketSummary.mockResolvedValue(null);

    const { result } = renderHook(() => useRealDashboardData());
    
    await act(async () => {
      await result.current.actions.refresh();
    });

    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBe("市場サマリーの生成に失敗しました");
  });

  it("handles unexpected errors", async () => {
    const { testConnection } = require("@/lib/jquants-adapter");
    
    testConnection.mockRejectedValue(new Error("Unexpected error"));

    const { result } = renderHook(() => useRealDashboardData());
    
    await act(async () => {
      await result.current.actions.refresh();
    });

    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBe("Unexpected error");
  });

  it("updates lastUpdated timestamp on successful refresh", async () => {
    const { testConnection } = require("@/lib/jquants-adapter");
    const { generateMarketSummary } = require("@/lib/stock-analysis");
    
    testConnection.mockResolvedValue({ success: true, message: "Connected" });
    generateMarketSummary.mockResolvedValue({
      analyzedSymbols: ["7203"],
      recommendations: { BUY: 1 },
      topGainers: [],
      topLosers: [],
    });

    const { result } = renderHook(() => useRealDashboardData());
    
    await act(async () => {
      await result.current.actions.refresh();
    });

    expect(result.current.lastUpdated).toBeDefined();
    expect(new Date(result.current.lastUpdated!)).toBeInstanceOf(Date);
  });
});
