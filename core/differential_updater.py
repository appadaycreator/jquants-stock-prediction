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
class ValidationResult:
    """検証結果クラス"""

    is_valid: bool
    issues: List[str]
    warnings: List[str] = None
    data_quality_score: float = 1.0

    def __post_init__(self):
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
    data_sources: Dict[str, int] = None

    def __post_init__(self):
        if self.data_sources is None:
            self.data_sources = {}

    def increment_total_updates(self):
        """総更新数を増加"""
        self.total_updates += 1

    def increment_successful_updates(self):
        """成功更新数を増加"""
        self.successful_updates += 1

    def increment_failed_updates(self):
        """失敗更新数を増加"""
        self.failed_updates += 1

    def increment_validation_errors(self):
        """検証エラー数を増加"""
        self.validation_errors += 1

    def add_processing_time(self, time: float):
        """処理時間を追加"""
        self.total_processing_time += time

    def set_last_update_time(self, time):
        """最終更新時間を設定"""
        if hasattr(time, "isoformat"):
            self.last_update_time = time.isoformat()
        else:
            self.last_update_time = str(time)


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
    data_hash: str = ""
    is_significant_change: bool = False
    symbol: str = ""
    status: str = ""
    changes_count: int = 0


class DataHashCalculator:
    """データハッシュ計算クラス"""

    @staticmethod
    def calculate_data_hash(data: List[Dict[str, Any]]) -> str:
        """データのハッシュ値を計算"""
        try:
            # データを正規化してハッシュ計算
            normalized_data = DataHashCalculator._normalize_data(data)
            data_str = json.dumps(normalized_data, sort_keys=True, ensure_ascii=False)
            return hashlib.sha256(data_str.encode("utf-8")).hexdigest()
        except Exception:
            return ""

    @staticmethod
    def _normalize_data(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """データの正規化"""
        normalized = []
        for item in data:
            normalized_item = {}
            for key, value in item.items():
                if isinstance(value, (int, float)):
                    normalized_item[key] = round(value, 6)
                else:
                    normalized_item[key] = value
            normalized.append(normalized_item)
        return normalized


class DiffCalculator:
    """差分計算クラス（メモリ最適化版）"""

    def __init__(self, logger=None, max_cache_size=100):
        self.logger = logger
        self._diff_cache = {}
        self.max_cache_size = max_cache_size
        self._cache_access_count = {}

    def calculate_comprehensive_diff(
        self, existing_data: List[Dict[str, Any]], new_data: List[Dict[str, Any]]
    ) -> DiffResult:
        """包括的差分計算"""
        start_time = datetime.now()

        # データのハッシュ計算
        existing_hash = DataHashCalculator.calculate_data_hash(existing_data)
        new_hash = DataHashCalculator.calculate_data_hash(new_data)

        # キャッシュヒットなら即返却（メモリ最適化版）
        cache_key = (existing_hash, new_hash)
        cached = self._diff_cache.get(cache_key)
        if cached:
            # アクセス回数を更新
            self._cache_access_count[cache_key] = self._cache_access_count.get(cache_key, 0) + 1
            return cached

        # 差分計算の実行
        diff_counts = self._calculate_diff_counts(existing_data, new_data)

        # 処理時間の計算
        processing_time = (datetime.now() - start_time).total_seconds()

        # 重要な変更の判定
        is_significant_change = self._is_significant_change(diff_counts)

        result = DiffResult(
            added_count=diff_counts["added"],
            updated_count=diff_counts["updated"],
            removed_count=diff_counts["removed"],
            unchanged_count=diff_counts["unchanged"],
            processing_time=processing_time,
            data_hash=new_hash,
            is_significant_change=is_significant_change,
        )

        # キャッシュ保存（メモリ最適化版）
        self._diff_cache[cache_key] = result
        self._cache_access_count[cache_key] = 1
        
        # キャッシュサイズ制限の適用
        self._enforce_cache_limit()
        
        return result

    def _calculate_diff_counts(
        self, existing_data: List[Dict[str, Any]], new_data: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """差分カウントの計算"""
        try:
            # データ構造の正規化（date vs Date）
            def normalize_item(item):
                normalized = {}
                for key, value in item.items():
                    if key.lower() == "date":
                        normalized["date"] = value
                    else:
                        normalized[key.lower()] = value
                return normalized

            existing_normalized = [normalize_item(item) for item in existing_data]
            new_normalized = [normalize_item(item) for item in new_data]

            existing_dict = {item.get("date", ""): item for item in existing_normalized}
            new_dict = {item.get("date", ""): item for item in new_normalized}

            added = 0
            updated = 0
            removed = 0
            unchanged = 0

            # 新規追加と更新の判定
            for date, new_item in new_dict.items():
                if date not in existing_dict:
                    added += 1
                elif self._has_changes(existing_dict[date], new_item):
                    updated += 1
                else:
                    unchanged += 1

            # 削除の判定
            for date in existing_dict:
                if date not in new_dict:
                    removed += 1

            return {
                "added": added,
                "updated": updated,
                "removed": removed,
                "unchanged": unchanged,
            }
        except Exception as e:
            if self.logger:
                self.logger.error(f"差分カウント計算エラー: {e}")
            return {"added": 0, "updated": 0, "removed": 0, "unchanged": 0}

    def _has_changes(self, existing: Dict[str, Any], new: Dict[str, Any]) -> bool:
        """変更の有無を判定"""
        for key in existing:
            if key in new and existing[key] != new[key]:
                return True
        return False

    def _is_significant_change(self, diff_counts: Dict[str, int]) -> bool:
        """重要な変更の判定"""
        total_changes = (
            diff_counts["added"] + diff_counts["updated"] + diff_counts["removed"]
        )
        return total_changes > 0

    def _enforce_cache_limit(self):
        """キャッシュサイズ制限の適用（LRU方式）"""
        if len(self._diff_cache) <= self.max_cache_size:
            return
            
        # アクセス回数が少ないエントリを削除
        sorted_items = sorted(
            self._cache_access_count.items(),
            key=lambda x: x[1]
        )
        
        # 古いエントリの半分を削除
        items_to_remove = len(self._diff_cache) - self.max_cache_size
        for cache_key, _ in sorted_items[:items_to_remove]:
            if cache_key in self._diff_cache:
                del self._diff_cache[cache_key]
            if cache_key in self._cache_access_count:
                del self._cache_access_count[cache_key]
                
        if self.logger:
            self.logger.info(f"キャッシュサイズ制限適用: {len(self._diff_cache)}/{self.max_cache_size}")

    def clear_cache(self):
        """キャッシュのクリア"""
        self._diff_cache.clear()
        self._cache_access_count.clear()
        if self.logger:
            self.logger.info("差分計算キャッシュをクリアしました")


class DataValidator:
    """データ検証クラス"""

    def __init__(self, logger=None):
        self.logger = logger

    def validate_update_data(
        self, data: List[Dict[str, Any]], symbol: str
    ) -> Dict[str, Any]:
        """更新データの検証"""
        try:
            if not data:
                return {"is_valid": False, "issues": ["データが空です"]}

            issues = []
            warnings = []

            # 必須フィールドのチェック
            issues.extend(self._validate_required_fields(data))

            # 日付形式のチェック
            issues.extend(self._validate_date_format(data))

            # 数値フィールドのチェック
            warnings.extend(self._validate_numeric_fields(data))

            return {
                "is_valid": len(issues) == 0,
                "issues": issues,
                "warnings": warnings,
                "validated_count": len(data),
            }

        except Exception as e:
            if self.logger:
                self.logger.error(f"データ検証エラー: {e}")
            return {"is_valid": False, "issues": [str(e)]}

    def _validate_required_fields(self, data: List[Dict[str, Any]]) -> List[str]:
        """必須フィールドの検証"""
        issues = []
        required_fields = ["date", "code"]
        for item in data:
            for field in required_fields:
                if field not in item or not item[field]:
                    issues.append(f"必須フィールド '{field}' が不足: {item}")
        return issues

    def _validate_date_format(self, data: List[Dict[str, Any]]) -> List[str]:
        """日付形式の検証"""
        issues = []
        for item in data:
            try:
                datetime.fromisoformat(item["date"])
            except (ValueError, TypeError):
                issues.append(f"無効な日付形式: {item['date']}")
        return issues

    def _validate_numeric_fields(self, data: List[Dict[str, Any]]) -> List[str]:
        """数値フィールドの検証"""
        warnings = []
        numeric_fields = ["open", "high", "low", "close", "volume"]
        for item in data:
            for field in numeric_fields:
                if field in item:
                    try:
                        float(item[field])
                    except (ValueError, TypeError):
                        warnings.append(f"数値フィールド '{field}' が無効: {item[field]}")
        return warnings


class DifferentialUpdater:
    """差分更新システム（リファクタリング版）"""

    def __init__(self, data_dir: str, logger=None, error_handler=None):
        """初期化（メモリ最適化版）"""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logger or logging.getLogger(__name__)
        self.error_handler = error_handler
        self.json_manager = JSONDataManager(str(self.data_dir), self.logger)
        self.config = UpdateConfig()

        # コンポーネントの初期化（メモリ制限付き）
        self.hash_calculator = DataHashCalculator()
        self.diff_calculator = DiffCalculator(self.logger, max_cache_size=50)  # キャッシュサイズ制限
        self.validator = DataValidator(self.logger)

        # 統計情報の初期化
        self.update_stats = UpdateStats()
        
        # メモリ最適化設定
        self.memory_optimization_enabled = True
        self.max_memory_usage_mb = 200  # 最大メモリ使用量

    def update_stock_data(
        self, symbol: str, new_data: List[Dict[str, Any]], source: str = "api"
    ) -> Dict[str, Any]:
        """株価データの差分更新"""
        try:
            # データ検証
            validation_result = self._validate_data_integrity(new_data, [])
            if not validation_result.is_valid:
                return {
                    "success": False,
                    "status": UpdateStatus.VALIDATION_ERROR.value,
                    "symbol": symbol,
                    "error": f"データ検証失敗: {validation_result.issues}",
                    "timestamp": datetime.now().isoformat(),
                }

            # 既存データの取得
            existing_data = self.json_manager.get_stock_data(symbol)
            if not existing_data:
                existing_data = []

            # 差分計算
            diff_result = self.diff_calculator.calculate_comprehensive_diff(
                existing_data, new_data
            )

            # データの更新
            if diff_result.is_significant_change:
                success = self.json_manager.save_stock_data(symbol, new_data, source)
                if success:
                    # 差分ログの記録
                    self._log_diff_update(symbol, diff_result, source)

                    return {
                        "success": True,
                        "status": UpdateStatus.SUCCESS.value,
                        "symbol": symbol,
                        "diff": {
                            "added": diff_result.added_count,
                            "updated": diff_result.updated_count,
                            "removed": diff_result.removed_count,
                            "unchanged": diff_result.unchanged_count,
                        },
                        "processing_time": diff_result.processing_time,
                        "data_hash": diff_result.data_hash,
                        "timestamp": datetime.now().isoformat(),
                    }
                else:
                    return {
                        "success": False,
                        "status": UpdateStatus.FAILED.value,
                        "symbol": symbol,
                        "error": "データ保存に失敗",
                        "timestamp": datetime.now().isoformat(),
                    }
            else:
                return {
                    "success": True,
                    "status": UpdateStatus.SUCCESS.value,
                    "symbol": symbol,
                    "diff": {"added": 0, "updated": 0, "removed": 0, "unchanged": 0},
                    "message": "変更なし",
                    "timestamp": datetime.now().isoformat(),
                }

        except Exception as e:
            if self.logger:
                self.logger.error(f"差分更新エラー {symbol}: {e}")
            return {
                "success": False,
                "status": UpdateStatus.FAILED.value,
                "symbol": symbol,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def _log_diff_update(
        self, symbol: str, diff_result: DiffResult, source: str
    ) -> None:
        """差分更新ログの記録"""
        try:
            log_entry = {
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "source": source,
                "diff": {
                    "added_count": diff_result.added_count,
                    "updated_count": diff_result.updated_count,
                    "removed_count": diff_result.removed_count,
                    "unchanged_count": diff_result.unchanged_count,
                },
                "processing_time": diff_result.processing_time,
                "data_hash": diff_result.data_hash,
            }

            # 差分ログの保存
            self.json_manager.add_diff_log_entry(log_entry)

        except Exception as e:
            if self.logger:
                self.logger.warning(f"差分ログ記録エラー: {e}")

    def get_update_statistics(self) -> Dict[str, Any]:
        """更新統計の取得"""
        try:
            metadata = self.json_manager.get_metadata()
            diff_log = self.json_manager.get_diff_log()

            total_updates = len(diff_log)
            symbols_updated = len(set(entry["symbol"] for entry in diff_log))

            recent_updates = [
                entry
                for entry in diff_log
                if datetime.fromisoformat(entry["timestamp"])
                > datetime.now() - timedelta(days=7)
            ]

            recent_count = len(recent_updates)

            return {
                "total_updates": total_updates,
                "symbols_updated": symbols_updated,
                "recent_updates_7days": recent_count,
                "last_updated": metadata.get("last_updated"),
            }

        except Exception as e:
            if self.logger:
                self.logger.error(f"更新統計取得エラー: {e}")
            return {}

    def optimize_data_structure(self, symbol: str) -> Dict[str, Any]:
        """データ構造の最適化"""
        try:
            # データの取得
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

                if self.logger:
                    self.logger.info(
                        f"データ構造最適化完了: {symbol} - "
                        f"元:{len(data)}件 -> 最適化後:{len(sorted_data)}件"
                    )

                return result
            else:
                return {"success": False, "error": "最適化データの保存に失敗"}

        except Exception as e:
            if self.logger:
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

    def _normalize_data_for_diff(
        self, data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """差分用データ正規化"""
        try:
            if not data:
                return []

            normalized = []
            for item in data:
                normalized_item = {}
                for key, value in item.items():
                    # 数値フィールドの正規化
                    if key.lower() in ["open", "high", "low", "close", "volume"]:
                        try:
                            normalized_item[key.lower()] = float(value)
                        except (ValueError, TypeError):
                            normalized_item[key.lower()] = 0.0
                    else:
                        normalized_item[key.lower()] = value

                # 不足しているフィールドをデフォルト値で補完
                required_fields = ["open", "high", "low", "close", "volume"]
                for field in required_fields:
                    if field not in normalized_item:
                        normalized_item[field] = 0.0

                normalized.append(normalized_item)
            return normalized
        except Exception as e:
            if self.logger:
                self.logger.error(f"データ正規化エラー: {e}")
            return data

    def _items_different(self, item1: Dict[str, Any], item2: Dict[str, Any]) -> bool:
        """アイテム差分判定"""
        try:
            # 主要フィールドの比較（大文字小文字を考慮）
            key_fields = ["date", "code", "open", "high", "low", "close", "volume"]
            for field in key_fields:
                # 大文字小文字を考慮してフィールドを検索
                field_variants = [field, field.capitalize(), field.upper()]
                for variant in field_variants:
                    if variant in item1 and variant in item2:
                        if item1[variant] != item2[variant]:
                            return True
                        break
                    elif variant in item1 or variant in item2:
                        return True
            return False
        except Exception:
            return True

    def _identify_changes(
        self, old_item: Dict[str, Any], new_item: Dict[str, Any]
    ) -> List[str]:
        """変更識別"""
        try:
            changes = []
            # 大文字小文字を考慮してフィールドを比較
            for key in old_item:
                # 大文字小文字のバリエーションをチェック
                key_variants = [key, key.lower(), key.capitalize(), key.upper()]
                for variant in key_variants:
                    if variant in new_item and old_item[key] != new_item[variant]:
                        changes.append(
                            f"{key.lower()}: {old_item[key]} -> {new_item[variant]}"
                        )
                        break
            return changes
        except Exception:
            return []

    def _validate_data_integrity(
        self, new_data: List[Dict[str, Any]], existing_data: List[Dict[str, Any]]
    ) -> ValidationResult:
        """データ整合性検証"""
        try:
            issues = []
            warnings = []

            # 基本検証
            if not new_data:
                issues.append("データが空です")
                return ValidationResult(is_valid=False, issues=issues)

            # 各データアイテムの検証
            for i, item in enumerate(new_data):
                try:
                    # 必須フィールドのチェック
                    required_fields = [
                        "date",
                        "code",
                        "open",
                        "high",
                        "low",
                        "close",
                        "volume",
                    ]
                    missing_fields = []
                    for field in required_fields:
                        # 大文字小文字を考慮
                        field_variants = [field, field.capitalize(), field.upper()]
                        found = False
                        for variant in field_variants:
                            if variant in item:
                                found = True
                                break
                        if not found:
                            missing_fields.append(field)

                    if missing_fields:
                        issues.append(f"アイテム{i}: 必須フィールドが不足: {missing_fields}")
                        continue

                    # 日付の検証
                    date_value = None
                    for key, value in item.items():
                        if key.lower() == "date":
                            date_value = value
                            break

                    if date_value:
                        try:
                            from datetime import datetime

                            datetime.fromisoformat(str(date_value))
                        except (ValueError, TypeError):
                            issues.append(f"アイテム{i}: 日付の解析エラー")

                    # 価格データの検証
                    # 大文字小文字を考慮して価格データを取得
                    open_price = None
                    high_price = None
                    low_price = None
                    close_price = None
                    volume = None

                    for key, value in item.items():
                        if key.lower() == "open":
                            open_price = float(value)
                        elif key.lower() == "high":
                            high_price = float(value)
                        elif key.lower() == "low":
                            low_price = float(value)
                        elif key.lower() == "close":
                            close_price = float(value)
                        elif key.lower() == "volume":
                            volume = float(value)

                    if (
                        open_price is not None
                        and high_price is not None
                        and low_price is not None
                        and close_price is not None
                    ):
                        # 負の価格チェック
                        if any(
                            price < 0
                            for price in [
                                open_price,
                                high_price,
                                low_price,
                                close_price,
                            ]
                        ):
                            issues.append(f"アイテム{i}: 負の価格が検出されました")

                        # 高値・安値の整合性
                        if high_price < low_price:
                            issues.append(f"アイテム{i}: High価格がLow価格より低い")
                        if high_price < max(open_price, close_price):
                            issues.append(f"アイテム{i}: High価格がOpen/Close価格より低い")
                        if low_price > min(open_price, close_price):
                            issues.append(f"アイテム{i}: Low価格がOpen/Close価格より高い")

                        # 極端な価格変動のチェック
                        if existing_data:
                            for existing_item in existing_data:
                                if existing_item.get("date") == item.get(
                                    "date"
                                ) or existing_item.get("Date") == item.get("date"):
                                    try:
                                        existing_close = None
                                        for key, value in existing_item.items():
                                            if key.lower() == "close":
                                                existing_close = float(value)
                                                break

                                        if existing_close is not None:
                                            price_change = (
                                                abs(close_price - existing_close)
                                                / existing_close
                                            )
                                            if price_change > 0.5:  # 50%以上の変動
                                                warnings.append(
                                                    f"アイテム{i}: 極端な価格変動が検出されました ({price_change:.2%})"
                                                )
                                    except (ValueError, TypeError):
                                        pass
                                    break

                    # ボリュームの検証
                    if volume is not None:
                        try:
                            volume_float = float(volume)
                            if volume_float < 0:
                                issues.append(f"アイテム{i}: Volumeが負の値です")
                        except (ValueError, TypeError):
                            issues.append(f"アイテム{i}: Volumeの解析エラー")

                except (ValueError, TypeError) as e:
                    issues.append(f"アイテム{i}: 価格データの解析エラー")
                except Exception as e:
                    issues.append(f"アイテム{i}: 検証エラー: {e}")

            return ValidationResult(
                is_valid=len(issues) == 0, issues=issues, warnings=warnings
            )
        except Exception as e:
            return ValidationResult(is_valid=False, issues=[str(e)])

    def _calculate_comprehensive_diff(
        self, existing_data: List[Dict[str, Any]], new_data: List[Dict[str, Any]]
    ) -> DiffResult:
        """包括的差分計算"""
        return self.diff_calculator.calculate_comprehensive_diff(
            existing_data, new_data
        )

    def _calculate_diff_counts(
        self, old_data: List[Dict[str, Any]], new_data: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """差分カウント計算"""
        return self.diff_calculator._calculate_diff_counts(old_data, new_data)

    def _calculate_data_hash(self, data: List[Dict[str, Any]]) -> str:
        """データハッシュ計算"""
        if data is None:
            return ""
        return self.hash_calculator.calculate_data_hash(data)

    def _calculate_hash(self, data: Dict[str, Any]) -> str:
        """ハッシュ計算"""
        try:
            data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
            return hashlib.sha256(data_str.encode("utf-8")).hexdigest()
        except Exception:
            return ""

    def _has_record_changed(
        self, old_record: Dict[str, Any], new_record: Dict[str, Any]
    ) -> bool:
        """レコード変更判定"""
        try:
            return self._items_different(old_record, new_record)
        except Exception:
            return True

    def _is_significant_change(self, diff_counts: Dict[str, int]) -> bool:
        """重要な変更判定"""
        total_changes = (
            diff_counts.get("added", 0)
            + diff_counts.get("updated", 0)
            + diff_counts.get("removed", 0)
        )
        return total_changes > 0

    def _get_record_key(self, record: Dict[str, Any]) -> str:
        """レコードキー取得"""
        try:
            date = record.get("date", "")
            code = record.get("code", "")
            return f"{code}_{date}"
        except Exception:
            return ""

    def _has_record_changed(
        self, old_record: Dict[str, Any], new_record: Dict[str, Any]
    ) -> bool:
        """レコード変更判定"""
        try:
            return self._items_different(old_record, new_record)
        except Exception:
            return True

    def _backup_data(self, symbol: str, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """データバックアップ"""
        try:
            backup_dir = self._create_backup_dir(symbol)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"backup_{timestamp}.json"

            with open(backup_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            return {"success": True, "backup_file": str(backup_file)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _create_backup_dir(self, symbol: str) -> Path:
        """バックアップディレクトリ作成"""
        backup_dir = self.data_dir / "backups" / symbol
        backup_dir.mkdir(parents=True, exist_ok=True)
        return backup_dir

    def _create_success_result(
        self,
        symbol: str,
        diff_result: DiffResult,
        processing_time: float,
        retry_count: int,
    ) -> Dict[str, Any]:
        """成功結果作成"""
        return {
            "success": True,
            "status": UpdateStatus.SUCCESS.value,
            "symbol": symbol,
            "diff": {
                "added": diff_result.added_count,
                "updated": diff_result.updated_count,
                "removed": diff_result.removed_count,
                "unchanged": diff_result.unchanged_count,
            },
            "processing_time": processing_time,
            "retry_count": retry_count,
            "data_hash": diff_result.data_hash,
        }

    def _create_error_result(
        self, status: Union[UpdateStatus, str], symbol: str, error_message: str
    ) -> Dict[str, Any]:
        """エラー結果作成"""
        status_value = status.value if hasattr(status, "value") else str(status)
        return {
            "success": False,
            "status": status_value,
            "symbol": symbol,
            "error": error_message,
            "timestamp": datetime.now().isoformat(),
        }

    def batch_update(self, updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """バッチ更新"""
        try:
            results = []
            successful = 0
            failed = 0

            for update in updates:
                symbol = update.get("symbol")
                data = update.get("data", [])
                source = update.get("source", "batch")

                result = self.update_stock_data(symbol, data, source)
                results.append(result)

                if result.get("success") is True:
                    successful += 1
                else:
                    failed += 1

            return {
                "success": failed == 0,
                "status": "completed",
                "total": len(updates),
                "successful": successful,
                "failed": failed,
                "success_count": successful,
                "error_count": failed,
                "results": results,
            }
        except Exception as e:
            if self.logger:
                self.logger.error(f"バッチ更新エラー: {e}")
            return {"success": False, "status": "error", "error": str(e)}

    def get_update_history(
        self, symbol: str = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """更新履歴取得"""
        try:
            diff_log = self.json_manager.get_diff_log()

            if symbol:
                filtered_log = [
                    entry for entry in diff_log if entry.get("symbol") == symbol
                ]
            else:
                filtered_log = diff_log

            # 最新順にソート
            filtered_log.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

            return filtered_log[:limit]
        except Exception as e:
            if self.logger:
                self.logger.error(f"更新履歴取得エラー: {e}")
            return []

    def get_update_statistics(self) -> Dict[str, Any]:
        """更新統計取得"""
        try:
            success_rate = 0.0
            if self.update_stats.total_updates > 0:
                success_rate = (
                    self.update_stats.successful_updates
                    / self.update_stats.total_updates
                )

            validation_error_rate = 0.0
            if self.update_stats.total_updates > 0:
                validation_error_rate = (
                    self.update_stats.validation_errors
                    / self.update_stats.total_updates
                )

            return {
                "total_updates": self.update_stats.total_updates,
                "successful_updates": self.update_stats.successful_updates,
                "failed_updates": self.update_stats.failed_updates,
                "validation_errors": self.update_stats.validation_errors,
                "total_processing_time": self.update_stats.total_processing_time,
                "last_update_time": self.update_stats.last_update_time,
                "last_updated": self.update_stats.last_update_time,
                "data_sources": self.update_stats.data_sources,
                "success_rate": success_rate,
                "validation_error_rate": validation_error_rate,
                "symbols_updated": len(self.update_stats.data_sources),
            }
        except Exception as e:
            if self.logger:
                self.logger.error(f"更新統計取得エラー: {e}")
            return {}

    def optimize_data_structure(self, symbol: str) -> Dict[str, Any]:
        """データ構造最適化"""
        try:
            # データの取得
            data = self.json_manager.get_stock_data(symbol)
            if not data:
                return {"success": False, "message": "データが見つかりません"}

            # 重複削除
            optimized_data = self._remove_duplicates(data)

            # データの保存
            success = self.json_manager.save_stock_data(
                symbol, optimized_data, "optimization"
            )

            if success:
                return {
                    "success": True,
                    "message": "最適化完了",
                    "original_count": len(data),
                    "optimized_count": len(optimized_data),
                    "removed_duplicates": len(data) - len(optimized_data),
                }
            else:
                return {"success": False, "error": "最適化データの保存に失敗"}
        except Exception as e:
            if self.logger:
                self.logger.error(f"データ構造最適化エラー: {e}")
            return {"success": False, "error": str(e)}

    def _create_backup_dir(self, symbol: str) -> Path:
        """バックアップディレクトリ作成"""
        try:
            backup_dir = self.data_dir / "backups" / symbol
            backup_dir.mkdir(parents=True, exist_ok=True)
            return backup_dir
        except Exception as e:
            if self.logger:
                self.logger.error(f"バックアップディレクトリ作成エラー: {e}")
            raise

    def _create_backup(self, symbol: str, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """データバックアップ作成"""
        try:
            backup_dir = self._create_backup_dir(symbol)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"backup_{timestamp}.json"

            with open(backup_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            return {
                "success": True,
                "backup_file": str(backup_file),
                "timestamp": timestamp,
            }
        except Exception as e:
            if self.logger:
                self.logger.error(f"バックアップ作成エラー: {e}")
            return {"success": False, "error": str(e)}

    def _backup_data(self, symbol: str, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """データバックアップ（エイリアス）"""
        return self._create_backup(symbol, data)

    def optimize_memory_usage(self):
        """メモリ使用量の最適化"""
        try:
            if not self.memory_optimization_enabled:
                return
                
            # キャッシュのクリア
            self.diff_calculator.clear_cache()
            
            # ガベージコレクションの実行
            import gc
            collected = gc.collect()
            
            if self.logger:
                self.logger.info(f"メモリ最適化完了: {collected}個のオブジェクトを回収")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"メモリ最適化エラー: {e}")

    def get_memory_usage(self) -> Dict[str, Any]:
        """メモリ使用量の取得"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                "rss_mb": memory_info.rss / 1024 / 1024,
                "vms_mb": memory_info.vms / 1024 / 1024,
                "cache_size": len(self.diff_calculator._diff_cache),
                "max_cache_size": self.diff_calculator.max_cache_size
            }
        except Exception as e:
            if self.logger:
                self.logger.error(f"メモリ使用量取得エラー: {e}")
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
