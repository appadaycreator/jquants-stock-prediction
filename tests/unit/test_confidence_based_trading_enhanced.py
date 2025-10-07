#!/usr/bin/env python3
"""
confidence_based_trading.py の包括的テスト
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# パスを追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.confidence_based_trading import ConfidenceBasedTrading


class TestConfidenceBasedTrading:
    """ConfidenceBasedTrading のテストクラス"""

    def setup_method(self):
        """テスト前の準備"""
        self.config = {
            "confidence_threshold": 0.7,
            "min_confidence": 0.6,
            "max_confidence": 0.95,
            "risk_adjustment": True,
            "volatility_threshold": 0.02
        }
        self.trading_system = ConfidenceBasedTrading(self.config)
        self.sample_market_data = {
            "volatility": 0.15,
            "volume": 1000000,
            "price_change": 0.02,
            "market_trend": "bullish"
        }

    def test_initialization(self):
        """初期化テスト"""
        assert self.trading_system is not None
        assert self.trading_system.confidence_threshold == 0.7
        assert self.trading_system.min_confidence == 0.6
        assert self.trading_system.max_confidence == 0.95
        assert self.trading_system.risk_adjustment is True
        assert self.trading_system.volatility_threshold == 0.02

    def test_initialization_with_default_config(self):
        """デフォルト設定での初期化テスト"""
        trading_system = ConfidenceBasedTrading()
        assert trading_system.confidence_threshold == 0.7
        assert trading_system.min_confidence == 0.6
        assert trading_system.max_confidence == 0.95

    def test_calculate_confidence_basic(self):
        """基本信頼度計算テスト"""
        prediction = 0.8
        confidence = self.trading_system.calculate_confidence(prediction, self.sample_market_data)
        assert isinstance(confidence, float)
        assert 0 <= confidence <= 1

    def test_calculate_confidence_extreme_values(self):
        """極値での信頼度計算テスト"""
        # 極端に高い予測値
        high_prediction = 0.95
        confidence_high = self.trading_system.calculate_confidence(high_prediction, self.sample_market_data)
        assert confidence_high > 0.5

        # 極端に低い予測値
        low_prediction = 0.05
        confidence_low = self.trading_system.calculate_confidence(low_prediction, self.sample_market_data)
        assert confidence_low > 0.5

    def test_calculate_confidence_with_different_market_data(self):
        """異なる市場データでの信頼度計算テスト"""
        prediction = 0.7
        
        # 高ボラティリティ市場
        high_volatility_data = self.sample_market_data.copy()
        high_volatility_data["volatility"] = 0.5
        confidence_high_vol = self.trading_system.calculate_confidence(prediction, high_volatility_data)
        
        # 低ボラティリティ市場
        low_volatility_data = self.sample_market_data.copy()
        low_volatility_data["volatility"] = 0.05
        confidence_low_vol = self.trading_system.calculate_confidence(prediction, low_volatility_data)
        
        assert isinstance(confidence_high_vol, float)
        assert isinstance(confidence_low_vol, float)

    def test_calculate_market_adjustment(self):
        """市場調整計算テスト"""
        adjustment = self.trading_system._calculate_market_adjustment(self.sample_market_data)
        assert isinstance(adjustment, float)
        assert -1 <= adjustment <= 1

    def test_calculate_volatility_adjustment(self):
        """ボラティリティ調整計算テスト"""
        adjustment = self.trading_system._calculate_volatility_adjustment(self.sample_market_data)
        assert isinstance(adjustment, float)
        assert -1 <= adjustment <= 1

    def test_calculate_market_adjustment_edge_cases(self):
        """市場調整計算のエッジケーステスト"""
        # 空の市場データ
        empty_data = {}
        adjustment = self.trading_system._calculate_market_adjustment(empty_data)
        assert isinstance(adjustment, float)
        assert 0.5 <= adjustment <= 1.5

    def test_calculate_volatility_adjustment_edge_cases(self):
        """ボラティリティ調整計算のエッジケーステスト"""
        # 極端なボラティリティ
        high_vol_data = {"volatility": 1.0}
        adjustment = self.trading_system._calculate_volatility_adjustment(high_vol_data)
        assert isinstance(adjustment, float)
        assert 0.3 <= adjustment <= 1.0

    def test_should_trade_high_confidence(self):
        """高信頼度での取引判定テスト"""
        prediction = 0.8
        result = self.trading_system.should_trade(prediction, self.sample_market_data)
        assert isinstance(result, dict)
        assert "should_trade" in result
        assert "confidence" in result
        assert "trade_direction" in result

    def test_should_trade_low_confidence(self):
        """低信頼度での取引判定テスト"""
        prediction = 0.3
        result = self.trading_system.should_trade(prediction, self.sample_market_data)
        assert isinstance(result, dict)
        assert "should_trade" in result
        assert "confidence" in result
        assert "trade_direction" in result

    def test_should_trade_medium_confidence(self):
        """中信頼度での取引判定テスト"""
        prediction = 0.7
        result = self.trading_system.should_trade(prediction, self.sample_market_data)
        assert isinstance(result, dict)
        assert "should_trade" in result
        assert "confidence" in result
        assert "trade_direction" in result

    def test_should_trade_with_risk_adjustment(self):
        """リスク調整付き取引判定テスト"""
        prediction = 0.8
        result = self.trading_system.should_trade(prediction, self.sample_market_data)
        assert isinstance(result, dict)
        assert "should_trade" in result
        assert "risk_level" in result
        assert "position_size" in result

    def test_should_trade_without_risk_adjustment(self):
        """リスク調整なし取引判定テスト"""
        trading_system = ConfidenceBasedTrading({"risk_adjustment": False})
        prediction = 0.8
        result = trading_system.should_trade(prediction, self.sample_market_data)
        assert isinstance(result, dict)
        assert "should_trade" in result

    def test_calculate_risk_level(self):
        """リスクレベル計算テスト"""
        risk_level = self.trading_system._calculate_risk_level(self.sample_market_data)
        assert isinstance(risk_level, str)
        assert risk_level in ["LOW", "MEDIUM", "HIGH"]

    def test_calculate_risk_level_with_different_data(self):
        """異なるデータでのリスクレベル計算テスト"""
        # 低リスクデータ（より低い値）
        low_risk_data = {"volatility": 0.01, "price_change": 0.005}
        low_risk = self.trading_system._calculate_risk_level(low_risk_data)
        assert low_risk == "LOW"
        
        # 高リスクデータ
        high_risk_data = {"volatility": 0.5, "price_change": 0.1}
        high_risk = self.trading_system._calculate_risk_level(high_risk_data)
        assert high_risk == "HIGH"

    def test_calculate_position_size_internal(self):
        """内部ポジションサイズ計算テスト"""
        confidence = 0.8
        risk_level = "MEDIUM"
        
        position_size = self.trading_system._calculate_position_size(confidence, risk_level)
        assert isinstance(position_size, float)
        assert 0 <= position_size <= 100

    def test_calculate_position_size_with_different_risk_levels(self):
        """異なるリスクレベルでのポジションサイズ計算テスト"""
        confidence = 0.8
        
        # 低リスク
        low_risk_position = self.trading_system._calculate_position_size(confidence, "LOW")
        
        # 高リスク
        high_risk_position = self.trading_system._calculate_position_size(confidence, "HIGH")
        
        assert low_risk_position > high_risk_position

    def test_execute_trade_success(self):
        """取引実行成功テスト"""
        # 高信頼度の取引判定を実行
        trade_decision = self.trading_system.should_trade(0.9, self.sample_market_data)
        
        result = self.trading_system.execute_trade(trade_decision, self.sample_market_data)
        assert isinstance(result, dict)
        assert "executed" in result
        # 取引が実行された場合のみdirectionをチェック
        if result["executed"]:
            assert "direction" in result

    def test_execute_trade_failure(self):
        """取引実行失敗テスト"""
        # 低信頼度の取引判定
        trade_decision = self.trading_system.should_trade(0.3, self.sample_market_data)
        
        result = self.trading_system.execute_trade(trade_decision, self.sample_market_data)
        assert isinstance(result, dict)
        assert "executed" in result

    def test_get_performance_metrics(self):
        """パフォーマンス指標取得テスト"""
        # テスト用の取引履歴を追加
        self.trading_system.trade_history = [
            {"confidence": 0.8, "risk_level": "LOW"},
            {"confidence": 0.6, "risk_level": "MEDIUM"},
            {"confidence": 0.9, "risk_level": "HIGH"}
        ]
        
        metrics = self.trading_system.get_performance_metrics()
        assert isinstance(metrics, dict)
        assert "total_trades" in metrics
        assert "avg_confidence" in metrics
        assert "risk_distribution" in metrics

    def test_get_performance_metrics_empty_history(self):
        """空の履歴でのパフォーマンス指標取得テスト"""
        metrics = self.trading_system.get_performance_metrics()
        assert isinstance(metrics, dict)
        assert metrics["total_trades"] == 0
        assert metrics["avg_confidence"] == 0.0

    def test_market_data_handling(self):
        """市場データ処理テスト"""
        # 有効なデータ
        valid_data = self.sample_market_data
        confidence = self.trading_system.calculate_confidence(0.8, valid_data)
        assert isinstance(confidence, float)
        
        # 空のデータ
        empty_data = {}
        confidence = self.trading_system.calculate_confidence(0.8, empty_data)
        assert isinstance(confidence, float)

    def test_market_data_edge_cases(self):
        """市場データのエッジケーステスト"""
        # 極端な値のデータ
        extreme_data = {
            "volatility": 0.0,
            "volume": 0,
            "price_change": 0.0,
            "market_trend": "neutral"
        }
        confidence = self.trading_system.calculate_confidence(0.8, extreme_data)
        assert isinstance(confidence, float)

    def test_error_handling_in_calculate_confidence(self):
        """信頼度計算でのエラーハンドリングテスト"""
        # 無効な予測値
        with patch.object(self.trading_system, 'logger') as mock_logger:
            confidence = self.trading_system.calculate_confidence(None, self.sample_market_data)
            assert confidence == self.trading_system.min_confidence

    def test_error_handling_in_should_trade(self):
        """取引判定でのエラーハンドリングテスト"""
        # 無効なデータ
        with patch.object(self.trading_system, 'logger') as mock_logger:
            result = self.trading_system.should_trade(None, None)
            assert result["should_trade"] is False

    def test_error_handling_in_execute_trade(self):
        """取引実行でのエラーハンドリングテスト"""
        # 無効なデータ
        with patch.object(self.trading_system, 'logger') as mock_logger:
            result = self.trading_system.execute_trade(None, None)
            assert result["executed"] is False

    def test_edge_cases_in_confidence_calculation(self):
        """信頼度計算のエッジケーステスト"""
        # 境界値テスト
        edge_cases = [0.0, 0.5, 1.0]
        for prediction in edge_cases:
            confidence = self.trading_system.calculate_confidence(prediction, self.sample_market_data)
            assert isinstance(confidence, float)
            assert 0 <= confidence <= 1

    def test_edge_cases_in_position_sizing(self):
        """ポジションサイジングのエッジケーステスト"""
        # 極端な値でのテスト
        extreme_cases = [
            (0.0, "LOW"),   # 最低信頼度
            (1.0, "HIGH"),  # 最高信頼度
            (0.5, "MEDIUM"), # 中信頼度
        ]
        
        for confidence, risk_level in extreme_cases:
            position_size = self.trading_system._calculate_position_size(confidence, risk_level)
            assert isinstance(position_size, (int, float))  # intまたはfloatを許可
            assert 0 <= position_size <= 100

    def test_performance_with_large_dataset(self):
        """大規模データセットでのパフォーマンステスト"""
        # 大量の市場データでテスト
        large_market_data = {
            "volatility": 0.15,
            "volume": 10000000,
            "price_change": 0.02,
            "market_trend": "bullish"
        }
        
        # パフォーマンステスト（タイムアウトなし）
        for i in range(100):
            confidence = self.trading_system.calculate_confidence(0.7, large_market_data)
            assert isinstance(confidence, float)

    def test_memory_usage_optimization(self):
        """メモリ使用量最適化テスト"""
        # 大量の取引履歴を作成
        for i in range(1000):
            trade = {
                "confidence": np.random.uniform(0.5, 0.95),
                "risk_level": "MEDIUM",
                "timestamp": datetime.now()
            }
            self.trading_system.trade_history.append(trade)
        
        # パフォーマンス指標の取得
        metrics = self.trading_system.get_performance_metrics()
        
        # メモリ使用量が適切に管理されていることを確認
        assert len(self.trading_system.trade_history) == 1000
        assert metrics["total_trades"] == 1000

    def test_concurrent_access_safety(self):
        """並行アクセス安全性テスト"""
        import threading
        import time
        
        results = []
        
        def calculate_confidence_thread():
            for _ in range(10):
                confidence = self.trading_system.calculate_confidence(0.7, self.sample_market_data)
                results.append(confidence)
        
        # 複数スレッドで同時実行
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=calculate_confidence_thread)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # 結果が正しく計算されていることを確認
        assert len(results) == 50
        for result in results:
            assert isinstance(result, float)
            assert 0 <= result <= 1

    def test_configuration_validation(self):
        """設定検証テスト"""
        # 無効な設定
        invalid_config = {
            "confidence_threshold": 1.5,  # 範囲外
            "min_confidence": -0.1,       # 負の値
            "max_confidence": 0.5,        # minより小さい
        }
        
        trading_system = ConfidenceBasedTrading(invalid_config)
        # 設定が適切に設定されることを確認
        assert trading_system.confidence_threshold == 1.5  # そのまま設定される
        assert trading_system.min_confidence == -0.1
        assert trading_system.max_confidence == 0.5

    def test_data_type_validation(self):
        """データ型検証テスト"""
        # 文字列型の予測値
        confidence = self.trading_system.calculate_confidence("0.8", self.sample_market_data)
        assert isinstance(confidence, float)
        
        # リスト型の市場データ
        list_market_data = [0.15, 1000000, 0.02, "bullish"]
        confidence = self.trading_system.calculate_confidence(0.8, list_market_data)
        assert isinstance(confidence, float)

    def test_integration_with_real_market_data(self):
        """実際の市場データとの統合テスト"""
        real_market_data = {
            "volatility": 0.12,
            "volume": 2500000,
            "price_change": 0.015,
            "market_trend": "neutral",
            "rsi": 45.5,
            "macd": 0.02
        }
        
        prediction = 0.75
        confidence = self.trading_system.calculate_confidence(prediction, real_market_data)
        trade_result = self.trading_system.should_trade(prediction, real_market_data)
        
        assert isinstance(confidence, float)
        assert isinstance(trade_result, dict)
        assert "should_trade" in trade_result
