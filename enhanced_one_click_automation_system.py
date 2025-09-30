#!/usr/bin/env python3
"""
ワンクリック分析の完全自動化システム
超高速分析 + 自動通知 + 自動アクション提案 + 自動リトライの統合システム
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import yaml
from pathlib import Path
import pandas as pd
import numpy as np

# 自作モジュールのインポート
from enhanced_analysis_notification_system import (
    EnhancedNotificationSystem,
    NotificationConfig,
    AnalysisResult,
    NotificationPriority,
)
from enhanced_auto_action_proposal_system import (
    EnhancedAutoActionProposalSystem,
    AnalysisContext,
    ActionProposal,
    MarketCondition,
)
from enhanced_auto_retry_system import (
    EnhancedAutoRetrySystem,
    RetryConfig,
    RetryStrategy,
    RetryCondition,
)

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/one_click_automation.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class AutomationStatus(Enum):
    """自動化ステータス"""

    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class AutomationConfig:
    """自動化設定"""

    # 基本設定
    enabled: bool = True
    max_concurrent_analyses: int = 3
    analysis_timeout: float = 300.0  # 5分

    # 通知設定
    notification_enabled: bool = True
    notification_priority_threshold: float = 0.7

    # アクション提案設定
    action_proposal_enabled: bool = True
    max_proposals_per_analysis: int = 5

    # リトライ設定
    retry_enabled: bool = True
    max_retry_attempts: int = 3
    retry_base_delay: float = 2.0

    # スケジューリング設定
    auto_schedule_enabled: bool = True
    morning_analysis_time: str = "09:00"
    evening_analysis_time: str = "15:00"
    timezone: str = "Asia/Tokyo"

    # パフォーマンス設定
    cache_enabled: bool = True
    cache_duration_hours: int = 24
    parallel_processing: bool = True


@dataclass
class AutomationResult:
    """自動化結果"""

    automation_id: str
    start_time: datetime
    end_time: Optional[datetime]
    status: AutomationStatus
    analysis_results: List[Dict[str, Any]]
    notifications_sent: int
    action_proposals: List[ActionProposal]
    retry_count: int
    total_duration: float
    error_message: Optional[str] = None

    def __post_init__(self):
        if self.end_time is None:
            self.end_time = datetime.now()
        self.total_duration = (self.end_time - self.start_time).total_seconds()


class EnhancedOneClickAutomationSystem:
    """ワンクリック分析の完全自動化システム"""

    def __init__(self, config_file: str = "automation_config.yaml"):
        self.config_file = config_file
        self.config = self._load_config()
        self.status = AutomationStatus.IDLE
        self.automation_history = []

        # サブシステムの初期化
        self.notification_system = self._initialize_notification_system()
        self.action_proposal_system = self._initialize_action_proposal_system()
        self.retry_system = self._initialize_retry_system()

        # 分析システムの初期化（既存システムとの統合）
        self.analysis_systems = self._initialize_analysis_systems()

    def _load_config(self) -> AutomationConfig:
        """設定の読み込み"""
        default_config = AutomationConfig()

        try:
            if Path(self.config_file).exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    yaml_config = yaml.safe_load(f)

                # YAML設定をAutomationConfigにマッピング
                if "automation" in yaml_config:
                    auto_config = yaml_config["automation"]
                    for key, value in auto_config.items():
                        if hasattr(default_config, key):
                            setattr(default_config, key, value)

            return default_config
        except Exception as e:
            logger.error(f"設定読み込みエラー: {e}")
            return default_config

    def _initialize_notification_system(self) -> EnhancedNotificationSystem:
        """通知システムの初期化"""
        notification_config = NotificationConfig(
            email_enabled=self.config.notification_enabled,
            slack_enabled=self.config.notification_enabled,
            email_user="",  # 環境変数から取得
            email_password="",  # 環境変数から取得
            email_to=[],  # 設定ファイルから取得
            slack_webhook_url="",  # 環境変数から取得
            slack_channel="#stock-analysis",
        )

        return EnhancedNotificationSystem(notification_config)

    def _initialize_action_proposal_system(self) -> EnhancedAutoActionProposalSystem:
        """アクション提案システムの初期化"""
        return EnhancedAutoActionProposalSystem()

    def _initialize_retry_system(self) -> EnhancedAutoRetrySystem:
        """リトライシステムの初期化"""
        return EnhancedAutoRetrySystem()

    def _initialize_analysis_systems(self) -> Dict[str, Any]:
        """分析システムの初期化"""
        # 既存の分析システムとの統合
        systems = {}

        try:
            # 統合J-Quantsシステム
            from unified_jquants_system import UnifiedJQuantsSystem

            systems["jquants"] = UnifiedJQuantsSystem()
        except ImportError:
            logger.warning("UnifiedJQuantsSystemのインポートに失敗")

        try:
            # Web分析ランナー
            from web_analysis_runner import WebAnalysisRunner

            systems["web_analysis"] = WebAnalysisRunner()
        except ImportError:
            logger.warning("WebAnalysisRunnerのインポートに失敗")

        return systems

    async def run_complete_automation(
        self, analysis_types: List[str] = None, force_refresh: bool = False
    ) -> AutomationResult:
        """完全自動化の実行"""
        automation_id = f"automation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.now()

        logger.info(f"完全自動化開始: {automation_id}")
        self.status = AutomationStatus.RUNNING

        try:
            # デフォルトの分析タイプ
            if analysis_types is None:
                analysis_types = ["ultra_fast", "comprehensive", "sentiment"]

            # 分析結果の格納
            analysis_results = []
            action_proposals = []
            notifications_sent = 0
            retry_count = 0

            # 各分析タイプの実行
            for analysis_type in analysis_types:
                try:
                    # 分析の実行（リトライ付き）
                    analysis_result = await self._execute_analysis_with_retry(
                        analysis_type, force_refresh
                    )

                    if analysis_result:
                        analysis_results.append(analysis_result)

                        # アクション提案の生成
                        if self.config.action_proposal_enabled:
                            proposals = await self._generate_action_proposals(
                                analysis_result, analysis_type
                            )
                            action_proposals.extend(proposals)

                        # 通知の送信
                        if self.config.notification_enabled:
                            notification_sent = await self._send_analysis_notification(
                                analysis_result, analysis_type
                            )
                            if notification_sent:
                                notifications_sent += 1

                except Exception as e:
                    logger.error(f"分析実行エラー ({analysis_type}): {e}")
                    retry_count += 1

                    # エラー通知の送信
                    if self.config.notification_enabled:
                        await self._send_error_notification(analysis_type, str(e))

            # 結果の統合
            result = AutomationResult(
                automation_id=automation_id,
                start_time=start_time,
                end_time=datetime.now(),
                status=(
                    AutomationStatus.COMPLETED
                    if analysis_results
                    else AutomationStatus.FAILED
                ),
                analysis_results=analysis_results,
                notifications_sent=notifications_sent,
                action_proposals=action_proposals,
                retry_count=retry_count,
                total_duration=0.0,  # __post_init__で計算
            )

            # 履歴の記録
            self.automation_history.append(result)

            logger.info(f"完全自動化完了: {automation_id} - {len(analysis_results)}件の分析完了")
            return result

        except Exception as e:
            logger.error(f"完全自動化エラー: {e}")
            self.status = AutomationStatus.FAILED

            result = AutomationResult(
                automation_id=automation_id,
                start_time=start_time,
                end_time=datetime.now(),
                status=AutomationStatus.FAILED,
                analysis_results=[],
                notifications_sent=0,
                action_proposals=[],
                retry_count=0,
                total_duration=0.0,
                error_message=str(e),
            )

            self.automation_history.append(result)
            return result

        finally:
            self.status = AutomationStatus.IDLE

    async def _execute_analysis_with_retry(
        self, analysis_type: str, force_refresh: bool = False
    ) -> Optional[Dict[str, Any]]:
        """リトライ付き分析実行"""
        if not self.config.retry_enabled:
            return await self._execute_single_analysis(analysis_type, force_refresh)

        # リトライ設定
        retry_config = RetryConfig(
            max_attempts=self.config.max_retry_attempts,
            base_delay=self.config.retry_base_delay,
            strategy=RetryStrategy.EXPONENTIAL,
            condition=RetryCondition.ALL_ERRORS,
        )

        # リトライ付き実行
        result = await self.retry_system.retry_operation(
            self._execute_single_analysis,
            f"analysis_{analysis_type}",
            retry_config,
            analysis_type,
            force_refresh,
        )

        return result.final_result if result.success else None

    async def _execute_single_analysis(
        self, analysis_type: str, force_refresh: bool = False
    ) -> Dict[str, Any]:
        """単一分析の実行"""
        logger.info(f"分析実行開始: {analysis_type}")

        try:
            if analysis_type == "ultra_fast":
                return await self._run_ultra_fast_analysis(force_refresh)
            elif analysis_type == "comprehensive":
                return await self._run_comprehensive_analysis(force_refresh)
            elif analysis_type == "sentiment":
                return await self._run_sentiment_analysis(force_refresh)
            elif analysis_type == "trading":
                return await self._run_trading_analysis(force_refresh)
            else:
                raise ValueError(f"未対応の分析タイプ: {analysis_type}")

        except Exception as e:
            logger.error(f"分析実行エラー ({analysis_type}): {e}")
            raise

    async def _run_ultra_fast_analysis(
        self, force_refresh: bool = False
    ) -> Dict[str, Any]:
        """超高速分析の実行"""
        if "web_analysis" in self.analysis_systems:
            runner = self.analysis_systems["web_analysis"]
            return await asyncio.get_event_loop().run_in_executor(
                None, runner.run_ultra_fast_analysis
            )
        else:
            # フォールバック実装
            return await self._fallback_analysis("ultra_fast")

    async def _run_comprehensive_analysis(
        self, force_refresh: bool = False
    ) -> Dict[str, Any]:
        """包括的分析の実行"""
        if "jquants" in self.analysis_systems:
            system = self.analysis_systems["jquants"]
            return await asyncio.get_event_loop().run_in_executor(
                None, system.run_comprehensive_analysis
            )
        else:
            return await self._fallback_analysis("comprehensive")

    async def _run_sentiment_analysis(
        self, force_refresh: bool = False
    ) -> Dict[str, Any]:
        """感情分析の実行"""
        # 感情分析システムの実装
        return await self._fallback_analysis("sentiment")

    async def _run_trading_analysis(
        self, force_refresh: bool = False
    ) -> Dict[str, Any]:
        """トレーディング分析の実行"""
        # トレーディング分析システムの実装
        return await self._fallback_analysis("trading")

    async def _fallback_analysis(self, analysis_type: str) -> Dict[str, Any]:
        """フォールバック分析の実装"""
        # 簡易的な分析結果を返す
        return {
            "analysis_type": analysis_type,
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "confidence_score": 0.7,
            "predictions": {"stock_prices": [100, 102, 105, 108, 110]},
            "risk_metrics": {"volatility": 0.15, "max_drawdown": 0.05},
            "recommendations": ["フォールバック分析結果", "詳細な分析が必要"],
            "performance_metrics": {"sharpe_ratio": 1.0, "return": 0.05},
        }

    async def _generate_action_proposals(
        self, analysis_result: Dict[str, Any], analysis_type: str
    ) -> List[ActionProposal]:
        """アクション提案の生成"""
        try:
            # 分析コンテキストの作成
            context = AnalysisContext(
                analysis_id=analysis_result.get(
                    "analysis_id",
                    f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                ),
                analysis_type=analysis_type,
                market_data=analysis_result.get("market_data", {}),
                technical_indicators=analysis_result.get("technical_indicators", {}),
                sentiment_data=analysis_result.get("sentiment_data", {}),
                risk_metrics=analysis_result.get("risk_metrics", {}),
                performance_metrics=analysis_result.get("performance_metrics", {}),
                portfolio_status=analysis_result.get("portfolio_status", {}),
                user_preferences=analysis_result.get("user_preferences", {}),
                market_condition=MarketCondition.BULL,  # デフォルト
                volatility_level=analysis_result.get("risk_metrics", {}).get(
                    "volatility", 0.15
                ),
                trend_direction="up",  # デフォルト
                support_resistance_levels={},
            )

            # アクション提案の生成
            proposals = await self.action_proposal_system.generate_action_proposals(
                context
            )

            # 最大提案数の制限
            max_proposals = self.config.max_proposals_per_analysis
            return proposals[:max_proposals]

        except Exception as e:
            logger.error(f"アクション提案生成エラー: {e}")
            return []

    async def _send_analysis_notification(
        self, analysis_result: Dict[str, Any], analysis_type: str
    ) -> bool:
        """分析結果の通知送信"""
        try:
            # AnalysisResultオブジェクトの作成
            result = AnalysisResult(
                analysis_id=analysis_result.get(
                    "analysis_id",
                    f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                ),
                analysis_type=analysis_type,
                timestamp=datetime.now(),
                duration=analysis_result.get("duration", 0.0),
                status=analysis_result.get("status", "success"),
                confidence_score=analysis_result.get("confidence_score", 0.7),
                predictions=analysis_result.get("predictions", {}),
                risk_metrics=analysis_result.get("risk_metrics", {}),
                recommendations=analysis_result.get("recommendations", []),
                performance_metrics=analysis_result.get("performance_metrics", {}),
            )

            # 優先度の決定
            priority = (
                NotificationPriority.HIGH
                if result.confidence_score > 0.8
                else NotificationPriority.NORMAL
            )

            # 通知の送信
            return await self.notification_system.send_analysis_notification(
                result, priority
            )

        except Exception as e:
            logger.error(f"通知送信エラー: {e}")
            return False

    async def _send_error_notification(self, analysis_type: str, error_message: str):
        """エラー通知の送信"""
        try:
            result = AnalysisResult(
                analysis_id=f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                analysis_type=analysis_type,
                timestamp=datetime.now(),
                duration=0.0,
                status="error",
                confidence_score=0.0,
                predictions={},
                risk_metrics={},
                recommendations=[],
                performance_metrics={},
                error_message=error_message,
            )

            await self.notification_system.send_analysis_notification(
                result, NotificationPriority.CRITICAL
            )

        except Exception as e:
            logger.error(f"エラー通知送信エラー: {e}")

    def get_automation_status(self) -> Dict[str, Any]:
        """自動化ステータスの取得"""
        return {
            "status": self.status.value,
            "total_automations": len(self.automation_history),
            "successful_automations": sum(
                1
                for r in self.automation_history
                if r.status == AutomationStatus.COMPLETED
            ),
            "failed_automations": sum(
                1
                for r in self.automation_history
                if r.status == AutomationStatus.FAILED
            ),
            "recent_automations": (
                [asdict(r) for r in self.automation_history[-5:]]
                if self.automation_history
                else []
            ),
        }

    def get_performance_metrics(self) -> Dict[str, Any]:
        """パフォーマンス指標の取得"""
        if not self.automation_history:
            return {"average_duration": 0.0, "success_rate": 0.0}

        total_duration = sum(r.total_duration for r in self.automation_history)
        average_duration = total_duration / len(self.automation_history)

        successful_count = sum(
            1 for r in self.automation_history if r.status == AutomationStatus.COMPLETED
        )
        success_rate = successful_count / len(self.automation_history)

        return {
            "average_duration": average_duration,
            "success_rate": success_rate,
            "total_analyses": sum(
                len(r.analysis_results) for r in self.automation_history
            ),
            "total_notifications": sum(
                r.notifications_sent for r in self.automation_history
            ),
            "total_proposals": sum(
                len(r.action_proposals) for r in self.automation_history
            ),
        }

    async def schedule_automation(self):
        """自動化のスケジューリング"""
        if not self.config.auto_schedule_enabled:
            return

        # スケジューリングの実装（簡略化）
        logger.info("自動化スケジューリングが有効です")
        # 実際の実装では、cronやAPSchedulerなどを使用


# 使用例
async def main():
    """使用例"""
    # 自動化システムの初期化
    automation_system = EnhancedOneClickAutomationSystem()

    # 完全自動化の実行
    result = await automation_system.run_complete_automation(
        analysis_types=["ultra_fast", "comprehensive"], force_refresh=False
    )

    print(f"自動化結果:")
    print(f"  ステータス: {result.status.value}")
    print(f"  分析件数: {len(result.analysis_results)}")
    print(f"  通知送信数: {result.notifications_sent}")
    print(f"  アクション提案数: {len(result.action_proposals)}")
    print(f"  総実行時間: {result.total_duration:.2f}秒")

    # ステータスの確認
    status = automation_system.get_automation_status()
    print(f"\n自動化ステータス:")
    print(f"  現在のステータス: {status['status']}")
    print(f"  総実行回数: {status['total_automations']}")
    print(f"  成功率: {status['successful_automations']}/{status['total_automations']}")

    # パフォーマンス指標の確認
    metrics = automation_system.get_performance_metrics()
    print(f"\nパフォーマンス指標:")
    print(f"  平均実行時間: {metrics['average_duration']:.2f}秒")
    print(f"  成功率: {metrics['success_rate']:.2%}")
    print(f"  総分析数: {metrics['total_analyses']}")
    print(f"  総通知数: {metrics['total_notifications']}")


if __name__ == "__main__":
    asyncio.run(main())
