# 🚨 レガシーファイル廃止予定通知

## 概要

J-Quants株価予測システムの最高優先度問題（アーキテクチャの複雑性と重複コード）を解決するため、以下のレガシーファイルを廃止予定とします。

## 📋 廃止予定ファイル一覧

### 設定ファイル
- `config.yaml` → `config_final.yaml`に統合済み
- `sentiment_config.yaml` → `config_final.yaml`に統合済み  
- `hft_config.yaml` → `config_final.yaml`に統合済み
- `test_config.yaml` → `config_final.yaml`に統合済み

### システムファイル
- `unified_jquants_system.py` → `unified_system.py`に統合済み
- `integrated_sentiment_system.py` → `unified_system.py`に統合済み
- `jquants_stock_prediction.py` → `unified_system.py`に統合済み

### エラーハンドリングファイル
- `unified_error_handler.py` → `unified_system.py`に統合済み
- `enhanced_logging.py` → `unified_system.py`に統合済み
- `unified_error_logging_system.py` → `unified_system.py`に統合済み

## 🎯 統合後のアーキテクチャ

### 統合システム (`unified_system.py`)
- **単一責任原則**: すべての機能を統合
- **統合エラーハンドリング**: 8つのエラーカテゴリで分類
- **統合ログシステム**: 機密情報マスキング機能付き
- **統合設定管理**: 単一設定ファイル (`config_final.yaml`)

### 統合設定ファイル (`config_final.yaml`)
- **システム設定**: 基本情報、環境設定
- **J-Quants API設定**: API設定、認証、エンドポイント
- **データ処理設定**: 取得、前処理、特徴量エンジニアリング
- **予測モデル設定**: モデル選択、パラメータ、評価
- **感情分析設定**: ニュース分析、SNS分析、リアルタイム指標
- **高頻度取引設定**: レイテンシー、利益、リスク管理
- **トレーディング設定**: 監視対象、シグナル、リスク管理
- **統合システム設定**: 最適化、レガシー廃止予定

## 📅 廃止スケジュール

- **2024年12月31日**: レガシーファイルの完全廃止
- **移行期間**: 2024年12月1日 - 2024年12月31日
- **サポート終了**: 2024年12月31日以降、レガシーファイルのサポートは行いません

## 🔄 移行ガイド

### 1. 設定ファイルの移行
```yaml
# 旧設定 (config.yaml)
jquants:
  base_url: "https://api.jquants.com/v1"

# 新設定 (config_final.yaml)
jquants:
  base_url: "https://api.jquants.com/v1"
  timeout: 30
  max_retries: 3
  # 追加の統合設定...
```

### 2. システムファイルの移行
```python
# 旧システム
from jquants_stock_prediction import JQuantsStockPrediction
system = JQuantsStockPrediction()

# 新統合システム
from unified_system import get_unified_system
system = get_unified_system("MainSystem")
```

### 3. エラーハンドリングの移行
```python
# 旧エラーハンドリング
try:
    # 処理
except Exception as e:
    logger.error(f"エラー: {e}")

# 新統合エラーハンドリング
try:
    # 処理
except Exception as e:
    system.log_error(e, "処理エラー", ErrorCategory.DATA_PROCESSING_ERROR)
```

## ✅ 統合の利点

### 1. **メンテナンス性の向上**
- 単一ファイルでの管理
- 重複コードの削除
- 一貫したエラーハンドリング

### 2. **パフォーマンスの向上**
- メモリ使用量の削減
- 処理速度の向上
- ログファイルの統合

### 3. **開発効率の向上**
- 設定の一元管理
- デバッグの簡素化
- テストの統合

## 🚀 推奨アクション

1. **即座に実行**: 新統合システム (`unified_system.py`) への移行
2. **設定更新**: `config_final.yaml` の使用開始
3. **テスト実行**: 統合システムの動作確認
4. **レガシー削除**: 廃止予定ファイルの削除準備

## 📞 サポート

移行に関する質問や問題がございましたら、統合システムのドキュメントを参照してください。

---
**最終更新**: 2024年12月
**廃止予定日**: 2024年12月31日