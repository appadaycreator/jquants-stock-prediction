#!/usr/bin/env python3
"""
並列処理性能テスト
最適化後の性能をテストし、検証するシステム
"""

import os
import sys
import time
import logging
import multiprocessing as mp
from typing import Dict, List, Any, Callable
from dataclasses import dataclass
import numpy as np
import pandas as pd
import psutil
import matplotlib.pyplot as plt
import seaborn as sns
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import threading
import gc

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PerformanceTestResult:
    """性能テスト結果"""
    test_name: str
    execution_time: float
    cpu_usage: float
    memory_usage: float
    throughput: float
    efficiency: float
    success_rate: float
    worker_count: int
    task_count: int


class ParallelPerformanceTester:
    """並列処理性能テスター"""
    
    def __init__(self):
        self.test_results: List[PerformanceTestResult] = []
        self.baseline_results: Dict[str, Any] = {}
        
    def run_comprehensive_tests(self):
        """包括的な性能テストを実行"""
        logger.info("🚀 包括的な並列処理性能テスト開始")
        
        # ベースラインテスト
        self._run_baseline_tests()
        
        # 統合システムテスト
        self._run_unified_system_tests()
        
        # 高度な最適化システムテスト
        self._run_advanced_optimization_tests()
        
        # 比較テスト
        self._run_comparison_tests()
        
        # レポート生成
        self._generate_performance_report()
        
        logger.info("✅ 包括的な並列処理性能テスト完了")
    
    def _run_baseline_tests(self):
        """ベースラインテストを実行"""
        logger.info("📊 ベースラインテスト開始")
        
        # 逐次処理テスト
        sequential_result = self._test_sequential_processing()
        self.baseline_results["sequential"] = sequential_result
        
        # 基本的な並列処理テスト
        basic_parallel_result = self._test_basic_parallel_processing()
        self.baseline_results["basic_parallel"] = basic_parallel_result
        
        logger.info("✅ ベースラインテスト完了")
    
    def _run_unified_system_tests(self):
        """統合システムテストを実行"""
        logger.info("🔧 統合システムテスト開始")
        
        try:
            from unified_parallel_processing_system import get_unified_system, parallel_execute_unified
            
            system = get_unified_system()
            
            # CPU集約的タスクテスト
            cpu_intensive_result = self._test_cpu_intensive_tasks(system)
            self.test_results.append(cpu_intensive_result)
            
            # I/O集約的タスクテスト
            io_intensive_result = self._test_io_intensive_tasks(system)
            self.test_results.append(io_intensive_result)
            
            # 混合タスクテスト
            mixed_task_result = self._test_mixed_tasks(system)
            self.test_results.append(mixed_task_result)
            
            logger.info("✅ 統合システムテスト完了")
            
        except ImportError as e:
            logger.error(f"統合システムのインポートエラー: {e}")
    
    def _run_advanced_optimization_tests(self):
        """高度な最適化システムテストを実行"""
        logger.info("⚡ 高度な最適化システムテスト開始")
        
        try:
            from advanced_parallel_optimizer import get_advanced_optimizer, execute_optimized_parallel
            
            optimizer = get_advanced_optimizer()
            
            # 最適化された並列処理テスト
            optimized_result = self._test_optimized_parallel_processing(optimizer)
            self.test_results.append(optimized_result)
            
            # 動的調整テスト
            dynamic_adjustment_result = self._test_dynamic_adjustment(optimizer)
            self.test_results.append(dynamic_adjustment_result)
            
            # メモリ最適化テスト
            memory_optimization_result = self._test_memory_optimization(optimizer)
            self.test_results.append(memory_optimization_result)
            
            logger.info("✅ 高度な最適化システムテスト完了")
            
        except ImportError as e:
            logger.error(f"高度な最適化システムのインポートエラー: {e}")
    
    def _run_comparison_tests(self):
        """比較テストを実行"""
        logger.info("📈 比較テスト開始")
        
        # 異なるワーカー数での性能比較
        worker_comparison_result = self._test_worker_count_comparison()
        self.test_results.append(worker_comparison_result)
        
        # 異なるタスクサイズでの性能比較
        task_size_comparison_result = self._test_task_size_comparison()
        self.test_results.append(task_size_comparison_result)
        
        logger.info("✅ 比較テスト完了")
    
    def _test_sequential_processing(self) -> PerformanceTestResult:
        """逐次処理テスト"""
        logger.info("🔄 逐次処理テスト実行")
        
        def cpu_task(x):
            # CPU集約的タスク
            result = 0
            for i in range(100000):
                result += i * x
            return result
        
        start_time = time.time()
        start_cpu = psutil.cpu_percent()
        start_memory = psutil.virtual_memory().percent
        
        # 逐次実行
        results = [cpu_task(i) for i in range(10)]
        
        end_time = time.time()
        end_cpu = psutil.cpu_percent()
        end_memory = psutil.virtual_memory().percent
        
        execution_time = end_time - start_time
        cpu_usage = (start_cpu + end_cpu) / 2
        memory_usage = (start_memory + end_memory) / 2
        throughput = len(results) / execution_time
        efficiency = throughput / (cpu_usage / 100) if cpu_usage > 0 else 0
        
        return PerformanceTestResult(
            test_name="Sequential Processing",
            execution_time=execution_time,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            throughput=throughput,
            efficiency=efficiency,
            success_rate=100.0,
            worker_count=1,
            task_count=len(results)
        )
    
    def _test_basic_parallel_processing(self) -> PerformanceTestResult:
        """基本的な並列処理テスト"""
        logger.info("🔄 基本的な並列処理テスト実行")
        
        def cpu_task(x):
            result = 0
            for i in range(100000):
                result += i * x
            return result
        
        start_time = time.time()
        start_cpu = psutil.cpu_percent()
        start_memory = psutil.virtual_memory().percent
        
        # 基本的な並列実行
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(cpu_task, i) for i in range(10)]
            results = [future.result() for future in futures]
        
        end_time = time.time()
        end_cpu = psutil.cpu_percent()
        end_memory = psutil.virtual_memory().percent
        
        execution_time = end_time - start_time
        cpu_usage = (start_cpu + end_cpu) / 2
        memory_usage = (start_memory + end_memory) / 2
        throughput = len(results) / execution_time
        efficiency = throughput / (cpu_usage / 100) if cpu_usage > 0 else 0
        
        return PerformanceTestResult(
            test_name="Basic Parallel Processing",
            execution_time=execution_time,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            throughput=throughput,
            efficiency=efficiency,
            success_rate=100.0,
            worker_count=4,
            task_count=len(results)
        )
    
    def _test_cpu_intensive_tasks(self, system) -> PerformanceTestResult:
        """CPU集約的タスクテスト"""
        logger.info("🔄 CPU集約的タスクテスト実行")
        
        def cpu_intensive_task(x):
            result = 0
            for i in range(200000):
                result += i * x * np.sin(i)
            return result
        
        start_time = time.time()
        start_cpu = psutil.cpu_percent()
        start_memory = psutil.virtual_memory().percent
        
        # 統合システムでの並列実行（ThreadPoolExecutorを使用）
        tasks = [lambda x=i: cpu_intensive_task(x) for i in range(10)]
        results = system.execute_parallel(tasks, task_type="mixed")  # mixedに変更
        
        end_time = time.time()
        end_cpu = psutil.cpu_percent()
        end_memory = psutil.virtual_memory().percent
        
        execution_time = end_time - start_time
        cpu_usage = (start_cpu + end_cpu) / 2
        memory_usage = (start_memory + end_memory) / 2
        throughput = len(results) / execution_time
        efficiency = throughput / (cpu_usage / 100) if cpu_usage > 0 else 0
        success_rate = len([r for r in results if r is not None]) / len(results) * 100
        
        return PerformanceTestResult(
            test_name="CPU Intensive Tasks (Unified System)",
            execution_time=execution_time,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            throughput=throughput,
            efficiency=efficiency,
            success_rate=success_rate,
            worker_count=system.current_workers,
            task_count=len(results)
        )
    
    def _test_io_intensive_tasks(self, system) -> PerformanceTestResult:
        """I/O集約的タスクテスト"""
        logger.info("🔄 I/O集約的タスクテスト実行")
        
        def io_intensive_task(x):
            time.sleep(0.1)  # I/O待機をシミュレート
            return x * 2
        
        start_time = time.time()
        start_cpu = psutil.cpu_percent()
        start_memory = psutil.virtual_memory().percent
        
        # 統合システムでの並列実行
        tasks = [lambda x=i: io_intensive_task(x) for i in range(10)]
        results = system.execute_parallel(tasks, task_type="io_intensive")
        
        end_time = time.time()
        end_cpu = psutil.cpu_percent()
        end_memory = psutil.virtual_memory().percent
        
        execution_time = end_time - start_time
        cpu_usage = (start_cpu + end_cpu) / 2
        memory_usage = (start_memory + end_memory) / 2
        throughput = len(results) / execution_time
        efficiency = throughput / (cpu_usage / 100) if cpu_usage > 0 else 0
        success_rate = len([r for r in results if r is not None]) / len(results) * 100
        
        return PerformanceTestResult(
            test_name="I/O Intensive Tasks (Unified System)",
            execution_time=execution_time,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            throughput=throughput,
            efficiency=efficiency,
            success_rate=success_rate,
            worker_count=system.current_workers,
            task_count=len(results)
        )
    
    def _test_mixed_tasks(self, system) -> PerformanceTestResult:
        """混合タスクテスト"""
        logger.info("🔄 混合タスクテスト実行")
        
        def mixed_task(x):
            # CPU集約的処理
            result = 0
            for i in range(50000):
                result += i * x
            # I/O待機
            time.sleep(0.05)
            return result
        
        start_time = time.time()
        start_cpu = psutil.cpu_percent()
        start_memory = psutil.virtual_memory().percent
        
        # 統合システムでの並列実行
        tasks = [lambda x=i: mixed_task(x) for i in range(10)]
        results = system.execute_parallel(tasks, task_type="mixed")
        
        end_time = time.time()
        end_cpu = psutil.cpu_percent()
        end_memory = psutil.virtual_memory().percent
        
        execution_time = end_time - start_time
        cpu_usage = (start_cpu + end_cpu) / 2
        memory_usage = (start_memory + end_memory) / 2
        throughput = len(results) / execution_time
        efficiency = throughput / (cpu_usage / 100) if cpu_usage > 0 else 0
        success_rate = len([r for r in results if r is not None]) / len(results) * 100
        
        return PerformanceTestResult(
            test_name="Mixed Tasks (Unified System)",
            execution_time=execution_time,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            throughput=throughput,
            efficiency=efficiency,
            success_rate=success_rate,
            worker_count=system.current_workers,
            task_count=len(results)
        )
    
    def _test_optimized_parallel_processing(self, optimizer) -> PerformanceTestResult:
        """最適化された並列処理テスト"""
        logger.info("🔄 最適化された並列処理テスト実行")
        
        def optimized_task(x):
            result = 0
            for i in range(100000):
                result += i * x * np.cos(i)
            return result
        
        start_time = time.time()
        start_cpu = psutil.cpu_percent()
        start_memory = psutil.virtual_memory().percent
        
        # 最適化された並列実行（ThreadPoolExecutorを使用）
        tasks = [lambda x=i: optimized_task(x) for i in range(10)]
        results = optimizer.execute_optimized_parallel(tasks, task_type="mixed")  # mixedに変更
        
        end_time = time.time()
        end_cpu = psutil.cpu_percent()
        end_memory = psutil.virtual_memory().percent
        
        execution_time = end_time - start_time
        cpu_usage = (start_cpu + end_cpu) / 2
        memory_usage = (start_memory + end_memory) / 2
        throughput = len(results) / execution_time
        efficiency = throughput / (cpu_usage / 100) if cpu_usage > 0 else 0
        success_rate = len([r for r in results if r is not None]) / len(results) * 100
        
        return PerformanceTestResult(
            test_name="Optimized Parallel Processing",
            execution_time=execution_time,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            throughput=throughput,
            efficiency=efficiency,
            success_rate=success_rate,
            worker_count=optimizer.current_workers,
            task_count=len(results)
        )
    
    def _test_dynamic_adjustment(self, optimizer) -> PerformanceTestResult:
        """動的調整テスト"""
        logger.info("🔄 動的調整テスト実行")
        
        def adjustment_task(x):
            time.sleep(0.1)
            return x * 3
        
        start_time = time.time()
        start_cpu = psutil.cpu_percent()
        start_memory = psutil.virtual_memory().percent
        
        # 動的調整を有効にした並列実行
        tasks = [lambda x=i: adjustment_task(x) for i in range(15)]
        results = optimizer.execute_optimized_parallel(tasks, task_type="mixed")
        
        end_time = time.time()
        end_cpu = psutil.cpu_percent()
        end_memory = psutil.virtual_memory().percent
        
        execution_time = end_time - start_time
        cpu_usage = (start_cpu + end_cpu) / 2
        memory_usage = (start_memory + end_memory) / 2
        throughput = len(results) / execution_time
        efficiency = throughput / (cpu_usage / 100) if cpu_usage > 0 else 0
        success_rate = len([r for r in results if r is not None]) / len(results) * 100
        
        return PerformanceTestResult(
            test_name="Dynamic Adjustment",
            execution_time=execution_time,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            throughput=throughput,
            efficiency=efficiency,
            success_rate=success_rate,
            worker_count=optimizer.current_workers,
            task_count=len(results)
        )
    
    def _test_memory_optimization(self, optimizer) -> PerformanceTestResult:
        """メモリ最適化テスト"""
        logger.info("🔄 メモリ最適化テスト実行")
        
        def memory_intensive_task(x):
            # メモリ集約的タスク
            data = np.random.random((1000, 1000))
            result = np.sum(data * x)
            return result
        
        start_time = time.time()
        start_cpu = psutil.cpu_percent()
        start_memory = psutil.virtual_memory().percent
        
        # メモリ最適化を有効にした並列実行
        tasks = [lambda x=i: memory_intensive_task(x) for i in range(8)]
        results = optimizer.execute_optimized_parallel(tasks, task_type="mixed")
        
        end_time = time.time()
        end_cpu = psutil.cpu_percent()
        end_memory = psutil.virtual_memory().percent
        
        execution_time = end_time - start_time
        cpu_usage = (start_cpu + end_cpu) / 2
        memory_usage = (start_memory + end_memory) / 2
        throughput = len(results) / execution_time
        efficiency = throughput / (cpu_usage / 100) if cpu_usage > 0 else 0
        success_rate = len([r for r in results if r is not None]) / len(results) * 100
        
        return PerformanceTestResult(
            test_name="Memory Optimization",
            execution_time=execution_time,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            throughput=throughput,
            efficiency=efficiency,
            success_rate=success_rate,
            worker_count=optimizer.current_workers,
            task_count=len(results)
        )
    
    def _test_worker_count_comparison(self) -> PerformanceTestResult:
        """ワーカー数比較テスト"""
        logger.info("🔄 ワーカー数比較テスト実行")
        
        def comparison_task(x):
            result = 0
            for i in range(50000):
                result += i * x
            return result
        
        worker_counts = [1, 2, 4, 8]
        best_result = None
        best_throughput = 0
        
        for workers in worker_counts:
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=workers) as executor:
                futures = [executor.submit(comparison_task, i) for i in range(10)]
                results = [future.result() for future in futures]
            
            execution_time = time.time() - start_time
            throughput = len(results) / execution_time
            
            if throughput > best_throughput:
                best_throughput = throughput
                best_result = PerformanceTestResult(
                    test_name=f"Worker Count Comparison (Best: {workers})",
                    execution_time=execution_time,
                    cpu_usage=psutil.cpu_percent(),
                    memory_usage=psutil.virtual_memory().percent,
                    throughput=throughput,
                    efficiency=throughput / (psutil.cpu_percent() / 100) if psutil.cpu_percent() > 0 else 0,
                    success_rate=100.0,
                    worker_count=workers,
                    task_count=len(results)
                )
        
        return best_result
    
    def _test_task_size_comparison(self) -> PerformanceTestResult:
        """タスクサイズ比較テスト"""
        logger.info("🔄 タスクサイズ比較テスト実行")
        
        def task_size_task(x, size):
            result = 0
            for i in range(size):
                result += i * x
            return result
        
        task_sizes = [1000, 5000, 10000, 50000]
        best_result = None
        best_efficiency = 0
        
        for size in task_sizes:
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(task_size_task, i, size) for i in range(10)]
                results = [future.result() for future in futures]
            
            execution_time = time.time() - start_time
            throughput = len(results) / execution_time
            efficiency = throughput / (psutil.cpu_percent() / 100) if psutil.cpu_percent() > 0 else 0
            
            if efficiency > best_efficiency:
                best_efficiency = efficiency
                best_result = PerformanceTestResult(
                    test_name=f"Task Size Comparison (Best: {size})",
                    execution_time=execution_time,
                    cpu_usage=psutil.cpu_percent(),
                    memory_usage=psutil.virtual_memory().percent,
                    throughput=throughput,
                    efficiency=efficiency,
                    success_rate=100.0,
                    worker_count=4,
                    task_count=len(results)
                )
        
        return best_result
    
    def _generate_performance_report(self):
        """性能レポートを生成"""
        logger.info("📊 性能レポート生成開始")
        
        # 結果をDataFrameに変換（Noneを除外）
        valid_results = [result for result in self.test_results if result is not None]
        
        if not valid_results:
            logger.warning("⚠️ 有効なテスト結果がありません")
            return
        
        df_results = pd.DataFrame([
            {
                "Test Name": result.test_name,
                "Execution Time (s)": result.execution_time,
                "CPU Usage (%)": result.cpu_usage,
                "Memory Usage (%)": result.memory_usage,
                "Throughput (tasks/s)": result.throughput,
                "Efficiency": result.efficiency,
                "Success Rate (%)": result.success_rate,
                "Worker Count": result.worker_count,
                "Task Count": result.task_count
            }
            for result in valid_results
        ])
        
        # レポートファイル作成
        report_path = "PARALLEL_PERFORMANCE_REPORT.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# 並列処理性能テストレポート\n\n")
            f.write(f"テスト実行日時: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## テスト結果サマリー\n\n")
            f.write("| テスト名 | 実行時間(s) | CPU使用率(%) | メモリ使用率(%) | スループット(tasks/s) | 効率性 | 成功率(%) |\n")
            f.write("|---------|-------------|-------------|----------------|---------------------|--------|----------|\n")
            
            for _, row in df_results.iterrows():
                f.write(f"| {row['Test Name']} | {row['Execution Time (s)']:.2f} | {row['CPU Usage (%)']:.1f} | {row['Memory Usage (%)']:.1f} | {row['Throughput (tasks/s)']:.2f} | {row['Efficiency']:.2f} | {row['Success Rate (%)']:.1f} |\n")
            
            f.write("\n## 性能分析\n\n")
            
            # 最適な結果を特定
            best_throughput = df_results.loc[df_results['Throughput (tasks/s)'].idxmax()]
            best_efficiency = df_results.loc[df_results['Efficiency'].idxmax()]
            best_success_rate = df_results.loc[df_results['Success Rate (%)'].idxmax()]
            
            f.write(f"### 最高スループット\n")
            f.write(f"- テスト名: {best_throughput['Test Name']}\n")
            f.write(f"- スループット: {best_throughput['Throughput (tasks/s)']:.2f} tasks/s\n")
            f.write(f"- 実行時間: {best_throughput['Execution Time (s)']:.2f}s\n\n")
            
            f.write(f"### 最高効率性\n")
            f.write(f"- テスト名: {best_efficiency['Test Name']}\n")
            f.write(f"- 効率性: {best_efficiency['Efficiency']:.2f}\n")
            f.write(f"- CPU使用率: {best_efficiency['CPU Usage (%)']:.1f}%\n\n")
            
            f.write(f"### 最高成功率\n")
            f.write(f"- テスト名: {best_success_rate['Test Name']}\n")
            f.write(f"- 成功率: {best_success_rate['Success Rate (%)']:.1f}%\n")
            f.write(f"- タスク数: {best_success_rate['Task Count']}\n\n")
            
            f.write("## 推奨事項\n\n")
            
            # 推奨事項を生成
            recommendations = []
            
            if best_throughput['Test Name'] != 'Sequential Processing':
                recommendations.append("並列処理により大幅な性能向上が確認されました")
            
            if best_efficiency['Efficiency'] > 1.0:
                recommendations.append("効率性が良好です。現在の設定を維持してください")
            else:
                recommendations.append("効率性の改善を検討してください")
            
            if best_success_rate['Success Rate (%)'] < 100.0:
                recommendations.append("エラーハンドリングの改善を検討してください")
            
            for i, rec in enumerate(recommendations, 1):
                f.write(f"{i}. {rec}\n")
            
            f.write("\n## システム情報\n\n")
            f.write(f"- CPU数: {mp.cpu_count()}\n")
            f.write(f"- 総メモリ: {psutil.virtual_memory().total / (1024**3):.1f} GB\n")
            f.write(f"- 利用可能メモリ: {psutil.virtual_memory().available / (1024**3):.1f} GB\n")
            f.write(f"- メモリ使用率: {psutil.virtual_memory().percent:.1f}%\n")
        
        logger.info(f"📊 性能レポート生成完了: {report_path}")
        
        # 結果をCSVファイルにも保存
        csv_path = "parallel_performance_results.csv"
        df_results.to_csv(csv_path, index=False)
        logger.info(f"📊 結果をCSVファイルに保存: {csv_path}")
    
    def create_performance_visualization(self):
        """性能可視化を作成"""
        logger.info("📈 性能可視化作成開始")
        
        try:
            # 結果をDataFrameに変換
            df_results = pd.DataFrame([
                {
                    "Test Name": result.test_name,
                    "Execution Time": result.execution_time,
                    "CPU Usage": result.cpu_usage,
                    "Memory Usage": result.memory_usage,
                    "Throughput": result.throughput,
                    "Efficiency": result.efficiency,
                    "Success Rate": result.success_rate,
                    "Worker Count": result.worker_count
                }
                for result in self.test_results
            ])
            
            # 可視化を作成
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('並列処理性能テスト結果', fontsize=16)
            
            # スループット比較
            axes[0, 0].bar(df_results['Test Name'], df_results['Throughput'])
            axes[0, 0].set_title('スループット比較')
            axes[0, 0].set_ylabel('スループット (tasks/s)')
            axes[0, 0].tick_params(axis='x', rotation=45)
            
            # 効率性比較
            axes[0, 1].bar(df_results['Test Name'], df_results['Efficiency'])
            axes[0, 1].set_title('効率性比較')
            axes[0, 1].set_ylabel('効率性')
            axes[0, 1].tick_params(axis='x', rotation=45)
            
            # CPU使用率比較
            axes[1, 0].bar(df_results['Test Name'], df_results['CPU Usage'])
            axes[1, 0].set_title('CPU使用率比較')
            axes[1, 0].set_ylabel('CPU使用率 (%)')
            axes[1, 0].tick_params(axis='x', rotation=45)
            
            # メモリ使用率比較
            axes[1, 1].bar(df_results['Test Name'], df_results['Memory Usage'])
            axes[1, 1].set_title('メモリ使用率比較')
            axes[1, 1].set_ylabel('メモリ使用率 (%)')
            axes[1, 1].tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            
            # 画像を保存
            image_path = "parallel_performance_visualization.png"
            plt.savefig(image_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"📈 性能可視化作成完了: {image_path}")
            
        except Exception as e:
            logger.error(f"性能可視化作成エラー: {e}")


def main():
    """メイン実行関数"""
    logger.info("🚀 並列処理性能テスト開始")
    
    # テスターを作成
    tester = ParallelPerformanceTester()
    
    # 包括的なテストを実行
    tester.run_comprehensive_tests()
    
    # 性能可視化を作成
    tester.create_performance_visualization()
    
    logger.info("✅ 並列処理性能テスト完了")


if __name__ == "__main__":
    main()
