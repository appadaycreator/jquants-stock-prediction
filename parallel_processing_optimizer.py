#!/usr/bin/env python3
"""
並列処理最適化システム
設定ファイルからmax_workersを読み込み、動的に並列処理を最適化
"""

import os
import sys
import time
import psutil
import logging
from typing import Dict, Any, Optional, List, Callable
from unified_parallel_processing_system import (
    execute_parallel,
    get_parallel_config,
    set_parallel_config
)
from unified_system import get_unified_system
from concurrent.futures import as_completed, ProcessPoolExecutor, ThreadPoolExecutor
from functools import wraps
import multiprocessing as mp
import threading
from dataclasses import dataclass
import yaml

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """パフォーマンス指標"""

    cpu_usage: float
    memory_usage: float
    active_threads: int
    active_processes: int
    timestamp: float


class ParallelProcessingOptimizer:
    """並列処理最適化クラス"""

    def __init__(self, config_path: str = "config_final.yaml"):
        """
        初期化

        Args:
            config_path: 設定ファイルのパス
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.max_workers = self._get_max_workers()
        self.current_workers = self.max_workers
        self.performance_history: List[PerformanceMetrics] = []
        self.lock = threading.Lock()

        # 動的調整設定
        self.auto_adjust = self.config.get("performance", {}).get("auto_adjust", True)
        self.adjustment_interval = self.config.get("performance", {}).get(
            "adjustment_interval", 30
        )
        self.min_workers = 1
        self.max_workers_limit = min(self.max_workers * 2, mp.cpu_count() * 2)

        logger.info(f"🚀 並列処理最適化システム初期化完了")
        logger.info(f"   - 最大ワーカー数: {self.max_workers}")
        logger.info(f"   - 動的調整: {'有効' if self.auto_adjust else '無効'}")

    def _load_config(self) -> Dict[str, Any]:
        """設定ファイルを読み込み"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"設定ファイル読み込みエラー: {e}")
            return {}

    def _get_max_workers(self) -> int:
        """設定から最大ワーカー数を取得"""
        try:
            # 環境別設定を優先
            environment = self.config.get("system", {}).get("environment", "production")
            env_config = self.config.get("environments", {}).get(environment, {})

            if (
                "performance" in env_config
                and "max_workers" in env_config["performance"]
            ):
                return env_config["performance"]["max_workers"]

            # デフォルト設定
            return self.config.get("performance", {}).get("max_workers", 4)
        except Exception as e:
            logger.warning(f"max_workers設定取得エラー: {e}")
            return min(4, mp.cpu_count())

    def get_performance_metrics(self) -> PerformanceMetrics:
        """現在のパフォーマンス指標を取得"""
        return PerformanceMetrics(
            cpu_usage=psutil.cpu_percent(interval=1),
            memory_usage=psutil.virtual_memory().percent,
            active_threads=threading.active_count(),
            active_processes=len(psutil.pids()),
            timestamp=time.time(),
        )

    def should_adjust_workers(self) -> bool:
        """ワーカー数を調整すべきか判定"""
        if not self.auto_adjust:
            return False

        with self.lock:
            if len(self.performance_history) < 5:
                return False

            recent_metrics = self.performance_history[-5:]
            avg_cpu = sum(m.cpu_usage for m in recent_metrics) / len(recent_metrics)
            avg_memory = sum(m.memory_usage for m in recent_metrics) / len(
                recent_metrics
            )

            # CPU使用率が高すぎる場合、ワーカー数を減らす
            if avg_cpu > 80 and self.current_workers > self.min_workers:
                return True

            # CPU使用率が低すぎる場合、ワーカー数を増やす
            if avg_cpu < 30 and self.current_workers < self.max_workers_limit:
                return True

            # メモリ使用率が高すぎる場合、ワーカー数を減らす
            if avg_memory > 85 and self.current_workers > self.min_workers:
                return True

        return False

    def adjust_workers(self):
        """ワーカー数を動的調整"""
        if not self.should_adjust_workers():
            return

        with self.lock:
            recent_metrics = self.performance_history[-5:]
            avg_cpu = sum(m.cpu_usage for m in recent_metrics) / len(recent_metrics)
            avg_memory = sum(m.memory_usage for m in recent_metrics) / len(
                recent_metrics
            )

            old_workers = self.current_workers

            # CPU使用率に基づく調整
            if avg_cpu > 80:
                self.current_workers = max(self.min_workers, self.current_workers - 1)
            elif avg_cpu < 30:
                self.current_workers = min(
                    self.max_workers_limit, self.current_workers + 1
                )

            # メモリ使用率に基づく調整
            if avg_memory > 85:
                self.current_workers = max(self.min_workers, self.current_workers - 1)

            if old_workers != self.current_workers:
                logger.info(
                    f"🔄 ワーカー数調整: {old_workers} → {self.current_workers}"
                )
                logger.info(f"   - CPU使用率: {avg_cpu:.1f}%")
                logger.info(f"   - メモリ使用率: {avg_memory:.1f}%")

    def monitor_performance(self):
        """パフォーマンス監視ループ"""
        while True:
            try:
                metrics = self.get_performance_metrics()

                with self.lock:
                    self.performance_history.append(metrics)
                    # 履歴を最新10件に制限
                    if len(self.performance_history) > 10:
                        self.performance_history = self.performance_history[-10:]

                # 動的調整
                self.adjust_workers()

                time.sleep(self.adjustment_interval)

            except Exception as e:
                logger.error(f"パフォーマンス監視エラー: {e}")
                time.sleep(5)

    def get_optimal_executor(self, task_type: str = "cpu_intensive") -> tuple:
        """
        タスクタイプに応じた最適なExecutorを取得

        Args:
            task_type: "cpu_intensive", "io_intensive", "mixed"

        Returns:
            (Executor, max_workers)
        """
        with self.lock:
            current_workers = self.current_workers

        if task_type == "cpu_intensive":
            # CPU集約的タスクはProcessPoolExecutor
            return ProcessPoolExecutor, min(current_workers, mp.cpu_count())
        elif task_type == "io_intensive":
            # I/O集約的タスクはThreadPoolExecutor
            return ThreadPoolExecutor, current_workers * 2
        else:  # mixed
            # 混合タスクはThreadPoolExecutor
            return ThreadPoolExecutor, current_workers

    def parallel_execute(
        self,
        tasks: List[Callable],
        task_type: str = "mixed",
        timeout: Optional[int] = None,
    ) -> List[Any]:
        """
        並列実行

        Args:
            tasks: 実行するタスクのリスト
            task_type: タスクタイプ
            timeout: タイムアウト（秒）

        Returns:
            実行結果のリスト
        """
        if not tasks:
            return []

        executor_class, max_workers = self.get_optimal_executor(task_type)

        logger.info(f"🚀 並列実行開始")
        logger.info(f"   - タスク数: {len(tasks)}")
        logger.info(f"   - タスクタイプ: {task_type}")
        logger.info(f"   - ワーカー数: {max_workers}")
        logger.info(f"   - Executor: {executor_class.__name__}")

        start_time = time.time()
        results = []

        try:
            with executor_class(max_workers=max_workers) as executor:
                # タスクを送信
                future_to_task = {
                    executor.submit(task): i for i, task in enumerate(tasks)
                }

                # 結果を収集
                for future in as_completed(future_to_task, timeout=timeout):
                    try:
                        result = future.result()
                        results.append((future_to_task[future], result))
                    except Exception as e:
                        task_index = future_to_task[future]
                        logger.error(f"タスク {task_index} 実行エラー: {e}")
                        results.append((task_index, None))

        except Exception as e:
            logger.error(f"並列実行エラー: {e}")
            return []

        # 結果を元の順序でソート
        results.sort(key=lambda x: x[0])
        final_results = [result for _, result in results]

        execution_time = time.time() - start_time
        logger.info(f"✅ 並列実行完了")
        logger.info(f"   - 実行時間: {execution_time:.2f}秒")
        logger.info(
            f"   - 成功率: {len([r for r in final_results if r is not None])}/{len(tasks)}"
        )

        return final_results

    def parallel_map(
        self,
        func: Callable,
        iterable: List[Any],
        task_type: str = "mixed",
        chunk_size: Optional[int] = None,
    ) -> List[Any]:
        """
        並列マップ実行

        Args:
            func: 実行する関数
            iterable: イテラブル
            task_type: タスクタイプ
            chunk_size: チャンクサイズ

        Returns:
            実行結果のリスト
        """
        if not iterable:
            return []

        # チャンクサイズの自動計算
        if chunk_size is None:
            executor_class, max_workers = self.get_optimal_executor(task_type)
            chunk_size = max(1, len(iterable) // max_workers)

        # チャンクに分割
        chunks = [
            iterable[i : i + chunk_size] for i in range(0, len(iterable), chunk_size)
        ]

        # チャンク処理関数
        def process_chunk(chunk):
            return [func(item) for item in chunk]

        # 並列実行
        chunk_results = self.parallel_execute(
            [lambda c=chunk: process_chunk(c) for chunk in chunks], task_type
        )

        # 結果を平坦化
        results = []
        for chunk_result in chunk_results:
            if chunk_result is not None:
                results.extend(chunk_result)

        return results


def parallel_optimized(func):
    """並列処理最適化デコレータ"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        # グローバルオプティマイザーを取得
        optimizer = getattr(parallel_optimized, "optimizer", None)
        if optimizer is None:
            optimizer = get_unified_system()
            parallel_optimized.optimizer = optimizer

        # タスクタイプを判定
        task_type = kwargs.get("task_type", "mixed")

        # 並列実行
        if hasattr(func, "__iter__"):
            return optimizer.parallel_execute(func, task_type)
        else:
            return optimizer.parallel_execute([func], task_type)[0]

    return wrapper


# グローバルオプティマイザー
_global_optimizer = None


def get_optimizer() -> ParallelProcessingOptimizer:
    """グローバルオプティマイザーを取得"""
    global _global_optimizer
    if _global_optimizer is None:
        _global_optimizer = get_unified_system()
    return _global_optimizer


def start_performance_monitoring():
    """パフォーマンス監視を開始"""
    optimizer = get_optimizer()
    monitor_thread = threading.Thread(target=optimizer.monitor_performance, daemon=True)
    monitor_thread.start()
    logger.info("📊 パフォーマンス監視開始")


def parallel_execute_unified(
    tasks: List[Callable], task_type: str = "mixed", timeout: Optional[int] = None
) -> List[Any]:
    """最適化された並列実行"""
    optimizer = get_optimizer()
    return optimizer.parallel_execute(tasks, task_type, timeout)


def parallel_map_unified(
    func: Callable,
    iterable: List[Any],
    task_type: str = "mixed",
    chunk_size: Optional[int] = None,
) -> List[Any]:
    """最適化された並列マップ"""
    optimizer = get_optimizer()
    return optimizer.parallel_map(func, iterable, task_type, chunk_size)


if __name__ == "__main__":
    # テスト実行
    optimizer = get_unified_system()

    # パフォーマンス監視開始
    start_performance_monitoring()

    # テストタスク
    def test_task(x):
        time.sleep(0.1)
        return x * 2

    # 並列実行テスト
    tasks = [lambda x=i: test_task(x) for i in range(10)]
    results = parallel_execute_unified(tasks, task_type="cpu_intensive")
    print(f"結果: {results}")

    # 並列マップテスト
    data = list(range(20))
    results = parallel_map_unified(test_task, data, task_type="mixed")
    print(f"マップ結果: {results}")
