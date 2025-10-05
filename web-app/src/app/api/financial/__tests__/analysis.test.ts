/**
 * 財務指標分析APIのテスト
 */

import { GET } from "../analysis/[symbol]/route";
import { NextRequest } from "next/server";

// モックデータ
const mockRequest = {
  url: "http://localhost:3000/api/financial/analysis/TEST",
} as NextRequest;

describe("/api/financial/analysis/[symbol]", () => {
  it("有効な銘柄コードで財務指標を取得する", async () => {
    const response = await GET(mockRequest, { params: { symbol: "TEST" } });
    const data = await response.json();
    
    expect(response.status).toBe(200);
    expect(data.success).toBe(true);
    expect(data.data).toBeDefined();
    expect(data.data.metrics).toBeDefined();
    expect(data.data.healthScore).toBeDefined();
    expect(data.data.industryComparison).toBeDefined();
    expect(data.data.historicalAnalysis).toBeDefined();
  });

  it("無効な銘柄コードでエラーを返す", async () => {
    const response = await GET(mockRequest, { params: { symbol: "" } });
    const data = await response.json();
    
    expect(response.status).toBe(400);
    expect(data.success).toBe(false);
    expect(data.error.code).toBe("VALIDATION_ERROR");
    expect(data.error.message).toBe("銘柄コードが必要です");
  });

  it("メタデータを正しく返す", async () => {
    const response = await GET(mockRequest, { params: { symbol: "TEST" } });
    const data = await response.json();
    
    expect(data.metadata).toBeDefined();
    expect(data.metadata.timestamp).toBeDefined();
    expect(data.metadata.version).toBe("1.0.0");
    expect(data.metadata.calculationTime).toBeDefined();
  });

  it("レスポンス形式を正しく返す", async () => {
    const response = await GET(mockRequest, { params: { symbol: "TEST" } });
    const data = await response.json();
    
    expect(data).toHaveProperty("success");
    expect(data).toHaveProperty("data");
    expect(data).toHaveProperty("metadata");
    
    if (data.success) {
      expect(data.data).toHaveProperty("metrics");
      expect(data.data).toHaveProperty("healthScore");
      expect(data.data).toHaveProperty("industryComparison");
      expect(data.data).toHaveProperty("historicalAnalysis");
    }
  });
});
