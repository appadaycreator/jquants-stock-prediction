# 新NISA枠効率的活用システム 仕様書 v3.0

## 1. 機能概要

### 1.1 目的
新NISA制度（2024年1月開始）の非課税枠を最大限活用し、税務効果を最大化するための包括的な投資枠管理システムを提供する。非課税枠の利用率を90%以上に向上させ、投資家の税務メリットを最大化する。

### 1.2 新NISA制度の基本仕様（2024年1月開始）
- **成長投資枠**: 年間投資枠240万円、非課税保有限度額1200万円（5年間）
- **つみたて投資枠**: 年間投資枠40万円、非課税保有限度額200万円（20年間）
- **枠の再利用**: 売却時の非課税枠の翌年以降の再利用可能
- **回転売買**: 年間投資枠内での回転売買可能
- **制度統合**: 旧NISA（2023年12月まで）との統合管理
- **税務計算**: 非課税枠の効率的な活用と税務最適化

### 1.3 主要目標
- **非課税枠利用率**: 90%以上
- **税務効果最大化**: 年間最大72万円の税務節約（240万円×30%税率）
- **投資戦略最適化**: AI を活用した投資戦略提案
- **リスク管理**: 分散投資によるリスク軽減

## 2. 機能仕様

### 2.1 投資枠管理機能

#### 2.1.1 枠の利用状況追跡
```typescript
interface NisaQuotaStatus {
  // 成長投資枠
  growthInvestment: {
    annualLimit: number;        // 年間投資枠: 2,400,000円
    taxFreeLimit: number;       // 非課税保有限度額: 12,000,000円
    usedAmount: number;         // 使用済み金額
    availableAmount: number;    // 利用可能金額
    utilizationRate: number;    // 利用率（%）
    remainingDays: number;      // 残り日数
    monthlyTarget: number;      // 月次目標額
    weeklyTarget: number;       // 週次目標額
  };
  
  // つみたて投資枠
  accumulationInvestment: {
    annualLimit: number;        // 年間投資枠: 400,000円
    taxFreeLimit: number;       // 非課税保有限度額: 2,000,000円
    usedAmount: number;         // 使用済み金額
    availableAmount: number;    // 利用可能金額
    utilizationRate: number;    // 利用率（%）
    remainingDays: number;      // 残り日数
    monthlyTarget: number;      // 月次目標額
    weeklyTarget: number;       // 週次目標額
  };
  
  // 枠の再利用状況
  quotaReuse: {
    growthAvailable: number;    // 成長枠再利用可能額
    accumulationAvailable: number; // つみたて枠再利用可能額
    nextYearAvailable: number;  // 翌年利用可能額
    totalReusable: number;      // 総再利用可能額
  };
  
  // 最適化指標
  optimization: {
    overallUtilizationRate: number;  // 総合利用率
    targetUtilizationRate: number;   // 目標利用率（90%）
    efficiencyScore: number;         // 効率スコア
    optimizationLevel: 'EXCELLENT' | 'GOOD' | 'FAIR' | 'POOR';
  };
}
```

#### 2.1.2 投資履歴管理
```typescript
interface NisaTransaction {
  id: string;
  type: 'BUY' | 'SELL';
  symbol: string;
  symbolName: string;
  quantity: number;
  price: number;
  amount: number;
  quotaType: 'GROWTH' | 'ACCUMULATION';
  transactionDate: string;
  profitLoss?: number;         // 売却時の損益
  taxFreeAmount?: number;      // 非課税枠解放額
  taxSavings?: number;         // 税務節約額
  efficiencyScore?: number;    // 効率スコア
  strategy?: string;          // 投資戦略
  riskLevel?: 'LOW' | 'MEDIUM' | 'HIGH';
}
```

#### 2.1.3 ポートフォリオ管理
```typescript
interface NisaPortfolio {
  positions: NisaPosition[];
  totalValue: number;
  totalCost: number;
  unrealizedProfitLoss: number;
  realizedProfitLoss: number;
  taxFreeProfitLoss: number;
  diversificationScore: number;
  riskLevel: 'LOW' | 'MEDIUM' | 'HIGH';
  optimizationScore: number;
  lastRebalanced: string;
}

interface NisaPosition {
  symbol: string;
  symbolName: string;
  quantity: number;
  averagePrice: number;
  currentPrice: number;
  cost: number;
  currentValue: number;
  unrealizedProfitLoss: number;
  quotaType: 'GROWTH' | 'ACCUMULATION';
  purchaseDate: string;
  taxEfficiency: number;      // 税務効率
  riskScore: number;          // リスクスコア
  expectedReturn: number;     // 期待リターン
}
```

### 2.2 投資戦略支援機能

