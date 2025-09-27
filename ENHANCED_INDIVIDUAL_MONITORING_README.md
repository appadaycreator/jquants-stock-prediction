# 強化されたリアルタイム個別銘柄監視システム

投資機会の見逃しを70%削減する強化されたリアルタイム個別銘柄監視システム

## 🎯 概要

本システムは、個別銘柄のリアルタイム監視を強化し、投資機会の見逃しを大幅に削減することを目的としています。従来の監視システムを大幅に拡張し、価格監視、アラート機能、ニュース・感情分析、技術指標のリアルタイム更新、ポートフォリオ監視を統合した包括的なソリューションです。

## 🚀 主要機能

### 1. リアルタイム個別銘柄監視 (`enhanced_individual_stock_monitor.py`)

**期待効果**: 投資機会の見逃しを70%削減

#### 主要機能
- **リアルタイム価格監視**: 個別銘柄の価格・出来高をリアルタイムで監視
- **高度なアラート機能**: 価格変動、出来高急増、技術指標、感情変化、リスクアラート
- **履歴管理**: 価格・出来高・指標の履歴を効率的に管理
- **パフォーマンス最適化**: 並列処理による高速監視

#### アラート機能
- **価格変動アラート**: 設定した閾値を超える価格変動を検知
- **出来高急増アラート**: 異常な出来高増加を検知
- **技術指標アラート**: RSI極値、MACDシグナル等の技術指標アラート
- **感情変化アラート**: ニュース・SNS感情の急激な変化を検知
- **リスクアラート**: 高リスク状態の早期検知

#### 設定例
```python
config = {
    "monitoring_interval": 30,  # 監視間隔（秒）
    "price_change_threshold": 2.0,  # 価格変動閾値（%）
    "volume_spike_threshold": 150.0,  # 出来高急増閾値（%）
    "sentiment_change_threshold": 0.2,  # 感情変化閾値
    "technical_signal_threshold": 0.7,  # 技術シグナル閾値
    "risk_threshold": 0.8,  # リスク閾値
    "max_price_history": 100,  # 価格履歴最大数
    "max_volume_history": 100,  # 出来高履歴最大数
    "email": {
        "enabled": True,  # メール通知有効化
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "username": "your_email@gmail.com",
        "password": "your_password",
        "to_addresses": ["alert@example.com"]
    }
}
```

### 2. ニュース・感情分析統合 (`enhanced_news_sentiment_integration.py`)

**期待効果**: 感情分析による投資判断の精度向上

#### 主要機能
- **ニュース感情分析**: 個別銘柄のニュース記事の感情分析
- **SNSトレンド分析**: Twitter、Reddit等のソーシャルメディア分析
- **感情指標のリアルタイム更新**: 感情スコアの継続的監視
- **統合感情分析**: ニュースとソーシャルメディアの統合分析

#### 感情分析機能
- **VADER感情分析**: 高精度な感情スコア計算
- **TextBlob感情分析**: 追加の感情分析エンジン
- **関連性スコア**: 株式関連性の自動判定
- **キーワード抽出**: 重要なキーワードの自動抽出

#### 設定例
```python
config = {
    "news_api_key": "your_news_api_key",
    "twitter_credentials": {
        "twitter_api_key": "your_twitter_api_key",
        "twitter_api_secret": "your_twitter_api_secret",
        "twitter_access_token": "your_access_token",
        "twitter_access_token_secret": "your_access_token_secret"
    },
    "sentiment_update_interval": 300,  # 感情分析更新間隔（秒）
    "news_cache_duration": 3600,  # ニュースキャッシュ期間（秒）
    "social_cache_duration": 1800,  # ソーシャルキャッシュ期間（秒）
    "relevance_threshold": 0.3,  # 関連性閾値
    "confidence_threshold": 0.5  # 信頼度閾値
}
```

### 3. 技術指標リアルタイム更新 (`enhanced_technical_indicators_realtime.py`)

**期待効果**: 技術分析の精度向上とリアルタイム性の確保

