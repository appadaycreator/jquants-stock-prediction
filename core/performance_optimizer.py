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
                target=self._monitoring_loop, args=(interval,), daemon=True
            )
            self.monitoring_thread.start()

            if self.logger:
                self.logger.log_info(
                    f"パフォーマンス監視を開始しました（間隔: {interval}秒）"
                )

        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_system_error(e, "パフォーマンス監視開始")
            elif self.logger:
                self.logger.log_error(f"パフォーマンス監視開始エラー: {e}")
            else:
                raise

    def stop_monitoring(self):
        """パフォーマンス監視の停止"""
        self.monitoring_active = False
        if self.monitoring_thread:
            try:
                self.monitoring_thread.join(timeout=5)
            except Exception:
                # スレッド停止エラーは無視
                pass

        try:
            if self.logger:
                self.logger.log_info("パフォーマンス監視を停止しました")
        except Exception:
            # ロガーエラーは無視
            pass

    def _monitoring_loop(self, interval: int):
        """監視ループ"""
        while self.monitoring_active:
            try:
                metrics = self.collect_system_metrics()
                self.metrics_history.append(metrics)

                # パフォーマンス問題の検出
                self._detect_performance_issues(metrics)

                time.sleep(interval)
            except KeyboardInterrupt:
                # キーボード割り込みの場合は正常終了
                break
            except Exception as e:
                if self.logger:
                    self.logger.log_warning(f"監視ループエラー: {e}")
                # エラー時は短い間隔でリトライ
                try:
                    time.sleep(min(interval, 5))
                except Exception:
                    break

    def collect_system_metrics(self) -> Dict[str, Any]:
        """システムメトリクスの収集"""
        metrics = {"timestamp": datetime.now().isoformat()}

        try:
            # CPU使用率（interval=0で即座に取得）
            cpu_percent = psutil.cpu_percent(interval=0)
            metrics["cpu_percent"] = cpu_percent
        except Exception:
            metrics["cpu_percent"] = 0.0

        try:
            # メモリ使用量
            memory = psutil.virtual_memory()
            metrics.update(
                {
                    "memory_total": memory.total,
                    "memory_available": memory.available,
                    "memory_percent": memory.percent,
                }
            )
        except Exception:
            metrics.update(
                {"memory_total": 0, "memory_available": 0, "memory_percent": 0.0}
            )

        try:
            # ディスク使用量
            disk = psutil.disk_usage("/")
            metrics.update(
                {
                    "disk_total": disk.total,
                    "disk_used": disk.used,
                    "disk_percent": (disk.used / disk.total) * 100,
                }
            )
        except Exception:
            metrics.update({"disk_total": 0, "disk_used": 0, "disk_percent": 0.0})

        try:
            # プロセス情報
            process = psutil.Process()
            process_memory = process.memory_info()
            metrics.update(
                {
                    "process_memory_rss": process_memory.rss,
                    "process_memory_vms": process_memory.vms,
                    "process_cpu_percent": process.cpu_percent(),
                }
            )
        except Exception:
            metrics.update(
                {
                    "process_memory_rss": 0,
                    "process_memory_vms": 0,
                    "process_cpu_percent": 0.0,
                }
            )

        return metrics

    def _detect_performance_issues(self, metrics: Dict[str, Any]):
        """パフォーマンス問題の検出"""
        try:
            issues = self._check_resource_usage(metrics)

            if issues:
                self._log_performance_issues(issues)
                self._execute_auto_optimization(issues)

        except Exception as e:
            if self.logger:
                self.logger.log_warning(f"パフォーマンス問題検出エラー: {e}")

    def _check_resource_usage(self, metrics: Dict[str, Any]) -> List[str]:
        """リソース使用量のチェック"""
        issues = []
        thresholds = {"cpu": 90, "memory": 90, "disk": 90}

        # CPU使用率のチェック
        cpu_percent = metrics.get("cpu_percent", 0)
        if cpu_percent > thresholds["cpu"]:
            issues.append(f"CPU使用率が高すぎます: {cpu_percent:.1f}%")
            self._log_performance_warning("high_cpu", cpu_percent, thresholds["cpu"])

        # メモリ使用率のチェック
        memory_percent = metrics.get("memory_percent", 0)
        if memory_percent > thresholds["memory"]:
            issues.append(f"メモリ使用率が高すぎます: {memory_percent:.1f}%")
            self._log_performance_warning(
                "high_memory", memory_percent, thresholds["memory"]
            )

        # ディスク使用率のチェック
        disk_percent = metrics.get("disk_percent", 0)
        if disk_percent > thresholds["disk"]:
            issues.append(f"ディスク使用率が高すぎます: {disk_percent:.1f}%")
            self._log_performance_warning("high_disk", disk_percent, thresholds["disk"])

        return issues

    def _log_performance_issues(self, issues: List[str]) -> None:
        """パフォーマンス問題のログ出力"""
        if self.logger:
            self.logger.log_warning(f"パフォーマンス問題を検出: {', '.join(issues)}")

    def _execute_auto_optimization(self, issues: List[str]) -> None:
        """自動最適化の実行"""
        if not self.optimization_enabled:
            return

        for issue in issues:
            if "CPU使用率" in issue:
                self._optimize_cpu_usage()
            elif "メモリ使用率" in issue:
                self._optimize_memory_usage()
            elif "ディスク使用率" in issue:
                self._optimize_disk_usage()

    def _optimize_cpu_usage(self) -> None:
        """CPU使用率の最適化"""
        try:
            # ガベージコレクションの実行
            gc.collect()

            if self.logger:
                self.logger.log_info("CPU使用率最適化を実行しました")
        except Exception as e:
            if self.logger:
                self.logger.log_error(f"CPU最適化エラー: {e}")

    def _optimize_memory_usage(self) -> None:
        """メモリ使用率の最適化"""
        try:
            # ガベージコレクションの実行
            gc.collect()

            if self.logger:
                self.logger.log_info("メモリ使用率最適化を実行しました")
        except Exception as e:
            if self.logger:
                self.logger.log_error(f"メモリ最適化エラー: {e}")

    def _optimize_disk_usage(self) -> None:
        """ディスク使用率の最適化"""
        try:
            # 一時ファイルのクリーンアップ
            import tempfile
            import os

            temp_dir = tempfile.gettempdir()
            for file in os.listdir(temp_dir):
                if file.startswith("tmp") and os.path.isfile(
                    os.path.join(temp_dir, file)
                ):
                    try:
                        os.remove(os.path.join(temp_dir, file))
                    except:
                        pass

            if self.logger:
                self.logger.log_info("ディスク使用率最適化を実行しました")
        except Exception as e:
            if self.logger:
                self.logger.log_error(f"ディスク最適化エラー: {e}")

    # 旧実装の重複 _auto_optimize は削除し、後段の包括版に統一

    def _log_performance_warning(
        self, warning_type: str, value: float, threshold: float
    ):
        """パフォーマンス警告ログ"""
        try:
            if self.logger:
                self.logger.log_warning(
                    f"パフォーマンス警告: {warning_type} = {value:.1f}% (閾値: {threshold:.1f}%)"
                )
        except Exception:
            # ロガーエラーが発生しても処理を継続
            pass

    def _auto_optimize(self, issue_type: str):
        """自動最適化の実行"""
        try:
            optimizations = []

            # メモリ最適化
            if issue_type == "memory_cleanup" or "メモリ" in str(issue_type):
                gc.collect()  # ガベージコレクション
                optimizations.append("ガベージコレクションを実行")

            # プロセス最適化
            if issue_type == "cpu_optimization" or "CPU" in str(issue_type):
                # プロセスの優先度調整（可能な場合）
                try:
                    process = psutil.Process()
                    process.nice(10)  # 優先度を下げる
                    optimizations.append("プロセス優先度を調整")
                except:
                    pass

            # 未知の問題の場合
            if issue_type == "unknown_issue":
                self._log_performance_warning("unknown_issue", 0.0, 0.0)

            if optimizations:
                if self.logger:
                    self.logger.log_info(
                        f"自動最適化を実行: {', '.join(optimizations)}"
                    )

        except Exception as e:
            if self.logger:
                self.logger.log_warning(f"自動最適化エラー: {e}")
            else:
                # ロガーが利用できない場合の警告
                self._log_performance_warning("optimization_error", 0.0, 0.0)

    def get_performance_summary(self) -> Dict[str, Any]:
        """パフォーマンスサマリーの取得"""
        try:
            if not self.metrics_history:
                return {
                    "average_cpu": 0,
                    "average_memory": 0,
                    "average_disk": 0,
                    "total_metrics": 0,
                }

            # 平均値の計算（数値のみを対象）
            cpu_values = []
            memory_values = []
            disk_values = []

            for m in self.metrics_history:
                if "cpu_percent" in m and isinstance(m["cpu_percent"], (int, float)):
                    cpu_values.append(m["cpu_percent"])
                if "memory_percent" in m and isinstance(
                    m["memory_percent"], (int, float)
                ):
                    memory_values.append(m["memory_percent"])
                if "disk_percent" in m and isinstance(m["disk_percent"], (int, float)):
                    disk_values.append(m["disk_percent"])

            return {
                "average_cpu": sum(cpu_values) / len(cpu_values) if cpu_values else 0,
                "average_memory": (
                    sum(memory_values) / len(memory_values) if memory_values else 0
                ),
                "average_disk": (
                    sum(disk_values) / len(disk_values) if disk_values else 0
                ),
                "total_metrics": len(self.metrics_history),
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
                self.logger.log_info(
                    f"メモリ最適化完了: {collected}個のオブジェクトを回収"
                )

            return {
                "collected_objects": collected,
                "timestamp": datetime.now().isoformat(),
            }

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
                recommendations.append(
                    "CPU使用率が高いです。処理の並列化を検討してください"
                )

            # メモリ推奨事項
            if latest_metrics.get("memory_percent", 0) > 80:
                recommendations.append(
                    "メモリ使用率が高いです。データのバッチ処理を検討してください"
                )

            # ディスク推奨事項
            if latest_metrics.get("disk_percent", 0) > 80:
                recommendations.append(
                    "ディスク使用率が高いです。古いログファイルの削除を検討してください"
                )

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
                "disk_total": psutil.disk_usage("/").total,
                "python_version": f"{psutil.sys.version_info.major}.{psutil.sys.version_info.minor}.{psutil.sys.version_info.micro}",
                "platform": psutil.sys.platform,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_system_error(e, "システム情報取得")
            return {"error": str(e)}
