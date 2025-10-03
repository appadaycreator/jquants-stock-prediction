/**
 * 評価指標計算ユーティリティのテスト
 */

// import { describe, it, expect } from "vitest";
import { mae, rmse, r2, mape, detectOverfitting, naiveBaseline, evaluateBaseline, compareModels } from "../metrics";

// describe("metrics utilities", () => {
  // describe("mae", () => {
    it("平均絶対誤差を正しく計算する", () => {
      const y = [1, 2, 3, 4, 5];
      const yhat = [1.1, 1.9, 3.1, 3.9, 5.1];
      const result = mae(y, yhat);
      expect(result).toBeCloseTo(0.1, 2);
    });

    it("配列の長さが異なる場合はエラーを投げる", () => {
      const y = [1, 2, 3];
      const yhat = [1, 2];
      expect(() => mae(y, yhat)).toThrow("配列の長さが一致しません");
    });
  });

  describe("rmse", () => {
    it("二乗平均平方根誤差を正しく計算する", () => {
      const y = [1, 2, 3, 4, 5];
      const yhat = [1.1, 1.9, 3.1, 3.9, 5.1];
      const result = rmse(y, yhat);
      expect(result).toBeCloseTo(0.1, 2);
    });
  });

  describe("r2", () => {
    it("決定係数を正しく計算する", () => {
      const y = [1, 2, 3, 4, 5];
      const yhat = [1, 2, 3, 4, 5];
      const result = r2(y, yhat);
      expect(result).toBe(1);
    });

    it("完全に異なる予測に対して負の値を返す", () => {
      const y = [1, 2, 3, 4, 5];
      const yhat = [5, 4, 3, 2, 1];
      const result = r2(y, yhat);
      expect(result).toBeLessThan(0);
    });

    it("定数系列に対して適切に処理する", () => {
      const y = [1, 1, 1, 1, 1];
      const yhat = [1, 1, 1, 1, 1];
      const result = r2(y, yhat);
      expect(result).toBe(1);
    });
  });

  describe("mape", () => {
    it("平均絶対パーセント誤差を正しく計算する", () => {
      const y = [100, 200, 300];
      const yhat = [110, 190, 310];
      const result = mape(y, yhat);
      expect(result).toBeCloseTo(3.33, 1);
    });

    it("ゼロ除算を避ける", () => {
      const y = [0, 100, 200];
      const yhat = [10, 110, 190];
      const result = mape(y, yhat);
      expect(result).toBeFinite();
    });
  });

  describe("detectOverfitting", () => {
    it("高リスク（R² > 0.99）を検出する", () => {
      const result = detectOverfitting(0.95, 0.995);
      expect(result.isOverfitting).toBe(true);
      expect(result.riskLevel).toBe("高");
      expect(result.message).toContain("高リスク");
    });

    it("中リスク（R² > 0.95）を検出する", () => {
      const result = detectOverfitting(0.90, 0.96);
      expect(result.isOverfitting).toBe(true);
      expect(result.riskLevel).toBe("中");
      expect(result.message).toContain("中リスク");
    });

    it("過学習疑いを検出する", () => {
      const result = detectOverfitting(0.95, 0.80);
      expect(result.isOverfitting).toBe(true);
      expect(result.riskLevel).toBe("中");
      expect(result.message).toContain("過学習疑い");
    });

    it("低リスクを正しく判定する", () => {
      const result = detectOverfitting(0.85, 0.82);
      expect(result.isOverfitting).toBe(false);
      expect(result.riskLevel).toBe("低");
      expect(result.message).toBe("低リスク");
    });
  });

  describe("naiveBaseline", () => {
    it("前日終値を維持する予測を生成する", () => {
      const y = [100, 110, 120, 130, 140];
      const result = naiveBaseline(y);
      expect(result).toEqual([100, 100, 110, 120, 130]);
    });

    it("データが少ない場合はそのまま返す", () => {
      const y = [100];
      const result = naiveBaseline(y);
      expect(result).toEqual([100]);
    });
  });

  describe("evaluateBaseline", () => {
    it("ベースライン性能を正しく評価する", () => {
      const y = [100, 110, 120, 130, 140];
      const result = evaluateBaseline(y);
      
      expect(result).toHaveProperty("mae");
      expect(result).toHaveProperty("rmse");
      expect(result).toHaveProperty("r2");
      expect(result).toHaveProperty("mape");
      expect(result.mae).toBeGreaterThan(0);
      expect(result.rmse).toBeGreaterThan(0);
    });
  });

  describe("compareModels", () => {
    it("モデル性能を正しく比較する", () => {
      const modelMetrics = { mae: 10, rmse: 15, r2: 0.8 };
      const baselineMetrics = { mae: 20, rmse: 25, r2: 0.6 };
      
      const result = compareModels(modelMetrics, baselineMetrics);
      
      expect(result.isBetter).toBe(true);
      expect(result.maeImprovement).toBeGreaterThan(0);
      expect(result.rmseImprovement).toBeGreaterThan(0);
      expect(result.r2Improvement).toBeGreaterThan(0);
    });

    it("ベースラインより劣るモデルを正しく判定する", () => {
      const modelMetrics = { mae: 30, rmse: 35, r2: 0.4 };
      const baselineMetrics = { mae: 20, rmse: 25, r2: 0.6 };
      
      const result = compareModels(modelMetrics, baselineMetrics);
      
      expect(result.isBetter).toBe(false);
      expect(result.maeImprovement).toBeLessThan(0);
      expect(result.rmseImprovement).toBeLessThan(0);
      expect(result.r2Improvement).toBeLessThan(0);
    });
  });
});
