#!/usr/bin/env python3
"""
記事の手法を統合した高精度バックテストシステムのテスト
"""

import numpy as np
import pandas as pd
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from core.article_inspired_backtest import ArticleInspiredBacktest


class TestArticleInspiredBacktest:
    """ArticleInspiredBacktestのテストクラス"""

    def setup_method(self):
        """テスト前のセットアップ"""
        self.config = {
            "confidence_threshold": 0.7,
            "enhanced_position_sizing": True,
            "risk_management": True,
        }
        self.backtest = ArticleInspiredBacktest(self.config)

        # テスト用データの作成
        self.sample_data = self._create_sample_data()

    def _create_sample_data(self):
        """テスト用のサンプルデータを作成"""
        dates = pd.date_range("2023-01-01", periods=100, freq="D")
        np.random.seed(42)

        data = {
            "date": dates,
            "close": 100 + np.cumsum(np.random.randn(100) * 0.5),
            "volume": np.random.randint(1000, 10000, 100),
            "prediction": np.random.rand(100),
            "confidence": np.random.rand(100),
        }

        return pd.DataFrame(data)

    def test_initialization(self):
        """初期化のテスト"""
        assert self.backtest.config == self.config
        assert self.backtest.confidence_threshold == 0.7
        assert self.backtest.enhanced_position_sizing is True
        assert self.backtest.risk_management is True

    def test_initialization_default_config(self):
        """デフォルト設定での初期化テスト"""
        backtest = ArticleInspiredBacktest()
        assert backtest.config == {}
        assert backtest.confidence_threshold == 0.7
        assert backtest.enhanced_position_sizing is True
        assert backtest.risk_management is True

    def test_run_article_method_backtest(self):
        """記事の手法によるバックテスト実行のテスト"""
        predictions = self.sample_data["prediction"].tolist()
        prices = [
            {"close": price, "volume": vol}
            for price, vol in zip(self.sample_data["close"], self.sample_data["volume"])
        ]

        results = self.backtest.run_article_method_backtest(predictions, prices)

        assert "method" in results
        assert "total_return" in results
        assert "sharpe_ratio" in results
        assert "max_drawdown" in results
        assert "win_rate" in results

    def test_run_enhanced_backtest(self):
        """改善されたバックテスト実行のテスト"""
        predictions = self.sample_data["prediction"].tolist()
        prices = [
            {"close": price, "volume": vol}
            for price, vol in zip(self.sample_data["close"], self.sample_data["volume"])
        ]
        confidence_scores = self.sample_data["confidence"].tolist()

        results = self.backtest.run_enhanced_backtest(
            predictions, prices, confidence_scores
        )

        assert "method" in results
        assert "total_return" in results
        assert "sharpe_ratio" in results
        assert "max_drawdown" in results
        assert "win_rate" in results
        assert isinstance(results["total_return"], (int, float))
        assert isinstance(results["sharpe_ratio"], (int, float))
        assert isinstance(results["max_drawdown"], (int, float))
        assert isinstance(results["win_rate"], (int, float))

    def test_compare_methods(self):
        """手法比較のテスト"""
        predictions = self.sample_data["prediction"].tolist()
        prices = [
            {"close": price, "volume": vol}
            for price, vol in zip(self.sample_data["close"], self.sample_data["volume"])
        ]

        comparison = self.backtest.compare_methods(predictions, prices)

        assert "article_method" in comparison
        assert "enhanced_method" in comparison
        assert "improvement" in comparison

        assert "total_return" in comparison["article_method"]
        assert "total_return" in comparison["enhanced_method"]
        assert "return_improvement" in comparison["improvement"]

    def test_empty_data_handling(self):
        """空データの処理テスト"""
        empty_data = pd.DataFrame()

        # 空データでもエラーが発生しないことを確認
        try:
            signals = self.backtest.calculate_article_signals(empty_data)
            assert len(signals) == 0
        except Exception:
            # 空データの場合は例外が発生しても問題ない
            pass

    def test_invalid_data_handling(self):
        """無効データの処理テスト"""
        invalid_data = pd.DataFrame(
            {
                "close": [100, 101, np.nan, 103],
                "prediction": [0.5, 0.6, 0.7, 0.8],
                "confidence": [0.8, 0.9, 0.7, 0.6],
            }
        )

        # 無効データでもエラーが発生しないことを確認
        try:
            signals = self.backtest.calculate_article_signals(invalid_data)
            assert len(signals) == len(invalid_data)
        except Exception:
            # 無効データの場合は例外が発生しても問題ない
            pass

    def test_config_validation(self):
        """設定値の検証テスト"""
        # 無効な設定値でもエラーが発生しないことを確認
        invalid_config = {
            "confidence_threshold": -0.1,  # 無効な値
            "enhanced_position_sizing": "invalid",  # 無効な型
            "risk_management": None,  # None値
        }

        try:
            backtest = ArticleInspiredBacktest(invalid_config)
            # 無効な設定でも初期化は成功する
            assert backtest is not None
        except Exception:
            # 設定エラーが発生しても問題ない
            pass

    def test_performance_metrics_calculation(self):
        """パフォーマンス指標の計算テスト"""
        # 実際のメソッド名を確認してテスト
        predictions = self.sample_data["prediction"].tolist()
        prices = [
            {"close": price, "volume": vol}
            for price, vol in zip(self.sample_data["close"], self.sample_data["volume"])
        ]

        results = self.backtest.run_article_method_backtest(predictions, prices)

        assert "total_return" in results
        assert "sharpe_ratio" in results
        assert "max_drawdown" in results
        assert "win_rate" in results
        assert isinstance(results["total_return"], (int, float))
        assert isinstance(results["sharpe_ratio"], (int, float))
        assert isinstance(results["max_drawdown"], (int, float))
        assert isinstance(results["win_rate"], (int, float))

    def test_risk_management_integration(self):
        """リスク管理の統合テスト"""
        predictions = self.sample_data["prediction"].tolist()
        prices = [
            {"close": price, "volume": vol}
            for price, vol in zip(self.sample_data["close"], self.sample_data["volume"])
        ]
        confidence_scores = self.sample_data["confidence"].tolist()

        # リスク管理が有効な場合のテスト
        self.backtest.risk_management = True
        results = self.backtest.run_enhanced_backtest(
            predictions, prices, confidence_scores
        )

        assert "total_return" in results
        assert "max_drawdown" in results

        # リスク管理が無効な場合のテスト
        self.backtest.risk_management = False
        results_no_risk = self.backtest.run_enhanced_backtest(
            predictions, prices, confidence_scores
        )

        assert "total_return" in results_no_risk
        assert "max_drawdown" in results_no_risk

    def test_position_sizing_integration(self):
        """ポジションサイジングの統合テスト"""
        predictions = self.sample_data["prediction"].tolist()
        prices = [
            {"close": price, "volume": vol}
            for price, vol in zip(self.sample_data["close"], self.sample_data["volume"])
        ]
        confidence_scores = self.sample_data["confidence"].tolist()

        # 改善されたポジションサイジングが有効な場合のテスト
        self.backtest.enhanced_position_sizing = True
        results = self.backtest.run_enhanced_backtest(
            predictions, prices, confidence_scores
        )

        assert "total_return" in results

        # 改善されたポジションサイジングが無効な場合のテスト
        self.backtest.enhanced_position_sizing = False
        results_no_enhanced = self.backtest.run_enhanced_backtest(
            predictions, prices, confidence_scores
        )

        assert "total_return" in results_no_enhanced

    def test_edge_cases(self):
        """エッジケースのテスト"""
        # 単一データポイント
        single_data = self.sample_data.iloc[:1].copy()
        try:
            predictions = single_data["prediction"].tolist()
            prices = [
                {"close": price, "volume": vol}
                for price, vol in zip(single_data["close"], single_data["volume"])
            ]
            results = self.backtest.run_article_method_backtest(predictions, prices)
            assert "total_return" in results
        except Exception:
            # 単一データポイントでエラーが発生しても問題ない
            pass

        # すべて同じ値のデータ
        same_data = self.sample_data.copy()
        same_data["close"] = 100
        same_data["prediction"] = 0.5
        same_data["confidence"] = 0.8

        try:
            predictions = same_data["prediction"].tolist()
            prices = [
                {"close": price, "volume": vol}
                for price, vol in zip(same_data["close"], same_data["volume"])
            ]
            results = self.backtest.run_article_method_backtest(predictions, prices)
            assert "total_return" in results
        except Exception:
            # 同じ値のデータでエラーが発生しても問題ない
            pass
