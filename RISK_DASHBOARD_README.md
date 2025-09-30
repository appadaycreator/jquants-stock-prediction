# 🛡️ リスク管理ダッシュボード

現在のポジション状況、損切りライン、リスクレベルをWeb上で可視化するリスク管理システムです。

## 🎯 主要機能

### 📊 リアルタイムリスク監視
- **ポートフォリオ概要**: ポートフォリオ価値、未実現損益、リスクスコアの表示
- **リスクレベル表示**: LOW/MEDIUM/HIGH/CRITICALの4段階リスク評価
- **リスク指標**: 最大ドローダウン、VaR、シャープレシオの可視化

### 📈 ポジション管理
- **現在のポジション**: 全ポジションの詳細情報表示
- **損切りライン**: 各ポジションの損切り価格と利確価格
- **パフォーマンス**: 個別ポジションの価格推移と損益状況
- **リスク評価**: ポジション別リスクスコアと推奨事項

### ⚠️ アラート機能
- **リスクアラート**: 高リスクポジションの自動検知
- **損失アラート**: 10%以上の損失発生時の通知
- **推奨事項**: リスク削減のための具体的なアクション提案

### 📊 可視化機能
- **リスク指標チャート**: リスクスコアとポートフォリオ価値の推移
- **ポジション分布**: ポートフォリオ内のポジション分布（円グラフ）
- **ドローダウン分析**: 最大ドローダウンの時系列分析
- **パフォーマンスチャート**: 個別ポジションの価格推移と損切りライン

## 🚀 使用方法

### 1. データ生成
```bash
# リスク管理ダッシュボード用データを生成
python3 generate_risk_dashboard_data.py
```

### 2. リアルタイム更新（オプション）
```bash
# リアルタイム更新システムを開始
python3 risk_dashboard_realtime_updater.py
```

### 3. Webダッシュボードの表示
```bash
# Webアプリケーションを起動
cd web-app
npm run dev
```

ブラウザで `http://localhost:3000` にアクセスし、「リスク管理」タブをクリック

## 📁 ファイル構成

### データ生成
- `generate_risk_dashboard_data.py`: リスク管理ダッシュボード用データ生成
- `risk_dashboard_realtime_updater.py`: リアルタイム更新システム

### Webアプリケーション
- `web-app/src/app/risk/page.tsx`: リスク管理ダッシュボードページ
- `web-app/src/app/page.tsx`: メインダッシュボード（リスク管理タブ追加）

### データファイル
- `web-app/public/data/risk_dashboard_data.json`: 統合リスクデータ
- `web-app/public/data/risk_portfolio_overview.json`: ポートフォリオ概要
- `web-app/public/data/risk_positions.json`: ポジション詳細
- `web-app/public/data/risk_metrics_chart.json`: リスク指標チャート
- `web-app/public/data/risk_position_performance.json`: ポジションパフォーマンス
- `web-app/public/data/risk_alerts.json`: リスクアラート
- `web-app/public/data/risk_recommendations.json`: 推奨事項
- `web-app/public/data/risk_realtime_data.json`: リアルタイムデータ

## 🎨 ダッシュボード機能

### 概要タブ
- **ポートフォリオ概要カード**: 価値、リスクレベル、ドローダウン、シャープレシオ
- **リスク指標推移**: リスクスコアとポートフォリオ価値の時系列チャート
- **ポジション分布**: ポートフォリオ内のポジション分布（円グラフ）

### ポジションタブ
- **ポジション一覧**: 全ポジションの詳細情報
- **パフォーマンスチャート**: 個別ポジションの価格推移と損切りライン
- **リスク評価**: ポジション別リスクスコアとステータス

### リスク指標タブ
- **ドローダウン分析**: 最大ドローダウンの時系列分析
- **リスクスコア分布**: ポジション別リスクスコアのバーチャート

### 推奨事項タブ
- **リスク管理推奨事項**: 具体的なアクションプラン
- **優先度別表示**: HIGH/MEDIUM/LOWの優先度で分類

## 🔧 設定

### リスク管理システム設定
```python
# アカウント価値設定
account_value = 1000000  # 100万円

# リスク閾値設定
max_risk_score = 0.7     # 最大リスクスコア
max_drawdown = 0.15      # 最大ドローダウン（15%）
var_threshold = 0.1      # VaR閾値（10%）
```

### リスク管理の即時反映（UIでON/OFF・閾値調整）

- Web設定ページ `設定 > リスク管理設定` から、以下のパラメータを保存すると即時に反映されます。
  - `enabled`: リスク管理全体のON/OFF
  - `maxLoss.enabled`: 最大損失管理のON/OFF
  - `maxLoss.max_loss_percent`: 最大損失率（小数、例 0.05 = 5%）
  - `maxLoss.auto_stop_loss_threshold`: 自動損切り発動閾値（小数、例 0.08 = 8%）
  - `volatility.enabled`: ボラティリティ調整のON/OFF
  - `volatility.high_vol_threshold`: 高ボラ閾値（年率換算）
  - `volatility.extreme_vol_threshold`: 極端ボラ閾値（年率換算）
  - `volatility.high_vol_multiplier`: 高ボラ時のポジション縮小係数
  - `volatility.extreme_vol_multiplier`: 極端ボラ時のポジション縮小係数
  - `enforcement.block_violation_signals`: リスク違反シグナルのブロック（提案/執行に反映）

保存先: `web-app/public/data/risk_settings.json`

