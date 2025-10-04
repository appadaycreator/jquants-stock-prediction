/**
 * 財務指標分析機能の計算ロジック
 * ROE、ROA、PER、PBR等の財務指標の算出・比較
 */

import {
  FinancialData,
  FinancialMetrics,
  FinancialHealthScore,
  IndustryComparison,
  HistoricalAnalysis,
  FinancialTrend,
  IndustryData,
  FinancialCalculationResult,
  FinancialValidationResult,
  FinancialErrorCode,
  ProfitabilityMetrics,
  MarketValuationMetrics,
  SafetyMetrics,
  GrowthMetrics,
} from './types';

export class FinancialCalculator {
  private industryData: Map<string, IndustryData> = new Map();
  private historicalData: Map<string, FinancialTrend[]> = new Map();

  constructor() {
    this.initializeIndustryData();
  }

  /**
   * 財務指標を計算
   */
  calculateMetrics(data: FinancialData): FinancialMetrics {
    const profitability = this.calculateProfitabilityMetrics(data);
    const marketValuation = this.calculateMarketValuationMetrics(data);
    const safety = this.calculateSafetyMetrics(data);
    const growth = this.calculateGrowthMetrics(data);

    return {
      profitability,
      marketValuation,
      safety,
      growth,
    };
  }

  /**
   * 収益性指標を計算
   */
  private calculateProfitabilityMetrics(data: FinancialData): ProfitabilityMetrics {
    const { incomeStatement, balanceSheet } = data;
    
    // ROE計算
    const roe = balanceSheet.equity > 0 
      ? (incomeStatement.netIncome / balanceSheet.equity) * 100 
      : 0;
    
    // ROA計算
    const roa = balanceSheet.totalAssets > 0 
      ? (incomeStatement.netIncome / balanceSheet.totalAssets) * 100 
      : 0;
    
    // 売上高利益率計算
    const profitMargin = incomeStatement.revenue > 0 
      ? (incomeStatement.netIncome / incomeStatement.revenue) * 100 
      : 0;

    // 業界内順位を計算
    const industryData = this.industryData.get(data.industry);
    const roeRanking = industryData ? this.calculateRanking(roe, industryData.companies.map(c => 
      c.balanceSheet.equity > 0 ? (c.incomeStatement.netIncome / c.balanceSheet.equity) * 100 : 0
    )) : 0;
    
    const roaRanking = industryData ? this.calculateRanking(roa, industryData.companies.map(c => 
      c.balanceSheet.totalAssets > 0 ? (c.incomeStatement.netIncome / c.balanceSheet.totalAssets) * 100 : 0
    )) : 0;
    
    const profitMarginRanking = industryData ? this.calculateRanking(profitMargin, industryData.companies.map(c => 
      c.incomeStatement.revenue > 0 ? (c.incomeStatement.netIncome / c.incomeStatement.revenue) * 100 : 0
    )) : 0;

    return {
      roe,
      roeRanking,
      roeTrend: this.calculateTrend(roe, data.symbol),
      roeScore: this.calculateScore(roe, 'roe'),
      
      roa,
      roaRanking,
      roaTrend: this.calculateTrend(roa, data.symbol),
      roaScore: this.calculateScore(roa, 'roa'),
      
      profitMargin,
      profitMarginRanking,
      profitMarginTrend: this.calculateTrend(profitMargin, data.symbol),
      profitMarginScore: this.calculateScore(profitMargin, 'profitMargin'),
    };
  }

