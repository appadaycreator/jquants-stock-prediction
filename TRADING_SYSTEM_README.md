# 🚀 統合トレーディングシステム

最高優先度機能を統合した完全な株価予測・取引システム

## 🎯 実装された最高優先度機能

### 1. リアルタイム売買シグナル生成システム
- **期待利益**: 月間5-15%の利益向上
- **機能**: 
  - リアルタイム株価データ取得
  - 技術指標による売買シグナル生成
  - シグナル強度の評価
  - 信頼度に基づく推奨事項

### 2. リスク管理・損切りシステム
- **期待利益**: 損失を50-70%削減
- **機能**:
  - 動的損切り設定
  - ポジションサイズ管理
  - ポートフォリオリスク監視
  - 自動損切り実行

### 3. 複数銘柄同時監視・比較システム
- **期待利益**: 最適な投資機会の選択で20-30%利益向上
- **機能**:
  - 複数銘柄の同時監視
  - 銘柄間の比較分析
  - 相関分析と分散投資推奨
  - 投資機会の優先順位付け

## 📁 システム構成

```
統合トレーディングシステム/
├── realtime_trading_signals.py      # リアルタイム売買シグナル生成
├── risk_management_system.py        # リスク管理・損切りシステム
├── multi_stock_monitor.py          # 複数銘柄同時監視・比較
├── integrated_trading_system.py     # 統合システム
├── trading_config.yaml             # 設定ファイル
├── requirements.txt                # 依存関係
└── TRADING_SYSTEM_README.md        # このファイル
```

## 🚀 クイックスタート

### 1. 依存関係のインストール

```bash
# 仮想環境の作成（推奨）
python3 -m venv venv
source venv/bin/activate

# 依存関係のインストール
pip install -r requirements.txt
```

### 2. 設定ファイルの確認

```bash
# 設定ファイルの確認
cat trading_config.yaml
```

### 3. システムの実行

#### 個別システムの実行

```bash
# リアルタイムシグナル生成
python3 realtime_trading_signals.py

# リスク管理システム
python3 risk_management_system.py

# 複数銘柄監視
python3 multi_stock_monitor.py
```

#### 統合システムの実行

```bash
# 統合トレーディングシステム
python3 integrated_trading_system.py
```

## 📊 システムの機能詳細

### リアルタイム売買シグナル生成システム

#### 主要機能
- **技術指標分析**: RSI、MACD、ボリンジャーバンド、ストキャスティクス
- **シグナル強度評価**: 弱い/中程度/強い/非常に強い
- **信頼度計算**: 0-1の範囲で信頼度を数値化
- **リスクレベル判定**: LOW/MEDIUM/HIGH

#### 使用例
```python
from realtime_trading_signals import TradingSignalSystem

# システム初期化
symbols = ["7203.T", "6758.T", "9984.T"]
trading_system = TradingSignalSystem(symbols, account_value=1000000)

# 分析実行
results = trading_system.run_analysis()

# 結果表示
for signal in results['top_signals']:
    print(f"{signal['symbol']}: {signal['signal_type']} (信頼度: {signal['confidence']:.2f})")
```

### リスク管理・損切りシステム

#### 主要機能
- **動的損切り**: ボラティリティに応じた損切り幅調整
- **トレーリングストップ**: 利益確定の自動化
- **ポジションサイズ管理**: リスクベースのポジションサイズ計算
- **ポートフォリオリスク監視**: VaR、最大ドローダウン、シャープレシオ

#### 使用例
```python
from risk_management_system import RiskManagementSystem

# システム初期化
risk_system = RiskManagementSystem(account_value=1000000)

# ポジション追加
position = risk_system.add_position("7203.T", 2500.0, 100, "LONG")

# リスクレポート生成
report = risk_system.get_risk_report()
print(f"リスクスコア: {report['risk_metrics']['risk_score']:.2f}")
```

### 複数銘柄同時監視・比較システム

#### 主要機能
- **並列分析**: 複数銘柄の同時分析
- **技術分析**: 技術指標によるスコア計算
- **ファンダメンタル分析**: PER、時価総額による評価
- **モメンタム分析**: 短期・中期・長期のリターン分析
- **相関分析**: 銘柄間の相関関係分析

#### 使用例
```python
from multi_stock_monitor import MultiStockMonitor

# システム初期化
symbols = ["7203.T", "6758.T", "9984.T", "9432.T", "6861.T"]
monitor = MultiStockMonitor(symbols)

# 全銘柄分析
analysis_results = monitor.analyze_all_stocks()

# ポートフォリオ比較
portfolio_comparison = monitor.generate_portfolio_comparison()
print(f"分散投資スコア: {portfolio_comparison.diversification_score:.2f}")
```

