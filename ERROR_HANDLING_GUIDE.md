# エラーハンドリング改善ガイド

## 概要

J-Quants株価予測システムのエラーハンドリングを包括的に改善し、デバッグの容易性とユーザビリティを向上させました。

## 改善内容

### 1. 包括的エラーハンドリングシステム

#### 新規追加ファイル
- `error_handler.py`: 包括的エラーハンドリングユーティリティ
- `enhanced_logging.py`: 強化されたログシステム

#### 主要な改善点

##### エラー分類の詳細化
- **API関連エラー**: 接続エラー、認証エラー、HTTPステータスエラー
- **データ処理エラー**: データ型エラー、欠損値エラー、検証エラー
- **モデルエラー**: 学習エラー、予測エラー、特徴量エラー
- **ファイルエラー**: 読み書き権限エラー、パスエラー、容量エラー

##### コンテキスト情報の充実
```python
# 改善前
except Exception as e:
    logger.error(f"エラー: {e}")

# 改善後
except Exception as e:
    self.error_handler.log_error(
        e, 
        "データ処理エラー",
        {
            'operation': 'データ読み込み',
            'file_path': input_file,
            'data_shape': df.shape if df is not None else None,
            'encoding': successful_encoding
        }
    )
```

### 2. 強化されたログシステム

#### ログレベルの適切な使用
- **DEBUG**: 詳細な処理情報
- **INFO**: 正常な操作の記録
- **WARNING**: 注意が必要な状況
- **ERROR**: エラーが発生したが処理継続可能
- **CRITICAL**: 処理停止が必要な重大なエラー

#### 構造化ログ出力
```json
{
  "timestamp": "2024-01-15T10:30:45.123456",
  "level": "ERROR",
  "logger": "JQuantsDataFetch",
  "message": "APIリクエスト失敗",
  "module": "jquants_data_fetch",
  "function": "_make_request_with_retry",
  "line": 85,
  "context": {
    "api_name": "J-Quants API",
    "endpoint": "https://api.jquants.com/v1/prices/daily_quotes",
    "status_code": 401,
    "retry_count": 2
  }
}
```

### 3. 主要ファイルの改善

#### `jquants_data_fetch.py`
- **API接続エラー**: タイムアウト、接続エラーの詳細分類
- **認証エラー**: トークン取得失敗の詳細情報
- **データ検証エラー**: 取得データの品質チェック強化

#### `jquants_data_preprocessing.py`
- **ファイルエラー**: 読み書き権限、エンコーディング問題の詳細処理
- **データ処理エラー**: 型変換、欠損値処理のエラー分類
- **技術指標計算エラー**: 計算失敗時の代替処理

#### `model_factory.py`
- **モデル作成エラー**: パラメータ検証、依存関係チェック
- **学習エラー**: データ不整合、メモリ不足の詳細処理
- **予測エラー**: 入力データ検証、モデル状態チェック

### 4. エラー復旧機能

#### 自動リトライ機能
```python
def handle_connection_error(self, error: Exception, retry_count: int = 0, 
                          max_retries: int = 3) -> bool:
    """接続エラーのハンドリング（リトライ可能）"""
    if retry_count < max_retries:
        self.logger.info(f"⏳ 接続を再試行します ({retry_count + 1}/{max_retries + 1})")
        return True  # リトライ可能
    else:
        self.logger.error("❌ 最大リトライ回数に達しました")
        return False  # リトライ不可
```

#### 代替処理機能
```python
def handle_model_training_error(self, error: Exception, 
                              model_name: str, 
                              training_data_info: Dict[str, Any] = None) -> bool:
    """モデル学習エラーのハンドリング"""
    # 代替モデルでの学習を試行
    self.logger.warning("⚠️ 代替モデルでの学習を試行します")
    return True  # 代替処理を試行
```

### 5. ログファイル管理

#### ログファイルの種類
- `enhanced.log`: 詳細な操作ログ（全レベル）
- `errors.log`: エラーのみのログ
- `application.log`: アプリケーション全体のログ（ローテーション対応）
- `error_details.log`: エラーの詳細情報（JSON形式）

#### ログローテーション
- ファイルサイズ制限: 10MB
- バックアップファイル数: 5個
- 自動圧縮: 古いログファイルの圧縮

### 6. 使用方法

#### 基本的なエラーハンドリング
```python
from error_handler import get_error_handler, get_specific_error_handler

# エラーハンドラーの初期化
error_handler = get_error_handler("MyModule")
specific_error_handler = get_specific_error_handler("MyModule")

try:
    # 処理実行
    result = some_operation()
except ValueError as e:
    error_handler.log_error(e, "値エラー", {'context': 'additional_info'})
    raise
except ConnectionError as e:
    if specific_error_handler.handle_connection_error(e, retry_count, max_retries):
        # リトライ処理
        pass
    else:
        raise
```

#### 強化ログの使用
```python
from unified_logging_config import get_system_logger

# ログ設定
logger = get_system_logger()

# 操作ログ
logger.info("データ処理開始", extra={"input_file": "data.csv"})
logger.info("処理データ", extra={"shape": (1000, 10), "dtype": "float64"})
logger.info("データ処理完了", extra={"success": True, "records": 1000})
```

### 7. デバッグ支援

#### エラー詳細の確認
```bash
# エラーログの確認
tail -f errors.log

# 詳細エラー情報の確認
cat error_details.log

# 構造化ログの確認
jq '.' structured.log
```

#### パフォーマンス監視
```bash
# 処理時間の確認
grep "実行時間" enhanced.log

# データサイズの確認
grep "データ情報" enhanced.log
```

## 効果

### デバッグの改善
- **エラー原因の特定**: 詳細なコンテキスト情報により、エラーの根本原因を迅速に特定
- **処理フローの追跡**: 操作開始/終了ログにより、処理の進行状況を把握
- **パフォーマンス分析**: 処理時間、データサイズの記録により、ボトルネックを特定

### ユーザビリティの向上
- **分かりやすいエラーメッセージ**: ユーザーが理解しやすいエラー説明
- **復旧手順の提示**: エラー発生時の対処法を具体的に提示
- **処理状況の可視化**: リアルタイムでの処理状況表示

### 運用性の向上
- **自動復旧**: 一時的なエラーの自動復旧により、手動介入を削減
- **ログ管理**: 構造化ログにより、ログ分析の自動化が可能
- **監視強化**: エラー発生パターンの把握により、予防的な対策が可能

## 今後の拡張

### 監視システムとの連携
- **アラート機能**: 重大なエラーの自動通知
- **メトリクス収集**: エラー率、処理時間の統計収集
- **ダッシュボード**: リアルタイムでのシステム状況表示

### 機械学習による予測
- **エラー予測**: 過去のエラーパターンから将来のエラーを予測
- **自動チューニング**: パフォーマンスに基づく自動パラメータ調整
- **異常検知**: システムの異常な動作パターンの検出
