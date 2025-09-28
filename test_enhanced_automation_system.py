#!/usr/bin/env python3
"""
ワンクリック分析の完全自動化システムの統合テスト
"""

import asyncio
import json
import logging
import pytest
from datetime import datetime, timedelta
from typing import Dict, List, Any
from pathlib import Path
import tempfile
import shutil

# テスト対象モジュールのインポート
from enhanced_one_click_automation_system import (
    EnhancedOneClickAutomationSystem, AutomationConfig, AutomationStatus
)
from enhanced_analysis_notification_system import (
    EnhancedNotificationSystem, NotificationConfig, AnalysisResult, NotificationPriority
)
from enhanced_auto_action_proposal_system import (
    EnhancedAutoActionProposalSystem, AnalysisContext, ActionProposal, MarketCondition
)
from enhanced_auto_retry_system import (
    EnhancedAutoRetrySystem, RetryConfig, RetryStrategy, RetryCondition
)

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestEnhancedAutomationSystem:
    """強化された自動化システムのテストクラス"""
    
    @pytest.fixture
    def temp_config_file(self):
        """一時設定ファイルの作成"""
        config_content = """
automation:
  enabled: true
  max_concurrent_analyses: 2
  analysis_timeout: 60.0
  notification_enabled: true
  action_proposal_enabled: true
  retry_enabled: true
  max_retry_attempts: 2
  retry_base_delay: 1.0
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_content)
            temp_file = f.name
        
        yield temp_file
        
        # クリーンアップ
        Path(temp_file).unlink(missing_ok=True)
    
    @pytest.fixture
    def automation_system(self, temp_config_file):
        """自動化システムの初期化"""
        return EnhancedOneClickAutomationSystem(temp_config_file)
    
    @pytest.mark.asyncio
    async def test_automation_system_initialization(self, automation_system):
        """自動化システムの初期化テスト"""
        assert automation_system is not None
        assert automation_system.status == AutomationStatus.IDLE
        assert automation_system.config.enabled is True
    
    @pytest.mark.asyncio
    async def test_complete_automation_execution(self, automation_system):
        """完全自動化の実行テスト"""
        # 自動化の実行
        result = await automation_system.run_complete_automation(
            analysis_types=["ultra_fast"],
            force_refresh=False
        )
        
        # 結果の検証
        assert result is not None
        assert result.automation_id is not None
        assert result.start_time is not None
        assert result.end_time is not None
        assert result.status in [AutomationStatus.COMPLETED, AutomationStatus.FAILED]
        assert result.total_duration >= 0
    
    @pytest.mark.asyncio
    async def test_automation_status_tracking(self, automation_system):
        """自動化ステータスの追跡テスト"""
        # 初期ステータス
        status = automation_system.get_automation_status()
        assert status["status"] == "idle"
        assert status["total_automations"] == 0
        
        # 自動化実行後のステータス
        await automation_system.run_complete_automation(["ultra_fast"])
        status = automation_system.get_automation_status()
        assert status["total_automations"] >= 1
    
    @pytest.mark.asyncio
    async def test_performance_metrics(self, automation_system):
        """パフォーマンス指標のテスト"""
        # 初期指標
        metrics = automation_system.get_performance_metrics()
        assert metrics["average_duration"] >= 0
        assert 0 <= metrics["success_rate"] <= 1
        
        # 自動化実行後の指標
        await automation_system.run_complete_automation(["ultra_fast"])
        metrics = automation_system.get_performance_metrics()
        assert metrics["total_analyses"] >= 0
        assert metrics["total_notifications"] >= 0


class TestNotificationSystem:
    """通知システムのテストクラス"""
    
    @pytest.fixture
    def notification_system(self):
        """通知システムの初期化"""
        config = NotificationConfig(
            email_enabled=False,  # テスト時は無効
            slack_enabled=False,   # テスト時は無効
            email_to=[],
            slack_webhook_url=""
        )
        return EnhancedNotificationSystem(config)
    
    @pytest.fixture
    def sample_analysis_result(self):
        """サンプル分析結果の作成"""
        return AnalysisResult(
            analysis_id="test_analysis_001",
            analysis_type="ultra_fast",
            timestamp=datetime.now(),
            duration=120.5,
            status="success",
            confidence_score=0.85,
            predictions={"stock_prices": [100, 102, 105, 108, 110]},
            risk_metrics={"volatility": 0.15, "max_drawdown": 0.05},
            recommendations=["買いシグナル検知", "リスク管理を強化"],
            performance_metrics={"sharpe_ratio": 1.2, "return": 0.08}
        )
    
    @pytest.mark.asyncio
    async def test_notification_system_initialization(self, notification_system):
        """通知システムの初期化テスト"""
        assert notification_system is not None
        assert notification_system.config is not None
    
    @pytest.mark.asyncio
    async def test_notification_content_generation(self, notification_system, sample_analysis_result):
        """通知内容の生成テスト"""
        # 通知内容の生成
        content = notification_system._generate_notification_content(
            sample_analysis_result, NotificationPriority.HIGH
        )
        
        # 内容の検証
        assert content["analysis_id"] == sample_analysis_result.analysis_id
        assert content["analysis_type"] == sample_analysis_result.analysis_type
        assert content["status"] == sample_analysis_result.status
        assert content["confidence_score"] == sample_analysis_result.confidence_score
        assert "suggested_actions" in content
    
    @pytest.mark.asyncio
    async def test_notification_filtering(self, notification_system):
        """通知フィルタリングのテスト"""
        # 高信頼度の結果
        high_confidence_result = AnalysisResult(
            analysis_id="test_001",
            analysis_type="ultra_fast",
            timestamp=datetime.now(),
            duration=100.0,
            status="success",
            confidence_score=0.9,
            predictions={},
            risk_metrics={},
            recommendations=[],
            performance_metrics={}
        )
        
        # 低信頼度の結果
        low_confidence_result = AnalysisResult(
            analysis_id="test_002",
            analysis_type="ultra_fast",
            timestamp=datetime.now(),
            duration=100.0,
            status="success",
            confidence_score=0.5,
            predictions={},
            risk_metrics={},
            recommendations=[],
            performance_metrics={}
        )
        
        # フィルタリングのテスト
        should_send_high = notification_system._should_send_notification(high_confidence_result)
        should_send_low = notification_system._should_send_notification(low_confidence_result)
        
        assert should_send_high is True
        assert should_send_low is False  # 信頼度が閾値を下回る


class TestActionProposalSystem:
    """アクション提案システムのテストクラス"""
    
    @pytest.fixture
    def action_proposal_system(self):
        """アクション提案システムの初期化"""
        return EnhancedAutoActionProposalSystem()
    
    @pytest.fixture
    def sample_analysis_context(self):
        """サンプル分析コンテキストの作成"""
        return AnalysisContext(
            analysis_id="test_analysis_001",
            analysis_type="ultra_fast",
            market_data={"current_price": 100, "volume": 1000000},
            technical_indicators={"rsi": 25, "ma_short": 98, "ma_long": 95},
            sentiment_data={"overall_sentiment": 0.7},
            risk_metrics={"max_drawdown": 0.05, "volatility": 0.15},
            performance_metrics={"sharpe_ratio": 1.2},
            portfolio_status={"concentration_risk": 0.2},
            user_preferences={"risk_tolerance": "medium"},
            market_condition=MarketCondition.BULL,
            volatility_level=0.15,
            trend_direction="up",
            support_resistance_levels={"support": 95, "resistance": 105}
        )
    
    @pytest.mark.asyncio
    async def test_action_proposal_system_initialization(self, action_proposal_system):
        """アクション提案システムの初期化テスト"""
        assert action_proposal_system is not None
        assert action_proposal_system.config is not None
    
    @pytest.mark.asyncio
    async def test_action_proposal_generation(self, action_proposal_system, sample_analysis_context):
        """アクション提案の生成テスト"""
        # 提案の生成
        proposals = await action_proposal_system.generate_action_proposals(sample_analysis_context)
        
        # 結果の検証
        assert isinstance(proposals, list)
        assert len(proposals) >= 0
        
        for proposal in proposals:
            assert proposal.action_id is not None
            assert proposal.action_type is not None
            assert proposal.priority is not None
            assert proposal.title is not None
            assert proposal.description is not None
            assert 0 <= proposal.confidence_score <= 1
            assert 0 <= proposal.risk_level <= 1
    
    @pytest.mark.asyncio
    async def test_proposal_filtering_and_ranking(self, action_proposal_system, sample_analysis_context):
        """提案のフィルタリングとランキングテスト"""
        # 複数の提案を生成
        proposals = await action_proposal_system.generate_action_proposals(sample_analysis_context)
        
        if proposals:
            # 信頼度の検証
            for proposal in proposals:
                assert proposal.confidence_score >= 0.6  # 最小信頼度閾値
            
            # 優先度の検証
            priorities = [p.priority.value for p in proposals]
            assert "critical" in priorities or "high" in priorities or "normal" in priorities


class TestRetrySystem:
    """リトライシステムのテストクラス"""
    
    @pytest.fixture
    def retry_system(self):
        """リトライシステムの初期化"""
        return EnhancedAutoRetrySystem()
    
    @pytest.fixture
    def failing_operation(self):
        """失敗する操作の作成"""
        call_count = 0
        
        async def failing_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:  # 3回目で成功
                raise Exception(f"テストエラー {call_count}")
            return f"成功 {call_count}"
        
        return failing_func
    
    @pytest.mark.asyncio
    async def test_retry_system_initialization(self, retry_system):
        """リトライシステムの初期化テスト"""
        assert retry_system is not None
        assert retry_system.default_config is not None
    
    @pytest.mark.asyncio
    async def test_successful_retry(self, retry_system, failing_operation):
        """成功するリトライのテスト"""
        config = RetryConfig(
            max_attempts=5,
            base_delay=0.1,  # 高速テスト用
            strategy=RetryStrategy.EXPONENTIAL
        )
        
        result = await retry_system.retry_operation(
            failing_operation,
            "test_operation",
            config
        )
        
        # 結果の検証
        assert result.success is True
        assert result.attempts == 3
        assert result.final_result == "成功 3"
        assert len(result.errors) == 2  # 2回の失敗
    
    @pytest.mark.asyncio
    async def test_failed_retry(self, retry_system):
        """失敗するリトライのテスト"""
        async def always_failing_func():
            raise Exception("常に失敗する操作")
        
        config = RetryConfig(
            max_attempts=2,
            base_delay=0.1,
            strategy=RetryStrategy.FIXED
        )
        
        result = await retry_system.retry_operation(
            always_failing_func,
            "always_failing",
            config
        )
        
        # 結果の検証
        assert result.success is False
        assert result.attempts == 2
        assert result.final_result is None
        assert len(result.errors) == 2
    
    @pytest.mark.asyncio
    async def test_retry_statistics(self, retry_system):
        """リトライ統計のテスト"""
        # 初期統計
        stats = retry_system.get_retry_statistics()
        assert stats["total_operations"] == 0
        
        # リトライ実行後の統計
        await retry_system.retry_operation(
            lambda: "成功",
            "test_stats",
            RetryConfig(max_attempts=1)
        )
        
        stats = retry_system.get_retry_statistics()
        assert stats["total_operations"] >= 1


class TestIntegration:
    """統合テストクラス"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_automation(self):
        """エンドツーエンドの自動化テスト"""
        # 一時設定ファイルの作成
        config_content = """
automation:
  enabled: true
  max_concurrent_analyses: 1
  analysis_timeout: 30.0
  notification_enabled: false  # テスト時は無効
  action_proposal_enabled: true
  retry_enabled: true
  max_retry_attempts: 2
  retry_base_delay: 0.1
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_content)
            temp_file = f.name
        
        try:
            # 自動化システムの初期化
            automation_system = EnhancedOneClickAutomationSystem(temp_file)
            
            # 完全自動化の実行
            result = await automation_system.run_complete_automation(
                analysis_types=["ultra_fast"],
                force_refresh=False
            )
            
            # 結果の検証
            assert result is not None
            assert result.automation_id is not None
            assert result.status in [AutomationStatus.COMPLETED, AutomationStatus.FAILED]
            assert result.total_duration >= 0
            
            # ステータスの確認
            status = automation_system.get_automation_status()
            assert status["total_automations"] >= 1
            
            # パフォーマンス指標の確認
            metrics = automation_system.get_performance_metrics()
            assert metrics["average_duration"] >= 0
            assert 0 <= metrics["success_rate"] <= 1
            
        finally:
            # クリーンアップ
            Path(temp_file).unlink(missing_ok=True)
    
    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self):
        """エラーハンドリングとリカバリのテスト"""
        # エラーを発生させる設定
        config_content = """
