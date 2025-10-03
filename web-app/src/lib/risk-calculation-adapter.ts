/**
 * ユーザー設定に基づくリスク計算アダプター
 * 既存のリスク計算ロジックをユーザーのカスタマイズ設定に合わせて調整
 */

// 外部ストアが存在しないためローカル定義に切り替え
export interface RiskCustomizationSettings {
  riskTolerance: {
    level?: "VERY_LOW" | "LOW" | "MEDIUM" | "HIGH" | "VERY_HIGH" | "CRITICAL";
    maxDrawdown: number;
    volatilityTolerance: number;
    varTolerance: number;
  };
  targetReturn: {
    annual: number;
    monthly: number;
    riskAdjusted: boolean;
  };
  individualStockSettings: Record<string, {
    riskLevel?: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
    targetPrice?: number;
    stopLossPrice?: number;
    maxPositionSize?: number;
  }>;
}

export interface RiskMetrics {
  portfolio_value: number;
  total_exposure: number;
  max_drawdown: number;
  var_95: number;
  sharpe_ratio: number;
  beta: number;
  correlation_matrix: Record<string, number>;
  risk_score: number;
}

export interface AdjustedRiskMetrics extends RiskMetrics {
  // ユーザー設定に基づく調整値
  adjusted_risk_score: number;
  risk_level: "VERY_LOW" | "LOW" | "MEDIUM" | "HIGH" | "VERY_HIGH" | "CRITICAL";
  risk_tolerance_status: "WITHIN_TOLERANCE" | "APPROACHING_LIMIT" | "EXCEEDED_LIMIT";
  target_return_status: "MEETING_TARGET" | "BELOW_TARGET" | "ABOVE_TARGET";
  recommendations: string[];
}

export interface IndividualStockRiskProfile {
  symbol: string;
  current_price: number;
  risk_score: number;
  adjusted_risk_score: number;
  risk_level: string;
  target_price?: number;
  stop_loss_price?: number;
  position_size?: number;
  expected_return: number;
  risk_adjusted_return: number;
  recommendations: string[];
}

export class RiskCalculationAdapter {
  private settings: RiskCustomizationSettings;

  constructor(settings: RiskCustomizationSettings) {
    this.settings = settings;
  }

  /**
   * ポートフォリオリスクをユーザー設定に基づいて調整
   */
  public adjustPortfolioRisk(riskMetrics: RiskMetrics): AdjustedRiskMetrics {
    const thresholds = this.getRiskThresholds();
    
    // 基本リスクスコアの調整
    const adjustedRiskScore = this.calculateAdjustedRiskScore(riskMetrics);
    
    // リスクレベル判定
    const riskLevel = this.determineRiskLevel(adjustedRiskScore);
    
    // リスク許容度ステータス
    const riskToleranceStatus = this.assessRiskTolerance(riskMetrics, thresholds);
    
    // 目標リターンステータス
    const targetReturnStatus = this.assessTargetReturn(riskMetrics);
    
    // 推奨事項の生成
    const recommendations = this.generateRecommendations(
      riskMetrics, 
      riskLevel, 
      riskToleranceStatus, 
      targetReturnStatus,
    );

    return {
      ...riskMetrics,
      adjusted_risk_score: adjustedRiskScore,
      risk_level: riskLevel,
      risk_tolerance_status: riskToleranceStatus,
      target_return_status: targetReturnStatus,
      recommendations,
    };
  }

  /**
   * 個別銘柄リスクをユーザー設定に基づいて調整
   */
  public adjustIndividualStockRisk(
    symbol: string,
    currentPrice: number,
    baseRiskScore: number,
    expectedReturn: number,
  ): IndividualStockRiskProfile {
    const stockSettings = this.settings.individualStockSettings[symbol];
    const thresholds = this.getRiskThresholds();
    
    // 個別銘柄のリスクスコア調整
    const adjustedRiskScore = this.calculateIndividualStockRiskScore(
      baseRiskScore, 
      stockSettings,
    );
    
    // リスクレベル判定
    const riskLevel = this.determineIndividualStockRiskLevel(adjustedRiskScore);
    
    // リスク調整後リターン計算
    const riskAdjustedReturn = this.calculateRiskAdjustedReturn(
      expectedReturn, 
      adjustedRiskScore,
    );
    
    // 推奨事項の生成
    const recommendations = this.generateIndividualStockRecommendations(
      symbol,
      currentPrice,
      adjustedRiskScore,
      riskLevel,
      stockSettings,
    );

    return {
      symbol,
      current_price: currentPrice,
      risk_score: baseRiskScore,
      adjusted_risk_score: adjustedRiskScore,
      risk_level: riskLevel,
      target_price: stockSettings?.targetPrice,
      stop_loss_price: stockSettings?.stopLossPrice,
      position_size: stockSettings?.maxPositionSize,
      expected_return: expectedReturn,
      risk_adjusted_return: riskAdjustedReturn,
      recommendations,
    };
  }

