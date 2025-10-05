# 新NISA枠管理機能 仕様書 v2.0

## 1. 機能概要

### 1.1 目的
新NISA制度（2024年1月開始）に完全対応した投資枠管理機能を提供し、個人投資家の非課税投資を効率的にサポートする。2024年1月以降の新制度に対応した包括的な投資枠管理システムを実装する。

### 1.2 新NISA制度の基本仕様（2024年1月開始）
- **成長投資枠**: 年間投資枠240万円、非課税保有限度額1200万円（5年間）
- **つみたて投資枠**: 年間投資枠40万円、非課税保有限度額200万円（20年間）
- **枠の再利用**: 売却時の非課税枠の翌年以降の再利用可能
- **回転売買**: 年間投資枠内での回転売買可能
- **制度統合**: 旧NISA（2023年12月まで）との統合管理
- **税務計算**: 非課税枠の効率的な活用と税務最適化

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
  };
  
  // つみたて投資枠
  accumulationInvestment: {
    annualLimit: number;        // 年間投資枠: 400,000円
    taxFreeLimit: number;       // 非課税保有限度額: 2,000,000円
    usedAmount: number;         // 使用済み金額
    availableAmount: number;    // 利用可能金額
    utilizationRate: number;    // 利用率（%）
  };
  
  // 枠の再利用状況
  quotaReuse: {
    growthAvailable: number;    // 成長枠再利用可能額
    accumulationAvailable: number; // つみたて枠再利用可能額
    nextYearAvailable: number;  // 翌年利用可能額
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
    };
    accumulationQuota: {
      suggestedAmount: number;
      reason: string;
      priority: 'HIGH' | 'MEDIUM' | 'LOW';
    };
  };
  riskAnalysis: {
    diversificationScore: number;
    sectorConcentration: number;
    riskLevel: 'LOW' | 'MEDIUM' | 'HIGH';
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
}
```

### 2.3 アラート・通知機能

#### 2.3.1 枠使用状況アラート
```typescript
interface QuotaAlert {
  type: 'WARNING' | 'CRITICAL' | 'INFO';
  message: string;
  quotaType: 'GROWTH' | 'ACCUMULATION';
  currentUsage: number;
  threshold: number;
  recommendedAction: string;
}
```

#### 2.3.2 投資機会通知
```typescript
interface InvestmentOpportunity {
  symbol: string;
  symbolName: string;
  reason: string;
  expectedReturn: number;
  riskLevel: 'LOW' | 'MEDIUM' | 'HIGH';
  quotaRecommendation: 'GROWTH' | 'ACCUMULATION';
  suggestedAmount: number;
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
  };
  quotas: NisaQuotaStatus;
  transactions: NisaTransaction[];
  portfolio: NisaPortfolio;
  settings: {
    autoRebalancing: boolean;
    alertThresholds: {
      growthWarning: number;    // 成長枠警告閾値（%）
      accumulationWarning: number; // つみたて枠警告閾値（%）
    };
    notifications: {
      email: boolean;
      browser: boolean;
      push: boolean;
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
  };
}
```

## 4. UI/UX仕様

### 4.1 ダッシュボード構成
1. **枠利用状況カード**
   - 成長投資枠の使用状況（円・%）
   - つみたて投資枠の使用状況（円・%）
   - 視覚的なプログレスバー

2. **ポートフォリオサマリー**
   - 総投資額・現在価値
   - 未実現損益・実現損益
   - 非課税枠内の損益

3. **投資機会提案**
   - 枠内での投資推奨銘柄
   - 最適化提案
   - リスク分析

4. **取引履歴**
   - 時系列での取引一覧
   - フィルタリング機能
   - エクスポート機能

### 4.2 モバイル対応
- レスポンシブデザイン
- タッチ操作最適化
- 重要な情報の優先表示

## 5. セキュリティ・プライバシー

### 5.1 データ保護
- ローカルストレージ暗号化
- 機密情報のマスキング
- セキュアな通信（HTTPS）

### 5.2 バックアップ・復旧
- 自動バックアップ機能
- データエクスポート/インポート
- 災害復旧計画

## 6. テスト仕様

### 6.1 単体テスト
- 各コンポーネントのテスト
- 計算ロジックのテスト
- エラーハンドリングのテスト

### 6.2 統合テスト
- API連携テスト
- データフロー全体のテスト
- ユーザーシナリオテスト

### 6.3 E2Eテスト
- 投資フロー全体のテスト
- モバイル・デスクトップ対応テスト
- パフォーマンステスト

## 7. パフォーマンス要件

### 7.1 レスポンス時間
- 枠状況表示: < 1秒
- 取引記録追加: < 2秒
- 最適化計算: < 5秒

### 7.2 可用性
- 目標稼働率: 99.9%
- データ整合性: 100%
- バックアップ頻度: 日次

## 8. 将来拡張計画

### 8.1 短期（3ヶ月）
- 基本的な枠管理機能
- シンプルなダッシュボード
- 基本的なアラート機能

### 8.2 中期（6ヶ月）
- 高度な最適化機能
- 証券会社連携
- 税務申告支援

### 8.3 長期（1年）
- AI投資戦略提案
- 他制度との統合
- 国際対応
