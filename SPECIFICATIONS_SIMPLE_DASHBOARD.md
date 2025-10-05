# シンプル投資判断ダッシュボード 仕様書 v2.0

## 1. 機能概要

### 1.1 目的
1日5分で投資判断を完結させるシンプル投資判断ダッシュボードを提供する。新規ユーザーが1分で投資判断に到達できることを目標とする。

### 1.2 主要機能
- **今日の推奨アクション**: 買い/売り/ホールドを3つまで表示
- **推奨詳細**: 各推奨に「理由」「信頼度」「期待リターン」を明記
- **保有銘柄損益**: 保有銘柄の損益状況を一目で確認
- **シンプルUI**: 投資判断に直結する情報のみ表示
- **損益の可視化強化**: 投資成果を3秒で把握できる強化された損益表示
- **パフォーマンス比較**: ベスト・ワーストパフォーマーの明確な表示
- **損益推移グラフ**: 日次・週次・月次の損益推移をグラフ化

## 2. 機能仕様

### 2.1 今日の推奨アクション

#### 2.1.1 推奨アクション表示
```typescript
interface SimpleRecommendation {
  id: string;
  symbol: string;
  symbolName: string;
  action: 'BUY' | 'SELL' | 'HOLD';
  reason: string;                    // 推奨理由
  confidence: number;               // 信頼度 (0-100%)
  expectedReturn: number;           // 期待リターン (%)
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  timeframe: string;               // 推奨期間
}
```

#### 2.1.2 推奨アクション制限
- **最大表示数**: 3つまで
- **優先順位**: HIGH > MEDIUM > LOW
- **信頼度閾値**: 60%以上のみ表示
- **更新頻度**: 30秒間隔

### 2.2 保有銘柄損益状況

#### 2.2.1 損益サマリー
```typescript
interface SimplePortfolioSummary {
  totalInvestment: number;         // 総投資額
  currentValue: number;            // 現在価値
  unrealizedPnL: number;          // 未実現損益
  unrealizedPnLPercent: number;    // 未実現損益率 (%)
  dailyPnL: number;               // 日次損益
  weeklyPnL: number;               // 週次損益
  monthlyPnL: number;              // 月次損益
  yearlyPnL: number;               // 年次損益
  sharpeRatio: number;             // シャープレシオ
  maxDrawdown: number;              // 最大ドローダウン
  volatility: number;               // ボラティリティ
  winRate: number;                  // 勝率
  profitFactor: number;             // プロフィットファクター
  bestPerformer: {
    symbol: string;
    symbolName: string;
    return: number;
    value: number;
  };
  worstPerformer: {
    symbol: string;
    symbolName: string;
    return: number;
    value: number;
  };
}
```

#### 2.2.2 損益の可視化強化
- **3秒理解**: 投資成果を3秒で把握できる大きな表示
- **期間別損益**: 日次・週次・月次・年次の損益を一目で確認
- **リスク指標**: シャープレシオ、最大ドローダウン、ボラティリティを表示
- **パフォーマンス統計**: 勝率、プロフィットファクターを表示

#### 2.2.3 損益推移グラフ
- **複数チャートタイプ**: ライン、エリア、バーチャート
- **期間選択**: 1日、1週、1月、3月、1年、全期間
- **ベンチマーク比較**: 市場指標との比較表示
- **インタラクティブ**: データポイントクリックで詳細表示

#### 2.2.4 パフォーマンス比較機能
- **銘柄ランキング**: 損益率、配分、ボラティリティ、ベータでソート
- **ベスト・ワースト表示**: 最も利益・損失の大きい銘柄を明確に表示
- **セクター分析**: セクター別パフォーマンスと配分を可視化
- **リスク分析**: リスク分布、ボラティリティ分析を表示
- **インタラクティブ**: 銘柄クリックで詳細情報表示

