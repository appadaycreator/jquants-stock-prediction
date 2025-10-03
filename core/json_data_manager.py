#!/usr/bin/env python3
"""
JSON形式でのデータ管理システム
jQuantsから取得されたデータをJSON形式で保持し、差分更新を実装
"""

import json
import os
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import logging
from pathlib import Path


class JSONDataManager:
    """JSON形式でのデータ管理クラス"""

    def __init__(self, data_dir: str = "data", logger=None):
        """
        初期化

        Args:
            data_dir: データ保存ディレクトリ
            logger: ロガーインスタンス
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.logger = logger or logging.getLogger(__name__)

        # データファイルのパス
        self.stock_data_file = self.data_dir / "stock_data.json"
        self.metadata_file = self.data_dir / "metadata.json"
        self.diff_log_file = self.data_dir / "diff_log.json"

        # メタデータの初期化
        self._initialize_metadata()

    def _initialize_metadata(self):
        """メタデータファイルの初期化"""
        if not self.metadata_file.exists():
            metadata = {
                "created_at": datetime.now().isoformat(),
                "last_updated": None,
                "version": "1.0",
                "data_sources": {},
                "update_history": [],
            }
            self._save_json(self.metadata_file, metadata)

    def _save_json(self, file_path: Path, data: Any) -> bool:
        """JSONファイルの保存（最適化版）"""
        try:
            # 一時ファイルに保存してからリネーム（アトミック操作）
            temp_path = file_path.with_suffix(".tmp")
            with open(temp_path, "w", encoding="utf-8") as f:
                # メモリ効率を考慮したJSON保存
                json.dump(data, f, ensure_ascii=False, indent=2, separators=(",", ":"))
            temp_path.replace(file_path)
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"JSON保存エラー {file_path}: {e}")
            return False

    def _load_json(self, file_path: Path, default: Any = None) -> Any:
        """JSONファイルの読み込み（最適化版）"""
        try:
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            return default
        except json.JSONDecodeError as e:
            if self.logger:
                self.logger.error(f"JSON解析エラー {file_path}: {e}")
            return default
        except Exception as e:
            if self.logger:
                self.logger.error(f"JSON読み込みエラー {file_path}: {e}")
            return default

    def _calculate_hash(self, data: Any) -> str:
        """データのハッシュ値を計算（最適化版）"""
        try:
            # メモリ効率を考慮したハッシュ計算
            data_str = json.dumps(
                data, sort_keys=True, ensure_ascii=False, separators=(",", ":")
            )
            return hashlib.md5(data_str.encode("utf-8")).hexdigest()
        except Exception as e:
            if self.logger:
                self.logger.error(f"ハッシュ計算エラー: {e}")
            return hashlib.md5(str(data).encode("utf-8")).hexdigest()

    def save_stock_data(
        self, symbol: str, data: List[Dict[str, Any]], source: str = "jquants_api"
    ) -> bool:
        """
        株価データの保存

        Args:
            symbol: 銘柄コード
            data: 株価データのリスト
            source: データソース

        Returns:
            bool: 保存成功フラグ
        """
        try:
            # 既存データの読み込み
            existing_data = self._load_json(self.stock_data_file, {})

            # データの正規化と検証
            normalized_data = self._normalize_stock_data(data)

            # 差分の計算
            diff_result = self._calculate_diff(
                existing_data.get(symbol, []), normalized_data
            )

            # データの更新
            existing_data[symbol] = normalized_data

            # 保存
            if self._save_json(self.stock_data_file, existing_data):
                # メタデータの更新
                self._update_metadata(symbol, source, diff_result)

                # 差分ログの記録
                self._log_diff(symbol, diff_result)

                if self.logger:
                    self.logger.info(
                        f"株価データ保存完了: {symbol} ({len(normalized_data)}件)"
                    )
                return True

            return False

        except Exception as e:
            if self.logger:
                self.logger.error(f"株価データ保存エラー {symbol}: {e}")
            return False

    def _normalize_stock_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """株価データの正規化"""
        normalized = []

        for item in data:
            try:
                # 必須フィールドの検証
                if not self._validate_required_fields(item):
                    continue

                # データ型の変換と検証
                normalized_item = self._convert_data_types(item)

                # 追加フィールドがあれば保持
                normalized_item.update(self._extract_additional_fields(item))

                normalized.append(normalized_item)
            except (ValueError, TypeError) as e:
                if self.logger:
                    self.logger.warning(f"データ正規化エラー: {item} - {e}")
                continue

        # 日付順でソート
        normalized.sort(key=lambda x: x["date"])

        return normalized

    def _validate_required_fields(self, item: Dict[str, Any]) -> bool:
        """必須フィールドの検証"""
        required_fields = ["date", "code", "open", "high", "low", "close", "volume"]
        if not all(field in item for field in required_fields):
            if self.logger:
                self.logger.warning(f"必須フィールドが不足: {item}")
            return False
        return True

    def _convert_data_types(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """データ型の変換"""
        return {
            "date": str(item["date"]),
            "code": str(item["code"]),
            "open": float(item["open"]) if item["open"] is not None else 0.0,
            "high": float(item["high"]) if item["high"] is not None else 0.0,
            "low": float(item["low"]) if item["low"] is not None else 0.0,
            "close": float(item["close"]) if item["close"] is not None else 0.0,
            "volume": int(item["volume"]) if item["volume"] is not None else 0,
        }

    def _extract_additional_fields(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """追加フィールドの抽出"""
        additional_fields = {}
        for key, value in item.items():
            if key not in ["date", "code", "open", "high", "low", "close", "volume"]:
                additional_fields[key] = value
        return additional_fields

    def _calculate_diff(
        self, old_data: List[Dict[str, Any]], new_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """差分の計算"""
        old_dates = {item["date"]: item for item in old_data}
        new_dates = {item["date"]: item for item in new_data}

        added = []
        updated = []
        removed = []

        # 新規追加・更新の検出
        for date, new_item in new_dates.items():
            if date not in old_dates:
                added.append(new_item)
            else:
                old_item = old_dates[date]
                if self._calculate_hash(old_item) != self._calculate_hash(new_item):
                    updated.append({"date": date, "old": old_item, "new": new_item})

        # 削除の検出
        for date, old_item in old_dates.items():
            if date not in new_dates:
                removed.append(old_item)

        return {
            "added_count": len(added),
            "updated_count": len(updated),
            "removed_count": len(removed),
            "added": added,
            "updated": updated,
            "removed": removed,
            "total_old": len(old_data),
            "total_new": len(new_data),
        }

    def _update_metadata(self, symbol: str, source: str, diff_result: Dict[str, Any]):
        """メタデータの更新"""
        metadata = self._load_json(self.metadata_file, {})

        # データソース情報の更新
        if "data_sources" not in metadata:
            metadata["data_sources"] = {}

        metadata["data_sources"][symbol] = {
            "source": source,
            "last_updated": datetime.now().isoformat(),
            "total_records": diff_result.get("total_new", 0),
            "last_diff": diff_result,
        }

        # 更新履歴の記録
        if "update_history" not in metadata:
            metadata["update_history"] = []

        metadata["update_history"].append(
            {
                "timestamp": datetime.now().isoformat(),
                "symbol": symbol,
                "source": source,
                "diff_summary": {
                    "added": diff_result["added_count"],
                    "updated": diff_result["updated_count"],
                    "removed": diff_result["removed_count"],
                },
            }
        )

        # 履歴の保持（最新100件）
        metadata["update_history"] = metadata["update_history"][-100:]

        metadata["last_updated"] = datetime.now().isoformat()

        self._save_json(self.metadata_file, metadata)

    def _log_diff(self, symbol: str, diff_result: Dict[str, Any]):
        """差分ログの記録"""
        diff_log = self._load_json(self.diff_log_file, [])

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "diff": diff_result,
        }

        diff_log.append(log_entry)

        # ログの保持（最新1000件）
        diff_log = diff_log[-1000:]

        self._save_json(self.diff_log_file, diff_log)

    def save_data(self, filename: str, data: List[Dict[str, Any]]) -> bool:
        """
        データの保存

        Args:
            filename: 保存先ファイル名
            data: 保存するデータ

        Returns:
            bool: 保存成功フラグ
        """
        try:
            file_path = self.data_dir / filename
            self._save_json(file_path, data)
            self.logger.info(f"データ保存完了: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"データ保存失敗: {filename} - {str(e)}")
            return False

    def get_stock_data(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        株価データの取得

        Args:
            symbol: 銘柄コード
            start_date: 開始日（YYYY-MM-DD）
            end_date: 終了日（YYYY-MM-DD）

        Returns:
            List[Dict[str, Any]]: 株価データのリスト
        """
        try:
            stock_data = self._load_json(self.stock_data_file, {})
            data = stock_data.get(symbol, [])

            if start_date or end_date:
                filtered_data = []
                for item in data:
                    item_date = item["date"]
                    if start_date and item_date < start_date:
                        continue
                    if end_date and item_date > end_date:
                        continue
                    filtered_data.append(item)
                return filtered_data

            return data

        except Exception as e:
            self.logger.error(f"株価データ取得エラー {symbol}: {e}")
            return []

    def get_latest_data(self, symbol: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        最新の株価データの取得

        Args:
            symbol: 銘柄コード
            days: 取得日数

        Returns:
            List[Dict[str, Any]]: 最新の株価データ
        """
        try:
            data = self.get_stock_data(symbol)

            # 日付順でソートして最新のデータを取得
            data.sort(key=lambda x: x["date"], reverse=True)

            return data[:days]

        except Exception as e:
            self.logger.error(f"最新データ取得エラー {symbol}: {e}")
            return []

    def get_incremental_data(
        self, symbol: str, last_update: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        差分データの取得

        Args:
            symbol: 銘柄コード
            last_update: 最終更新日時

        Returns:
            Dict[str, Any]: 差分データ
        """
        try:
            # メタデータから最終更新時刻を取得
            metadata = self._load_json(self.metadata_file, {})
            symbol_metadata = metadata.get("data_sources", {}).get(symbol, {})

            if not last_update:
                last_update = symbol_metadata.get("last_updated")

            if not last_update:
                # 初回取得の場合は全データを返す
                return {
                    "is_full_update": True,
                    "data": self.get_stock_data(symbol),
                    "last_update": None,
                }

            # 差分ログから該当期間の変更を取得
            diff_log = self._load_json(self.diff_log_file, [])
            relevant_diffs = [
                entry
                for entry in diff_log
                if entry["symbol"] == symbol and entry["timestamp"] > last_update
            ]

            if not relevant_diffs:
                return {"is_full_update": False, "data": [], "last_update": last_update}

            # 差分データの構築
            incremental_data = []
            for diff_entry in relevant_diffs:
                diff = diff_entry["diff"]
                incremental_data.extend(diff.get("added", []))
                incremental_data.extend(
                    [item["new"] for item in diff.get("updated", [])]
                )

            return {
                "is_full_update": False,
                "data": incremental_data,
                "last_update": datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"差分データ取得エラー {symbol}: {e}")
            return {
                "is_full_update": True,
                "data": self.get_stock_data(symbol),
                "last_update": None,
            }

    def get_metadata(self) -> Dict[str, Any]:
        """メタデータの取得"""
        return self._load_json(self.metadata_file, {})

    def get_diff_log(
        self, symbol: Optional[str] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        差分ログの取得

        Args:
            symbol: 銘柄コード（指定時は該当銘柄のみ）
            limit: 取得件数制限

        Returns:
            List[Dict[str, Any]]: 差分ログ
        """
        try:
            diff_log = self._load_json(self.diff_log_file, [])

            if symbol:
                diff_log = [entry for entry in diff_log if entry["symbol"] == symbol]

            return diff_log[-limit:]

        except Exception as e:
            self.logger.error(f"差分ログ取得エラー: {e}")
            return []

    def cleanup_old_data(self, days_to_keep: int = 365):
        """
        古いデータのクリーンアップ

        Args:
            days_to_keep: 保持日数
        """
        try:
            if days_to_keep <= 0:
                # 全てのデータを削除
                cutoff_date = datetime.now()
                cutoff_str = cutoff_date.strftime("%Y-%m-%d")
            else:
                cutoff_date = datetime.now() - timedelta(days=days_to_keep)
                cutoff_str = cutoff_date.strftime("%Y-%m-%d")

            # 株価データのクリーンアップ
            stock_data = self._load_json(self.stock_data_file, {})
            cleaned_data = {}

            for symbol, data in stock_data.items():
                if isinstance(data, list):
                    cleaned_symbol_data = [
                        item
                        for item in data
                        if isinstance(item, dict) and item.get("date", "") >= cutoff_str
                    ]
                    if cleaned_symbol_data:
                        cleaned_data[symbol] = cleaned_symbol_data

            self._save_json(self.stock_data_file, cleaned_data)

            # 差分ログのクリーンアップ
            diff_log = self._load_json(self.diff_log_file, [])
            cleaned_log = [
                entry
                for entry in diff_log
                if datetime.fromisoformat(entry["timestamp"]) >= cutoff_date
            ]
            self._save_json(self.diff_log_file, cleaned_log)

            if self.logger:
                self.logger.info(
                    f"データクリーンアップ完了: {days_to_keep}日以前のデータを削除"
                )
            return True

        except Exception as e:
            if self.logger:
                self.logger.error(f"データクリーンアップエラー: {e}")
            return False

    def export_data(self, symbol: str, output_file: str) -> bool:
        """
        データのエクスポート

        Args:
            symbol: 銘柄コード
            output_file: 出力ファイルパス

        Returns:
            bool: エクスポート成功フラグ
        """
        try:
            data = self.get_stock_data(symbol)

            if not data:
                self.logger.warning(f"エクスポート対象データがありません: {symbol}")
                return False

            metadata = self.get_metadata()

            export_data = {
                "symbol": symbol,
                "exported_at": datetime.now().isoformat(),
                "metadata": metadata.get("data_sources", {}).get(symbol, {}),
                "data": data,
            }

            # 出力ディレクトリの作成
            import os

            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)

            self.logger.info(f"データエクスポート完了: {symbol} -> {output_file}")
            return True

        except Exception as e:
            self.logger.error(f"データエクスポートエラー {symbol}: {e}")
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """データ統計の取得"""
        try:
            stock_data = self._load_json(self.stock_data_file, {})
            metadata = self._load_json(self.metadata_file, {})

            stats = {
                "total_symbols": len(stock_data),
                "total_records": sum(len(data) for data in stock_data.values()),
                "last_updated": metadata.get("last_updated"),
                "data_sources": metadata.get("data_sources", {}),
                "symbols": list(stock_data.keys()),
            }

            return stats

        except Exception as e:
            self.logger.error(f"統計取得エラー: {e}")
            return {}

    def get_all_symbols(self) -> List[str]:
        """全銘柄コードの取得"""
        try:
            stock_data = self._load_json(self.stock_data_file, {})
            return list(stock_data.keys())
        except Exception as e:
            self.logger.error(f"銘柄コード取得エラー: {e}")
            return []

    def get_data_statistics(self) -> Dict[str, Any]:
        """データ統計の取得（テスト互換性のため）"""
        return self.get_statistics()


# 使用例
if __name__ == "__main__":
    # ログ設定
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # JSONDataManagerの初期化
    manager = JSONDataManager("data", logger)

    # サンプルデータの保存
    sample_data = [
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

    # データの保存
    success = manager.save_stock_data("7203", sample_data, "jquants_api")
    print(f"データ保存: {'成功' if success else '失敗'}")

    # データの取得
    data = manager.get_stock_data("7203")
    print(f"取得データ件数: {len(data)}")

    # 統計情報の取得
    stats = manager.get_statistics()
    print(f"統計情報: {stats}")