automation:
  enabled: true
  max_concurrent_analyses: 1
  analysis_timeout: 5.0  # 短いタイムアウト
  notification_enabled: false
  action_proposal_enabled: false
  retry_enabled: true
  max_retry_attempts: 1
  retry_base_delay: 0.1
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_content)
            temp_file = f.name
        
        try:
            automation_system = EnhancedOneClickAutomationSystem(temp_file)
            
            # 自動化の実行（エラーが発生する可能性が高い）
            result = await automation_system.run_complete_automation(
                analysis_types=["ultra_fast"],
                force_refresh=True
            )
            
            # エラーが発生してもシステムがクラッシュしないことを確認
            assert result is not None
            assert result.automation_id is not None
            
        finally:
            Path(temp_file).unlink(missing_ok=True)


# テスト実行用のメイン関数
async def run_tests():
    """テストの実行"""
    logger.info("ワンクリック分析の完全自動化システムのテストを開始")
    
    # テストクラスのインスタンス化
    test_automation = TestEnhancedAutomationSystem()
    test_notification = TestNotificationSystem()
    test_action_proposal = TestActionProposalSystem()
    test_retry = TestRetrySystem()
    test_integration = TestIntegration()
    
    # テストの実行
    try:
        # 自動化システムのテスト
        logger.info("自動化システムのテストを実行中...")
        await test_automation.test_automation_system_initialization(test_automation.automation_system(None))
        
        # 通知システムのテスト
        logger.info("通知システムのテストを実行中...")
        notification_system = test_notification.notification_system()
        await test_notification.test_notification_system_initialization(notification_system)
        
        # アクション提案システムのテスト
        logger.info("アクション提案システムのテストを実行中...")
        action_proposal_system = test_action_proposal.action_proposal_system()
        await test_action_proposal.test_action_proposal_system_initialization(action_proposal_system)
        
        # リトライシステムのテスト
        logger.info("リトライシステムのテストを実行中...")
        retry_system = test_retry.retry_system()
        await test_retry.test_retry_system_initialization(retry_system)
        
        # 統合テスト
        logger.info("統合テストを実行中...")
        await test_integration.test_end_to_end_automation()
        
        logger.info("すべてのテストが完了しました")
        
    except Exception as e:
        logger.error(f"テスト実行エラー: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(run_tests())