  /**
   * リスク閾値を取得
   */
  private getRiskThresholds() {
    const { level, maxDrawdown, volatilityTolerance, varTolerance } = this.settings.riskTolerance;
    
    // リスクレベルに応じた閾値の調整
    const levelMultipliers = {
      "VERY_LOW": 0.5,
      "LOW": 0.7,
      "MEDIUM": 1.0,
      "HIGH": 1.3,
      "VERY_HIGH": 1.6,
      "CRITICAL": 2.0,
    };

    const multiplier = levelMultipliers[level as keyof typeof levelMultipliers] ?? 1.0;

    return {
      maxDrawdown: maxDrawdown * multiplier,
      volatilityTolerance: volatilityTolerance * multiplier,
      varTolerance: varTolerance * multiplier,
      level,
    };
  }

  /**
   * 調整後リスクスコアを計算
   */
  private calculateAdjustedRiskScore(riskMetrics: RiskMetrics): number {
    const thresholds = this.getRiskThresholds();
    
    // 各リスク指標の重み付きスコア計算
    const drawdownScore = Math.min(riskMetrics.max_drawdown / thresholds.maxDrawdown, 1.0);
    const volatilityScore = Math.min(riskMetrics.var_95 / thresholds.varTolerance, 1.0);
    const correlationScore = this.calculateCorrelationRiskScore(riskMetrics.correlation_matrix);
    
    // ユーザー設定に基づく重み調整
    const weights = this.getRiskWeights();
    
    const adjustedScore = 
      drawdownScore * weights.drawdown +
      volatilityScore * weights.volatility +
      correlationScore * weights.correlation +
      riskMetrics.risk_score * weights.base;
    
    return Math.min(Math.max(adjustedScore, 0), 1);
  }

  /**
   * 個別銘柄リスクスコアを計算
   */
  private calculateIndividualStockRiskScore(
    baseRiskScore: number, 
    stockSettings?: RiskCustomizationSettings["individualStockSettings"][string],
  ): number {
    if (!stockSettings) {
      return baseRiskScore;
    }

    let adjustedScore = baseRiskScore;

    // 個別リスクレベルによる調整
    const riskLevelMultipliers = {
      "LOW": 0.7,
      "MEDIUM": 1.0,
      "HIGH": 1.3,
      "CRITICAL": 1.6,
    };

    if (stockSettings.riskLevel) {
      adjustedScore *= riskLevelMultipliers[stockSettings.riskLevel as keyof typeof riskLevelMultipliers] ?? 1.0;
    }

    // ポジションサイズによる調整
    if (stockSettings.maxPositionSize) {
      const positionSizeRisk = Math.min(stockSettings.maxPositionSize / 1000, 1.0);
      adjustedScore = (adjustedScore + positionSizeRisk) / 2;
    }

    return Math.min(Math.max(adjustedScore, 0), 1);
  }

  /**
   * リスクレベルを判定
   */
  private determineRiskLevel(riskScore: number): "VERY_LOW" | "LOW" | "MEDIUM" | "HIGH" | "VERY_HIGH" | "CRITICAL" {
    if (riskScore < 0.2) return "VERY_LOW";
    if (riskScore < 0.4) return "LOW";
    if (riskScore < 0.6) return "MEDIUM";
    if (riskScore < 0.8) return "HIGH";
    if (riskScore < 0.9) return "VERY_HIGH";
    return "CRITICAL";
  }

  /**
   * 個別銘柄リスクレベルを判定
   */
  private determineIndividualStockRiskLevel(riskScore: number): string {
    if (riskScore < 0.3) return "LOW";
    if (riskScore < 0.6) return "MEDIUM";
    if (riskScore < 0.8) return "HIGH";
    return "CRITICAL";
  }

  /**
   * リスク許容度を評価
   */
  private assessRiskTolerance(
    riskMetrics: RiskMetrics, 
    thresholds: ReturnType<typeof this.getRiskThresholds>,
  ): "WITHIN_TOLERANCE" | "APPROACHING_LIMIT" | "EXCEEDED_LIMIT" {
    const drawdownExceeded = riskMetrics.max_drawdown > thresholds.maxDrawdown;
    const volatilityExceeded = riskMetrics.var_95 > thresholds.varTolerance;
    
    if (drawdownExceeded || volatilityExceeded) {
      return "EXCEEDED_LIMIT";
    }
    
    const approachingDrawdown = riskMetrics.max_drawdown > thresholds.maxDrawdown * 0.8;
    const approachingVolatility = riskMetrics.var_95 > thresholds.varTolerance * 0.8;
    
    if (approachingDrawdown || approachingVolatility) {
      return "APPROACHING_LIMIT";
    }
    
    return "WITHIN_TOLERANCE";
  }

