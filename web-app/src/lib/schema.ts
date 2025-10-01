/**
 * Zodスキーマ定義
 * APIレスポンスの厳格な検証
 */

import { z } from "zod";

// 予測ポイントのスキーマ
export const PredictionPoint = z.object({
  date: z.string(),
  symbol: z.string().min(4),
  y_true: z.number().finite(),
  y_pred: z.number().finite(),
});

// 予測結果レスポンスのスキーマ
export const PredictionResponse = z.object({
  meta: z.object({
    model: z.string(),
    generatedAt: z.string(),
  }).optional(),
  data: z.array(PredictionPoint).min(1),
});

// 株価データのスキーマ
export const StockData = z.object({
  date: z.string(),
  close: z.number().finite(),
  sma_5: z.number().finite().optional(),
  sma_10: z.number().finite().optional(),
  sma_25: z.number().finite().optional(),
  sma_50: z.number().finite().optional(),
  volume: z.number().finite(),
  predicted: z.number().finite().optional(),
});

// モデル比較データのスキーマ
export const ModelComparison = z.object({
  model_name: z.string(),
  model_type: z.string(),
  mae: z.number().finite(),
  rmse: z.number().finite(),
  r2: z.number().finite(),
  rank: z.number().int().min(1),
});

// ダッシュボードサマリーのスキーマ
export const DashboardSummary = z.object({
  total_stocks: z.number().int().min(0),
  total_predictions: z.number().int().min(0),
  last_updated: z.string(),
  model_performance: z.object({
    best_model: z.string(),
    accuracy: z.number().min(0).max(1),
    mae: z.number().finite(),
    rmse: z.number().finite(),
  }),
});

// 特徴量分析のスキーマ
export const FeatureAnalysis = z.object({
  feature: z.string(),
  importance: z.number().min(0).max(1),
  percentage: z.number().min(0).max(100),
});

// 市場インサイトのスキーマ
export const MarketInsights = z.object({
  market_trend: z.string(),
  volatility: z.number().finite(),
  recommendations: z.array(z.string()),
  risk_level: z.enum(["低", "中", "高"]),
});

// リスク評価のスキーマ
export const RiskAssessment = z.object({
  overall_risk: z.enum(["低", "中", "高"]),
  portfolio_value: z.number().finite(),
  var_95: z.number().finite(),
  max_drawdown: z.number().finite(),
  sharpe_ratio: z.number().finite(),
});

// 型エクスポート
export type PredictionPointType = z.infer<typeof PredictionPoint>;
export type PredictionResponseType = z.infer<typeof PredictionResponse>;
export type StockDataType = z.infer<typeof StockData>;
export type ModelComparisonType = z.infer<typeof ModelComparison>;
export type DashboardSummaryType = z.infer<typeof DashboardSummary>;
export type FeatureAnalysisType = z.infer<typeof FeatureAnalysis>;
export type MarketInsightsType = z.infer<typeof MarketInsights>;
export type RiskAssessmentType = z.infer<typeof RiskAssessment>;
