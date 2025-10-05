/**
 * 新NISA枠管理機能の計算ロジック統合テスト
 */

import { NisaCalculator } from "../calculator";
import { NisaTransaction } from "../types";

describe("NisaCalculator Integration Tests", () => {
  let calculator: NisaCalculator;

  beforeEach(() => {
    calculator = new NisaCalculator();
  });

  describe("複雑なシナリオのテスト", () => {
    it("複数銘柄のポートフォリオを正しく計算する", () => {
      // 複数の取引を追加
      const transactions: NisaTransaction[] = [
        {
          id: "tx-1",
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
        },
        {
          id: "tx-2",
          type: "BUY",
          symbol: "6758",
          symbolName: "ソニーグループ",
          quantity: 50,
          price: 12000,
          amount: 600_000,
          quotaType: "GROWTH",
          transactionDate: "2024-01-16",
          createdAt: "2024-01-16T10:00:00Z",
          updatedAt: "2024-01-16T10:00:00Z",
        },
        {
          id: "tx-3",
          type: "BUY",
          symbol: "9984",
          symbolName: "ソフトバンクグループ",
          quantity: 100,
          price: 5000,
          amount: 500_000,
          quotaType: "ACCUMULATION",
          transactionDate: "2024-01-17",
          createdAt: "2024-01-17T10:00:00Z",
          updatedAt: "2024-01-17T10:00:00Z",
        },
      ];

      // 取引を追加
      transactions.forEach(tx => calculator.addTransaction(tx));

      // 現在価格を設定
      calculator.setCurrentPrice("7203", 2600);
      calculator.setCurrentPrice("6758", 12500);
      calculator.setCurrentPrice("9984", 5200);

      // 計算結果を取得
      const result = calculator.calculateAll();

      // 投資枠の検証
      expect(result.quotas.growthInvestment.usedAmount).toBe(850_000);
      expect(result.quotas.growthInvestment.availableAmount).toBe(1_550_000);
      expect(result.quotas.accumulationInvestment.usedAmount).toBe(500_000);
      expect(result.quotas.accumulationInvestment.availableAmount).toBe(-100_000); // 枠超過

      // ポートフォリオの検証
      expect(result.portfolio.positions).toHaveLength(3);
      expect(result.portfolio.totalCost).toBe(1_350_000);
      expect(result.portfolio.totalValue).toBe(1_385_000);
      expect(result.portfolio.unrealizedProfitLoss).toBe(35_000);

      // 最適化提案の検証
      expect(result.optimization.recommendations.growthQuota.suggestedAmount).toBeGreaterThan(0);
      expect(result.optimization.recommendations.accumulationQuota.suggestedAmount).toBe(0); // 枠超過のため

      // 税務計算の検証
      expect(result.taxCalculation.currentYear.totalTaxFreeAmount).toBe(1_350_000);
      expect(result.taxCalculation.taxSavings.estimatedTaxSavings).toBeGreaterThan(0);
    });

    it("売却取引を含む複雑なシナリオを処理する", () => {
      // 買い取引
      const buyTransaction: NisaTransaction = {
        id: "tx-buy",
        type: "BUY",
        symbol: "7203",
        symbolName: "トヨタ自動車",
        quantity: 200,
        price: 2500,
        amount: 500_000,
        quotaType: "GROWTH",
        transactionDate: "2024-01-15",
        createdAt: "2024-01-15T10:00:00Z",
        updatedAt: "2024-01-15T10:00:00Z",
      };

      calculator.addTransaction(buyTransaction);

      // 一部売却
      const sellTransaction: NisaTransaction = {
        id: "tx-sell",
        type: "SELL",
        symbol: "7203",
        symbolName: "トヨタ自動車",
        quantity: 100,
        price: 2600,
        amount: 260_000,
        quotaType: "GROWTH",
        transactionDate: "2024-01-20",
        profitLoss: 10_000,
        taxFreeAmount: 260_000,
        createdAt: "2024-01-20T10:00:00Z",
        updatedAt: "2024-01-20T10:00:00Z",
      };

      calculator.addTransaction(sellTransaction);

      // 現在価格を設定
      calculator.setCurrentPrice("7203", 2700);

      const result = calculator.calculateAll();

      // 投資枠の検証（売却分が差し引かれる）
      expect(result.quotas.growthInvestment.usedAmount).toBe(240_000); // 500_000 - 260_000
      expect(result.quotas.growthInvestment.availableAmount).toBe(2_160_000);

      // ポートフォリオの検証
      expect(result.portfolio.positions).toHaveLength(1);
      expect(result.portfolio.positions[0].quantity).toBe(100); // 200 - 100
      expect(result.portfolio.positions[0].cost).toBe(250_000); // 500_000 - 250_000
      expect(result.portfolio.positions[0].currentValue).toBe(270_000); // 100 * 2700
      expect(result.portfolio.unrealizedProfitLoss).toBe(20_000); // 270_000 - 250_000
      expect(result.portfolio.realizedProfitLoss).toBe(10_000);

      // 枠の再利用
      expect(result.quotas.quotaReuse.growthAvailable).toBe(260_000);
      expect(result.quotas.quotaReuse.nextYearAvailable).toBe(260_000);
    });

    it("高利用率でのアラート生成をテストする", () => {
      // 高利用率の状態を作成
      const largeTransaction: NisaTransaction = {
        id: "tx-large",
        type: "BUY",
        symbol: "7203",
        symbolName: "トヨタ自動車",
        quantity: 1000,
        price: 2200,
        amount: 2_200_000, // 91.67%の利用率
        quotaType: "GROWTH",
        transactionDate: "2024-01-15",
        createdAt: "2024-01-15T10:00:00Z",
        updatedAt: "2024-01-15T10:00:00Z",
      };

      calculator.addTransaction(largeTransaction);
      const result = calculator.calculateAll();

      // アラートの検証
      expect(result.alerts.length).toBeGreaterThan(0);
      const criticalAlert = result.alerts.find(alert => alert.type === "CRITICAL");
      expect(criticalAlert).toBeDefined();
      expect(criticalAlert?.quotaType).toBe("GROWTH");
      expect(criticalAlert?.currentUsage).toBeGreaterThan(90);
    });

    it("投資機会の生成をテストする", () => {
      const result = calculator.calculateAll();

      // 投資機会の検証
      expect(result.opportunities.length).toBeGreaterThan(0);
      const opportunity = result.opportunities[0];
      expect(opportunity.symbol).toBeDefined();
      expect(opportunity.symbolName).toBeDefined();
      expect(opportunity.expectedReturn).toBeGreaterThan(0);
      expect(opportunity.suggestedAmount).toBeGreaterThan(0);
      expect(["GROWTH", "ACCUMULATION"]).toContain(opportunity.quotaRecommendation);
    });

    it("統計情報の計算をテストする", () => {
      // 取引を追加
      const transaction: NisaTransaction = {
        id: "tx-stats",
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
      expect(statistics.bestPerformer.symbol).toBe("7203");
      expect(statistics.worstPerformer.symbol).toBe("7203");
      expect(statistics.diversificationScore).toBe(10);
      expect(statistics.riskScore).toBeGreaterThan(0);
    });
  });

  describe("エッジケースのテスト", () => {
    it("空の取引履歴でエラーが発生しない", () => {
      const result = calculator.calculateAll();
      
      expect(result.quotas.growthInvestment.usedAmount).toBe(0);
      expect(result.quotas.accumulationInvestment.usedAmount).toBe(0);
      expect(result.portfolio.positions).toHaveLength(0);
      expect(result.alerts).toHaveLength(0);
      expect(result.opportunities.length).toBeGreaterThan(0); // 投資機会は生成される
    });

    it("無効な取引でエラーが発生する", () => {
      const invalidTransaction = {
        type: "BUY" as const,
        symbol: "",
        symbolName: "",
        quantity: 0,
        price: -100,
        amount: 0,
        quotaType: "INVALID" as any,
        transactionDate: "2024-01-15",
      };

      const validation = calculator.validateTransaction(invalidTransaction);
      expect(validation.isValid).toBe(false);
      expect(validation.errors.length).toBeGreaterThan(0);
    });

    it("投資枠を超過する取引でエラーが発生する", () => {
      // まず大きな取引を追加して枠を埋める
      const largeTransaction: NisaTransaction = {
        id: "tx-large",
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

      const overLimitTransaction = {
        type: "BUY" as const,
        symbol: "6758",
        symbolName: "ソニーグループ",
        quantity: 100,
        price: 10000,
        amount: 1_000_000,
        quotaType: "GROWTH" as const,
        transactionDate: "2024-01-15",
      };

      const validation = calculator.validateTransaction(overLimitTransaction);
      expect(validation.isValid).toBe(false);
      expect(validation.errors.some(error => error.includes("利用可能額を超えています"))).toBe(true);
    });
  });
});