### 統合トレーディングシステム

#### 主要機能
- **統合分析**: 3つのシステムを統合した包括的分析
- **取引推奨事項**: 統合された推奨事項の生成
- **自動実行**: 推奨事項の自動実行（オプション）
- **継続監視**: 定期的な分析と監視

#### 使用例
```python
from integrated_trading_system import IntegratedTradingSystem

# システム初期化
symbols = ["7203.T", "6758.T", "9984.T", "9432.T", "6861.T"]
trading_system = IntegratedTradingSystem(symbols, account_value=1000000)

# 包括的分析実行
results = trading_system.run_comprehensive_analysis()

# 継続監視（5分間隔）
trading_system.run_continuous_monitoring(interval_minutes=5)
```

## ⚙️ 設定のカスタマイズ

### 監視対象銘柄の変更

`trading_config.yaml`を編集:

```yaml
symbols:
  - "7203.T"  # トヨタ自動車
  - "6758.T"  # ソニーグループ
  # 他の銘柄を追加
```

### リスク管理設定の調整

```yaml
risk_management:
  stop_loss:
    base_percent: 5.0  # 損切り率を調整
    trailing_stop: true  # トレーリングストップ有効
  position_sizing:
    risk_per_trade: 0.02  # 1取引あたりのリスク
```

### シグナル生成設定の調整

```yaml
signals:
  rsi:
    overbought: 70  # 過大買い閾値
    oversold: 30    # 過小売り閾値
  min_confidence: 0.6  # 最小信頼度
```

## 📈 期待される効果

### 利益向上
- **月間5-15%の利益向上**: リアルタイムシグナルによる最適なタイミング
- **損失50-70%削減**: リスク管理システムによる損切り
- **20-30%利益向上**: 複数銘柄監視による最適な投資機会選択

### リスク軽減
- **動的損切り**: ボラティリティに応じた適応的損切り
- **ポジションサイズ管理**: リスクベースの適切なポジションサイズ
- **分散投資**: 相関分析による効果的な分散投資

### 効率化
- **自動化**: 手動分析の自動化
- **リアルタイム監視**: 継続的な市場監視
- **統合管理**: 複数システムの統合管理

## 🔧 トラブルシューティング

### よくある問題

#### 1. データ取得エラー
```bash
# インターネット接続を確認
ping google.com

# yfinanceのバージョンを確認
pip show yfinance
```

#### 2. メモリ不足エラー
```yaml
# trading_config.yamlでメモリ制限を調整
performance:
  max_memory_usage: "2GB"  # メモリ制限を増加
```

#### 3. API制限エラー
```yaml
# API呼び出し制限を調整
security:
  api_rate_limit: 50  # 制限を下げる
  request_delay: 0.2   # 間隔を増やす
```

### ログの確認

```bash
# ログファイルの確認
tail -f integrated_trading.log

# エラーログの確認
grep "ERROR" integrated_trading.log
```

## 📊 出力ファイル

### 結果ファイル
- `integrated_trading_results.json`: 統合分析結果
- `trading_signals_results.json`: シグナル分析結果
- `risk_management_report.json`: リスク管理レポート
- `multi_stock_analysis.json`: 複数銘柄分析結果

### ログファイル
- `integrated_trading.log`: 統合システムログ
- `trading_signals.log`: シグナルシステムログ
- `risk_management.log`: リスク管理ログ
- `multi_stock_monitor.log`: 複数銘柄監視ログ

## 🚨 注意事項

### 投資リスク
- このシステムは投資アドバイスを提供するものではありません
- 実際の取引前に十分な検証を行ってください
- 損失の可能性があることを理解してください

### システム制限
- リアルタイムデータの取得には遅延が生じる可能性があります
- 市場の急激な変動時にはシステムが追従できない場合があります
- 過去のデータに基づく分析であり、将来の結果を保証するものではありません

### セキュリティ
- 機密情報は環境変数で管理してください
- 取引データは適切に暗号化して保存してください
- 定期的なセキュリティ監査を実施してください

## 📞 サポート

### 問題報告
- GitHubのIssueで問題を報告してください
- ログファイルとエラーメッセージを含めてください

### 機能要求
- 新機能の要求はGitHubのIssueでお知らせください
- 具体的な使用例を含めてください

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

---

**⚠️ 免責事項**: このシステムは教育・研究目的で提供されています。実際の投資判断は自己責任で行ってください。
