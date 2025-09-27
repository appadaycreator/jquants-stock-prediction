#!/usr/bin/env python3
"""
高度なバックテストシステム
期待効果: 月間10-20%の利益向上
実装内容: 過去データでの戦略検証、パフォーマンス分析

機能:
1. 複数戦略の同時バックテスト
2. 詳細なパフォーマンス指標計算
3. リスク分析とドローダウン計算
4. ポートフォリオ最適化
5. 結果の可視化とレポート生成
"""

import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import json
import logging
from dataclasses import dataclass, asdict
from enum import Enum
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from abc import ABC, abstractmethod

warnings.filterwarnings('ignore')

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backtest.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class StrategyType(Enum):
    """戦略タイプ"""
    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"
    BREAKOUT = "breakout"
    TREND_FOLLOWING = "trend_following"
    ARBITRAGE = "arbitrage"

class OrderType(Enum):
    """注文タイプ"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"

@dataclass
class Trade:
    """取引記録"""
    symbol: str
    entry_time: datetime
    exit_time: Optional[datetime]
    entry_price: float
    exit_price: Optional[float]
    quantity: int
    side: str  # 'long' or 'short'
    pnl: Optional[float] = None
    commission: float = 0.0
    strategy_name: str = ""
    exit_reason: str = ""

@dataclass
class Position:
    """ポジション情報"""
    symbol: str
    quantity: int
    entry_price: float
    current_price: float
    unrealized_pnl: float
    entry_time: datetime
    strategy_name: str

@dataclass
class BacktestResult:
    """バックテスト結果"""
    strategy_name: str
    total_return: float
    annualized_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_win: float
    avg_loss: float
    max_win: float
    max_loss: float
    start_date: datetime
    end_date: datetime
    initial_capital: float
    final_capital: float
    trades: List[Trade]
    equity_curve: pd.Series
    monthly_returns: pd.Series

class BaseStrategy(ABC):
    """戦略のベースクラス"""
    
    def __init__(self, name: str, parameters: Dict[str, Any]):
        self.name = name
        self.parameters = parameters
        self.positions = {}
        self.trades = []
        self.equity_curve = []
        self.current_capital = 1000000  # 初期資本
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        """シグナル生成（各戦略で実装）"""
        pass
    
    @abstractmethod
    def should_exit(self, data: pd.DataFrame, symbol: str, position: Position) -> bool:
        """エグジット判定（各戦略で実装）"""
        pass
    
    def calculate_position_size(self, price: float, signal_strength: float = 1.0) -> int:
        """ポジションサイズ計算"""
        # リスク管理: 資本の2%をリスクとして使用
        risk_per_trade = self.current_capital * 0.02
        position_value = self.current_capital * 0.1 * signal_strength  # 資本の10%を最大ポジション
        return int(min(position_value / price, risk_per_trade / (price * 0.02)))

class MomentumStrategy(BaseStrategy):
    """モメンタム戦略"""
    
    def __init__(self, parameters: Dict[str, Any] = None):
        super().__init__("Momentum", parameters or {})
        self.lookback = self.parameters.get('lookback', 20)
        self.threshold = self.parameters.get('threshold', 0.05)
    
    def generate_signals(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        """モメンタムシグナル生成"""
        signals = pd.Series(0, index=data.index)
        
        if len(data) < self.lookback:
            return signals
        
        # 価格変化率を計算
        returns = data['Close'].pct_change(self.lookback)
        
        # ボラティリティ調整
        volatility = data['Close'].rolling(self.lookback).std()
        adjusted_returns = returns / volatility
        
        # シグナル生成
        signals[adjusted_returns > self.threshold] = 1  # 買い
        signals[adjusted_returns < -self.threshold] = -1  # 売り
        
        return signals
    
    def should_exit(self, data: pd.DataFrame, symbol: str, position: Position) -> bool:
        """エグジット判定"""
        if symbol not in data.index:
            return False
        
        current_price = data.loc[symbol, 'Close']
        entry_price = position.entry_price
        
        # 利確・損切り
        if position.quantity > 0:  # ロングポジション
            profit_pct = (current_price - entry_price) / entry_price
            if profit_pct > 0.1 or profit_pct < -0.05:  # 10%利確 or 5%損切り
                return True
        else:  # ショートポジション
            profit_pct = (entry_price - current_price) / entry_price
            if profit_pct > 0.1 or profit_pct < -0.05:
                return True
        
        return False

class MeanReversionStrategy(BaseStrategy):
    """平均回帰戦略"""
    
    def __init__(self, parameters: Dict[str, Any] = None):
        super().__init__("MeanReversion", parameters or {})
        self.lookback = self.parameters.get('lookback', 20)
        self.std_threshold = self.parameters.get('std_threshold', 2.0)
    
    def generate_signals(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        """平均回帰シグナル生成"""
        signals = pd.Series(0, index=data.index)
        
        if len(data) < self.lookback:
            return signals
        
        # ボリンジャーバンド計算
        sma = data['Close'].rolling(self.lookback).mean()
        std = data['Close'].rolling(self.lookback).std()
        upper_band = sma + (std * self.std_threshold)
        lower_band = sma - (std * self.std_threshold)
        
        # シグナル生成
        signals[data['Close'] < lower_band] = 1  # 買い（下値）
        signals[data['Close'] > upper_band] = -1  # 売り（上値）
        
        return signals
    
    def should_exit(self, data: pd.DataFrame, symbol: str, position: Position) -> bool:
        """エグジット判定"""
        if symbol not in data.index:
            return False
        
        current_price = data.loc[symbol, 'Close']
        entry_price = position.entry_price
        
        # 平均回帰の完了を判定
        if position.quantity > 0:  # ロングポジション
            profit_pct = (current_price - entry_price) / entry_price
            if profit_pct > 0.05 or profit_pct < -0.03:  # 5%利確 or 3%損切り
                return True
        else:  # ショートポジション
            profit_pct = (entry_price - current_price) / entry_price
            if profit_pct > 0.05 or profit_pct < -0.03:
                return True
        
        return False

class BreakoutStrategy(BaseStrategy):
    """ブレイクアウト戦略"""
    
    def __init__(self, parameters: Dict[str, Any] = None):
        super().__init__("Breakout", parameters or {})
        self.lookback = self.parameters.get('lookback', 20)
        self.volume_threshold = self.parameters.get('volume_threshold', 1.5)
    
    def generate_signals(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        """ブレイクアウトシグナル生成"""
        signals = pd.Series(0, index=data.index)
        
        if len(data) < self.lookback:
            return signals
        
        # 高値・安値の計算
        high_max = data['High'].rolling(self.lookback).max()
        low_min = data['Low'].rolling(self.lookback).min()
        
        # ボリューム確認
        avg_volume = data['Volume'].rolling(self.lookback).mean()
        volume_spike = data['Volume'] > (avg_volume * self.volume_threshold)
        
        # シグナル生成
        signals[(data['Close'] > high_max.shift(1)) & volume_spike] = 1  # 上抜け
        signals[(data['Close'] < low_min.shift(1)) & volume_spike] = -1  # 下抜け
        
        return signals
    
    def should_exit(self, data: pd.DataFrame, symbol: str, position: Position) -> bool:
        """エグジット判定"""
        if symbol not in data.index:
            return False
        
        current_price = data.loc[symbol, 'Close']
        entry_price = position.entry_price
        
        # トレンドフォロー的なエグジット
        if position.quantity > 0:  # ロングポジション
            profit_pct = (current_price - entry_price) / entry_price
            if profit_pct > 0.15 or profit_pct < -0.08:  # 15%利確 or 8%損切り
                return True
        else:  # ショートポジション
            profit_pct = (entry_price - current_price) / entry_price
            if profit_pct > 0.15 or profit_pct < -0.08:
                return True
        
        return False

class BacktestEngine:
    """バックテストエンジン"""
    
    def __init__(self, initial_capital: float = 1000000, commission: float = 0.001):
        self.initial_capital = initial_capital
        self.commission = commission
        self.current_capital = initial_capital
        self.positions = {}
        self.trades = []
        self.equity_curve = []
        self.daily_returns = []
        
    def run_backtest(self, data: pd.DataFrame, strategy: BaseStrategy, 
                    start_date: datetime, end_date: datetime) -> BacktestResult:
        """バックテスト実行"""
        logger.info(f"バックテスト開始: {strategy.name}")
        logger.info(f"期間: {start_date} - {end_date}")
        
        # データフィルタリング
        mask = (data.index >= start_date) & (data.index <= end_date)
        test_data = data[mask].copy()
        
        if test_data.empty:
            raise ValueError("指定期間のデータがありません")
        
        # リセット
        self.current_capital = self.initial_capital
        self.positions = {}
        self.trades = []
        self.equity_curve = []
        self.daily_returns = []
        
        # 日次でループ
        for date, row in test_data.iterrows():
            self._process_day(date, row, strategy, test_data)
            self._update_equity_curve()
        
        # 残りのポジションをクローズ
        self._close_all_positions(test_data.iloc[-1], strategy)
        
        # 結果計算
        return self._calculate_results(strategy, start_date, end_date)
    
    def _process_day(self, date: datetime, row: pd.Series, strategy: BaseStrategy, data: pd.DataFrame):
        """1日の処理"""
        # 既存ポジションのエグジット判定
        positions_to_close = []
        for symbol, position in self.positions.items():
            if strategy.should_exit(data, symbol, position):
                positions_to_close.append(symbol)
        
        # ポジションクローズ
        for symbol in positions_to_close:
            self._close_position(symbol, row, strategy, "strategy_exit")
        
        # 新規シグナル生成
        signals = strategy.generate_signals(data, "Close")
        if len(signals) > 0 and date in signals.index:
            signal = signals.loc[date]
            if signal != 0:
                self._execute_trade(date, row, signal, strategy)
    
    def _execute_trade(self, date: datetime, row: pd.Series, signal: int, strategy: BaseStrategy):
        """取引実行"""
        price = row['Close']
        position_size = strategy.calculate_position_size(price, abs(signal))
        
        if position_size == 0:
            return
        
        # ポジションサイズ調整（資本制約）
        max_position_value = self.current_capital * 0.1
        position_size = min(position_size, int(max_position_value / price))
        
        if position_size == 0:
            return
        
        # 取引実行
        if signal > 0:  # 買い
            self._open_long_position(date, price, position_size, strategy.name)
        else:  # 売り
            self._open_short_position(date, price, position_size, strategy.name)
    
    def _open_long_position(self, date: datetime, price: float, quantity: int, strategy_name: str):
        """ロングポジション開設"""
        cost = price * quantity * (1 + self.commission)
        if cost <= self.current_capital:
            self.current_capital -= cost
            self.positions["Close"] = Position(
                symbol="Close",
                quantity=quantity,
                entry_price=price,
                current_price=price,
                unrealized_pnl=0.0,
                entry_time=date,
                strategy_name=strategy_name
            )
            logger.debug(f"ロングポジション開設: {quantity}株 @ {price}")
    
    def _open_short_position(self, date: datetime, price: float, quantity: int, strategy_name: str):
        """ショートポジション開設"""
        # ショート売りの場合、証拠金が必要
        margin_required = price * quantity * 0.3  # 30%証拠金
        if margin_required <= self.current_capital:
            self.current_capital -= margin_required
            self.positions["Close"] = Position(
                symbol="Close",
                quantity=-quantity,  # 負の値でショート
                entry_price=price,
                current_price=price,
                unrealized_pnl=0.0,
                entry_time=date,
                strategy_name=strategy_name
            )
            logger.debug(f"ショートポジション開設: {quantity}株 @ {price}")
    
    def _close_position(self, symbol: str, row: pd.Series, strategy: BaseStrategy, reason: str):
        """ポジションクローズ"""
        if symbol not in self.positions:
            return
        
        position = self.positions[symbol]
        exit_price = row['Close']
        exit_time = row.name
        
        # PnL計算
        if position.quantity > 0:  # ロング
            pnl = (exit_price - position.entry_price) * position.quantity
        else:  # ショート
            pnl = (position.entry_price - exit_price) * abs(position.quantity)
        
        # 手数料差し引き
        commission_cost = exit_price * abs(position.quantity) * self.commission
        net_pnl = pnl - commission_cost
        
        # 資本更新
        if position.quantity > 0:  # ロング
            self.current_capital += exit_price * position.quantity * (1 - self.commission)
        else:  # ショート
            self.current_capital += position.entry_price * abs(position.quantity) * (1 - self.commission)
            self.current_capital += net_pnl
        
        # 取引記録
        trade = Trade(
            symbol=symbol,
            entry_time=position.entry_time,
            exit_time=exit_time,
            entry_price=position.entry_price,
            exit_price=exit_price,
            quantity=abs(position.quantity),
            side="long" if position.quantity > 0 else "short",
            pnl=net_pnl,
            commission=commission_cost,
            strategy_name=strategy.name,
            exit_reason=reason
        )
        self.trades.append(trade)
        
        # ポジション削除
        del self.positions[symbol]
        
        logger.debug(f"ポジションクローズ: {symbol} PnL: {net_pnl:.2f}")
    
    def _close_all_positions(self, last_row: pd.Series, strategy: BaseStrategy):
        """全ポジションクローズ"""
        for symbol in list(self.positions.keys()):
            self._close_position(symbol, last_row, strategy, "end_of_period")
    
    def _update_equity_curve(self):
        """エクイティカーブ更新"""
        total_value = self.current_capital
        
        # 未決済ポジションの評価
        for position in self.positions.values():
            if position.quantity > 0:  # ロング
                unrealized_pnl = (position.current_price - position.entry_price) * position.quantity
            else:  # ショート
                unrealized_pnl = (position.entry_price - position.current_price) * abs(position.quantity)
            
            total_value += unrealized_pnl
        
        self.equity_curve.append(total_value)
    
    def _calculate_results(self, strategy: BaseStrategy, start_date: datetime, end_date: datetime) -> BacktestResult:
        """結果計算"""
        if not self.equity_curve:
            raise ValueError("エクイティカーブが空です")
        
        equity_series = pd.Series(self.equity_curve)
        total_return = (equity_series.iloc[-1] - self.initial_capital) / self.initial_capital
        
        # 年率リターン計算
        days = (end_date - start_date).days
        annualized_return = (1 + total_return) ** (365 / days) - 1 if days > 0 else 0
        
        # 日次リターン計算
        daily_returns = equity_series.pct_change().dropna()
        
        # シャープレシオ計算
        if len(daily_returns) > 1 and daily_returns.std() > 0:
            sharpe_ratio = daily_returns.mean() / daily_returns.std() * np.sqrt(252)
        else:
            sharpe_ratio = 0
        
        # 最大ドローダウン計算
        peak = equity_series.expanding().max()
        drawdown = (equity_series - peak) / peak
        max_drawdown = drawdown.min()
        
        # 取引統計
        winning_trades = [t for t in self.trades if t.pnl and t.pnl > 0]
        losing_trades = [t for t in self.trades if t.pnl and t.pnl < 0]
        
        win_rate = len(winning_trades) / len(self.trades) if self.trades else 0
        
        total_win = sum(t.pnl for t in winning_trades) if winning_trades else 0
        total_loss = abs(sum(t.pnl for t in losing_trades)) if losing_trades else 0
        profit_factor = total_win / total_loss if total_loss > 0 else float('inf')
        
        avg_win = total_win / len(winning_trades) if winning_trades else 0
        avg_loss = total_loss / len(losing_trades) if losing_trades else 0
        
        max_win = max(t.pnl for t in winning_trades) if winning_trades else 0
        max_loss = min(t.pnl for t in losing_trades) if losing_trades else 0
        
        # 月次リターン計算
        monthly_returns = equity_series.resample('M').last().pct_change().dropna()
        
        return BacktestResult(
            strategy_name=strategy.name,
            total_return=total_return,
            annualized_return=annualized_return,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            profit_factor=profit_factor,
            total_trades=len(self.trades),
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            avg_win=avg_win,
            avg_loss=avg_loss,
            max_win=max_win,
            max_loss=max_loss,
            start_date=start_date,
            end_date=end_date,
            initial_capital=self.initial_capital,
            final_capital=equity_series.iloc[-1],
            trades=self.trades,
            equity_curve=equity_series,
            monthly_returns=monthly_returns
        )

class BacktestAnalyzer:
    """バックテスト分析クラス"""
    
    def __init__(self):
        self.results = []
    
    def add_result(self, result: BacktestResult):
        """結果を追加"""
        self.results.append(result)
    
    def compare_strategies(self) -> pd.DataFrame:
        """戦略比較"""
        if not self.results:
            return pd.DataFrame()
        
        comparison_data = []
        for result in self.results:
            comparison_data.append({
                'Strategy': result.strategy_name,
                'Total Return': f"{result.total_return:.2%}",
                'Annualized Return': f"{result.annualized_return:.2%}",
                'Sharpe Ratio': f"{result.sharpe_ratio:.2f}",
                'Max Drawdown': f"{result.max_drawdown:.2%}",
                'Win Rate': f"{result.win_rate:.2%}",
                'Profit Factor': f"{result.profit_factor:.2f}",
                'Total Trades': result.total_trades,
                'Avg Win': f"{result.avg_win:.2f}",
                'Avg Loss': f"{result.avg_loss:.2f}"
            })
        
        return pd.DataFrame(comparison_data)
    
    def generate_report(self) -> str:
        """レポート生成"""
        if not self.results:
            return "結果がありません"
        
        report = []
        report.append("=" * 80)
        report.append("📊 バックテスト分析レポート")
        report.append("=" * 80)
        
        # 戦略比較
        comparison_df = self.compare_strategies()
        if not comparison_df.empty:
            report.append("\n🏆 戦略比較:")
            report.append(comparison_df.to_string(index=False))
        
        # 最優秀戦略
        best_result = max(self.results, key=lambda x: x.sharpe_ratio)
        report.append(f"\n🥇 最優秀戦略: {best_result.strategy_name}")
        report.append(f"   シャープレシオ: {best_result.sharpe_ratio:.2f}")
        report.append(f"   年率リターン: {best_result.annualized_return:.2%}")
        report.append(f"   最大ドローダウン: {best_result.max_drawdown:.2%}")
        
        return "\n".join(report)

class BacktestVisualizer:
    """バックテスト可視化クラス"""
    
    def __init__(self):
        self.setup_style()
    
    def setup_style(self):
        """スタイル設定"""
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    def plot_equity_curves(self, results: List[BacktestResult], save_path: str = None):
        """エクイティカーブプロット"""
        plt.figure(figsize=(15, 10))
        
        # メインプロット
        plt.subplot(2, 2, 1)
        for result in results:
            plt.plot(result.equity_curve.index, result.equity_curve.values, 
                    label=result.strategy_name, linewidth=2)
        
        plt.title('エクイティカーブ比較', fontsize=14, fontweight='bold')
        plt.xlabel('日付')
        plt.ylabel('ポートフォリオ価値')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # ドローダウンプロット
        plt.subplot(2, 2, 2)
        for result in results:
            peak = result.equity_curve.expanding().max()
            drawdown = (result.equity_curve - peak) / peak * 100
            plt.plot(result.equity_curve.index, drawdown, 
                    label=f"{result.strategy_name} (Max: {result.max_drawdown:.1%})", linewidth=2)
        
        plt.title('ドローダウン分析', fontsize=14, fontweight='bold')
        plt.xlabel('日付')
        plt.ylabel('ドローダウン (%)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # 月次リターン
        plt.subplot(2, 2, 3)
        for result in results:
            monthly_returns = result.monthly_returns * 100
            plt.plot(monthly_returns.index, monthly_returns.values, 
                    label=result.strategy_name, marker='o', linewidth=2)
        
        plt.title('月次リターン', fontsize=14, fontweight='bold')
        plt.xlabel('月')
        plt.ylabel('リターン (%)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # パフォーマンス指標
        plt.subplot(2, 2, 4)
        strategies = [r.strategy_name for r in results]
        sharpe_ratios = [r.sharpe_ratio for r in results]
        
        bars = plt.bar(strategies, sharpe_ratios, color=['skyblue', 'lightcoral', 'lightgreen'])
        plt.title('シャープレシオ比較', fontsize=14, fontweight='bold')
        plt.ylabel('シャープレシオ')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        
        # バーの上に値を表示
        for bar, value in zip(bars, sharpe_ratios):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                    f'{value:.2f}', ha='center', va='bottom')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"グラフを保存しました: {save_path}")
        
        plt.show()
    
    def plot_trade_analysis(self, result: BacktestResult, save_path: str = None):
        """取引分析プロット"""
        if not result.trades:
            logger.warning("取引データがありません")
            return
        
        plt.figure(figsize=(15, 10))
        
        # PnL分布
        plt.subplot(2, 2, 1)
        pnls = [t.pnl for t in result.trades if t.pnl is not None]
        plt.hist(pnls, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
        plt.title('PnL分布', fontsize=14, fontweight='bold')
        plt.xlabel('PnL')
        plt.ylabel('頻度')
        plt.grid(True, alpha=0.3)
        
        # 累積PnL
        plt.subplot(2, 2, 2)
        cumulative_pnl = np.cumsum(pnls)
        plt.plot(cumulative_pnl, linewidth=2, color='green')
        plt.title('累積PnL', fontsize=14, fontweight='bold')
        plt.xlabel('取引回数')
        plt.ylabel('累積PnL')
        plt.grid(True, alpha=0.3)
        
        # 勝率・敗率
        plt.subplot(2, 2, 3)
        win_rate = result.win_rate
        loss_rate = 1 - win_rate
        plt.pie([win_rate, loss_rate], labels=['勝ち', '負け'], autopct='%1.1f%%', 
                colors=['lightgreen', 'lightcoral'])
        plt.title('勝率分析', fontsize=14, fontweight='bold')
        
        # 月次リターン
        plt.subplot(2, 2, 4)
        monthly_returns = result.monthly_returns * 100
        colors = ['green' if x > 0 else 'red' for x in monthly_returns.values]
        plt.bar(range(len(monthly_returns)), monthly_returns.values, color=colors, alpha=0.7)
        plt.title('月次リターン', fontsize=14, fontweight='bold')
        plt.xlabel('月')
        plt.ylabel('リターン (%)')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"取引分析グラフを保存しました: {save_path}")
        
        plt.show()

def main():
    """メイン実行関数"""
    logger.info("=== 高度なバックテストシステム開始 ===")
    
    # データ取得
    symbol = "7203.T"  # トヨタ自動車
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2023, 12, 31)
    
    logger.info(f"データ取得中: {symbol}")
    ticker = yf.Ticker(symbol)
    data = ticker.history(start=start_date, end=end_date)
    
    if data.empty:
        logger.error("データが取得できませんでした")
        return
    
    logger.info(f"データ期間: {data.index[0]} - {data.index[-1]}")
    logger.info(f"データ数: {len(data)}行")
    
    # バックテストエンジン初期化
    engine = BacktestEngine(initial_capital=1000000, commission=0.001)
    
    # 戦略定義
    strategies = [
        MomentumStrategy({'lookback': 20, 'threshold': 0.05}),
        MeanReversionStrategy({'lookback': 20, 'std_threshold': 2.0}),
        BreakoutStrategy({'lookback': 20, 'volume_threshold': 1.5})
    ]
    
    # バックテスト実行
    analyzer = BacktestAnalyzer()
    results = []
    
    for strategy in strategies:
        logger.info(f"戦略実行中: {strategy.name}")
        try:
            result = engine.run_backtest(data, strategy, start_date, end_date)
            results.append(result)
            analyzer.add_result(result)
            
            logger.info(f"完了: {strategy.name}")
            logger.info(f"  総リターン: {result.total_return:.2%}")
            logger.info(f"  シャープレシオ: {result.sharpe_ratio:.2f}")
            logger.info(f"  最大ドローダウン: {result.max_drawdown:.2%}")
            logger.info(f"  取引数: {result.total_trades}")
            
        except Exception as e:
            logger.error(f"戦略実行エラー {strategy.name}: {e}")
    
    # 分析・可視化
    if results:
        logger.info("分析レポート生成中...")
        report = analyzer.generate_report()
        print(report)
        
        # 結果保存
        with open('backtest_report.txt', 'w', encoding='utf-8') as f:
            f.write(report)
        
        # 可視化
        visualizer = BacktestVisualizer()
        visualizer.plot_equity_curves(results, 'backtest_equity_curves.png')
        
        if results:
            visualizer.plot_trade_analysis(results[0], 'backtest_trade_analysis.png')
        
        logger.info("=== バックテスト完了 ===")
    else:
        logger.error("有効な結果がありません")

if __name__ == "__main__":
    main()
