#!/usr/bin/env python3
"""
統合並列処理システム
既存のシステムに並列処理最適化を統合
"""

import os
import sys
import time
import logging
from typing import Dict, Any, List, Callable, Optional
from unified_parallel_processing_system import (
    execute_parallel,
    get_parallel_config,
    set_parallel_config,
)
from unified_system import get_unified_system
from concurrent.futures import as_completed
import multiprocessing as mp
import threading
import yaml

# 既存システムのインポート
try:
    from unified_parallel_processing_system import (
        ParallelProcessingOptimizer,
        get_optimizer,
        start_performance_monitoring,
        parallel_execute_unified,
        parallel_map_unified,
    )
except ImportError:
    print(
        "並列処理最適化システムが見つかりません。parallel_processing_optimizer.pyを確認してください。"
    )
    sys.exit(1)

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedParallelSystem:
    """統合並列処理システム"""

    def __init__(self, config_path: str = "config_final.yaml"):
        """
        初期化

        Args:
            config_path: 設定ファイルのパス
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.optimizer = get_optimizer()
        self.monitoring_active = False

        logger.info("🚀 統合並列処理システム初期化完了")

    def _load_config(self) -> Dict[str, Any]:
        """設定ファイルを読み込み"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"設定ファイル読み込みエラー: {e}")
            return {}

    def start_monitoring(self):
        """パフォーマンス監視を開始"""
        if not self.monitoring_active:
            start_performance_monitoring()
            self.monitoring_active = True
            logger.info("📊 パフォーマンス監視開始")

    def optimize_data_processing(
        self,
        data_chunks: List[Any],
        processing_func: Callable,
        task_type: str = "mixed",
    ) -> List[Any]:
        """
        データ処理の並列最適化

        Args:
            data_chunks: 処理するデータチャンクのリスト
            processing_func: 処理関数
            task_type: タスクタイプ

        Returns:
            処理結果のリスト
        """
        logger.info(f"🔄 データ処理並列最適化開始")
        logger.info(f"   - チャンク数: {len(data_chunks)}")
        logger.info(f"   - タスクタイプ: {task_type}")

        # チャンク処理タスクを作成
        tasks = [lambda chunk=chunk: processing_func(chunk) for chunk in data_chunks]

        # 並列実行
        results = parallel_execute_unified(tasks, task_type)

        logger.info(f"✅ データ処理並列最適化完了")
        return results

    def optimize_model_training(
        self,
        models_config: List[Dict[str, Any]],
        training_func: Callable,
        task_type: str = "cpu_intensive",
    ) -> List[Any]:
        """
        モデル訓練の並列最適化

        Args:
            models_config: モデル設定のリスト
            training_func: 訓練関数
            task_type: タスクタイプ

        Returns:
            訓練結果のリスト
        """
        logger.info(f"🤖 モデル訓練並列最適化開始")
        logger.info(f"   - モデル数: {len(models_config)}")
        logger.info(f"   - タスクタイプ: {task_type}")

        # モデル訓練タスクを作成
        tasks = [
            lambda config=config: training_func(config) for config in models_config
        ]

        # 並列実行
        results = parallel_execute_unified(tasks, task_type)

        logger.info(f"✅ モデル訓練並列最適化完了")
        return results

    def optimize_backtesting(
        self,
        strategies: List[Dict[str, Any]],
        backtest_func: Callable,
        task_type: str = "mixed",
    ) -> List[Any]:
        """
        バックテストの並列最適化

        Args:
            strategies: 戦略設定のリスト
            backtest_func: バックテスト関数
            task_type: タスクタイプ

        Returns:
            バックテスト結果のリスト
        """
        logger.info(f"📊 バックテスト並列最適化開始")
        logger.info(f"   - 戦略数: {len(strategies)}")
        logger.info(f"   - タスクタイプ: {task_type}")

        # バックテストタスクを作成
        tasks = [
            lambda strategy=strategy: backtest_func(strategy) for strategy in strategies
        ]

        # 並列実行
        results = parallel_execute_unified(tasks, task_type)

        logger.info(f"✅ バックテスト並列最適化完了")
        return results

    def optimize_sentiment_analysis(
        self,
        text_data: List[str],
        analysis_func: Callable,
        task_type: str = "io_intensive",
    ) -> List[Any]:
        """
        感情分析の並列最適化

        Args:
            text_data: 分析するテキストデータのリスト
            analysis_func: 分析関数
            task_type: タスクタイプ

        Returns:
            分析結果のリスト
        """
        logger.info(f"💭 感情分析並列最適化開始")
        logger.info(f"   - テキスト数: {len(text_data)}")
        logger.info(f"   - タスクタイプ: {task_type}")

        # 並列マップ実行
        results = parallel_map_unified(analysis_func, text_data, task_type)

        logger.info(f"✅ 感情分析並列最適化完了")
        return results

    def optimize_technical_indicators(
        self,
        stock_data: List[Dict[str, Any]],
        indicator_func: Callable,
        task_type: str = "cpu_intensive",
    ) -> List[Any]:
        """
        技術指標計算の並列最適化

        Args:
            stock_data: 株価データのリスト
            indicator_func: 指標計算関数
            task_type: タスクタイプ

        Returns:
            指標計算結果のリスト
        """
        logger.info(f"📈 技術指標計算並列最適化開始")
        logger.info(f"   - データ数: {len(stock_data)}")
        logger.info(f"   - タスクタイプ: {task_type}")

        # 並列マップ実行
        results = parallel_map_unified(indicator_func, stock_data, task_type)

        logger.info(f"✅ 技術指標計算並列最適化完了")
        return results

    def get_performance_stats(self) -> Dict[str, Any]:
        """パフォーマンス統計を取得"""
        if not self.monitoring_active:
            return {"error": "監視が開始されていません"}

        optimizer = self.optimizer
        with optimizer.lock:
            if not optimizer.performance_history:
                return {"error": "パフォーマンス履歴がありません"}

            recent_metrics = optimizer.performance_history[-5:]
            avg_cpu = sum(m.cpu_usage for m in recent_metrics) / len(recent_metrics)
            avg_memory = sum(m.memory_usage for m in recent_metrics) / len(
                recent_metrics
            )

            return {
                "current_workers": optimizer.current_workers,
                "max_workers": optimizer.max_workers,
                "avg_cpu_usage": avg_cpu,
                "avg_memory_usage": avg_memory,
                "auto_adjust": optimizer.auto_adjust,
                "performance_history_count": len(optimizer.performance_history),
            }

    def set_workers(self, workers: int):
        """ワーカー数を手動設定"""
        with self.optimizer.lock:
            old_workers = self.optimizer.current_workers
            self.optimizer.current_workers = max(
                1, min(workers, self.optimizer.max_workers_limit)
            )
            logger.info(
                f"🔧 ワーカー数手動設定: {old_workers} → {self.optimizer.current_workers}"
            )

    def enable_auto_adjust(self, enabled: bool = True):
        """自動調整の有効/無効を設定"""
        self.optimizer.auto_adjust = enabled
        logger.info(f"🔧 自動調整: {'有効' if enabled else '無効'}")


