/**
 * 財務指標分析機能の型定義
 * ROE、ROA、PER、PBR等の財務指標の算出・比較
 */

// 基本財務指標
export interface FinancialMetrics {
  // 収益性指標
  profitability: ProfitabilityMetrics;
  // 市場評価指標
  marketValuation: MarketValuationMetrics;
  // 安全性指標
  safety: SafetyMetrics;
  // 成長性指標
  growth: GrowthMetrics;
}

// 収益性指標
export interface ProfitabilityMetrics {
  roe: number;                    // 自己資本利益率
  roeRanking: number;            // 業界内順位
  roeTrend: "improving" | "stable" | "declining";
  roeScore: number;              // スコア (0-100)
  
  roa: number;                   // 総資産利益率
  roaRanking: number;            // 業界内順位
  roaTrend: "improving" | "stable" | "declining";
  roaScore: number;              // スコア (0-100)
  
  profitMargin: number;          // 売上高利益率
  profitMarginRanking: number;   // 業界内順位
  profitMarginTrend: "improving" | "stable" | "declining";
  profitMarginScore: number;     // スコア (0-100)
}

// 市場評価指標
export interface MarketValuationMetrics {
  per: number;                   // 株価収益率
  perRanking: number;            // 業界内順位
  perStatus: "undervalued" | "fair" | "overvalued";
  perScore: number;              // スコア (0-100)
  
  pbr: number;                   // 株価純資産倍率
  pbrRanking: number;            // 業界内順位
  pbrStatus: "undervalued" | "fair" | "overvalued";
  pbrScore: number;              // スコア (0-100)
  
  psr: number;                   // 株価売上高倍率
  psrRanking: number;            // 業界内順位
  psrStatus: "undervalued" | "fair" | "overvalued";
  psrScore: number;              // スコア (0-100)
}

// 安全性指標
export interface SafetyMetrics {
  equityRatio: number;           // 自己資本比率
  equityRatioRanking: number;    // 業界内順位
  equityRatioStatus: "excellent" | "good" | "fair" | "poor";
  equityRatioScore: number;      // スコア (0-100)
  
  currentRatio: number;          // 流動比率
  currentRatioRanking: number;   // 業界内順位
  currentRatioStatus: "excellent" | "good" | "fair" | "poor";
  currentRatioScore: number;     // スコア (0-100)
  
  quickRatio: number;            // 当座比率
  quickRatioRanking: number;     // 業界内順位
  quickRatioStatus: "excellent" | "good" | "fair" | "poor";
  quickRatioScore: number;       // スコア (0-100)
}

// 成長性指標
export interface GrowthMetrics {
  revenueGrowthRate: number;     // 売上高成長率
  revenueGrowthRanking: number;  // 業界内順位
  revenueGrowthTrend: "accelerating" | "stable" | "decelerating";
  revenueGrowthScore: number; // スコア (0-100)
  
  profitGrowthRate: number;      // 利益成長率
  profitGrowthRanking: number;   // 業界内順位
  profitGrowthTrend: "accelerating" | "stable" | "decelerating";
  profitGrowthScore: number;    // スコア (0-100)
  
  assetGrowthRate: number;       // 資産成長率
  assetGrowthRanking: number;    // 業界内順位
  assetGrowthTrend: "accelerating" | "stable" | "decelerating";
  assetGrowthScore: number;      // スコア (0-100)
}

// 総合評価指標
export interface FinancialHealthScore {
  overallScore: number;           // 総合スコア (0-100)
  profitabilityScore: number;    // 収益性スコア (0-100)
  marketScore: number;           // 市場評価スコア (0-100)
  safetyScore: number;           // 安全性スコア (0-100)
  growthScore: number;           // 成長性スコア (0-100)
  
  grade: "A+" | "A" | "B+" | "B" | "C+" | "C" | "D" | "F";
  recommendation: "Strong Buy" | "Buy" | "Hold" | "Sell" | "Strong Sell";
  riskLevel: "Low" | "Medium" | "High";
  
  strengths: string[];           // 強み
  weaknesses: string[];          // 弱み
  opportunities: string[];       // 機会
  threats: string[];            // 脅威
}

// 業界比較分析
export interface IndustryComparison {
  industry: string;              // 業界名
  industryAverage: FinancialMetrics; // 業界平均
  industryMedian: FinancialMetrics;  // 業界中央値
  industryTop: FinancialMetrics;     // 業界トップ
  industryBottom: FinancialMetrics; // 業界ボトム
  
  companyRanking: {
    roe: number;                 // ROE業界内順位
    roa: number;                 // ROA業界内順位
    per: number;                 // PER業界内順位
    pbr: number;                 // PBR業界内順位
    overall: number;             // 総合順位
  };
  