  /**
   * 市場評価指標を計算
   */
  private calculateMarketValuationMetrics(data: FinancialData): MarketValuationMetrics {
    const { marketData, incomeStatement, balanceSheet } = data;
    
    // PER計算
    const per = incomeStatement.eps > 0 
      ? marketData.stockPrice / incomeStatement.eps 
      : 0;
    
    // PBR計算
    const pbr = balanceSheet.bps > 0 
      ? marketData.stockPrice / balanceSheet.bps 
      : 0;
    
    // PSR計算
    const psr = incomeStatement.revenue > 0 
      ? marketData.marketCap / incomeStatement.revenue 
      : 0;

    // 業界内順位を計算
    const industryData = this.industryData.get(data.industry);
    const perRanking = industryData ? this.calculateRanking(per, industryData.companies.map(c => 
      c.incomeStatement.eps > 0 ? c.marketData.stockPrice / c.incomeStatement.eps : 0
    )) : 0;
    
    const pbrRanking = industryData ? this.calculateRanking(pbr, industryData.companies.map(c => 
      c.balanceSheet.bps > 0 ? c.marketData.stockPrice / c.balanceSheet.bps : 0
    )) : 0;
    
    const psrRanking = industryData ? this.calculateRanking(psr, industryData.companies.map(c => 
      c.incomeStatement.revenue > 0 ? c.marketData.marketCap / c.incomeStatement.revenue : 0
    )) : 0;

    return {
      per,
      perRanking,
      perStatus: this.getValuationStatus(per, 'per'),
      perScore: this.calculateScore(per, 'per'),
      
      pbr,
      pbrRanking,
      pbrStatus: this.getValuationStatus(pbr, 'pbr'),
      pbrScore: this.calculateScore(pbr, 'pbr'),
      
      psr,
      psrRanking,
      psrStatus: this.getValuationStatus(psr, 'psr'),
      psrScore: this.calculateScore(psr, 'psr'),
    };
  }

  /**
   * 安全性指標を計算
   */
  private calculateSafetyMetrics(data: FinancialData): SafetyMetrics {
    const { balanceSheet } = data;
    
    // 自己資本比率計算
    const equityRatio = balanceSheet.totalAssets > 0 
      ? (balanceSheet.equity / balanceSheet.totalAssets) * 100 
      : 0;
    
    // 流動比率計算
    const currentRatio = balanceSheet.currentLiabilities > 0 
      ? (balanceSheet.currentAssets / balanceSheet.currentLiabilities) * 100 
      : 0;
    
    // 当座比率計算
    const quickRatio = balanceSheet.currentLiabilities > 0 
      ? (balanceSheet.quickAssets / balanceSheet.currentLiabilities) * 100 
      : 0;

    // 業界内順位を計算
    const industryData = this.industryData.get(data.industry);
    const equityRatioRanking = industryData ? this.calculateRanking(equityRatio, industryData.companies.map(c => 
      c.balanceSheet.totalAssets > 0 ? (c.balanceSheet.equity / c.balanceSheet.totalAssets) * 100 : 0
    )) : 0;
    
    const currentRatioRanking = industryData ? this.calculateRanking(currentRatio, industryData.companies.map(c => 
      c.balanceSheet.currentLiabilities > 0 ? (c.balanceSheet.currentAssets / c.balanceSheet.currentLiabilities) * 100 : 0
    )) : 0;
    
    const quickRatioRanking = industryData ? this.calculateRanking(quickRatio, industryData.companies.map(c => 
      c.balanceSheet.currentLiabilities > 0 ? (c.balanceSheet.quickAssets / c.balanceSheet.currentLiabilities) * 100 : 0
    )) : 0;

    return {
      equityRatio,
      equityRatioRanking,
      equityRatioStatus: this.getSafetyStatus(equityRatio, 'equityRatio'),
      equityRatioScore: this.calculateScore(equityRatio, 'equityRatio'),
      
      currentRatio,
      currentRatioRanking,
      currentRatioStatus: this.getSafetyStatus(currentRatio, 'currentRatio'),
      currentRatioScore: this.calculateScore(currentRatio, 'currentRatio'),
      
      quickRatio,
      quickRatioRanking,
      quickRatioStatus: this.getSafetyStatus(quickRatio, 'quickRatio'),
      quickRatioScore: this.calculateScore(quickRatio, 'quickRatio'),
    };
  }

