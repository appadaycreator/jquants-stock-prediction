"""
手法比較エンジンのテスト
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import json

from core.method_comparison_engine import (
    MethodComparisonEngine,
    ComparisonReport
)
from core.article_method_analyzer import (
    ArticleMethodResult,
    ImprovedMethodResult,
    create_sample_data
)

class TestMethodComparisonEngine:
    """手法比較エンジンのテスト"""
    
    def setup_method(self):
        """テストのセットアップ"""
        self.engine = MethodComparisonEngine(output_dir="test_reports")
        self.sample_data = create_sample_data()
    
    def test_initialization(self):
        """初期化テスト"""
        assert self.engine.output_dir == Path("test_reports")
        assert self.engine.output_dir.exists()
        assert hasattr(self.engine, 'article_analyzer')
        assert hasattr(self.engine, 'improved_analyzer')
        assert hasattr(self.engine, 'comparison')
        assert hasattr(self.engine, 'trading_system')
    
    def test_initialization_with_default_output_dir(self):
        """デフォルト出力ディレクトリでの初期化テスト"""
        engine = MethodComparisonEngine()
        assert engine.output_dir == Path("comparison_reports")
    
    def test_run_comprehensive_comparison_success(self):
        """包括的な手法比較の成功テスト"""
        report = self.engine.run_comprehensive_comparison(self.sample_data)
        
        assert isinstance(report, ComparisonReport)
        assert hasattr(report, 'article_method_performance')
        assert hasattr(report, 'improved_method_performance')
        assert hasattr(report, 'improvement_metrics')
        assert hasattr(report, 'recommendation')
        assert hasattr(report, 'detailed_analysis')
        assert hasattr(report, 'charts_data')
        assert hasattr(report, 'generated_at')
        
        assert isinstance(report.article_method_performance, dict)
        assert isinstance(report.improved_method_performance, dict)
        assert isinstance(report.improvement_metrics, dict)
        assert isinstance(report.recommendation, str)
        assert isinstance(report.detailed_analysis, dict)
        assert isinstance(report.charts_data, dict)
        assert isinstance(report.generated_at, str)
    
    def test_run_comprehensive_comparison_with_invalid_data(self):
        """無効なデータでの包括的な手法比較テスト"""
        invalid_data = pd.DataFrame()
        
        with pytest.raises(Exception):
            self.engine.run_comprehensive_comparison(invalid_data)
    
    def test_analyze_trading_system_success(self):
        """取引システム分析の成功テスト"""
        result = self.engine._analyze_trading_system(self.sample_data)
        
        assert isinstance(result, dict)
        assert 'model_performance' in result
        assert 'backtest_result' in result
        assert 'risk_metrics' in result
        assert 'feature_importance' in result
        
        assert isinstance(result['model_performance'], dict)
        assert isinstance(result['backtest_result'], dict)
        assert isinstance(result['risk_metrics'], dict)
        assert isinstance(result['feature_importance'], dict)
    
    def test_analyze_trading_system_with_invalid_data(self):
        """無効なデータでの取引システム分析テスト"""
        invalid_data = pd.DataFrame()
        
        with pytest.raises(Exception):
            self.engine._analyze_trading_system(invalid_data)
    
    def test_perform_detailed_comparison(self):
        """詳細比較のテスト"""
        # モックの結果を作成
        article_result = ArticleMethodResult(
            accuracy=0.74,
            total_return=-0.01778,
            total_trades=10,
            winning_trades=5,
            losing_trades=5,
            max_drawdown=-0.1,
            sharpe_ratio=0.5,
            profit_factor=1.0,
            analysis_period="2023-01-01 to 2023-12-31",
            method_name="記事の手法"
        )
        
        improved_result = ImprovedMethodResult(
            accuracy=0.9,
            total_return=0.05,
            total_trades=15,
            winning_trades=12,
            losing_trades=3,
            max_drawdown=-0.05,
            sharpe_ratio=1.5,
            profit_factor=2.0,
            analysis_period="2023-01-01 to 2023-12-31",
            method_name="改善手法",
            reliability_threshold=0.7,
            dynamic_stop_loss=True,
            position_sizing="動的"
        )
        
        trading_performance = {
            'backtest_result': {
                'total_return': 0.08,
                'sharpe_ratio': 1.8,
                'max_drawdown': -0.03,
                'total_trades': 20,
                'win_rate': 0.75
            },
            'risk_metrics': {
                'var_95': -0.02,
                'max_drawdown': -0.03,
                'sharpe_ratio': 1.8,
                'sortino_ratio': 2.5,
                'calmar_ratio': 2.0,
                'volatility': 0.12,
                'beta': 1.0
            }
        }
        
        result = self.engine._perform_detailed_comparison(
            article_result, improved_result, trading_performance
        )
        
        assert isinstance(result, dict)
        assert 'basic_comparison' in result
        assert 'trading_comparison' in result
        assert 'improvement_metrics' in result
        assert 'statistical_significance' in result
        assert 'detailed_analysis' in result
        
        # 基本比較の検証
        basic_comparison = result['basic_comparison']
        assert 'accuracy' in basic_comparison
        assert 'total_return' in basic_comparison
        assert 'max_drawdown' in basic_comparison
        assert 'sharpe_ratio' in basic_comparison
        
        # 改善効果の検証
        improvement_metrics = result['improvement_metrics']
        assert 'return_improvement_vs_article' in improvement_metrics
        assert 'return_improvement_vs_trading' in improvement_metrics
        assert 'accuracy_improvement' in improvement_metrics
        assert 'risk_reduction' in improvement_metrics
        assert 'sharpe_improvement' in improvement_metrics
    
    def test_calculate_statistical_significance(self):
        """統計的有意性計算のテスト"""
        article_result = ArticleMethodResult(
            accuracy=0.74,
            total_return=-0.01778,
            total_trades=10,
            winning_trades=5,
            losing_trades=5,
            max_drawdown=-0.1,
            sharpe_ratio=0.5,
            profit_factor=1.0,
            analysis_period="2023-01-01 to 2023-12-31",
            method_name="記事の手法"
        )
        
        improved_result = ImprovedMethodResult(
            accuracy=0.9,
            total_return=0.05,
            total_trades=15,
            winning_trades=12,
            losing_trades=3,
            max_drawdown=-0.05,
            sharpe_ratio=1.5,
            profit_factor=2.0,
            analysis_period="2023-01-01 to 2023-12-31",
            method_name="改善手法",
            reliability_threshold=0.7,
            dynamic_stop_loss=True,
            position_sizing="動的"
        )
        
        trading_performance = {
            'backtest_result': {
                'total_return': 0.08,
                'sharpe_ratio': 1.8,
                'max_drawdown': -0.03
            }
        }
        
        significance = self.engine._calculate_statistical_significance(
            article_result, improved_result, trading_performance
        )
        
        assert isinstance(significance, dict)
        assert 'return_significance' in significance
        assert 'accuracy_significance' in significance
        assert 'risk_significance' in significance
        
        assert significance['return_significance'] in ['p < 0.05', 'p > 0.05']
        assert significance['accuracy_significance'] in ['p < 0.05', 'p > 0.05']
        assert significance['risk_significance'] in ['p < 0.05', 'p > 0.05']
    
    def test_identify_article_method_issues(self):
        """記事の手法の問題点特定のテスト"""
        # 問題のある結果
        problematic_result = ArticleMethodResult(
            accuracy=0.65,
            total_return=-0.05,
            total_trades=10,
            winning_trades=3,
            losing_trades=7,
            max_drawdown=-0.25,
            sharpe_ratio=0.3,
            profit_factor=0.8,
            analysis_period="2023-01-01 to 2023-12-31",
            method_name="記事の手法"
        )
        
        issues = self.engine._identify_article_method_issues(problematic_result)
        
        assert isinstance(issues, list)
        assert len(issues) > 0
        assert any("負のリターン" in issue for issue in issues)
        assert any("低い精度" in issue for issue in issues)
        assert any("大きなドローダウン" in issue for issue in issues)
        assert any("低いシャープレシオ" in issue for issue in issues)
    
    def test_identify_improved_method_advantages(self):
        """改善手法の利点特定のテスト"""
        # 優秀な結果
        excellent_result = ImprovedMethodResult(
            accuracy=0.92,
            total_return=0.15,
            total_trades=20,
            winning_trades=16,
            losing_trades=4,
            max_drawdown=-0.08,
            sharpe_ratio=2.1,
            profit_factor=3.5,
            analysis_period="2023-01-01 to 2023-12-31",
            method_name="改善手法",
            reliability_threshold=0.7,
            dynamic_stop_loss=True,
            position_sizing="動的"
        )
        
        advantages = self.engine._identify_improved_method_advantages(excellent_result)
        
        assert isinstance(advantages, list)
        assert len(advantages) > 0
        assert any("正のリターン" in advantage for advantage in advantages)
        assert any("高い精度" in advantage for advantage in advantages)
        assert any("制御されたドローダウン" in advantage for advantage in advantages)
        assert any("高いシャープレシオ" in advantage for advantage in advantages)
    
    def test_identify_trading_system_benefits(self):
        """取引システムの利点特定のテスト"""
        # 優秀な取引システム結果
        excellent_trading_performance = {
            'backtest_result': {
                'total_return': 0.12,
                'win_rate': 0.75,
                'sharpe_ratio': 2.0,
                'max_drawdown': -0.05
            }
        }
        
        benefits = self.engine._identify_trading_system_benefits(excellent_trading_performance)
        
        assert isinstance(benefits, list)
        assert len(benefits) > 0
        assert any("高いリターン" in benefit for benefit in benefits)
        assert any("高い勝率" in benefit for benefit in benefits)
        assert any("優秀なシャープレシオ" in benefit for benefit in benefits)
        assert any("低いドローダウン" in benefit for benefit in benefits)
    
    def test_generate_charts_data(self):
        """チャートデータ生成のテスト"""
        article_result = ArticleMethodResult(
            accuracy=0.74,
            total_return=-0.01778,
            total_trades=10,
            winning_trades=5,
            losing_trades=5,
            max_drawdown=-0.1,
            sharpe_ratio=0.5,
            profit_factor=1.0,
            analysis_period="2023-01-01 to 2023-12-31",
            method_name="記事の手法"
        )
        
        improved_result = ImprovedMethodResult(
            accuracy=0.9,
            total_return=0.05,
            total_trades=15,
            winning_trades=12,
            losing_trades=3,
            max_drawdown=-0.05,
            sharpe_ratio=1.5,
            profit_factor=2.0,
            analysis_period="2023-01-01 to 2023-12-31",
            method_name="改善手法",
            reliability_threshold=0.7,
            dynamic_stop_loss=True,
            position_sizing="動的"
        )
        
        trading_performance = {
            'backtest_result': {
                'total_return': 0.08,
                'sharpe_ratio': 1.8,
                'max_drawdown': -0.03,
                'equity_curve': [100000, 101000, 102000, 103000, 104000]
            },
            'feature_importance': {
                'model1': {'feature1': 0.3, 'feature2': 0.7}
            }
        }
        
        charts_data = self.engine._generate_charts_data(
            self.sample_data, article_result, improved_result, trading_performance
        )
        
        assert isinstance(charts_data, dict)
        assert 'equity_curves' in charts_data
        assert 'return_distributions' in charts_data
        assert 'risk_metrics_comparison' in charts_data
        assert 'feature_importance' in charts_data
        
        # エクイティカーブの検証
        equity_curves = charts_data['equity_curves']
        assert 'article_method' in equity_curves
        assert 'improved_method' in equity_curves
        assert 'trading_system' in equity_curves
        
        for method, curve in equity_curves.items():
            assert isinstance(curve, list)
            assert len(curve) > 0
            assert all(isinstance(val, (int, float)) for val in curve)
    
    def test_simulate_equity_curve(self):
        """エクイティカーブシミュレーションのテスト"""
        result = ArticleMethodResult(
            accuracy=0.74,
            total_return=0.05,
            total_trades=10,
            winning_trades=5,
            losing_trades=5,
            max_drawdown=-0.1,
            sharpe_ratio=0.5,
            profit_factor=1.0,
            analysis_period="2023-01-01 to 2023-12-31",
            method_name="記事の手法"
        )
        
        equity_curve = self.engine._simulate_equity_curve(self.sample_data, result)
        
        assert isinstance(equity_curve, list)
        assert len(equity_curve) == len(self.sample_data)
        assert all(isinstance(val, (int, float)) for val in equity_curve)
        assert equity_curve[0] == 100000  # 初期資本
    
    def test_calculate_return_distribution(self):
        """リターン分布計算のテスト"""
        equity_curve = [100000, 101000, 102000, 103000, 104000, 105000]
        distribution = self.engine._calculate_return_distribution(equity_curve)
        
        assert isinstance(distribution, dict)
        assert 'mean' in distribution
        assert 'std' in distribution
        assert 'skewness' in distribution
        assert 'kurtosis' in distribution
        assert 'percentiles' in distribution
        
        assert isinstance(distribution['mean'], (int, float))
        assert isinstance(distribution['std'], (int, float))
        assert isinstance(distribution['skewness'], (int, float))
        assert isinstance(distribution['kurtosis'], (int, float))
        assert isinstance(distribution['percentiles'], dict)
        
        percentiles = distribution['percentiles']
        assert '5th' in percentiles
        assert '25th' in percentiles
        assert '50th' in percentiles
        assert '75th' in percentiles
        assert '95th' in percentiles
    
    def test_generate_recommendation_positive_improvement(self):
        """正の改善での推奨事項生成テスト"""
        detailed_comparison = {
            'improvement_metrics': {
                'return_improvement_vs_article': 0.1,
                'accuracy_improvement': 0.15,
                'risk_reduction': 0.05,
                'sharpe_improvement': 0.8
            }
        }
        
        recommendation = self.engine._generate_recommendation(detailed_comparison)
        
        assert isinstance(recommendation, str)
        assert len(recommendation) > 0
        assert "改善された手法" in recommendation or "推奨" in recommendation
    
    def test_generate_recommendation_negative_improvement(self):
        """負の改善での推奨事項生成テスト"""
        detailed_comparison = {
            'improvement_metrics': {
                'return_improvement_vs_article': -0.05,
                'accuracy_improvement': -0.1,
                'risk_reduction': -0.02,
                'sharpe_improvement': -0.3
            }
        }
        
        recommendation = self.engine._generate_recommendation(detailed_comparison)
        
        assert isinstance(recommendation, str)
        assert len(recommendation) > 0
        assert "改善が必要" in recommendation or "調整" in recommendation
    
    def test_save_report(self):
        """レポート保存のテスト"""
        report = ComparisonReport(
            article_method_performance={},
            improved_method_performance={},
            improvement_metrics={},
            recommendation="テスト推奨事項",
            detailed_analysis={},
            charts_data={},
            generated_at=datetime.now().isoformat()
        )
        
        self.engine._save_report(report)
        
        # レポートファイルが作成されていることを確認
        report_files = list(self.engine.output_dir.glob("comparison_report_*.json"))
        assert len(report_files) > 0
        
        # 最新のレポートファイルを読み込み
        latest_report = max(report_files, key=lambda x: x.stat().st_mtime)
        with open(latest_report, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        assert saved_data['recommendation'] == "テスト推奨事項"
    
    def test_generate_summary_report(self):
        """サマリーレポート生成のテスト"""
        report = ComparisonReport(
            article_method_performance={
                'method_name': '記事の手法',
                'total_return': -0.01778,
                'accuracy': 0.74,
                'max_drawdown': -0.1,
                'sharpe_ratio': 0.5
            },
            improved_method_performance={
                'method_name': '改善手法',
                'total_return': 0.05,
                'accuracy': 0.9,
                'max_drawdown': -0.05,
                'sharpe_ratio': 1.5
            },
            improvement_metrics={
                'return_improvement_vs_article': 0.06778,
                'accuracy_improvement': 0.16,
                'risk_reduction': 0.05,
                'sharpe_improvement': 1.0
            },
            recommendation="改善された手法を強く推奨します。",
            detailed_analysis={},
            charts_data={},
            generated_at=datetime.now().isoformat()
        )
        
        summary = self.engine.generate_summary_report(report)
        
        assert isinstance(summary, str)
        assert len(summary) > 0
        assert "手法比較レポート" in summary
        assert "記事の手法" in summary
        assert "改善手法" in summary
        assert "改善された手法を強く推奨します" in summary

class TestComparisonReport:
    """比較レポートのテスト"""
    
    def test_comparison_report_creation(self):
        """比較レポート作成のテスト"""
        report = ComparisonReport(
            article_method_performance={'test': 'data'},
            improved_method_performance={'test': 'data'},
            improvement_metrics={'test': 'data'},
            recommendation="テスト推奨事項",
            detailed_analysis={'test': 'data'},
            charts_data={'test': 'data'},
            generated_at=datetime.now().isoformat()
        )
        
        assert report.article_method_performance == {'test': 'data'}
        assert report.improved_method_performance == {'test': 'data'}
        assert report.improvement_metrics == {'test': 'data'}
        assert report.recommendation == "テスト推奨事項"
        assert report.detailed_analysis == {'test': 'data'}
        assert report.charts_data == {'test': 'data'}
        assert isinstance(report.generated_at, str)

class TestIntegration:
    """統合テスト"""
    
    def setup_method(self):
        """テストのセットアップ"""
        self.engine = MethodComparisonEngine()
    
    def test_full_comparison_pipeline(self):
        """完全な比較パイプラインのテスト"""
        data = create_sample_data()
        
        # 包括的な比較の実行
        report = self.engine.run_comprehensive_comparison(data)
        
        # 結果の検証
        assert isinstance(report, ComparisonReport)
        assert report.article_method_performance is not None
        assert report.improved_method_performance is not None
        assert report.improvement_metrics is not None
        assert report.recommendation is not None
        
        # サマリーレポートの生成
        summary = self.engine.generate_summary_report(report)
        assert isinstance(summary, str)
        assert len(summary) > 0
    
    def test_error_handling(self):
        """エラーハンドリングのテスト"""
        # 空のデータフレーム
        empty_data = pd.DataFrame()
        
        with pytest.raises(Exception):
            self.engine.run_comprehensive_comparison(empty_data)
        
        # 不正なデータ型
        invalid_data = "invalid_data"
        
        with pytest.raises(Exception):
            self.engine.run_comprehensive_comparison(invalid_data)
    
    def test_performance_requirements(self):
        """パフォーマンス要件のテスト"""
        data = create_sample_data()
        
        # 包括的な比較の実行時間
        import time
        start_time = time.time()
        
        report = self.engine.run_comprehensive_comparison(data)
        
        execution_time = time.time() - start_time
        
        # 実行時間が120秒以内であることを確認
        assert execution_time < 120
        
        # 結果の妥当性確認
        assert isinstance(report, ComparisonReport)
        assert report.article_method_performance is not None
        assert report.improved_method_performance is not None
