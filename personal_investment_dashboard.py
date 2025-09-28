#!/usr/bin/env python3
"""
個人投資特化ダッシュボードシステム
投資判断に直結する情報の優先表示、損益状況の一目瞭然な表示、
次のアクション（買い・売り・ホールド）の明確な提示を実現
"""

import pandas as pd
import numpy as np
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
import aiohttp
from pathlib import Path

# 既存システムのインポート
from enhanced_individual_stock_monitor import EnhancedIndividualStockMonitor
from realtime_trading_signals import SignalGenerator, RiskManager
from risk_management_system import PortfolioRiskMonitor, Position
from enhanced_sentiment_trading import EnhancedSentimentTradingSystem

logger = logging.getLogger(__name__)


class InvestmentAction(Enum):
    """投資アクション"""

    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"


class PriorityLevel(Enum):
    """優先度レベル"""

    CRITICAL = "CRITICAL"  # 即座に対応が必要
    HIGH = "HIGH"  # 高優先度
    MEDIUM = "MEDIUM"  # 中優先度
    LOW = "LOW"  # 低優先度


@dataclass
class PnLSummary:
    """損益サマリー"""

    total_investment: float
    current_value: float
    unrealized_pnl: float
    realized_pnl: float
    total_pnl: float
    pnl_percentage: float
    daily_pnl: float
    weekly_pnl: float
    monthly_pnl: float
    best_performer: str
    worst_performer: str
    risk_adjusted_return: float


@dataclass
class PositionSummary:
    """ポジションサマリー"""

    symbol: str
    company_name: str
    current_price: float
    quantity: int
    total_value: float
    cost_basis: float
    unrealized_pnl: float
    pnl_percentage: float
    action_recommendation: InvestmentAction
    confidence: float
    priority: PriorityLevel
    risk_level: str
    next_action: str
    target_price: Optional[float]
    stop_loss: Optional[float]


@dataclass
class InvestmentRecommendation:
    """投資推奨事項"""

    symbol: str
    action: InvestmentAction
    confidence: float
    priority: PriorityLevel
    reason: str
    target_price: Optional[float]
    stop_loss: Optional[float]
    position_size: Optional[int]
    expected_return: Optional[float]
    risk_level: str
    timeframe: str


@dataclass
class MarketOverview:
    """市場概況"""

    market_trend: str
    volatility_level: str
    sentiment_score: float
    key_events: List[str]
    sector_performance: Dict[str, float]
    market_alert: Optional[str]


