#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
個別銘柄リスク許容度最適化システム
Individual Stock Risk Tolerance Optimization System

個別銘柄のリスク許容度を動的に調整し、投資効率を向上させる
"""

import numpy as np
import pandas as pd
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime, timedelta
import json


class RiskLevel(Enum):
    """リスクレベル"""

    VERY_LOW = "very_low"  # 非常に低リスク
    LOW = "low"  # 低リスク
    MODERATE = "moderate"  # 中程度リスク
    HIGH = "high"  # 高リスク
    VERY_HIGH = "very_high"  # 非常に高リスク


@dataclass
class RiskMetrics:
    """リスク指標"""

    volatility: float  # ボラティリティ（年率）
    sharpe_ratio: float  # シャープレシオ
    max_drawdown: float  # 最大ドローダウン
    var_95: float  # 95% VaR
    beta: float  # ベータ値
    correlation_market: float  # 市場との相関
    momentum_score: float  # モメンタムスコア
    quality_score: float  # クオリティスコア


@dataclass
class RiskToleranceProfile:
    """リスク許容度プロファイル"""

    symbol: str
    current_risk_level: RiskLevel
    target_risk_level: RiskLevel
    risk_capacity: float  # リスク容量（0-1）
    risk_tolerance: float  # リスク許容度（0-1）
    volatility_tolerance: float  # ボラティリティ許容度
    drawdown_tolerance: float  # ドローダウン許容度
    correlation_limit: float  # 相関制限
    last_updated: datetime
    adjustment_history: List[Dict[str, Any]]


class RiskToleranceOptimizer:
    """リスク許容度最適化システム"""

    def __init__(self, config_file: str = "risk_tolerance_config.json"):
        self.config_file = config_file
        self.profiles: Dict[str, RiskToleranceProfile] = {}
        self.logger = logging.getLogger(__name__)
        self._load_profiles()

    def _load_profiles(self) -> None:
        """リスク許容度プロファイルを読み込み"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                for symbol, profile_data in data.get("profiles", {}).items():
                    self._create_profile_from_data(symbol, profile_data)

                self.logger.info(
                    f"リスク許容度プロファイルを読み込み完了: {len(self.profiles)}銘柄"
                )
            else:
                self._create_default_profiles()
                self.logger.info("デフォルトリスク許容度プロファイルを作成")

        except Exception as e:
            self.logger.error(f"リスク許容度プロファイルの読み込みエラー: {e}")
            self._create_default_profiles()

    def _create_profile_from_data(self, symbol: str, data: Dict[str, Any]) -> None:
        """データからリスク許容度プロファイルを作成"""
        try:
            profile = RiskToleranceProfile(
                symbol=symbol,
                current_risk_level=RiskLevel(
                    data.get("current_risk_level", "moderate")
                ),
                target_risk_level=RiskLevel(data.get("target_risk_level", "moderate")),
                risk_capacity=data.get("risk_capacity", 0.5),
                risk_tolerance=data.get("risk_tolerance", 0.5),
                volatility_tolerance=data.get("volatility_tolerance", 0.2),
                drawdown_tolerance=data.get("drawdown_tolerance", 0.1),
                correlation_limit=data.get("correlation_limit", 0.7),
                last_updated=datetime.fromisoformat(
                    data.get("last_updated", datetime.now().isoformat())
                ),
                adjustment_history=data.get("adjustment_history", []),
            )

            self.profiles[symbol] = profile

        except Exception as e:
            self.logger.error(
                f"銘柄 {symbol} のリスク許容度プロファイル作成エラー: {e}"
            )

    def _create_default_profiles(self) -> None:
        """デフォルトリスク許容度プロファイルを作成"""
        default_stocks = [
            {
                "symbol": "7203.T",
                "name": "トヨタ自動車",
                "risk_level": "moderate",
                "risk_capacity": 0.6,
                "volatility_tolerance": 0.15,
            },
            {
                "symbol": "6758.T",
                "name": "ソニーグループ",
                "risk_level": "high",
                "risk_capacity": 0.8,
                "volatility_tolerance": 0.25,
            },
            {
                "symbol": "9984.T",
                "name": "ソフトバンクグループ",
                "risk_level": "very_high",
                "risk_capacity": 0.9,
                "volatility_tolerance": 0.35,
            },
            {
                "symbol": "9432.T",
                "name": "日本電信電話",
                "risk_level": "low",
                "risk_capacity": 0.4,
                "volatility_tolerance": 0.1,
            },
            {
                "symbol": "6861.T",
                "name": "キーエンス",
                "risk_level": "moderate",
                "risk_capacity": 0.7,
                "volatility_tolerance": 0.18,
            },
        ]

        for stock_data in default_stocks:
            risk_level = RiskLevel(stock_data["risk_level"])

            profile = RiskToleranceProfile(
                symbol=stock_data["symbol"],
                current_risk_level=risk_level,
                target_risk_level=risk_level,
                risk_capacity=stock_data["risk_capacity"],
                risk_tolerance=self._calculate_risk_tolerance(risk_level),
                volatility_tolerance=stock_data["volatility_tolerance"],
                drawdown_tolerance=self._calculate_drawdown_tolerance(risk_level),
                correlation_limit=0.7,
                last_updated=datetime.now(),
                adjustment_history=[],
            )

            self.profiles[stock_data["symbol"]] = profile

    def _calculate_risk_tolerance(self, risk_level: RiskLevel) -> float:
        """リスクレベルからリスク許容度を計算"""
        risk_mapping = {
            RiskLevel.VERY_LOW: 0.2,
            RiskLevel.LOW: 0.35,
            RiskLevel.MODERATE: 0.5,
            RiskLevel.HIGH: 0.7,
            RiskLevel.VERY_HIGH: 0.85,
        }
        return risk_mapping.get(risk_level, 0.5)

    def _calculate_drawdown_tolerance(self, risk_level: RiskLevel) -> float:
        """リスクレベルからドローダウン許容度を計算"""
        drawdown_mapping = {
            RiskLevel.VERY_LOW: 0.05,
            RiskLevel.LOW: 0.08,
            RiskLevel.MODERATE: 0.12,
            RiskLevel.HIGH: 0.18,
            RiskLevel.VERY_HIGH: 0.25,
        }
        return drawdown_mapping.get(risk_level, 0.12)

    def calculate_risk_metrics(
        self, symbol: str, price_data: pd.DataFrame
    ) -> RiskMetrics:
        """リスク指標を計算"""
        try:
            if price_data.empty or len(price_data) < 30:
                return self._get_default_risk_metrics()

            # リターンの計算
            returns = price_data["Close"].pct_change().dropna()

            # ボラティリティ（年率）
            volatility = returns.std() * np.sqrt(252)

            # シャープレシオ（リスクフリーレートを2%と仮定）
            risk_free_rate = 0.02
            sharpe_ratio = (returns.mean() * 252 - risk_free_rate) / (
                returns.std() * np.sqrt(252)
            )

            # 最大ドローダウン
            cumulative_returns = (1 + returns).cumprod()
            rolling_max = cumulative_returns.expanding().max()
            drawdowns = (cumulative_returns - rolling_max) / rolling_max
            max_drawdown = drawdowns.min()

            # 95% VaR
            var_95 = np.percentile(returns, 5)

            # ベータ値（市場との相関を簡略化）
            beta = 1.0  # 実際の実装では市場インデックスとの回帰分析が必要

            # 市場との相関（簡略化）
            correlation_market = 0.7  # 実際の実装では市場インデックスとの相関を計算

            # モメンタムスコア（過去3ヶ月のリターン）
            if len(returns) >= 60:
                momentum_score = returns.tail(60).mean() * 252
            else:
                momentum_score = returns.mean() * 252

            # クオリティスコア（ボラティリティの逆数）
            quality_score = 1.0 / (1.0 + volatility)

            return RiskMetrics(
                volatility=volatility,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=abs(max_drawdown),
                var_95=var_95,
                beta=beta,
                correlation_market=correlation_market,
                momentum_score=momentum_score,
                quality_score=quality_score,
            )

        except Exception as e:
            self.logger.error(f"銘柄 {symbol} のリスク指標計算エラー: {e}")
            return self._get_default_risk_metrics()

    def _get_default_risk_metrics(self) -> RiskMetrics:
        """デフォルトリスク指標を取得"""
        return RiskMetrics(
            volatility=0.2,
            sharpe_ratio=0.5,
            max_drawdown=0.1,
            var_95=-0.05,
            beta=1.0,
            correlation_market=0.7,
            momentum_score=0.1,
            quality_score=0.5,
        )

    def optimize_risk_tolerance(
        self, symbol: str, risk_metrics: RiskMetrics
    ) -> Dict[str, Any]:
        """リスク許容度を最適化"""
        if symbol not in self.profiles:
            self.logger.warning(
                f"銘柄 {symbol} のリスク許容度プロファイルが見つかりません"
            )
            return {}

        profile = self.profiles[symbol]

        # 現在のリスクレベルを評価
        current_risk_score = self._calculate_risk_score(risk_metrics)

        # 最適なリスクレベルを決定
        optimal_risk_level = self._determine_optimal_risk_level(
            risk_metrics, profile.risk_capacity
        )

        # リスク許容度の調整
        risk_adjustment = self._calculate_risk_adjustment(
            current_risk_score, optimal_risk_level, profile
        )

        # 調整履歴に記録
        adjustment_record = {
            "timestamp": datetime.now().isoformat(),
            "current_risk_score": current_risk_score,
            "optimal_risk_level": optimal_risk_level.value,
            "risk_adjustment": risk_adjustment,
            "risk_metrics": {
                "volatility": risk_metrics.volatility,
                "sharpe_ratio": risk_metrics.sharpe_ratio,
                "max_drawdown": risk_metrics.max_drawdown,
                "var_95": risk_metrics.var_95,
            },
        }

        profile.adjustment_history.append(adjustment_record)
        profile.last_updated = datetime.now()

        # プロファイルを更新
        if optimal_risk_level != profile.current_risk_level:
            profile.current_risk_level = optimal_risk_level
            profile.risk_tolerance = self._calculate_risk_tolerance(optimal_risk_level)
            profile.volatility_tolerance = self._calculate_volatility_tolerance(
                optimal_risk_level
            )
            profile.drawdown_tolerance = self._calculate_drawdown_tolerance(
                optimal_risk_level
            )

        self._save_profiles()

        return {
            "symbol": symbol,
            "current_risk_level": profile.current_risk_level.value,
            "optimal_risk_level": optimal_risk_level.value,
            "risk_adjustment": risk_adjustment,
            "recommended_position_size": self._calculate_optimal_position_size(
                profile, risk_metrics
            ),
            "risk_metrics": risk_metrics,
            "optimization_timestamp": datetime.now().isoformat(),
        }

    def _calculate_risk_score(self, risk_metrics: RiskMetrics) -> float:
        """リスクスコアを計算"""
        # 複数のリスク指標を統合してリスクスコアを計算
        volatility_score = min(risk_metrics.volatility / 0.3, 1.0)  # 30%を最大とする
        drawdown_score = min(risk_metrics.max_drawdown / 0.2, 1.0)  # 20%を最大とする
        var_score = min(abs(risk_metrics.var_95) / 0.1, 1.0)  # 10%を最大とする

        # 重み付き平均
        risk_score = volatility_score * 0.4 + drawdown_score * 0.3 + var_score * 0.3

        return min(max(risk_score, 0.0), 1.0)

    def _determine_optimal_risk_level(
        self, risk_metrics: RiskMetrics, risk_capacity: float
    ) -> RiskLevel:
        """最適なリスクレベルを決定"""
        risk_score = self._calculate_risk_score(risk_metrics)

        # リスク容量とリスクスコアを考慮
        combined_score = (risk_score + risk_capacity) / 2

        if combined_score <= 0.2:
            return RiskLevel.VERY_LOW
        elif combined_score <= 0.4:
            return RiskLevel.LOW
        elif combined_score <= 0.6:
            return RiskLevel.MODERATE
        elif combined_score <= 0.8:
            return RiskLevel.HIGH
        else:
            return RiskLevel.VERY_HIGH

    def _calculate_risk_adjustment(
        self,
        current_score: float,
        optimal_level: RiskLevel,
        profile: RiskToleranceProfile,
    ) -> Dict[str, Any]:
        """リスク調整を計算"""
        optimal_tolerance = self._calculate_risk_tolerance(optimal_level)

        adjustment = {
            "risk_tolerance_change": optimal_tolerance - profile.risk_tolerance,
            "volatility_tolerance_change": self._calculate_volatility_tolerance(
                optimal_level
            )
            - profile.volatility_tolerance,
            "drawdown_tolerance_change": self._calculate_drawdown_tolerance(
                optimal_level
            )
            - profile.drawdown_tolerance,
            "position_size_adjustment": self._calculate_position_size_adjustment(
                optimal_tolerance, profile.risk_tolerance
            ),
        }

        return adjustment

    def _calculate_volatility_tolerance(self, risk_level: RiskLevel) -> float:
        """リスクレベルからボラティリティ許容度を計算"""
        volatility_mapping = {
            RiskLevel.VERY_LOW: 0.08,
            RiskLevel.LOW: 0.12,
            RiskLevel.MODERATE: 0.18,
            RiskLevel.HIGH: 0.25,
            RiskLevel.VERY_HIGH: 0.35,
        }
        return volatility_mapping.get(risk_level, 0.18)

    def _calculate_position_size_adjustment(
        self, new_tolerance: float, current_tolerance: float
    ) -> float:
        """ポジションサイズ調整を計算"""
        if current_tolerance == 0:
            return 1.0

        return new_tolerance / current_tolerance

    def _calculate_optimal_position_size(
        self, profile: RiskToleranceProfile, risk_metrics: RiskMetrics
    ) -> float:
        """最適なポジションサイズを計算"""
        # ケリー基準をベースにしたポジションサイズ計算
        expected_return = risk_metrics.momentum_score
        volatility = risk_metrics.volatility

        if volatility == 0:
            return 0.0

        # ケリー比率
        kelly_ratio = expected_return / (volatility**2)

        # リスク許容度で調整
        optimal_size = kelly_ratio * profile.risk_tolerance

        # 最大ポジションサイズを制限
        max_size = profile.risk_capacity
        optimal_size = min(optimal_size, max_size)

        return max(0.0, optimal_size)

    def get_risk_tolerance_profile(self, symbol: str) -> Optional[RiskToleranceProfile]:
        """指定銘柄のリスク許容度プロファイルを取得"""
        return self.profiles.get(symbol)

    def update_risk_capacity(self, symbol: str, new_capacity: float) -> bool:
        """リスク容量を更新"""
        if symbol not in self.profiles:
            return False

        if not 0 <= new_capacity <= 1:
            self.logger.warning(
                f"リスク容量は0-1の範囲で設定してください: {new_capacity}"
            )
            return False

        self.profiles[symbol].risk_capacity = new_capacity
        self._save_profiles()
        self.logger.info(f"銘柄 {symbol} のリスク容量を更新: {new_capacity}")
        return True

    def get_portfolio_risk_summary(self) -> Dict[str, Any]:
        """ポートフォリオ全体のリスク要約を取得"""
        if not self.profiles:
            return {}

        total_stocks = len(self.profiles)
        risk_distribution = {}

        for risk_level in RiskLevel:
            count = sum(
                1
                for profile in self.profiles.values()
                if profile.current_risk_level == risk_level
            )
            risk_distribution[risk_level.value] = count / total_stocks

        avg_risk_capacity = np.mean(
            [profile.risk_capacity for profile in self.profiles.values()]
        )
        avg_risk_tolerance = np.mean(
            [profile.risk_tolerance for profile in self.profiles.values()]
        )

        return {
            "total_stocks": total_stocks,
            "risk_distribution": risk_distribution,
            "average_risk_capacity": avg_risk_capacity,
            "average_risk_tolerance": avg_risk_tolerance,
            "diversification_score": self._calculate_diversification_score(),
            "risk_balance_score": self._calculate_risk_balance_score(),
        }

    def _calculate_diversification_score(self) -> float:
        """分散投資スコアを計算"""
        if len(self.profiles) < 2:
            return 0.0

        risk_levels = [profile.current_risk_level for profile in self.profiles.values()]
        unique_levels = len(set(risk_levels))
        max_possible_levels = len(RiskLevel)

        return unique_levels / max_possible_levels

    def _calculate_risk_balance_score(self) -> float:
        """リスクバランススコアを計算"""
        if not self.profiles:
            return 0.0

        risk_tolerances = [profile.risk_tolerance for profile in self.profiles.values()]
        tolerance_std = np.std(risk_tolerances)

        # 標準偏差が小さいほどバランスが良い
        balance_score = 1.0 / (1.0 + tolerance_std)
        return balance_score

    def _save_profiles(self) -> None:
        """プロファイルをファイルに保存"""
        try:
            data = {"profiles": {}}

            for symbol, profile in self.profiles.items():
                profile_dict = {
                    "current_risk_level": profile.current_risk_level.value,
                    "target_risk_level": profile.target_risk_level.value,
                    "risk_capacity": profile.risk_capacity,
                    "risk_tolerance": profile.risk_tolerance,
                    "volatility_tolerance": profile.volatility_tolerance,
                    "drawdown_tolerance": profile.drawdown_tolerance,
                    "correlation_limit": profile.correlation_limit,
                    "last_updated": profile.last_updated.isoformat(),
                    "adjustment_history": profile.adjustment_history,
                }
                data["profiles"][symbol] = profile_dict

            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"リスク許容度プロファイルを保存: {self.config_file}")

        except Exception as e:
            self.logger.error(f"リスク許容度プロファイルの保存エラー: {e}")


def main():
    """メイン実行関数"""
    # ログ設定
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # リスク許容度最適化システムの初期化
    optimizer = RiskToleranceOptimizer()

    # ポートフォリオリスク要約の表示
    summary = optimizer.get_portfolio_risk_summary()
    print("=== ポートフォリオリスク要約 ===")
    print(f"管理銘柄数: {summary.get('total_stocks', 0)}")
    print(f"平均リスク容量: {summary.get('average_risk_capacity', 0):.2f}")
    print(f"平均リスク許容度: {summary.get('average_risk_tolerance', 0):.2f}")
    print(f"分散投資スコア: {summary.get('diversification_score', 0):.2f}")
    print(f"リスクバランススコア: {summary.get('risk_balance_score', 0):.2f}")

    print("\nリスク分布:")
    for risk_level, ratio in summary.get("risk_distribution", {}).items():
        print(f"  {risk_level}: {ratio:.1%}")


if __name__ == "__main__":
    main()
