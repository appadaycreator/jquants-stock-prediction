#!/usr/bin/env python3
"""
差分更新システム（リファクタリング版）
jQuantsから取得されたデータの差分更新を管理
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union
import logging
from pathlib import Path
import hashlib
from dataclasses import dataclass
from enum import Enum
from .json_data_manager import JSONDataManager


class UpdateStatus(Enum):
    """更新ステータス列挙型"""

    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    VALIDATION_ERROR = "validation_error"
    RETRY_EXHAUSTED = "retry_exhausted"


@dataclass
class UpdateConfig:
    """更新設定クラス"""

    max_retry_attempts: int = 3
    retry_delay_seconds: int = 5
    batch_size: int = 100
    enable_validation: bool = True
    enable_compression: bool = False
    enable_backup: bool = True
    max_data_age_days: int = 30


@dataclass
class DiffResult:
    """差分結果クラス"""

    added_count: int = 0
    updated_count: int = 0
    removed_count: int = 0
    unchanged_count: int = 0
    processing_time: float = 0.0
    data_hash: Optional[str] = None
    is_significant_change: bool = False


@dataclass
class ValidationResult:
    """検証結果クラス"""

    is_valid: bool = True
    issues: List[str] = None
    warnings: List[str] = None
    data_quality_score: float = 1.0

    def __post_init__(self):
        if self.issues is None:
            self.issues = []
        if self.warnings is None:
            self.warnings = []


@dataclass
class UpdateStats:
    """更新統計クラス"""

    total_updates: int = 0
    successful_updates: int = 0
    failed_updates: int = 0
    validation_errors: int = 0
    total_processing_time: float = 0.0
    last_update_time: Optional[str] = None

    # テストで要求されるインクリメント系ユーティリティ
    def increment_total_updates(self) -> None:
        self.total_updates += 1

    def increment_successful_updates(self) -> None:
        self.successful_updates += 1

    def increment_failed_updates(self) -> None:
        self.failed_updates += 1

    def increment_validation_errors(self) -> None:
        self.validation_errors += 1

    def add_processing_time(self, seconds: float) -> None:
        self.total_processing_time += max(0.0, float(seconds))

    def set_last_update_time(self, dt: datetime) -> None:
        self.last_update_time = dt.isoformat()


@dataclass
class UpdateResult:
    """更新結果クラス"""

    success: bool
    symbol: str
    timestamp: str
    added_count: int = 0
    updated_count: int = 0
    removed_count: int = 0
    unchanged_count: int = 0
    error: Optional[str] = None


class DifferentialUpdater:
    """差分更新システム（リファクタリング版）"""

    def __init__(
        self, data_dir: str = "data", logger=None, config: Optional[UpdateConfig] = None
    ):
        """
        初期化

        Args:
            data_dir: データ保存ディレクトリ
            logger: ロガーインスタンス
            config: 更新設定
        """
        self.data_dir = Path(data_dir)
        self.logger = logger or logging.getLogger(__name__)
        self.config = config or UpdateConfig()

        # JSONDataManagerの初期化
        self.json_manager = JSONDataManager(data_dir, logger)

        # 統計情報
        self.update_stats = UpdateStats()

        # キャッシュの初期化
        self._data_cache: Dict[str, List[Dict[str, Any]]] = {}
        self._cache_timestamps: Dict[str, datetime] = {}

    def update_stock_data(
        self, symbol: str, new_data: List[Dict[str, Any]], source: str = "jquants_api"
    ) -> Dict[str, Any]:
        """
        株価データの差分更新（リファクタリング版）

        Args:
            symbol: 銘柄コード
            new_data: 新しいデータ
            source: データソース

        Returns:
            Dict[str, Any]: 更新結果
        """
        start_time = datetime.now()
        self.update_stats.total_updates += 1

        try:
            self.logger.info(f"差分更新開始: {symbol}")

            # 既存データの取得
            existing_data = self.json_manager.get_stock_data(symbol)

            # 差分の計算
            diff_result = self._calculate_comprehensive_diff(existing_data, new_data)

            # データの検証
            if self.config.enable_validation:
                validation_result = self._validate_data_integrity(
                    new_data, existing_data
                )
                if not validation_result.is_valid:
                    self.logger.warning(f"データ検証エラー: {validation_result.issues}")
                    self.update_stats.validation_errors += 1
                    return self._create_error_result(
                        symbol,
                        UpdateStatus.VALIDATION_ERROR,
                        f"データ検証エラー: {validation_result.issues}",
                    )

            # バックアップの作成
            if self.config.enable_backup:
                self._create_backup(symbol, existing_data)

            # データの保存
            save_success = self.json_manager.save_stock_data(symbol, new_data, source)

            if save_success:
                processing_time = (datetime.now() - start_time).total_seconds()
                self.update_stats.successful_updates += 1

                # 更新結果の構築
                result = self._create_success_result(
                    symbol, diff_result, processing_time, len(new_data)
                )

                self.logger.info(
                    f"差分更新完了: {symbol} - 追加:{diff_result.added_count}, "
                    f"更新:{diff_result.updated_count}, 削除:{diff_result.removed_count}"
                )

                return result
            else:
                self.update_stats.failed_updates += 1
                return self._create_error_result(
                    symbol, UpdateStatus.FAILED, "データ保存に失敗しました"
                )

        except Exception as e:
            self.logger.error(f"差分更新エラー: {symbol} - {str(e)}")
            self.update_stats.failed_updates += 1
            return self._create_error_result(symbol, UpdateStatus.FAILED, str(e))

    def _create_success_result(
        self,
        symbol: str,
        diff_result: DiffResult,
        processing_time: float,
        total_records: int,
    ) -> Dict[str, Any]:
        """成功結果の作成"""
        return {
            "success": True,
            "status": UpdateStatus.SUCCESS.value,
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "diff_summary": {
                "added": diff_result.added_count,
                "updated": diff_result.updated_count,
                "removed": diff_result.removed_count,
                "total_records": total_records,
            },
            "performance": {
                "processing_time": processing_time,
                "data_hash": diff_result.data_hash,
                "is_significant_change": diff_result.is_significant_change,
            },
        }

    def _create_error_result(
        self, symbol: str, status: UpdateStatus, error_message: str
    ) -> Dict[str, Any]:
        """エラー結果の作成"""
        return {
            "success": False,
            "status": status.value,
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "error": error_message,
        }

    def _create_backup(self, symbol: str, data: List[Dict[str, Any]]) -> None:
        """バックアップの作成"""
        try:
            backup_dir = self._create_backup_dir(symbol)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"backup_{timestamp}.json"

            with open(backup_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            self.logger.info(f"バックアップ作成: {backup_file}")

        except Exception as e:
            self.logger.warning(f"バックアップ作成失敗: {symbol} - {str(e)}")

    def _create_backup_dir(self, symbol: str) -> Optional[Path]:
        """バックアップディレクトリの作成とパス返却（テスト用に分離）"""
        try:
            backup_dir = self.data_dir / "backups" / symbol
            backup_dir.mkdir(parents=True, exist_ok=True)
            return backup_dir
        except Exception:
            # テストでは例外時にNone返却を期待
            return None

    def _backup_data(self, symbol: str, data: List[Dict[str, Any]]) -> bool:
        """バックアップ実体（テスト用に戻り値boolで成否を返却）"""
        try:
            backup_dir = self._create_backup_dir(symbol)
            if not backup_dir:
                return False
            # テストでディレクトリ未作成が返る場合に備え、ここでも確実に作成
            try:
                backup_dir.mkdir(parents=True, exist_ok=True)
            except Exception:
                pass
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"backup_{timestamp}.json"
            with open(backup_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    def get_update_statistics(self) -> Dict[str, Any]:
        """更新統計の取得"""
        return {
            "total_updates": self.update_stats.total_updates,
            "successful_updates": self.update_stats.successful_updates,
            "failed_updates": self.update_stats.failed_updates,
            "validation_errors": self.update_stats.validation_errors,
            "total_processing_time": self.update_stats.total_processing_time,
            "last_update_time": self.update_stats.last_update_time,
            "success_rate": (
                self.update_stats.successful_updates
                / max(self.update_stats.total_updates, 1)
            ),
            "validation_error_rate": (
                self.update_stats.validation_errors
                / max(self.update_stats.total_updates, 1)
            ),
        }

    def _calculate_comprehensive_diff(
        self, existing_data: List[Dict[str, Any]], new_data: List[Dict[str, Any]]
    ) -> DiffResult:
        """
        包括的差分計算（リファクタリング版）

        Args:
            existing_data: 既存データ
            new_data: 新しいデータ

        Returns:
            DiffResult: 差分結果
        """
        start_time = datetime.now()

        # データのハッシュ計算
        existing_hash = self._calculate_data_hash(existing_data)
        new_hash = self._calculate_data_hash(new_data)

        # 差分計算の実行
        diff_counts = self._calculate_diff_counts(existing_data, new_data)

        # 処理時間の計算
        processing_time = (datetime.now() - start_time).total_seconds()

        # 重要な変更の判定
        is_significant_change = self._is_significant_change(diff_counts)

        return DiffResult(
            added_count=diff_counts["added"],
            updated_count=diff_counts["updated"],
            removed_count=diff_counts["removed"],
            unchanged_count=diff_counts["unchanged"],
            processing_time=processing_time,
            data_hash=new_hash,
            is_significant_change=is_significant_change,
        )

    def _calculate_diff_counts(
        self, existing_data: List[Dict[str, Any]], new_data: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """差分カウントの計算（最適化版）"""
        # データを辞書に変換してO(1)アクセスを実現
        existing_dict = {
            self._get_record_key(record): record for record in existing_data
        }
        new_dict = {self._get_record_key(record): record for record in new_data}

        # キーセットの計算
        existing_keys = set(existing_dict.keys())
        new_keys = set(new_dict.keys())

        # 追加されたレコード
        added_keys = new_keys - existing_keys
        added_count = len(added_keys)

        # 削除されたレコード
        removed_keys = existing_keys - new_keys
        removed_count = len(removed_keys)

        # 更新されたレコードと変更なしレコード
        common_keys = existing_keys & new_keys
        updated_count = 0
        unchanged_count = 0

        for key in common_keys:
            existing_record = existing_dict[key]
            new_record = new_dict[key]
            if self._has_record_changed(existing_record, new_record):
                updated_count += 1
            else:
                unchanged_count += 1

        return {
            "added": added_count,
            "updated": updated_count,
            "removed": removed_count,
            "unchanged": unchanged_count,
        }

    def _is_significant_change(self, diff_counts: Dict[str, int]) -> bool:
        """重要な変更の判定"""
        total_changes = (
            diff_counts["added"] + diff_counts["removed"] + diff_counts["updated"]
        )
        total_records = sum(diff_counts.values())

        if total_records == 0:
            return False

        change_ratio = total_changes / total_records
        # 5%以上の変更を重要とみなす（5%ちょうども含む）
        return change_ratio >= 0.05

    def _calculate_data_hash(self, data: List[Dict[str, Any]]) -> str:
        """データハッシュの計算"""
        data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(data_str.encode("utf-8")).hexdigest()

    def _get_record_key(self, record: Dict[str, Any]) -> str:
        """レコードのキー取得"""
        # 日付と銘柄コードをキーとして使用
        date_key = record.get("Date", record.get("date", ""))
        symbol_key = record.get("Code", record.get("code", ""))
        return f"{symbol_key}_{date_key}"

    def _has_record_changed(
        self, old_record: Dict[str, Any], new_record: Dict[str, Any]
    ) -> bool:
        """レコードの変更判定"""
        # まずハッシュで包括的に比較（テストでモック可能な経路）
        try:
            return self._calculate_hash(old_record) != self._calculate_hash(new_record)
        except Exception:
            # フォールバック: 重要フィールドのみの比較
            important_fields = ["Open", "High", "Low", "Close", "Volume"]
            for field in important_fields:
                if old_record.get(field) != new_record.get(field):
                    return True
            return False

    def _calculate_hash(self, data: Any) -> str:
        """任意データの安定ハッシュ（テストでモック対象）"""
        try:
            data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        except Exception:
            # json化に失敗した場合はreprで代替
            data_str = repr(data)
        return hashlib.md5(data_str.encode("utf-8")).hexdigest()

    def _validate_data_integrity(
        self, new_data: List[Dict[str, Any]], existing_data: List[Dict[str, Any]]
    ) -> ValidationResult:
        """
        データ整合性の検証（リファクタリング版）

        Args:
            new_data: 新しいデータ
            existing_data: 既存データ

        Returns:
            ValidationResult: 検証結果
        """
        issues = []
        warnings = []
        data_quality_score = 1.0

        # データの存在チェック
        if not new_data:
            issues.append("新しいデータが空です")
            return ValidationResult(False, issues, warnings, 0.0)

        # 必須フィールドのチェック（Dateは任意: 提供されていれば妥当性を検証）
        required_fields = ["Open", "High", "Low", "Close", "Volume"]
        for i, record in enumerate(new_data):
            for field in required_fields:
                if field not in record or record[field] is None:
                    issues.append(
                        f"レコード {i}: 必須フィールド '{field}' が不足しています"
                    )

        # データ型のチェック
        for i, record in enumerate(new_data):
            for field in ["Open", "High", "Low", "Close", "Volume"]:
                if field in record:
                    try:
                        float(record[field])
                    except (ValueError, TypeError):
                        issues.append(
                            f"レコード {i}: フィールド '{field}' の値が数値ではありません"
                        )

        # 価格データの妥当性チェック
        for i, record in enumerate(new_data):
            try:
                open_price = float(record.get("Open", 0))
                high_price = float(record.get("High", 0))
                low_price = float(record.get("Low", 0))
                close_price = float(record.get("Close", 0))

                # 価格の妥当性チェック
                # 負の価格チェック
                if any(
                    price < 0
                    for price in [open_price, high_price, low_price, close_price]
                ):
                    issues.append(f"レコード {i}: 負の価格が検出されました")

                if high_price < low_price:
                    issues.append(f"レコード {i}: High価格がLow価格より低いです")

                if high_price < max(open_price, close_price):
                    issues.append(f"レコード {i}: High価格がOpen/Close価格より低いです")

                if low_price > min(open_price, close_price):
                    issues.append(f"レコード {i}: Low価格がOpen/Close価格より高いです")

                # 極端な価格変動のチェック
                if existing_data:
                    prev_record = existing_data[-1] if existing_data else None
                    if prev_record:
                        prev_close = float(prev_record.get("Close", 0))
                        if prev_close > 0:
                            price_change = abs(close_price - prev_close) / prev_close
                            if price_change > 0.5:  # 50%以上の変動
                                warnings.append(
                                    f"レコード {i}: 極端な価格変動が検出されました ({price_change:.2%})"
                                )
                                data_quality_score -= 0.1

            except (ValueError, TypeError) as e:
                issues.append(f"レコード {i}: 価格データの解析エラー - {str(e)}")

        # 日付の妥当性チェック（Dateが提供されている場合のみ）
        for i, record in enumerate(new_data):
            if "Date" in record and record["Date"]:
                date_str = record.get("Date", "")
                try:
                    datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    # テスト期待の文言に合わせる
                    issues.append(f"レコード {i}: 日付の解析エラー - {date_str}")

        # データ品質スコアの計算
        if issues:
            data_quality_score = max(0.0, 1.0 - len(issues) * 0.2)
        elif warnings:
            data_quality_score = max(0.5, 1.0 - len(warnings) * 0.1)

        is_valid = len(issues) == 0

        return ValidationResult(
            is_valid=is_valid,
            issues=issues,
            warnings=warnings,
            data_quality_score=data_quality_score,
        )

    def _normalize_data_for_diff(
        self, data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """差分計算用のデータ正規化"""
        normalized = []

        for item in data:
            # 必須フィールドの確保（大文字・小文字両方に対応）
            normalized_item = {
                "date": str(item.get("Date", item.get("date", ""))),
                "code": str(item.get("Code", item.get("code", ""))),
                "open": (
                    float(item.get("Open", item.get("open", 0)))
                    if item.get("Open", item.get("open")) is not None
                    else 0.0
                ),
                "high": (
                    float(item.get("High", item.get("high", 0)))
                    if item.get("High", item.get("high")) is not None
                    else 0.0
                ),
                "low": (
                    float(item.get("Low", item.get("low", 0)))
                    if item.get("Low", item.get("low")) is not None
                    else 0.0
                ),
                "close": (
                    float(item.get("Close", item.get("close", 0)))
                    if item.get("Close", item.get("close")) is not None
                    else 0.0
                ),
                "volume": (
                    int(item.get("Volume", item.get("volume", 0)))
                    if item.get("Volume", item.get("volume")) is not None
                    else 0
                ),
            }

            # 追加フィールドの保持
            for key, value in item.items():
                if key not in normalized_item:
                    normalized_item[key] = value

            normalized.append(normalized_item)

        # 日付順でソート
        normalized.sort(key=lambda x: x["date"])

        return normalized

    def _items_different(self, item1: Dict[str, Any], item2: Dict[str, Any]) -> bool:
        """2つのアイテムが異なるかチェック"""
        # 重要なフィールドのみを比較（大文字・小文字両方に対応）
        important_fields = [
            "open",
            "high",
            "low",
            "close",
            "volume",
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
        ]

        for field in important_fields:
            if item1.get(field) != item2.get(field):
                return True

        return False

    def _identify_changes(
        self, old_item: Dict[str, Any], new_item: Dict[str, Any]
    ) -> List[str]:
        """変更されたフィールドの特定"""
        changes = []

        # 大文字・小文字両方のフィールドをチェック
        field_mappings = [
            ("open", "Open"),
            ("high", "High"),
            ("low", "Low"),
            ("close", "Close"),
            ("volume", "Volume"),
        ]

        for lower_key, upper_key in field_mappings:
            old_val = old_item.get(lower_key) or old_item.get(upper_key)
            new_val = new_item.get(lower_key) or new_item.get(upper_key)
            if old_val != new_val:
                changes.append(f"{lower_key}: {old_val} -> {new_val}")

        return changes

    def batch_update(self, updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        バッチ差分更新

        Args:
            updates: 更新データのリスト [{'symbol': str, 'data': List[Dict], 'source': str}]

        Returns:
            Dict[str, Any]: バッチ更新結果
        """
        try:
            self.logger.info(f"バッチ差分更新開始: {len(updates)}件")

            results = []
            success_count = 0
            error_count = 0

            for update in updates:
                symbol = update.get("symbol")
                data = update.get("data", [])
                source = update.get("source", "jquants_api")

                if not symbol or not data:
                    error_count += 1
                    results.append(
                        {
                            "symbol": symbol,
                            "success": False,
                            "error": "必須パラメータが不足",
                        }
                    )
                    continue

                # 個別更新の実行
                result = self.update_stock_data(symbol, data, source)
                results.append(result)

                if result["success"]:
                    success_count += 1
                else:
                    error_count += 1

            batch_result = {
                "success": error_count == 0,
                "total_updates": len(updates),
                "success_count": success_count,
                "error_count": error_count,
                "results": results,
                "timestamp": datetime.now().isoformat(),
            }

            self.logger.info(
                f"バッチ差分更新完了: 成功{success_count}件, エラー{error_count}件"
            )

            return batch_result

        except Exception as e:
            self.logger.error(f"バッチ差分更新エラー: {e}")
            return {
                "success": False,
                "error": str(e),
                "total_updates": len(updates),
                "success_count": 0,
                "error_count": len(updates),
            }

    def get_update_history(
        self, symbol: Optional[str] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        更新履歴の取得

        Args:
            symbol: 銘柄コード（指定時は該当銘柄のみ）
            limit: 取得件数制限

        Returns:
            List[Dict[str, Any]]: 更新履歴
        """
        try:
            diff_log = self.json_manager.get_diff_log(symbol, limit)

            # 履歴の整形
            history = []
            for entry in diff_log:
                history.append(
                    {
                        "timestamp": entry["timestamp"],
                        "symbol": entry["symbol"],
                        "summary": {
                            "added": entry["diff"]["added_count"],
                            "updated": entry["diff"]["updated_count"],
                            "removed": entry["diff"]["removed_count"],
                        },
                        "details": entry["diff"],
                    }
                )

            return history

        except Exception as e:
            self.logger.error(f"更新履歴取得エラー: {e}")
            return []

    def optimize_data_structure(self, symbol: str) -> Dict[str, Any]:
        """
        データ構造の最適化

        Args:
            symbol: 銘柄コード

        Returns:
            Dict[str, Any]: 最適化結果
        """
        try:
            self.logger.info(f"データ構造最適化開始: {symbol}")

            # 現在のデータを取得
            data = self.json_manager.get_stock_data(symbol)

            if not data:
                return {"success": False, "error": "データが見つかりません"}

            # 重複データの除去
            unique_data = self._remove_duplicates(data)

            # データのソート
            sorted_data = sorted(unique_data, key=lambda x: x["date"])

            # 最適化されたデータの保存
            save_success = self.json_manager.save_stock_data(
                symbol, sorted_data, "optimization"
            )

            if save_success:
                result = {
                    "success": True,
                    "original_count": len(data),
                    "optimized_count": len(sorted_data),
                    "removed_duplicates": len(data) - len(sorted_data),
                    "timestamp": datetime.now().isoformat(),
                }

                self.logger.info(
                    f"データ構造最適化完了: {symbol} - "
                    f"元:{len(data)}件 -> 最適化後:{len(sorted_data)}件"
                )

                return result
            else:
                return {"success": False, "error": "最適化データの保存に失敗"}

        except Exception as e:
            self.logger.error(f"データ構造最適化エラー {symbol}: {e}")
            return {"success": False, "error": str(e)}

    def _remove_duplicates(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """重複データの除去"""
        seen = set()
        unique_data = []

        for item in data:
            # 日付をキーとして重複チェック
            date_key = item.get("date")
            if date_key and date_key not in seen:
                seen.add(date_key)
                unique_data.append(item)

        return unique_data

    def get_update_statistics_from_logs(self) -> Dict[str, Any]:
        """更新統計の取得（ログ由来の集計版）"""
        try:
            metadata = self.json_manager.get_metadata()
            diff_log = self.json_manager.get_diff_log()

            total_updates = len(diff_log)
            symbols_updated = len(set(entry["symbol"] for entry in diff_log))

            recent_updates = [
                entry
                for entry in diff_log
                if datetime.fromisoformat(entry["timestamp"]) > datetime.now() - timedelta(days=7)
            ]

            recent_count = len(recent_updates)

            symbol_stats = {}
            for entry in diff_log:
                symbol = entry["symbol"]
                if symbol not in symbol_stats:
                    symbol_stats[symbol] = {
                        "update_count": 0,
                        "total_added": 0,
                        "total_updated": 0,
                        "total_removed": 0,
                        "last_update": None,
                    }

                symbol_stats[symbol]["update_count"] += 1
                symbol_stats[symbol]["total_added"] += entry["diff"]["added_count"]
                symbol_stats[symbol]["total_updated"] += entry["diff"]["updated_count"]
                symbol_stats[symbol]["total_removed"] += entry["diff"]["removed_count"]

                if (
                    not symbol_stats[symbol]["last_update"]
                    or entry["timestamp"] > symbol_stats[symbol]["last_update"]
                ):
                    symbol_stats[symbol]["last_update"] = entry["timestamp"]

            return {
                "total_updates": total_updates,
                "symbols_updated": symbols_updated,
                "recent_updates_7days": recent_count,
                "symbol_statistics": symbol_stats,
                "last_updated": metadata.get("last_updated"),
                "data_sources": metadata.get("data_sources", {}),
            }

        except Exception as e:
            self.logger.error(f"更新統計取得エラー: {e}")
            return {}


# 使用例
if __name__ == "__main__":
    # ログ設定
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # DifferentialUpdaterの初期化
    updater = DifferentialUpdater("data", logger)

    # サンプルデータの準備
    existing_data = [
        {
            "date": "2024-01-01",
            "code": "7203",
            "open": 100.0,
            "high": 105.0,
            "low": 98.0,
            "close": 103.0,
            "volume": 1000000,
        }
    ]

    new_data = [
        {
            "date": "2024-01-01",
            "code": "7203",
            "open": 100.0,
            "high": 105.0,
            "low": 98.0,
            "close": 103.0,
            "volume": 1000000,
        },
        {
            "date": "2024-01-02",
            "code": "7203",
            "open": 103.0,
            "high": 108.0,
            "low": 101.0,
            "close": 106.0,
            "volume": 1200000,
        },
    ]

    # 差分更新の実行
    result = updater.update_stock_data("7203", new_data, "jquants_api")
    print(f"差分更新結果: {result}")

    # 統計情報の取得
    stats = updater.get_update_statistics()
    print(f"更新統計: {stats}")
