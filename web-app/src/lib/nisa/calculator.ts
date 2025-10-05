/**
 * 新NISA枠管理機能の計算ロジック
 * 税務計算、枠管理、最適化提案を提供
 */

import {
  NisaQuotaStatus,
  NisaTransaction,
  NisaPortfolio,
  NisaPosition,
  QuotaOptimization,
  TaxCalculation,
  QuotaAlert,
  InvestmentOpportunity,
  NisaCalculationResult,
  NisaStatistics,
  QuotaType,
  TransactionType,
  RiskLevel,
  Priority,
  AlertType,
  NISA_CONSTANTS,
  NisaErrorCode,
  ValidationResult,
} from "./types";

export class NisaCalculator {
  private transactions: NisaTransaction[] = [];
  private currentPrices: Map<string, number> = new Map();

  constructor(transactions: NisaTransaction[] = []) {
    this.transactions = transactions;
  }

  /**
   * 投資枠利用状況を計算
   */
  calculateQuotaStatus(): NisaQuotaStatus {
    const currentYear = new Date().getFullYear();
    const currentYearTransactions = this.transactions.filter(
      t => new Date(t.transactionDate).getFullYear() === currentYear,
    );

    // 成長投資枠の計算
    const growthTransactions = currentYearTransactions.filter(
      t => t.quotaType === "GROWTH",
    );
    const growthUsed = growthTransactions
      .filter(t => t.type === "BUY")
      .reduce((sum, t) => sum + t.amount, 0);
    const growthSold = growthTransactions
      .filter(t => t.type === "SELL")
      .reduce((sum, t) => sum + (t.amount || 0), 0);

    // つみたて投資枠の計算
    const accumulationTransactions = currentYearTransactions.filter(
      t => t.quotaType === "ACCUMULATION",
    );
    const accumulationUsed = accumulationTransactions
      .filter(t => t.type === "BUY")
      .reduce((sum, t) => sum + t.amount, 0);
    const accumulationSold = accumulationTransactions
      .filter(t => t.type === "SELL")
      .reduce((sum, t) => sum + (t.amount || 0), 0);

    return {
      growthInvestment: {
        annualLimit: NISA_CONSTANTS.GROWTH_ANNUAL_LIMIT,
        taxFreeLimit: NISA_CONSTANTS.GROWTH_TAX_FREE_LIMIT,
        usedAmount: growthUsed - growthSold,
        availableAmount: NISA_CONSTANTS.GROWTH_ANNUAL_LIMIT - (growthUsed - growthSold),
        utilizationRate: ((growthUsed - growthSold) / NISA_CONSTANTS.GROWTH_ANNUAL_LIMIT) * 100,
      },
      accumulationInvestment: {
        annualLimit: NISA_CONSTANTS.ACCUMULATION_ANNUAL_LIMIT,
        taxFreeLimit: NISA_CONSTANTS.ACCUMULATION_TAX_FREE_LIMIT,
        usedAmount: accumulationUsed - accumulationSold,
        availableAmount: NISA_CONSTANTS.ACCUMULATION_ANNUAL_LIMIT - (accumulationUsed - accumulationSold),
        utilizationRate: ((accumulationUsed - accumulationSold) / NISA_CONSTANTS.ACCUMULATION_ANNUAL_LIMIT) * 100,
      },
      quotaReuse: {
        growthAvailable: growthSold,
        accumulationAvailable: accumulationSold,
        nextYearAvailable: growthSold + accumulationSold,
      },
    };
  }

  /**
   * ポートフォリオを計算
   */
  calculatePortfolio(): NisaPortfolio {
    const positions = this.calculatePositions();
    const totalValue = positions.reduce((sum, p) => sum + p.currentValue, 0);
    const totalCost = positions.reduce((sum, p) => sum + p.cost, 0);
    const unrealizedProfitLoss = totalValue - totalCost;

    // 実現損益の計算
    const realizedProfitLoss = this.transactions
      .filter(t => t.type === "SELL" && t.profitLoss)
      .reduce((sum, t) => sum + (t.profitLoss || 0), 0);

    // 非課税枠内の損益
    const taxFreeProfitLoss = this.calculateTaxFreeProfitLoss(positions);

    return {
      positions,
      totalValue,
      totalCost,
      unrealizedProfitLoss,
      realizedProfitLoss,
      taxFreeProfitLoss,
      lastUpdated: new Date().toISOString(),
    };
  }

