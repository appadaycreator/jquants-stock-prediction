#!/usr/bin/env python3
"""
強化されたポートフォリオ監視システム
複数銘柄ポートフォリオ監視への横展開機能

機能:
1. 複数銘柄の統合監視
2. ポートフォリオ分析
3. リスク管理
4. パフォーマンス追跡
5. アラート統合
"""

import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any, Callable
import json
from dataclasses import dataclass, asdict
from enum import Enum
import warnings
import threading
from collections import deque
import matplotlib.pyplot as plt
import seaborn as sns
from concurrent.futures import ThreadPoolExecutor, as_completed

# 統合ログシステムのインポート
from unified_logging_config import get_system_logger, get_enhanced_logger

warnings.filterwarnings("ignore")

# 統合ログシステムを使用
logger = get_system_logger()
enhanced_logger = get_enhanced_logger()

# 既存システムのインポート
try:
    from enhanced_individual_stock_monitor import (
        EnhancedIndividualStockMonitor,
        IndividualStockMonitor,
        AlertType,
        AlertPriority,
    )
    from enhanced_news_sentiment_integration import (
        EnhancedNewsSentimentIntegration,
        IndividualStockSentiment,
    )
    from enhanced_technical_indicators_realtime import (
        EnhancedTechnicalIndicatorsRealtime,
        IndividualStockTechnical,
        TechnicalSignal,
    )
    from multi_stock_monitor import InvestmentOpportunity, PortfolioComparison
    from realtime_trading_signals import SignalType, SignalStrength
except ImportError as e:
    logger.warning(f"既存システムのインポートに失敗: {e}")


