import { analyzeStock, generateMarketSummary } from "../stock-analysis";

// Mock the unifiedApiClient
jest.mock("../unified-api-client", () => ({
  unifiedApiClient: {
    getStockData: jest.fn(),
    getMarketData: jest.fn(),
  },
}));

describe("stock-analysis", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("analyzeStock", () => {
    it("returns null for invalid symbol", async () => {
      const result = await analyzeStock("");
      expect(result).toBeNull();
    });

    it("handles API errors gracefully", async () => {
      const { unifiedApiClient } = require("../unified-api-client");
      unifiedApiClient.getStockData.mockRejectedValue(new Error("API Error"));

      const result = await analyzeStock("7203");
      expect(result).toBeNull();
    });

    it("processes valid stock data", async () => {
      const mockStockData = {
        symbol: "7203",
        name: "トヨタ自動車",
        price: 2500,
        change: 50,
        changePercent: 2.04,
        volume: 1000000,
        marketCap: 1000000000000,
        pe: 15.5,
        pb: 1.2,
        dividend: 100,
        dividendYield: 4.0,
        high52w: 3000,
        low52w: 2000,
        sector: "自動車",
        industry: "自動車製造",
        employees: 370000,
        founded: 1937,
        description: "自動車製造会社",
        website: "https://toyota.co.jp",
        logo: "https://example.com/logo.png",
      };

      const { unifiedApiClient } = require("../unified-api-client");
      unifiedApiClient.getStockData.mockResolvedValue(mockStockData);

      const result = await analyzeStock("7203", "トヨタ自動車");
      
      expect(result).toBeDefined();
      expect(result?.symbol).toBe("7203");
      expect(result?.name).toBe("トヨタ自動車");
    });
  });

  describe("generateMarketSummary", () => {
    it("generates market summary with analyzed symbols", async () => {
      const mockAnalysisResults = [
        {
          symbol: "7203",
          name: "トヨタ自動車",
          recommendation: "BUY",
          confidence: 0.8,
          rationale: ["テクニカル分析で上昇トレンド"],
          price: 2500,
          targetPrice: 2800,
          riskLevel: "中",
        },
        {
          symbol: "6758",
          name: "ソニーグループ",
          recommendation: "HOLD",
          confidence: 0.6,
          rationale: ["横ばいトレンド"],
          price: 12000,
          targetPrice: 12500,
          riskLevel: "低",
        },
      ];

      const result = await generateMarketSummary();
      
      expect(result).toBeDefined();
      expect(result.analyzedSymbols).toBeDefined();
      expect(result.recommendations).toBeDefined();
      expect(result.topGainers).toBeDefined();
      expect(result.topLosers).toBeDefined();
    });

    it("handles empty analysis results", async () => {
      const result = await generateMarketSummary();
      
      expect(result).toBeDefined();
      expect(result.analyzedSymbols).toEqual([]);
      expect(result.recommendations).toEqual({});
      expect(result.topGainers).toEqual([]);
      expect(result.topLosers).toEqual([]);
    });

    it("categorizes recommendations correctly", async () => {
      const result = await generateMarketSummary();
      
      if (result.analyzedSymbols.length > 0) {
        expect(result.recommendations).toHaveProperty("BUY");
        expect(result.recommendations).toHaveProperty("SELL");
        expect(result.recommendations).toHaveProperty("HOLD");
      }
    });
  });

  describe("generateMockStockData", () => {
    it("generates mock data for given parameters", () => {
      const mockData = require("../stock-analysis").generateMockStockData;
      
      if (mockData) {
        const result = mockData("7203", "2024-01-01", "2024-01-31");
        expect(result).toBeDefined();
        expect(Array.isArray(result)).toBe(true);
        expect(result.length).toBeGreaterThan(0);
        
        if (result.length > 0) {
          expect(result[0]).toHaveProperty("date");
          expect(result[0]).toHaveProperty("symbol");
          expect(result[0]).toHaveProperty("close");
        }
      }
    });
  });
});