  /**
   * 成長性指標を計算
   */
  private calculateGrowthMetrics(data: FinancialData): GrowthMetrics {
    const { incomeStatement, balanceSheet, previousYear } = data;
    
    // 売上高成長率計算
    const revenueGrowthRate = previousYear.revenue > 0 
      ? ((incomeStatement.revenue - previousYear.revenue) / previousYear.revenue) * 100 
      : 0;
    
    // 利益成長率計算
    const profitGrowthRate = previousYear.netIncome > 0 
      ? ((incomeStatement.netIncome - previousYear.netIncome) / previousYear.netIncome) * 100 
      : 0;
    
    // 資産成長率計算
    const assetGrowthRate = previousYear.totalAssets > 0 
      ? ((balanceSheet.totalAssets - previousYear.totalAssets) / previousYear.totalAssets) * 100 
      : 0;

    // 業界内順位を計算
    const industryData = this.industryData.get(data.industry);
    const revenueGrowthRanking = industryData ? this.calculateRanking(revenueGrowthRate, industryData.companies.map(c => 
      c.previousYear.revenue > 0 ? ((c.incomeStatement.revenue - c.previousYear.revenue) / c.previousYear.revenue) * 100 : 0
    )) : 0;
    
    const profitGrowthRanking = industryData ? this.calculateRanking(profitGrowthRate, industryData.companies.map(c => 
      c.previousYear.netIncome > 0 ? ((c.incomeStatement.netIncome - c.previousYear.netIncome) / c.previousYear.netIncome) * 100 : 0
    )) : 0;
    
    const assetGrowthRanking = industryData ? this.calculateRanking(assetGrowthRate, industryData.companies.map(c => 
      c.previousYear.totalAssets > 0 ? ((c.balanceSheet.totalAssets - c.previousYear.totalAssets) / c.previousYear.totalAssets) * 100 : 0
    )) : 0;

    return {
      revenueGrowthRate,
      revenueGrowthRanking,
      revenueGrowthTrend: this.calculateGrowthTrend(revenueGrowthRate, data.symbol),
      revenueGrowthScore: this.calculateScore(revenueGrowthRate, 'revenueGrowth'),
      
      profitGrowthRate,
      profitGrowthRanking,
      profitGrowthTrend: this.calculateGrowthTrend(profitGrowthRate, data.symbol),
      profitGrowthScore: this.calculateScore(profitGrowthRate, 'profitGrowth'),
      
      assetGrowthRate,
      assetGrowthRanking,
      assetGrowthTrend: this.calculateGrowthTrend(assetGrowthRate, data.symbol),
      assetGrowthScore: this.calculateScore(assetGrowthRate, 'assetGrowth'),
    };
  }

  /**
   * 財務健全性スコアを計算
   */
  calculateHealthScore(metrics: FinancialMetrics): FinancialHealthScore {
    const profitabilityScore = this.calculateProfitabilityScore(metrics.profitability);
    const marketScore = this.calculateMarketScore(metrics.marketValuation);
    const safetyScore = this.calculateSafetyScore(metrics.safety);
    const growthScore = this.calculateGrowthScore(metrics.growth);

    // 重み付き平均で総合スコア算出
    const overallScore = (
      profitabilityScore * 0.3 +
      marketScore * 0.25 +
      safetyScore * 0.25 +
      growthScore * 0.2
    );

    return {
      overallScore,
      profitabilityScore,
      marketScore,
      safetyScore,
      growthScore,
      grade: this.getGrade(overallScore),
      recommendation: this.getRecommendation(overallScore),
      riskLevel: this.getRiskLevel(overallScore),
      strengths: this.identifyStrengths(metrics),
      weaknesses: this.identifyWeaknesses(metrics),
      opportunities: this.identifyOpportunities(metrics),
      threats: this.identifyThreats(metrics),
    };
  }

  /**
   * 収益性スコアを計算
   */
  private calculateProfitabilityScore(profitability: ProfitabilityMetrics): number {
    return (
      profitability.roeScore * 0.4 +
      profitability.roaScore * 0.4 +
      profitability.profitMarginScore * 0.2
    );
  }

  /**
   * 市場評価スコアを計算
   */
  private calculateMarketScore(marketValuation: MarketValuationMetrics): number {
    return (
      marketValuation.perScore * 0.4 +
      marketValuation.pbrScore * 0.4 +
      marketValuation.psrScore * 0.2
    );
  }

  /**
   * 安全性スコアを計算
   */
  private calculateSafetyScore(safety: SafetyMetrics): number {
    return (
      safety.equityRatioScore * 0.5 +
      safety.currentRatioScore * 0.3 +
      safety.quickRatioScore * 0.2
    );
  }

  /**
   * 成長性スコアを計算
   */
  private calculateGrowthScore(growth: GrowthMetrics): number {
    return (
      growth.revenueGrowthScore * 0.4 +
      growth.profitGrowthScore * 0.4 +
      growth.assetGrowthScore * 0.2
    );
  }

