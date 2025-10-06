/**
 * 新NISA枠管理機能の計算ロジックテスト
 */

import { NisaCalculator } from "../calculator";
import { NisaTransaction, QuotaType, TransactionType } from "../types";

describe("NisaCalculator", () => {
  let calculator: NisaCalculator;

  beforeEach(() => {
    calculator = new NisaCalculator();
  });

  describe("投資枠利用状況の計算", () => {
    it("空の取引履歴で初期状態を返す", () => {
      const status = calculator.calculateQuotaStatus();
      
      expect(status.growthInvestment.usedAmount).toBe(0);
      expect(status.growthInvestment.availableAmount).toBe(2_400_000);
      expect(status.growthInvestment.utilizationRate).toBe(0);
      
      expect(status.accumulationInvestment.usedAmount).toBe(0);
      expect(status.accumulationInvestment.availableAmount).toBe(400_000);
      expect(status.accumulationInvestment.utilizationRate).toBe(0);
    });

    it("成長投資枠の買い取引で利用状況を更新", () => {
      const transaction: NisaTransaction = {
        id: "test-1",
        type: "BUY",
        symbol: "7203",
        symbolName: "トヨタ自動車",
        quantity: 100,
        price: 2500,
        amount: 250_000,
        quotaType: "GROWTH",
        transactionDate: "2024-01-15",
        createdAt: "2024-01-15T10:00:00Z",
        updatedAt: "2024-01-15T10:00:00Z",
      };

      calculator.addTransaction(transaction);
      const status = calculator.calculateQuotaStatus();

      expect(status.growthInvestment.usedAmount).toBe(250_000);
      expect(status.growthInvestment.availableAmount).toBe(2_150_000);
      expect(status.growthInvestment.utilizationRate).toBeCloseTo(10.42, 2);
    });

    it("つみたて投資枠の買い取引で利用状況を更新", () => {
      const transaction: NisaTransaction = {
        id: "test-2",
        type: "BUY",
        symbol: "6758",
        symbolName: "ソニーグループ",
        quantity: 50,
        price: 12000,
        amount: 600_000,
        quotaType: "ACCUMULATION",
        transactionDate: "2024-01-15",
        createdAt: "2024-01-15T10:00:00Z",
        updatedAt: "2024-01-15T10:00:00Z",
      };

      calculator.addTransaction(transaction);
      const status = calculator.calculateQuotaStatus();

      expect(status.accumulationInvestment.usedAmount).toBe(600_000);
      expect(status.accumulationInvestment.availableAmount).toBe(-200_000); // 枠を超過
      expect(status.accumulationInvestment.utilizationRate).toBe(150);
    });

    it("売り取引で利用状況を更新", () => {
      // まず買い取引を追加
      const buyTransaction: NisaTransaction = {
        id: "test-3",
        type: "BUY",
        symbol: "7203",
        symbolName: "トヨタ自動車",
        quantity: 100,
        price: 2500,
        amount: 250_000,
        quotaType: "GROWTH",
        transactionDate: "2024-01-15",
        createdAt: "2024-01-15T10:00:00Z",
        updatedAt: "2024-01-15T10:00:00Z",
      };

      calculator.addTransaction(buyTransaction);

      // 売り取引を追加
      const sellTransaction: NisaTransaction = {
        id: "test-4",
        type: "SELL",
        symbol: "7203",
        symbolName: "トヨタ自動車",
        quantity: 50,
        price: 2600,
        amount: 130_000,
        quotaType: "GROWTH",
        transactionDate: "2024-01-20",
        profitLoss: 5_000,
        taxFreeAmount: 130_000,
        createdAt: "2024-01-20T10:00:00Z",
        updatedAt: "2024-01-20T10:00:00Z",
      };

      calculator.addTransaction(sellTransaction);
      const status = calculator.calculateQuotaStatus();

      expect(status.growthInvestment.usedAmount).toBe(120_000); // 250_000 - 130_000
      expect(status.growthInvestment.availableAmount).toBe(2_280_000);
      expect(status.quotaReuse.growthAvailable).toBe(130_000);
    });
  });

  describe("ポートフォリオの計算", () => {
    it("空のポートフォリオを返す", () => {
      const portfolio = calculator.calculatePortfolio();
      
      expect(portfolio.positions).toHaveLength(0);
      expect(portfolio.totalValue).toBe(0);
      expect(portfolio.totalCost).toBe(0);
      expect(portfolio.unrealizedProfitLoss).toBe(0);
    });

    it("買い取引のみのポートフォリオを計算", () => {
      const transaction: NisaTransaction = {
        id: "test-5",
        type: "BUY",
        symbol: "7203",
        symbolName: "トヨタ自動車",
        quantity: 100,
        price: 2500,
        amount: 250_000,
        quotaType: "GROWTH",
        transactionDate: "2024-01-15",
        createdAt: "2024-01-15T10:00:00Z",
        updatedAt: "2024-01-15T10:00:00Z",
      };

      calculator.addTransaction(transaction);
      calculator.setCurrentPrice("7203", 2600);
      
      const portfolio = calculator.calculatePortfolio();

      expect(portfolio.positions).toHaveLength(1);
      expect(portfolio.positions[0].symbol).toBe("7203");
      expect(portfolio.positions[0].quantity).toBe(100);
      expect(portfolio.positions[0].cost).toBe(250_000);
      expect(portfolio.positions[0].currentValue).toBe(260_000);
      expect(portfolio.positions[0].unrealizedProfitLoss).toBe(10_000);
      expect(portfolio.totalCost).toBe(250_000);
      expect(portfolio.totalValue).toBe(260_000);
      expect(portfolio.unrealizedProfitLoss).toBe(10_000);
    });
  });

  describe("取引の妥当性検証", () => {
    it("有効な取引を検証", () => {
      const transaction = {
        type: "BUY" as TransactionType,
        symbol: "7203",
        symbolName: "トヨタ自動車",
        quantity: 100,
        price: 2500,
        amount: 250_000,
        quotaType: "GROWTH" as QuotaType,
        transactionDate: "2024-01-15",
      };

      const validation = calculator.validateTransaction(transaction);
      expect(validation.isValid).toBe(true);
      expect(validation.errors).toHaveLength(0);
    });

    it("無効な取引を検証", () => {
      const transaction = {
        type: "BUY" as TransactionType,
        symbol: "",
        symbolName: "",
        quantity: 0,
        price: -100,
        amount: 0,
        quotaType: "INVALID" as any,
        transactionDate: "2024-01-15",
      };

      const validation = calculator.validateTransaction(transaction);
      expect(validation.isValid).toBe(false);
      expect(validation.errors.length).toBeGreaterThan(0);
    });

    it("投資枠超過の取引を検証", () => {
      // まず大きな取引を追加して枠を埋める
      const largeTransaction: NisaTransaction = {
        id: "test-6",
        type: "BUY",
        symbol: "7203",
        symbolName: "トヨタ自動車",
        quantity: 1000,
        price: 2500,
        amount: 2_500_000, // 枠を超過
        quotaType: "GROWTH",
        transactionDate: "2024-01-15",
        createdAt: "2024-01-15T10:00:00Z",
        updatedAt: "2024-01-15T10:00:00Z",
      };

      calculator.addTransaction(largeTransaction);

      const transaction = {
        type: "BUY" as TransactionType,
        symbol: "6758",
        symbolName: "ソニーグループ",
        quantity: 100,
        price: 10000,
        amount: 1_000_000,
        quotaType: "GROWTH" as QuotaType,
        transactionDate: "2024-01-15",
      };

      const validation = calculator.validateTransaction(transaction);
      expect(validation.isValid).toBe(false);
      expect(validation.errors.some(error => error.includes("利用可能額を超えています"))).toBe(true);
    });
  });

  describe("最適化提案の生成", () => {
    it("低利用率での最適化提案", () => {
      const optimization = calculator.calculateOptimization();
      
      expect(optimization.recommendations.growthQuota.priority).toBe("HIGH");
      expect(optimization.recommendations.accumulationQuota.priority).toBe("HIGH");
      expect(optimization.recommendations.growthQuota.suggestedAmount).toBeGreaterThan(0);
      expect(optimization.recommendations.accumulationQuota.suggestedAmount).toBeGreaterThan(0);
    });

    it("高利用率での最適化提案", () => {
      // 高利用率の状態を作成
      const largeTransaction: NisaTransaction = {
        id: "test-7",
        type: "BUY",
        symbol: "7203",
        symbolName: "トヨタ自動車",
        quantity: 1000,
        price: 2000,
        amount: 2_000_000, // 高利用率
        quotaType: "GROWTH",
        transactionDate: "2024-01-15",
        createdAt: "2024-01-15T10:00:00Z",
        updatedAt: "2024-01-15T10:00:00Z",
      };

      calculator.addTransaction(largeTransaction);
      const optimization = calculator.calculateOptimization();
      
      expect(optimization.recommendations.growthQuota.priority).toBe("LOW");
      expect(optimization.recommendations.growthQuota.suggestedAmount).toBeLessThan(500_000);
    });
  });

  describe("アラートの生成", () => {
    it("高利用率でのアラート生成", () => {
      // 高利用率の状態を作成
      const largeTransaction: NisaTransaction = {
        id: "test-8",
        type: "BUY",
        symbol: "7203",
        symbolName: "トヨタ自動車",
        quantity: 1000,
        price: 2200,
        amount: 2_200_000, // 90%以上
        quotaType: "GROWTH",
        transactionDate: "2024-01-15",
        createdAt: "2024-01-15T10:00:00Z",
        updatedAt: "2024-01-15T10:00:00Z",
      };

      calculator.addTransaction(largeTransaction);
      const alerts = calculator.generateAlerts();
      
      expect(alerts.length).toBeGreaterThan(0);
      expect(alerts.some(alert => alert.type === "CRITICAL")).toBe(true);
      expect(alerts.some(alert => alert.quotaType === "GROWTH")).toBe(true);
    });

    it("低利用率ではアラートを生成しない", () => {
      const alerts = calculator.generateAlerts();
      expect(alerts).toHaveLength(0);
    });
  });

  describe("統計情報の計算", () => {
    it("空のポートフォリオの統計", () => {
      const statistics = calculator.calculateStatistics();
      
      expect(statistics.totalInvested).toBe(0);
      expect(statistics.totalValue).toBe(0);
      expect(statistics.totalProfitLoss).toBe(0);
      expect(statistics.averageReturn).toBe(0);
    });

    it("取引がある場合の統計", () => {
      const transaction: NisaTransaction = {
        id: "test-9",
        type: "BUY",
        symbol: "7203",
        symbolName: "トヨタ自動車",
        quantity: 100,
        price: 2500,
        amount: 250_000,
        quotaType: "GROWTH",
        transactionDate: "2024-01-15",
        createdAt: "2024-01-15T10:00:00Z",
        updatedAt: "2024-01-15T10:00:00Z",
      };

      calculator.addTransaction(transaction);
      calculator.setCurrentPrice("7203", 2600);
      
      const statistics = calculator.calculateStatistics();
      
      expect(statistics.totalInvested).toBe(250_000);
      expect(statistics.totalValue).toBe(260_000);
      expect(statistics.totalProfitLoss).toBe(10_000);
      expect(statistics.averageReturn).toBeCloseTo(4.0, 1);
    });
  });
});