  /**
   * ポジションを計算
   */
  private calculatePositions(): NisaPosition[] {
    const positionMap = new Map<string, {
      symbol: string;
      symbolName: string;
      quantity: number;
      totalCost: number;
      quotaType: QuotaType;
      firstPurchaseDate: string;
    }>();

    // 取引履歴からポジションを計算
    for (const transaction of this.transactions) {
      const key = `${transaction.symbol}_${transaction.quotaType}`;
      const existing = positionMap.get(key);

      if (transaction.type === "BUY") {
        if (existing) {
          existing.quantity += transaction.quantity;
          existing.totalCost += transaction.amount;
        } else {
          positionMap.set(key, {
            symbol: transaction.symbol,
            symbolName: transaction.symbolName,
            quantity: transaction.quantity,
            totalCost: transaction.amount,
            quotaType: transaction.quotaType,
            firstPurchaseDate: transaction.transactionDate,
          });
        }
      } else if (transaction.type === "SELL") {
        if (existing) {
          existing.quantity -= transaction.quantity;
          existing.totalCost -= transaction.amount;
          if (existing.quantity <= 0) {
            positionMap.delete(key);
          }
        }
      }
    }

    // ポジションをNisaPosition形式に変換
    return Array.from(positionMap.values()).map(pos => {
      const currentPrice = this.currentPrices.get(pos.symbol) || 0;
      const currentValue = pos.quantity * currentPrice;
      const averagePrice = pos.quantity > 0 ? pos.totalCost / pos.quantity : 0;

      return {
        symbol: pos.symbol,
        symbolName: pos.symbolName,
        quantity: pos.quantity,
        averagePrice,
        currentPrice,
        cost: pos.totalCost,
        currentValue,
        unrealizedProfitLoss: currentValue - pos.totalCost,
        quotaType: pos.quotaType,
        purchaseDate: pos.firstPurchaseDate,
        lastUpdated: new Date().toISOString(),
      };
    });
  }

  /**
   * 非課税枠内の損益を計算
   */
  private calculateTaxFreeProfitLoss(positions: NisaPosition[]): number {
    return positions.reduce((sum, pos) => {
      // 非課税枠内の損益は未実現損益の一部として計算
      const taxFreeRatio = this.calculateTaxFreeRatio(pos.quotaType);
      return sum + (pos.unrealizedProfitLoss * taxFreeRatio);
    }, 0);
  }

  /**
   * 非課税枠比率を計算
   */
  private calculateTaxFreeRatio(quotaType: QuotaType): number {
    const quotaStatus = this.calculateQuotaStatus();
    const quota = quotaType === "GROWTH" 
      ? quotaStatus.growthInvestment 
      : quotaStatus.accumulationInvestment;
    
    return Math.min(quota.usedAmount / quota.taxFreeLimit, 1);
  }

  /**
   * 最適化提案を生成
   */
  calculateOptimization(): QuotaOptimization {
    const quotaStatus = this.calculateQuotaStatus();
    const portfolio = this.calculatePortfolio();

    // 成長投資枠の提案
    const growthRecommendation = this.generateGrowthRecommendation(quotaStatus, portfolio);
    
    // つみたて投資枠の提案
    const accumulationRecommendation = this.generateAccumulationRecommendation(quotaStatus, portfolio);

    // リスク分析
    const riskAnalysis = this.analyzeRisk(portfolio);

    return {
      recommendations: {
        growthQuota: growthRecommendation,
        accumulationQuota: accumulationRecommendation,
      },
      riskAnalysis,
      lastCalculated: new Date().toISOString(),
    };
  }

  /**
   * 成長投資枠の推奨を生成
   */
  private generateGrowthRecommendation(
    quotaStatus: NisaQuotaStatus,
    portfolio: NisaPortfolio,
  ): { suggestedAmount: number; reason: string; priority: Priority } {
    const available = quotaStatus.growthInvestment.availableAmount;
    const utilization = quotaStatus.growthInvestment.utilizationRate;

    if (utilization < 50) {
      return {
        suggestedAmount: Math.min(available, 500_000),
        reason: "成長投資枠の利用率が低いため、積極的な投資を推奨",
        priority: "HIGH",
      };
    } else if (utilization < 80) {
      return {
        suggestedAmount: Math.min(available, 200_000),
        reason: "成長投資枠の利用率が中程度のため、適度な投資を推奨",
        priority: "MEDIUM",
      };
    } else {
      return {
        suggestedAmount: Math.min(available, 50_000),
        reason: "成長投資枠の利用率が高いため、慎重な投資を推奨",
        priority: "LOW",
      };
    }
  }

