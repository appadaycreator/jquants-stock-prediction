#!/usr/bin/env python3
"""
統合感情分析・ニュース統合システム（拡張版）
既存システムと新機能を統合した完全なシステム

機能:
- リアルタイム感情指標の生成
- 感情分析に基づく動的リスク調整
- 感情トレンドの予測
- 統合テストと検証
"""

import asyncio
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import json
import yfinance as yf
from dataclasses import dataclass, asdict
from enum import Enum
import warnings
import threading
import time
from collections import deque
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings("ignore")

# 既存システムのインポート
try:
    from realtime_sentiment_metrics import RealtimeSentimentMetricsGenerator, MetricType
    from dynamic_risk_adjustment import DynamicRiskAdjustmentSystem, RiskAdjustmentType
    from sentiment_trend_prediction import SentimentTrendPredictor, PredictionModel
    from sentiment_analysis_system import SentimentTradingSystem, SentimentType
    from enhanced_sentiment_trading import EnhancedSentimentTradingSystem
except ImportError as e:
    logging.warning(f"既存システムのインポートに失敗: {e}")

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("integrated_sentiment_enhancement.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class IntegratedSentimentAnalysis:
    """統合感情分析結果"""

    timestamp: datetime
    symbol: str
    realtime_metrics: Dict[str, Any]
    risk_adjustments: Dict[str, Any]
    trend_predictions: Dict[str, Any]
    trading_recommendations: List[str]
    confidence_score: float
    overall_sentiment: str


@dataclass
class SystemPerformance:
    """システム性能指標"""

    timestamp: datetime
    metrics_generation_time: float
    risk_adjustment_time: float
    prediction_time: float
    total_processing_time: float
    accuracy_score: float
    reliability_score: float


class IntegratedSentimentEnhancementSystem:
    """統合感情分析拡張システム"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}

        # 各システムの初期化
        self.metrics_generator = None
        self.risk_system = None
        self.trend_predictor = None
        self.sentiment_system = None
        self.enhanced_trading = None

        # 性能監視
        self.performance_history = deque(maxlen=1000)
        self.analysis_history = deque(maxlen=500)

        # システム状態
        self.is_running = False
        self.last_update = None

        self._initialize_systems()

    def _initialize_systems(self):
        """システムの初期化"""
        try:
            # リアルタイム感情指標生成器
            self.metrics_generator = RealtimeSentimentMetricsGenerator()

            # 動的リスク調整システム
            self.risk_system = DynamicRiskAdjustmentSystem()

            # 感情トレンド予測器
            self.trend_predictor = SentimentTrendPredictor()

            # 既存の感情分析システム
            self.sentiment_system = SentimentTradingSystem()

            # 拡張感情分析トレーディングシステム
            self.enhanced_trading = EnhancedSentimentTradingSystem()

            logger.info("統合感情分析拡張システムの初期化に成功")

        except Exception as e:
            logger.error(f"システムの初期化に失敗: {e}")

    async def perform_integrated_analysis(
        self, symbols: List[str]
    ) -> List[IntegratedSentimentAnalysis]:
        """統合感情分析の実行"""
        start_time = time.time()
        analyses = []

        try:
            for symbol in symbols:
                symbol_start_time = time.time()

                # 1. リアルタイム感情指標の生成
                metrics_start = time.time()
                realtime_metrics = await self._generate_realtime_metrics(symbol)
                metrics_time = time.time() - metrics_start

                # 2. 動的リスク調整
                risk_start = time.time()
                risk_adjustments = await self._perform_risk_adjustment(symbol)
                risk_time = time.time() - risk_start

                # 3. 感情トレンド予測
                prediction_start = time.time()
                trend_predictions = await self._perform_trend_prediction(symbol)
                prediction_time = time.time() - prediction_start

                # 4. 取引推奨事項の生成
                recommendations = self._generate_trading_recommendations(
                    symbol, realtime_metrics, risk_adjustments, trend_predictions
                )

                # 5. 総合信頼度の計算
                confidence_score = self._calculate_overall_confidence(
                    realtime_metrics, risk_adjustments, trend_predictions
                )

                # 6. 総合感情の判定
                overall_sentiment = self._determine_overall_sentiment(
                    realtime_metrics, trend_predictions
                )

                # 分析結果の作成
                analysis = IntegratedSentimentAnalysis(
                    timestamp=datetime.now(),
                    symbol=symbol,
                    realtime_metrics=realtime_metrics,
                    risk_adjustments=risk_adjustments,
                    trend_predictions=trend_predictions,
                    trading_recommendations=recommendations,
                    confidence_score=confidence_score,
                    overall_sentiment=overall_sentiment,
                )

                analyses.append(analysis)
                self.analysis_history.append(analysis)

                # 性能指標の記録
                symbol_time = time.time() - symbol_start_time
                performance = SystemPerformance(
                    timestamp=datetime.now(),
                    metrics_generation_time=metrics_time,
                    risk_adjustment_time=risk_time,
                    prediction_time=prediction_time,
                    total_processing_time=symbol_time,
                    accuracy_score=confidence_score,
                    reliability_score=self._calculate_reliability_score(analysis),
                )

                self.performance_history.append(performance)

                logger.info(f"シンボル {symbol} の統合分析完了: {symbol_time:.2f}秒")

            total_time = time.time() - start_time
            logger.info(f"全シンボルの統合分析完了: {total_time:.2f}秒")

            return analyses

        except Exception as e:
            logger.error(f"統合分析の実行に失敗: {e}")
            return []

    async def _generate_realtime_metrics(self, symbol: str) -> Dict[str, Any]:
        """リアルタイム感情指標の生成"""
        try:
            if self.metrics_generator:
                metrics = await self.metrics_generator.generate_realtime_metrics(
                    [symbol]
                )
                return {
                    "metrics": [asdict(metric) for metric in metrics],
                    "summary": self.metrics_generator.get_metrics_summary(symbol),
                    "alerts": self.metrics_generator.generate_alerts(),
                }
            else:
                return {"error": "リアルタイム指標生成器が利用できません"}

        except Exception as e:
            logger.error(f"リアルタイム指標の生成に失敗: {e}")
            return {"error": str(e)}

    async def _perform_risk_adjustment(self, symbol: str) -> Dict[str, Any]:
        """動的リスク調整の実行"""
        try:
            if self.risk_system:
                risk_profile = await self.risk_system.adjust_risk_parameters(symbol)
                return {
                    "risk_profile": asdict(risk_profile),
                    "adjustment_summary": self.risk_system.get_adjustment_summary(
                        symbol
                    ),
                    "recommendations": self.risk_system.get_risk_adjustment_recommendations(
                        symbol
                    ),
                }
            else:
                return {"error": "リスク調整システムが利用できません"}

        except Exception as e:
            logger.error(f"リスク調整の実行に失敗: {e}")
            return {"error": str(e)}

    async def _perform_trend_prediction(self, symbol: str) -> Dict[str, Any]:
        """感情トレンド予測の実行"""
        try:
            if self.trend_predictor:
                # 短期予測（15分）
                short_prediction = await self.trend_predictor.predict_sentiment_trend(
                    symbol, horizon=15
                )

                # 中期予測（60分）
                medium_prediction = await self.trend_predictor.predict_sentiment_trend(
                    symbol, horizon=60
                )

                # トレンドパターンの検出
                patterns = self.trend_predictor.detect_trend_patterns(symbol)

                return {
                    "short_term_prediction": asdict(short_prediction),
                    "medium_term_prediction": asdict(medium_prediction),
                    "trend_patterns": [asdict(pattern) for pattern in patterns],
                    "prediction_summary": self.trend_predictor.get_prediction_summary(
                        symbol
                    ),
                }
            else:
                return {"error": "感情トレンド予測器が利用できません"}

        except Exception as e:
            logger.error(f"感情トレンド予測の実行に失敗: {e}")
            return {"error": str(e)}

    def _generate_trading_recommendations(
        self,
        symbol: str,
        realtime_metrics: Dict[str, Any],
        risk_adjustments: Dict[str, Any],
        trend_predictions: Dict[str, Any],
    ) -> List[str]:
        """取引推奨事項の生成"""
        recommendations = []

        try:
            # リアルタイム指標に基づく推奨事項
            if "metrics" in realtime_metrics:
                for metric in realtime_metrics["metrics"]:
                    if metric.get("alert_level") in ["high", "critical"]:
                        recommendations.append(
                            f"アラート: {metric.get('metric_type')} で異常値が検出されました"
                        )

            # リスク調整に基づく推奨事項
            if "recommendations" in risk_adjustments:
                recommendations.extend(risk_adjustments["recommendations"])

            # 感情トレンド予測に基づく推奨事項
            if "short_term_prediction" in trend_predictions:
                pred = trend_predictions["short_term_prediction"]
                sentiment = pred.get("predicted_sentiment", 0)
                trend = pred.get("trend_direction", "stable")

                if sentiment > 0.5 and trend == "up":
                    recommendations.append(
                        "強いポジティブ感情が予測されています。買いシグナルを検討してください。"
                    )
                elif sentiment < -0.5 and trend == "down":
                    recommendations.append(
                        "強いネガティブ感情が予測されています。売りシグナルを検討してください。"
                    )
                elif trend == "stable":
                    recommendations.append(
                        "感情が安定しています。現在のポジションを維持してください。"
                    )

            # トレンドパターンに基づく推奨事項
            if "trend_patterns" in trend_predictions:
                for pattern in trend_predictions["trend_patterns"]:
                    pattern_type = pattern.get("pattern_type", "")
                    if pattern_type == "bullish":
                        recommendations.append(
                            "上昇トレンドパターンが検出されました。ポジティブな感情の継続が期待されます。"
                        )
                    elif pattern_type == "bearish":
                        recommendations.append(
                            "下降トレンドパターンが検出されました。ネガティブな感情の継続に注意してください。"
                        )

            return recommendations

        except Exception as e:
            logger.error(f"取引推奨事項の生成に失敗: {e}")
            return ["推奨事項の生成中にエラーが発生しました"]

    def _calculate_overall_confidence(
        self,
        realtime_metrics: Dict[str, Any],
        risk_adjustments: Dict[str, Any],
        trend_predictions: Dict[str, Any],
    ) -> float:
        """総合信頼度の計算"""
        try:
            confidences = []

            # リアルタイム指標の信頼度
            if "metrics" in realtime_metrics:
                for metric in realtime_metrics["metrics"]:
                    if "confidence" in metric:
                        confidences.append(metric["confidence"])

            # 感情トレンド予測の信頼度
            if "short_term_prediction" in trend_predictions:
                pred_conf = trend_predictions["short_term_prediction"].get(
                    "confidence", 0.5
                )
                confidences.append(pred_conf)

            if "medium_term_prediction" in trend_predictions:
                pred_conf = trend_predictions["medium_term_prediction"].get(
                    "confidence", 0.5
                )
                confidences.append(pred_conf)

            # 平均信頼度の計算
            if confidences:
                return float(np.mean(confidences))
            else:
                return 0.5  # デフォルト信頼度

        except Exception as e:
            logger.error(f"総合信頼度の計算に失敗: {e}")
            return 0.5

    def _determine_overall_sentiment(
        self, realtime_metrics: Dict[str, Any], trend_predictions: Dict[str, Any]
    ) -> str:
        """総合感情の判定"""
        try:
            sentiment_scores = []

            # リアルタイム指標から感情スコアを取得
            if "metrics" in realtime_metrics:
                for metric in realtime_metrics["metrics"]:
                    if metric.get("metric_type") == "sentiment_score":
                        sentiment_scores.append(metric.get("value", 0))

            # 予測から感情スコアを取得
            if "short_term_prediction" in trend_predictions:
                pred_sentiment = trend_predictions["short_term_prediction"].get(
                    "predicted_sentiment", 0
                )
                sentiment_scores.append(pred_sentiment)

            if not sentiment_scores:
                return "neutral"

            # 平均感情スコアの計算
            avg_sentiment = np.mean(sentiment_scores)

            # 感情の判定
            if avg_sentiment > 0.3:
                return "positive"
            elif avg_sentiment < -0.3:
                return "negative"
            else:
                return "neutral"

        except Exception as e:
            logger.error(f"総合感情の判定に失敗: {e}")
            return "neutral"

    def _calculate_reliability_score(
        self, analysis: IntegratedSentimentAnalysis
    ) -> float:
        """信頼性スコアの計算"""
        try:
            # 信頼度スコア
            confidence_score = analysis.confidence_score

            # 推奨事項の数（多いほど信頼性が高い）
            recommendation_score = min(len(analysis.trading_recommendations) / 5.0, 1.0)

            # エラーの有無
            error_penalty = 0.0
            if "error" in analysis.realtime_metrics:
                error_penalty += 0.2
            if "error" in analysis.risk_adjustments:
                error_penalty += 0.2
            if "error" in analysis.trend_predictions:
                error_penalty += 0.2

            # 総合信頼性スコア
            reliability = (
                confidence_score * 0.6 + recommendation_score * 0.4
            ) - error_penalty

            return max(0.0, min(1.0, reliability))

        except Exception as e:
            logger.error(f"信頼性スコアの計算に失敗: {e}")
            return 0.5

    async def start_continuous_monitoring(
        self, symbols: List[str], interval: int = 300
    ):
        """継続監視の開始"""
        self.is_running = True
        logger.info(f"継続監視を開始: {symbols} (間隔: {interval}秒)")

        while self.is_running:
            try:
                start_time = time.time()

                # 統合分析の実行
                analyses = await self.perform_integrated_analysis(symbols)

                # 結果のログ出力
                for analysis in analyses:
                    logger.info(
                        f"シンボル {analysis.symbol}: {analysis.overall_sentiment} "
                        f"(信頼度: {analysis.confidence_score:.2f})"
                    )

                    if analysis.trading_recommendations:
                        logger.info(
                            f"  推奨事項: {len(analysis.trading_recommendations)}件"
                        )
                        for rec in analysis.trading_recommendations[
                            :3
                        ]:  # 最初の3件のみ表示
                            logger.info(f"    - {rec}")

                # 性能統計の表示
                if self.performance_history:
                    recent_performance = list(self.performance_history)[-len(symbols) :]
                    avg_processing_time = np.mean(
                        [p.total_processing_time for p in recent_performance]
                    )
                    avg_accuracy = np.mean(
                        [p.accuracy_score for p in recent_performance]
                    )
                    avg_reliability = np.mean(
                        [p.reliability_score for p in recent_performance]
                    )

                    logger.info(
                        f"性能統計 - 平均処理時間: {avg_processing_time:.2f}秒, "
                        f"平均精度: {avg_accuracy:.2f}, 平均信頼性: {avg_reliability:.2f}"
                    )

                self.last_update = datetime.now()

                # 待機
                elapsed_time = time.time() - start_time
                sleep_time = max(0, interval - elapsed_time)
                await asyncio.sleep(sleep_time)

            except Exception as e:
                logger.error(f"継続監視中のエラー: {e}")
                await asyncio.sleep(interval)

    def stop_monitoring(self):
        """監視の停止"""
        self.is_running = False
        logger.info("継続監視を停止しました")

    def get_system_status(self) -> Dict[str, Any]:
        """システム状態の取得"""
        try:
            status = {
                "is_running": self.is_running,
                "last_update": (
                    self.last_update.isoformat() if self.last_update else None
                ),
                "systems_initialized": {
                    "metrics_generator": self.metrics_generator is not None,
                    "risk_system": self.risk_system is not None,
                    "trend_predictor": self.trend_predictor is not None,
                    "sentiment_system": self.sentiment_system is not None,
                    "enhanced_trading": self.enhanced_trading is not None,
                },
                "performance_stats": self._get_performance_stats(),
                "analysis_count": len(self.analysis_history),
            }

            return status

        except Exception as e:
            logger.error(f"システム状態の取得に失敗: {e}")
            return {"error": str(e)}

    def _get_performance_stats(self) -> Dict[str, Any]:
        """性能統計の取得"""
        try:
            if not self.performance_history:
                return {"message": "性能データがありません"}

            recent_performance = list(self.performance_history)[-100:]  # 最新100件

            stats = {
                "avg_processing_time": np.mean(
                    [p.total_processing_time for p in recent_performance]
                ),
                "avg_metrics_time": np.mean(
                    [p.metrics_generation_time for p in recent_performance]
                ),
                "avg_risk_time": np.mean(
                    [p.risk_adjustment_time for p in recent_performance]
                ),
                "avg_prediction_time": np.mean(
                    [p.prediction_time for p in recent_performance]
                ),
                "avg_accuracy": np.mean([p.accuracy_score for p in recent_performance]),
                "avg_reliability": np.mean(
                    [p.reliability_score for p in recent_performance]
                ),
                "total_analyses": len(recent_performance),
            }

            return stats

        except Exception as e:
            logger.error(f"性能統計の取得に失敗: {e}")
            return {"error": str(e)}

    def generate_system_report(self, save_path: str = None) -> Dict[str, Any]:
        """システムレポートの生成"""
        try:
            report = {
                "timestamp": datetime.now().isoformat(),
                "system_status": self.get_system_status(),
                "recent_analyses": [],
                "performance_trends": self._analyze_performance_trends(),
                "recommendations": self._generate_system_recommendations(),
            }

            # 最近の分析結果を追加
            recent_analyses = list(self.analysis_history)[-10:]  # 最新10件
            for analysis in recent_analyses:
                report["recent_analyses"].append(
                    {
                        "symbol": analysis.symbol,
                        "overall_sentiment": analysis.overall_sentiment,
                        "confidence_score": analysis.confidence_score,
                        "recommendation_count": len(analysis.trading_recommendations),
                        "timestamp": analysis.timestamp.isoformat(),
                    }
                )

            if save_path:
                with open(save_path, "w", encoding="utf-8") as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)
                logger.info(f"システムレポートを保存しました: {save_path}")

            return report

        except Exception as e:
            logger.error(f"システムレポートの生成に失敗: {e}")
            return {"error": str(e)}

    def _analyze_performance_trends(self) -> Dict[str, Any]:
        """性能トレンドの分析"""
        try:
            if len(self.performance_history) < 10:
                return {"message": "十分な性能データがありません"}

            recent_performance = list(self.performance_history)[-50:]  # 最新50件

            # 処理時間のトレンド
            processing_times = [p.total_processing_time for p in recent_performance]
            time_trend = (
                "改善" if processing_times[-1] < processing_times[0] else "悪化"
            )

            # 精度のトレンド
            accuracies = [p.accuracy_score for p in recent_performance]
            accuracy_trend = "改善" if accuracies[-1] > accuracies[0] else "悪化"

            return {
                "processing_time_trend": time_trend,
                "accuracy_trend": accuracy_trend,
                "avg_processing_time": np.mean(processing_times),
                "avg_accuracy": np.mean(accuracies),
                "data_points": len(recent_performance),
            }

        except Exception as e:
            logger.error(f"性能トレンドの分析に失敗: {e}")
            return {"error": str(e)}

    def _generate_system_recommendations(self) -> List[str]:
        """システム推奨事項の生成"""
        recommendations = []

        try:
            # 性能に基づく推奨事項
            if self.performance_history:
                recent_performance = list(self.performance_history)[-10:]
                avg_processing_time = np.mean(
                    [p.total_processing_time for p in recent_performance]
                )
                avg_accuracy = np.mean([p.accuracy_score for p in recent_performance])

                if avg_processing_time > 10.0:
                    recommendations.append(
                        "処理時間が長くなっています。システムの最適化を検討してください。"
                    )

                if avg_accuracy < 0.6:
                    recommendations.append(
                        "予測精度が低下しています。モデルの再訓練を検討してください。"
                    )

            # システム状態に基づく推奨事項
            status = self.get_system_status()
            if not status["systems_initialized"]["metrics_generator"]:
                recommendations.append("リアルタイム指標生成器が初期化されていません。")

            if not status["systems_initialized"]["risk_system"]:
                recommendations.append("リスク調整システムが初期化されていません。")

            if not status["systems_initialized"]["trend_predictor"]:
                recommendations.append("感情トレンド予測器が初期化されていません。")

            return recommendations

        except Exception as e:
            logger.error(f"システム推奨事項の生成に失敗: {e}")
            return ["システム推奨事項の生成中にエラーが発生しました"]


async def main():
    """メイン関数"""
    # 統合感情分析拡張システムの初期化
    system = IntegratedSentimentEnhancementSystem()

    # テストシンボル
    symbols = ["AAPL", "GOOGL", "MSFT", "TSLA"]

    # システム状態の確認
    status = system.get_system_status()
    logger.info(f"システム状態: {json.dumps(status, indent=2, ensure_ascii=False)}")

    # 統合分析の実行
    logger.info("統合感情分析を実行中...")
    analyses = await system.perform_integrated_analysis(symbols)

    # 結果の表示
    for analysis in analyses:
        logger.info(f"\n=== シンボル {analysis.symbol} の分析結果 ===")
        logger.info(f"総合感情: {analysis.overall_sentiment}")
        logger.info(f"信頼度: {analysis.confidence_score:.2f}")
        logger.info(f"推奨事項: {len(analysis.trading_recommendations)}件")

        for i, rec in enumerate(analysis.trading_recommendations, 1):
            logger.info(f"  {i}. {rec}")

    # システムレポートの生成
    report = system.generate_system_report("integrated_sentiment_report.json")
    logger.info(f"システムレポートを生成しました: {len(report)} 項目")

    # 継続監視の例（短時間）
    logger.info("継続監視を開始（30秒間）...")
    monitoring_task = asyncio.create_task(
        system.start_continuous_monitoring(symbols, interval=30)
    )

    # 30秒後に停止
    await asyncio.sleep(30)
    system.stop_monitoring()
    monitoring_task.cancel()

    logger.info("統合感情分析拡張システムのテスト完了")


if __name__ == "__main__":
    asyncio.run(main())
