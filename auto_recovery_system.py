#!/usr/bin/env python3
"""
自動復旧システム
データパイプラインの堅牢性向上のための自動復旧機能
"""

import pandas as pd
import numpy as np
import logging
import os
import time
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass
from enum import Enum
import traceback
from functools import wraps
import json
from datetime import datetime, timedelta


class RecoveryStrategy(Enum):
    """復旧戦略の定義"""

    RETRY = "retry"
    FALLBACK = "fallback"
    SKIP = "skip"
    MANUAL = "manual"
    AUTO_FIX = "auto_fix"


@dataclass
class RecoveryAction:
    """復旧アクションのデータクラス"""

    strategy: RecoveryStrategy
    action: Callable
    max_attempts: int = 3
    delay: float = 1.0
    description: str = ""


@dataclass
class RecoveryResult:
    """復旧結果のデータクラス"""

    success: bool
    recovered_data: Optional[pd.DataFrame] = None
    error_message: Optional[str] = None
    recovery_time: float = 0.0
    attempts_made: int = 0
    strategy_used: Optional[RecoveryStrategy] = None


class AutoRecoverySystem:
    """自動復旧システム"""

    def __init__(self, max_retry_attempts: int = 3, retry_delay: float = 1.0):
        self.max_retry_attempts = max_retry_attempts
        self.retry_delay = retry_delay
        self.logger = logging.getLogger(__name__)
        self.recovery_history = []
        self.recovery_strategies = self._setup_recovery_strategies()

    def _setup_recovery_strategies(self) -> Dict[str, RecoveryAction]:
        """復旧戦略の設定"""
        strategies = {
            "data_loading_error": RecoveryAction(
                strategy=RecoveryStrategy.RETRY,
                action=self._retry_data_loading,
                max_attempts=3,
                delay=2.0,
                description="データ読み込みエラーの再試行",
            ),
            "data_validation_error": RecoveryAction(
                strategy=RecoveryStrategy.AUTO_FIX,
                action=self._auto_fix_data_validation,
                max_attempts=1,
                delay=0.5,
                description="データ検証エラーの自動修正",
            ),
            "processing_error": RecoveryAction(
                strategy=RecoveryStrategy.FALLBACK,
                action=self._fallback_processing,
                max_attempts=2,
                delay=1.0,
                description="処理エラーのフォールバック",
            ),
            "memory_error": RecoveryAction(
                strategy=RecoveryStrategy.AUTO_FIX,
                action=self._handle_memory_error,
                max_attempts=1,
                delay=0.1,
                description="メモリエラーの自動処理",
            ),
            "file_not_found": RecoveryAction(
                strategy=RecoveryStrategy.FALLBACK,
                action=self._handle_file_not_found,
                max_attempts=1,
                delay=0.5,
                description="ファイル不存在エラーのフォールバック",
            ),
            "network_error": RecoveryAction(
                strategy=RecoveryStrategy.RETRY,
                action=self._retry_network_operation,
                max_attempts=5,
                delay=3.0,
                description="ネットワークエラーの再試行",
            ),
        }
        return strategies

    def auto_recover(self, error: Exception, context: Dict[str, Any]) -> RecoveryResult:
        """自動復旧の実行"""
        start_time = time.time()
        error_type = type(error).__name__

        self.logger.info(f"🔄 自動復旧を開始: エラー={error_type}")

        # エラータイプに応じた復旧戦略を選択
        strategy = self._select_recovery_strategy(error, context)

        if strategy is None:
            return RecoveryResult(
                success=False,
                error_message=f"復旧戦略が見つかりません: {error_type}",
                recovery_time=time.time() - start_time,
            )

        # 復旧の実行
        result = self._execute_recovery(strategy, error, context)
        result.recovery_time = time.time() - start_time
        result.strategy_used = strategy.strategy

        # 復旧履歴の記録
        self._record_recovery_history(error, result, context)

        if result.success:
            self.logger.info(
                f"✅ 自動復旧成功: 戦略={strategy.strategy.value}, 時間={result.recovery_time:.2f}秒"
            )
        else:
            self.logger.warning(
                f"❌ 自動復旧失敗: 戦略={strategy.strategy.value}, エラー={result.error_message}"
            )

        return result

    def _select_recovery_strategy(
        self, error: Exception, context: Dict[str, Any]
    ) -> Optional[RecoveryAction]:
        """復旧戦略の選択"""
        error_type = type(error).__name__.lower()

        # エラータイプに基づく戦略選択
        if "file" in error_type or "notfound" in error_type:
            return self.recovery_strategies.get("file_not_found")
        elif "validation" in error_type or "value" in error_type:
            return self.recovery_strategies.get("data_validation_error")
        elif "memory" in error_type or "memoryerror" in error_type:
            return self.recovery_strategies.get("memory_error")
        elif "network" in error_type or "connection" in error_type:
            return self.recovery_strategies.get("network_error")
        elif "processing" in error_type or "calculation" in error_type:
            return self.recovery_strategies.get("processing_error")
        else:
            return self.recovery_strategies.get("data_loading_error")

    def _execute_recovery(
        self, strategy: RecoveryAction, error: Exception, context: Dict[str, Any]
    ) -> RecoveryResult:
        """復旧の実行"""
        attempts = 0
        last_error = error

        while attempts < strategy.max_attempts:
            try:
                attempts += 1
                self.logger.debug(
                    f"復旧試行 {attempts}/{strategy.max_attempts}: {strategy.description}"
                )

                result = strategy.action(error, context)

                if result.success:
                    return result
                else:
                    last_error = result.error_message or error

            except Exception as e:
                last_error = e
                self.logger.warning(f"復旧試行 {attempts} でエラー: {str(e)}")

            if attempts < strategy.max_attempts:
                time.sleep(strategy.delay)

        return RecoveryResult(
            success=False,
            error_message=f"復旧失敗: {str(last_error)}",
            attempts_made=attempts,
        )

    def _retry_data_loading(
        self, error: Exception, context: Dict[str, Any]
    ) -> RecoveryResult:
        """データ読み込みの再試行"""
        try:
            # コンテキストからデータ読み込み関数を取得
            load_function = context.get("load_function")
            if not load_function:
                return RecoveryResult(
                    success=False,
                    error_message="データ読み込み関数が指定されていません",
                )

            # データの再読み込み
            data = load_function()
            return RecoveryResult(success=True, recovered_data=data)

        except Exception as e:
            return RecoveryResult(success=False, error_message=str(e))

    def _auto_fix_data_validation(
        self, error: Exception, context: Dict[str, Any]
    ) -> RecoveryResult:
        """データ検証エラーの自動修正"""
        try:
            data = context.get("data")
            if data is None:
                return RecoveryResult(
                    success=False, error_message="データが指定されていません"
                )

            # データの自動修正
            fixed_data = self._fix_data_issues(data)
            return RecoveryResult(success=True, recovered_data=fixed_data)

        except Exception as e:
            return RecoveryResult(success=False, error_message=str(e))

    def _fallback_processing(
        self, error: Exception, context: Dict[str, Any]
    ) -> RecoveryResult:
        """フォールバック処理"""
        try:
            # フォールバック用の簡易処理
            data = context.get("data")
            if data is None:
                return RecoveryResult(
                    success=False, error_message="データが指定されていません"
                )

            # 簡易処理の実行
            processed_data = self._simplified_processing(data)
            return RecoveryResult(success=True, recovered_data=processed_data)

        except Exception as e:
            return RecoveryResult(success=False, error_message=str(e))

    def _handle_memory_error(
        self, error: Exception, context: Dict[str, Any]
    ) -> RecoveryResult:
        """メモリエラーの処理"""
        try:
            # メモリ使用量の削減
            import gc

            gc.collect()

            # データの分割処理
            data = context.get("data")
            if data is None:
                return RecoveryResult(
                    success=False, error_message="データが指定されていません"
                )

            # データを小さなチャンクに分割
            chunk_size = len(data) // 4
            processed_chunks = []

            for i in range(0, len(data), chunk_size):
                chunk = data.iloc[i : i + chunk_size]
                processed_chunk = self._process_chunk(chunk)
                processed_chunks.append(processed_chunk)
                gc.collect()  # メモリの解放

            # 結果の結合
            result_data = pd.concat(processed_chunks, ignore_index=True)
            return RecoveryResult(success=True, recovered_data=result_data)

        except Exception as e:
            return RecoveryResult(success=False, error_message=str(e))

    def _handle_file_not_found(
        self, error: Exception, context: Dict[str, Any]
    ) -> RecoveryResult:
        """ファイル不存在エラーの処理"""
        try:
            # 代替ファイルの検索
            original_path = context.get("file_path")
            if not original_path:
                return RecoveryResult(
                    success=False, error_message="ファイルパスが指定されていません"
                )

            # 代替ファイルの検索
            alternative_paths = self._find_alternative_files(original_path)

            for alt_path in alternative_paths:
                if os.path.exists(alt_path):
                    # 代替ファイルからの読み込み
                    data = pd.read_csv(alt_path)
                    return RecoveryResult(success=True, recovered_data=data)

            return RecoveryResult(
                success=False, error_message="代替ファイルが見つかりません"
            )

        except Exception as e:
            return RecoveryResult(success=False, error_message=str(e))

    def _retry_network_operation(
        self, error: Exception, context: Dict[str, Any]
    ) -> RecoveryResult:
        """ネットワーク操作の再試行"""
        try:
            # ネットワーク操作の再試行
            network_function = context.get("network_function")
            if not network_function:
                return RecoveryResult(
                    success=False, error_message="ネットワーク関数が指定されていません"
                )

            # 再試行
            result = network_function()
            return RecoveryResult(success=True, recovered_data=result)

        except Exception as e:
            return RecoveryResult(success=False, error_message=str(e))

    def _fix_data_issues(self, data: pd.DataFrame) -> pd.DataFrame:
        """データ問題の自動修正"""
        fixed_data = data.copy()

        # 欠損値の処理
        numeric_columns = fixed_data.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if fixed_data[col].isnull().any():
                # 前値補完
                fixed_data[col] = fixed_data[col].fillna(method="ffill")
                # まだ欠損値がある場合は後値補完
                fixed_data[col] = fixed_data[col].fillna(method="bfill")
                # それでも欠損値がある場合は平均値で補完
                fixed_data[col] = fixed_data[col].fillna(fixed_data[col].mean())

        # 異常値の処理
        for col in numeric_columns:
            if col in ["Open", "High", "Low", "Close", "Volume"]:
                # 負の値の修正
                if col == "Volume":
                    fixed_data[col] = fixed_data[col].clip(lower=0)
                else:
                    fixed_data[col] = fixed_data[col].clip(lower=0.01)

                # 異常に大きな値の修正
                q99 = fixed_data[col].quantile(0.99)
                fixed_data[col] = fixed_data[col].clip(upper=q99)

        # OHLCデータの整合性修正
        if all(col in fixed_data.columns for col in ["Open", "High", "Low", "Close"]):
            # High >= Low の保証
            fixed_data["High"] = np.maximum(fixed_data["High"], fixed_data["Low"])
            # High >= Open, Close の保証
            fixed_data["High"] = np.maximum(fixed_data["High"], fixed_data["Open"])
            fixed_data["High"] = np.maximum(fixed_data["High"], fixed_data["Close"])
            # Low <= Open, Close の保証
            fixed_data["Low"] = np.minimum(fixed_data["Low"], fixed_data["Open"])
            fixed_data["Low"] = np.minimum(fixed_data["Low"], fixed_data["Close"])

        return fixed_data

    def _simplified_processing(self, data: pd.DataFrame) -> pd.DataFrame:
        """簡易処理"""
        # 基本的な処理のみ実行
        processed_data = data.copy()

        # 基本的な技術指標の計算
        if "Close" in processed_data.columns:
            processed_data["SMA_5"] = processed_data["Close"].rolling(window=5).mean()
            processed_data["SMA_25"] = processed_data["Close"].rolling(window=25).mean()

        return processed_data

    def _process_chunk(self, chunk: pd.DataFrame) -> pd.DataFrame:
        """チャンクの処理"""
        # チャンクに対する基本的な処理
        processed_chunk = chunk.copy()

        # 基本的な技術指標の計算
        if "Close" in processed_chunk.columns:
            processed_chunk["SMA_5"] = processed_chunk["Close"].rolling(window=5).mean()
            processed_chunk["SMA_25"] = (
                processed_chunk["Close"].rolling(window=25).mean()
            )

        return processed_chunk

    def _find_alternative_files(self, original_path: str) -> List[str]:
        """代替ファイルの検索"""
        alternatives = []

        # 同じディレクトリ内の類似ファイル
        directory = os.path.dirname(original_path)
        filename = os.path.basename(original_path)
        name, ext = os.path.splitext(filename)

        # バックアップファイルの検索
        backup_patterns = [
            f"{name}_backup{ext}",
            f"{name}_old{ext}",
            f"{name}_bak{ext}",
            f"{name}.bak{ext}",
            f"{name}_1{ext}",
            f"{name}_2{ext}",
        ]

        for pattern in backup_patterns:
            alt_path = os.path.join(directory, pattern)
            alternatives.append(alt_path)

        # 親ディレクトリの検索
        parent_dir = os.path.dirname(directory)
        if parent_dir:
            alt_path = os.path.join(parent_dir, filename)
            alternatives.append(alt_path)

        return alternatives

    def _record_recovery_history(
        self, error: Exception, result: RecoveryResult, context: Dict[str, Any]
    ):
        """復旧履歴の記録"""
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "recovery_success": result.success,
            "recovery_time": result.recovery_time,
            "attempts_made": result.attempts_made,
            "strategy_used": (
                result.strategy_used.value if result.strategy_used else None
            ),
            "context": {
                k: str(v) for k, v in context.items() if k != "data"
            },  # データは除外
        }

        self.recovery_history.append(history_entry)

        # 履歴の保存（最新100件まで）
        if len(self.recovery_history) > 100:
            self.recovery_history = self.recovery_history[-100:]

    def get_recovery_statistics(self) -> Dict[str, Any]:
        """復旧統計の取得"""
        if not self.recovery_history:
            return {"total_recoveries": 0}

        total_recoveries = len(self.recovery_history)
        successful_recoveries = sum(
            1 for h in self.recovery_history if h["recovery_success"]
        )
        success_rate = (
            successful_recoveries / total_recoveries if total_recoveries > 0 else 0
        )

        # エラータイプ別の統計
        error_types = {}
        for entry in self.recovery_history:
            error_type = entry["error_type"]
            if error_type not in error_types:
                error_types[error_type] = {"count": 0, "success": 0}
            error_types[error_type]["count"] += 1
            if entry["recovery_success"]:
                error_types[error_type]["success"] += 1

        # 戦略別の統計
        strategies = {}
        for entry in self.recovery_history:
            strategy = entry["strategy_used"]
            if strategy:
                if strategy not in strategies:
                    strategies[strategy] = {"count": 0, "success": 0}
                strategies[strategy]["count"] += 1
                if entry["recovery_success"]:
                    strategies[strategy]["success"] += 1

        return {
            "total_recoveries": total_recoveries,
            "successful_recoveries": successful_recoveries,
            "success_rate": success_rate,
            "error_types": error_types,
            "strategies": strategies,
            "average_recovery_time": np.mean(
                [h["recovery_time"] for h in self.recovery_history]
            ),
        }

    def save_recovery_history(self, file_path: str):
        """復旧履歴の保存"""
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.recovery_history, f, ensure_ascii=False, indent=2)

    def load_recovery_history(self, file_path: str):
        """復旧履歴の読み込み"""
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                self.recovery_history = json.load(f)


