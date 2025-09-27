# 高頻度取引アルゴリズムシステム

## 概要

このシステムは、複数の取引所間での価格差を利用した裁定取引を自動実行する高頻度取引（HFT）アルゴリズムです。ミリ秒単位のレイテンシーで取引機会を発見し、リスク管理機能を備えた安全な取引を実現します。

## 主な機能

### 1. 裁定取引アルゴリズム
- 複数取引所間の価格差をリアルタイム監視
- 利益率閾値に基づく自動取引実行
- ミリ秒単位の高速取引処理

### 2. リスク管理
- ポジションサイズ制限
- 日次損失制限
- ストップロス機能
- 同時取引数制限

### 3. パフォーマンス監視
- 実行時間計測
- 利益・損失追跡
- 取引統計
- リアルタイム監視

### 4. 複数取引所対応
- Binance
- Coinbase
- Kraken
- その他の取引所（拡張可能）

## システム構成

```
high_frequency_trading.py     # メインシステム
├── HighFrequencyTrading      # 高頻度取引クラス
├── ArbitrageOpportunity      # 裁定取引機会クラス
├── Trade                     # 取引クラス
├── MarketData               # 市場データクラス
└── MockDataSource           # モックデータソース

tests/
└── test_high_frequency_trading.py  # テストファイル

hft_config.yaml              # 設定ファイル
```

## インストール

### 必要な依存関係

```bash
pip install numpy pandas asyncio
```

### 環境変数の設定

```bash
# 取引所APIキー
export BINANCE_API_KEY="your_binance_api_key"
export BINANCE_SECRET_KEY="your_binance_secret_key"
export COINBASE_API_KEY="your_coinbase_api_key"
export COINBASE_SECRET_KEY="your_coinbase_secret_key"
export KRAKEN_API_KEY="your_kraken_api_key"
export KRAKEN_SECRET_KEY="your_kraken_secret_key"

# その他の設定
export ENCRYPTION_KEY="your_encryption_key"
export SLACK_WEBHOOK_URL="your_slack_webhook_url"
```

## 使用方法

### 基本的な使用例

```python
from high_frequency_trading import HighFrequencyTrading

# 設定
config = {
    'latency_threshold': 0.001,  # 1ms
    'profit_threshold': 0.001,   # 0.1%
    'max_position_size': 1000000,
    'risk_limit': 0.02
}

# システム初期化
hft = HighFrequencyTrading(config)

# 裁定取引実行
price_differences = {
    'BTC': {
        'Binance': 50000.0,
        'Coinbase': 50100.0
    }
}

trades = hft.execute_arbitrage(price_differences)
print(f"実行された取引数: {len(trades)}")

# パフォーマンス指標取得
metrics = hft.get_performance_metrics()
print(f"総利益: {metrics['profit_loss']}")
print(f"平均実行時間: {metrics['avg_execution_time']:.4f}s")

# クリーンアップ
hft.cleanup()
```

### 設定ファイルの使用

```python
import yaml
from high_frequency_trading import HighFrequencyTrading

# 設定ファイル読み込み
with open('hft_config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# システム初期化
hft = HighFrequencyTrading(config)
```

## 設定項目

### レイテンシー設定
- `latency_threshold`: 実行時間閾値（秒）
- `max_execution_time`: 最大実行時間（秒）
- `network_timeout`: ネットワークタイムアウト（秒）

### 利益設定
- `profit_threshold`: 最小利益率
- `target_spread`: 目標スプレッド
- `max_profit_per_trade`: 最大利益（ドル）

### リスク管理
- `max_position_size`: 最大ポジションサイズ（ドル）
- `risk_limit`: リスク制限（パーセンテージ）
- `max_daily_loss`: 最大日次損失（ドル）
- `stop_loss_percentage`: ストップロス（パーセンテージ）

## テスト

### テスト実行

```bash
# 全テスト実行
python -m pytest tests/test_high_frequency_trading.py -v

# 特定のテスト実行
python -m pytest tests/test_high_frequency_trading.py::TestHighFrequencyTrading::test_execute_arbitrage -v
```

### テストカバレッジ

```bash
# カバレッジレポート生成
python -m pytest tests/test_high_frequency_trading.py --cov=high_frequency_trading --cov-report=html
```

## パフォーマンス最適化

### 1. レイテンシー最適化
- 非同期処理の活用
- メモリプールの使用
- ネットワーク最適化

### 2. メモリ最適化
- データ構造の最適化
- ガベージコレクション調整
- キャッシュ戦略

### 3. CPU最適化
- マルチスレッド処理
- 並列計算
- アルゴリズム最適化

## 監視・アラート

### パフォーマンス監視
- 実行時間監視
- 利益・損失追跡
- エラー率監視
- リソース使用量監視

### アラート設定
- 実行時間超過
- 損失閾値超過
- エラー率上昇
- システム異常

## セキュリティ

### APIキー管理
- 環境変数での管理
- 暗号化保存
- 定期的なローテーション

### アクセス制御
- IP制限
- 認証機能
- 監査ログ

## トラブルシューティング

### よくある問題

1. **実行時間が閾値を超える**
   - ネットワーク遅延の確認
   - システムリソースの確認
   - 設定値の調整

2. **取引が実行されない**
   - 利益率閾値の確認
   - リスク制限の確認
   - API接続の確認

3. **エラーが頻発する**
   - ログファイルの確認
   - 設定値の検証
   - 依存関係の確認

### ログ確認

```bash
# ログファイルの確認
tail -f logs/hft.log

# エラーログの確認
grep "ERROR" logs/hft.log
```

## 開発・貢献

### 開発環境セットアップ

```bash
# リポジトリクローン
git clone <repository-url>
cd jquants-stock-prediction

# 仮想環境作成
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 依存関係インストール
pip install -r requirements.txt

# 開発用依存関係インストール
pip install -r requirements-dev.txt
```

### コード品質

```bash
# リント実行
flake8 high_frequency_trading.py

# 型チェック
mypy high_frequency_trading.py

# フォーマット
black high_frequency_trading.py
```

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## サポート

問題や質問がある場合は、GitHubのIssuesページで報告してください。

## 更新履歴

### v1.0.0 (2024-01-01)
- 初回リリース
- 基本的な裁定取引機能
- リスク管理機能
- パフォーマンス監視機能