#### 2.2.2 保有銘柄一覧
```typescript
interface SimplePosition {
  symbol: string;
  symbolName: string;
  quantity: number;
  averagePrice: number;
  currentPrice: number;
  cost: number;
  currentValue: number;
  unrealizedPnL: number;
  unrealizedPnLPercent: number;
  action: 'BUY_MORE' | 'SELL' | 'HOLD';
  confidence: number;
}
```

### 2.3 シンプルUI仕様

#### 2.3.1 画面構成
1. **ヘッダー**
   - 最終更新時刻
   - 自動更新スイッチ
   - リフレッシュボタン

2. **推奨アクションカード**（最大3つ）
   - 銘柄名・コード
   - アクション（BUY/SELL/HOLD）
   - 理由
   - 信頼度
   - 期待リターン

3. **損益サマリーカード**
   - 総投資額・現在価値
   - 未実現損益・損益率
   - ベスト・ワーストパフォーマー

4. **保有銘柄一覧**（簡易表示）
   - 銘柄名・コード
   - 損益・損益率
   - 推奨アクション

#### 2.3.2 レスポンシブデザイン
- **デスクトップ**: 3カラムレイアウト
- **タブレット**: 2カラムレイアウト
- **モバイル**: 1カラムレイアウト

## 3. データ構造

### 3.1 シンプルダッシュボードデータ
```typescript
interface SimpleDashboardData {
  lastUpdate: string;
  recommendations: SimpleRecommendation[];
  portfolioSummary: SimplePortfolioSummary;
  positions: SimplePosition[];
  marketStatus: {
    isOpen: boolean;
    nextOpen: string;
  };
}
```

### 3.2 API仕様

#### 3.2.1 エンドポイント
```
GET /api/simple-dashboard          # シンプルダッシュボードデータ取得
POST /api/simple-dashboard/refresh # データ更新実行
GET /api/simple-dashboard/status   # データ更新状況取得
```

#### 3.2.2 レスポンス形式
```typescript
interface SimpleDashboardResponse {
  success: boolean;
  data?: SimpleDashboardData;
  error?: {
    code: string;
    message: string;
  };
  metadata: {
    timestamp: string;
    version: string;
  };
}
```

## 4. UI/UX仕様

### 4.1 デザイン原則
- **シンプル**: 必要最小限の情報のみ表示
- **直感的**: 1分で理解できる構成
- **レスポンシブ**: 全デバイス対応
- **高速**: 2秒以内での表示

### 4.2 カラーパレット
```css
:root {
  --primary-color: #2563eb;        /* プライマリ（青） */
  --success-color: #16a34a;        /* 成功（緑） */
  --warning-color: #ca8a04;        /* 警告（黄） */
  --danger-color: #dc2626;         /* 危険（赤） */
  --neutral-color: #6b7280;        /* 中性（グレー） */
  --background-color: #f8fafc;     /* 背景（薄グレー） */
  --card-background: #ffffff;      /* カード背景（白） */
}
```

### 4.3 コンポーネント仕様

#### 4.3.1 推奨アクションカード
```typescript
interface RecommendationCardProps {
  recommendation: SimpleRecommendation;
  onActionClick?: (symbol: string, action: string) => void;
}
```

#### 4.3.2 損益サマリーカード
```typescript
interface PortfolioSummaryCardProps {
  summary: SimplePortfolioSummary;
  onDetailClick?: () => void;
}
```

#### 4.3.3 保有銘柄一覧
```typescript
interface PositionListProps {
  positions: SimplePosition[];
  onPositionClick?: (symbol: string) => void;
}
```

## 5. 実装仕様

### 5.1 バックエンド実装

#### 5.1.1 データ生成スクリプト
```python
# scripts/generate_simple_dashboard_data.py
def generate_simple_dashboard_data():
    """
    シンプルダッシュボード用データを生成
    - 推奨アクション（最大3つ）
    - 保有銘柄損益状況
    - 市場状況
    """
    pass
```

#### 5.1.2 API実装
```python
# core/simple_dashboard_manager.py
class SimpleDashboardManager:
    def get_dashboard_data(self) -> SimpleDashboardData:
        """シンプルダッシュボードデータを取得"""
        pass
    
    def refresh_data(self) -> bool:
        """データを更新"""
        pass
```

