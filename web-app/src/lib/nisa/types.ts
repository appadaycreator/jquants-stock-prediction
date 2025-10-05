/**
 * 新NISA枠管理機能の型定義
 * 2024年1月開始の新NISA制度に対応
 */

// 基本定数
export const NISA_CONSTANTS = {
  GROWTH_ANNUAL_LIMIT: 2_400_000,      // 成長投資枠年間投資枠
  GROWTH_TAX_FREE_LIMIT: 12_000_000,   // 成長投資枠非課税保有限度額
  ACCUMULATION_ANNUAL_LIMIT: 400_000,  // つみたて投資枠年間投資枠
  ACCUMULATION_TAX_FREE_LIMIT: 2_000_000, // つみたて投資枠非課税保有限度額
} as const;

// 投資枠タイプ
export type QuotaType = "GROWTH" | "ACCUMULATION";

// 取引タイプ
export type TransactionType = "BUY" | "SELL";

// リスクレベル
export type RiskLevel = "LOW" | "MEDIUM" | "HIGH";

// 優先度
export type Priority = "HIGH" | "MEDIUM" | "LOW";

// アラートタイプ
export type AlertType = "WARNING" | "CRITICAL" | "INFO";

// 投資枠利用状況
export interface NisaQuotaStatus {
  growthInvestment: {
    annualLimit: number;
    taxFreeLimit: number;
    usedAmount: number;
    availableAmount: number;
    utilizationRate: number;
  };
  accumulationInvestment: {
    annualLimit: number;
    taxFreeLimit: number;
    usedAmount: number;
    availableAmount: number;
    utilizationRate: number;
  };
  quotaReuse: {
    growthAvailable: number;
    accumulationAvailable: number;
    nextYearAvailable: number;
  };
}

// 取引記録
export interface NisaTransaction {
  id: string;
  type: TransactionType;
  symbol: string;
  symbolName: string;
  quantity: number;
  price: number;
  amount: number;
  quotaType: QuotaType;
  transactionDate: string;
  profitLoss?: number;
  taxFreeAmount?: number;
  createdAt: string;
  updatedAt: string;
}

// ポートフォリオポジション
export interface NisaPosition {
  symbol: string;
  symbolName: string;
  quantity: number;
  averagePrice: number;
  currentPrice: number;
  cost: number;
  currentValue: number;
  unrealizedProfitLoss: number;
  quotaType: QuotaType;
  purchaseDate: string;
  lastUpdated: string;
}

// ポートフォリオ
export interface NisaPortfolio {
  positions: NisaPosition[];
  totalValue: number;
  totalCost: number;
  unrealizedProfitLoss: number;
  realizedProfitLoss: number;
  taxFreeProfitLoss: number;
  lastUpdated: string;
}

// 枠最適化提案
export interface QuotaOptimization {
  recommendations: {
    growthQuota: {
      suggestedAmount: number;
      reason: string;
      priority: Priority;
    };
    accumulationQuota: {
      suggestedAmount: number;
      reason: string;
      priority: Priority;
    };
  };
  riskAnalysis: {
    diversificationScore: number;
    sectorConcentration: number;
    riskLevel: RiskLevel;
  };
  lastCalculated: string;
}

// 税務計算
export interface TaxCalculation {
  currentYear: {
    growthQuotaUsed: number;
    accumulationQuotaUsed: number;
    totalTaxFreeAmount: number;
  };
  nextYear: {
    availableGrowthQuota: number;
    availableAccumulationQuota: number;
    reusableQuota: number;
  };
  taxSavings: {
    estimatedTaxSavings: number;
    taxRate: number;
    effectiveTaxRate: number;
  };
  calculatedAt: string;
}

// アラート
export interface QuotaAlert {
  id: string;
  type: AlertType;
  message: string;
  quotaType: QuotaType;
  currentUsage: number;
  threshold: number;
  recommendedAction: string;
  createdAt: string;
  isRead: boolean;
}

// 投資機会
export interface InvestmentOpportunity {
  id: string;
  symbol: string;
  symbolName: string;
  reason: string;
  expectedReturn: number;
  riskLevel: RiskLevel;
  quotaRecommendation: QuotaType;
  suggestedAmount: number;
  confidence: number;
  createdAt: string;
}

// ユーザープロファイル
export interface NisaUserProfile {
  userId: string;
  startDate: string;
  taxYear: number;
  preferences: {
    autoRebalancing: boolean;
    alertThresholds: {
      growthWarning: number;
      accumulationWarning: number;
    };
    notifications: {
      email: boolean;
      browser: boolean;
      push: boolean;
    };
  };
  createdAt: string;
  updatedAt: string;
}

// 設定
export interface NisaSettings {
  autoRebalancing: boolean;
  alertThresholds: {
    growthWarning: number;
    accumulationWarning: number;
  };
  notifications: {
    email: boolean;
    browser: boolean;
    push: boolean;
  };
}

// メインデータ構造
export interface NisaData {
  userProfile: NisaUserProfile;
  quotas: NisaQuotaStatus;
  transactions: NisaTransaction[];
  portfolio: NisaPortfolio;
  settings: NisaSettings;
  lastUpdated: string;
}

// APIレスポンス
export interface NisaApiResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
  metadata: {
    timestamp: string;
    version: string;
  };
}

// 計算結果
export interface NisaCalculationResult {
  quotas: NisaQuotaStatus;
  portfolio: NisaPortfolio;
  optimization: QuotaOptimization;
  taxCalculation: TaxCalculation;
  alerts: QuotaAlert[];
  opportunities: InvestmentOpportunity[];
}

// エラーコード
export enum NisaErrorCode {
  INVALID_QUOTA_TYPE = "INVALID_QUOTA_TYPE",
  QUOTA_EXCEEDED = "QUOTA_EXCEEDED",
  INVALID_TRANSACTION = "INVALID_TRANSACTION",
  CALCULATION_ERROR = "CALCULATION_ERROR",
  DATA_NOT_FOUND = "DATA_NOT_FOUND",
  VALIDATION_ERROR = "VALIDATION_ERROR",
}

// バリデーション結果
export interface ValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

// 統計情報
export interface NisaStatistics {
  totalInvested: number;
  totalValue: number;
  totalProfitLoss: number;
  totalTaxFreeProfitLoss: number;
  averageReturn: number;
  bestPerformer: {
    symbol: string;
    symbolName: string;
    return: number;
  };
  worstPerformer: {
    symbol: string;
    symbolName: string;
    return: number;
  };
  diversificationScore: number;
  riskScore: number;
}
