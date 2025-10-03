/**
 * データフェッチユーティリティのテスト
 */

// import { describe, it, expect, vi, beforeEach } from "vitest";
import { fetchJson, fetchMultiple, AppError } from "../fetcher";

// fetchのモック
global.fetch = vi.fn();

describe("fetcher utilities", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("fetchJson", () => {
    it("正常なレスポンスを処理する", async () => {
      const mockData = { test: "data" };
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        headers: {
          get: vi.fn().mockReturnValue("application/json"),
        },
        json: vi.fn().mockResolvedValueOnce(mockData),
      });

      const result = await fetchJson("/test-url");
      expect(result).toEqual(mockData);
    });

    it("HTTPエラーを適切に処理する", async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: "Not Found",
      });

      await expect(fetchJson("/test-url")).rejects.toThrow(AppError);
    });

    it("タイムアウトを適切に処理する", async () => {
      (global.fetch as any).mockImplementationOnce(() => 
        new Promise((_, reject) => 
          setTimeout(() => reject(new Error("timeout")), 100),
        ),
      );

      await expect(fetchJson("/test-url", { timeout: 50 })).rejects.toThrow();
    });

    it("AbortControllerでリクエストを中断する", async () => {
      const controller = new AbortController();
      controller.abort();

      await expect(fetchJson("/test-url", { signal: controller.signal })).rejects.toThrow(AppError);
    });

    it("リトライ機能を正しく動作させる", async () => {
      (global.fetch as any)
        .mockRejectedValueOnce(new Error("Network error"))
        .mockRejectedValueOnce(new Error("Network error"))
        .mockResolvedValueOnce({
          ok: true,
          headers: {
            get: vi.fn().mockReturnValue("application/json"),
          },
          json: vi.fn().mockResolvedValueOnce({ success: true }),
        });

      const result = await fetchJson("/test-url", { retries: 3 });
      expect(result).toEqual({ success: true });
      expect(global.fetch).toHaveBeenCalledTimes(3);
    });

    it("無効なContent-Typeでエラーを投げる", async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        headers: {
          get: vi.fn().mockReturnValue("text/html"),
        },
      });

      await expect(fetchJson("/test-url")).rejects.toThrow(AppError);
    });
  });

  describe("fetchMultiple", () => {
    it("複数のリクエストを並列処理する", async () => {
      (global.fetch as any)
        .mockResolvedValueOnce({
          ok: true,
          headers: { get: vi.fn().mockReturnValue("application/json") },
          json: vi.fn().mockResolvedValueOnce({ data1: "value1" }),
        })
        .mockResolvedValueOnce({
          ok: true,
          headers: { get: vi.fn().mockReturnValue("application/json") },
          json: vi.fn().mockResolvedValueOnce({ data2: "value2" }),
        });

      const result = await fetchMultiple({
        data1: "/url1",
        data2: "/url2",
      });

      expect(result).toEqual({
        data1: { data1: "value1" },
        data2: { data2: "value2" },
      });
    });

    it("一部のリクエストが失敗しても続行する", async () => {
      (global.fetch as any)
        .mockResolvedValueOnce({
          ok: true,
          headers: { get: vi.fn().mockReturnValue("application/json") },
          json: vi.fn().mockResolvedValueOnce({ data1: "value1" }),
        })
        .mockRejectedValueOnce(new Error("Network error"));

      const result = await fetchMultiple({
        data1: "/url1",
        data2: "/url2",
      });

      expect(result).toEqual({
        data1: { data1: "value1" },
      });
    });
  });

  describe("AppError", () => {
    it("適切なエラーメッセージとコードを持つ", () => {
      const error = new AppError("Test error", "TEST_ERROR", 500);
      expect(error.message).toBe("Test error");
      expect(error.code).toBe("TEST_ERROR");
      expect(error.status).toBe(500);
      expect(error.name).toBe("AppError");
    });
  });
});