適用箇所:
- シグナル生成・集計 `realtime_trading_signals.py` の `RiskManager` で読み込み、
  - 高ボラ時はポジションサイズを縮小
  - 最大損失違反が見込まれる提案はゼロサイズ（ブロック有効時）
  を適用します。

### リアルタイム更新設定
```python
# 更新間隔設定
update_interval = 30      # 30秒間隔

# 価格変動シミュレーション設定
volatility_map = {
    "7203.T": 0.02,      # トヨタ: 2%
    "6758.T": 0.03,      # ソニー: 3%
    "9984.T": 0.04,      # ソフトバンク: 4%
    "7974.T": 0.025,     # 任天堂: 2.5%
    "6861.T": 0.015      # キーエンス: 1.5%
}
```

## 📊 データ構造

### ポートフォリオ概要
```json
{
  "timestamp": "2024-01-01T12:00:00",
  "account_value": 1000000,
  "portfolio_value": 1250000,
  "total_exposure": 1200000,
  "total_unrealized_pnl": 50000,
  "risk_level": "HIGH",
  "risk_color": "#EF4444",
  "risk_score": 0.75,
  "max_drawdown": 0.085,
  "var_95": 125000,
  "sharpe_ratio": 1.25,
  "should_reduce_risk": true
}
```

### ポジション詳細
```json
{
  "symbol": "7203.T",
  "company_name": "トヨタ自動車",
  "position_type": "LONG",
  "entry_price": 2500.0,
  "current_price": 2400.0,
  "quantity": 100,
  "unrealized_pnl": -10000,
  "unrealized_pnl_percent": -4.0,
  "stop_loss_price": 2375.0,
  "take_profit_price": 2625.0,
  "risk_score": 0.8,
  "risk_level": "HIGH",
  "status": "OPEN"
}
```

### リスクアラート
```json
{
  "id": "portfolio_risk_high",
  "type": "WARNING",
  "title": "ポートフォリオリスクが高すぎます",
  "message": "リスクスコアが閾値を超えています。ポジションサイズの縮小を検討してください。",
  "timestamp": "2024-01-01T12:00:00",
  "priority": "HIGH",
  "color": "#EF4444"
}
```

## 🚨 アラート条件

### ポートフォリオレベル
- **リスクスコア > 0.7**: ポートフォリオリスクが高すぎる
- **最大ドローダウン > 15%**: 損失が拡大している
- **VaR > 10%**: リスクが許容範囲を超えている

### 個別ポジション
- **リスクスコア > 0.8**: 個別ポジションのリスクが高すぎる
- **損失 > 10%**: 10%以上の損失が発生
- **損切り接近**: 損切りラインに近づいている

## 💡 推奨事項

### リスク管理
- **ポジションサイズ縮小**: リスクスコアが高い場合
- **損切りライン厳格化**: ドローダウンが大きい場合
- **分散投資**: 相関の高いポジションの整理

### ポジション管理
- **高リスクポジションクローズ**: リスクスコアが0.8を超える場合
- **損切り実行**: 損失が10%を超える場合
- **利確検討**: 利益が目標に達した場合

## 🔄 リアルタイム更新

### 自動更新機能
- **価格更新**: 30秒間隔でポジション価格を更新
- **リスク再計算**: 価格変動に応じてリスク指標を再計算
- **アラート生成**: リスク条件を満たす場合にアラートを生成
- **データ保存**: 更新されたデータを自動保存

### 手動更新
```bash
# 強制更新
python3 -c "
from risk_dashboard_realtime_updater import RiskDashboardRealtimeUpdater
updater = RiskDashboardRealtimeUpdater()
updater.force_update()
"
```

## 📈 期待効果

### 損失の早期発見
- **リアルタイム監視**: ポジションの価格変動をリアルタイムで監視
- **リスクアラート**: 高リスク状況の早期検知
- **自動通知**: 重要なリスク指標の変化を即座に通知

### 適切な損切り
- **損切りライン表示**: 各ポジションの損切り価格を明確に表示
- **損切り推奨**: リスク条件を満たす場合の損切り推奨
- **自動損切り**: 設定された条件での自動損切り実行

### リスク管理の最適化
- **ポートフォリオリスク**: 全体のリスク状況を可視化
- **個別ポジションリスク**: 各ポジションのリスク評価
- **推奨事項**: 具体的なリスク削減アクションの提案

## 🛠️ トラブルシューティング

### よくある問題

#### データが表示されない
```bash
# データ生成を再実行
python3 generate_risk_dashboard_data.py

# Webアプリケーションを再起動
cd web-app
npm run dev
```

#### リアルタイム更新が動作しない
```bash
# 更新システムのステータス確認
python3 -c "
from risk_dashboard_realtime_updater import RiskDashboardRealtimeUpdater
updater = RiskDashboardRealtimeUpdater()
print(updater.get_current_status())
"
```

#### アラートが表示されない
- リスク閾値の設定を確認
- ポジションの価格データが正しく更新されているか確認
- ログファイルでエラーを確認

### ログ確認
```bash
# リスク管理ログ
tail -f risk_management.log

# リアルタイム更新ログ
tail -f risk_dashboard_realtime_updater.log
```

## 📚 関連ドキュメント

- [リスク管理システム](risk_management_system.py): コアリスク管理機能
- [統合トレーディングシステム](TRADING_SYSTEM_README.md): 全体的な取引システム
- [Webダッシュボード](web-app/README.md): Webアプリケーションの詳細

---

**🎯 リスク管理ダッシュボードにより、損失の早期発見と適切な損切りを実現し、投資リスクを大幅に削減できます。**