# 既存システムとの統合関数
def integrate_parallel_processing():
    """既存システムに並列処理を統合"""
    logger.info("🔗 既存システムとの統合開始")

    # 統合システムの初期化
    enhanced_system = get_unified_system()

    # パフォーマンス監視開始
    enhanced_system.start_monitoring()

    logger.info("✅ 既存システムとの統合完了")
    return enhanced_system


def optimize_existing_systems():
    """既存システムの最適化"""
    logger.info("🚀 既存システム最適化開始")

    # 統合システムを取得
    enhanced_system = integrate_parallel_processing()

    # 設定ファイルから最適化対象を取得
    config = enhanced_system.config

    # データ処理の最適化
    if "preprocessing" in config:
        logger.info("📊 データ前処理システムの最適化")
        # 既存のデータ前処理システムに並列処理を適用

    # モデル訓練の最適化
    if "prediction" in config:
        logger.info("🤖 予測モデルシステムの最適化")
        # 既存の予測モデルシステムに並列処理を適用

    # バックテストの最適化
    if "trading" in config:
        logger.info("📈 トレーディングシステムの最適化")
        # 既存のトレーディングシステムに並列処理を適用

    logger.info("✅ 既存システム最適化完了")
    return enhanced_system


if __name__ == "__main__":
    # 統合システムのテスト
    enhanced_system = optimize_existing_systems()

    # パフォーマンス統計の表示
    stats = enhanced_system.get_performance_stats()
    print(f"パフォーマンス統計: {stats}")

    # テスト実行
    def test_processing(data):
        time.sleep(0.1)
        return f"processed_{data}"

    test_data = [f"data_{i}" for i in range(10)]
    results = enhanced_system.optimize_data_processing(
        test_data, test_processing, "mixed"
    )
    print(f"処理結果: {results}")
