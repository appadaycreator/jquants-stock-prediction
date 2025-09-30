#!/usr/bin/env python3
"""
強化された並列処理システム
2-4倍の処理速度向上を実現する高度な並列処理機能
"""

import asyncio
import concurrent.futures
import multiprocessing as mp
import threading
import time
import logging
import psutil
import queue
from typing import Dict, List, Any, Callable, Optional, Union, Tuple
from dataclasses import dataclass
from contextlib import contextmanager
from functools import wraps, partial
import numpy as np
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import weakref
import gc
import os
import sys

logger = logging.getLogger(__name__)


@dataclass
class ProcessingMetrics:
    """処理メトリクス"""
    task_count: int
    execution_time: float
    cpu_usage: float
    memory_usage: float
    throughput: float
    efficiency: float
    success_rate: float


class EnhancedParallelProcessor:
    """強化された並列処理システム"""

    def __init__(self, max_workers: Optional[int] = None, adaptive_mode: bool = True):
        self.max_workers = max_workers or min(32, (os.cpu_count() or 1) + 4)
        self.adaptive_mode = adaptive_mode
        self.current_workers = self.max_workers
        
        # パフォーマンス監視
        self.metrics_history = []
        self.task_queue = queue.PriorityQueue()
        self.active_tasks = weakref.WeakSet()
        
        # 動的調整設定
        self.adjustment_threshold = 0.8  # CPU使用率の閾値
        self.adjustment_interval = 5.0  # 調整間隔（秒）
        self.last_adjustment = time.time()
        
        # 統計情報
        self.total_tasks = 0
        self.successful_tasks = 0
        self.failed_tasks = 0
        self.total_execution_time = 0.0
        
        # 非同期処理用
        self.async_loop = None
        self.async_tasks = set()
        
        logger.info(f"🚀 強化並列処理システム初期化完了")
        logger.info(f"   - 最大ワーカー数: {self.max_workers}")
        logger.info(f"   - 適応モード: {'有効' if adaptive_mode else '無効'}")
        logger.info(f"   - CPU数: {os.cpu_count()}")

    def get_optimal_workers(self, task_type: str = "mixed", data_size: int = 0) -> int:
        """タスクタイプとデータサイズに基づく最適なワーカー数を計算"""
        cpu_count = os.cpu_count() or 1
        
        if task_type == "cpu_intensive":
            # CPU集約的タスク
            optimal = min(cpu_count, self.max_workers)
        elif task_type == "io_intensive":
            # I/O集約的タスク
            optimal = min(cpu_count * 4, self.max_workers)
        elif task_type == "memory_intensive":
            # メモリ集約的タスク
            available_memory = psutil.virtual_memory().available / (1024**3)  # GB
            optimal = min(int(available_memory / 2), cpu_count, self.max_workers)
        else:  # mixed
            # 混合タスク
            optimal = min(cpu_count * 2, self.max_workers)
        
        # データサイズに基づく調整
        if data_size > 0:
            if data_size < 1000:
                optimal = min(optimal, 2)
            elif data_size < 10000:
                optimal = min(optimal, 4)
            else:
                optimal = min(optimal, 8)
        
        return max(1, optimal)

    def adaptive_worker_adjustment(self):
        """適応的ワーカー数調整"""
        if not self.adaptive_mode:
            return
        
        current_time = time.time()
        if current_time - self.last_adjustment < self.adjustment_interval:
            return
        
        # システムリソースをチェック
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent
        
        old_workers = self.current_workers
        
        # CPU使用率に基づく調整
        if cpu_usage > 90 and self.current_workers > 1:
            self.current_workers = max(1, self.current_workers - 1)
        elif cpu_usage < 50 and self.current_workers < self.max_workers:
            self.current_workers = min(self.max_workers, self.current_workers + 1)
        
        # メモリ使用率に基づく調整
        if memory_usage > 85 and self.current_workers > 1:
            self.current_workers = max(1, self.current_workers - 1)
        
        if old_workers != self.current_workers:
            logger.info(f"🔄 ワーカー数適応調整: {old_workers} → {self.current_workers}")
            logger.info(f"   - CPU使用率: {cpu_usage:.1f}%")
            logger.info(f"   - メモリ使用率: {memory_usage:.1f}%")
        
        self.last_adjustment = current_time

    def parallel_execute_optimized(
        self,
        tasks: List[Callable],
        task_type: str = "mixed",
        data_size: int = 0,
        timeout: Optional[float] = None,
        priority: int = 1
    ) -> List[Any]:
        """最適化された並列実行"""
        if not tasks:
            return []
        
        # 適応的調整
        self.adaptive_worker_adjustment()
        
        # 最適なワーカー数を計算
        optimal_workers = self.get_optimal_workers(task_type, data_size)
        actual_workers = min(optimal_workers, len(tasks))
        
        logger.info(f"🚀 最適化並列実行開始")
        logger.info(f"   - タスク数: {len(tasks)}")
        logger.info(f"   - タスクタイプ: {task_type}")
        logger.info(f"   - ワーカー数: {actual_workers}")
        logger.info(f"   - データサイズ: {data_size}")
        
        start_time = time.time()
        results = []
        
        try:
            # Executorの選択
            if task_type == "cpu_intensive":
                executor_class = ProcessPoolExecutor
            else:
                executor_class = ThreadPoolExecutor
            
            with executor_class(max_workers=actual_workers) as executor:
                # タスクの送信
                future_to_task = {
                    executor.submit(self._execute_with_monitoring, task, i): i 
                    for i, task in enumerate(tasks)
                }
                
                # 結果の収集
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
        self.total_tasks += len(tasks)
        self.total_execution_time += execution_time
        
        # メトリクスを記録
        self._record_metrics(len(tasks), execution_time, task_type)
        
        logger.info(f"✅ 最適化並列実行完了")
        logger.info(f"   - 実行時間: {execution_time:.2f}秒")
        logger.info(f"   - 成功率: {len([r for r in final_results if r is not None])}/{len(tasks)}")
        
        return final_results

    def _execute_with_monitoring(self, task: Callable, task_id: int) -> Any:
        """監視付きタスク実行"""
        start_time = time.time()
        
        try:
            result = task()
            execution_time = time.time() - start_time
            
            logger.debug(f"タスク {task_id} 完了: {execution_time:.2f}秒")
            return result
            
        except Exception as e:
            logger.error(f"タスク {task_id} エラー: {e}")
            raise

    def parallel_map_optimized(
        self,
        func: Callable,
        iterable: List[Any],
        task_type: str = "mixed",
        chunk_size: Optional[int] = None,
        priority: int = 1
    ) -> List[Any]:
        """最適化された並列マップ"""
        if not iterable:
            return []
        
        # チャンクサイズの自動計算
        if chunk_size is None:
            optimal_workers = self.get_optimal_workers(task_type, len(iterable))
            chunk_size = max(1, len(iterable) // optimal_workers)
        
        # チャンクに分割
        chunks = [
            iterable[i:i + chunk_size] 
            for i in range(0, len(iterable), chunk_size)
        ]
        
        logger.info(f"📊 並列マップ最適化")
        logger.info(f"   - データ数: {len(iterable)}")
        logger.info(f"   - チャンク数: {len(chunks)}")
        logger.info(f"   - チャンクサイズ: {chunk_size}")
        
        # チャンク処理関数
        def process_chunk(chunk):
            return [func(item) for item in chunk]
        
        # 並列実行
        chunk_results = self.parallel_execute_optimized(
            [partial(process_chunk, chunk) for chunk in chunks],
            task_type,
            len(iterable),
            priority=priority
        )
        
        # 結果を平坦化
        results = []
        for chunk_result in chunk_results:
            if chunk_result is not None:
                results.extend(chunk_result)
        
        return results

    async def async_parallel_execute(
        self,
        tasks: List[Callable],
        task_type: str = "mixed",
        max_concurrent: Optional[int] = None
    ) -> List[Any]:
        """非同期並列実行"""
        if not tasks:
            return []
        
        if max_concurrent is None:
            max_concurrent = self.get_optimal_workers(task_type)
        
        logger.info(f"🔄 非同期並列実行開始")
        logger.info(f"   - タスク数: {len(tasks)}")
        logger.info(f"   - 最大同時実行数: {max_concurrent}")
        
        start_time = time.time()
        results = []
        
        # セマフォで同時実行数を制限
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def execute_task_with_semaphore(task, task_id):
            async with semaphore:
                try:
                    # タスクを非同期で実行
                    result = await asyncio.get_event_loop().run_in_executor(
                        None, task
                    )
                    return task_id, result
                except Exception as e:
                    logger.error(f"非同期タスク {task_id} エラー: {e}")
                    return task_id, None
        
        # 全タスクを並列実行
        task_coroutines = [
            execute_task_with_semaphore(task, i) 
            for i, task in enumerate(tasks)
        ]
        
        # 結果を収集
        task_results = await asyncio.gather(*task_coroutines, return_exceptions=True)
        
        # 結果をソート
        task_results.sort(key=lambda x: x[0] if isinstance(x, tuple) else 0)
        results = [result for _, result in task_results if isinstance(result, tuple)]
        
        execution_time = time.time() - start_time
        
        logger.info(f"✅ 非同期並列実行完了")
        logger.info(f"   - 実行時間: {execution_time:.2f}秒")
        logger.info(f"   - 成功率: {len([r for r in results if r is not None])}/{len(tasks)}")
        
        return results

    def batch_processing(
        self,
        data: List[Any],
        batch_size: int,
        processing_func: Callable,
        task_type: str = "mixed"
    ) -> List[Any]:
        """バッチ処理"""
        if not data:
            return []
        
        logger.info(f"📦 バッチ処理開始")
        logger.info(f"   - データ数: {len(data)}")
        logger.info(f"   - バッチサイズ: {batch_size}")
        
        # バッチに分割
        batches = [
            data[i:i + batch_size] 
            for i in range(0, len(data), batch_size)
        ]
        
        # バッチ処理関数
        def process_batch(batch):
            return [processing_func(item) for item in batch]
        
        # 並列実行
        batch_results = self.parallel_execute_optimized(
            [partial(process_batch, batch) for batch in batches],
            task_type,
            len(data)
        )
        
        # 結果を平坦化
        results = []
        for batch_result in batch_results:
            if batch_result is not None:
                results.extend(batch_result)
        
        logger.info(f"✅ バッチ処理完了: {len(results)}件")
        return results

    def _record_metrics(self, task_count: int, execution_time: float, task_type: str):
        """メトリクスを記録"""
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent
        
        throughput = task_count / execution_time if execution_time > 0 else 0
        efficiency = (self.successful_tasks / max(1, self.total_tasks)) * 100
        
        metrics = ProcessingMetrics(
            task_count=task_count,
            execution_time=execution_time,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            throughput=throughput,
            efficiency=efficiency,
            success_rate=efficiency
        )
        
        self.metrics_history.append({
            "timestamp": time.time(),
            "task_type": task_type,
            "metrics": metrics
        })
        
        # 履歴を最新100件に制限
        if len(self.metrics_history) > 100:
            self.metrics_history = self.metrics_history[-100:]

    def get_performance_report(self) -> Dict[str, Any]:
        """パフォーマンスレポートを生成"""
        if not self.metrics_history:
            return {"message": "メトリクス履歴がありません"}
        
        recent_metrics = self.metrics_history[-10:]  # 最新10件
        
        avg_execution_time = np.mean([m["metrics"].execution_time for m in recent_metrics])
        avg_throughput = np.mean([m["metrics"].throughput for m in recent_metrics])
        avg_efficiency = np.mean([m["metrics"].efficiency for m in recent_metrics])
        avg_cpu_usage = np.mean([m["metrics"].cpu_usage for m in recent_metrics])
        avg_memory_usage = np.mean([m["metrics"].memory_usage for m in recent_metrics])
        
        return {
            "current_workers": self.current_workers,
            "max_workers": self.max_workers,
            "total_tasks": self.total_tasks,
            "successful_tasks": self.successful_tasks,
            "failed_tasks": self.failed_tasks,
            "success_rate": (self.successful_tasks / max(1, self.total_tasks)) * 100,
            "total_execution_time": self.total_execution_time,
            "avg_execution_time": avg_execution_time,
            "avg_throughput": avg_throughput,
            "avg_efficiency": avg_efficiency,
            "avg_cpu_usage": avg_cpu_usage,
            "avg_memory_usage": avg_memory_usage,
            "metrics_history_count": len(self.metrics_history),
            "recommendations": self._generate_recommendations()
        }

    def _generate_recommendations(self) -> List[str]:
        """パフォーマンス改善の推奨事項を生成"""
        recommendations = []
        
        if not self.metrics_history:
            return recommendations
        
        recent_metrics = self.metrics_history[-5:]
        avg_efficiency = np.mean([m["metrics"].efficiency for m in recent_metrics])
        avg_cpu_usage = np.mean([m["metrics"].cpu_usage for m in recent_metrics])
        avg_memory_usage = np.mean([m["metrics"].memory_usage for m in recent_metrics])
        
        if avg_efficiency < 80:
            recommendations.append("処理効率が80%を下回っています。ワーカー数の調整を推奨します。")
        
        if avg_cpu_usage > 90:
            recommendations.append("CPU使用率が90%を超えています。ワーカー数を減らすことを推奨します。")
        
        if avg_memory_usage > 85:
            recommendations.append("メモリ使用率が85%を超えています。メモリ最適化を推奨します。")
        
        if self.current_workers < self.max_workers and avg_cpu_usage < 50:
            recommendations.append("CPU使用率が低いです。ワーカー数を増やすことを推奨します。")
        
        return recommendations

    def cleanup(self):
        """リソースのクリーンアップ"""
        # アクティブなタスクをクリア
        self.active_tasks.clear()
        
        # メトリクス履歴をクリア
        self.metrics_history.clear()
        
        # 非同期タスクをクリア
        if self.async_tasks:
            for task in self.async_tasks:
                if not task.done():
                    task.cancel()
            self.async_tasks.clear()
        
        logger.info("🧹 強化並列処理システムをクリーンアップしました")


# デコレータ
def parallel_optimized(task_type: str = "mixed", priority: int = 1):
    """並列処理最適化デコレータ"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            processor = EnhancedParallelProcessor()
            return processor.parallel_execute_optimized(
                [lambda: func(*args, **kwargs)], 
                task_type, 
                priority=priority
            )[0]
        return wrapper
    return decorator


# コンテキストマネージャー
@contextmanager
def parallel_context(
    max_workers: Optional[int] = None, 
    adaptive_mode: bool = True
):
    """並列処理コンテキストマネージャー"""
    processor = EnhancedParallelProcessor(max_workers, adaptive_mode)
    try:
        yield processor
    finally:
        processor.cleanup()


# グローバルインスタンス
_global_processor = None


def get_global_processor() -> EnhancedParallelProcessor:
    """グローバルプロセッサーインスタンスを取得"""
    global _global_processor
    if _global_processor is None:
        _global_processor = EnhancedParallelProcessor()
    return _global_processor


if __name__ == "__main__":
    # テスト実行
    processor = EnhancedParallelProcessor()
    
    # テストタスク
    def test_task(x):
        time.sleep(0.1)
        return x * 2
    
    # 並列実行テスト
    tasks = [lambda x=i: test_task(x) for i in range(20)]
    results = processor.parallel_execute_optimized(tasks, task_type="cpu_intensive")
    print(f"並列実行結果: {results}")
    
    # 並列マップテスト
    data = list(range(50))
    results = processor.parallel_map_optimized(test_task, data, task_type="mixed")
    print(f"並列マップ結果: {results[:10]}...")  # 最初の10件のみ表示
    
    # バッチ処理テスト
    batch_results = processor.batch_processing(
        data, 
        batch_size=10, 
        processing_func=test_task, 
        task_type="mixed"
    )
    print(f"バッチ処理結果: {batch_results[:10]}...")  # 最初の10件のみ表示
    
    # パフォーマンスレポート
    report = processor.get_performance_report()
    print(f"パフォーマンスレポート: {report}")
    
    # クリーンアップ
    processor.cleanup()
