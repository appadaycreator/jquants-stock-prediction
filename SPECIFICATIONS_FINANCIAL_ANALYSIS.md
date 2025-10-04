# 財務指標分析機能 仕様書

## 1. 機能概要

### 1.1 目的
企業の財務健全性を定量的に評価するための財務指標分析機能を提供し、投資判断の精度向上をサポートする。

### 1.2 主要機能
- **財務指標の算出**: ROE、ROA、PER、PBR等の基本財務指標の計算
- **業界比較分析**: 同業他社との財務指標比較
- **時系列分析**: 過去の財務指標推移の可視化
- **総合評価**: 複数指標を統合した財務健全性スコアの算出
- **投資判断支援**: 財務指標に基づく投資推奨の生成

## 2. 財務指標仕様

### 2.1 基本財務指標

#### 2.1.1 収益性指標
```typescript
interface ProfitabilityMetrics {
  // 自己資本利益率
  roe: number;                    // ROE = 当期純利益 / 自己資本 × 100
  roeRanking: number;            // 業界内順位
  roeTrend: 'improving' | 'stable' | 'declining';
  
  // 総資産利益率
  roa: number;                   // ROA = 当期純利益 / 総資産 × 100
  roaRanking: number;            // 業界内順位
  roaTrend: 'improving' | 'stable' | 'declining';
  
  // 売上高利益率
  profitMargin: number;          // 売上高利益率 = 当期純利益 / 売上高 × 100
  profitMarginRanking: number;   // 業界内順位
  profitMarginTrend: 'improving' | 'stable' | 'declining';
}
```

#### 2.1.2 市場評価指標
```typescript
interface MarketValuationMetrics {
  // 株価収益率
  per: number;                   // PER = 株価 / 1株当たり純利益
  perRanking: number;            // 業界内順位
  perStatus: 'undervalued' | 'fair' | 'overvalued';
  
  // 株価純資産倍率
  pbr: number;                   // PBR = 株価 / 1株当たり純資産
  pbrRanking: number;            // 業界内順位
  pbrStatus: 'undervalued' | 'fair' | 'overvalued';
  
  // 株価売上高倍率
  psr: number;                   // PSR = 時価総額 / 売上高
  psrRanking: number;            // 業界内順位
  psrStatus: 'undervalued' | 'fair' | 'overvalued';
}
```

#### 2.1.3 安全性指標
```typescript
interface SafetyMetrics {
  // 自己資本比率
  equityRatio: number;           // 自己資本比率 = 自己資本 / 総資産 × 100
  equityRatioRanking: number;    // 業界内順位
  equityRatioStatus: 'excellent' | 'good' | 'fair' | 'poor';
  
  // 流動比率
  currentRatio: number;          // 流動比率 = 流動資産 / 流動負債 × 100
  currentRatioRanking: number;   // 業界内順位
  currentRatioStatus: 'excellent' | 'good' | 'fair' | 'poor';
  
  // 当座比率
  quickRatio: number;            // 当座比率 = 当座資産 / 流動負債 × 100
  quickRatioRanking: number;     // 業界内順位
  quickRatioStatus: 'excellent' | 'good' | 'fair' | 'poor';
}
```

#### 2.1.4 成長性指標
```typescript
interface GrowthMetrics {
  // 売上高成長率
  revenueGrowthRate: number;     // 売上高成長率 = (当期売上高 - 前期売上高) / 前期売上高 × 100
  revenueGrowthRanking: number;  // 業界内順位
  revenueGrowthTrend: 'accelerating' | 'stable' | 'decelerating';
  
  // 利益成長率
  profitGrowthRate: number;      // 利益成長率 = (当期純利益 - 前期純利益) / 前期純利益 × 100
  profitGrowthRanking: number;   // 業界内順位
  profitGrowthTrend: 'accelerating' | 'stable' | 'decelerating';
  
  // 資産成長率
  assetGrowthRate: number;       // 資産成長率 = (当期総資産 - 前期総資産) / 前期総資産 × 100
  assetGrowthRanking: number;    // 業界内順位
  assetGrowthTrend: 'accelerating' | 'stable' | 'decelerating';
}
```

### 2.2 総合評価指標

#### 2.2.1 財務健全性スコア
```typescript
interface FinancialHealthScore {
  overallScore: number;           // 総合スコア (0-100)
  profitabilityScore: number;    // 収益性スコア (0-100)
  marketScore: number;           // 市場評価スコア (0-100)
  safetyScore: number;           // 安全性スコア (0-100)
  growthScore: number;           // 成長性スコア (0-100)
  
  grade: 'A+' | 'A' | 'B+' | 'B' | 'C+' | 'C' | 'D' | 'F';
  recommendation: 'Strong Buy' | 'Buy' | 'Hold' | 'Sell' | 'Strong Sell';
  riskLevel: 'Low' | 'Medium' | 'High';
}
```

#### 2.2.2 業界比較分析
```typescript
interface IndustryComparison {
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
}
```

### 2.3 時系列分析