#### 2.2.1 枠最適化提案
```typescript
interface QuotaOptimization {
  recommendations: {
    growthQuota: {
      suggestedAmount: number;
      reason: string;
      priority: 'HIGH' | 'MEDIUM' | 'LOW';
      expectedTaxSavings: number;
      riskLevel: 'LOW' | 'MEDIUM' | 'HIGH';
      timeline: string;
    };
    accumulationQuota: {
      suggestedAmount: number;
      reason: string;
      priority: 'HIGH' | 'MEDIUM' | 'LOW';
      expectedTaxSavings: number;
      riskLevel: 'LOW' | 'MEDIUM' | 'HIGH';
      timeline: string;
    };
  };
  riskAnalysis: {
    diversificationScore: number;
    sectorConcentration: number;
    riskLevel: 'LOW' | 'MEDIUM' | 'HIGH';
    correlationAnalysis: number;
    volatilityScore: number;
  };
  taxOptimization: {
    currentTaxSavings: number;
    potentialTaxSavings: number;
    optimizationScore: number;
    recommendations: string[];
  };
}
```

#### 2.2.2 税務計算機能
```typescript
interface TaxCalculation {
  currentYear: {
    growthQuotaUsed: number;
    accumulationQuotaUsed: number;
    totalTaxFreeAmount: number;
    taxSavings: number;
    effectiveTaxRate: number;
  };
  nextYear: {
    availableGrowthQuota: number;
    availableAccumulationQuota: number;
    reusableQuota: number;
    totalAvailable: number;
  };
  taxSavings: {
    estimatedTaxSavings: number;
    taxRate: number;
    effectiveTaxRate: number;
    annualSavings: number;
    lifetimeSavings: number;
    optimizationPotential: number;
  };
  optimization: {
    currentEfficiency: number;
    targetEfficiency: number;
    improvementPotential: number;
    recommendedActions: string[];
  };
}
```

### 2.3 アラート・通知機能

#### 2.3.1 枠使用状況アラート
```typescript
interface QuotaAlert {
  type: 'WARNING' | 'CRITICAL' | 'INFO' | 'SUCCESS';
  message: string;
  quotaType: 'GROWTH' | 'ACCUMULATION';
  currentUsage: number;
  threshold: number;
  recommendedAction: string;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  estimatedImpact: number;
  deadline?: string;
}

interface InvestmentOpportunity {
  symbol: string;
  symbolName: string;
  reason: string;
  expectedReturn: number;
  riskLevel: 'LOW' | 'MEDIUM' | 'HIGH';
  quotaRecommendation: 'GROWTH' | 'ACCUMULATION';
  suggestedAmount: number;
  confidence: number;
  timeframe: string;
  taxEfficiency: number;
}
```

### 2.4 AI最適化機能

#### 2.4.1 投資戦略提案
```typescript
interface AIInvestmentStrategy {
  strategy: {
    name: string;
    description: string;
    riskLevel: 'LOW' | 'MEDIUM' | 'HIGH';
    expectedReturn: number;
    timeframe: string;
    confidence: number;
  };
  recommendations: {
    growthQuota: {
      suggestedStocks: string[];
      allocation: number;
      reasoning: string;
    };
    accumulationQuota: {
      suggestedStocks: string[];
      allocation: number;
      reasoning: string;
    };
  };
  optimization: {
    currentScore: number;
    targetScore: number;
    improvementActions: string[];
    expectedOutcome: string;
  };
}
```

## 3. データ構造

### 3.1 ローカルストレージ構造
```typescript
interface NisaData {
  userProfile: {
    userId: string;
    startDate: string;          // NISA開始日
    taxYear: number;           // 現在の課税年度
    riskTolerance: 'LOW' | 'MEDIUM' | 'HIGH';
    investmentGoals: string[];
    timeHorizon: number;       // 投資期間（年）
  };
  quotas: NisaQuotaStatus;
  transactions: NisaTransaction[];
  portfolio: NisaPortfolio;
  optimization: {
    currentStrategy: string;
    performanceMetrics: {
      totalReturn: number;
      taxSavings: number;
      efficiencyScore: number;
    };
    aiRecommendations: AIInvestmentStrategy[];
  };
  settings: {
    autoRebalancing: boolean;
    alertThresholds: {
      growthWarning: number;    // 成長枠警告閾値（%）
      accumulationWarning: number; // つみたて枠警告閾値（%）
      utilizationTarget: number; // 利用率目標（%）
    };
    notifications: {
      email: boolean;
      browser: boolean;
      push: boolean;
    };
    optimization: {
      autoOptimization: boolean;
      rebalancingFrequency: 'WEEKLY' | 'MONTHLY' | 'QUARTERLY';
      riskManagement: boolean;
    };
  };
}
```

### 3.2 API仕様

#### 3.2.1 エンドポイント
```
GET /api/nisa/status          # 枠利用状況取得
POST /api/nisa/transaction    # 取引記録追加
PUT /api/nisa/transaction/:id # 取引記録更新
DELETE /api/nisa/transaction/:id # 取引記録削除
GET /api/nisa/portfolio       # ポートフォリオ取得
GET /api/nisa/optimization    # 最適化提案取得
GET /api/nisa/alerts          # アラート取得
POST /api/nisa/calculate      # 税務計算実行
GET /api/nisa/ai-recommendations # AI推奨事項取得
POST /api/nisa/optimize       # 最適化実行
GET /api/nisa/analytics       # 分析データ取得
```

