import { renderHook, act } from "@testing-library/react";
import { useRealDashboardData } from "../useRealDashboardData";

// Mock the unifiedApiClient and stock-analysis functions
jest.mock("@/lib/unified-api-client", () => ({
  testConnection: jest.fn(),
}));
jest.mock("@/lib/stock-analysis", () => ({
  generateMarketSummary: jest.fn(),
}));

describe("useRealDashboardData", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("initializes with correct default values", () => {
    const { result } = renderHook(() => useRealDashboardData());
    
    expect(result.current.marketSummary).toBeNull();
    expect(result.current.isLoading).toBe(true);
    expect(result.current.error).toBe(null);
    expect(typeof result.current.actions.refresh).toBe("function");
  });

  it("handles successful data fetch", async () => {
    const { testConnection } = require("@/lib/unified-api-client");
    const { generateMarketSummary } = require("@/lib/stock-analysis");

    testConnection.mockResolvedValue({ success: true, message: "Connected" });
    const mockData = {
      analyzedSymbols: 15,
      recommendations: { BUY: 10, HOLD: 5, SELL: 2 },
      topGainers: [],
      topLosers: [],
      totalSymbols: 15,
      lastUpdated: "2024-01-01T00:00:00Z",
    };
    generateMarketSummary.mockResolvedValue(mockData);

    const { result } = renderHook(() => useRealDashboardData());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(result.current.marketSummary).toEqual(mockData);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBe(null);
  });

  it("handles API errors gracefully", async () => {
    const { testConnection } = require("@/lib/unified-api-client");
    const { generateMarketSummary } = require("@/lib/stock-analysis");

    testConnection.mockResolvedValue({ success: true, message: "Connected" });
    generateMarketSummary.mockRejectedValue(new Error("API Error"));

    const { result } = renderHook(() => useRealDashboardData());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(result.current.marketSummary).toBeNull();
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBe("API Error");
  });

  it("refetches data when refetch is called", async () => {
    const { testConnection } = require("@/lib/unified-api-client");
    const { generateMarketSummary } = require("@/lib/stock-analysis");

    testConnection.mockResolvedValue({ success: true, message: "Connected" });
    generateMarketSummary.mockResolvedValue({
      analyzedSymbols: 15,
      recommendations: { BUY: 10, HOLD: 5, SELL: 2 },
      topGainers: [],
      topLosers: [],
      totalSymbols: 15,
      lastUpdated: "2024-01-01T00:00:00Z",
    });

    const { result } = renderHook(() => useRealDashboardData());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(generateMarketSummary).toHaveBeenCalledTimes(1);

    await act(async () => {
      result.current.actions.refresh();
    });

    expect(generateMarketSummary).toHaveBeenCalledTimes(2);
  });

  it("sets loading state during fetch", async () => {
    const { testConnection } = require("@/lib/unified-api-client");
    const { generateMarketSummary } = require("@/lib/stock-analysis");

    testConnection.mockResolvedValue({ success: true, message: "Connected" });
    let resolvePromise;
    const promise = new Promise(resolve => {
      resolvePromise = resolve;
    });
    generateMarketSummary.mockReturnValue(promise);

    const { result } = renderHook(() => useRealDashboardData());

    expect(result.current.isLoading).toBe(true);

    await act(async () => {
      resolvePromise({
        analyzedSymbols: 15,
        recommendations: { BUY: 10, HOLD: 5, SELL: 2 },
        topGainers: [],
        topLosers: [],
        totalSymbols: 15,
        lastUpdated: "2024-01-01T00:00:00Z",
      });
      await promise;
    });

    expect(result.current.isLoading).toBe(false);
  });
});