  /**
   * つみたて投資枠の推奨を生成
   */
  private generateAccumulationRecommendation(
    quotaStatus: NisaQuotaStatus,
    portfolio: NisaPortfolio,
  ): { suggestedAmount: number; reason: string; priority: Priority } {
    const available = quotaStatus.accumulationInvestment.availableAmount;
    const utilization = quotaStatus.accumulationInvestment.utilizationRate;

    if (utilization < 30) {
      return {
        suggestedAmount: Math.min(available, 100_000),
        reason: "つみたて投資枠の利用率が低いため、定期的な積立投資を推奨",
        priority: "HIGH",
      };
    } else if (utilization < 70) {
      return {
        suggestedAmount: Math.min(available, 50_000),
        reason: "つみたて投資枠の利用率が中程度のため、継続的な積立投資を推奨",
        priority: "MEDIUM",
      };
    } else {
      return {
        suggestedAmount: Math.min(available, 20_000),
        reason: "つみたて投資枠の利用率が高いため、少額の積立投資を推奨",
        priority: "LOW",
      };
    }
  }

  /**
   * リスク分析を実行
   */
  private analyzeRisk(portfolio: NisaPortfolio): {
    diversificationScore: number;
    sectorConcentration: number;
    riskLevel: RiskLevel;
  } {
    const positions = portfolio.positions;
    const totalValue = portfolio.totalValue;

    if (positions.length === 0) {
      return {
        diversificationScore: 0,
        sectorConcentration: 100,
        riskLevel: "HIGH",
      };
    }

    // 分散投資スコアの計算（銘柄数の多さとバランス）
    const diversificationScore = Math.min(positions.length * 10, 100);

    // セクター集中度の計算（仮実装）
    const sectorConcentration = this.calculateSectorConcentration(positions);

    // リスクレベルの判定
    let riskLevel: RiskLevel = "LOW";
    if (diversificationScore < 30 || sectorConcentration > 80) {
      riskLevel = "HIGH";
    } else if (diversificationScore < 60 || sectorConcentration > 60) {
      riskLevel = "MEDIUM";
    }

    return {
      diversificationScore,
      sectorConcentration,
      riskLevel,
    };
  }

  /**
   * セクター集中度を計算
   */
  private calculateSectorConcentration(positions: NisaPosition[]): number {
    // 仮実装：実際のセクター情報が必要
    const sectorMap = new Map<string, number>();
    
    positions.forEach(pos => {
      // 仮のセクター分類（実際の実装では適切なセクター情報を使用）
      const sector = this.getSectorFromSymbol(pos.symbol);
      const value = sectorMap.get(sector) || 0;
      sectorMap.set(sector, value + pos.currentValue);
    });

    const totalValue = Array.from(sectorMap.values()).reduce((sum, val) => sum + val, 0);
    const maxSectorValue = Math.max(...Array.from(sectorMap.values()));
    
    return totalValue > 0 ? (maxSectorValue / totalValue) * 100 : 100;
  }

  /**
   * 銘柄からセクターを取得（仮実装）
   */
  private getSectorFromSymbol(symbol: string): string {
    // 仮実装：実際の実装では適切なセクター情報を使用
    const sectorMap: Record<string, string> = {
      "7203": "自動車",
      "6758": "電気機器",
      "8035": "銀行",
      "9984": "小売業",
    };
    return sectorMap[symbol] || "その他";
  }

  /**
   * 税務計算を実行
   */
  calculateTax(): TaxCalculation {
    const quotaStatus = this.calculateQuotaStatus();
    const currentYear = new Date().getFullYear();

    // 現在年度の使用状況
    const currentYearData = {
      growthQuotaUsed: quotaStatus.growthInvestment.usedAmount,
      accumulationQuotaUsed: quotaStatus.accumulationInvestment.usedAmount,
      totalTaxFreeAmount: quotaStatus.growthInvestment.usedAmount + quotaStatus.accumulationInvestment.usedAmount,
    };

    // 翌年度の利用可能枠
    const nextYearData = {
      availableGrowthQuota: NISA_CONSTANTS.GROWTH_ANNUAL_LIMIT,
      availableAccumulationQuota: NISA_CONSTANTS.ACCUMULATION_ANNUAL_LIMIT,
      reusableQuota: quotaStatus.quotaReuse.nextYearAvailable,
    };

    // 税務効果の計算
    const taxSavings = this.calculateTaxSavings(currentYearData.totalTaxFreeAmount);

    return {
      currentYear: currentYearData,
      nextYear: nextYearData,
      taxSavings,
      calculatedAt: new Date().toISOString(),
    };
  }

