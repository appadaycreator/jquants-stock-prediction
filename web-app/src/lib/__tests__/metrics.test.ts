/**
 * metrics.ts のテスト
 */

import { calculatePerformanceMetrics, formatMetricValue, getMetricColor } from "../metrics";

describe("metrics", () => {
  describe("calculatePerformanceMetrics", () => {
    it("正常なデータでメトリクスを計算する", () => {
      const data = {
        predictions: [0.1, 0.2, 0.3],
        actual: [0.15, 0.25, 0.35],
        dates: ["2024-01-01", "2024-01-02", "2024-01-03"]
      };
      
      const result = calculatePerformanceMetrics(data);
      expect(result).toHaveProperty("accuracy");
      expect(result).toHaveProperty("precision");
      expect(result).toHaveProperty("recall");
      expect(result).toHaveProperty("f1Score");
    });

    it("空のデータを処理する", () => {
      const data = {
        predictions: [],
        actual: [],
        dates: []
      };
      
      const result = calculatePerformanceMetrics(data);
      expect(result.accuracy).toBe(0);
    });
  });

  describe("formatMetricValue", () => {
    it("パーセンテージをフォーマットする", () => {
      const result = formatMetricValue(0.8542, "percentage");
      expect(result).toContain("%");
    });

    it("数値をフォーマットする", () => {
      const result = formatMetricValue(0.8542, "number");
      expect(typeof result).toBe("string");
    });
  });

  describe("getMetricColor", () => {
    it("高い値に適切な色を返す", () => {
      const color = getMetricColor(0.9);
      expect(color).toBeDefined();
    });

    it("低い値に適切な色を返す", () => {
      const color = getMetricColor(0.1);
      expect(color).toBeDefined();
    });
  });
});
