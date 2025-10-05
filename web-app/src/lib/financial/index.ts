/**
 * 財務指標分析機能のメインエクスポート
 * 統合されたAPIとユーティリティを提供
 */

export * from "./types";
export * from "./calculator";

// 統合された財務分析管理クラス
export class FinancialAnalysisManager {
  private calculator: import("./calculator").FinancialCalculator;

  constructor() {
    this.calculator = new (require("./calculator").FinancialCalculator)();
  }

  /**
   * 財務指標を計算
   */
  async calculateFinancialMetrics(data: import("./types").FinancialData): Promise<import("./types").FinancialCalculationResult> {
    try {
      // データの妥当性を検証
      const validation = this.calculator.validateData(data);
      if (!validation.isValid) {
        throw new Error(`データ検証エラー: ${validation.errors.join(", ")}`);
      }

      // 財務指標を計算
      return this.calculator.calculateAll(data);
    } catch (error) {
      console.error("財務指標計算エラー:", error);
      throw error;
    }
  }

  /**
   * 業界比較分析を実行
   */
  async calculateIndustryComparison(
    data: import("./types").FinancialData,
    metrics: import("./types").FinancialMetrics,
  ): Promise<import("./types").IndustryComparison> {
    try {
      return this.calculator.calculateIndustryComparison(data, metrics);
    } catch (error) {
      console.error("業界比較分析エラー:", error);
      throw error;
    }
  }

  /**
   * 時系列分析を実行
   */
  async calculateHistoricalAnalysis(symbol: string): Promise<import("./types").HistoricalAnalysis> {
    try {
      return this.calculator.calculateHistoricalAnalysis(symbol);
    } catch (error) {
      console.error("時系列分析エラー:", error);
      throw error;
    }
  }

  /**
   * 財務健全性スコアを計算
   */
  async calculateHealthScore(metrics: import("./types").FinancialMetrics): Promise<import("./types").FinancialHealthScore> {
    try {
      return this.calculator.calculateHealthScore(metrics);
    } catch (error) {
      console.error("財務健全性スコア計算エラー:", error);
      throw error;
    }
  }
}
