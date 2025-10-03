import { renderHook, act } from "@testing-library/react";
import { useRealDashboardData } from "../useRealDashboardData";

// Mock the fetchJson function
jest.mock("@/lib/fetcher", () => ({
  fetchJson: jest.fn(),
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
    const mockData = {
      summary: {
        totalStocks: 100,
        analyzedStocks: 50,
        lastUpdated: "2024-01-01T00:00:00Z",
      },
      predictions: [
        {
          symbol: "7203",
          name: "トヨタ自動車",
          recommendation: "BUY",
          confidence: 0.8,
        },
      ],
    };

    const { fetchJson } = require("@/lib/fetcher");
    fetchJson.mockResolvedValue(mockData);

    const { result } = renderHook(() => useRealDashboardData());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(result.current.marketSummary).toEqual(mockData);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBe(null);
  });

  it("handles API errors gracefully", async () => {
    const { fetchJson } = require("@/lib/fetcher");
    fetchJson.mockRejectedValue(new Error("API Error"));

    const { result } = renderHook(() => useRealDashboardData());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(result.current.marketSummary).toBeNull();
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBe("API Error");
  });

  it("refetches data when refetch is called", async () => {
    const { fetchJson } = require("@/lib/fetcher");
    fetchJson.mockResolvedValue({ data: "test" });

    const { result } = renderHook(() => useRealDashboardData());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(fetchJson).toHaveBeenCalledTimes(1);

    await act(async () => {
      result.current.actions.refresh();
    });

    expect(fetchJson).toHaveBeenCalledTimes(2);
  });

  it("sets loading state during fetch", async () => {
    const { fetchJson } = require("@/lib/fetcher");
    let resolvePromise;
    const promise = new Promise(resolve => {
      resolvePromise = resolve;
    });
    fetchJson.mockReturnValue(promise);

    const { result } = renderHook(() => useRealDashboardData());

    expect(result.current.isLoading).toBe(true);

    act(() => {
      resolvePromise({ data: "test" });
    });

    await act(async () => {
      await promise;
    });

    expect(result.current.isLoading).toBe(false);
  });
});