  percentile: {
    roe: number;                 // ROEパーセンタイル
    roa: number;                 // ROAパーセンタイル
    per: number;                 // PERパーセンタイル
    pbr: number;                 // PBRパーセンタイル
    overall: number;             // 総合パーセンタイル
  };
}

// 時系列分析
export interface FinancialTrend {
  period: string;                // 期間
  metrics: FinancialMetrics;     // 財務指標
  change: {
    roe: number;                // ROE変化率
    roa: number;                // ROA変化率
    per: number;                // PER変化率
    pbr: number;                // PBR変化率
  };
}

export interface HistoricalAnalysis {
  trends: FinancialTrend[];      // 過去の財務指標推移
  volatility: {
    roe: number;                 // ROE変動係数
    roa: number;                 // ROA変動係数
    per: number;                 // PER変動係数
    pbr: number;                 // PBR変動係数
  };
  stability: "high" | "medium" | "low";
  consistency: "high" | "medium" | "low";
}

// 財務データ
export interface FinancialData {
  symbol: string;                // 銘柄コード
  companyName: string;           // 会社名
  industry: string;              // 業界
  fiscalYear: number;            // 会計年度
  
  // 損益計算書データ
  incomeStatement: {
    revenue: number;             // 売上高
    operatingIncome: number;     // 営業利益
    netIncome: number;           // 当期純利益
    eps: number;                 // 1株当たり純利益
  };
  
  // 貸借対照表データ
  balanceSheet: {
    totalAssets: number;         // 総資産
    currentAssets: number;       // 流動資産
    quickAssets: number;         // 当座資産
    totalLiabilities: number;    // 総負債
    currentLiabilities: number;  // 流動負債
    equity: number;              // 自己資本
    bps: number;                 // 1株当たり純資産
  };
  
  // 市場データ
  marketData: {
    stockPrice: number;          // 株価
    marketCap: number;           // 時価総額
    sharesOutstanding: number;   // 発行済み株式数
  };
  
  // 前年度データ（成長率計算用）
  previousYear: {
    revenue: number;
    netIncome: number;
    totalAssets: number;
  };
}

// 業界データ
export interface IndustryData {
  industry: string;              // 業界名
  companies: FinancialData[];    // 業界内企業の財務データ
  statistics: {
    average: FinancialMetrics;   // 業界平均
    median: FinancialMetrics;    // 業界中央値
    top25: FinancialMetrics;      // 上位25%
    bottom25: FinancialMetrics;  // 下位25%
  };
}

// APIレスポンス
export interface FinancialAnalysisResponse {
  success: boolean;
  data?: {
    metrics: FinancialMetrics;
    healthScore: FinancialHealthScore;
    industryComparison: IndustryComparison;
    historicalAnalysis: HistoricalAnalysis;
  };
  error?: {
    code: string;
    message: string;
    details?: any;
  };
  metadata: {
    timestamp: string;
    version: string;
    calculationTime: number;
  };
}

// 計算結果
export interface FinancialCalculationResult {
  metrics: FinancialMetrics;
  healthScore: FinancialHealthScore;
  industryComparison: IndustryComparison;
  historicalAnalysis: HistoricalAnalysis;
}

// エラーコード
export enum FinancialErrorCode {
  INVALID_DATA = "INVALID_DATA",
  CALCULATION_ERROR = "CALCULATION_ERROR",
  DATA_NOT_FOUND = "DATA_NOT_FOUND",
  INDUSTRY_NOT_FOUND = "INDUSTRY_NOT_FOUND",
  VALIDATION_ERROR = "VALIDATION_ERROR",
}

// バリデーション結果
export interface FinancialValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

// 統計情報
export interface FinancialStatistics {
  totalCompanies: number;
  industryCount: number;
  averageMetrics: FinancialMetrics;
  topPerformers: {
    roe: string[];
    roa: string[];
    per: string[];
    pbr: string[];
  };
  worstPerformers: {
    roe: string[];
    roa: string[];
    per: string[];
    pbr: string[];
  };
}

// 設定
export interface FinancialAnalysisSettings {
  weights: {
    profitability: number;        // 収益性の重み
    market: number;              // 市場評価の重み
    safety: number;              // 安全性の重み
    growth: number;              // 成長性の重み
  };
  thresholds: {
    roe: { excellent: number; good: number; fair: number; };
    roa: { excellent: number; good: number; fair: number; };
    per: { undervalued: number; fair: number; overvalued: number; };
    pbr: { undervalued: number; fair: number; overvalued: number; };
  };
  industryClassification: {
    [key: string]: string[];     // 業界分類マッピング
  };
}