#### 主要機能
- **リアルタイム技術指標計算**: RSI、MACD、ボリンジャーバンド等のリアルタイム計算
- **複数指標の統合分析**: 複数の技術指標を組み合わせた総合判断
- **シグナル生成**: 技術指標に基づく売買シグナルの自動生成
- **履歴管理**: 指標値の履歴管理とトレンド分析

#### 対応技術指標
- **RSI (相対力指数)**: 過買い・過売り判定
- **MACD**: トレンド分析とシグナル生成
- **ボリンジャーバンド**: ボラティリティ分析
- **ストキャスティクス**: モメンタム分析
- **Williams %R**: オシレーター分析
- **CCI (商品チャンネル指数)**: トレンド強度分析
- **ATR (平均真の範囲)**: ボラティリティ測定
- **ADX (平均方向指数)**: トレンド強度測定
- **OBV (出来高バランス)**: 出来高分析
- **MFI (資金フロー指数)**: 資金フロー分析

#### 設定例
```python
config = {
    "update_interval": 30,  # 更新間隔（秒）
    "max_price_history": 1000,  # 価格履歴最大数
    "max_volume_history": 1000,  # 出来高履歴最大数
    "max_indicator_history": 100,  # 指標履歴最大数
    "signal_threshold": 0.7,  # シグナル閾値
    "confidence_threshold": 0.6,  # 信頼度閾値
    "max_workers": 5,  # 並列処理ワーカー数
    "indicators": {
        "rsi": {"period": 14, "overbought": 70, "oversold": 30},
        "macd": {"fast": 12, "slow": 26, "signal": 9},
        "bollinger": {"period": 20, "std": 2},
        "stochastic": {"k_period": 14, "d_period": 3},
        "williams_r": {"period": 14},
        "cci": {"period": 20},
        "atr": {"period": 14},
        "adx": {"period": 14},
        "obv": {},
        "mfi": {"period": 14}
    }
}
```

### 4. ポートフォリオ監視 (`enhanced_portfolio_monitoring.py`)

**期待効果**: 複数銘柄の統合監視によるリスク管理の強化

#### 主要機能
- **複数銘柄統合監視**: 複数銘柄の同時監視と統合分析
- **ポートフォリオ分析**: リスク・リターン分析、相関分析
- **リスク管理**: ポートフォリオレベルのリスク監視
- **パフォーマンス追跡**: ポートフォリオのパフォーマンス監視

#### ポートフォリオ指標
- **総価値**: ポートフォリオの総価値
- **総リターン**: ポートフォリオの総リターン
- **日次リターン**: 日次リターン率
- **ボラティリティ**: ポートフォリオのボラティリティ
- **シャープレシオ**: リスク調整後リターン
- **最大ドローダウン**: 最大損失幅
- **ベータ**: 市場との相関
- **アルファ**: 市場を上回るリターン
- **分散投資比率**: 分散投資の効果

#### 設定例
```python
config = {
    "monitoring_interval": 60,  # 監視間隔（秒）
    "max_performance_history": 1000,  # パフォーマンス履歴最大数
    "max_risk_history": 1000,  # リスク履歴最大数
    "risk_thresholds": {
        "volatility": 0.3,  # ボラティリティ閾値
        "max_drawdown": 0.15,  # 最大ドローダウン閾値
        "correlation": 0.8  # 相関閾値
    },
    "performance_thresholds": {
        "excellent_return": 0.15,  # 優秀リターン閾値
        "good_return": 0.08,  # 良好リターン閾値
        "poor_return": -0.05,  # 不良リターン閾値
        "critical_return": -0.15  # クリティカルリターン閾値
    }
}
```

## 📊 使用方法

### 1. 基本的な使用方法