  /**
   * 業界比較分析を実行
   */
  calculateIndustryComparison(data: FinancialData, metrics: FinancialMetrics): IndustryComparison {
    const industryData = this.industryData.get(data.industry);
    if (!industryData) {
      throw new Error(`Industry data not found for ${data.industry}`);
    }

    const industryAverage = this.calculateIndustryAverage(industryData);
    const industryMedian = this.calculateIndustryMedian(industryData);
    const industryTop = this.calculateIndustryTop(industryData);
    const industryBottom = this.calculateIndustryBottom(industryData);

    return {
      industry: data.industry,
      industryAverage,
      industryMedian,
      industryTop,
      industryBottom,
      companyRanking: {
        roe: metrics.profitability.roeRanking,
        roa: metrics.profitability.roaRanking,
        per: metrics.marketValuation.perRanking,
        pbr: metrics.marketValuation.pbrRanking,
        overall: this.calculateOverallRanking(metrics, industryData),
      },
      percentile: {
        roe: this.calculatePercentile(metrics.profitability.roe, industryData.companies.map(c => 
          c.balanceSheet.equity > 0 ? (c.incomeStatement.netIncome / c.balanceSheet.equity) * 100 : 0
        )),
        roa: this.calculatePercentile(metrics.profitability.roa, industryData.companies.map(c => 
          c.balanceSheet.totalAssets > 0 ? (c.incomeStatement.netIncome / c.balanceSheet.totalAssets) * 100 : 0
        )),
        per: this.calculatePercentile(metrics.marketValuation.per, industryData.companies.map(c => 
          c.incomeStatement.eps > 0 ? c.marketData.stockPrice / c.incomeStatement.eps : 0
        )),
        pbr: this.calculatePercentile(metrics.marketValuation.pbr, industryData.companies.map(c => 
          c.balanceSheet.bps > 0 ? c.marketData.stockPrice / c.balanceSheet.bps : 0
        )),
        overall: this.calculateOverallPercentile(metrics, industryData),
      },
    };
  }

  /**
   * 時系列分析を実行
   */
  calculateHistoricalAnalysis(symbol: string): HistoricalAnalysis {
    const trends = this.historicalData.get(symbol) || [];
    
    if (trends.length === 0) {
      return {
        trends: [],
        volatility: { roe: 0, roa: 0, per: 0, pbr: 0 },
        stability: 'low',
        consistency: 'low',
      };
    }

    const volatility = this.calculateVolatility(trends);
    const stability = this.calculateStability(volatility);
    const consistency = this.calculateConsistency(trends);

    return {
      trends,
      volatility,
      stability,
      consistency,
    };
  }

  /**
   * 完全な計算結果を取得
   */
  calculateAll(data: FinancialData): FinancialCalculationResult {
    const metrics = this.calculateMetrics(data);
    const healthScore = this.calculateHealthScore(metrics);
    const industryComparison = this.calculateIndustryComparison(data, metrics);
    const historicalAnalysis = this.calculateHistoricalAnalysis(data.symbol);

    return {
      metrics,
      healthScore,
      industryComparison,
      historicalAnalysis,
    };
  }

  /**
   * 業界内順位を計算
   */
  private calculateRanking(value: number, industryValues: number[]): number {
    const sortedValues = industryValues.filter(v => !isNaN(v)).sort((a, b) => b - a);
    const rank = sortedValues.findIndex(v => v <= value) + 1;
    return rank || sortedValues.length;
  }

  /**
   * パーセンタイルを計算
   */
  private calculatePercentile(value: number, industryValues: number[]): number {
    const sortedValues = industryValues.filter(v => !isNaN(v)).sort((a, b) => a - b);
    const index = sortedValues.findIndex(v => v >= value);
    return index >= 0 ? (index / sortedValues.length) * 100 : 100;
  }

  /**
   * スコアを計算
   */
  private calculateScore(value: number, metricType: string): number {
    const thresholds = this.getThresholds(metricType);
    
    if (value >= thresholds.excellent) return 100;
    if (value >= thresholds.good) return 80;
    if (value >= thresholds.fair) return 60;
    if (value >= thresholds.poor) return 40;
    return 20;
  }