class PortfolioRiskLevel(Enum):
    """ポートフォリオリスクレベルの定義"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PortfolioPerformance(Enum):
    """ポートフォリオパフォーマンスの定義"""

    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"
    CRITICAL = "critical"


@dataclass
class PortfolioAlert:
    """ポートフォリオアラートデータクラス"""

    alert_type: str
    priority: AlertPriority
    message: str
    affected_symbols: List[str]
    current_value: float
    threshold_value: float
    timestamp: datetime
    recommendations: List[str]


@dataclass
class PortfolioMetrics:
    """ポートフォリオ指標データクラス"""

    total_value: float
    total_return: float
    daily_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    beta: float
    alpha: float
    correlation_matrix: Dict[str, Dict[str, float]]
    diversification_ratio: float
    risk_level: PortfolioRiskLevel
    performance_rating: PortfolioPerformance


@dataclass
class EnhancedPortfolioMonitor:
    """強化されたポートフォリオ監視データクラス"""

    symbols: List[str]
    individual_monitors: Dict[str, IndividualStockMonitor]
    sentiment_data: Dict[str, IndividualStockSentiment]
    technical_data: Dict[str, IndividualStockTechnical]
    portfolio_metrics: PortfolioMetrics
    alerts: List[PortfolioAlert]
    performance_history: deque
    risk_history: deque
    last_updated: datetime


class EnhancedPortfolioMonitoring:
    """強化されたポートフォリオ監視システム"""

    def __init__(self, symbols: List[str], config: Dict[str, Any] = None):
        self.symbols = symbols
        self.config = config or self._get_default_config()
        self.portfolio_monitor = None
        self.running = False
        self.lock = threading.Lock()

        # 個別システムの初期化
        self.individual_monitor = EnhancedIndividualStockMonitor(
            symbols, self.config.get("individual_monitor", {})
        )
        self.sentiment_system = EnhancedNewsSentimentIntegration(
            self.config.get("sentiment", {})
        )
        self.technical_system = EnhancedTechnicalIndicatorsRealtime(
            symbols, self.config.get("technical", {})
        )

        # ポートフォリオ監視データの初期化
        self._initialize_portfolio_monitor()

        # アラートコールバック
        self.alert_callbacks = []

    def _get_default_config(self) -> Dict[str, Any]:
        """デフォルト設定の取得"""
        return {
            "monitoring_interval": 60,  # 秒
            "max_performance_history": 1000,
            "max_risk_history": 1000,
            "risk_thresholds": {
                "volatility": 0.3,
                "max_drawdown": 0.15,
                "correlation": 0.8,
            },
            "performance_thresholds": {
                "excellent_return": 0.15,
                "good_return": 0.08,
                "poor_return": -0.05,
                "critical_return": -0.15,
            },
            "individual_monitor": {
                "monitoring_interval": 30,
                "price_change_threshold": 2.0,
                "volume_spike_threshold": 150.0,
            },
            "sentiment": {"sentiment_update_interval": 300, "relevance_threshold": 0.3},
            "technical": {"update_interval": 30, "confidence_threshold": 0.6},
        }

    def _initialize_portfolio_monitor(self):
        """ポートフォリオ監視データの初期化"""
        self.portfolio_monitor = EnhancedPortfolioMonitor(
            symbols=self.symbols,
            individual_monitors={},
            sentiment_data={},
            technical_data={},
            portfolio_metrics=PortfolioMetrics(
                total_value=0.0,
                total_return=0.0,
                daily_return=0.0,
                volatility=0.0,
                sharpe_ratio=0.0,
                max_drawdown=0.0,
                beta=0.0,
                alpha=0.0,
                correlation_matrix={},
                diversification_ratio=0.0,
                risk_level=PortfolioRiskLevel.MEDIUM,
                performance_rating=PortfolioPerformance.AVERAGE,
            ),
            alerts=[],
            performance_history=deque(maxlen=self.config["max_performance_history"]),
            risk_history=deque(maxlen=self.config["max_risk_history"]),
            last_updated=datetime.now(),
        )

    async def start_portfolio_monitoring(self):
        """ポートフォリオ監視の開始"""
        logger.info("強化されたポートフォリオ監視システムを開始します")
        self.running = True

        # 個別システムの監視開始
        individual_task = asyncio.create_task(
            self.individual_monitor.start_monitoring()
        )
        sentiment_task = asyncio.create_task(
            self.sentiment_system.start_sentiment_monitoring()
        )
        technical_task = asyncio.create_task(
            self.technical_system.start_technical_monitoring()
        )

        # ポートフォリオ統合監視タスク
        portfolio_task = asyncio.create_task(self._portfolio_monitoring_loop())
        alert_task = asyncio.create_task(self._portfolio_alert_loop())

        try:
            await asyncio.gather(
                individual_task,
                sentiment_task,
                technical_task,
                portfolio_task,
                alert_task,
                return_exceptions=True,
            )
        except KeyboardInterrupt:
            logger.info("ポートフォリオ監視システムを停止します")
            self.running = False

    async def _portfolio_monitoring_loop(self):
        """ポートフォリオ監視ループ"""
        while self.running:
            try:
                await self._update_portfolio_data()
                await asyncio.sleep(self.config["monitoring_interval"])
            except Exception as e:
                logger.error(f"ポートフォリオ監視エラー: {e}")
                await asyncio.sleep(10)

    async def _portfolio_alert_loop(self):
        """ポートフォリオアラートループ"""
        while self.running:
            try:
                await self._process_portfolio_alerts()
                await asyncio.sleep(30)
            except Exception as e:
                logger.error(f"ポートフォリオアラートエラー: {e}")
                await asyncio.sleep(10)

    async def _update_portfolio_data(self):
        """ポートフォリオデータの更新"""
        try:
            # 個別監視データの取得
            individual_monitors = self.individual_monitor.get_all_monitors()
            sentiment_data = self.sentiment_system.get_all_sentiments()
            technical_data = self.technical_system.get_all_technical_data()

            # ポートフォリオ指標の計算
            portfolio_metrics = await self._calculate_portfolio_metrics(
                individual_monitors, sentiment_data, technical_data
            )

            # データ更新
            with self.lock:
                self.portfolio_monitor.individual_monitors = individual_monitors
                self.portfolio_monitor.sentiment_data = sentiment_data
                self.portfolio_monitor.technical_data = technical_data
                self.portfolio_monitor.portfolio_metrics = portfolio_metrics

                # 履歴更新
                self.portfolio_monitor.performance_history.append(
                    {
                        "timestamp": datetime.now(),
                        "total_return": portfolio_metrics.total_return,
                        "daily_return": portfolio_metrics.daily_return,
                        "volatility": portfolio_metrics.volatility,
                        "sharpe_ratio": portfolio_metrics.sharpe_ratio,
                    }
                )

                self.portfolio_monitor.risk_history.append(
                    {
                        "timestamp": datetime.now(),
                        "risk_level": portfolio_metrics.risk_level.value,
                        "max_drawdown": portfolio_metrics.max_drawdown,
                        "volatility": portfolio_metrics.volatility,
                        "diversification_ratio": portfolio_metrics.diversification_ratio,
                    }
                )

                self.portfolio_monitor.last_updated = datetime.now()

            # アラートチェック
            await self._check_portfolio_alerts(portfolio_metrics)

            logger.info(f"ポートフォリオデータ更新完了: {len(individual_monitors)}銘柄")

        except Exception as e:
            logger.error(f"ポートフォリオデータ更新エラー: {e}")

    async def _calculate_portfolio_metrics(
        self,
        individual_monitors: Dict[str, IndividualStockMonitor],
        sentiment_data: Dict[str, IndividualStockSentiment],
        technical_data: Dict[str, IndividualStockTechnical],
    ) -> PortfolioMetrics:
        """ポートフォリオ指標の計算"""
        try:
            # 基本指標
            total_value = sum(
                monitor.current_price for monitor in individual_monitors.values()
            )
            total_return = self._calculate_total_return(individual_monitors)
            daily_return = self._calculate_daily_return(individual_monitors)
            volatility = self._calculate_portfolio_volatility(individual_monitors)

            # リスク指標
            sharpe_ratio = self._calculate_sharpe_ratio(daily_return, volatility)
            max_drawdown = self._calculate_max_drawdown(individual_monitors)
            beta = self._calculate_portfolio_beta(individual_monitors)
            alpha = self._calculate_portfolio_alpha(individual_monitors, beta)

            # 相関分析
            correlation_matrix = self._calculate_correlation_matrix(individual_monitors)
            diversification_ratio = self._calculate_diversification_ratio(
                correlation_matrix
            )

            # リスクレベル判定
            risk_level = self._determine_portfolio_risk_level(
                volatility, max_drawdown, diversification_ratio
            )

            # パフォーマンス評価
            performance_rating = self._determine_portfolio_performance(
                total_return, volatility, sharpe_ratio
            )

            return PortfolioMetrics(
                total_value=total_value,
                total_return=total_return,
                daily_return=daily_return,
                volatility=volatility,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                beta=beta,
                alpha=alpha,
                correlation_matrix=correlation_matrix,
                diversification_ratio=diversification_ratio,
                risk_level=risk_level,
                performance_rating=performance_rating,
            )

        except Exception as e:
            logger.error(f"ポートフォリオ指標計算エラー: {e}")
            return PortfolioMetrics(
                total_value=0.0,
                total_return=0.0,
                daily_return=0.0,
                volatility=0.0,
                sharpe_ratio=0.0,
                max_drawdown=0.0,
                beta=0.0,
                alpha=0.0,
                correlation_matrix={},
                diversification_ratio=0.0,
                risk_level=PortfolioRiskLevel.MEDIUM,
                performance_rating=PortfolioPerformance.AVERAGE,
            )

    def _calculate_total_return(
        self, individual_monitors: Dict[str, IndividualStockMonitor]
    ) -> float:
        """総リターンの計算"""
        returns = [monitor.change_percent for monitor in individual_monitors.values()]
        return np.mean(returns) if returns else 0.0

    def _calculate_daily_return(
        self, individual_monitors: Dict[str, IndividualStockMonitor]
    ) -> float:
        """日次リターンの計算"""
        # 簡易的な日次リターン計算（実際の実装ではより詳細な計算）
        returns = [monitor.change_percent for monitor in individual_monitors.values()]
        return np.mean(returns) if returns else 0.0

    def _calculate_portfolio_volatility(
        self, individual_monitors: Dict[str, IndividualStockMonitor]
    ) -> float:
        """ポートフォリオボラティリティの計算"""
        volatilities = [monitor.volatility for monitor in individual_monitors.values()]
        return np.mean(volatilities) if volatilities else 0.0

    def _calculate_sharpe_ratio(self, return_rate: float, volatility: float) -> float:
        """シャープレシオの計算"""
        if volatility == 0:
            return 0.0
        return return_rate / volatility

    def _calculate_max_drawdown(
        self, individual_monitors: Dict[str, IndividualStockMonitor]
    ) -> float:
        """最大ドローダウンの計算"""
        # 簡易的な最大ドローダウン計算
        max_drawdowns = []
        for monitor in individual_monitors.values():
            if len(monitor.price_history) > 1:
                prices = list(monitor.price_history)
                peak = max(prices)
                trough = min(prices)
                drawdown = (peak - trough) / peak if peak > 0 else 0.0
                max_drawdowns.append(drawdown)

        return max(max_drawdowns) if max_drawdowns else 0.0

    def _calculate_portfolio_beta(
        self, individual_monitors: Dict[str, IndividualStockMonitor]
    ) -> float:
        """ポートフォリオベータの計算"""
        # 簡易的なベータ計算（実際の実装では市場インデックスとの相関を計算）
        betas = []
        for monitor in individual_monitors.values():
            # 簡易的なベータ値（実際の実装では市場データとの相関を計算）
            beta = min(monitor.volatility * 2, 3.0)  # 仮のベータ値
            betas.append(beta)

        return np.mean(betas) if betas else 1.0

    def _calculate_portfolio_alpha(
        self, individual_monitors: Dict[str, IndividualStockMonitor], beta: float
    ) -> float:
        """ポートフォリオアルファの計算"""
        # 簡易的なアルファ計算
        total_return = self._calculate_total_return(individual_monitors)
        market_return = 0.08  # 仮の市場リターン
        risk_free_rate = 0.02  # 仮のリスクフリーレート

        expected_return = risk_free_rate + beta * (market_return - risk_free_rate)
        alpha = total_return - expected_return

        return alpha

    def _calculate_correlation_matrix(
        self, individual_monitors: Dict[str, IndividualStockMonitor]
    ) -> Dict[str, Dict[str, float]]:
        """相関行列の計算"""
        correlation_matrix = {}

        for symbol1 in individual_monitors.keys():
            correlation_matrix[symbol1] = {}
            for symbol2 in individual_monitors.keys():
                if symbol1 == symbol2:
                    correlation_matrix[symbol1][symbol2] = 1.0
                else:
                    # 簡易的な相関計算（実際の実装では価格データの相関を計算）
                    correlation = np.random.uniform(-0.5, 0.8)  # 仮の相関値
                    correlation_matrix[symbol1][symbol2] = correlation

        return correlation_matrix

    def _calculate_diversification_ratio(
        self, correlation_matrix: Dict[str, Dict[str, float]]
    ) -> float:
        """分散投資比率の計算"""
        if not correlation_matrix:
            return 0.0

        # 平均相関の計算
        correlations = []
        symbols = list(correlation_matrix.keys())

        for i, symbol1 in enumerate(symbols):
            for j, symbol2 in enumerate(symbols):
                if i < j:  # 上三角のみ
                    corr = correlation_matrix[symbol1].get(symbol2, 0)
                    correlations.append(abs(corr))

        if not correlations:
            return 0.0

        avg_correlation = np.mean(correlations)
        diversification_ratio = max(0, 1 - avg_correlation)

        return diversification_ratio

    def _determine_portfolio_risk_level(
        self, volatility: float, max_drawdown: float, diversification_ratio: float
    ) -> PortfolioRiskLevel:
        """ポートフォリオリスクレベルの判定"""
        risk_score = 0

        # ボラティリティリスク
        if volatility > 0.4:
            risk_score += 3
        elif volatility > 0.3:
            risk_score += 2
        elif volatility > 0.2:
            risk_score += 1

        # ドローダウンリスク
        if max_drawdown > 0.2:
            risk_score += 3
        elif max_drawdown > 0.15:
            risk_score += 2
        elif max_drawdown > 0.1:
            risk_score += 1

        # 分散投資リスク
        if diversification_ratio < 0.3:
            risk_score += 2
        elif diversification_ratio < 0.5:
            risk_score += 1

        if risk_score >= 6:
            return PortfolioRiskLevel.CRITICAL
        elif risk_score >= 4:
            return PortfolioRiskLevel.HIGH
        elif risk_score >= 2:
            return PortfolioRiskLevel.MEDIUM
        else:
            return PortfolioRiskLevel.LOW

    def _determine_portfolio_performance(
        self, total_return: float, volatility: float, sharpe_ratio: float
    ) -> PortfolioPerformance:
        """ポートフォリオパフォーマンスの判定"""
        thresholds = self.config["performance_thresholds"]

        if total_return >= thresholds["excellent_return"] and sharpe_ratio > 1.5:
            return PortfolioPerformance.EXCELLENT
        elif total_return >= thresholds["good_return"] and sharpe_ratio > 1.0:
            return PortfolioPerformance.GOOD
        elif total_return >= thresholds["poor_return"]:
            return PortfolioPerformance.AVERAGE
        elif total_return >= thresholds["critical_return"]:
            return PortfolioPerformance.POOR
        else:
            return PortfolioPerformance.CRITICAL

    async def _check_portfolio_alerts(self, portfolio_metrics: PortfolioMetrics):
        """ポートフォリオアラートチェック"""
        alerts = []

        # リスクアラート
        if portfolio_metrics.risk_level == PortfolioRiskLevel.CRITICAL:
            alerts.append(
                PortfolioAlert(
                    alert_type="CRITICAL_RISK",
                    priority=AlertPriority.CRITICAL,
                    message=f"ポートフォリオがクリティカルリスク状態: {portfolio_metrics.risk_level.value}",
                    affected_symbols=self.symbols,
                    current_value=portfolio_metrics.volatility,
                    threshold_value=self.config["risk_thresholds"]["volatility"],
                    timestamp=datetime.now(),
                    recommendations=[
                        "即座にリスク軽減策を実施",
                        "ポジションサイズの縮小",
                        "ヘッジ戦略の検討",
                    ],
                )
            )

        # パフォーマンスアラート
        if portfolio_metrics.performance_rating == PortfolioPerformance.CRITICAL:
            alerts.append(
                PortfolioAlert(
                    alert_type="CRITICAL_PERFORMANCE",
                    priority=AlertPriority.CRITICAL,
                    message=f"ポートフォリオパフォーマンスがクリティカル: {portfolio_metrics.performance_rating.value}",
                    affected_symbols=self.symbols,
                    current_value=portfolio_metrics.total_return,
                    threshold_value=self.config["performance_thresholds"][
                        "critical_return"
                    ],
                    timestamp=datetime.now(),
                    recommendations=[
                        "緊急のポートフォリオ見直し",
                        "損失限定の実施",
                        "専門家への相談",
                    ],
                )
            )

        # 分散投資アラート
        if portfolio_metrics.diversification_ratio < 0.3:
            alerts.append(
                PortfolioAlert(
                    alert_type="LOW_DIVERSIFICATION",
                    priority=AlertPriority.HIGH,
                    message=f"分散投資が不十分: {portfolio_metrics.diversification_ratio:.2f}",
                    affected_symbols=self.symbols,
                    current_value=portfolio_metrics.diversification_ratio,
                    threshold_value=0.3,
                    timestamp=datetime.now(),
                    recommendations=[
                        "新規銘柄の追加",
                        "セクター分散の改善",
                        "資産クラス分散の検討",
                    ],
                )
            )

        # アラートの追加
        with self.lock:
            self.portfolio_monitor.alerts.extend(alerts)

        for alert in alerts:
            logger.warning(
                f"ポートフォリオアラート: {alert.alert_type} - {alert.message}"
            )

    async def _process_portfolio_alerts(self):
        """ポートフォリオアラート処理"""
        with self.lock:
            current_alerts = self.portfolio_monitor.alerts.copy()
            self.portfolio_monitor.alerts.clear()

        for alert in current_alerts:
            # アラートコールバックの実行
            for callback in self.alert_callbacks:
                try:
                    await callback(alert)
                except Exception as e:
                    logger.error(f"ポートフォリオアラートコールバックエラー: {e}")

    def add_alert_callback(self, callback: Callable[[PortfolioAlert], None]):
        """アラートコールバックの追加"""
        self.alert_callbacks.append(callback)

    def get_portfolio_data(self) -> Optional[EnhancedPortfolioMonitor]:
        """ポートフォリオデータの取得"""
        return self.portfolio_monitor

    def get_portfolio_summary(self) -> Dict[str, Any]:
        """ポートフォリオサマリーの取得"""
        if not self.portfolio_monitor:
            return {}

        metrics = self.portfolio_monitor.portfolio_metrics

        return {
            "timestamp": self.portfolio_monitor.last_updated,
            "total_symbols": len(self.symbols),
            "total_value": metrics.total_value,
            "total_return": metrics.total_return,
            "daily_return": metrics.daily_return,
            "volatility": metrics.volatility,
            "sharpe_ratio": metrics.sharpe_ratio,
            "max_drawdown": metrics.max_drawdown,
            "beta": metrics.beta,
            "alpha": metrics.alpha,
            "diversification_ratio": metrics.diversification_ratio,
            "risk_level": metrics.risk_level.value,
            "performance_rating": metrics.performance_rating.value,
            "active_alerts": len(self.portfolio_monitor.alerts),
            "performance_history_length": len(
                self.portfolio_monitor.performance_history
            ),
            "risk_history_length": len(self.portfolio_monitor.risk_history),
        }

    def generate_portfolio_report(self) -> Dict[str, Any]:
        """ポートフォリオレポートの生成"""
        if not self.portfolio_monitor:
            return {}

        # 個別銘柄分析
        individual_analysis = {}
        for symbol, monitor in self.portfolio_monitor.individual_monitors.items():
            individual_analysis[symbol] = {
                "current_price": monitor.current_price,
                "change_percent": monitor.change_percent,
                "volume": monitor.volume,
                "risk_level": monitor.risk_level,
                "investment_opportunity": monitor.investment_opportunity.value,
                "confidence": monitor.confidence,
            }

        # 感情分析サマリー
        sentiment_summary = {}
        for symbol, sentiment in self.portfolio_monitor.sentiment_data.items():
            sentiment_summary[symbol] = {
                "overall_sentiment_score": sentiment.overall_sentiment_score,
                "sentiment_trend": sentiment.sentiment_trend.value,
                "confidence": sentiment.confidence,
                "news_count": sentiment.news_count,
                "social_mentions": sentiment.social_mentions,
            }

        # 技術分析サマリー
        technical_summary = {}
        for symbol, technical in self.portfolio_monitor.technical_data.items():
            technical_summary[symbol] = {
                "current_price": technical.current_price,
                "indicators_count": len(technical.indicators),
                "signals_count": len(technical.signals),
                "performance_metrics": technical.performance_metrics,
            }

        return {
            "timestamp": datetime.now(),
            "portfolio_summary": self.get_portfolio_summary(),
            "individual_analysis": individual_analysis,
            "sentiment_summary": sentiment_summary,
            "technical_summary": technical_summary,
            "recommendations": self._generate_recommendations(),
        }

    def _generate_recommendations(self) -> List[str]:
        """推奨事項の生成"""
        if not self.portfolio_monitor:
            return []

        recommendations = []
        metrics = self.portfolio_monitor.portfolio_metrics

        # リスク関連の推奨事項
        if metrics.risk_level == PortfolioRiskLevel.CRITICAL:
            recommendations.append("緊急のリスク軽減策を実施してください")
        elif metrics.risk_level == PortfolioRiskLevel.HIGH:
            recommendations.append("リスク軽減のためのポジション調整を検討してください")

        # パフォーマンス関連の推奨事項
        if metrics.performance_rating == PortfolioPerformance.CRITICAL:
            recommendations.append("ポートフォリオの根本的な見直しが必要です")
        elif metrics.performance_rating == PortfolioPerformance.POOR:
            recommendations.append("投資戦略の見直しを検討してください")

        # 分散投資関連の推奨事項
        if metrics.diversification_ratio < 0.3:
            recommendations.append(
                "分散投資を改善するため新規銘柄の追加を検討してください"
            )

        # シャープレシオ関連の推奨事項
        if metrics.sharpe_ratio < 0.5:
            recommendations.append("リスク調整後リターンの改善が必要です")

        return recommendations

    def save_portfolio_data(self, filename: str = "enhanced_portfolio_data.json"):
        """ポートフォリオデータの保存"""
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "portfolio_summary": self.get_portfolio_summary(),
                "portfolio_report": self.generate_portfolio_report(),
                "performance_history": [
                    {
                        "timestamp": h["timestamp"].isoformat(),
                        "total_return": h["total_return"],
                        "daily_return": h["daily_return"],
                        "volatility": h["volatility"],
                        "sharpe_ratio": h["sharpe_ratio"],
                    }
                    for h in self.portfolio_monitor.performance_history
                ],
                "risk_history": [
                    {
                        "timestamp": h["timestamp"].isoformat(),
                        "risk_level": h["risk_level"],
                        "max_drawdown": h["max_drawdown"],
                        "volatility": h["volatility"],
                        "diversification_ratio": h["diversification_ratio"],
                    }
                    for h in self.portfolio_monitor.risk_history
                ],
                "alerts": [
                    {
                        "alert_type": alert.alert_type,
                        "priority": alert.priority.value,
                        "message": alert.message,
                        "affected_symbols": alert.affected_symbols,
                        "current_value": alert.current_value,
                        "threshold_value": alert.threshold_value,
                        "timestamp": alert.timestamp.isoformat(),
                        "recommendations": alert.recommendations,
                    }
                    for alert in self.portfolio_monitor.alerts
                ],
            }

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)

            logger.info(f"ポートフォリオデータを保存しました: {filename}")

        except Exception as e:
            logger.error(f"ポートフォリオデータ保存エラー: {e}")


async def main():
    """メイン実行関数"""
    # 監視対象銘柄
    symbols = [
        "7203.T",  # トヨタ自動車
        "6758.T",  # ソニーグループ
        "9984.T",  # ソフトバンクグループ
        "9432.T",  # 日本電信電話
        "6861.T",  # キーエンス
    ]

    # 設定
    config = {
        "monitoring_interval": 60,
        "max_performance_history": 1000,
        "max_risk_history": 1000,
        "risk_thresholds": {
            "volatility": 0.3,
            "max_drawdown": 0.15,
            "correlation": 0.8,
        },
        "performance_thresholds": {
            "excellent_return": 0.15,
            "good_return": 0.08,
            "poor_return": -0.05,
            "critical_return": -0.15,
        },
        "individual_monitor": {
            "monitoring_interval": 30,
            "price_change_threshold": 2.0,
            "volume_spike_threshold": 150.0,
        },
        "sentiment": {"sentiment_update_interval": 300, "relevance_threshold": 0.3},
        "technical": {"update_interval": 30, "confidence_threshold": 0.6},
    }

    # ポートフォリオ監視システム初期化
    portfolio_system = EnhancedPortfolioMonitoring(symbols, config)

    # アラートコールバックの追加
    async def portfolio_alert_callback(alert: PortfolioAlert):
        print(f"🚨 ポートフォリオアラート: {alert.alert_type} - {alert.message}")
        print(f"   推奨事項: {', '.join(alert.recommendations)}")

    portfolio_system.add_alert_callback(portfolio_alert_callback)

    # 監視開始
    try:
        await portfolio_system.start_portfolio_monitoring()
    except KeyboardInterrupt:
        logger.info("ポートフォリオ監視システムを停止します")

        # 最終データ保存
        portfolio_system.save_portfolio_data()

        # サマリー表示
        summary = portfolio_system.get_portfolio_summary()
        print("\n" + "=" * 80)
        print("📊 強化されたポートフォリオ監視システム - 最終サマリー")
        print("=" * 80)
        print(f"監視銘柄数: {summary['total_symbols']}")
        print(f"総価値: ¥{summary['total_value']:,.0f}")
        print(f"総リターン: {summary['total_return']:+.2f}%")
        print(f"日次リターン: {summary['daily_return']:+.2f}%")
        print(f"ボラティリティ: {summary['volatility']:.2f}")
        print(f"シャープレシオ: {summary['sharpe_ratio']:.2f}")
        print(f"最大ドローダウン: {summary['max_drawdown']:.2f}")
        print(f"分散投資比率: {summary['diversification_ratio']:.2f}")
        print(f"リスクレベル: {summary['risk_level']}")
        print(f"パフォーマンス評価: {summary['performance_rating']}")
        print(f"アクティブアラート数: {summary['active_alerts']}")


if __name__ == "__main__":
    asyncio.run(main())
