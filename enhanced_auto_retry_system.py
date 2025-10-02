#!/usr/bin/env python3
"""
強化された自動リトライシステム
ワンクリック分析の完全自動化 - 自動リトライ機能
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import random
import yaml
from pathlib import Path
import traceback

# ログ設定
import os
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/auto_retry.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class RetryStrategy(Enum):
    """リトライ戦略"""

    FIXED = "fixed"  # 固定間隔
    EXPONENTIAL = "exponential"  # 指数バックオフ
    LINEAR = "linear"  # 線形増加
    RANDOM = "random"  # ランダム間隔
    CUSTOM = "custom"  # カスタム戦略


class RetryCondition(Enum):
    """リトライ条件"""

    ALL_ERRORS = "all_errors"  # 全てのエラー
    NETWORK_ERRORS = "network_errors"  # ネットワークエラーのみ
    API_ERRORS = "api_errors"  # APIエラーのみ
    TIMEOUT_ERRORS = "timeout_errors"  # タイムアウトエラーのみ
    CUSTOM = "custom"  # カスタム条件


@dataclass
class RetryConfig:
    """リトライ設定"""

    max_attempts: int = 3
    base_delay: float = 1.0  # 基本遅延時間（秒）
    max_delay: float = 60.0  # 最大遅延時間（秒）
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    condition: RetryCondition = RetryCondition.ALL_ERRORS
    jitter: bool = True  # ジッター（ランダム性）の有効化
    backoff_multiplier: float = 2.0  # バックオフ乗数
    timeout: Optional[float] = None  # 全体タイムアウト
    custom_conditions: List[Callable[[Exception], bool]] = None  # カスタム条件
    custom_delays: List[float] = None  # カスタム遅延時間
    retry_on_success: bool = False  # 成功時もリトライするか
    log_retries: bool = True  # リトライログの出力

    def __post_init__(self):
        if self.custom_conditions is None:
            self.custom_conditions = []
        if self.custom_delays is None:
            self.custom_delays = []


@dataclass
class RetryResult:
    """リトライ結果"""

    success: bool
    attempts: int
    total_duration: float
    final_result: Any = None
    errors: List[Exception] = None
    retry_times: List[float] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.retry_times is None:
            self.retry_times = []


@dataclass
class RetryContext:
    """リトライコンテキスト"""

    operation_id: str
    operation_name: str
    start_time: datetime
    config: RetryConfig
    attempt_count: int = 0
    last_error: Optional[Exception] = None
    last_result: Any = None
    custom_data: Dict[str, Any] = None

    def __post_init__(self):
        if self.custom_data is None:
            self.custom_data = {}


class EnhancedAutoRetrySystem:
    """強化された自動リトライシステム"""

    def __init__(self, config_file: str = "retry_config.yaml"):
        self.config_file = config_file
        self.default_config = self._load_default_config()
        self.retry_history = []
        self.active_retries = {}

    def _load_default_config(self) -> Dict[str, Any]:
        """デフォルト設定の読み込み"""
        return {
            "retry_system": {
                "enabled": True,
                "default_max_attempts": 3,
                "default_base_delay": 1.0,
                "default_max_delay": 60.0,
                "default_strategy": "exponential",
                "global_timeout": 300.0,  # 5分
                "circuit_breaker": {
                    "enabled": True,
                    "failure_threshold": 5,
                    "recovery_timeout": 60.0,
                },
                "adaptive_retry": {
                    "enabled": True,
                    "success_rate_threshold": 0.8,
                    "adjustment_factor": 0.1,
                },
            },
            "operation_configs": {
                "data_fetch": {
                    "max_attempts": 5,
                    "base_delay": 2.0,
                    "strategy": "exponential",
                    "condition": "network_errors",
                },
                "model_prediction": {
                    "max_attempts": 3,
                    "base_delay": 1.0,
                    "strategy": "fixed",
                    "condition": "all_errors",
                },
                "notification_send": {
                    "max_attempts": 2,
                    "base_delay": 5.0,
                    "strategy": "linear",
                    "condition": "network_errors",
                },
            },
        }

    def _load_config(self) -> Dict[str, Any]:
        """設定ファイルの読み込み"""
        try:
            if Path(self.config_file).exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f)
                    return {**self.default_config, **config}
            else:
                return self.default_config
        except Exception as e:
            logger.error(f"設定ファイル読み込みエラー: {e}")
            return self.default_config

    async def retry_operation(
        self,
        operation: Callable,
        operation_name: str,
        config: Optional[RetryConfig] = None,
        *args,
        **kwargs,
    ) -> RetryResult:
        """操作のリトライ実行"""
        # 設定の決定
        final_config = config or self._get_operation_config(operation_name)

        # リトライコンテキストの作成
        context = RetryContext(
            operation_id=f"{operation_name}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            operation_name=operation_name,
            start_time=datetime.now(),
            config=final_config,
        )

        # アクティブリトライの記録
        self.active_retries[context.operation_id] = context

        try:
            result = await self._execute_with_retry(operation, context, *args, **kwargs)
            return result
        finally:
            # アクティブリトライの削除
            if context.operation_id in self.active_retries:
                del self.active_retries[context.operation_id]

    async def _execute_with_retry(
        self, operation: Callable, context: RetryContext, *args, **kwargs
    ) -> RetryResult:
        """リトライ付き実行"""
        config = context.config
        errors = []
        retry_times = []

        for attempt in range(config.max_attempts):
            context.attempt_count = attempt + 1

            try:
                # 操作の実行
                if asyncio.iscoroutinefunction(operation):
                    result = await operation(*args, **kwargs)
                else:
                    result = operation(*args, **kwargs)

                # 成功時の処理
                if config.retry_on_success and attempt < config.max_attempts - 1:
                    # 成功時もリトライする場合
                    delay = self._calculate_delay(attempt, config)
                    if config.log_retries:
                        logger.info(
                            f"操作成功（リトライ継続）: {context.operation_name} - 試行 {attempt + 1}/{config.max_attempts}"
                        )
                    await asyncio.sleep(delay)
                    retry_times.append(delay)
                    continue
                else:
                    # 通常の成功
                    duration = (datetime.now() - context.start_time).total_seconds()
                    result = RetryResult(
                        success=True,
                        attempts=attempt + 1,
                        total_duration=duration,
                        final_result=result,
                        errors=errors,
                        retry_times=retry_times,
                    )

                    self._record_retry_success(context, result)
                    return result

            except Exception as e:
                context.last_error = e
                errors.append(e)

                # リトライ条件のチェック
                if not self._should_retry(e, config, attempt):
                    duration = (datetime.now() - context.start_time).total_seconds()
                    result = RetryResult(
                        success=False,
                        attempts=attempt + 1,
                        total_duration=duration,
                        final_result=None,
                        errors=errors,
                        retry_times=retry_times,
                    )

                    self._record_retry_failure(context, result)
                    return result

                # 最後の試行でない場合のみリトライ
                if attempt < config.max_attempts - 1:
                    delay = self._calculate_delay(attempt, config)
                    if config.log_retries:
                        logger.warning(
                            f"操作失敗、リトライ予定: {context.operation_name} - 試行 {attempt + 1}/{config.max_attempts} - エラー: {str(e)}"
                        )
                    await asyncio.sleep(delay)
                    retry_times.append(delay)
                else:
                    # 最後の試行で失敗
                    duration = (datetime.now() - context.start_time).total_seconds()
                    result = RetryResult(
                        success=False,
                        attempts=attempt + 1,
                        total_duration=duration,
                        final_result=None,
                        errors=errors,
                        retry_times=retry_times,
                    )

                    self._record_retry_failure(context, result)
                    return result

    def _should_retry(
        self, error: Exception, config: RetryConfig, attempt: int
    ) -> bool:
        """リトライすべきかの判定"""
        # 最大試行回数チェック
        if attempt >= config.max_attempts - 1:
            return False

        # 条件別チェック
        if config.condition == RetryCondition.ALL_ERRORS:
            return True
        elif config.condition == RetryCondition.NETWORK_ERRORS:
            return self._is_network_error(error)
        elif config.condition == RetryCondition.API_ERRORS:
            return self._is_api_error(error)
        elif config.condition == RetryCondition.TIMEOUT_ERRORS:
            return self._is_timeout_error(error)
        elif config.condition == RetryCondition.CUSTOM:
            return any(condition(error) for condition in config.custom_conditions)

        return False

    def _is_network_error(self, error: Exception) -> bool:
        """ネットワークエラーの判定"""
        error_str = str(error).lower()
        network_keywords = [
            "connection",
            "network",
            "timeout",
            "unreachable",
            "refused",
            "reset",
            "unavailable",
            "dns",
        ]
        return any(keyword in error_str for keyword in network_keywords)

    def _is_api_error(self, error: Exception) -> bool:
        """APIエラーの判定"""
        error_str = str(error).lower()
        api_keywords = [
            "api",
            "http",
            "status",
            "unauthorized",
            "forbidden",
            "not found",
            "server error",
            "bad request",
        ]
        return any(keyword in error_str for keyword in api_keywords)

    def _is_timeout_error(self, error: Exception) -> bool:
        """タイムアウトエラーの判定"""
        error_str = str(error).lower()
        timeout_keywords = ["timeout", "timed out", "deadline"]
        return any(keyword in error_str for keyword in timeout_keywords)

    def _calculate_delay(self, attempt: int, config: RetryConfig) -> float:
        """遅延時間の計算"""
        if config.strategy == RetryStrategy.FIXED:
            delay = config.base_delay
        elif config.strategy == RetryStrategy.EXPONENTIAL:
            delay = config.base_delay * (config.backoff_multiplier**attempt)
        elif config.strategy == RetryStrategy.LINEAR:
            delay = config.base_delay * (attempt + 1)
        elif config.strategy == RetryStrategy.RANDOM:
            delay = random.uniform(config.base_delay, config.base_delay * 2)
        elif config.strategy == RetryStrategy.CUSTOM:
            if attempt < len(config.custom_delays):
                delay = config.custom_delays[attempt]
            else:
                delay = config.base_delay
        else:
            delay = config.base_delay

        # 最大遅延時間の制限
        delay = min(delay, config.max_delay)

        # ジッターの適用
        if config.jitter:
            jitter_range = delay * 0.1  # 10%のジッター
            delay += random.uniform(-jitter_range, jitter_range)
            delay = max(0, delay)  # 負の値にならないよう制限

        return delay

    def _get_operation_config(self, operation_name: str) -> RetryConfig:
        """操作別設定の取得"""
        config = self._load_config()
        operation_configs = config.get("operation_configs", {})

        if operation_name in operation_configs:
            op_config = operation_configs[operation_name]
            return RetryConfig(
                max_attempts=op_config.get("max_attempts", 3),
                base_delay=op_config.get("base_delay", 1.0),
                max_delay=op_config.get("max_delay", 60.0),
                strategy=RetryStrategy(op_config.get("strategy", "exponential")),
                condition=RetryCondition(op_config.get("condition", "all_errors")),
            )
        else:
            # デフォルト設定
            return RetryConfig()

    def _record_retry_success(self, context: RetryContext, result: RetryResult):
        """リトライ成功の記録"""
        record = {
            "operation_id": context.operation_id,
            "operation_name": context.operation_name,
            "success": True,
            "attempts": result.attempts,
            "duration": result.total_duration,
            "timestamp": datetime.now(),
            "retry_times": result.retry_times,
        }

        self.retry_history.append(record)
        logger.info(
            f"リトライ成功: {context.operation_name} - {result.attempts}回の試行で成功"
        )

    def _record_retry_failure(self, context: RetryContext, result: RetryResult):
        """リトライ失敗の記録"""
        record = {
            "operation_id": context.operation_id,
            "operation_name": context.operation_name,
            "success": False,
            "attempts": result.attempts,
            "duration": result.total_duration,
            "timestamp": datetime.now(),
            "retry_times": result.retry_times,
            "final_error": str(result.errors[-1]) if result.errors else None,
        }

        self.retry_history.append(record)
        logger.error(
            f"リトライ失敗: {context.operation_name} - {result.attempts}回の試行で失敗"
        )

    def get_retry_statistics(self) -> Dict[str, Any]:
        """リトライ統計の取得"""
        if not self.retry_history:
            return {"total_operations": 0, "success_rate": 0.0, "average_attempts": 0.0}

        total_operations = len(self.retry_history)
        successful_operations = sum(
            1 for record in self.retry_history if record["success"]
        )
        success_rate = (
            successful_operations / total_operations if total_operations > 0 else 0.0
        )

        # 操作別統計
        operation_stats = {}
        for record in self.retry_history:
            op_name = record["operation_name"]
            if op_name not in operation_stats:
                operation_stats[op_name] = {"total": 0, "success": 0, "attempts": []}

            operation_stats[op_name]["total"] += 1
            if record["success"]:
                operation_stats[op_name]["success"] += 1
            operation_stats[op_name]["attempts"].append(record["attempts"])

        # 平均試行回数の計算
        for op_name in operation_stats:
            attempts = operation_stats[op_name]["attempts"]
            operation_stats[op_name]["average_attempts"] = (
                sum(attempts) / len(attempts) if attempts else 0
            )
            operation_stats[op_name]["success_rate"] = (
                operation_stats[op_name]["success"] / operation_stats[op_name]["total"]
            )

        return {
            "total_operations": total_operations,
            "successful_operations": successful_operations,
            "success_rate": success_rate,
            "operation_stats": operation_stats,
            "recent_retries": self.retry_history[-10:] if self.retry_history else [],
        }

    def get_active_retries(self) -> Dict[str, RetryContext]:
        """アクティブなリトライの取得"""
        return self.active_retries.copy()

    def cancel_retry(self, operation_id: str) -> bool:
        """リトライのキャンセル"""
        if operation_id in self.active_retries:
            del self.active_retries[operation_id]
            logger.info(f"リトライキャンセル: {operation_id}")
            return True
        return False

    async def retry_with_circuit_breaker(
        self,
        operation: Callable,
        operation_name: str,
        config: Optional[RetryConfig] = None,
        *args,
        **kwargs,
    ) -> RetryResult:
        """サーキットブレーカー付きリトライ"""
        # サーキットブレーカーの状態チェック
        if self._is_circuit_breaker_open(operation_name):
            logger.warning(
                f"サーキットブレーカーが開いているため操作をスキップ: {operation_name}"
            )
            return RetryResult(
                success=False,
                attempts=0,
                total_duration=0.0,
                final_result=None,
                errors=[Exception("Circuit breaker is open")],
                retry_times=[],
            )

        # 通常のリトライ実行
        result = await self.retry_operation(
            operation, operation_name, config, *args, **kwargs
        )

        # サーキットブレーカーの状態更新
        self._update_circuit_breaker(operation_name, result.success)

        return result

    def _is_circuit_breaker_open(self, operation_name: str) -> bool:
        """サーキットブレーカーの状態チェック"""
        # 実装は簡略化（実際の実装では状態管理が必要）
        return False

    def _update_circuit_breaker(self, operation_name: str, success: bool):
        """サーキットブレーカーの状態更新"""
        # 実装は簡略化（実際の実装では状態管理が必要）
        pass


# デコレータ版のリトライシステム
def retry_on_failure(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
    condition: RetryCondition = RetryCondition.ALL_ERRORS,
):
    """リトライデコレータ"""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            retry_system = EnhancedAutoRetrySystem()
            config = RetryConfig(
                max_attempts=max_attempts,
                base_delay=base_delay,
                strategy=strategy,
                condition=condition,
            )

            return await retry_system.retry_operation(
                func, func.__name__, config, *args, **kwargs
            )

        return wrapper

    return decorator


# 使用例
async def main():
    """使用例"""
    retry_system = EnhancedAutoRetrySystem()

    # 例1: 基本的なリトライ
    async def unreliable_operation():
        if random.random() < 0.7:  # 70%の確率で失敗
            raise Exception("ランダムエラー")
        return "成功"

    result = await retry_system.retry_operation(
        unreliable_operation,
        "unreliable_operation",
        RetryConfig(max_attempts=5, base_delay=1.0, strategy=RetryStrategy.EXPONENTIAL),
    )

    print(f"結果: {result.success}")
    print(f"試行回数: {result.attempts}")
    print(f"総時間: {result.total_duration:.2f}秒")

    # 例2: デコレータを使用したリトライ
    @retry_on_failure(max_attempts=3, base_delay=2.0)
    async def another_operation():
        if random.random() < 0.5:
            raise Exception("デコレータエラー")
        return "デコレータ成功"

    result = await another_operation()
    print(f"デコレータ結果: {result.success}")


if __name__ == "__main__":
    asyncio.run(main())
