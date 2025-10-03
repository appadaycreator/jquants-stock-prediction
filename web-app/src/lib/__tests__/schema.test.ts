import { z } from "zod";
import { StockData, PredictionPoint, DashboardSummary } from "../schema";
describe("schema validation", () => {
  describe("stockDataSchema", () => {
    it("validates correct stock data", () => {
      const validStockData = {
        date: "2024-01-01",
        close: 2500,
        volume: 1000000,
        sma_5: 2450,
        sma_10: 2400,
        sma_25: 2350,
        sma_50: 2300,
        predicted: 2600,
      };
      expect(() => StockData.parse(validStockData)).not.toThrow();
    });
    it("rejects invalid stock data", () => {
      const invalidStockData = {
        date: "",
        close: -100,
        volume: "invalid",
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