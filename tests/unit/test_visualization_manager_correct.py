#!/usr/bin/env python3
"""
visualization_manager.pyの正しいテスト
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
from core.visualization_manager import VisualizationManager


class TestVisualizationManagerCorrect:
    """可視化管理の正しいテストクラス"""

    @pytest.fixture
    def viz_manager(self):
        """VisualizationManagerのフィクスチャ"""
        return VisualizationManager()

    @pytest.fixture
    def sample_data(self):
        """サンプルデータのフィクスチャ"""
        dates = pd.date_range('2024-01-01', periods=10, freq='D')
        data = {
            'Date': dates,
            'Open': np.random.uniform(100, 110, 10),
            'High': np.random.uniform(110, 120, 10),
            'Low': np.random.uniform(90, 100, 10),
            'Close': np.random.uniform(100, 110, 10),
            'Volume': np.random.randint(100000, 1000000, 10)
        }
        return pd.DataFrame(data)

    def test_create_prediction_visualization_basic(self, viz_manager):
        """予測結果可視化の基本テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            y_test = pd.Series([100, 105, 110, 95, 100])
            y_pred = np.array([102, 107, 108, 97, 99])
            
            output_file = os.path.join(temp_dir, "prediction_test.png")
            
            result = viz_manager.create_prediction_visualization(
                y_test=y_test,
                y_pred=y_pred,
                model_name="Test Model",
                output_file=output_file
            )
            
            assert result is True
            assert os.path.exists(output_file)

    def test_create_time_series_plot_basic(self, viz_manager, sample_data):
        """時系列プロットの基本テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, "time_series_test.png")
            
            result = viz_manager.create_time_series_plot(
                data=sample_data,
                output_file=output_file,
                title="Time Series Plot",
                date_column="Date",
                value_column="Close"
            )
            
            assert result is True
            assert os.path.exists(output_file)

    def test_error_handling_invalid_file_path(self, viz_manager):
        """無効なファイルパスのエラーハンドリングテスト"""
        y_test = pd.Series([100, 105, 110])
        y_pred = np.array([102, 107, 108])
        
        # 無効なディレクトリ
        invalid_path = "/invalid/directory/prediction.png"
        
        result = viz_manager.create_prediction_visualization(
            y_test=y_test,
            y_pred=y_pred,
            model_name="Test Model",
            output_file=invalid_path
        )
        
        assert result is False

    def test_matplotlib_backend_configuration(self, viz_manager):
        """matplotlibバックエンドの設定テスト"""
        import matplotlib
        backend = matplotlib.get_backend()
        
        # バックエンドが設定されていることを確認
        assert backend is not None
        assert backend in ['Agg', 'TkAgg', 'Qt5Agg', 'Qt4Agg', 'macosx']

    def test_visualization_manager_initialization(self):
        """VisualizationManagerの初期化テスト"""
        manager = VisualizationManager()
        
        assert manager.logger is None
        assert manager.error_handler is None