  /**
   * 税務効果を計算
   */
  private calculateTaxSavings(taxFreeAmount: number): {
    estimatedTaxSavings: number;
    taxRate: number;
    effectiveTaxRate: number;
  } {
    // 仮の税率（実際の実装では適切な税率計算を使用）
    const taxRate = 0.20; // 20%
    const estimatedTaxSavings = taxFreeAmount * taxRate;
    const effectiveTaxRate = taxRate;

    return {
      estimatedTaxSavings,
      taxRate,
      effectiveTaxRate,
    };
  }

  /**
   * アラートを生成
   */
  generateAlerts(): QuotaAlert[] {
    const quotaStatus = this.calculateQuotaStatus();
    const alerts: QuotaAlert[] = [];

    // 成長投資枠のアラート
    if (quotaStatus.growthInvestment.utilizationRate > 90) {
      alerts.push({
        id: `growth_critical_${Date.now()}`,
        type: "CRITICAL",
        message: "成長投資枠の利用率が90%を超えています",
        quotaType: "GROWTH",
        currentUsage: quotaStatus.growthInvestment.utilizationRate,
        threshold: 90,
        recommendedAction: "投資枠の見直しを検討してください",
        createdAt: new Date().toISOString(),
        isRead: false,
      });
    } else if (quotaStatus.growthInvestment.utilizationRate > 70) {
      alerts.push({
        id: `growth_warning_${Date.now()}`,
        type: "WARNING",
        message: "成長投資枠の利用率が70%を超えています",
        quotaType: "GROWTH",
        currentUsage: quotaStatus.growthInvestment.utilizationRate,
        threshold: 70,
        recommendedAction: "投資計画の見直しを検討してください",
        createdAt: new Date().toISOString(),
        isRead: false,
      });
    }

    // つみたて投資枠のアラート
    if (quotaStatus.accumulationInvestment.utilizationRate > 90) {
      alerts.push({
        id: `accumulation_critical_${Date.now()}`,
        type: "CRITICAL",
        message: "つみたて投資枠の利用率が90%を超えています",
        quotaType: "ACCUMULATION",
        currentUsage: quotaStatus.accumulationInvestment.utilizationRate,
        threshold: 90,
        recommendedAction: "積立投資の見直しを検討してください",
        createdAt: new Date().toISOString(),
        isRead: false,
      });
    }

    return alerts;
  }

  /**
   * 投資機会を生成
   */
  generateInvestmentOpportunities(): InvestmentOpportunity[] {
    const quotaStatus = this.calculateQuotaStatus();
    const opportunities: InvestmentOpportunity[] = [];

    // 成長投資枠の機会
    if (quotaStatus.growthInvestment.availableAmount > 100_000) {
      opportunities.push({
        id: `growth_opportunity_${Date.now()}`,
        symbol: "7203",
        symbolName: "トヨタ自動車",
        reason: "成長投資枠の利用率が低く、投資機会があります",
        expectedReturn: 0.08,
        riskLevel: "MEDIUM",
        quotaRecommendation: "GROWTH",
        suggestedAmount: Math.min(quotaStatus.growthInvestment.availableAmount, 200_000),
        confidence: 0.75,
        createdAt: new Date().toISOString(),
      });
    }

    // つみたて投資枠の機会
    if (quotaStatus.accumulationInvestment.availableAmount > 50_000) {
      opportunities.push({
        id: `accumulation_opportunity_${Date.now()}`,
        symbol: "6758",
        symbolName: "ソニーグループ",
        reason: "つみたて投資枠の利用率が低く、積立投資の機会があります",
        expectedReturn: 0.06,
        riskLevel: "LOW",
        quotaRecommendation: "ACCUMULATION",
        suggestedAmount: Math.min(quotaStatus.accumulationInvestment.availableAmount, 100_000),
        confidence: 0.80,
        createdAt: new Date().toISOString(),
      });
    }

    return opportunities;
  }

