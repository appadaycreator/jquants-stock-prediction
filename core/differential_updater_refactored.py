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
    data_hash: str = ""
    is_significant_change: bool = False


class DataHashCalculator:
    """データハッシュ計算クラス"""

    @staticmethod
    def calculate_data_hash(data: List[Dict[str, Any]]) -> str:
        """データのハッシュ値を計算"""
        try:
            # データを正規化してハッシュ計算
            normalized_data = DataHashCalculator._normalize_data(data)
            data_str = json.dumps(normalized_data, sort_keys=True, ensure_ascii=False)
            return hashlib.md5(data_str.encode('utf-8')).hexdigest()
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
    """差分計算クラス"""

    def __init__(self, logger=None):
        self.logger = logger
        self._diff_cache = {}

    def calculate_comprehensive_diff(
        self, existing_data: List[Dict[str, Any]], new_data: List[Dict[str, Any]]
    ) -> DiffResult:
        """包括的差分計算"""
        start_time = datetime.now()

        # データのハッシュ計算
        existing_hash = DataHashCalculator.calculate_data_hash(existing_data)
        new_hash = DataHashCalculator.calculate_data_hash(new_data)

        # キャッシュヒットなら即返却
        cache_key = (existing_hash, new_hash)
        cached = self._diff_cache.get(cache_key)
        if cached:
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
        
        # キャッシュ保存
        self._diff_cache[cache_key] = result
        return result

    def _calculate_diff_counts(
        self, existing_data: List[Dict[str, Any]], new_data: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """差分カウントの計算"""
        existing_dict = {item["date"]: item for item in existing_data}
        new_dict = {item["date"]: item for item in new_data}

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

    def _has_changes(self, existing: Dict[str, Any], new: Dict[str, Any]) -> bool:
        """変更の有無を判定"""
        for key in existing:
            if key in new and existing[key] != new[key]:
                return True
        return False

    def _is_significant_change(self, diff_counts: Dict[str, int]) -> bool:
        """重要な変更の判定"""
        total_changes = diff_counts["added"] + diff_counts["updated"] + diff_counts["removed"]
        return total_changes > 0


class DataValidator:
    """データ検証クラス"""

    def __init__(self, logger=None):
        self.logger = logger

    def validate_update_data(self, data: List[Dict[str, Any]], symbol: str) -> Dict[str, Any]:
        """更新データの検証"""
        try:
            if not data:
                return {"is_valid": False, "issues": ["データが空です"]}

            issues = []
            warnings = []

            # 必須フィールドのチェック
            required_fields = ["date", "code"]
            for item in data:
                for field in required_fields:
                    if field not in item or not item[field]:
                        issues.append(f"必須フィールド '{field}' が不足: {item}")

            # 日付形式のチェック
            for item in data:
                try:
                    datetime.fromisoformat(item["date"])
                except (ValueError, TypeError):
                    issues.append(f"無効な日付形式: {item['date']}")

            # 数値フィールドのチェック
            numeric_fields = ["open", "high", "low", "close", "volume"]
            for item in data:
                for field in numeric_fields:
                    if field in item:
                        try:
                            float(item[field])
                        except (ValueError, TypeError):
                            warnings.append(f"数値フィールド '{field}' が無効: {item[field]}")

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


class DifferentialUpdater:
    """差分更新システム（リファクタリング版）"""

    def __init__(self, data_dir: str, logger=None, error_handler=None):
        """初期化"""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logger or logging.getLogger(__name__)
        self.error_handler = error_handler
        self.json_manager = JSONDataManager(str(self.data_dir), self.logger)
        self.config = UpdateConfig()
        
        # コンポーネントの初期化
        self.hash_calculator = DataHashCalculator()
        self.diff_calculator = DiffCalculator(self.logger)
        self.validator = DataValidator(self.logger)

    def update_stock_data(
        self, symbol: str, new_data: List[Dict[str, Any]], source: str = "api"
    ) -> Dict[str, Any]:
        """株価データの差分更新"""
        try:
            # データ検証
            validation_result = self.validator.validate_update_data(new_data, symbol)
            if not validation_result["is_valid"]:
                return {
                    "status": UpdateStatus.VALIDATION_ERROR.value,
                    "error": f"データ検証失敗: {validation_result['issues']}",
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
                        "status": UpdateStatus.SUCCESS.value,
                        "diff": {
                            "added": diff_result.added_count,
                            "updated": diff_result.updated_count,
                            "removed": diff_result.removed_count,
                            "unchanged": diff_result.unchanged_count,
                        },
                        "processing_time": diff_result.processing_time,
                        "data_hash": diff_result.data_hash,
                    }
                else:
                    return {
                        "status": UpdateStatus.FAILED.value,
                        "error": "データ保存に失敗",
                    }
            else:
                return {
                    "status": UpdateStatus.SUCCESS.value,
                    "diff": {"added": 0, "updated": 0, "removed": 0, "unchanged": 0},
                    "message": "変更なし",
                }

        except Exception as e:
            if self.logger:
                self.logger.error(f"差分更新エラー {symbol}: {e}")
            return {
                "status": UpdateStatus.FAILED.value,
                "error": str(e),
            }

    def _log_diff_update(self, symbol: str, diff_result: DiffResult, source: str) -> None:
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
