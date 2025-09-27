#!/usr/bin/env python3
"""
高度な並列処理最適化システム
CPU使用率と処理速度を最適化する高度な機能を提供
"""

import os
import sys
import time
import logging
import threading
import multiprocessing as mp
from typing import Dict, Any, List, Callable, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from dataclasses import dataclass
import yaml
import psutil
import numpy as np
from queue import PriorityQueue
import gc
from contextlib import contextmanager
from functools import wraps
import tracemalloc

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class OptimizationMetrics:
    """最適化指標"""
    cpu_usage: float
    memory_usage: float
    execution_time: float
    throughput: float
    efficiency: float
    timestamp: float


@dataclass
class TaskProfile:
    """タスクプロファイル"""
    task_id: str
    task_type: str
    estimated_duration: float
    memory_requirement: float
    cpu_intensity: float
    priority: int
    dependencies: List[str] = None


class AdvancedParallelOptimizer:
    """高度な並列処理最適化クラス"""
    
    def __init__(self, config_path: str = "config_final.yaml"):
        """
        初期化
        
        Args:
            config_path: 設定ファイルのパス
        """
        self.config_path = config_path
        self.config = self._load_config()
        
        # システム情報
        self.cpu_count = mp.cpu_count()
        self.total_memory = psutil.virtual_memory().total
        self.max_workers = self._get_max_workers()
        
        # 最適化設定
        self.optimization_enabled = self.config.get("performance", {}).get("optimization", True)
        self.auto_scaling = self.config.get("performance", {}).get("auto_scaling", True)
        self.memory_threshold = self.config.get("performance", {}).get("memory_threshold", 0.8)
        self.cpu_threshold = self.config.get("performance", {}).get("cpu_threshold", 0.8)
        
        # パフォーマンス監視
        self.performance_history: List[OptimizationMetrics] = []
        self.task_profiles: Dict[str, TaskProfile] = {}
        self.optimization_lock = threading.Lock()
        
        # 動的調整
        self.current_workers = self.max_workers
        self.worker_adjustment_history = []
        self.optimization_interval = 10  # 10秒間隔
        
        # メモリ最適化
        self.memory_optimization_enabled = True
        self.gc_threshold = 0.9  # メモリ使用率90%でガベージコレクション
        
        # タスクキュー
        self.task_queue = PriorityQueue()
        self.worker_threads = []
        
        # 統計情報
        self.total_tasks_processed = 0
        self.total_execution_time = 0.0
        self.optimization_savings = 0.0
        
        logger.info("🚀 高度な並列処理最適化システム初期化完了")
        logger.info(f"   - CPU数: {self.cpu_count}")
        logger.info(f"   - 最大ワーカー数: {self.max_workers}")
        logger.info(f"   - 最適化: {'有効' if self.optimization_enabled else '無効'}")
        logger.info(f"   - 自動スケーリング: {'有効' if self.auto_scaling else '無効'}")
    
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
            environment = self.config.get("system", {}).get("environment", "production")
            env_config = self.config.get("environments", {}).get(environment, {})
            
            if "performance" in env_config and "max_workers" in env_config["performance"]:
                return env_config["performance"]["max_workers"]
            
            return self.config.get("performance", {}).get("max_workers", 4)
        except Exception as e:
            logger.warning(f"max_workers設定取得エラー: {e}")
            return min(4, mp.cpu_count())
    
    def get_system_metrics(self) -> OptimizationMetrics:
        """システム指標を取得"""
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent / 100
        
        # スループット計算（タスク/秒）
        if self.total_execution_time > 0:
            throughput = self.total_tasks_processed / self.total_execution_time
        else:
            throughput = 0.0
        
        # 効率性計算（CPU使用率に対するスループット）
        if cpu_usage > 0:
            efficiency = throughput / (cpu_usage / 100)
        else:
            efficiency = 0.0
        
        return OptimizationMetrics(
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            execution_time=self.total_execution_time,
            throughput=throughput,
            efficiency=efficiency,
            timestamp=time.time()
        )
    
    def optimize_worker_count(self) -> int:
        """ワーカー数を最適化"""
        if not self.auto_scaling:
            return self.current_workers
        
        with self.optimization_lock:
            metrics = self.get_system_metrics()
            
            # CPU使用率に基づく調整
            if metrics.cpu_usage > self.cpu_threshold * 100:
                # CPU使用率が高い場合、ワーカー数を減らす
                new_workers = max(1, self.current_workers - 1)
            elif metrics.cpu_usage < (self.cpu_threshold * 100) / 2:
                # CPU使用率が低い場合、ワーカー数を増やす
                new_workers = min(self.max_workers, self.current_workers + 1)
            else:
                new_workers = self.current_workers
            
            # メモリ使用率に基づく調整
            if metrics.memory_usage > self.memory_threshold:
                new_workers = max(1, new_workers - 1)
            
            # 効率性に基づく調整
            if len(self.performance_history) >= 3:
                recent_efficiency = [m.efficiency for m in self.performance_history[-3:]]
                avg_efficiency = np.mean(recent_efficiency)
                
                if avg_efficiency < 0.5:  # 効率性が低い場合
                    new_workers = max(1, new_workers - 1)
                elif avg_efficiency > 1.0:  # 効率性が高い場合
                    new_workers = min(self.max_workers, new_workers + 1)
            
            if new_workers != self.current_workers:
                old_workers = self.current_workers
                self.current_workers = new_workers
                self.worker_adjustment_history.append({
                    "timestamp": time.time(),
                    "old_workers": old_workers,
                    "new_workers": new_workers,
                    "cpu_usage": metrics.cpu_usage,
                    "memory_usage": metrics.memory_usage,
                    "efficiency": metrics.efficiency
                })
                
                logger.info(f"🔄 ワーカー数最適化: {old_workers} → {new_workers}")
                logger.info(f"   - CPU使用率: {metrics.cpu_usage:.1f}%")
                logger.info(f"   - メモリ使用率: {metrics.memory_usage:.1f}%")
                logger.info(f"   - 効率性: {metrics.efficiency:.2f}")
        
        return self.current_workers
    
    def optimize_memory_usage(self):
        """メモリ使用量を最適化"""
        if not self.memory_optimization_enabled:
            return
        
        current_memory = psutil.virtual_memory().percent / 100
        
        if current_memory > self.gc_threshold:
            logger.info("🧹 メモリ使用率が閾値を超過、ガベージコレクションを実行")
            gc.collect()
            
            # メモリ使用量を再チェック
            new_memory = psutil.virtual_memory().percent / 100
            logger.info(f"   - メモリ使用率: {current_memory:.1f}% → {new_memory:.1f}%")
    
    def profile_task(self, task_id: str, task_type: str, estimated_duration: float, 
                     memory_requirement: float, cpu_intensity: float, priority: int = 1):
        """タスクをプロファイル"""
        profile = TaskProfile(
            task_id=task_id,
            task_type=task_type,
            estimated_duration=estimated_duration,
            memory_requirement=memory_requirement,
            cpu_intensity=cpu_intensity,
            priority=priority
        )
        
        self.task_profiles[task_id] = profile
        logger.debug(f"📊 タスクプロファイル作成: {task_id}")
    
    def get_optimal_executor(self, task_type: str, task_profile: Optional[TaskProfile] = None) -> Tuple[type, int]:
        """最適なExecutorを取得"""
        optimized_workers = self.optimize_worker_count()
        
        if task_profile:
            # タスクプロファイルに基づく最適化
            if task_profile.cpu_intensity > 0.7:
                # CPU集約的タスク
                return ProcessPoolExecutor, min(optimized_workers, self.cpu_count)
            elif task_profile.memory_requirement > 0.5:
                # メモリ集約的タスク
                return ThreadPoolExecutor, max(1, optimized_workers // 2)
            else:
                # 混合タスク
                return ThreadPoolExecutor, optimized_workers
        else:
            # 従来の判定
            if task_type == "cpu_intensive":
                return ProcessPoolExecutor, min(optimized_workers, self.cpu_count)
            elif task_type == "io_intensive":
                return ThreadPoolExecutor, optimized_workers * 2
            else:
                return ThreadPoolExecutor, optimized_workers
    
    def execute_optimized_parallel(
        self,
        tasks: List[Callable],
        task_type: str = "mixed",
        timeout: Optional[int] = None,
        priority: int = 1,
        task_profiles: Optional[List[TaskProfile]] = None
    ) -> List[Any]:
        """最適化された並列実行"""
        if not tasks:
            return []
        
        start_time = time.time()
        
        # メモリ最適化
        self.optimize_memory_usage()
        
        # タスクプロファイルの適用
        if task_profiles:
            executor_class, max_workers = self.get_optimal_executor(task_type, task_profiles[0])
        else:
            executor_class, max_workers = self.get_optimal_executor(task_type)
        
        logger.info(f"🚀 最適化並列実行開始")
        logger.info(f"   - タスク数: {len(tasks)}")
        logger.info(f"   - タスクタイプ: {task_type}")
        logger.info(f"   - ワーカー数: {max_workers}")
        logger.info(f"   - Executor: {executor_class.__name__}")
        logger.info(f"   - 優先度: {priority}")
        
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
            logger.error(f"最適化並列実行エラー: {e}")
            return []
        
        # 結果を元の順序でソート
        results.sort(key=lambda x: x[0])
        final_results = [result for _, result in results]
        
        execution_time = time.time() - start_time
        self.total_tasks_processed += len(tasks)
        self.total_execution_time += execution_time
        
        # パフォーマンス指標を記録
        metrics = self.get_system_metrics()
        metrics.execution_time = execution_time
        self.performance_history.append(metrics)
        
        # 履歴を最新50件に制限
        if len(self.performance_history) > 50:
            self.performance_history = self.performance_history[-50:]
        
        logger.info(f"✅ 最適化並列実行完了")
        logger.info(f"   - 実行時間: {execution_time:.2f}秒")
        logger.info(f"   - スループット: {metrics.throughput:.2f} タスク/秒")
        logger.info(f"   - 効率性: {metrics.efficiency:.2f}")
        logger.info(f"   - 成功率: {len([r for r in final_results if r is not None])}/{len(tasks)}")
        
        return final_results
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """最適化統計を取得"""
        with self.optimization_lock:
            recent_metrics = self.performance_history[-10:] if self.performance_history else []
            
            stats = {
                "current_workers": self.current_workers,
                "max_workers": self.max_workers,
                "total_tasks_processed": self.total_tasks_processed,
                "total_execution_time": self.total_execution_time,
                "optimization_enabled": self.optimization_enabled,
                "auto_scaling": self.auto_scaling,
                "worker_adjustments": len(self.worker_adjustment_history),
                "task_profiles": len(self.task_profiles)
            }
            
            if recent_metrics:
                stats.update({
                    "avg_cpu_usage": np.mean([m.cpu_usage for m in recent_metrics]),
                    "avg_memory_usage": np.mean([m.memory_usage for m in recent_metrics]),
                    "avg_throughput": np.mean([m.throughput for m in recent_metrics]),
                    "avg_efficiency": np.mean([m.efficiency for m in recent_metrics]),
                    "performance_history_count": len(self.performance_history)
                })
            
            return stats
    
    def start_optimization_monitoring(self):
        """最適化監視を開始"""
        def monitor_worker():
            while True:
                try:
                    # パフォーマンス指標を記録
                    metrics = self.get_system_metrics()
                    self.performance_history.append(metrics)
                    
                    # 履歴を最新100件に制限
                    if len(self.performance_history) > 100:
                        self.performance_history = self.performance_history[-100:]
                    
                    # ワーカー数最適化
                    if self.auto_scaling:
                        self.optimize_worker_count()
                    
                    # メモリ最適化
                    self.optimize_memory_usage()
                    
                    time.sleep(self.optimization_interval)
                    
                except Exception as e:
                    logger.error(f"最適化監視エラー: {e}")
                    time.sleep(5)
        
        monitor_thread = threading.Thread(target=monitor_worker, daemon=True)
        monitor_thread.start()
        logger.info("📊 最適化監視開始")
    
    def create_optimization_report(self) -> Dict[str, Any]:
        """最適化レポートを作成"""
        stats = self.get_optimization_stats()
        
        report = {
            "system_info": {
                "cpu_count": self.cpu_count,
                "total_memory_gb": self.total_memory / (1024**3),
                "max_workers": self.max_workers,
                "current_workers": self.current_workers
            },
            "performance_metrics": stats,
            "optimization_settings": {
                "optimization_enabled": self.optimization_enabled,
                "auto_scaling": self.auto_scaling,
                "memory_threshold": self.memory_threshold,
                "cpu_threshold": self.cpu_threshold
            },
            "worker_adjustments": self.worker_adjustment_history[-10:],  # 最新10件
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """最適化推奨事項を生成"""
        recommendations = []
        
        if not self.optimization_enabled:
            recommendations.append("最適化機能を有効にすることを推奨します")
        
        if not self.auto_scaling:
            recommendations.append("自動スケーリング機能を有効にすることを推奨します")
        
        if self.performance_history:
            recent_metrics = self.performance_history[-5:]
            avg_cpu = np.mean([m.cpu_usage for m in recent_metrics])
            avg_memory = np.mean([m.memory_usage for m in recent_metrics])
            
            if avg_cpu > 80:
                recommendations.append("CPU使用率が高いため、ワーカー数を減らすことを検討してください")
            
            if avg_memory > 0.8:
                recommendations.append("メモリ使用率が高いため、メモリ最適化を検討してください")
            
            if len(self.performance_history) > 10:
                avg_efficiency = np.mean([m.efficiency for m in recent_metrics])
                if avg_efficiency < 0.5:
                    recommendations.append("効率性が低いため、タスクの分割や最適化を検討してください")
        
        return recommendations


# グローバル最適化システム
_global_optimizer = None


def get_advanced_optimizer() -> AdvancedParallelOptimizer:
    """グローバル最適化システムを取得"""
    global _global_optimizer
    if _global_optimizer is None:
        _global_optimizer = AdvancedParallelOptimizer()
        _global_optimizer.start_optimization_monitoring()
    return _global_optimizer


def execute_optimized_parallel(
    tasks: List[Callable],
    task_type: str = "mixed",
    timeout: Optional[int] = None,
    priority: int = 1,
    task_profiles: Optional[List[TaskProfile]] = None
) -> List[Any]:
    """最適化された並列実行"""
    optimizer = get_advanced_optimizer()
    return optimizer.execute_optimized_parallel(tasks, task_type, timeout, priority, task_profiles)


def advanced_parallel_decorator(task_type: str = "mixed", priority: int = 1):
    """高度な並列処理デコレータ"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            optimizer = get_advanced_optimizer()
            return optimizer.execute_optimized_parallel([lambda: func(*args, **kwargs)], task_type, priority=priority)[0]
        return wrapper
    return decorator


@contextmanager
def optimization_context(task_type: str = "mixed", max_workers: Optional[int] = None):
    """最適化コンテキストマネージャー"""
    optimizer = get_advanced_optimizer()
    
    if max_workers:
        old_workers = optimizer.current_workers
        optimizer.current_workers = max_workers
    
    try:
        yield optimizer
    finally:
        if max_workers:
            optimizer.current_workers = old_workers


if __name__ == "__main__":
    # テスト実行
    optimizer = get_advanced_optimizer()
    
    # テストタスク
    def test_task(x):
        time.sleep(0.1)
        return x * 2
    
    # 最適化並列実行テスト
    tasks = [lambda x=i: test_task(x) for i in range(10)]
    results = execute_optimized_parallel(tasks, task_type="cpu_intensive")
    print(f"結果: {results}")
    
    # 最適化統計表示
    stats = optimizer.get_optimization_stats()
    print(f"最適化統計: {stats}")
    
    # 最適化レポート作成
    report = optimizer.create_optimization_report()
    print(f"最適化レポート: {report}")