#### 2.3.1 財務指標推移
```typescript
interface FinancialTrend {
  period: string;                // 期間
  metrics: FinancialMetrics;     // 財務指標
  change: {
    roe: number;                // ROE変化率
    roa: number;                // ROA変化率
    per: number;                // PER変化率
    pbr: number;                // PBR変化率
  };
}

interface HistoricalAnalysis {
  trends: FinancialTrend[];      // 過去の財務指標推移
  volatility: {
    roe: number;                 // ROE変動係数
    roa: number;                 // ROA変動係数
    per: number;                 // PER変動係数
    pbr: number;                 // PBR変動係数
  };
  stability: 'high' | 'medium' | 'low';
}
```

## 3. データ構造

### 3.1 財務データ
```typescript
interface FinancialData {
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
```

### 3.2 業界データ
```typescript
interface IndustryData {
  industry: string;              // 業界名
  companies: FinancialData[];    // 業界内企業の財務データ
  statistics: {
    average: FinancialMetrics;   // 業界平均
    median: FinancialMetrics;    // 業界中央値
    top25: FinancialMetrics;      // 上位25%
    bottom25: FinancialMetrics;  // 下位25%
  };
}
```

## 4. API仕様

### 4.1 エンドポイント
```
GET /api/financial/analysis/:symbol          # 財務指標分析取得
GET /api/financial/industry/:industry        # 業界比較分析取得
GET /api/financial/trend/:symbol            # 時系列分析取得
POST /api/financial/calculate               # 財務指標計算実行
GET /api/financial/health/:symbol           # 財務健全性スコア取得
```

### 4.2 レスポンス形式
```typescript
interface FinancialAnalysisResponse {
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
```

## 5. UI/UX仕様

### 5.1 財務指標ダッシュボード
1. **総合スコア表示**
   - 財務健全性スコア（0-100）
   - グレード（A+〜F）
   - 投資推奨（Strong Buy〜Strong Sell）

2. **指標別詳細表示**
   - 収益性指標（ROE、ROA、売上高利益率）
   - 市場評価指標（PER、PBR、PSR）
   - 安全性指標（自己資本比率、流動比率、当座比率）
   - 成長性指標（売上高成長率、利益成長率、資産成長率）

3. **業界比較表示**
   - 業界内順位
   - 業界平均との比較
   - 業界内ポジション

4. **時系列推移表示**
   - 過去5年間の財務指標推移
   - トレンド分析
   - 変動性分析

### 5.2 モバイル対応
- レスポンシブデザイン
- タッチ操作最適化
- 重要な指標の優先表示

## 6. 計算ロジック

### 6.1 基本財務指標の計算
```typescript
// ROE計算
const calculateROE = (netIncome: number, equity: number): number => {
  return equity > 0 ? (netIncome / equity) * 100 : 0;
};

// ROA計算
const calculateROA = (netIncome: number, totalAssets: number): number => {
  return totalAssets > 0 ? (netIncome / totalAssets) * 100 : 0;
};

// PER計算
const calculatePER = (stockPrice: number, eps: number): number => {
  return eps > 0 ? stockPrice / eps : 0;
};

// PBR計算
const calculatePBR = (stockPrice: number, bps: number): number => {
  return bps > 0 ? stockPrice / bps : 0;
};
```

### 6.2 総合スコアの計算
```typescript
const calculateFinancialHealthScore = (metrics: FinancialMetrics): FinancialHealthScore => {
  // 各指標のスコア計算（0-100）
  const profitabilityScore = calculateProfitabilityScore(metrics);
  const marketScore = calculateMarketScore(metrics);
  const safetyScore = calculateSafetyScore(metrics);
  const growthScore = calculateGrowthScore(metrics);
  
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
    grade: getGrade(overallScore),
    recommendation: getRecommendation(overallScore),
    riskLevel: getRiskLevel(overallScore)
  };
};
```

## 7. テスト仕様

### 7.1 単体テスト
- 各財務指標の計算ロジック
- 総合スコアの算出ロジック
- 業界比較の計算ロジック
- 時系列分析の計算ロジック

### 7.2 統合テスト
- API連携テスト
- データフロー全体のテスト
- エラーハンドリングのテスト

### 7.3 E2Eテスト
- 財務分析フロー全体のテスト
- モバイル・デスクトップ対応テスト
- パフォーマンステスト

## 8. パフォーマンス要件

### 8.1 レスポンス時間
- 財務指標計算: < 2秒
- 業界比較分析: < 3秒
- 時系列分析: < 5秒

### 8.2 可用性
- 目標稼働率: 99.9%
- データ整合性: 100%
- 計算精度: 小数点以下2桁

## 9. 将来拡張計画

### 9.1 短期（3ヶ月）
- 基本財務指標の算出
- 業界比較機能
- シンプルなダッシュボード

### 9.2 中期（6ヶ月）
- 高度な財務分析機能
- 予測モデル統合
- カスタム指標作成

### 9.3 長期（1年）
- AI財務分析
- リアルタイム更新
- 国際対応