  /**
   * 目標リターンを評価
   */
  private assessTargetReturn(riskMetrics: RiskMetrics): "MEETING_TARGET" | "BELOW_TARGET" | "ABOVE_TARGET" {
    const targetReturn = this.settings.targetReturn.annual;
    const currentReturn = riskMetrics.sharpe_ratio * 0.1; // 簡易的なリターン計算
    
    if (currentReturn >= targetReturn * 1.1) {
      return "ABOVE_TARGET";
    } else if (currentReturn >= targetReturn * 0.9) {
      return "MEETING_TARGET";
    } else {
      return "BELOW_TARGET";
    }
  }

  /**
   * リスク調整後リターンを計算
   */
  private calculateRiskAdjustedReturn(expectedReturn: number, riskScore: number): number {
    if (this.settings.targetReturn.riskAdjusted) {
      return expectedReturn / (1 + riskScore);
    }
    return expectedReturn;
  }

  /**
   * 相関リスクスコアを計算
   */
  private calculateCorrelationRiskScore(correlationMatrix: Record<string, number>): number {
    const correlations = Object.values(correlationMatrix);
    if (correlations.length === 0) return 0;
    
    const avgCorrelation = correlations.reduce((sum, corr) => sum + Math.abs(corr), 0) / correlations.length;
    return Math.min(avgCorrelation, 1.0);
  }

  /**
   * リスク重みを取得
   */
  private getRiskWeights() {
    const { level } = this.settings.riskTolerance;
    
    // リスクレベルに応じた重み調整
    const weightProfiles = {
      "VERY_LOW": { drawdown: 0.5, volatility: 0.3, correlation: 0.1, base: 0.1 },
      "LOW": { drawdown: 0.4, volatility: 0.3, correlation: 0.2, base: 0.1 },
      "MEDIUM": { drawdown: 0.3, volatility: 0.3, correlation: 0.2, base: 0.2 },
      "HIGH": { drawdown: 0.2, volatility: 0.3, correlation: 0.3, base: 0.2 },
      "VERY_HIGH": { drawdown: 0.1, volatility: 0.3, correlation: 0.4, base: 0.2 },
      "CRITICAL": { drawdown: 0.1, volatility: 0.2, correlation: 0.4, base: 0.3 },
    };
    
    return weightProfiles[(level as keyof typeof weightProfiles) || "MEDIUM"];
  }

  /**
   * 推奨事項を生成
   */
  private generateRecommendations(
    riskMetrics: RiskMetrics,
    riskLevel: string,
    riskToleranceStatus: string,
    targetReturnStatus: string,
  ): string[] {
    const recommendations: string[] = [];
    
    // リスク許容度に基づく推奨事項
    if (riskToleranceStatus === "EXCEEDED_LIMIT") {
      recommendations.push("リスクが許容範囲を超えています。ポジションサイズを縮小してください。");
    } else if (riskToleranceStatus === "APPROACHING_LIMIT") {
      recommendations.push("リスクが許容範囲に近づいています。注意深く監視してください。");
    }
    
    // 目標リターンに基づく推奨事項
    if (targetReturnStatus === "BELOW_TARGET") {
      recommendations.push("目標リターンを下回っています。投資戦略の見直しを検討してください。");
    } else if (targetReturnStatus === "ABOVE_TARGET") {
      recommendations.push("目標リターンを上回っています。リスク管理を継続してください。");
    }
    
    // リスクレベルに基づく推奨事項
    if (riskLevel === "HIGH" || riskLevel === "VERY_HIGH" || riskLevel === "CRITICAL") {
      recommendations.push("リスクレベルが高いです。分散投資の強化を検討してください。");
    }
    
    return recommendations;
  }

  /**
   * 個別銘柄推奨事項を生成
   */
  private generateIndividualStockRecommendations(
    symbol: string,
    currentPrice: number,
    riskScore: number,
    riskLevel: string,
    stockSettings?: RiskCustomizationSettings["individualStockSettings"][string],
  ): string[] {
    const recommendations: string[] = [];
    
    // 目標価格に関する推奨事項
    if (stockSettings?.targetPrice) {
      const targetReturn = ((stockSettings.targetPrice - currentPrice) / currentPrice) * 100;
      if (targetReturn > 20) {
        recommendations.push("目標価格が高すぎる可能性があります。現実的な目標に調整してください。");
      } else if (targetReturn < 5) {
        recommendations.push("目標価格が低すぎる可能性があります。より高い目標を検討してください。");
      }
    }
    
    // 損切ラインに関する推奨事項
    if (stockSettings?.stopLossPrice) {
      const stopLossReturn = ((currentPrice - stockSettings.stopLossPrice) / currentPrice) * 100;
      if (stopLossReturn > 20) {
        recommendations.push("損切ラインが緩すぎる可能性があります。より厳しい損切を検討してください。");
      } else if (stopLossReturn < 5) {
        recommendations.push("損切ラインが厳しすぎる可能性があります。適切な損切レベルに調整してください。");
      }
    }
    
    // リスクレベルに基づく推奨事項
    if (riskLevel === "HIGH" || riskLevel === "CRITICAL") {
      recommendations.push(`${symbol}のリスクが高いです。ポジションサイズを縮小することを検討してください。`);
    }
    
    return recommendations;
  }
}
