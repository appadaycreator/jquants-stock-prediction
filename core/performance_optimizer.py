#!/usr/bin/env python3
"""
パフォーマンス最適化システム
システム全体のパフォーマンスを監視・最適化
"""

import time
import psutil
import threading
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from collections import deque
import gc


class PerformanceOptimizer:
    """パフォーマンス最適化クラス"""

    def __init__(self, logger=None, error_handler=None):
        """初期化"""
        self.logger = logger
        self.error_handler = error_handler
        self.metrics_history = deque(maxlen=1000)  # 最新1000件のメトリクスを保持
        self.optimization_enabled = True
        self.monitoring_thread = None
        self.monitoring_active = False

    def start_monitoring(self, interval: int = 30):
        """パフォーマンス監視の開始"""
        try:
            if self.monitoring_active:
                if self.logger:
                    self.logger.log_info("パフォーマンス監視は既に開始されています")
                return

            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop, 
                args=(interval,), 
                daemon=True
            )
            self.monitoring_thread.start()

            if self.logger:
                self.logger.log_info(f"パフォーマンス監視を開始しました（間隔: {interval}秒）")

        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_system_error(e, "パフォーマンス監視開始")
            else:
                if self.logger:
                    self.logger.log_error(f"パフォーマンス監視開始エラー: {e}")
            raise

    def stop_monitoring(self):
        """パフォーマンス監視の停止"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)

        if self.logger:
            self.logger.log_info("パフォーマンス監視を停止しました")

    def _monitoring_loop(self, interval: int):
        """監視ループ"""
        while self.monitoring_active:
            try:
                metrics = self.collect_system_metrics()
                self.metrics_history.append(metrics)
                
                # パフォーマンス問題の検出
                self._detect_performance_issues(metrics)
                
                time.sleep(interval)
            except Exception as e:
                if self.logger:
                    self.logger.log_warning(f"監視ループエラー: {e}")
                time.sleep(interval)

    def collect_system_metrics(self) -> Dict[str, Any]:
        """システムメトリクスの収集"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # メモリ使用量
            memory = psutil.virtual_memory()
            
            # ディスク使用量
            disk = psutil.disk_usage('/')
            
            # プロセス情報
            process = psutil.Process()
            process_memory = process.memory_info()
            
            return {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": cpu_percent,
                "memory_total": memory.total,
                "memory_available": memory.available,
                "memory_percent": memory.percent,
                "disk_total": disk.total,
                "disk_used": disk.used,
                "disk_percent": (disk.used / disk.total) * 100,
                "process_memory_rss": process_memory.rss,
                "process_memory_vms": process_memory.vms,
                "process_cpu_percent": process.cpu_percent()
            }
        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_system_error(e, "メトリクス収集")
            return {"timestamp": datetime.now().isoformat(), "error": str(e)}

    def _detect_performance_issues(self, metrics: Dict[str, Any]):
        """パフォーマンス問題の検出"""
        try:
            issues = []

            # CPU使用率のチェック
            if metrics.get("cpu_percent", 0) > 90:
                issues.append(f"CPU使用率が高すぎます: {metrics['cpu_percent']:.1f}%")
                self._log_performance_warning("high_cpu", metrics['cpu_percent'], 90.0)

            # メモリ使用率のチェック
            if metrics.get("memory_percent", 0) > 90:
                issues.append(f"メモリ使用率が高すぎます: {metrics['memory_percent']:.1f}%")
                self._log_performance_warning("high_memory", metrics['memory_percent'], 90.0)

            # ディスク使用率のチェック
            if metrics.get("disk_percent", 0) > 90:
                issues.append(f"ディスク使用率が高すぎます: {metrics['disk_percent']:.1f}%")
                self._log_performance_warning("high_disk", metrics['disk_percent'], 90.0)

            if issues:
                if self.logger:
                    self.logger.log_warning(f"パフォーマンス問題を検出: {', '.join(issues)}")
                
                # 自動最適化の実行
                if self.optimization_enabled:
                    self._auto_optimize(issues)

        except Exception as e:
            if self.logger:
                self.logger.log_warning(f"パフォーマンス問題検出エラー: {e}")

    def _log_performance_warning(self, warning_type: str, value: float, threshold: float):
        """パフォーマンス警告ログ"""
        if self.logger:
            self.logger.log_warning(f"パフォーマンス警告: {warning_type} = {value:.1f}% (閾値: {threshold:.1f}%)")

    def _auto_optimize(self, issues: List[str]):
        """自動最適化の実行"""
        try:
            optimizations = []

            # メモリ最適化
            if any("メモリ" in issue for issue in issues):
                gc.collect()  # ガベージコレクション
                optimizations.append("ガベージコレクションを実行")

            # プロセス最適化
            if any("CPU" in issue for issue in issues):
                # プロセスの優先度調整（可能な場合）
                try:
                    process = psutil.Process()
                    process.nice(10)  # 優先度を下げる
                    optimizations.append("プロセス優先度を調整")
                except:
                    pass

            if optimizations:
                if self.logger:
                    self.logger.log_info(f"自動最適化を実行: {', '.join(optimizations)}")

        except Exception as e:
            if self.logger:
                self.logger.log_warning(f"自動最適化エラー: {e}")

    def get_performance_summary(self) -> Dict[str, Any]:
        """パフォーマンスサマリーの取得"""
        try:
            if not self.metrics_history:
                return {
                    "average_cpu": 0,
                    "average_memory": 0,
                    "average_disk": 0,
                    "total_metrics": 0
                }

            # 平均値の計算
            cpu_values = [m.get("cpu_percent", 0) for m in self.metrics_history if "cpu_percent" in m]
            memory_values = [m.get("memory_percent", 0) for m in self.metrics_history if "memory_percent" in m]
            disk_values = [m.get("disk_percent", 0) for m in self.metrics_history if "disk_percent" in m]

            return {
                "average_cpu": sum(cpu_values) / len(cpu_values) if cpu_values else 0,
                "average_memory": sum(memory_values) / len(memory_values) if memory_values else 0,
                "average_disk": sum(disk_values) / len(disk_values) if disk_values else 0,
                "total_metrics": len(self.metrics_history)
            }

        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_system_error(e, "パフォーマンスサマリー取得")
            return {"error": str(e)}

    def optimize_memory(self):
        """メモリ最適化"""
        try:
            # ガベージコレクション
            collected = gc.collect()
            
            if self.logger:
                self.logger.log_info(f"メモリ最適化完了: {collected}個のオブジェクトを回収")

            return {"collected_objects": collected, "timestamp": datetime.now().isoformat()}

        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_system_error(e, "メモリ最適化")
            return {"error": str(e)}

    def optimize_memory_usage(self):
        """メモリ使用量最適化（テスト互換性のため）"""
        return self.optimize_memory()

    def get_optimization_recommendations(self) -> List[str]:
        """最適化推奨事項の取得"""
        try:
            if not self.metrics_history:
                return ["メトリクス履歴が不足しています"]

            latest_metrics = self.metrics_history[-1]
            recommendations = []

            # CPU推奨事項
            if latest_metrics.get("cpu_percent", 0) > 80:
                recommendations.append("CPU使用率が高いです。処理の並列化を検討してください")

            # メモリ推奨事項
            if latest_metrics.get("memory_percent", 0) > 80:
                recommendations.append("メモリ使用率が高いです。データのバッチ処理を検討してください")

            # ディスク推奨事項
            if latest_metrics.get("disk_percent", 0) > 80:
                recommendations.append("ディスク使用率が高いです。古いログファイルの削除を検討してください")

            if not recommendations:
                recommendations.append("現在のパフォーマンスは良好です")

            return recommendations

        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_system_error(e, "推奨事項取得")
            return [f"推奨事項取得エラー: {str(e)}"]

    def reset_metrics(self):
        """メトリクス履歴のリセット"""
        self.metrics_history.clear()
        if self.logger:
            self.logger.log_info("パフォーマンスメトリクスをリセットしました")

    def get_system_info(self) -> Dict[str, Any]:
        """システム情報の取得"""
        try:
            return {
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "disk_total": psutil.disk_usage('/').total,
                "python_version": f"{psutil.sys.version_info.major}.{psutil.sys.version_info.minor}.{psutil.sys.version_info.micro}",
                "platform": psutil.sys.platform,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_system_error(e, "システム情報取得")
            return {"error": str(e)}