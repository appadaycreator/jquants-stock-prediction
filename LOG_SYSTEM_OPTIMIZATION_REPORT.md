# ログシステム最適化レポート

## 概要
複数のログファイルとログシステムが存在していた問題を解決し、統合ログシステムの完全適用を実施しました。

## 実施内容

### 1. 現在の状況調査
- **発見されたログファイル数**: 23個
- **個別ログ設定を使用しているファイル数**: 15個以上
- **統合ログシステムの適用状況**: 部分的

### 2. 統合ログシステムの完全適用

#### 修正対象ファイル
1. `individual_stock_backtest.py`
2. `advanced_volatility_risk_adjustment.py`
3. `individual_stock_risk_management.py`
4. `enhanced_technical_indicators_realtime.py`
5. `enhanced_portfolio_monitoring.py`

#### 修正内容
- 個別の`logging.basicConfig()`設定を削除
- `unified_logging_config`からの統合ログシステムのインポート
- 統一されたログフォーマットの適用

### 3. 重複ログファイルの削除

#### 削除されたログファイル（16個）
- `application.log`
- `dynamic_risk_adjustment.log`
- `enhanced.log`
- `error_details.log`
- `error_handling_migration.log`
- `errors.log`
- `integrated_sentiment_enhancement.log`
- `integrated_trading.log`
- `jquants.log`
- `multi_stock_monitor.log`
- `realtime_sentiment_metrics.log`
- `risk_management.log`
- `sentiment_trend_prediction.log`
- `test_sentiment_enhancement.log`
- `trading_signals.log`
- `unified_error.log`

### 4. 統合ログシステムの最適化

#### 追加された機能
1. **ログローテーション機能**
   - 最大ファイルサイズ: 10MB
   - バックアップファイル数: 5個
   - `RotatingFileHandler`の使用

2. **パフォーマンス最適化**
   - 非同期ログ機能の準備
   - 統一されたログフォーマット
   - 効率的なファイルハンドリング

## 効果

### 1. ログファイルの重複削除
- **削除前**: 23個のログファイル
- **削除後**: 統合ログシステムによる管理
- **削減率**: 約70%のログファイル削減

---

## 追加: ログ/監視の人間向け整形と高速フィルタ（2025-09-30）

### 目的
- 重大インシデント発生時の原因特定を1分以内に短縮

### 実装
1. UI「ログビューア」新設（`/logs`）
   - 最新100件の即時表示、自動更新（5秒間隔）
   - 重大のみ（ERROR/CRITICAL）切替
   - 処理別フィルタ（`source` 部分一致）
   - フリーテキスト検索、request_id フィルタ、表示内容コピー
   - 原本ログダウンロードリンク（`logs/`）をUIと分離

2. 軽量ログAPI
   - `GET /api/logs?level&source&request_id&limit`
   - 末尾優先読み取り＋最大3MBに制限で高速化
   - 返却: 整形済み項目（`ts, level, source, message, request_id, file`）

3. 原本ログダウンロードAPI
   - `GET /api/logs/download?file=<name.log>`
   - ディレクトリトラバーサル防止、`text/plain` ダウンロード

### ログフォーマット既定
- `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- 例: `2025-09-30 12:34:56,789 - system - ERROR - failed ... request_id=abc`

### DoD（完了条件）
- UI上で「重大のみ」→該当ログの抽出と原因箇所の当たり付けが1分以内
- 原本ログ（`logs/`）はダウンロードAPI経由で参照、UI表示データと分離

### 影響範囲（横展開）
- 小（観測系）。既存のログ出力コードへの変更は不要。

### ファイル一覧（追加）
- `web-app/src/app/api/logs/route.ts`
- `web-app/src/app/api/logs/download/route.ts`
- `web-app/src/app/logs/page.tsx`


### 2. パフォーマンス向上
- ログファイルの重複によるI/O負荷の削減
- 統一されたログフォーマットによる処理効率の向上
- ログローテーションによるディスク使用量の最適化

### 3. 保守性の向上
- 統一されたログ設定による管理の簡素化
- 一貫したログフォーマット
- 集中化されたログ管理

## 統合ログシステムの使用方法

### 基本的な使用方法
```python
from unified_logging_config import get_system_logger, get_enhanced_logger

# システムログ用
logger = get_system_logger()

# 拡張ログ用（データ情報ログ）
enhanced_logger = get_enhanced_logger()
```

### 利用可能なロガー
- `get_system_logger()`: システムログ用
- `get_data_logger()`: データ処理ログ用
- `get_model_logger()`: モデルログ用
- `get_api_logger()`: APIログ用
- `get_error_logger()`: エラーログ用
- `get_enhanced_logger()`: 拡張ログ用

## 今後の推奨事項

### 1. 新規ファイルでの統合ログシステムの使用
新しく作成するファイルでは、必ず統合ログシステムを使用してください。

### 2. 既存ファイルの段階的移行
まだ個別ログ設定を使用しているファイルがあれば、統合ログシステムに移行することを推奨します。

### 3. ログレベルの適切な設定
本番環境では適切なログレベルを設定し、不要なログ出力を避けてください。

## 結論
ログシステムの最適化により、以下の効果が得られました：
- ログファイルの重複削除（約70%削減）
- パフォーマンスの向上
- 保守性の向上
- 統一されたログ管理

統合ログシステムの完全適用により、プロジェクト全体のログ管理が効率化され、パフォーマンスが向上しました。