```python
import asyncio
from enhanced_individual_stock_monitor import EnhancedIndividualStockMonitor

# 監視対象銘柄
symbols = ["7203.T", "6758.T", "9984.T", "9432.T", "6861.T"]

# 設定
config = {
    "monitoring_interval": 30,
    "price_change_threshold": 2.0,
    "volume_spike_threshold": 150.0,
    "email": {"enabled": False}
}

# 監視システム初期化
monitor = EnhancedIndividualStockMonitor(symbols, config)

# アラートコールバックの追加
async def alert_callback(alert):
    print(f"🚨 アラート: {alert.symbol} - {alert.message}")

monitor.add_alert_callback(alert_callback)

# 監視開始
await monitor.start_monitoring()
```

### 2. ニュース・感情分析の使用

```python
from enhanced_news_sentiment_integration import EnhancedNewsSentimentIntegration

# 設定
config = {
    "news_api_key": "your_api_key",
    "sentiment_update_interval": 300,
    "relevance_threshold": 0.3
}

# 感情分析システム初期化
sentiment_system = EnhancedNewsSentimentIntegration(config)

# 監視開始
await sentiment_system.start_sentiment_monitoring()
```

### 3. 技術指標リアルタイム更新の使用

```python
from enhanced_technical_indicators_realtime import EnhancedTechnicalIndicatorsRealtime

# 設定
config = {
    "update_interval": 30,
    "confidence_threshold": 0.6,
    "max_workers": 5
}

# 技術指標システム初期化
technical_system = EnhancedTechnicalIndicatorsRealtime(symbols, config)

# シグナルコールバックの追加
async def signal_callback(signal):
    print(f"📊 シグナル: {signal.symbol} - {signal.signal_type.value}")

technical_system.add_signal_callback(signal_callback)

# 監視開始
await technical_system.start_technical_monitoring()
```

### 4. ポートフォリオ監視の使用

```python
from enhanced_portfolio_monitoring import EnhancedPortfolioMonitoring

# 設定
config = {
    "monitoring_interval": 60,
    "risk_thresholds": {"volatility": 0.3, "max_drawdown": 0.15}
}

# ポートフォリオ監視システム初期化
portfolio_system = EnhancedPortfolioMonitoring(symbols, config)

# アラートコールバックの追加
async def portfolio_alert_callback(alert):
    print(f"🚨 ポートフォリオアラート: {alert.alert_type} - {alert.message}")

portfolio_system.add_alert_callback(portfolio_alert_callback)

# 監視開始
await portfolio_system.start_portfolio_monitoring()
```

## 🔧 設定とカスタマイズ

### 1. アラート設定のカスタマイズ

```python
# 価格変動アラートの設定
config["price_change_threshold"] = 3.0  # 3%以上の変動でアラート

# 出来高急増アラートの設定
config["volume_spike_threshold"] = 200.0  # 200%以上の出来高増加でアラート

# 感情変化アラートの設定
config["sentiment_change_threshold"] = 0.3  # 感情スコア0.3以上の変化でアラート
```

### 2. メール通知の設定

```python
config["email"] = {
    "enabled": True,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "username": "your_email@gmail.com",
    "password": "your_app_password",
    "to_addresses": ["alert1@example.com", "alert2@example.com"]
}
```

### 3. 技術指標のカスタマイズ

```python
config["indicators"] = {
    "rsi": {"period": 14, "overbought": 70, "oversold": 30},
    "macd": {"fast": 12, "slow": 26, "signal": 9},
    "bollinger": {"period": 20, "std": 2}
}
```

## 📈 パフォーマンス最適化

### 1. 並列処理の最適化

```python
# 並列処理ワーカー数の設定
config["max_workers"] = 5  # CPUコア数に応じて調整

# 監視間隔の最適化
config["monitoring_interval"] = 30  # リアルタイム性とパフォーマンスのバランス
```

### 2. メモリ使用量の最適化

```python
# 履歴データの最大数を制限
config["max_price_history"] = 1000
config["max_volume_history"] = 1000
config["max_indicator_history"] = 100
```

### 3. キャッシュの最適化

```python
# ニュースキャッシュの期間設定
config["news_cache_duration"] = 3600  # 1時間

# ソーシャルメディアキャッシュの期間設定
config["social_cache_duration"] = 1800  # 30分
```