def auto_recover_decorator(recovery_system: AutoRecoverySystem):
    """自動復旧デコレータ"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # コンテキストの準備
                context = {
                    "function_name": func.__name__,
                    "args": str(args)[:100],  # 最初の100文字のみ
                    "kwargs": str(kwargs)[:100],
                }

                # 自動復旧の実行
                recovery_result = recovery_system.auto_recover(e, context)

                if recovery_result.success:
                    return recovery_result.recovered_data
                else:
                    # 復旧に失敗した場合は元のエラーを再発生
                    raise e

        return wrapper

    return decorator


# 便利関数
def create_auto_recovery_system(
    max_retry_attempts: int = 3, retry_delay: float = 1.0
) -> AutoRecoverySystem:
    """自動復旧システムの作成"""
    return AutoRecoverySystem(max_retry_attempts, retry_delay)


def with_auto_recovery(max_retry_attempts: int = 3, retry_delay: float = 1.0):
    """自動復旧付きデコレータ"""
    recovery_system = create_auto_recovery_system(max_retry_attempts, retry_delay)
    return auto_recover_decorator(recovery_system)


if __name__ == "__main__":
    # テスト用のサンプル
    recovery_system = create_auto_recovery_system()

    # 復旧統計の表示
    stats = recovery_system.get_recovery_statistics()
    print(f"復旧統計: {stats}")
