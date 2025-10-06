#!/usr/bin/env python3
"""
可視化管理システムのテスト
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
from pathlib import Path

from core.visualization_manager import VisualizationManager


class TestVisualizationManager:
    """可視化管理クラスのテスト"""

    def test_initialization(self):
        """初期化テスト"""
        vm = VisualizationManager()
        assert vm.logger is None
        assert vm.error_handler is None

    def test_initialization_with_logger_and_error_handler(self):
        """ロガーとエラーハンドラー付き初期化テスト"""
        logger = Mock()
        error_handler = Mock()
        vm = VisualizationManager(logger=logger, error_handler=error_handler)
        assert vm.logger == logger
        assert vm.error_handler == error_handler

    def test_setup_matplotlib(self):
        """matplotlib設定テスト"""
        vm = VisualizationManager()
        # 設定が正常に実行されることを確認
        vm._setup_matplotlib()

    @patch("matplotlib.pyplot.figure")
    @patch("matplotlib.pyplot.subplot")
    @patch("matplotlib.pyplot.plot")
    @patch("matplotlib.pyplot.scatter")
    @patch("matplotlib.pyplot.legend")
    @patch("matplotlib.pyplot.title")
    @patch("matplotlib.pyplot.xlabel")
    @patch("matplotlib.pyplot.ylabel")
    @patch("matplotlib.pyplot.grid")
    @patch("matplotlib.pyplot.tight_layout")
    @patch("matplotlib.pyplot.savefig")
    @patch("matplotlib.pyplot.close")
    def test_create_prediction_visualization_success(
        self,
        mock_close,
        mock_savefig,
        mock_tight_layout,
        mock_grid,
        mock_ylabel,
        mock_xlabel,
        mock_title,
        mock_legend,
        mock_scatter,
        mock_plot,
        mock_subplot,
        mock_figure,
    ):
        """予測結果可視化成功テスト"""
        vm = VisualizationManager()

        # テストデータの準備
        y_test = pd.Series([100, 105, 110, 108, 112])
        y_pred = np.array([102, 107, 109, 111, 113])

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            output_file = tmp.name

        try:
            result = vm.create_prediction_visualization(
                y_test, y_pred, "TestModel", output_file, "Test Title"
            )

            assert result is True
            # figure is called multiple times due to subplot creation
            assert mock_figure.call_count >= 1
            mock_savefig.assert_called_once()
            mock_close.assert_called_once()
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)

    def test_create_prediction_visualization_error(self):
        """予測結果可視化エラーテスト"""
        vm = VisualizationManager()
        error_handler = Mock()
        vm.error_handler = error_handler

        # 無効なデータでテスト
        result = vm.create_prediction_visualization(
            None, None, "TestModel", "/invalid/path/test.png"
        )

        assert result is False
        error_handler.handle_file_error.assert_called_once()

    @patch("matplotlib.pyplot.figure")
    @patch("matplotlib.pyplot.subplot")
    @patch("matplotlib.pyplot.bar")
    @patch("matplotlib.pyplot.text")
    @patch("matplotlib.pyplot.title")
    @patch("matplotlib.pyplot.ylabel")
    @patch("matplotlib.pyplot.xticks")
    @patch("matplotlib.pyplot.grid")
    @patch("matplotlib.pyplot.tight_layout")
    @patch("matplotlib.pyplot.savefig")
    @patch("matplotlib.pyplot.close")
    def test_create_model_comparison_chart_success(
        self,
        mock_close,
        mock_savefig,
        mock_tight_layout,
        mock_grid,
        mock_xticks,
        mock_ylabel,
        mock_title,
        mock_text,
        mock_bar,
        mock_subplot,
        mock_figure,
    ):
        """モデル比較チャート成功テスト"""
        vm = VisualizationManager()

        comparison_results = [
            {"model_name": "Model1", "metrics": {"test_mae": 0.1, "test_r2": 0.9}},
            {"model_name": "Model2", "metrics": {"test_mae": 0.2, "test_r2": 0.8}},
        ]

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            output_file = tmp.name

        try:
            result = vm.create_model_comparison_chart(
                comparison_results, output_file, "Test Comparison"
            )

            assert result is True
            mock_figure.assert_called_once()
            mock_savefig.assert_called_once()
            mock_close.assert_called_once()
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)

    def test_create_model_comparison_chart_empty_results(self):
        """モデル比較チャート空結果テスト"""
        vm = VisualizationManager()

        result = vm.create_model_comparison_chart([], "/tmp/test.png")

        assert result is False

    def test_create_model_comparison_chart_error(self):
        """モデル比較チャートエラーテスト"""
        vm = VisualizationManager()
        error_handler = Mock()
        vm.error_handler = error_handler

        result = vm.create_model_comparison_chart(
            [{"invalid": "data"}], "/invalid/path/test.png"
        )

        assert result is False
        error_handler.handle_file_error.assert_called_once()

    @patch("matplotlib.pyplot.figure")
    @patch("matplotlib.pyplot.bar")
    @patch("matplotlib.pyplot.text")
    @patch("matplotlib.pyplot.title")
    @patch("matplotlib.pyplot.ylabel")
    @patch("matplotlib.pyplot.xticks")
    @patch("matplotlib.pyplot.grid")
    @patch("matplotlib.pyplot.tight_layout")
    @patch("matplotlib.pyplot.savefig")
    @patch("matplotlib.pyplot.close")
    def test_create_performance_metrics_chart_success(
        self,
        mock_close,
        mock_savefig,
        mock_tight_layout,
        mock_grid,
        mock_xticks,
        mock_ylabel,
        mock_title,
        mock_text,
        mock_bar,
        mock_figure,
    ):
        """パフォーマンス指標チャート成功テスト"""
        vm = VisualizationManager()

        metrics = {"MAE": 0.1, "RMSE": 0.2, "R2": 0.9}

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            output_file = tmp.name

        try:
            result = vm.create_performance_metrics_chart(
                metrics, output_file, "Test Metrics"
            )

            assert result is True
            mock_figure.assert_called_once()
            mock_savefig.assert_called_once()
            mock_close.assert_called_once()
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)

    def test_create_performance_metrics_chart_error(self):
        """パフォーマンス指標チャートエラーテスト"""
        vm = VisualizationManager()
        error_handler = Mock()
        vm.error_handler = error_handler

        result = vm.create_performance_metrics_chart({}, "/invalid/path/test.png")

        assert result is False
        error_handler.handle_file_error.assert_called_once()

    @patch("matplotlib.pyplot.figure")
    @patch("matplotlib.pyplot.plot")
    @patch("matplotlib.pyplot.title")
    @patch("matplotlib.pyplot.xlabel")
    @patch("matplotlib.pyplot.ylabel")
    @patch("matplotlib.pyplot.grid")
    @patch("matplotlib.pyplot.xticks")
    @patch("matplotlib.pyplot.tight_layout")
    @patch("matplotlib.pyplot.savefig")
    @patch("matplotlib.pyplot.close")
    def test_create_time_series_plot_success(
        self,
        mock_close,
        mock_savefig,
        mock_tight_layout,
        mock_xticks,
        mock_grid,
        mock_ylabel,
        mock_xlabel,
        mock_title,
        mock_plot,
        mock_figure,
    ):
        """時系列プロット成功テスト"""
        vm = VisualizationManager()

        data = pd.DataFrame(
            {
                "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
                "value": [100, 105, 110],
            }
        )

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            output_file = tmp.name

        try:
            result = vm.create_time_series_plot(
                data, "date", "value", output_file, "Test Time Series"
            )

            assert result is True
            mock_figure.assert_called_once()
            mock_savefig.assert_called_once()
            mock_close.assert_called_once()
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)

    def test_create_time_series_plot_error(self):
        """時系列プロットエラーテスト"""
        vm = VisualizationManager()
        error_handler = Mock()
        vm.error_handler = error_handler

        result = vm.create_time_series_plot(
            pd.DataFrame(), "date", "value", "/invalid/path/test.png"
        )

        assert result is False
        error_handler.handle_file_error.assert_called_once()

    def test_get_visualization_info(self):
        """可視化情報取得テスト"""
        vm = VisualizationManager()

        info = vm.get_visualization_info()

        assert "supported_formats" in info
        assert "default_dpi" in info
        assert "default_figure_size" in info
        assert "timestamp" in info
        assert "png" in info["supported_formats"]
        assert info["default_dpi"] == 300
        assert info["default_figure_size"] == (15, 8)

    def test_create_prediction_visualization_with_logger(self):
        """ロガー付き予測結果可視化テスト"""
        logger = Mock()
        vm = VisualizationManager(logger=logger)

        y_test = pd.Series([100, 105, 110])
        y_pred = np.array([102, 107, 109])

        with (
            patch("matplotlib.pyplot.figure"),
            patch("matplotlib.pyplot.subplot"),
            patch("matplotlib.pyplot.plot"),
            patch("matplotlib.pyplot.scatter"),
            patch("matplotlib.pyplot.legend"),
            patch("matplotlib.pyplot.title"),
            patch("matplotlib.pyplot.xlabel"),
            patch("matplotlib.pyplot.ylabel"),
            patch("matplotlib.pyplot.grid"),
            patch("matplotlib.pyplot.tight_layout"),
            patch("matplotlib.pyplot.savefig"),
            patch("matplotlib.pyplot.close"),
        ):
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                output_file = tmp.name

            try:
                result = vm.create_prediction_visualization(
                    y_test, y_pred, "TestModel", output_file
                )

                assert result is True
                logger.log_info.assert_called_once()
            finally:
                if os.path.exists(output_file):
                    os.unlink(output_file)

    def test_create_model_comparison_chart_with_logger(self):
        """ロガー付きモデル比較チャートテスト"""
        logger = Mock()
        vm = VisualizationManager(logger=logger)

        comparison_results = [
            {"model_name": "Model1", "metrics": {"test_mae": 0.1, "test_r2": 0.9}}
        ]

        with (
            patch("matplotlib.pyplot.figure"),
            patch("matplotlib.pyplot.subplot"),
            patch("matplotlib.pyplot.bar"),
            patch("matplotlib.pyplot.text"),
            patch("matplotlib.pyplot.title"),
            patch("matplotlib.pyplot.ylabel"),
            patch("matplotlib.pyplot.xticks"),
            patch("matplotlib.pyplot.grid"),
            patch("matplotlib.pyplot.tight_layout"),
            patch("matplotlib.pyplot.savefig"),
            patch("matplotlib.pyplot.close"),
        ):
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                output_file = tmp.name

            try:
                result = vm.create_model_comparison_chart(
                    comparison_results, output_file
                )

                assert result is True
                logger.log_info.assert_called_once()
            finally:
                if os.path.exists(output_file):
                    os.unlink(output_file)

    def test_create_performance_metrics_chart_with_logger(self):
        """ロガー付きパフォーマンス指標チャートテスト"""
        logger = Mock()
        vm = VisualizationManager(logger=logger)

        metrics = {"MAE": 0.1, "RMSE": 0.2}

        with (
            patch("matplotlib.pyplot.figure"),
            patch("matplotlib.pyplot.bar"),
            patch("matplotlib.pyplot.text"),
            patch("matplotlib.pyplot.title"),
            patch("matplotlib.pyplot.ylabel"),
            patch("matplotlib.pyplot.xticks"),
            patch("matplotlib.pyplot.grid"),
            patch("matplotlib.pyplot.tight_layout"),
            patch("matplotlib.pyplot.savefig"),
            patch("matplotlib.pyplot.close"),
        ):
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                output_file = tmp.name

            try:
                result = vm.create_performance_metrics_chart(metrics, output_file)

                assert result is True
                logger.log_info.assert_called_once()
            finally:
                if os.path.exists(output_file):
                    os.unlink(output_file)

    def test_create_time_series_plot_with_logger(self):
        """ロガー付き時系列プロットテスト"""
        logger = Mock()
        vm = VisualizationManager(logger=logger)

        data = pd.DataFrame({"date": ["2024-01-01", "2024-01-02"], "value": [100, 105]})

        with (
            patch("matplotlib.pyplot.figure"),
            patch("matplotlib.pyplot.plot"),
            patch("matplotlib.pyplot.title"),
            patch("matplotlib.pyplot.xlabel"),
            patch("matplotlib.pyplot.ylabel"),
            patch("matplotlib.pyplot.grid"),
            patch("matplotlib.pyplot.xticks"),
            patch("matplotlib.pyplot.tight_layout"),
            patch("matplotlib.pyplot.savefig"),
            patch("matplotlib.pyplot.close"),
        ):
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                output_file = tmp.name

            try:
                result = vm.create_time_series_plot(data, "date", "value", output_file)

                assert result is True
                logger.log_info.assert_called_once()
            finally:
                if os.path.exists(output_file):
                    os.unlink(output_file)
