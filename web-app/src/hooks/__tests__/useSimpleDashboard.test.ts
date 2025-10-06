import { renderHook, act, waitFor } from "@testing-library/react";
import { useSimpleDashboard } from "../useSimpleDashboard";

// モック設定
global.fetch = jest.fn();

const mockFetch = fetch as jest.MockedFunction<typeof fetch>;

describe("useSimpleDashboard", () => {
  beforeEach(() => {
    mockFetch.mockClear();
  });

  it("初期状態でローディングがtrueになる", () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        success: true,
        data: {
          lastUpdate: "2025-01-05T00:00:00Z",
          recommendations: [],
          portfolioSummary: {
            totalInvestment: 0,
            currentValue: 0,
            unrealizedPnL: 0,
            unrealizedPnLPercent: 0,
            bestPerformer: { symbol: "", symbolName: "", return: 0 },
            worstPerformer: { symbol: "", symbolName: "", return: 0 },
          },
          positions: [],
          marketStatus: { isOpen: false, nextOpen: "" },
        },
      }),
    } as Response);

    const { result } = renderHook(() => useSimpleDashboard());

    expect(result.current.loading).toBe(true);
    expect(result.current.data).toBeNull();
    expect(result.current.error).toBeNull();
  });

  it("データ取得成功時に適切な状態になる", async () => {
    const mockData = {
      lastUpdate: "2025-01-05T00:00:00Z",
      recommendations: [
        {
          id: "1",
          symbol: "7203",
          symbolName: "トヨタ自動車",
          action: "BUY",
          reason: "業績好調",
          confidence: 85,
          expectedReturn: 12.5,
          priority: "HIGH",
          timeframe: "3ヶ月",
        },
      ],
      portfolioSummary: {
        totalInvestment: 1000000,
        currentValue: 1050000,
        unrealizedPnL: 50000,
        unrealizedPnLPercent: 5.0,
        bestPerformer: { symbol: "7203", symbolName: "トヨタ自動車", return: 15.2 },
        worstPerformer: { symbol: "9984", symbolName: "ソフトバンクグループ", return: -12.8 },
      },
      positions: [],
      marketStatus: { isOpen: true, nextOpen: "" },
    };

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        success: true,
        data: mockData,
      }),
    } as Response);

    const { result } = renderHook(() => useSimpleDashboard());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toEqual(mockData);
    expect(result.current.error).toBeNull();
    expect(result.current.lastUpdate).toBe("2025-01-05T00:00:00Z");
  });

  it("データ取得失敗時にエラー状態になる", async () => {
    mockFetch.mockRejectedValueOnce(new Error("Network error"));

    const { result } = renderHook(() => useSimpleDashboard());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toBeNull();
    expect(result.current.error).toBe("Network error");
  });

  it("HTTPエラー時に適切なエラーメッセージが設定される", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
    } as Response);

    const { result } = renderHook(() => useSimpleDashboard());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.error).toBe("HTTP error! status: 500");
  });

  it("APIレスポンスが失敗時にエラー状態になる", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        success: false,
        error: { message: "API error" },
      }),
    } as Response);

    const { result } = renderHook(() => useSimpleDashboard());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.error).toBe("API error");
  });

  it("refreshDataが正常に動作する", async () => {
    const mockData = {
      lastUpdate: "2025-01-05T00:00:00Z",
      recommendations: [],
      portfolioSummary: {
        totalInvestment: 0,
        currentValue: 0,
        unrealizedPnL: 0,
        unrealizedPnLPercent: 0,
        bestPerformer: { symbol: "", symbolName: "", return: 0 },
        worstPerformer: { symbol: "", symbolName: "", return: 0 },
      },
      positions: [],
      marketStatus: { isOpen: false, nextOpen: "" },
    };

    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: true,
          data: mockData,
        }),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: true,
          data: { ...mockData, lastUpdate: "2025-01-05T01:00:00Z" },
        }),
      } as Response);

    const { result } = renderHook(() => useSimpleDashboard());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    await act(async () => {
      await result.current.refreshData();
    });

    expect(mockFetch).toHaveBeenCalledTimes(2);
    expect(result.current.lastUpdate).toBe("2025-01-05T01:00:00Z");
  });

  it("自動更新が30秒間隔で実行される", async () => {
    jest.useFakeTimers();

    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => ({
        success: true,
        data: {
          lastUpdate: "2025-01-05T00:00:00Z",
          recommendations: [],
          portfolioSummary: {
            totalInvestment: 0,
            currentValue: 0,
            unrealizedPnL: 0,
            unrealizedPnLPercent: 0,
            bestPerformer: { symbol: "", symbolName: "", return: 0 },
            worstPerformer: { symbol: "", symbolName: "", return: 0 },
          },
          positions: [],
          marketStatus: { isOpen: false, nextOpen: "" },
        },
      }),
    } as Response);

    const { result } = renderHook(() => useSimpleDashboard());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    // 初期呼び出し
    expect(mockFetch).toHaveBeenCalledTimes(1);

    // 30秒経過
    act(() => {
      jest.advanceTimersByTime(30000);
    });

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledTimes(2);
    });

    jest.useRealTimers();
  });
});