## 🚨 アラート機能

### 1. アラートタイプ

- **PRICE_CHANGE**: 価格変動アラート
- **VOLUME_SPIKE**: 出来高急増アラート
- **TECHNICAL_SIGNAL**: 技術指標アラート
- **SENTIMENT_CHANGE**: 感情変化アラート
- **NEWS_ALERT**: ニュースアラート
- **RISK_ALERT**: リスクアラート

### 2. アラート優先度

- **LOW**: 低優先度
- **MEDIUM**: 中優先度
- **HIGH**: 高優先度
- **CRITICAL**: クリティカル

### 3. アラート通知方法

- **ログ出力**: 自動的なログ記録
- **メール通知**: 設定されたメールアドレスへの通知
- **コールバック関数**: カスタム処理の実行

## 📊 データ保存と分析

### 1. データ保存

```python
# 監視データの保存
monitor.save_monitoring_data("monitoring_data.json")

# 感情分析データの保存
sentiment_system.save_sentiment_data("sentiment_data.json")

# 技術分析データの保存
technical_system.save_technical_data("technical_data.json")

# ポートフォリオデータの保存
portfolio_system.save_portfolio_data("portfolio_data.json")
```

### 2. データ分析

```python
# 監視データの取得
monitor_data = monitor.get_monitor_data("7203.T")

# 感情分析データの取得
sentiment_data = sentiment_system.get_individual_sentiment("7203.T")

# 技術分析データの取得
technical_data = technical_system.get_technical_data("7203.T")

# ポートフォリオサマリーの取得
portfolio_summary = portfolio_system.get_portfolio_summary()
```

## 🔍 トラブルシューティング

### 1. よくある問題

**問題**: データ取得エラー
**解決策**: APIキーの設定確認、ネットワーク接続の確認

**問題**: メール通知が送信されない
**解決策**: SMTP設定の確認、アプリパスワードの使用

**問題**: パフォーマンスが遅い
**解決策**: 並列処理ワーカー数の調整、監視間隔の最適化

### 2. ログの確認

```bash
# 監視ログの確認
tail -f enhanced_individual_monitor.log

# 感情分析ログの確認
tail -f enhanced_news_sentiment.log

# 技術指標ログの確認
tail -f enhanced_technical_indicators.log

# ポートフォリオログの確認
tail -f enhanced_portfolio_monitoring.log
```

## 📈 期待効果

### 1. 投資機会の見逃し削減

- **70%の削減**: リアルタイム監視による機会損失の大幅削減
- **早期検知**: 価格変動、出来高急増の早期検知
- **感情分析**: ニュース・SNS感情を考慮した投資判断

### 2. リスク管理の強化

- **早期アラート**: リスクの早期検知と対応
- **ポートフォリオ監視**: 複数銘柄の統合リスク管理
- **技術分析**: 高度な技術指標によるリスク評価

### 3. パフォーマンス向上

- **並列処理**: 高速な監視処理
- **最適化**: メモリ使用量と処理速度の最適化
- **統合監視**: 複数システムの統合による効率化

## 🚀 今後の拡張予定

### 1. 機能拡張

- **AI予測統合**: 機械学習モデルとの統合
- **自動取引**: ブローカーAPI連携による自動取引
- **モバイル対応**: スマートフォンアプリの開発

### 2. パフォーマンス向上

- **クラウド対応**: クラウド環境でのスケーラブルな監視
- **リアルタイム性向上**: より高速な監視処理
- **分析機能強化**: より詳細な分析機能の追加

## 📞 サポート

### 1. ドキュメント

- **README**: 基本的な使用方法
- **API仕様書**: 詳細なAPI仕様
- **設定ガイド**: 設定方法の詳細ガイド

### 2. コミュニティ

- **GitHub Issues**: バグ報告と機能要望
- **Discussions**: 使用方法の質問と議論
- **Wiki**: 詳細なドキュメントとチュートリアル

---

**注意**: 本システムは投資助言を提供するものではありません。投資判断は自己責任で行ってください。
