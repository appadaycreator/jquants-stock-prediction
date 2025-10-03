import { z } from "zod";
import { StockData, PredictionPoint, DashboardSummary } from "../schema";

describe("schema validation", () => {
  describe("stockDataSchema", () => {
    it("validates correct stock data", () => {
      const validStockData = {
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

      expect(() => StockData.parse(validStockData)).not.toThrow();
    });

    it("rejects invalid stock data", () => {
      const invalidStockData = {
        symbol: "",
        name: "",
        price: -100,
        change: "invalid",
      };

      expect(() => StockData.parse(invalidStockData)).toThrow();
    });
  });

  describe("predictionPoint", () => {
    it("validates correct prediction data", () => {
      const validPrediction = {
        date: "2024-01-01",
        symbol: "7203",
        y_true: 2500,
        y_pred: 2600,
      };

      expect(() => PredictionPoint.parse(validPrediction)).not.toThrow();
    });

    it("rejects invalid prediction data", () => {
      const invalidPrediction = {
        date: "",
        symbol: "",
        y_true: "invalid",
        y_pred: "invalid",
      };

      expect(() => PredictionPoint.parse(invalidPrediction)).toThrow();
    });
  });

  describe("dashboardSummary", () => {
    it("validates correct dashboard data", () => {
      const validDashboardData = {
        total_stocks: 100,
        total_predictions: 50,
        last_updated: "2024-01-01T00:00:00Z",
        model_performance: {
          best_model: "RandomForest",
          accuracy: 0.85,
          mae: 100,
          rmse: 150,
        },
      };

      expect(() => DashboardSummary.parse(validDashboardData)).not.toThrow();
    });

    it("rejects invalid dashboard data", () => {
      const invalidDashboardData = {
        total_stocks: -1, // Invalid negative number
        total_predictions: "invalid",
      };

      expect(() => DashboardSummary.parse(invalidDashboardData)).toThrow();
    });
  });
});