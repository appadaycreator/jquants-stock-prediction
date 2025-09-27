# 🚨 レガシーモジュール廃止予定通知

## 概要

J-Quants株価予測システムのアーキテクチャ改善により、以下のモジュールは**廃止予定**となりました。

## 廃止予定モジュール

### 1. 個別モジュール（廃止予定）
- `jquants_stock_prediction.py` - 個別予測モジュール
- `jquants_data_preprocessing.py` - 個別前処理モジュール
- `jquants_data_fetch.py` - 個別データ取得モジュール

### 2. 重複設定ファイル（廃止予定）
- `config/api.yaml` - API設定
- `config/core.yaml` - コア設定
- `config/data.yaml` - データ設定
- `config/models.yaml` - モデル設定

### 3. 重複エラーハンドリング（廃止予定）
- `unified_error_handler.py` - 旧統合エラーハンドラー
- `enhanced_logging.py` - 旧強化ログシステム

## 移行先

### ✅ 推奨システム（統合システム）
- **メインシステム**: `unified_jquants_system.py` - 完全統合システム
- **統合設定**: `config_unified.yaml` - 単一設定ファイル
- **統合エラーハンドリング**: `unified_error_logging_system.py` - 統一エラーハンドリング
- **統合設定ローダー**: `unified_config_loader.py` - 統一設定管理

## 移行スケジュール

### Phase 1: 即座に実行（完了済み）
- ✅ 統合システムの実装
- ✅ 統合設定ファイルの作成
- ✅ 統合エラーハンドリングの実装

### Phase 2: 段階的移行（進行中）
- 🔄 既存コードの統合システムへの移行
- 🔄 レガシーモジュールの使用停止
- 🔄 テストの更新

### Phase 3: 完全廃止（予定）
- ⏳ レガシーモジュールの削除
- ⏳ 重複ファイルの削除
- ⏳ ドキュメントの更新

## 移行方法

### 1. コードの移行
```python
# 旧方式（廃止予定）
from jquants_stock_prediction import predict_stock_prices
from jquants_data_preprocessing import preprocess_data
from config_loader import get_config

# 新方式（推奨）
from unified_jquants_system import UnifiedJQuantsSystem
from unified_config_loader import get_unified_config

# 統合システムの使用
system = UnifiedJQuantsSystem()
result = system.predict_stock_prices(input_file)
```

### 2. 設定の移行
```yaml
# 旧方式（廃止予定）
# config/api.yaml, config/core.yaml, config/data.yaml, config/models.yaml

# 新方式（推奨）
# config_unified.yaml - 単一設定ファイル
```

### 3. エラーハンドリングの移行
```python
# 旧方式（廃止予定）
from unified_error_handler import get_unified_error_handler
from enhanced_logging import setup_enhanced_logging

# 新方式（推奨）
from unified_error_logging_system import get_unified_error_logging_system
```

## 利点

### 1. アーキテクチャの簡素化
- 単一責任原則の徹底
- 重複コードの削除
- メンテナンス性の向上

### 2. 設定管理の統一
- 単一設定ファイル
- 環境別設定の明確化
- 設定検証の強化

### 3. エラーハンドリングの統一
- 統一エラーハンドリング
- ログレベルの標準化
- エラー分類の明確化

## 注意事項

1. **即座に移行を開始してください**
2. **新しいコードでは統合システムのみを使用してください**
3. **レガシーモジュールの使用は避けてください**
4. **移行期間中は両システムが並行稼働します**

## サポート

移行に関する質問や問題がある場合は、統合システムのドキュメントを参照するか、開発チームにご連絡ください。

---

**重要**: この廃止予定通知は、システムの品質向上とメンテナンス性の改善を目的としています。早期の移行をお願いします。