#### 3.2.2 レスポンス形式
```typescript
interface NisaApiResponse<T> {
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
    optimizationScore?: number;
    efficiencyScore?: number;
  };
}
```

## 4. UI/UX仕様

### 4.1 ダッシュボード構成
1. **枠利用状況カード**
   - 成長投資枠の使用状況（円・%）
   - つみたて投資枠の使用状況（円・%）
   - 視覚的なプログレスバー
   - 目標達成率の表示
   - 残り日数と推奨投資額

2. **ポートフォリオサマリー**
   - 総投資額・現在価値
   - 未実現損益・実現損益
   - 非課税枠内の損益
   - 税務節約額の表示
   - 効率スコアの表示

3. **投資機会提案**
   - 枠内での投資推奨銘柄
   - 最適化提案
   - リスク分析
   - AI推奨事項

4. **取引履歴**
   - 時系列での取引一覧
   - フィルタリング機能
   - エクスポート機能
   - 税務効果の表示

5. **最適化ダッシュボード**
   - 現在の効率スコア
   - 改善提案
   - 目標達成状況
   - 推奨アクション

### 4.2 モバイル対応
- レスポンシブデザイン
- タッチ操作最適化
- 重要な情報の優先表示
- プッシュ通知対応

## 5. セキュリティ・プライバシー

### 5.1 データ保護
- ローカルストレージ暗号化
- 機密情報のマスキング
- セキュアな通信（HTTPS）
- データ匿名化

### 5.2 バックアップ・復旧
- 自動バックアップ機能
- データエクスポート/インポート
- 災害復旧計画
- データ整合性チェック

## 6. テスト仕様

### 6.1 単体テスト
- 各コンポーネントのテスト
- 計算ロジックのテスト
- エラーハンドリングのテスト
- 税務計算の精度テスト

### 6.2 統合テスト
- API連携テスト
- データフロー全体のテスト
- ユーザーシナリオテスト
- 最適化アルゴリズムのテスト

### 6.3 E2Eテスト
- 投資フロー全体のテスト
- モバイル・デスクトップ対応テスト
- パフォーマンステスト
- セキュリティテスト

### 6.4 テストカバレッジ
- **目標カバレッジ**: 98%以上
- **重要機能**: 100%カバレッジ
- **税務計算**: 100%カバレッジ
- **最適化アルゴリズム**: 100%カバレッジ

## 7. パフォーマンス要件

### 7.1 レスポンス時間
- 枠状況表示: < 1秒
- 取引記録追加: < 2秒
- 最適化計算: < 5秒
- AI推奨事項生成: < 10秒

### 7.2 可用性
- 目標稼働率: 99.9%
- データ整合性: 100%
- バックアップ頻度: 日次
- 復旧時間: < 1時間

## 8. 最適化要件

### 8.1 非課税枠利用率
- **目標利用率**: 90%以上
- **成長投資枠**: 年間240万円の90%以上活用
- **つみたて投資枠**: 年間40万円の90%以上活用
- **総合効率**: 両枠の合計利用率90%以上

### 8.2 税務効果最大化
- **年間税務節約**: 最大72万円（240万円×30%税率）
- **つみたて枠節約**: 最大12万円（40万円×30%税率）
- **総合節約**: 最大84万円/年
- **5年間累計**: 最大420万円の税務節約

### 8.3 投資戦略最適化
- **分散投資**: 最低10銘柄以上
- **セクター分散**: 3セクター以上
- **リスク管理**: 適切なリスクスコア維持
- **リターン最適化**: リスク調整後リターンの最大化

## 9. 将来拡張計画

### 9.1 短期（3ヶ月）
- 基本的な枠管理機能
- シンプルなダッシュボード
- 基本的なアラート機能
- 税務計算機能

### 9.2 中期（6ヶ月）
- 高度な最適化機能
- AI投資戦略提案
- 証券会社連携
- 税務申告支援

### 9.3 長期（1年）
- 機械学習による予測
- 他制度との統合
- 国際対応
- 高度なリスク管理

## 10. 品質保証

### 10.1 コード品質
- **リンターエラー**: 0件
- **警告**: 0件
- **デプロイエラー**: 0件
- **コンソールエラー**: 0件

### 10.2 テスト品質
- **テストカバレッジ**: 98%以上
- **重要機能テスト**: 100%
- **統合テスト**: 100%
- **E2Eテスト**: 100%

### 10.3 パフォーマンス品質
- **レスポンス時間**: 要件内
- **メモリ使用量**: 最適化済み
- **CPU使用率**: 最適化済み
- **ネットワーク効率**: 最適化済み
