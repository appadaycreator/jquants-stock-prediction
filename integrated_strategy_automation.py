#!/usr/bin/env python3
"""
統合投資戦略自動化システム
既存のバックテストシステム、AI予測システム、自動取引システムと統合した
包括的な投資戦略自動提案・実行システム

主要機能:
1. 既存システムとの完全統合
2. リアルタイム戦略提案
3. 自動実行とモニタリング
4. パフォーマンス追跡と改善
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any, Union
import json
import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time

# 既存システムのインポート
from unified_system import UnifiedSystem, ErrorCategory, LogLevel, LogCategory
from enhanced_ai_prediction_system import EnhancedAIPredictionSystem, PredictionResult
from automated_strategy_recommendation_system import (
    AutomatedStrategyRecommendationSystem,
    StrategyRecommendation,
    StrategyExecution,
    HistoricalAnalysis,
    StrategyType,
    MarketRegime,
)
from integrated_backtest_system import IntegratedBacktestSystem
from enhanced_automated_trading_system import (
    EnhancedAutomatedTradingSystem,
    TradingSignal,
    TradingStrategy,
)
from investment_style_optimizer import (
    InvestmentStyleOptimizer,
    InvestmentStyle,
    MarketCondition,
)


class IntegratedStrategyAutomation:
    """統合投資戦略自動化システム"""

    def __init__(self, unified_system: UnifiedSystem = None):
        self.unified_system = unified_system or UnifiedSystem()

        # 各システムの初期化
        self.ai_prediction_system = EnhancedAIPredictionSystem(self.unified_system)
        self.strategy_recommendation_system = AutomatedStrategyRecommendationSystem(
            self.unified_system
        )
        self.backtest_system = IntegratedBacktestSystem()
        self.trading_system = EnhancedAutomatedTradingSystem(
            self.unified_system, self.ai_prediction_system
        )
        self.style_optimizer = InvestmentStyleOptimizer()

        # 統合設定
        self.config = {
            "auto_execution_enabled": True,
            "real_time_monitoring": True,
            "risk_management_enabled": True,
            "performance_tracking": True,
            "update_frequency_minutes": 5,
            "max_concurrent_strategies": 10,
            "min_confidence_threshold": 0.6,
            "max_risk_per_trade": 0.02,  # 2%
            "portfolio_risk_limit": 0.10,  # 10%
        }

        # 監視スレッド
        self.monitoring_thread = None
        self.is_running = False

        # ログ設定
        self.logger = logging.getLogger(f"{self.__class__.__name__}")

        self.logger.info("🚀 統合投資戦略自動化システム初期化完了")

    def start_automation(self):
        """自動化システムの開始"""
        try:
            if self.is_running:
                self.logger.warning("自動化システムは既に実行中です")
                return

            self.is_running = True

            # 監視スレッドの開始
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop, daemon=True
            )
            self.monitoring_thread.start()

            # 取引システムの開始
            self.trading_system.start_trading()

            self.logger.info("🤖 統合投資戦略自動化システム開始")

        except Exception as e:
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.SYSTEM_ERROR,
                context="自動化システム開始エラー",
            )

    def stop_automation(self):
        """自動化システムの停止"""
        try:
            self.is_running = False

            if self.monitoring_thread:
                self.monitoring_thread.join(timeout=5.0)

            # 取引システムの停止
            self.trading_system.stop_trading()

            self.logger.info("🛑 統合投資戦略自動化システム停止")

        except Exception as e:
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.SYSTEM_ERROR,
                context="自動化システム停止エラー",
            )

    def _monitoring_loop(self):
        """監視ループ"""
        while self.is_running:
            try:
                # 市場データの取得と分析
                self._update_market_analysis()

                # 既存ポジションの監視
                self._monitor_existing_positions()

                # 新しい戦略の提案
                self._generate_new_recommendations()

                # パフォーマンスの追跡
                self._track_performance()

                # 設定された間隔で待機
                time.sleep(self.config["update_frequency_minutes"] * 60)

            except Exception as e:
                self.unified_system.log_error(
                    error=e,
                    category=ErrorCategory.SYSTEM_ERROR,
                    context="監視ループエラー",
                )
                time.sleep(60)  # エラー時は1分待機

    def _update_market_analysis(self):
        """市場分析の更新"""
        try:
            # 主要銘柄のデータを取得
            symbols = ["7203.T", "6758.T", "9984.T", "6861.T", "4063.T"]

            for symbol in symbols:
                try:
                    # 最新データの取得
                    current_data = self._fetch_latest_data(symbol)

                    if current_data.empty:
                        continue

                    # 市場条件の分析
                    market_conditions = self._analyze_market_conditions(current_data)

                    # 過去の分析結果を追加
                    historical_analysis = self._create_historical_analysis(
                        symbol, current_data, market_conditions
                    )

                    self.strategy_recommendation_system.add_historical_analysis(
                        historical_analysis
                    )

                except Exception as e:
                    self.logger.warning(f"銘柄 {symbol} の分析更新エラー: {e}")
                    continue

        except Exception as e:
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.DATA_PROCESSING_ERROR,
                context="市場分析更新エラー",
            )

    def _monitor_existing_positions(self):
        """既存ポジションの監視"""
        try:
            # アクティブな実行を取得
            active_executions = (
                self.strategy_recommendation_system.strategy_executor.active_executions
            )

            for execution_id, execution in active_executions.items():
                try:
                    # 実行の監視
                    status = self.strategy_recommendation_system.strategy_executor.monitor_execution(
                        execution_id
                    )

                    if status.get("status") == "closed":
                        self.logger.info(f"📊 ポジションクローズ: {execution_id}")

                except Exception as e:
                    self.logger.warning(f"ポジション監視エラー {execution_id}: {e}")
                    continue

        except Exception as e:
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.MODEL_ERROR,
                context="ポジション監視エラー",
            )

    def _generate_new_recommendations(self):
        """新しい戦略推奨の生成"""
        try:
            # 監視対象銘柄
            watchlist = ["7203.T", "6758.T", "9984.T", "6861.T", "4063.T"]

            for symbol in watchlist:
                try:
                    # 最新データの取得
                    current_data = self._fetch_latest_data(symbol)

                    if current_data.empty or len(current_data) < 20:
                        continue

                    # 市場条件の分析
                    market_conditions = self._analyze_market_conditions(current_data)

                    # 戦略推奨の生成
                    recommendation = (
                        self.strategy_recommendation_system.generate_recommendation(
                            symbol, current_data, market_conditions
                        )
                    )

                    # 信頼度とリスクのチェック
                    if (
                        recommendation.confidence_score
                        >= self.config["min_confidence_threshold"]
                        and recommendation.risk_level != "high"
                    ):

                        # 自動実行が有効な場合
                        if self.config["auto_execution_enabled"]:
                            execution = self.strategy_recommendation_system.execute_recommendation(
                                recommendation
                            )
                            self.logger.info(
                                f"🚀 自動戦略実行: {symbol} - {recommendation.recommended_strategy.value}"
                            )
                        else:
                            self.logger.info(
                                f"📊 戦略推奨生成: {symbol} - {recommendation.recommended_strategy.value}"
                            )

                except Exception as e:
                    self.logger.warning(f"銘柄 {symbol} の推奨生成エラー: {e}")
                    continue

        except Exception as e:
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.MODEL_ERROR,
                context="戦略推奨生成エラー",
            )

    def _track_performance(self):
        """パフォーマンスの追跡"""
        try:
            # システムパフォーマンスの取得
            performance = self.strategy_recommendation_system.get_system_performance()

            # ポートフォリオサマリーの取得
            portfolio_summary = self.trading_system.get_portfolio_summary()

            # パフォーマンスログの出力
            self.logger.info(
                f"📈 システムパフォーマンス: 成功率 {performance.get('success_rate', 0):.1%}"
            )
            self.logger.info(
                f"💰 ポートフォリオ評価額: ¥{portfolio_summary.get('total_equity', 0):,.0f}"
            )

            # リスクチェック
            if (
                portfolio_summary.get("total_pnl", 0)
                < -portfolio_summary.get("total_equity", 0) * 0.05
            ):
                self.logger.warning("⚠️ ポートフォリオリスクが高レベルです")

        except Exception as e:
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.MODEL_ERROR,
                context="パフォーマンス追跡エラー",
            )

    def _fetch_latest_data(self, symbol: str, days: int = 30) -> pd.DataFrame:
        """最新データの取得"""
        try:
            import yfinance as yf

            ticker = yf.Ticker(symbol)
            data = ticker.history(period=f"{days}d")

            if data.empty:
                return pd.DataFrame()

            # データの正規化
            data.columns = [col.lower() for col in data.columns]
            data.reset_index(inplace=True)
            data.rename(columns={"date": "Date"}, inplace=True)
            data.set_index("Date", inplace=True)

            return data

        except Exception as e:
            self.logger.warning(f"データ取得エラー {symbol}: {e}")
            return pd.DataFrame()

    def _analyze_market_conditions(self, data: pd.DataFrame) -> Dict[str, Any]:
        """市場条件の分析"""
        try:
            if data.empty or len(data) < 20:
                return {"volatility": 0.15, "trend_strength": 0.0}

            # リターンの計算
            returns = data["Close"].pct_change().dropna()

            # ボラティリティの計算
            volatility = returns.std() * np.sqrt(252)

            # トレンドの強さの計算
            sma_short = data["Close"].rolling(window=10).mean()
            sma_long = data["Close"].rolling(window=20).mean()
            trend_strength = (sma_short.iloc[-1] - sma_long.iloc[-1]) / sma_long.iloc[
                -1
            ]

            # モメンタムの計算
            momentum = (data["Close"].iloc[-1] - data["Close"].iloc[-10]) / data[
                "Close"
            ].iloc[-10]

            return {
                "volatility": volatility,
                "trend_strength": trend_strength,
                "momentum": momentum,
                "volume_ratio": (
                    data["Volume"].iloc[-5:].mean() / data["Volume"].iloc[-20:].mean()
                    if len(data) >= 20
                    else 1.0
                ),
            }

        except Exception as e:
            self.logger.warning(f"市場条件分析エラー: {e}")
            return {"volatility": 0.15, "trend_strength": 0.0}

    def _create_historical_analysis(
        self, symbol: str, data: pd.DataFrame, market_conditions: Dict[str, Any]
    ) -> HistoricalAnalysis:
        """過去分析結果の作成"""
        try:
            # 技術指標の計算
            technical_indicators = self._calculate_technical_indicators(data)

            # 基本パフォーマンス指標
            if len(data) >= 2:
                total_return = (data["Close"].iloc[-1] - data["Close"].iloc[0]) / data[
                    "Close"
                ].iloc[0]
            else:
                total_return = 0.0

            # 成功スコアの計算（簡易版）
            success_score = min(
                1.0, max(0.0, (total_return + 0.1) / 0.3)
            )  # -10%から+20%の範囲で正規化

            return HistoricalAnalysis(
                symbol=symbol,
                analysis_date=datetime.now(),
                strategy_type=StrategyType.MOMENTUM,  # デフォルト
                performance_metrics={"total_return": total_return},
                market_conditions=market_conditions,
                technical_indicators=technical_indicators,
                fundamental_indicators={},
                sentiment_score=0.5,  # デフォルト
                risk_metrics={"volatility": market_conditions.get("volatility", 0.15)},
                success_score=success_score,
            )

        except Exception as e:
            self.logger.warning(f"過去分析結果作成エラー {symbol}: {e}")
            return None

    def _calculate_technical_indicators(self, data: pd.DataFrame) -> Dict[str, float]:
        """技術指標の計算"""
        try:
            indicators = {}

            if len(data) < 14:
                return indicators

            # RSI
            delta = data["Close"].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            indicators["rsi"] = (100 - (100 / (1 + rs))).iloc[-1]

            # MACD
            exp1 = data["Close"].ewm(span=12).mean()
            exp2 = data["Close"].ewm(span=26).mean()
            indicators["macd"] = (exp1 - exp2).iloc[-1]

            # ボリンジャーバンド位置
            sma = data["Close"].rolling(window=20).mean()
            std = data["Close"].rolling(window=20).std()
            bb_upper = sma + (std * 2)
            bb_lower = sma - (std * 2)
            current_price = data["Close"].iloc[-1]
            indicators["bollinger_position"] = (current_price - bb_lower.iloc[-1]) / (
                bb_upper.iloc[-1] - bb_lower.iloc[-1]
            )

            # 複合スコア
            rsi_score = 1 - abs(indicators["rsi"] - 50) / 50
            macd_score = 1 if indicators["macd"] > 0 else 0
            bb_score = 1 - abs(indicators["bollinger_position"] - 0.5) * 2
            indicators["composite_score"] = (rsi_score + macd_score + bb_score) / 3

            return indicators

        except Exception as e:
            self.logger.warning(f"技術指標計算エラー: {e}")
            return {}

    def get_system_status(self) -> Dict[str, Any]:
        """システムステータスの取得"""
        try:
            # 各システムのステータス
            strategy_performance = (
                self.strategy_recommendation_system.get_system_performance()
            )
            portfolio_summary = self.trading_system.get_portfolio_summary()

            return {
                "system_running": self.is_running,
                "strategy_performance": strategy_performance,
                "portfolio_summary": portfolio_summary,
                "active_executions": len(
                    self.strategy_recommendation_system.strategy_executor.active_executions
                ),
                "total_recommendations": len(
                    self.strategy_recommendation_system.recommendations
                ),
                "last_update": datetime.now().isoformat(),
            }

        except Exception as e:
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.MODEL_ERROR,
                context="システムステータス取得エラー",
            )
            return {"status": "error"}

    def update_config(self, **kwargs):
        """設定の更新"""
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
                self.logger.info(f"設定更新: {key} = {value}")

    def export_system_data(self, file_path: str) -> bool:
        """システムデータのエクスポート"""
        try:
            export_data = {
                "system_status": self.get_system_status(),
                "config": self.config,
                "recommendations": [
                    {
                        "symbol": rec.symbol,
                        "strategy": rec.recommended_strategy.value,
                        "confidence": rec.confidence_score,
                        "expected_return": rec.expected_return,
                        "risk_level": rec.risk_level,
                        "created_at": rec.created_at.isoformat(),
                    }
                    for rec in self.strategy_recommendation_system.recommendations
                ],
                "executions": [
                    {
                        "execution_id": exec.recommendation_id,
                        "symbol": exec.symbol,
                        "strategy": exec.strategy.value,
                        "entry_price": exec.entry_price,
                        "position_size": exec.position_size,
                        "status": exec.status,
                        "entry_time": exec.entry_time.isoformat(),
                        "pnl": exec.pnl,
                    }
                    for exec in self.strategy_recommendation_system.executions
                ],
            }

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, default=str, ensure_ascii=False, indent=2)

            self.logger.info(f"📊 システムデータエクスポート完了: {file_path}")
            return True

        except Exception as e:
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.FILE_ERROR,
                context=f"システムデータエクスポートエラー: {file_path}",
            )
            return False


def main():
    """メイン実行関数"""
    try:
        # 統合システムの初期化
        unified_system = UnifiedSystem()

        # 統合投資戦略自動化システムの初期化
        automation_system = IntegratedStrategyAutomation(unified_system)

        # 設定の更新
        automation_system.update_config(
            auto_execution_enabled=True,
            min_confidence_threshold=0.7,
            update_frequency_minutes=2,
        )

        print("=== 統合投資戦略自動化システム ===")
        print("システムを開始しています...")

        # 自動化システムの開始
        automation_system.start_automation()

        # システムステータスの表示
        status = automation_system.get_system_status()
        print(f"\nシステムステータス:")
        print(f"  実行中: {status.get('system_running', False)}")
        print(f"  アクティブ実行数: {status.get('active_executions', 0)}")
        print(f"  総推奨数: {status.get('total_recommendations', 0)}")

        # ポートフォリオサマリー
        portfolio = status.get("portfolio_summary", {})
        if portfolio:
            print(f"\nポートフォリオサマリー:")
            print(f"  総評価額: ¥{portfolio.get('total_equity', 0):,.0f}")
            print(f"  総損益: ¥{portfolio.get('total_pnl', 0):,.0f}")
            print(f"  ポジション数: {portfolio.get('total_positions', 0)}")

        # システムデータのエクスポート
        automation_system.export_system_data("integrated_automation_data.json")

        print("\nシステムデータをエクスポートしました: integrated_automation_data.json")
        print("\n自動化システムが実行中です。Ctrl+Cで停止してください。")

        # デモンストレーション用の待機
        try:
            while True:
                time.sleep(10)
                status = automation_system.get_system_status()
                print(f"アクティブ実行数: {status.get('active_executions', 0)}")

        except KeyboardInterrupt:
            print("\nシステムを停止しています...")
            automation_system.stop_automation()
            print("システムが停止しました。")

    except Exception as e:
        print(f"エラー: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