  /**
   * 閾値を取得
   */
  private getThresholds(metricType: string): { excellent: number; good: number; fair: number; poor: number } {
    const thresholds: { [key: string]: { excellent: number; good: number; fair: number; poor: number } } = {
      roe: { excellent: 15, good: 10, fair: 5, poor: 0 },
      roa: { excellent: 10, good: 5, fair: 2, poor: 0 },
      profitMargin: { excellent: 10, good: 5, fair: 2, poor: 0 },
      per: { excellent: 10, good: 15, fair: 25, poor: 50 },
      pbr: { excellent: 1, good: 1.5, fair: 2, poor: 3 },
      psr: { excellent: 1, good: 2, fair: 5, poor: 10 },
      equityRatio: { excellent: 50, good: 30, fair: 20, poor: 10 },
      currentRatio: { excellent: 200, good: 150, fair: 100, poor: 50 },
      quickRatio: { excellent: 150, good: 100, fair: 50, poor: 25 },
      revenueGrowth: { excellent: 20, good: 10, fair: 5, poor: 0 },
      profitGrowth: { excellent: 30, good: 15, fair: 5, poor: 0 },
      assetGrowth: { excellent: 15, good: 10, fair: 5, poor: 0 },
    };
    
    return thresholds[metricType] || { excellent: 0, good: 0, fair: 0, poor: 0 };
  }

  /**
   * 評価ステータスを取得
   */
  private getValuationStatus(value: number, metricType: string): 'undervalued' | 'fair' | 'overvalued' {
    const thresholds = this.getThresholds(metricType);
    
    if (value <= thresholds.excellent) return 'undervalued';
    if (value <= thresholds.good) return 'fair';
    return 'overvalued';
  }

  /**
   * 安全性ステータスを取得
   */
  private getSafetyStatus(value: number, metricType: string): 'excellent' | 'good' | 'fair' | 'poor' {
    const thresholds = this.getThresholds(metricType);
    
    if (value >= thresholds.excellent) return 'excellent';
    if (value >= thresholds.good) return 'good';
    if (value >= thresholds.fair) return 'fair';
    return 'poor';
  }

  /**
   * グレードを取得
   */
  private getGrade(score: number): 'A+' | 'A' | 'B+' | 'B' | 'C+' | 'C' | 'D' | 'F' {
    if (score >= 95) return 'A+';
    if (score >= 90) return 'A';
    if (score >= 85) return 'B+';
    if (score >= 80) return 'B';
    if (score >= 75) return 'C+';
    if (score >= 70) return 'C';
    if (score >= 60) return 'D';
    return 'F';
  }

  /**
   * 投資推奨を取得
   */
  private getRecommendation(score: number): 'Strong Buy' | 'Buy' | 'Hold' | 'Sell' | 'Strong Sell' {
    if (score >= 90) return 'Strong Buy';
    if (score >= 80) return 'Buy';
    if (score >= 70) return 'Hold';
    if (score >= 60) return 'Sell';
    return 'Strong Sell';
  }

  /**
   * リスクレベルを取得
   */
  private getRiskLevel(score: number): 'Low' | 'Medium' | 'High' {
    if (score >= 80) return 'Low';
    if (score >= 60) return 'Medium';
    return 'High';
  }

  /**
   * 強みを特定
   */
  private identifyStrengths(metrics: FinancialMetrics): string[] {
    const strengths: string[] = [];
    
    if (metrics.profitability.roe > 15) strengths.push('高いROE');
    if (metrics.profitability.roa > 10) strengths.push('高いROA');
    if (metrics.safety.equityRatio > 50) strengths.push('高い自己資本比率');
    if (metrics.growth.revenueGrowthRate > 20) strengths.push('高い売上成長率');
    
    return strengths;
  }

  /**
   * 弱みを特定
   */
  private identifyWeaknesses(metrics: FinancialMetrics): string[] {
    const weaknesses: string[] = [];
    
    if (metrics.profitability.roe < 5) weaknesses.push('低いROE');
    if (metrics.profitability.roa < 2) weaknesses.push('低いROA');
    if (metrics.safety.equityRatio < 20) weaknesses.push('低い自己資本比率');
    if (metrics.growth.revenueGrowthRate < 0) weaknesses.push('売上減少');
    
    return weaknesses;
  }

  /**
   * 機会を特定
   */
  private identifyOpportunities(metrics: FinancialMetrics): string[] {
    const opportunities: string[] = [];
    
    if (metrics.marketValuation.per < 10) opportunities.push('割安な株価');
    if (metrics.marketValuation.pbr < 1) opportunities.push('PBR1倍以下');
    if (metrics.growth.revenueGrowthRate > 10) opportunities.push('成長市場');
    
    return opportunities;
  }

