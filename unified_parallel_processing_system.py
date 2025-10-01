#!/usr/bin/env python3
"""
統合並列処理システム
分散した並列処理設定を統合し、一元管理するシステム
"""

import os
import sys
import time
import logging
import threading
import multiprocessing as mp
from typing import Dict, Any, List, Callable, Optional, Union
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from dataclasses import dataclass
import yaml
import psutil
from contextlib import contextmanager
from functools import wraps
import queue

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
    execution_time: float = 0.0


@dataclass
class TaskConfig:
    """タスク設定"""

    task_type: str  # "cpu_intensive", "io_intensive", "mixed"
    max_workers: int
    timeout: Optional[int] = None
    priority: int = 1  # 1=高, 2=中, 3=低


class UnifiedParallelProcessingSystem:
    """統合並列処理システム"""

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

        # パフォーマンス監視
        self.performance_history: List[PerformanceMetrics] = []
        self.lock = threading.Lock()
        self.monitoring_active = False
        self.monitor_thread = None

        # 動的調整設定
        self.auto_adjust = self.config.get("performance", {}).get("auto_adjust", True)
        self.adjustment_interval = self.config.get("performance", {}).get(
            "adjustment_interval", 30
        )
        self.min_workers = 1
        self.max_workers_limit = min(self.max_workers * 2, mp.cpu_count() * 2)

        # タスクキュー
        self.task_queue = queue.PriorityQueue()
        self.worker_threads = []

        # 統計情報
        self.total_tasks_executed = 0
        self.total_execution_time = 0.0
        self.successful_tasks = 0
        self.failed_tasks = 0

        logger.info("🚀 統合並列処理システム初期化完了")
        logger.info(f"   - 最大ワーカー数: {self.max_workers}")
        logger.info(f"   - 動的調整: {'有効' if self.auto_adjust else '無効'}")
        logger.info(f"   - CPU数: {mp.cpu_count()}")

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

    def start_monitoring(self):
        """パフォーマンス監視を開始"""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_performance, daemon=True
        )
        self.monitor_thread.start()
        logger.info("📊 パフォーマンス監視開始")

    def stop_monitoring(self):
        """パフォーマンス監視を停止"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("📊 パフォーマンス監視停止")

    def _monitor_performance(self):
        """パフォーマンス監視ループ"""
        while self.monitoring_active:
            try:
                metrics = self.get_performance_metrics()

                with self.lock:
                    self.performance_history.append(metrics)
                    # 履歴を最新20件に制限
                    if len(self.performance_history) > 20:
                        self.performance_history = self.performance_history[-20:]

                # 動的調整
                self.adjust_workers()

                time.sleep(self.adjustment_interval)

            except Exception as e:
                logger.error(f"パフォーマンス監視エラー: {e}")
                time.sleep(5)

    def get_optimal_executor(self, task_type: str = "mixed") -> tuple:
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

    def execute_parallel(
        self,
        tasks: List[Callable],
        task_type: str = "mixed",
        timeout: Optional[int] = None,
        priority: int = 1,
    ) -> List[Any]:
        """
        並列実行

        Args:
            tasks: 実行するタスクのリスト
            task_type: タスクタイプ
            timeout: タイムアウト（秒）
            priority: 優先度（1=高, 2=中, 3=低）

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
        logger.info(f"   - 優先度: {priority}")

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
                        self.successful_tasks += 1
                    except Exception as e:
                        task_index = future_to_task[future]
                        logger.error(f"タスク {task_index} 実行エラー: {e}")
                        results.append((task_index, None))
                        self.failed_tasks += 1

        except Exception as e:
            logger.error(f"並列実行エラー: {e}")
            return []

        # 結果を元の順序でソート
        results.sort(key=lambda x: x[0])
        final_results = [result for _, result in results]

        execution_time = time.time() - start_time
        self.total_tasks_executed += len(tasks)
        self.total_execution_time += execution_time

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
        priority: int = 1,
    ) -> List[Any]:
        """
        並列マップ実行

        Args:
            func: 実行する関数
            iterable: イテラブル
            task_type: タスクタイプ
            chunk_size: チャンクサイズ
            priority: 優先度

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
        chunk_results = self.execute_parallel(
            [lambda c=chunk: process_chunk(c) for chunk in chunks],
            task_type,
            priority=priority,
        )

        # 結果を平坦化
        results = []
        for chunk_result in chunk_results:
            if chunk_result is not None:
                results.extend(chunk_result)

        return results

    def get_system_stats(self) -> Dict[str, Any]:
        """システム統計を取得"""
        with self.lock:
            recent_metrics = (
                self.performance_history[-5:] if self.performance_history else []
            )

            stats = {
                "current_workers": self.current_workers,
                "max_workers": self.max_workers,
                "auto_adjust": self.auto_adjust,
                "monitoring_active": self.monitoring_active,
                "total_tasks_executed": self.total_tasks_executed,
                "successful_tasks": self.successful_tasks,
                "failed_tasks": self.failed_tasks,
                "total_execution_time": self.total_execution_time,
                "avg_execution_time": self.total_execution_time
                / max(1, self.total_tasks_executed),
                "success_rate": self.successful_tasks
                / max(1, self.total_tasks_executed)
                * 100,
            }

            if recent_metrics:
                stats.update(
                    {
                        "avg_cpu_usage": sum(m.cpu_usage for m in recent_metrics)
                        / len(recent_metrics),
                        "avg_memory_usage": sum(m.memory_usage for m in recent_metrics)
                        / len(recent_metrics),
                        "performance_history_count": len(self.performance_history),
                    }
                )

            return stats

    def set_workers(self, workers: int):
        """ワーカー数を手動設定"""
        with self.lock:
            old_workers = self.current_workers
            self.current_workers = max(1, min(workers, self.max_workers_limit))
            logger.info(
                f"🔧 ワーカー数手動設定: {old_workers} → {self.current_workers}"
            )

    def enable_auto_adjust(self, enabled: bool = True):
        """自動調整の有効/無効を設定"""
        self.auto_adjust = enabled
        logger.info(f"🔧 自動調整: {'有効' if enabled else '無効'}")

    def cleanup(self):
        """リソースをクリーンアップ"""
        self.stop_monitoring()
        logger.info("🧹 統合並列処理システムをクリーンアップしました")


# グローバルシステムインスタンス
_global_system = None


def get_unified_system() -> UnifiedParallelProcessingSystem:
    """グローバルシステムインスタンスを取得"""
    global _global_system
    if _global_system is None:
        _global_system = UnifiedParallelProcessingSystem()
        _global_system.start_monitoring()
    return _global_system


def parallel_execute_unified(
    tasks: List[Callable],
    task_type: str = "mixed",
    timeout: Optional[int] = None,
    priority: int = 1,
) -> List[Any]:
    """統合並列実行"""
    system = get_unified_system()
    return system.execute_parallel(tasks, task_type, timeout, priority)


def parallel_map_unified(
    func: Callable,
    iterable: List[Any],
    task_type: str = "mixed",
    chunk_size: Optional[int] = None,
    priority: int = 1,
) -> List[Any]:
    """統合並列マップ"""
    system = get_unified_system()
    return system.parallel_map(func, iterable, task_type, chunk_size, priority)


def parallel_optimized_decorator(task_type: str = "mixed", priority: int = 1):
    """並列処理最適化デコレータ"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            system = get_unified_system()
            return system.execute_parallel(
                [lambda: func(*args, **kwargs)], task_type, priority=priority
            )[0]

        return wrapper

    return decorator


@contextmanager
def parallel_context(task_type: str = "mixed", max_workers: Optional[int] = None):
    """並列処理コンテキストマネージャー"""
    system = get_unified_system()

    if max_workers:
        old_workers = system.current_workers
        system.set_workers(max_workers)

    try:
        yield system
    finally:
        if max_workers:
            system.set_workers(old_workers)


if __name__ == "__main__":
    # テスト実行
    system = get_unified_system()

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

    # 統計情報表示
    stats = system.get_system_stats()
    print(f"システム統計: {stats}")

    # クリーンアップ
    system.cleanup()
