#!/usr/bin/env python3
"""
簡素化されたリスク管理システムのテスト
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import sys
import os

# パスを追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.simplified_risk_management import (
    SimplifiedRiskManager, 
    SimplifiedRiskLevel, 
    SimplifiedRiskMetrics,
    PortfolioRiskBalance
)
from core.simplified_risk_api import SimplifiedRiskAPI
from core.enhanced_risk_alerts import (
    EnhancedRiskAlerts,
    AlertSeverity,
    AlertType,
    RiskAlert
)


class TestSimplifiedRiskManager(unittest.TestCase):
    """簡素化リスク管理システムのテスト"""
    
    def setUp(self):
        """テスト前準備"""
        self.config = {
            "risk_thresholds": {
                "low_risk_max": 30,
                "medium_risk_max": 70,
                "high_risk_min": 70
            },
            "volatility_thresholds": {
                "low": 0.15,
                "medium": 0.30,
                "high": 0.30
            },
            "max_loss_calculation": {
                "var_multiplier": 2.0,
                "confidence_level": 0.95,
                "position_size_factor": 0.1
            },
            "color_codes": {
                "low_risk": "#4CAF50",
                "medium_risk": "#FF9800",
                "high_risk": "#F44336"
            },
            "recommendations": {
                "low_risk": "投資推奨",
                "medium_risk": "注意深く投資",
                "high_risk": "投資見送り推奨"
            }
        }
        self.risk_manager = SimplifiedRiskManager(self.config)
        
        # テスト用データ
        self.sample_stock_data = pd.DataFrame({
            'Close': [100, 105, 102, 108, 110, 115, 112, 118, 120, 125],
            'Volume': [1000, 1200, 900, 1300, 1100, 1400, 1000, 1500, 1200, 1600]
        })
        
        self.sample_portfolio_data = {
            "7203": {
                "stock_data": self.sample_stock_data,
                "current_price": 125,
                "position_size": 100,
                "account_balance": 1000000
            },
            "6758": {
                "stock_data": self.sample_stock_data * 0.8,  # 異なる価格
                "current_price": 100,
                "position_size": 50,
                "account_balance": 1000000
            }
        }
    
    def test_initialization(self):
        """初期化テスト"""
        self.assertIsNotNone(self.risk_manager)
        self.assertEqual(self.risk_manager.config, self.config)
        self.assertEqual(len(self.risk_manager.risk_history), 0)
    
    def test_calculate_simplified_risk_metrics(self):
        """簡素化リスクメトリクス計算テスト"""
        # 正常ケース
        result = self.risk_manager.calculate_simplified_risk_metrics(
            self.sample_stock_data, 125.0, 100.0, 1000000.0
        )
        
        self.assertIsInstance(result, SimplifiedRiskMetrics)
        self.assertIn(result.risk_level, [SimplifiedRiskLevel.LOW, SimplifiedRiskLevel.MEDIUM, SimplifiedRiskLevel.HIGH])
        self.assertGreaterEqual(result.risk_score, 0)
        self.assertLessEqual(result.risk_score, 100)
        self.assertGreaterEqual(result.max_loss_amount, 0)
        self.assertIn(result.volatility_level, ['low', 'medium', 'high'])
        self.assertIn(result.color_code, ['#4CAF50', '#FF9800', '#F44336'])
        self.assertIsInstance(result.recommendation, str)
        self.assertGreaterEqual(result.confidence, 0)
        self.assertLessEqual(result.confidence, 1)
    
    def test_calculate_simplified_risk_metrics_empty_data(self):
        """空データでの簡素化リスクメトリクス計算テスト"""
        empty_data = pd.DataFrame()
        result = self.risk_manager.calculate_simplified_risk_metrics(
            empty_data, 125.0, 100.0, 1000000.0
        )
        
        self.assertIsInstance(result, SimplifiedRiskMetrics)
        self.assertEqual(result.risk_level, SimplifiedRiskLevel.MEDIUM)
        self.assertEqual(result.max_loss_amount, 0.0)
    
    def test_calculate_simplified_risk_metrics_invalid_price(self):
        """無効価格での簡素化リスクメトリクス計算テスト"""
        result = self.risk_manager.calculate_simplified_risk_metrics(
            self.sample_stock_data, 0.0, 100.0, 1000000.0
        )
        
        self.assertIsInstance(result, SimplifiedRiskMetrics)
        self.assertEqual(result.max_loss_amount, 0.0)
    
    def test_calculate_portfolio_risk_balance(self):
        """ポートフォリオリスクバランス計算テスト"""
        result = self.risk_manager.calculate_portfolio_risk_balance(
            self.sample_portfolio_data, 1000000.0
        )
        
        self.assertIsInstance(result, PortfolioRiskBalance)
        self.assertGreaterEqual(result.total_risk_score, 0)
        self.assertLessEqual(result.total_risk_score, 100)
        self.assertGreaterEqual(result.low_risk_count, 0)
        self.assertGreaterEqual(result.medium_risk_count, 0)
        self.assertGreaterEqual(result.high_risk_count, 0)
        self.assertIsInstance(result.risk_distribution, dict)
        self.assertIn('low', result.risk_distribution)
        self.assertIn('medium', result.risk_distribution)
        self.assertIn('high', result.risk_distribution)
        self.assertIsInstance(result.color_balance, dict)
        self.assertIsInstance(result.overall_recommendation, str)
    
    def test_calculate_portfolio_risk_balance_empty_portfolio(self):
        """空ポートフォリオでのリスクバランス計算テスト"""
        result = self.risk_manager.calculate_portfolio_risk_balance({}, 1000000.0)
        
        self.assertIsInstance(result, PortfolioRiskBalance)
        self.assertEqual(result.total_risk_score, 0.0)
        self.assertEqual(result.low_risk_count, 0)
        self.assertEqual(result.medium_risk_count, 0)
        self.assertEqual(result.high_risk_count, 0)
    
    def test_get_risk_alerts(self):
        """リスクアラート取得テスト"""
        alerts = self.risk_manager.get_risk_alerts(self.sample_portfolio_data)
        
        self.assertIsInstance(alerts, list)
        for alert in alerts:
            self.assertIn('type', alert)
            self.assertIn('symbol', alert)
            self.assertIn('message', alert)
            self.assertIn('severity', alert)
            self.assertIn('color_code', alert)
    
    def test_get_visual_risk_display_data(self):
        """視覚的リスク表示データ取得テスト"""
        display_data = self.risk_manager.get_visual_risk_display_data(self.sample_portfolio_data)
        
        self.assertIsInstance(display_data, dict)
        if display_data:  # データが存在する場合
            self.assertIn('portfolio_balance', display_data)
            self.assertIn('stock_risk_data', display_data)
            self.assertIn('risk_alerts', display_data)
            self.assertIn('display_timestamp', display_data)
    
    def test_get_risk_statistics(self):
        """リスク統計情報取得テスト"""
        # 履歴にデータを追加
        self.risk_manager.risk_history = [
            SimplifiedRiskMetrics(
                risk_level=SimplifiedRiskLevel.LOW,
                max_loss_amount=1000.0,
                risk_score=20.0,
                volatility_level='low',
                color_code='#4CAF50',
                recommendation='投資推奨',
                confidence=0.8
            ),
            SimplifiedRiskMetrics(
                risk_level=SimplifiedRiskLevel.HIGH,
                max_loss_amount=5000.0,
                risk_score=80.0,
                volatility_level='high',
                color_code='#F44336',
                recommendation='投資見送り推奨',
                confidence=0.3
            )
        ]
        
        stats = self.risk_manager.get_risk_statistics()
        
        self.assertIsInstance(stats, dict)
        if stats:  # 統計データが存在する場合
            self.assertIn('total_samples', stats)
            self.assertIn('avg_risk_score', stats)
            self.assertIn('max_risk_score', stats)
            self.assertIn('min_risk_score', stats)
            self.assertIn('risk_level_distribution', stats)
    
    def test_risk_level_determination(self):
        """リスクレベル決定テスト"""
        # 低リスク
        low_risk_score = 20.0
        risk_level = self.risk_manager._determine_risk_level(low_risk_score)
        self.assertEqual(risk_level, SimplifiedRiskLevel.LOW)
        
        # 中リスク
        medium_risk_score = 50.0
        risk_level = self.risk_manager._determine_risk_level(medium_risk_score)
        self.assertEqual(risk_level, SimplifiedRiskLevel.MEDIUM)
        
        # 高リスク
        high_risk_score = 80.0
        risk_level = self.risk_manager._determine_risk_level(high_risk_score)
        self.assertEqual(risk_level, SimplifiedRiskLevel.HIGH)
    
    def test_volatility_level_determination(self):
        """ボラティリティレベル決定テスト"""
        # 低ボラティリティ
        low_volatility = 0.10
        level = self.risk_manager._determine_volatility_level(low_volatility)
        self.assertEqual(level, 'low')
        
        # 中ボラティリティ
        medium_volatility = 0.20
        level = self.risk_manager._determine_volatility_level(medium_volatility)
        self.assertEqual(level, 'medium')
        
        # 高ボラティリティ
        high_volatility = 0.40
        level = self.risk_manager._determine_volatility_level(high_volatility)
        self.assertEqual(level, 'high')
    
    def test_color_code_assignment(self):
        """色分けコード割り当てテスト"""
        # 低リスク
        color = self.risk_manager._get_color_code(SimplifiedRiskLevel.LOW)
        self.assertEqual(color, '#4CAF50')
        
        # 中リスク
        color = self.risk_manager._get_color_code(SimplifiedRiskLevel.MEDIUM)
        self.assertEqual(color, '#FF9800')
        
        # 高リスク
        color = self.risk_manager._get_color_code(SimplifiedRiskLevel.HIGH)
        self.assertEqual(color, '#F44336')
    
    def test_recommendation_assignment(self):
        """推奨事項割り当てテスト"""
        # 低リスク
        recommendation = self.risk_manager._get_recommendation(SimplifiedRiskLevel.LOW)
        self.assertEqual(recommendation, '投資推奨')
        
        # 中リスク
        recommendation = self.risk_manager._get_recommendation(SimplifiedRiskLevel.MEDIUM)
        self.assertEqual(recommendation, '注意深く投資')
        
        # 高リスク
        recommendation = self.risk_manager._get_recommendation(SimplifiedRiskLevel.HIGH)
        self.assertEqual(recommendation, '投資見送り推奨')
    
    def test_max_loss_amount_calculation(self):
        """最大損失額計算テスト"""
        current_price = 100.0
        position_size = 100.0
        var_95 = 0.05
        account_balance = 1000000.0
        
        max_loss = self.risk_manager._calculate_max_loss_amount(
            current_price, position_size, var_95, account_balance
        )
        
        self.assertGreaterEqual(max_loss, 0)
        self.assertLessEqual(max_loss, account_balance * 0.1)  # 口座残高の10%以下
    
    def test_confidence_calculation(self):
        """信頼度計算テスト"""
        volatility = 0.20
        var_95 = 0.05
        max_drawdown = 0.10
        
        confidence = self.risk_manager._calculate_confidence(volatility, var_95, max_drawdown)
        
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
    
    def test_error_handling(self):
        """エラーハンドリングテスト"""
        # Noneデータでのテスト
        result = self.risk_manager.calculate_simplified_risk_metrics(
            None, 125.0, 100.0, 1000000.0
        )
        self.assertIsInstance(result, SimplifiedRiskMetrics)
        
        # 無効なポートフォリオデータでのテスト
        result = self.risk_manager.calculate_portfolio_risk_balance(
            None, 1000000.0
        )
        self.assertIsInstance(result, PortfolioRiskBalance)


class TestSimplifiedRiskAPI(unittest.TestCase):
    """簡素化リスクAPIのテスト"""
    
    def setUp(self):
        """テスト前準備"""
        self.config = {
            "risk_thresholds": {
                "low_risk_max": 30,
                "medium_risk_max": 70,
                "high_risk_min": 70
            }
        }
        self.api = SimplifiedRiskAPI(self.config)
        
        self.sample_stock_data = pd.DataFrame({
            'Close': [100, 105, 102, 108, 110, 115, 112, 118, 120, 125],
            'Volume': [1000, 1200, 900, 1300, 1100, 1400, 1000, 1500, 1200, 1600]
        })
    
    def test_initialization(self):
        """初期化テスト"""
        self.assertIsNotNone(self.api)
        self.assertIsNotNone(self.api.risk_manager)
    
    def test_get_simplified_risk_assessment(self):
        """簡素化リスク評価取得テスト"""
        result = self.api.get_simplified_risk_assessment(
            self.sample_stock_data, 125.0, 100.0, 1000000.0
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
        if result['success']:
            self.assertIn('data', result)
            data = result['data']
            self.assertIn('risk_level', data)
            self.assertIn('risk_score', data)
            self.assertIn('max_loss_amount', data)
            self.assertIn('volatility_level', data)
            self.assertIn('color_code', data)
            self.assertIn('recommendation', data)
            self.assertIn('confidence', data)
            self.assertIn('display_text', data)
            self.assertIn('timestamp', data)
    
    def test_get_simplified_risk_assessment_error(self):
        """簡素化リスク評価取得エラーテスト"""
        result = self.api.get_simplified_risk_assessment(
            None, 125.0, 100.0, 1000000.0
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
        # Noneが渡された場合でも空のDataFrameが作成され、デフォルトメトリクスが返される
        self.assertTrue(result['success'])
        self.assertIn('data', result)
    
    def test_get_portfolio_risk_balance(self):
        """ポートフォリオリスクバランス取得テスト"""
        portfolio_data = {
            "7203": {
                "stock_data": self.sample_stock_data,
                "current_price": 125,
                "position_size": 100,
                "account_balance": 1000000
            }
        }
        
        result = self.api.get_portfolio_risk_balance(portfolio_data, 1000000.0)
        
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
        if result['success']:
            self.assertIn('data', result)
            data = result['data']
            self.assertIn('total_risk_score', data)
            self.assertIn('risk_distribution', data)
            self.assertIn('color_balance', data)
            self.assertIn('overall_recommendation', data)
            self.assertIn('risk_counts', data)
            self.assertIn('risk_summary', data)
            self.assertIn('timestamp', data)
    
    def test_get_risk_alerts(self):
        """リスクアラート取得テスト"""
        portfolio_data = {
            "7203": {
                "stock_data": self.sample_stock_data,
                "current_price": 125,
                "position_size": 100,
                "account_balance": 1000000
            }
        }
        
        result = self.api.get_risk_alerts(portfolio_data)
        
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
        if result['success']:
            self.assertIn('data', result)
            data = result['data']
            self.assertIn('alerts', data)
            self.assertIn('alert_counts', data)
            self.assertIn('high_priority_alerts', data)
            self.assertIn('medium_priority_alerts', data)
            self.assertIn('low_priority_alerts', data)
            self.assertIn('timestamp', data)
    
    def test_get_visual_risk_display(self):
        """視覚的リスク表示データ取得テスト"""
        portfolio_data = {
            "7203": {
                "stock_data": self.sample_stock_data,
                "current_price": 125,
                "position_size": 100,
                "account_balance": 1000000
            }
        }
        
        result = self.api.get_visual_risk_display(portfolio_data)
        
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
        if result['success']:
            self.assertIn('data', result)
            data = result['data']
            self.assertIn('portfolio_summary', data)
            self.assertIn('stock_risk_data', data)
            self.assertIn('risk_alerts', data)
            self.assertIn('chart_data', data)
            self.assertIn('stock_risk_chart', data)
            self.assertIn('display_timestamp', data)
    
    def test_get_risk_statistics(self):
        """リスク統計情報取得テスト"""
        result = self.api.get_risk_statistics()
        
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
        if result['success']:
            self.assertIn('data', result)
    
    def test_update_risk_settings(self):
        """リスク設定更新テスト"""
        settings = {
            "risk_thresholds": {
                "low_risk_max": 25,
                "medium_risk_max": 75,
                "high_risk_min": 75
            }
        }
        
        result = self.api.update_risk_settings(settings)
        
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
        if result['success']:
            self.assertIn('data', result)
            data = result['data']
            self.assertIn('message', data)
            self.assertIn('updated_settings', data)
            self.assertIn('timestamp', data)
    
    def test_export_risk_report(self):
        """リスクレポートエクスポートテスト"""
        portfolio_data = {
            "7203": {
                "stock_data": self.sample_stock_data,
                "current_price": 125,
                "position_size": 100,
                "account_balance": 1000000
            }
        }
        
        result = self.api.export_risk_report(portfolio_data)
        
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
        if result['success']:
            self.assertIn('data', result)
            data = result['data']
            self.assertIn('report_type', data)
            self.assertIn('generated_at', data)
            self.assertIn('portfolio_summary', data)
            self.assertIn('risk_alerts', data)
            self.assertIn('recommendations', data)


class TestEnhancedRiskAlerts(unittest.TestCase):
    """改善されたリスクアラートのテスト"""
    
    def setUp(self):
        """テスト前準備"""
        self.config = {
            "alert_settings": {
                "high_risk_threshold": 70,
                "high_volatility_threshold": 0.3,
                "max_loss_ratio_threshold": 0.1,
                "portfolio_imbalance_threshold": 0.5,
                "position_size_threshold": 0.2,
                "correlation_threshold": 0.8,
                "liquidity_threshold": 100000,
                "alert_retention_days": 30
            }
        }
        self.alerts = EnhancedRiskAlerts(self.config)
        
        self.sample_stock_data = pd.DataFrame({
            'Close': [100, 105, 102, 108, 110, 115, 112, 118, 120, 125],
            'Volume': [1000, 1200, 900, 1300, 1100, 1400, 1000, 1500, 1200, 1600]
        })
        
        self.sample_portfolio_data = {
            "7203": {
                "stock_data": self.sample_stock_data,
                "current_price": 125,
                "position_size": 100,
                "account_balance": 1000000
            }
        }
    
    def test_initialization(self):
        """初期化テスト"""
        self.assertIsNotNone(self.alerts)
        self.assertEqual(self.alerts.config, self.config)
        self.assertEqual(len(self.alerts.alert_history), 0)
    
    def test_generate_comprehensive_alerts(self):
        """包括的アラート生成テスト"""
        alerts = self.alerts.generate_comprehensive_alerts(self.sample_portfolio_data)
        
        self.assertIsInstance(alerts, list)
        for alert in alerts:
            self.assertIsInstance(alert, RiskAlert)
            self.assertIsNotNone(alert.id)
            self.assertIsInstance(alert.type, AlertType)
            self.assertIsInstance(alert.severity, AlertSeverity)
            self.assertIsNotNone(alert.symbol)
            self.assertIsNotNone(alert.title)
            self.assertIsNotNone(alert.message)
            self.assertIsNotNone(alert.recommendation)
            self.assertIsInstance(alert.action_required, bool)
            self.assertIsInstance(alert.created_at, datetime)
            self.assertIsNotNone(alert.color_code)
            self.assertIsNotNone(alert.icon)
    
    def test_get_alert_summary(self):
        """アラートサマリー取得テスト"""
        # テスト用アラートを履歴に追加
        test_alert = RiskAlert(
            id="test_alert_1",
            type=AlertType.HIGH_RISK,
            severity=AlertSeverity.CRITICAL,
            symbol="7203",
            title="テストアラート",
            message="テストメッセージ",
            recommendation="テスト推奨事項",
            action_required=True,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=7),
            metadata={},
            color_code="#F44336",
            icon="error"
        )
        self.alerts.alert_history.append(test_alert)
        
        summary = self.alerts.get_alert_summary()
        
        self.assertIsNotNone(summary)
        self.assertGreaterEqual(summary.total_alerts, 0)
        self.assertGreaterEqual(summary.critical_alerts, 0)
        self.assertGreaterEqual(summary.warning_alerts, 0)
        self.assertGreaterEqual(summary.info_alerts, 0)
        self.assertGreaterEqual(summary.emergency_alerts, 0)
        self.assertIsInstance(summary.alerts_by_type, dict)
        self.assertIsInstance(summary.alerts_by_symbol, dict)
        self.assertIsInstance(summary.recent_alerts, list)
        self.assertIsInstance(summary.top_risks, list)
    
    def test_get_personalized_recommendations(self):
        """個人化推奨事項取得テスト"""
        recommendations = self.alerts.get_personalized_recommendations(
            self.sample_portfolio_data, "medium"
        )
        
        self.assertIsInstance(recommendations, list)
        for rec in recommendations:
            self.assertIn('type', rec)
            self.assertIn('priority', rec)
            self.assertIn('title', rec)
            self.assertIn('description', rec)
            self.assertIn('action', rec)
            self.assertIn('impact', rec)
            self.assertIn('effort', rec)
    
    def test_create_alert_notification(self):
        """アラート通知作成テスト"""
        test_alert = RiskAlert(
            id="test_alert_1",
            type=AlertType.HIGH_RISK,
            severity=AlertSeverity.CRITICAL,
            symbol="7203",
            title="テストアラート",
            message="テストメッセージ",
            recommendation="テスト推奨事項",
            action_required=True,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=7),
            metadata={},
            color_code="#F44336",
            icon="error"
        )
        
        notification = self.alerts.create_alert_notification(test_alert)
        
        self.assertIsInstance(notification, dict)
        self.assertIn('success', notification)
        if notification['success']:
            self.assertIn('data', notification)
            data = notification['data']
            self.assertIn('alert_id', data)
            self.assertIn('title', data)
            self.assertIn('message', data)
            self.assertIn('severity', data)
            self.assertIn('symbol', data)
            self.assertIn('created_at', data)
            self.assertIn('notification_methods', data)
            self.assertIn('metadata', data)
    
    def test_risk_level_determination(self):
        """リスクレベル決定テスト"""
        # 低リスク
        low_risk_score = 20.0
        risk_level = self.alerts._determine_risk_level(low_risk_score)
        self.assertEqual(risk_level, SimplifiedRiskLevel.LOW)
        
        # 中リスク
        medium_risk_score = 50.0
        risk_level = self.alerts._determine_risk_level(medium_risk_score)
        self.assertEqual(risk_level, SimplifiedRiskLevel.MEDIUM)
        
        # 高リスク
        high_risk_score = 80.0
        risk_level = self.alerts._determine_risk_level(high_risk_score)
        self.assertEqual(risk_level, SimplifiedRiskLevel.HIGH)
    
    def test_error_handling(self):
        """エラーハンドリングテスト"""
        # 空データでのテスト
        alerts = self.alerts.generate_comprehensive_alerts({})
        self.assertIsInstance(alerts, list)
        
        # Noneデータでのテスト
        alerts = self.alerts.generate_comprehensive_alerts(None)
        self.assertIsInstance(alerts, list)
        
        # 無効なポートフォリオデータでのテスト
        invalid_portfolio = {
            "7203": {
                "stock_data": None,
                "current_price": 125,
                "position_size": 100,
                "account_balance": 1000000
            }
        }
        alerts = self.alerts.generate_comprehensive_alerts(invalid_portfolio)
        self.assertIsInstance(alerts, list)


if __name__ == '__main__':
    # テスト実行
    unittest.main(verbosity=2)