### 5.2 フロントエンド実装

#### 5.2.1 ページ構成
```
web-app/src/app/simple-dashboard/
├── page.tsx                    # メインページ
├── components/
│   ├── RecommendationCard.tsx  # 推奨アクションカード
│   ├── PortfolioSummary.tsx    # 損益サマリー
│   ├── PositionList.tsx        # 保有銘柄一覧
│   └── SimpleHeader.tsx       # ヘッダー
└── hooks/
    └── useSimpleDashboard.ts   # データ取得フック
```

#### 5.2.2 データ取得フック
```typescript
// hooks/useSimpleDashboard.ts
export const useSimpleDashboard = () => {
  const [data, setData] = useState<SimpleDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const refreshData = useCallback(async () => {
    // データ更新ロジック
  }, []);
  
  return { data, loading, error, refreshData };
};
```

## 6. パフォーマンス要件

### 6.1 レスポンス時間
- **初期表示**: < 2秒
- **データ更新**: < 3秒
- **自動更新**: 30秒間隔

### 6.2 可用性
- **目標稼働率**: 99.9%
- **データ整合性**: 100%
- **エラー率**: < 1%

## 7. テスト仕様

### 7.1 単体テスト
- **コンポーネントテスト**: 各UIコンポーネント
- **フックテスト**: データ取得フック
- **ユーティリティテスト**: 計算ロジック

### 7.2 統合テスト
- **API連携テスト**: バックエンドAPI
- **データフローテスト**: データ取得から表示まで
- **エラーハンドリングテスト**: エラー時の動作

### 7.3 E2Eテスト
- **ユーザーフローテスト**: 1分での投資判断フロー
- **レスポンシブテスト**: 全デバイス対応
- **パフォーマンステスト**: 表示速度

### 7.4 テストカバレッジ
- **目標カバレッジ**: 98%以上
- **必須カバレッジ**: 95%以上
- **継続的テスト**: CI/CDパイプライン

## 8. セキュリティ仕様

### 8.1 データ保護
- **ローカルストレージ**: 暗号化保存
- **API通信**: HTTPS必須
- **機密情報**: マスキング表示

### 8.2 アクセス制御
- **認証**: 不要（公開ダッシュボード）
- **レート制限**: API呼び出し制限
- **監査ログ**: アクセス記録

## 9. 運用仕様

### 9.1 データ更新
- **自動更新**: 30秒間隔
- **手動更新**: リフレッシュボタン
- **バックアップ**: 日次バックアップ

### 9.2 監視
- **ヘルスチェック**: 1分間隔
- **エラー監視**: リアルタイム
- **パフォーマンス監視**: 継続的

## 10. 成功基準

### 10.1 機能要件
- **表示速度**: 2秒以内
- **データ精度**: 100%
- **ユーザビリティ**: 1分で判断完了

### 10.2 非機能要件
- **可用性**: 99.9%
- **パフォーマンス**: 高速表示
- **セキュリティ**: 脆弱性ゼロ

## 11. 制約事項

### 11.1 技術制約
- **データ容量**: ローカルストレージ制限
- **API制限**: J-Quants API制限
- **計算リソース**: 単一サーバー

### 11.2 機能制約
- **推奨数**: 最大3つまで
- **更新頻度**: 30秒間隔
- **表示情報**: 必要最小限のみ

## 12. 将来拡張計画

### 12.1 短期（1ヶ月）
- 基本的なシンプルダッシュボード
- 推奨アクション表示
- 損益状況表示

### 12.2 中期（3ヶ月）
- カスタマイズ機能
- アラート機能
- 詳細分析リンク

### 12.3 長期（6ヶ月）
- AI推奨機能
- ポートフォリオ最適化
- 他システム連携

---

**文書バージョン**: 1.0  
**作成日**: 2025年1月  
**承認者**: システムアーキテクト  
**次回見直し**: 2025年4月
