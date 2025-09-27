#!/usr/bin/env python3
"""
メモリ最適化効果測定テスト
AdvancedMemoryOptimizerの統合システムへの適用効果を検証
"""

import pandas as pd
import numpy as np
import time
import psutil
import gc
from typing import Dict, Any
import logging
from unified_system import UnifiedSystem

# ログ設定
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MemoryOptimizationTester:
    """メモリ最適化効果測定クラス"""

    def __init__(self):
        self.system = UnifiedSystem("MemoryOptimizationTester")
        self.results = {}

    def create_test_dataframe(self, rows: int = 100000, cols: int = 50) -> pd.DataFrame:
        """テスト用データフレームの作成"""
        logger.info(f"📊 テストデータフレーム作成: {rows}行 x {cols}列")

        # 大規模データフレームの作成
        data = {f"col_{i}": np.random.randn(rows) for i in range(cols)}

        # 意図的に非効率なデータ型を使用
        df = pd.DataFrame(data)

        # データ型を非効率に設定
        for col in df.columns:
            if col.startswith("col_") and int(col.split("_")[1]) % 2 == 0:
                df[col] = df[col].astype("float64")
            else:
                df[col] = df[col].astype("int64")

        logger.info(f"✅ テストデータフレーム作成完了: {df.shape}")
        return df

    def measure_memory_usage(self, df: pd.DataFrame, operation: str) -> Dict[str, Any]:
        """メモリ使用量の測定"""
        # ガベージコレクション実行
        gc.collect()

        # メモリ使用量の取得
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024

        # データフレームのメモリ使用量
        df_memory_mb = df.memory_usage(deep=True).sum() / 1024 / 1024

        return {
            "operation": operation,
            "total_memory_mb": memory_mb,
            "dataframe_memory_mb": df_memory_mb,
            "timestamp": time.time(),
        }

    def test_memory_optimization_effectiveness(self):
        """メモリ最適化の効果測定テスト"""
        logger.info("🚀 メモリ最適化効果測定テスト開始")

        # テストデータの作成
        test_df = self.create_test_dataframe(rows=50000, cols=30)

        # 最適化前のメモリ使用量測定
        before_metrics = self.measure_memory_usage(test_df, "before_optimization")
        logger.info(
            f"📊 最適化前メモリ使用量: {before_metrics['total_memory_mb']:.1f}MB"
        )
        logger.info(
            f"📊 データフレームメモリ使用量: {before_metrics['dataframe_memory_mb']:.1f}MB"
        )

        # 統合システムによるメモリ最適化
        logger.info("🔧 統合システムによるメモリ最適化実行")
        optimized_df = self.system.auto_apply_memory_optimization(test_df)

        # 最適化後のメモリ使用量測定
        after_metrics = self.measure_memory_usage(optimized_df, "after_optimization")
        logger.info(
            f"📊 最適化後メモリ使用量: {after_metrics['total_memory_mb']:.1f}MB"
        )
        logger.info(
            f"📊 データフレームメモリ使用量: {after_metrics['dataframe_memory_mb']:.1f}MB"
        )

        # 効果の計算
        total_memory_saved = (
            before_metrics["total_memory_mb"] - after_metrics["total_memory_mb"]
        )
        df_memory_saved = (
            before_metrics["dataframe_memory_mb"] - after_metrics["dataframe_memory_mb"]
        )

        # パーセンテージ計算
        total_memory_reduction_percent = (
            total_memory_saved / before_metrics["total_memory_mb"]
        ) * 100
        df_memory_reduction_percent = (
            df_memory_saved / before_metrics["dataframe_memory_mb"]
        ) * 100

        # 結果の記録
        self.results["memory_optimization"] = {
            "before_total_memory_mb": before_metrics["total_memory_mb"],
            "after_total_memory_mb": after_metrics["total_memory_mb"],
            "total_memory_saved_mb": total_memory_saved,
            "total_memory_reduction_percent": total_memory_reduction_percent,
            "before_df_memory_mb": before_metrics["dataframe_memory_mb"],
            "after_df_memory_mb": after_metrics["dataframe_memory_mb"],
            "df_memory_saved_mb": df_memory_saved,
            "df_memory_reduction_percent": df_memory_reduction_percent,
        }

        # 結果の表示
        logger.info("🎉 メモリ最適化効果測定結果:")
        logger.info(
            f"  💾 総メモリ節約: {total_memory_saved:.1f}MB ({total_memory_reduction_percent:.1f}%)"
        )
        logger.info(
            f"  📊 データフレームメモリ節約: {df_memory_saved:.1f}MB ({df_memory_reduction_percent:.1f}%)"
        )

        return self.results["memory_optimization"]

    def test_large_dataset_processing(self):
        """大規模データセット処理テスト"""
        logger.info("🚀 大規模データセット処理テスト開始")

        # より大きなデータセットの作成
        large_df = self.create_test_dataframe(rows=200000, cols=50)

        # 処理前のメモリ使用量
        before_metrics = self.measure_memory_usage(large_df, "before_large_processing")

        # 統合システムによるデータ処理最適化
        logger.info("🔧 統合システムによる大規模データ処理最適化実行")
        optimized_df = self.system.optimize_data_processing(large_df)

        # 処理後のメモリ使用量
        after_metrics = self.measure_memory_usage(
            optimized_df, "after_large_processing"
        )

        # 効果の計算
        memory_saved = (
            before_metrics["total_memory_mb"] - after_metrics["total_memory_mb"]
        )
        memory_reduction_percent = (
            memory_saved / before_metrics["total_memory_mb"]
        ) * 100

        # 結果の記録
        self.results["large_dataset_processing"] = {
            "before_memory_mb": before_metrics["total_memory_mb"],
            "after_memory_mb": after_metrics["total_memory_mb"],
            "memory_saved_mb": memory_saved,
            "memory_reduction_percent": memory_reduction_percent,
            "data_rows": len(large_df),
            "data_cols": len(large_df.columns),
        }

        logger.info("🎉 大規模データセット処理結果:")
        logger.info(
            f"  💾 メモリ節約: {memory_saved:.1f}MB ({memory_reduction_percent:.1f}%)"
        )
        logger.info(f"  📊 処理データ: {len(large_df)}行 x {len(large_df.columns)}列")

        return self.results["large_dataset_processing"]

    def test_memory_limit_handling(self):
        """メモリ制限処理テスト"""
        logger.info("🚀 メモリ制限処理テスト開始")

        # メモリ制限を低く設定してテスト
        if self.system.memory_optimizer:
            original_limit = self.system.memory_optimizer.memory_limit_mb
            self.system.memory_optimizer.memory_limit_mb = 100  # 100MBに制限

            try:
                # 大きなデータセットの処理
                test_df = self.create_test_dataframe(rows=100000, cols=20)

                # メモリ制限チェック
                is_within_limit = self.system.memory_optimizer.check_memory_limit()
                logger.info(
                    f"📊 メモリ制限チェック: {'✅ 制限内' if is_within_limit else '⚠️ 制限超過'}"
                )

                # 自動最適化の適用
                optimized_df = self.system.auto_apply_memory_optimization(test_df)

                # 最適化後の制限チェック
                final_check = self.system.memory_optimizer.check_memory_limit()
                logger.info(
                    f"📊 最適化後メモリ制限チェック: {'✅ 制限内' if final_check else '⚠️ 制限超過'}"
                )

                # 結果の記録
                self.results["memory_limit_handling"] = {
                    "memory_limit_mb": self.system.memory_optimizer.memory_limit_mb,
                    "initial_within_limit": is_within_limit,
                    "final_within_limit": final_check,
                    "optimization_applied": not is_within_limit and final_check,
                }

            finally:
                # 元の制限に戻す
                self.system.memory_optimizer.memory_limit_mb = original_limit

        return self.results.get("memory_limit_handling", {})

    def run_comprehensive_test(self):
        """包括的なメモリ最適化テストの実行"""
        logger.info("🎯 包括的なメモリ最適化テスト開始")

        # 1. メモリ最適化効果測定
        memory_optimization_result = self.test_memory_optimization_effectiveness()

        # 2. 大規模データセット処理テスト
        large_dataset_result = self.test_large_dataset_processing()

        # 3. メモリ制限処理テスト
        memory_limit_result = self.test_memory_limit_handling()

        # 総合結果の表示
        logger.info("🎉 包括的メモリ最適化テスト完了")
        logger.info("=" * 60)
        logger.info("📊 テスト結果サマリー:")

        if memory_optimization_result:
            logger.info(
                f"  💾 メモリ最適化効果: {memory_optimization_result['total_memory_reduction_percent']:.1f}%削減"
            )

        if large_dataset_result:
            logger.info(
                f"  📈 大規模データ処理: {large_dataset_result['memory_reduction_percent']:.1f}%削減"
            )

        if memory_limit_result:
            logger.info(
                f"  🛡️ メモリ制限処理: {'✅ 成功' if memory_limit_result.get('optimization_applied', False) else '⚠️ 要改善'}"
            )

        # パフォーマンスメトリクスの取得
        performance_metrics = self.system.get_performance_metrics()
        logger.info(
            f"  🚀 システム状態: {performance_metrics.get('memory_status', 'unknown')}"
        )

        return {
            "memory_optimization": memory_optimization_result,
            "large_dataset_processing": large_dataset_result,
            "memory_limit_handling": memory_limit_result,
            "performance_metrics": performance_metrics,
        }


def main():
    """メイン実行関数"""
    logger.info("🚀 メモリ最適化効果測定テスト開始")

    # テスト実行
    tester = MemoryOptimizationTester()
    results = tester.run_comprehensive_test()

    # 結果の保存
    import json

    with open("memory_optimization_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    logger.info("✅ テスト結果を memory_optimization_test_results.json に保存しました")
    logger.info("🎉 メモリ最適化効果測定テスト完了")


if __name__ == "__main__":
    main()