class PersonalInvestmentDashboard:
    """個人投資特化ダッシュボードシステム"""

    def __init__(self, config_path: str = "config_final.yaml"):
        self.config = self._load_config(config_path)
        self.monitor = EnhancedIndividualStockMonitor()
        self.signal_generator = SignalGenerator()
        self.risk_manager = RiskManager()
        self.portfolio_monitor = PortfolioRiskMonitor()
        self.sentiment_system = EnhancedSentimentTradingSystem()
        
        # ダッシュボードデータ
        self.positions: Dict[str, Position] = {}
        self.watchlist: List[str] = []
        self.last_update: Optional[datetime] = None
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """設定ファイルの読み込み"""
        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"設定ファイル読み込みエラー: {e}")
            return {}
    
    async def initialize_dashboard(self, symbols: List[str], initial_capital: float = 1000000):
        """ダッシュボードの初期化"""
        logger.info("個人投資ダッシュボードを初期化中...")
        
        self.watchlist = symbols
        self.portfolio_monitor = PortfolioRiskMonitor()
        
        # 初期ポジションの設定（サンプルデータ）
        await self._setup_sample_positions(initial_capital)
        
        # 初期データの取得
        await self._update_all_data()
        
        logger.info("ダッシュボード初期化完了")
    
    async def _setup_sample_positions(self, initial_capital: float):
        """サンプルポジションの設定"""
        sample_positions = [
            {"symbol": "7203.T", "quantity": 100, "cost_basis": 2500.0},
            {"symbol": "6758.T", "quantity": 50, "cost_basis": 4500.0},
            {"symbol": "6861.T", "quantity": 200, "cost_basis": 5000.0},
            {"symbol": "9984.T", "quantity": 30, "cost_basis": 8000.0},
        ]
        
        for pos_data in sample_positions:
            position = Position(
                symbol=pos_data["symbol"],
                quantity=pos_data["quantity"],
                entry_price=pos_data["cost_basis"],
                current_price=pos_data["cost_basis"] * (1 + np.random.uniform(-0.1, 0.1)),
                stop_loss=pos_data["cost_basis"] * 0.9,
                take_profit=pos_data["cost_basis"] * 1.2
            )
            self.portfolio_monitor.add_position(position)
            self.positions[pos_data["symbol"]] = position
    
    async def _update_all_data(self):
        """全データの更新"""
        try:
            # ポジション価格の更新
            for symbol in self.positions.keys():
                await self._update_position_price(symbol)
            
            # 監視銘柄の分析
            for symbol in self.watchlist:
                if symbol not in self.positions:
                    await self._analyze_watchlist_stock(symbol)
            
            self.last_update = datetime.now()
            logger.info("全データ更新完了")
            
        except Exception as e:
            logger.error(f"データ更新エラー: {e}")
    
    async def _update_position_price(self, symbol: str):
        """ポジション価格の更新"""
        try:
            # 実際の実装では、リアルタイム価格APIを使用
            # ここではサンプルデータを使用
            current_price = self.positions[symbol].current_price * (1 + np.random.uniform(-0.02, 0.02))
            self.positions[symbol].current_price = current_price
            self.portfolio_monitor.update_position_price(symbol, current_price)
            
        except Exception as e:
            logger.error(f"価格更新エラー {symbol}: {e}")
    
    async def _analyze_watchlist_stock(self, symbol: str):
        """監視銘柄の分析"""
        try:
            # 個別銘柄分析の実行
            analysis = await self.monitor.analyze_stock(symbol)
            if analysis:
                logger.info(f"監視銘柄分析完了: {symbol}")
        except Exception as e:
            logger.error(f"監視銘柄分析エラー {symbol}: {e}")
    
    def get_pnl_summary(self) -> PnLSummary:
        """損益サマリーの取得"""
        try:
            total_investment = sum(
                pos.entry_price * pos.quantity for pos in self.positions.values()
            )
            current_value = sum(
                pos.current_price * pos.quantity for pos in self.positions.values()
            )
            unrealized_pnl = current_value - total_investment
            pnl_percentage = (unrealized_pnl / total_investment) * 100 if total_investment > 0 else 0
            
            # 日次・週次・月次損益の計算（サンプル）
            daily_pnl = unrealized_pnl * 0.01  # 1%の変動を想定
            weekly_pnl = unrealized_pnl * 0.05  # 5%の変動を想定
            monthly_pnl = unrealized_pnl * 0.15  # 15%の変動を想定
            
            # ベスト・ワーストパフォーマー
            performances = {
                symbol: ((pos.current_price - pos.entry_price) / pos.entry_price) * 100
                for symbol, pos in self.positions.items()
            }
            best_performer = max(performances, key=performances.get) if performances else ""
            worst_performer = min(performances, key=performances.get) if performances else ""
            
            # リスク調整後リターン（シャープレシオ）
            risk_adjusted_return = self._calculate_risk_adjusted_return()
            
            return PnLSummary(
                total_investment=total_investment,
                current_value=current_value,
                unrealized_pnl=unrealized_pnl,
                realized_pnl=0.0,  # 実装時は実際の実現損益を取得
                total_pnl=unrealized_pnl,
                pnl_percentage=pnl_percentage,
                daily_pnl=daily_pnl,
                weekly_pnl=weekly_pnl,
                monthly_pnl=monthly_pnl,
                best_performer=best_performer,
                worst_performer=worst_performer,
                risk_adjusted_return=risk_adjusted_return
            )
            
        except Exception as e:
            logger.error(f"損益サマリー計算エラー: {e}")
            return PnLSummary(
                total_investment=0, current_value=0, unrealized_pnl=0,
                realized_pnl=0, total_pnl=0, pnl_percentage=0,
                daily_pnl=0, weekly_pnl=0, monthly_pnl=0,
                best_performer="", worst_performer="", risk_adjusted_return=0
            )
    
    def _calculate_risk_adjusted_return(self) -> float:
        """リスク調整後リターンの計算"""
        try:
            risk_metrics = self.portfolio_monitor.calculate_portfolio_risk(1000000)
            return risk_metrics.sharpe_ratio
        except:
            return 0.0
    
    def get_position_summaries(self) -> List[PositionSummary]:
        """ポジションサマリーの取得"""
        summaries = []
        
        for symbol, position in self.positions.items():
            try:
                # 投資アクションの判定
                action_rec = self._determine_investment_action(symbol, position)
                
                # 信頼度の計算
                confidence = self._calculate_confidence(symbol, position)
                
                # 優先度の判定
                priority = self._determine_priority(action_rec, confidence, position)
                
                # リスクレベルの判定
                risk_level = self._determine_risk_level(position)
                
                # 次のアクションの決定
                next_action = self._determine_next_action(action_rec, position)
                
                # 目標価格・損切りの計算
                target_price, stop_loss = self._calculate_price_targets(position, action_rec)
                
                summary = PositionSummary(
                    symbol=symbol,
                    company_name=self._get_company_name(symbol),
                    current_price=position.current_price,
                    quantity=position.quantity,
                    total_value=position.current_price * position.quantity,
                    cost_basis=position.entry_price,
                    unrealized_pnl=position.unrealized_pnl,
                    pnl_percentage=((position.current_price - position.entry_price) / position.entry_price) * 100,
                    action_recommendation=action_rec,
                    confidence=confidence,
                    priority=priority,
                    risk_level=risk_level,
                    next_action=next_action,
                    target_price=target_price,
                    stop_loss=stop_loss
                )
                summaries.append(summary)
                
            except Exception as e:
                logger.error(f"ポジションサマリー計算エラー {symbol}: {e}")
        
        return summaries
    
    def _determine_investment_action(self, symbol: str, position: Position) -> InvestmentAction:
        """投資アクションの判定"""
        try:
            # 技術分析による判定
            pnl_percentage = ((position.current_price - position.entry_price) / position.entry_price) * 100
            
            # 損切りの判定
            if position.current_price <= position.stop_loss:
                return InvestmentAction.STRONG_SELL
            
            # 利確の判定
            if position.current_price >= position.take_profit:
                return InvestmentAction.SELL
            
            # 技術指標による判定（簡易版）
            if pnl_percentage > 10:
                return InvestmentAction.SELL
            elif pnl_percentage < -5:
                return InvestmentAction.STRONG_SELL
            elif pnl_percentage > 5:
                return InvestmentAction.HOLD
            elif pnl_percentage < -2:
                return InvestmentAction.BUY
            else:
                return InvestmentAction.HOLD
                
        except Exception as e:
            logger.error(f"投資アクション判定エラー {symbol}: {e}")
            return InvestmentAction.HOLD
    
    def _calculate_confidence(self, symbol: str, position: Position) -> float:
        """信頼度の計算"""
        try:
            # ポジションサイズとリスクに基づく信頼度
            position_ratio = (position.current_price * position.quantity) / 1000000  # ポートフォリオ比率
            
            if position_ratio > 0.1:  # 10%以上
                base_confidence = 0.8
            elif position_ratio > 0.05:  # 5%以上
                base_confidence = 0.7
            else:
                base_confidence = 0.6
            
            # 損益状況による調整
            pnl_percentage = ((position.current_price - position.entry_price) / position.entry_price) * 100
            if abs(pnl_percentage) > 10:
                base_confidence *= 0.9  # 大きな変動は信頼度を下げる
            
            return min(0.95, max(0.1, base_confidence))
            
        except Exception as e:
            logger.error(f"信頼度計算エラー {symbol}: {e}")
            return 0.5
    
    def _determine_priority(self, action: InvestmentAction, confidence: float, position: Position) -> PriorityLevel:
        """優先度の判定"""
        try:
            pnl_percentage = ((position.current_price - position.entry_price) / position.entry_price) * 100
            
            # 損切りの場合は最高優先度
            if position.current_price <= position.stop_loss:
                return PriorityLevel.CRITICAL
            
            # 大きな損失の場合は高優先度
            if pnl_percentage < -5:
                return PriorityLevel.HIGH
            
            # 利確の場合は中優先度
            if position.current_price >= position.take_profit:
                return PriorityLevel.MEDIUM
            
            # 信頼度とアクションに基づく判定
            if confidence > 0.8 and action in [InvestmentAction.STRONG_BUY, InvestmentAction.STRONG_SELL]:
                return PriorityLevel.HIGH
            elif confidence > 0.6 and action in [InvestmentAction.BUY, InvestmentAction.SELL]:
                return PriorityLevel.MEDIUM
            else:
                return PriorityLevel.LOW
                
        except Exception as e:
            logger.error(f"優先度判定エラー: {e}")
            return PriorityLevel.LOW
    
    def _determine_risk_level(self, position: Position) -> str:
        """リスクレベルの判定"""
        try:
            pnl_percentage = ((position.current_price - position.entry_price) / position.entry_price) * 100
            
            if abs(pnl_percentage) > 15:
                return "HIGH"
            elif abs(pnl_percentage) > 8:
                return "MEDIUM"
            else:
                return "LOW"
                
        except Exception as e:
            logger.error(f"リスクレベル判定エラー: {e}")
            return "MEDIUM"
    
    def _determine_next_action(self, action: InvestmentAction, position: Position) -> str:
        """次のアクションの決定"""
        action_map = {
            InvestmentAction.STRONG_BUY: "積極的に買い増しを検討",
            InvestmentAction.BUY: "買い増しを検討",
            InvestmentAction.HOLD: "現状維持",
            InvestmentAction.SELL: "利確を検討",
            InvestmentAction.STRONG_SELL: "即座に売却を検討"
        }
        return action_map.get(action, "現状維持")
    
    def _calculate_price_targets(self, position: Position, action: InvestmentAction) -> Tuple[Optional[float], Optional[float]]:
        """価格目標の計算"""
        try:
            if action in [InvestmentAction.STRONG_SELL, InvestmentAction.SELL]:
                return None, position.current_price * 0.95  # 5%下げで損切り
            elif action in [InvestmentAction.STRONG_BUY, InvestmentAction.BUY]:
                return position.current_price * 1.15, position.current_price * 0.92  # 15%上げ、8%下げ
            else:
                return position.take_profit, position.stop_loss
                
        except Exception as e:
            logger.error(f"価格目標計算エラー: {e}")
            return None, None
    
    def _get_company_name(self, symbol: str) -> str:
        """会社名の取得"""
        company_names = {
            "7203.T": "トヨタ自動車",
            "6758.T": "ソニーグループ",
            "6861.T": "キーエンス",
            "9984.T": "ソフトバンクグループ"
        }
        return company_names.get(symbol, symbol)
    
    def get_investment_recommendations(self) -> List[InvestmentRecommendation]:
        """投資推奨事項の取得"""
        recommendations = []
        
        # 監視銘柄の推奨事項
        for symbol in self.watchlist:
            if symbol not in self.positions:
                try:
                    # 新規投資の推奨事項
                    recommendation = self._analyze_new_investment(symbol)
                    if recommendation:
                        recommendations.append(recommendation)
                except Exception as e:
                    logger.error(f"新規投資分析エラー {symbol}: {e}")
        
        # 既存ポジションの推奨事項
        for symbol, position in self.positions.items():
            try:
                action = self._determine_investment_action(symbol, position)
                if action != InvestmentAction.HOLD:
                    recommendation = InvestmentRecommendation(
                        symbol=symbol,
                        action=action,
                        confidence=self._calculate_confidence(symbol, position),
                        priority=self._determine_priority(action, self._calculate_confidence(symbol, position), position),
                        reason=self._get_recommendation_reason(symbol, action),
                        target_price=self._calculate_price_targets(position, action)[0],
                        stop_loss=self._calculate_price_targets(position, action)[1],
                        position_size=self._calculate_position_size(symbol, action),
                        expected_return=self._calculate_expected_return(symbol, action),
                        risk_level=self._determine_risk_level(position),
                        timeframe="1-3ヶ月"
                    )
                    recommendations.append(recommendation)
            except Exception as e:
                logger.error(f"推奨事項生成エラー {symbol}: {e}")
        
        # 優先度順にソート
        recommendations.sort(key=lambda x: x.priority.value, reverse=True)
        return recommendations
    
    def _analyze_new_investment(self, symbol: str) -> Optional[InvestmentRecommendation]:
        """新規投資の分析"""
        try:
            # 簡易的な分析（実際の実装では詳細な分析を実行）
            if np.random.random() > 0.7:  # 30%の確率で推奨
                return InvestmentRecommendation(
                    symbol=symbol,
                    action=InvestmentAction.BUY,
                    confidence=0.7,
                    priority=PriorityLevel.MEDIUM,
                    reason="技術指標が良好",
                    target_price=None,
                    stop_loss=None,
                    position_size=100,
                    expected_return=0.1,
                    risk_level="MEDIUM",
                    timeframe="1-3ヶ月"
                )
            return None
        except Exception as e:
            logger.error(f"新規投資分析エラー {symbol}: {e}")
            return None
    
    def _get_recommendation_reason(self, symbol: str, action: InvestmentAction) -> str:
        """推奨理由の取得"""
        reasons = {
            InvestmentAction.STRONG_BUY: "技術指標が非常に良好で、上昇トレンドが継続",
            InvestmentAction.BUY: "技術指標が良好で、買い場の可能性が高い",
            InvestmentAction.HOLD: "現状維持が最適",
            InvestmentAction.SELL: "利確のタイミング",
            InvestmentAction.STRONG_SELL: "損切りの必要性が高い"
        }
        return reasons.get(action, "分析中")
    
    def _calculate_position_size(self, symbol: str, action: InvestmentAction) -> Optional[int]:
        """ポジションサイズの計算"""
        if action in [InvestmentAction.STRONG_BUY, InvestmentAction.BUY]:
            return 100  # サンプル値
        return None
    
    def _calculate_expected_return(self, symbol: str, action: InvestmentAction) -> Optional[float]:
        """期待リターンの計算"""
        if action in [InvestmentAction.STRONG_BUY, InvestmentAction.BUY]:
            return 0.1  # 10%の期待リターン
        elif action in [InvestmentAction.STRONG_SELL, InvestmentAction.SELL]:
            return -0.05  # 5%の損失回避
        return None
    
    def get_market_overview(self) -> MarketOverview:
        """市場概況の取得"""
        try:
            # 市場トレンドの判定
            market_trend = "上昇" if np.random.random() > 0.5 else "下落"
            
            # ボラティリティレベル
            volatility_level = "HIGH" if np.random.random() > 0.7 else "MEDIUM"
            
            # センチメントスコア
            sentiment_score = np.random.uniform(-1, 1)
            
            # キーイベント
            key_events = [
                "日銀金融政策決定会合",
                "米国雇用統計発表",
                "企業業績発表期"
            ]
            
            # セクター別パフォーマンス
            sector_performance = {
                "テクノロジー": np.random.uniform(-0.05, 0.05),
                "金融": np.random.uniform(-0.03, 0.03),
                "製造業": np.random.uniform(-0.02, 0.04),
                "小売": np.random.uniform(-0.01, 0.02)
            }
            
            # 市場アラート
            market_alert = None
            if volatility_level == "HIGH":
                market_alert = "高ボラティリティ環境のため注意が必要"
            
            return MarketOverview(
                market_trend=market_trend,
                volatility_level=volatility_level,
                sentiment_score=sentiment_score,
                key_events=key_events,
                sector_performance=sector_performance,
                market_alert=market_alert
            )
            
        except Exception as e:
            logger.error(f"市場概況取得エラー: {e}")
            return MarketOverview(
                market_trend="不明",
                volatility_level="MEDIUM",
                sentiment_score=0.0,
                key_events=[],
                sector_performance={},
                market_alert=None
            )
    
    async def generate_dashboard_data(self) -> Dict[str, Any]:
        """ダッシュボードデータの生成"""
        try:
            # 全データの更新
            await self._update_all_data()
            
            # 各コンポーネントのデータ取得
            pnl_summary = self.get_pnl_summary()
            position_summaries = self.get_position_summaries()
            recommendations = self.get_investment_recommendations()
            market_overview = self.get_market_overview()
            
            dashboard_data = {
                "timestamp": datetime.now().isoformat(),
                "pnl_summary": asdict(pnl_summary),
                "positions": [asdict(pos) for pos in position_summaries],
                "recommendations": [asdict(rec) for rec in recommendations],
                "market_overview": asdict(market_overview),
                "last_update": self.last_update.isoformat() if self.last_update else None
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"ダッシュボードデータ生成エラー: {e}")
            return {}
    
    async def save_dashboard_data(self, output_path: str = "data/personal_investment_dashboard.json"):
        """ダッシュボードデータの保存"""
        try:
            data = await self.generate_dashboard_data()
            
            # ディレクトリの作成
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # データの保存
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"ダッシュボードデータを保存: {output_path}")
            
        except Exception as e:
            logger.error(f"ダッシュボードデータ保存エラー: {e}")


async def main():
    """メイン実行関数"""
    # ログ設定
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # ダッシュボードの初期化
    dashboard = PersonalInvestmentDashboard()
    
    # 監視銘柄の設定
    symbols = ["7203.T", "6758.T", "6861.T", "9984.T", "9432.T"]
    
    # ダッシュボードの初期化
    await dashboard.initialize_dashboard(symbols, initial_capital=1000000)
    
    # ダッシュボードデータの生成と保存
    await dashboard.save_dashboard_data()
    
    print("個人投資ダッシュボードのデータ生成が完了しました。")


if __name__ == "__main__":
    asyncio.run(main())
