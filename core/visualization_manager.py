#!/usr/bin/env python3
"""
可視化管理システム
予測結果の可視化、チャート生成を管理
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, List
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")


class VisualizationManager:
    """可視化管理クラス"""

    def __init__(self, logger=None, error_handler=None):
        """初期化"""
        self.logger = logger
        self.error_handler = error_handler
        self._setup_matplotlib()

    def _setup_matplotlib(self):
        """matplotlibの設定"""
        try:
            import matplotlib.font_manager as fm

            # 日本語フォントの設定
            plt.rcParams["font.family"] = [
                "DejaVu Sans",
                "Hiragino Sans",
                "Yu Gothic",
                "Meiryo",
                "Takao",
                "IPAexGothic",
                "IPAPGothic",
                "VL PGothic",
                "Noto Sans CJK JP",
            ]
        except Exception:
            if self.logger:
                self.logger.log_warning("日本語フォント設定をスキップします")

    def create_prediction_visualization(
        self,
        y_test: pd.Series,
        y_pred: np.ndarray,
        model_name: str,
        output_file: str,
        title: str = "株価予測結果",
    ) -> bool:
        """予測結果の可視化"""
        try:
            # 高解像度対応
            plt.figure(figsize=(15, 8), dpi=100)

            # メインプロット
            plt.subplot(2, 2, 1)
            plt.plot(
                y_test.values, label="実際の株価", color="blue", alpha=0.7, linewidth=2
            )
            plt.plot(y_pred, label="予測株価", color="red", alpha=0.7, linewidth=2)
            plt.legend()
            plt.title(f"{title} ({model_name})")
            plt.xlabel("データポイント")
            plt.ylabel("株価")
            plt.grid(True, alpha=0.3)

            # 散布図
            plt.subplot(2, 2, 2)
            plt.scatter(y_test, y_pred, alpha=0.6, color="green")
            plt.plot(
                [y_test.min(), y_test.max()], [y_test.min(), y_test.max()], "r--", lw=2
            )
            plt.xlabel("実際の株価")
            plt.ylabel("予測株価")
            plt.title("実測値 vs 予測値")
            plt.grid(True, alpha=0.3)

            # 残差プロット
            plt.subplot(2, 2, 3)
            residuals = y_test - y_pred
            plt.scatter(y_pred, residuals, alpha=0.6, color="orange")
            plt.axhline(y=0, color="r", linestyle="--")
            plt.xlabel("予測株価")
            plt.ylabel("残差")
            plt.title("残差プロット")
            plt.grid(True, alpha=0.3)

            # 予測精度のヒストグラム
            plt.subplot(2, 2, 4)
            errors = np.abs(y_test - y_pred)
            plt.hist(errors, bins=20, alpha=0.7, color="purple")
            plt.xlabel("絶対誤差")
            plt.ylabel("頻度")
            plt.title("予測誤差の分布")
            plt.grid(True, alpha=0.3)

            plt.tight_layout()
            plt.savefig(output_file, dpi=300, bbox_inches="tight", facecolor="white")
            plt.close()  # メモリ節約のため

            if self.logger:
                self.logger.log_info(f"🎨 結果を '{output_file}' に保存しました")

            return True

        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_file_error(e, output_file, "可視化保存")
            return False

    def create_model_comparison_chart(
        self,
        comparison_results: List[Dict],
        output_file: str,
        title: str = "モデル比較結果",
    ) -> bool:
        """モデル比較チャートの作成"""
        try:
            if not comparison_results:
                return False

            # データの準備
            model_names = [
                r.get("model_name", f"Model_{i}")
                for i, r in enumerate(comparison_results)
            ]
            mae_scores = [
                r.get("metrics", {}).get("test_mae", 0) for r in comparison_results
            ]
            r2_scores = [
                r.get("metrics", {}).get("test_r2", 0) for r in comparison_results
            ]

            plt.figure(figsize=(12, 6), dpi=100)

            # MAE比較
            plt.subplot(1, 2, 1)
            bars1 = plt.bar(model_names, mae_scores, color="skyblue", alpha=0.7)
            plt.title("MAE比較")
            plt.ylabel("MAE")
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)

            # バーの上に値を表示
            for bar, score in zip(bars1, mae_scores):
                plt.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.001,
                    f"{score:.4f}",
                    ha="center",
                    va="bottom",
                )

            # R²比較
            plt.subplot(1, 2, 2)
            bars2 = plt.bar(model_names, r2_scores, color="lightcoral", alpha=0.7)
            plt.title("R²比較")
            plt.ylabel("R²")
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)

            # バーの上に値を表示
            for bar, score in zip(bars2, r2_scores):
                plt.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.001,
                    f"{score:.4f}",
                    ha="center",
                    va="bottom",
                )

            plt.tight_layout()
            plt.savefig(output_file, dpi=300, bbox_inches="tight", facecolor="white")
            plt.close()

            if self.logger:
                self.logger.log_info(
                    f"📊 モデル比較チャートを '{output_file}' に保存しました"
                )

            return True

        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_file_error(e, output_file, "モデル比較可視化")
            return False

    def create_performance_metrics_chart(
        self,
        metrics: Dict[str, float],
        output_file: str,
        title: str = "パフォーマンス指標",
    ) -> bool:
        """パフォーマンス指標チャートの作成"""
        try:
            # 指標の準備
            metric_names = list(metrics.keys())
            metric_values = list(metrics.values())

            plt.figure(figsize=(10, 6), dpi=100)
            bars = plt.bar(metric_names, metric_values, color="lightgreen", alpha=0.7)
            plt.title(title)
            plt.ylabel("値")
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)

            # バーの上に値を表示
            for bar, value in zip(bars, metric_values):
                plt.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.001,
                    f"{value:.4f}",
                    ha="center",
                    va="bottom",
                )

            plt.tight_layout()
            plt.savefig(output_file, dpi=300, bbox_inches="tight", facecolor="white")
            plt.close()

            if self.logger:
                self.logger.log_info(
                    f"📈 パフォーマンス指標を '{output_file}' に保存しました"
                )

            return True

        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_file_error(
                    e, output_file, "パフォーマンス指標可視化"
                )
            return False

    def create_time_series_plot(
        self,
        data: pd.DataFrame,
        date_column: str,
        value_column: str,
        output_file: str,
        title: str = "時系列データ",
    ) -> bool:
        """時系列プロットの作成"""
        try:
            plt.figure(figsize=(12, 6), dpi=100)
            plt.plot(data[date_column], data[value_column], linewidth=2, alpha=0.8)
            plt.title(title)
            plt.xlabel("日付")
            plt.ylabel("値")
            plt.grid(True, alpha=0.3)
            plt.xticks(rotation=45)

            plt.tight_layout()
            plt.savefig(output_file, dpi=300, bbox_inches="tight", facecolor="white")
            plt.close()

            if self.logger:
                self.logger.log_info(
                    f"📅 時系列プロットを '{output_file}' に保存しました"
                )

            return True

        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_file_error(e, output_file, "時系列可視化")
            return False

    def get_visualization_info(self) -> Dict[str, Any]:
        """可視化情報の取得"""
        return {
            "supported_formats": ["png", "jpg", "svg", "pdf"],
            "default_dpi": 300,
            "default_figure_size": (15, 8),
            "timestamp": datetime.now().isoformat(),
        }
