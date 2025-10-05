/**
 * 新NISA枠管理機能のメインエクスポート
 * 統合されたAPIとユーティリティを提供
 */

export * from "./types";
export * from "./calculator";
export * from "./storage";

// 統合されたNISA管理クラス
export class NisaManager {
  private calculator: import("./calculator").NisaCalculator;
  private storage: import("./storage").NisaStorageManager;

  constructor() {
    this.calculator = new (require("./calculator").NisaCalculator)();
    this.storage = new (require("./storage").NisaStorageManager)();
  }

  /**
   * 初期化
   */
  async initialize(): Promise<boolean> {
    try {
      const data = await this.storage.loadData();
      if (data) {
        this.calculator = new (require("./calculator").NisaCalculator)(data.transactions);
      }
      return true;
    } catch (error) {
      console.error("NISA管理の初期化エラー:", error);
      return false;
    }
  }

  /**
   * 完全な計算結果を取得
   */
  async getCalculationResult(): Promise<import("./types").NisaCalculationResult | null> {
    try {
      const data = await this.storage.loadData();
      if (!data) {
        return null;
      }

      // 現在価格を設定（実際の実装では適切な価格取得APIを使用）
      for (const position of data.portfolio.positions) {
        this.calculator.setCurrentPrice(position.symbol, position.currentPrice);
      }

      return this.calculator.calculateAll();
    } catch (error) {
      console.error("計算結果取得エラー:", error);
      return null;
    }
  }

  /**
   * 取引を追加
   */
  async addTransaction(transaction: Omit<import("./types").NisaTransaction, "id" | "createdAt" | "updatedAt">): Promise<import("./types").ValidationResult> {
    try {
      // 計算機で検証
      const validation = this.calculator.validateTransaction(transaction);
      if (!validation.isValid) {
        return validation;
      }

      // ストレージに保存
      return await this.storage.addTransaction(transaction);
    } catch (error) {
      console.error("取引追加エラー:", error);
      return {
        isValid: false,
        errors: ["取引の追加に失敗しました"],
        warnings: [],
      };
    }
  }

  /**
   * データを保存
   */
  async saveData(data: import("./types").NisaData): Promise<boolean> {
    return await this.storage.saveData(data);
  }

  /**
   * データを読み込み
   */
  async loadData(): Promise<import("./types").NisaData | null> {
    return await this.storage.loadData();
  }
}