  /**
   * 脅威を特定
   */
  private identifyThreats(metrics: FinancialMetrics): string[] {
    const threats: string[] = [];
    
    if (metrics.marketValuation.per > 30) threats.push('高PER');
    if (metrics.marketValuation.pbr > 3) threats.push('高PBR');
    if (metrics.safety.currentRatio < 100) threats.push('流動性リスク');
    
    return threats;
  }

  /**
   * 業界データを初期化
   */
  private initializeIndustryData(): void {
    // 実際の実装では、外部データソースから業界データを取得
    // ここではサンプルデータを使用
    const sampleIndustries = ['自動車', '電気機器', '銀行', '小売業', '製薬'];
    
    sampleIndustries.forEach(industry => {
      this.industryData.set(industry, {
        industry,
        companies: [], // 実際の実装では業界内企業のデータを取得
        statistics: {
          average: {} as FinancialMetrics,
          median: {} as FinancialMetrics,
          top25: {} as FinancialMetrics,
          bottom25: {} as FinancialMetrics,
        },
      });
    });
  }

  /**
   * 業界平均を計算
   */
  private calculateIndustryAverage(industryData: IndustryData): FinancialMetrics {
    // 実際の実装では業界内企業の平均値を計算
    return {} as FinancialMetrics;
  }

  /**
   * 業界中央値を計算
   */
  private calculateIndustryMedian(industryData: IndustryData): FinancialMetrics {
    // 実際の実装では業界内企業の中央値を計算
    return {} as FinancialMetrics;
  }

  /**
   * 業界トップを計算
   */
  private calculateIndustryTop(industryData: IndustryData): FinancialMetrics {
    // 実際の実装では業界内企業の上位値を計算
    return {} as FinancialMetrics;
  }

  /**
   * 業界ボトムを計算
   */
  private calculateIndustryBottom(industryData: IndustryData): FinancialMetrics {
    // 実際の実装では業界内企業の下位値を計算
    return {} as FinancialMetrics;
  }

  /**
   * 総合順位を計算
   */
  private calculateOverallRanking(metrics: FinancialMetrics, industryData: IndustryData): number {
    // 実際の実装では総合順位を計算
    return 0;
  }

  /**
   * 総合パーセンタイルを計算
   */
  private calculateOverallPercentile(metrics: FinancialMetrics, industryData: IndustryData): number {
    // 実際の実装では総合パーセンタイルを計算
    return 0;
  }

  /**
   * 変動性を計算
   */
  private calculateVolatility(trends: FinancialTrend[]): { roe: number; roa: number; per: number; pbr: number } {
    // 実際の実装では変動係数を計算
    return { roe: 0, roa: 0, per: 0, pbr: 0 };
  }

  /**
   * 安定性を計算
   */
  private calculateStability(volatility: { roe: number; roa: number; per: number; pbr: number }): 'high' | 'medium' | 'low' {
    // 実際の実装では安定性を判定
    return 'medium';
  }

  /**
   * 一貫性を計算
   */
  private calculateConsistency(trends: FinancialTrend[]): 'high' | 'medium' | 'low' {
    // 実際の実装では一貫性を判定
    return 'medium';
  }

  /**
   * トレンドを計算
   */
  private calculateTrend(value: number, symbol: string): 'improving' | 'stable' | 'declining' {
    // 実際の実装では過去データと比較してトレンドを判定
    return 'stable';
  }

  /**
   * 成長トレンドを計算
   */
  private calculateGrowthTrend(value: number, symbol: string): 'accelerating' | 'stable' | 'decelerating' {
    // 実際の実装では過去データと比較して成長トレンドを判定
    return 'stable';
  }

  /**
   * データの妥当性を検証
   */
  validateData(data: FinancialData): FinancialValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];

    // 基本データの検証
    if (!data.symbol || !data.companyName) {
      errors.push('銘柄情報が不足しています');
    }

    if (data.incomeStatement.revenue <= 0) {
      errors.push('売上高が無効です');
    }

    if (data.balanceSheet.totalAssets <= 0) {
      errors.push('総資産が無効です');
    }

    if (data.marketData.stockPrice <= 0) {
      errors.push('株価が無効です');
    }

    // 警告の検証
    if (data.incomeStatement.netIncome < 0) {
      warnings.push('当期純利益がマイナスです');
    }

    if (data.balanceSheet.equity <= 0) {
      warnings.push('自己資本がマイナスまたはゼロです');
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings,
    };
  }
}
