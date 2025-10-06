import { NextRequest } from "next/server";
import { GET, POST } from "../route";

// モック設定
jest.mock("next/server", () => ({
  NextRequest: jest.fn(),
  NextResponse: {
    json: jest.fn((data, options) => ({
      json: () => Promise.resolve(data),
      status: options?.status || 200,
    })),
  },
}));

describe("/api/simple-dashboard", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("GET", () => {
    it("シンプルダッシュボードデータを正常に取得できる", async () => {
      const mockRequest = {
        url: "http://localhost:3000/api/simple-dashboard",
      } as NextRequest;

      const response = await GET(mockRequest);
      const responseData = await response.json();

      expect(response.status).toBe(200);
      expect(responseData.success).toBe(true);
      expect(responseData.data).toBeDefined();
      expect(responseData.data.recommendations).toHaveLength(3);
      expect(responseData.data.portfolioSummary).toBeDefined();
      expect(responseData.data.positions).toBeDefined();
      expect(responseData.data.marketStatus).toBeDefined();
    });

    it("リフレッシュパラメータが正しく処理される", async () => {
      const mockRequest = {
        url: "http://localhost:3000/api/simple-dashboard?refresh=true",
      } as NextRequest;

      const response = await GET(mockRequest);
      const responseData = await response.json();

      expect(response.status).toBe(200);
      expect(responseData.success).toBe(true);
    });

    it("エラー時に適切なレスポンスを返す", async () => {
      // エラーを強制的に発生させる
      const originalConsoleError = console.error;
      console.error = jest.fn();

      const mockRequest = {
        url: "invalid-url",
      } as NextRequest;

      const response = await GET(mockRequest);
      const responseData = await response.json();

      expect(response.status).toBe(500);
      expect(responseData.success).toBe(false);
      expect(responseData.error).toBeDefined();

      console.error = originalConsoleError;
    });
  });

  describe("POST", () => {
    it("データ更新を正常に実行できる", async () => {
      const mockRequest = {
        json: jest.fn().mockResolvedValue({ forceRefresh: true }),
      } as unknown as NextRequest;

      const response = await POST(mockRequest);
      const responseData = await response.json();

      expect(response.status).toBe(200);
      expect(responseData.success).toBe(true);
      expect(responseData.message).toBe("データを更新しました");
    });

    it("エラー時に適切なレスポンスを返す", async () => {
      const originalConsoleError = console.error;
      console.error = jest.fn();

      const mockRequest = {
        json: jest.fn().mockRejectedValue(new Error("JSON parse error")),
      } as unknown as NextRequest;

      const response = await POST(mockRequest);
      const responseData = await response.json();

      expect(response.status).toBe(500);
      expect(responseData.success).toBe(false);
      expect(responseData.error).toBeDefined();

      console.error = originalConsoleError;
    });
  });
});
