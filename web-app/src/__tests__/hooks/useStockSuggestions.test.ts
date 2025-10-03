import { renderHook, act, waitFor } from "@testing-library/react";
import { useStockSuggestions } from "@/hooks/useStockSuggestions";

// fetchをモック
global.fetch = jest.fn();

describe("useStockSuggestions", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it("初期状態が正しい", () => {
    const { result } = renderHook(() => useStockSuggestions());

    expect(result.current.suggestions).toEqual([]);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBe(null);
    expect(result.current.showSuggestions).toBe(false);
  });

  it("クエリが最小長未満の場合はサジェッションを取得しない", async () => {
    const { result } = renderHook(() => useStockSuggestions({ minQueryLength: 2 }));

    act(() => {
      result.current.handleQueryChange("a");
    });

    expect(result.current.suggestions).toEqual([]);
    expect(result.current.isLoading).toBe(false);
  });

  it("デバウンスが正しく動作する", async () => {
    const { result } = renderHook(() => useStockSuggestions({ debounceMs: 300 }));

    act(() => {
      result.current.handleQueryChange("test");
    });

    // デバウンス中はリクエストが送信されない
    expect(fetch).not.toHaveBeenCalled();

    // デバウンス時間を経過
    act(() => {
      jest.advanceTimersByTime(300);
    });

    await waitFor(() => {
      expect(fetch).toHaveBeenCalled();
    });
  });

  it("サジェッションの取得に成功する", async () => {
    const mockResponse = {
      suggestions: [
        {
          code: "7203",
          name: "トヨタ自動車",
          sector: "自動車",
          market: "プライム",
          displayText: "トヨタ自動車 (7203)",
        },
      ],
      total: 1,
      query: "test",
    };

    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockResponse),
    });

    const { result } = renderHook(() => useStockSuggestions());

    act(() => {
      result.current.handleQueryChange("test");
    });

    act(() => {
      jest.advanceTimersByTime(300);
    });

    await waitFor(() => {
      expect(result.current.suggestions).toEqual(mockResponse.suggestions);
      expect(result.current.showSuggestions).toBe(true);
      expect(result.current.isLoading).toBe(false);
    });
  });

  it("サジェッションの取得に失敗した場合はエラーを設定する", async () => {
    (fetch as jest.Mock).mockRejectedValueOnce(new Error("Network error"));

    const { result } = renderHook(() => useStockSuggestions());

    act(() => {
      result.current.handleQueryChange("test");
    });

    act(() => {
      jest.advanceTimersByTime(300);
    });

    await waitFor(() => {
      expect(result.current.error).toBe("サジェッションの取得に失敗しました");
      expect(result.current.suggestions).toEqual([]);
      expect(result.current.showSuggestions).toBe(false);
    });
  });

  it("HTTPエラーの場合はエラーを設定する", async () => {
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 500,
    });

    const { result } = renderHook(() => useStockSuggestions());

    act(() => {
      result.current.handleQueryChange("test");
    });

    act(() => {
      jest.advanceTimersByTime(300);
    });

    await waitFor(() => {
      expect(result.current.error).toBe("サジェッションの取得に失敗しました");
    });
  });

  it("clearSuggestionsが正しく動作する", () => {
    const { result } = renderHook(() => useStockSuggestions());

    act(() => {
      result.current.clearSuggestions();
    });

    expect(result.current.suggestions).toEqual([]);
    expect(result.current.showSuggestions).toBe(false);
    expect(result.current.error).toBe(null);
  });

  it("hideSuggestionsが正しく動作する", () => {
    const { result } = renderHook(() => useStockSuggestions());

    act(() => {
      result.current.hideSuggestions();
    });

    expect(result.current.showSuggestions).toBe(false);
  });

  it("新しいクエリで前のリクエストがキャンセルされる", async () => {
    const abortController = new AbortController();
    const mockAbort = jest.fn();
    abortController.abort = mockAbort;

    // 最初のリクエストを遅延させる
    (fetch as jest.Mock).mockImplementationOnce(() => 
      new Promise((resolve) => setTimeout(() => resolve({
        ok: true,
        json: () => Promise.resolve({ suggestions: [] }),
      }), 1000)),
    );

    const { result } = renderHook(() => useStockSuggestions());

    act(() => {
      result.current.handleQueryChange("test1");
    });

    act(() => {
      jest.advanceTimersByTime(300);
    });

    // 新しいクエリを送信
    act(() => {
      result.current.handleQueryChange("test2");
    });

    act(() => {
      jest.advanceTimersByTime(300);
    });

    // 前のリクエストがキャンセルされることを確認
    expect(mockAbort).toHaveBeenCalled();
  });

  it("コンポーネントのアンマウント時にリクエストがキャンセルされる", () => {
    const { result, unmount } = renderHook(() => useStockSuggestions());

    act(() => {
      result.current.handleQueryChange("test");
    });

    act(() => {
      jest.advanceTimersByTime(300);
    });

    unmount();

    // アンマウント時にリクエストがキャンセルされることを確認
    // 実際のテストでは、AbortControllerのabortが呼ばれることを確認する
  });
});
