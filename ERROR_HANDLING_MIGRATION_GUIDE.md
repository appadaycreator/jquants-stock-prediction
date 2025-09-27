# エラーハンドリングシステム移行ガイド

## 移行概要

このガイドは、複数のエラーハンドリングシステムを統合システムに移行するための手順を説明します。

## 移行対象システム

### 1. unified_error_handler.py (旧統合システム)
- 使用ファイル数: 2
- 状態: 廃止予定

### 2. unified_error_logging_system.py (新統合システム)
- 使用ファイル数: 1
- 状態: 統合対象

### 3. enhanced_logging.py (強化ログシステム)
- 使用ファイル数: 2
- 状態: 機能統合

## 新しい統合システム

### unified_error_handling_system.py
統合されたエラーハンドリングシステムの特徴:
- 統一されたエラー分類とハンドリング
- 構造化ログ出力
- エラー復旧機能
- パフォーマンス監視
- セキュリティ監査

## 移行手順

### 1. インポート文の更新

#### 旧形式:
```python
from unified_error_handler import get_unified_error_handler
from unified_error_logging_system import get_unified_error_logging_system
from unified_logging_config import get_system_logger
```

#### 新形式:
```python
from unified_error_handling_system import (
    get_unified_error_handler,
    ErrorCategory,
    ErrorSeverity,
    error_handler,
    error_context,
    log_api_error,
    log_data_error,
    log_model_error,
    log_file_error
)
```

### 2. エラーハンドリングの更新

#### 旧形式:
```python
error_handler = get_unified_error_handler()
error_handler.log_error(error, "エラー説明")
```

#### 新形式:
```python
from unified_error_handling_system import get_unified_error_handler, ErrorCategory, ErrorSeverity

error_handler = get_unified_error_handler()
error_handler.log_error(
    error=error,
    category=ErrorCategory.API,
    severity=ErrorSeverity.HIGH,
    operation="API呼び出し"
)
```

### 3. デコレータの使用

#### 新機能:
```python
from unified_error_handling_system import error_handler, ErrorCategory, ErrorSeverity

@error_handler(ErrorCategory.API, ErrorSeverity.HIGH, "API呼び出し")
def api_call():
    # API呼び出し処理
    pass
```

### 4. コンテキストマネージャーの使用

#### 新機能:
```python
from unified_error_handling_system import error_context, ErrorCategory, ErrorSeverity

with error_context("データ処理", ErrorCategory.DATA, ErrorSeverity.MEDIUM) as error_handler:
    # データ処理
    pass
```

## 影響を受けるファイル

### unified_error_handler を使用しているファイル:
- /Users/masayukitokunaga/workspace/jquants-stock-prediction/unified_jquants_system.py
- /Users/masayukitokunaga/workspace/jquants-stock-prediction/tests/unit/test_edge_cases_comprehensive.py

### unified_error_logging_system を使用しているファイル:
- /Users/masayukitokunaga/workspace/jquants-stock-prediction/unified_jquants_system.py

### enhanced_logging を使用しているファイル:
- /Users/masayukitokunaga/workspace/jquants-stock-prediction/enhanced_logging.py
- /Users/masayukitokunaga/workspace/jquants-stock-prediction/jquants_data_preprocessing.py

## 移行後の確認事項

1. すべてのインポート文が更新されているか
2. エラーハンドリングの動作が正常か
3. ログ出力が期待通りか
4. パフォーマンスに問題がないか

## ロールバック手順

移行に問題が発生した場合:

1. バックアップファイルの復元
2. 旧システムの再有効化
3. 問題の調査と修正

## サポート

移行に関する質問や問題がある場合は、開発チームに連絡してください。
