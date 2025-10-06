#!/usr/bin/env python3
"""
routine_apiのユニットテスト
"""

import unittest
import sys
import os
import json
import pandas as pd
from unittest.mock import Mock, patch

# パスの設定
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from routine_api import RoutineAnalysisAPI


class TestRoutineAnalysisAPI(unittest.TestCase):
    """RoutineAnalysisAPIクラスのテスト"""

    def setUp(self):
        """テスト前の準備"""
        self.api = RoutineAnalysisAPI()

    def test_api_initialization(self):
        """API初期化のテスト"""
        self.assertIsNotNone(self.api)
        self.assertIsNotNone(self.api.config)
        self.assertIsNotNone(self.api.logger)

    def test_simplified_risk_dashboard_data(self):
        """簡素化リスクダッシュボードデータ取得のテスト"""
        # テスト用ポートフォリオデータ
        test_portfolio = {
            "7203": {
                "stock_data": pd.DataFrame({
                    'Close': [100, 105, 102, 108, 110],
                    'Volume': [1000, 1200, 900, 1300, 1100]
                }),
                "current_price": 110,
                "position_size": 100,
                "account_balance": 1000000
            }
        }
        
        result = self.api.get_simplified_risk_dashboard_data(test_portfolio)
        
        # 結果の検証
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
        
        if result['success']:
            self.assertIn('data', result)
            data = result['data']
            self.assertIn('portfolio_summary', data)
            self.assertIn('risk_metrics', data)
            self.assertIn('recommendations', data)

    def test_error_handling(self):
        """エラーハンドリングのテスト"""
        # 無効なポートフォリオデータ
        invalid_portfolio = None
        
        result = self.api.get_simplified_risk_dashboard_data(invalid_portfolio)
        
        # エラーが適切に処理されることを確認
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
        if not result['success']:
            self.assertIn('error', result)

    def test_config_loading(self):
        """設定ファイル読み込みのテスト"""
        self.assertIsNotNone(self.api.config)
        self.assertIsInstance(self.api.config, dict)

    def test_logger_initialization(self):
        """ロガー初期化のテスト"""
        self.assertIsNotNone(self.api.logger)


if __name__ == '__main__':
    unittest.main()