  /**
   * 統計情報を計算
   */
  calculateStatistics(): NisaStatistics {
    const portfolio = this.calculatePortfolio();
    const positions = portfolio.positions;

    if (positions.length === 0) {
      return {
        totalInvested: 0,
        totalValue: 0,
        totalProfitLoss: 0,
        totalTaxFreeProfitLoss: 0,
        averageReturn: 0,
        bestPerformer: { symbol: "", symbolName: "", return: 0 },
        worstPerformer: { symbol: "", symbolName: "", return: 0 },
        diversificationScore: 0,
        riskScore: 0,
      };
    }

    const totalInvested = portfolio.totalCost;
    const totalValue = portfolio.totalValue;
    const totalProfitLoss = portfolio.unrealizedProfitLoss + portfolio.realizedProfitLoss;
    const totalTaxFreeProfitLoss = portfolio.taxFreeProfitLoss;
    const averageReturn = totalInvested > 0 ? (totalProfitLoss / totalInvested) * 100 : 0;

    // ベスト・ワーストパフォーマー
    const performers = positions.map(pos => ({
      symbol: pos.symbol,
      symbolName: pos.symbolName,
      return: pos.cost > 0 ? (pos.unrealizedProfitLoss / pos.cost) * 100 : 0,
    }));

    const bestPerformer = performers.reduce((best, current) => 
      current.return > best.return ? current : best,
    );
    const worstPerformer = performers.reduce((worst, current) => 
      current.return < worst.return ? current : worst,
    );

    // 分散投資スコア
    const diversificationScore = Math.min(positions.length * 10, 100);

    // リスクスコア
    const riskScore = this.calculateRiskScore(positions);

    return {
      totalInvested,
      totalValue,
      totalProfitLoss,
      totalTaxFreeProfitLoss,
      averageReturn,
      bestPerformer,
      worstPerformer,
      diversificationScore,
      riskScore,
    };
  }

  /**
   * リスクスコアを計算
   */
  private calculateRiskScore(positions: NisaPosition[]): number {
    if (positions.length === 0) return 0;

    // 簡易的なリスクスコア計算
    const totalValue = positions.reduce((sum, pos) => sum + pos.currentValue, 0);
    const maxPositionValue = Math.max(...positions.map(pos => pos.currentValue));
    const concentrationRisk = (maxPositionValue / totalValue) * 100;

    return Math.min(concentrationRisk, 100);
  }

  /**
   * 取引の妥当性を検証
   */
  validateTransaction(transaction: Omit<NisaTransaction, "id" | "createdAt" | "updatedAt">): ValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];

    // 基本検証
    if (!transaction.symbol || !transaction.symbolName) {
      errors.push("銘柄情報が不足しています");
    }

    if (transaction.quantity <= 0) {
      errors.push("数量は0より大きい必要があります");
    }

    if (transaction.price <= 0) {
      errors.push("価格は0より大きい必要があります");
    }

    if (!["GROWTH", "ACCUMULATION"].includes(transaction.quotaType)) {
      errors.push("無効な投資枠タイプです");
    }

    if (!["BUY", "SELL"].includes(transaction.type)) {
      errors.push("無効な取引タイプです");
    }

    // 投資枠の検証
    if (transaction.type === "BUY") {
      const quotaStatus = this.calculateQuotaStatus();
      const quota = transaction.quotaType === "GROWTH" 
        ? quotaStatus.growthInvestment 
        : quotaStatus.accumulationInvestment;

      if (transaction.amount > quota.availableAmount) {
        errors.push(`${transaction.quotaType}枠の利用可能額を超えています`);
      }
    }

    // 売却時の検証
    if (transaction.type === "SELL") {
      const positions = this.calculatePositions();
      const position = positions.find(p => 
        p.symbol === transaction.symbol && p.quotaType === transaction.quotaType,
      );

      if (!position) {
        errors.push("売却対象のポジションが見つかりません");
      } else if (transaction.quantity > position.quantity) {
        errors.push("売却数量が保有数量を超えています");
      }
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings,
    };
  }

  /**
   * 現在価格を設定
   */
  setCurrentPrice(symbol: string, price: number): void {
    this.currentPrices.set(symbol, price);
  }

  /**
   * 取引を追加
   */
  addTransaction(transaction: Omit<NisaTransaction, "id" | "createdAt" | "updatedAt">): ValidationResult {
    const validation = this.validateTransaction(transaction);
    
    if (validation.isValid) {
      const newTransaction: NisaTransaction = {
        ...transaction,
        id: `tx_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
      
      this.transactions.push(newTransaction);
    }

    return validation;
  }

  /**
   * 完全な計算結果を取得
   */
  calculateAll(): NisaCalculationResult {
    return {
      quotas: this.calculateQuotaStatus(),
      portfolio: this.calculatePortfolio(),
      optimization: this.calculateOptimization(),
      taxCalculation: this.calculateTax(),
      alerts: this.generateAlerts(),
      opportunities: this.generateInvestmentOpportunities(),
    };
  }
}
