/**
 * 財務指標計算機能のテスト
 */

import { FinancialCalculator } from '../calculator';
import { FinancialData } from '../types';

describe('FinancialCalculator', () => {
  let calculator: FinancialCalculator;
  let sampleData: FinancialData;

  beforeEach(() => {
    calculator = new FinancialCalculator();
    sampleData = {
      symbol: 'TEST',
      companyName: 'テスト企業',
      industry: '電気機器',
      fiscalYear: 2024,
      incomeStatement: {
        revenue: 1000000000,      // 10億円
        operatingIncome: 100000000, // 1億円
        netIncome: 80000000,      // 8000万円
        eps: 100,                 // 100円
      },
      balanceSheet: {
        totalAssets: 2000000000,   // 20億円
        currentAssets: 800000000,  // 8億円
        quickAssets: 600000000,     // 6億円
        totalLiabilities: 1200000000, // 12億円
        currentLiabilities: 400000000, // 4億円
        equity: 800000000,         // 8億円
        bps: 1000,                 // 1000円
      },
      marketData: {
        stockPrice: 1500,         // 1500円
        marketCap: 15000000000,   // 150億円
        sharesOutstanding: 10000000, // 1000万株
      },
      previousYear: {
        revenue: 900000000,      // 9億円
        netIncome: 70000000,       // 7000万円
        totalAssets: 1800000000,   // 18億円
      },
    };
  });

  describe('calculateMetrics', () => {
    it('収益性指標を正しく計算する', () => {
      const metrics = calculator.calculateMetrics(sampleData);
      
      // ROE計算: 当期純利益 / 自己資本 × 100
      expect(metrics.profitability.roe).toBeCloseTo(10, 1); // 8000万 / 8億 × 100 = 10%
      
      // ROA計算: 当期純利益 / 総資産 × 100
      expect(metrics.profitability.roa).toBeCloseTo(4, 1); // 8000万 / 20億 × 100 = 4%
      
      // 売上高利益率計算: 当期純利益 / 売上高 × 100
      expect(metrics.profitability.profitMargin).toBeCloseTo(8, 1); // 8000万 / 10億 × 100 = 8%
    });

    it('市場評価指標を正しく計算する', () => {
      const metrics = calculator.calculateMetrics(sampleData);
      
      // PER計算: 株価 / 1株当たり純利益
      expect(metrics.marketValuation.per).toBeCloseTo(15, 1); // 1500 / 100 = 15
      
      // PBR計算: 株価 / 1株当たり純資産
      expect(metrics.marketValuation.pbr).toBeCloseTo(1.5, 1); // 1500 / 1000 = 1.5
      
      // PSR計算: 時価総額 / 売上高
      expect(metrics.marketValuation.psr).toBeCloseTo(15, 1); // 150億 / 10億 = 15
    });

    it('安全性指標を正しく計算する', () => {
      const metrics = calculator.calculateMetrics(sampleData);
      
      // 自己資本比率計算: 自己資本 / 総資産 × 100
      expect(metrics.safety.equityRatio).toBeCloseTo(40, 1); // 8億 / 20億 × 100 = 40%
      
      // 流動比率計算: 流動資産 / 流動負債 × 100
      expect(metrics.safety.currentRatio).toBeCloseTo(200, 1); // 8億 / 4億 × 100 = 200%
      
      // 当座比率計算: 当座資産 / 流動負債 × 100
      expect(metrics.safety.quickRatio).toBeCloseTo(150, 1); // 6億 / 4億 × 100 = 150%
    });

    it('成長性指標を正しく計算する', () => {
      const metrics = calculator.calculateMetrics(sampleData);
      
      // 売上高成長率計算: (当期売上高 - 前期売上高) / 前期売上高 × 100
      expect(metrics.growth.revenueGrowthRate).toBeCloseTo(11.1, 1); // (10億 - 9億) / 9億 × 100 = 11.1%
      
      // 利益成長率計算: (当期純利益 - 前期純利益) / 前期純利益 × 100
      expect(metrics.growth.profitGrowthRate).toBeCloseTo(14.3, 1); // (8000万 - 7000万) / 7000万 × 100 = 14.3%
      
      // 資産成長率計算: (当期総資産 - 前期総資産) / 前期総資産 × 100
      expect(metrics.growth.assetGrowthRate).toBeCloseTo(11.1, 1); // (20億 - 18億) / 18億 × 100 = 11.1%
    });
  });

  describe('calculateHealthScore', () => {
    it('財務健全性スコアを正しく計算する', () => {
      const metrics = calculator.calculateMetrics(sampleData);
      const healthScore = calculator.calculateHealthScore(metrics);
      
      expect(healthScore.overallScore).toBeGreaterThan(0);
      expect(healthScore.overallScore).toBeLessThanOrEqual(100);
      expect(healthScore.profitabilityScore).toBeGreaterThan(0);
      expect(healthScore.marketScore).toBeGreaterThan(0);
      expect(healthScore.safetyScore).toBeGreaterThan(0);
      expect(healthScore.growthScore).toBeGreaterThan(0);
    });

    it('グレードを正しく判定する', () => {
      const metrics = calculator.calculateMetrics(sampleData);
      const healthScore = calculator.calculateHealthScore(metrics);
      
      expect(['A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'F']).toContain(healthScore.grade);
    });

    it('投資推奨を正しく判定する', () => {
      const metrics = calculator.calculateMetrics(sampleData);
      const healthScore = calculator.calculateHealthScore(metrics);
      
      expect(['Strong Buy', 'Buy', 'Hold', 'Sell', 'Strong Sell']).toContain(healthScore.recommendation);
    });

    it('リスクレベルを正しく判定する', () => {
      const metrics = calculator.calculateMetrics(sampleData);
      const healthScore = calculator.calculateHealthScore(metrics);
      
      expect(['Low', 'Medium', 'High']).toContain(healthScore.riskLevel);
    });
  });

  describe('validateData', () => {
    it('有効なデータを正しく検証する', () => {
      const validation = calculator.validateData(sampleData);
      
      expect(validation.isValid).toBe(true);
      expect(validation.errors).toHaveLength(0);
    });

    it('無効なデータを正しく検証する', () => {
      const invalidData = {
        ...sampleData,
        symbol: '',
        incomeStatement: {
          ...sampleData.incomeStatement,
          revenue: 0,
        },
      };
      
      const validation = calculator.validateData(invalidData);
      
      expect(validation.isValid).toBe(false);
      expect(validation.errors.length).toBeGreaterThan(0);
    });

    it('警告を正しく検出する', () => {
      const warningData = {
        ...sampleData,
        incomeStatement: {
          ...sampleData.incomeStatement,
          netIncome: -1000000, // マイナス利益
        },
      };
      
      const validation = calculator.validateData(warningData);
      
      expect(validation.warnings.length).toBeGreaterThan(0);
    });
  });

  describe('calculateAll', () => {
    it('完全な計算結果を正しく生成する', () => {
      const result = calculator.calculateAll(sampleData);
      
      expect(result.metrics).toBeDefined();
      expect(result.healthScore).toBeDefined();
      expect(result.industryComparison).toBeDefined();
      expect(result.historicalAnalysis).toBeDefined();
    });
  });

  describe('エラーハンドリング', () => {
    it('ゼロ除算を正しく処理する', () => {
      const zeroData = {
        ...sampleData,
        balanceSheet: {
          ...sampleData.balanceSheet,
          equity: 0,
        },
      };
      
      const metrics = calculator.calculateMetrics(zeroData);
      
      expect(metrics.profitability.roe).toBe(0);
    });

    it('無効なデータを正しく処理する', () => {
      const invalidData = {
        ...sampleData,
        incomeStatement: {
          ...sampleData.incomeStatement,
          revenue: -1000000,
        },
      };
      
      const metrics = calculator.calculateMetrics(invalidData);
      
      expect(metrics.profitability.profitMargin).toBe(0);
    });
  });
});
