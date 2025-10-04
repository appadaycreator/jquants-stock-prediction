#!/usr/bin/env python3
"""
記事の手法を統合した高精度バックテストシステム
記事の手法を超える高度なバックテスト機能を実装
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta
import logging

class ArticleInspiredBacktest:
    """記事の手法を統合した高精度バックテストシステム"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """初期化"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # 記事の手法設定
        self.article_threshold = 0.5  # 記事と同じ閾値
        self.article_position_size = 1  # 記事と同じ1株単位
        
        # 改善された設定
        self.confidence_threshold = self.config.get('confidence_threshold', 0.7)
        self.enhanced_position_sizing = self.config.get('enhanced_position_sizing', True)
        self.risk_management = self.config.get('risk_management', True)
        
        # 取引コスト設定
        self.commission_rate = self.config.get('commission_rate', 0.001)  # 0.1%
        self.slippage_rate = self.config.get('slippage_rate', 0.0005)  # 0.05%
        
        # バックテスト結果
        self.trades = []
        self.equity_curve = []
        self.performance_metrics = {}
        
    def run_article_method_backtest(self, predictions: List[float], prices: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        記事の手法によるバックテスト
        記事と同じ手法でバックテストを実行
        """
        try:
            self.logger.info("記事の手法によるバックテストを開始")
            
            # 初期設定
            initial_capital = self.config.get('initial_capital', 100000)
            current_capital = initial_capital
            self.equity_curve = [initial_capital]
            
            # 取引履歴の初期化
            self.trades = []
            
            # 各予測に対して取引判定
            for i, (prediction, price_data) in enumerate(zip(predictions, prices)):
                # 記事の手法: 0.5閾値での判定
                if prediction >= self.article_threshold:
                    # 買い注文
                    trade_result = self._execute_buy_trade(price_data, prediction, current_capital)
                else:
                    # 空売り注文
                    trade_result = self._execute_sell_trade(price_data, prediction, current_capital)
                
                if trade_result['executed']:
                    self.trades.append(trade_result)
                    current_capital = trade_result['capital_after']
                    self.equity_curve.append(current_capital)
            
            # パフォーマンス指標の計算
            performance = self._calculate_performance_metrics(initial_capital, current_capital)
            
            return {
                'method': 'article_method',
                'initial_capital': initial_capital,
                'final_capital': current_capital,
                'total_return': performance['total_return'],
                'total_trades': len(self.trades),
                'win_rate': performance['win_rate'],
                'max_drawdown': performance['max_drawdown'],
                'sharpe_ratio': performance['sharpe_ratio'],
                'trades': self.trades,
                'equity_curve': self.equity_curve
            }
            
        except Exception as e:
            self.logger.error(f"記事の手法バックテストエラー: {e}")
            return {'error': str(e)}
    
    def run_enhanced_backtest(self, predictions: List[float], prices: List[Dict[str, Any]], 
                            confidence_scores: List[float] = None) -> Dict[str, Any]:
        """
        改善された手法によるバックテスト
        記事の手法を超える高度なバックテスト
        """
        try:
            self.logger.info("改善された手法によるバックテストを開始")
            
            # 初期設定
            initial_capital = self.config.get('initial_capital', 100000)
            current_capital = initial_capital
            self.equity_curve = [initial_capital]
            
            # 取引履歴の初期化
            self.trades = []
            
            # 各予測に対して取引判定
            for i, (prediction, price_data) in enumerate(zip(predictions, prices)):
                # 信頼度ベースの判定
                confidence = confidence_scores[i] if confidence_scores else 0.7
                
                if confidence >= self.confidence_threshold:
                    if prediction >= self.article_threshold:
                        # 買い注文（改善版）
                        trade_result = self._execute_enhanced_buy_trade(price_data, prediction, confidence, current_capital)
                    else:
                        # 空売り注文（改善版）
                        trade_result = self._execute_enhanced_sell_trade(price_data, prediction, confidence, current_capital)
                    
                    if trade_result['executed']:
                        self.trades.append(trade_result)
                        current_capital = trade_result['capital_after']
                        self.equity_curve.append(current_capital)
            
            # パフォーマンス指標の計算
            performance = self._calculate_performance_metrics(initial_capital, current_capital)
            
            return {
                'method': 'enhanced_method',
                'initial_capital': initial_capital,
                'final_capital': current_capital,
                'total_return': performance['total_return'],
                'total_trades': len(self.trades),
                'win_rate': performance['win_rate'],
                'max_drawdown': performance['max_drawdown'],
                'sharpe_ratio': performance['sharpe_ratio'],
                'avg_confidence': np.mean(confidence_scores) if confidence_scores else 0,
                'trades': self.trades,
                'equity_curve': self.equity_curve
            }
            
        except Exception as e:
            self.logger.error(f"改善された手法バックテストエラー: {e}")
            return {'error': str(e)}
    
    def _execute_buy_trade(self, price_data: Dict[str, Any], prediction: float, current_capital: float) -> Dict[str, Any]:
        """記事の手法による買い取引の実行"""
        try:
            # 記事の手法: 翌営業日の安値で約定
            entry_price = price_data['low']
            exit_price = price_data['close']
            
            # 取引コストの計算
            commission = self.article_position_size * entry_price * self.commission_rate
            slippage = self.article_position_size * entry_price * self.slippage_rate
            
            # 損益の計算
            pnl = (exit_price - entry_price) * self.article_position_size
            net_pnl = pnl - commission - slippage
            
            # 資本の更新
            new_capital = current_capital + net_pnl
            
            return {
                'executed': True,
                'direction': 'BUY',
                'entry_price': entry_price,
                'exit_price': exit_price,
                'position_size': self.article_position_size,
                'pnl': pnl,
                'net_pnl': net_pnl,
                'commission': commission,
                'slippage': slippage,
                'capital_after': new_capital,
                'prediction': prediction,
                'method': 'article'
            }
            
        except Exception as e:
            self.logger.error(f"買い取引実行エラー: {e}")
            return {'executed': False, 'error': str(e)}
    
    def _execute_sell_trade(self, price_data: Dict[str, Any], prediction: float, current_capital: float) -> Dict[str, Any]:
        """記事の手法による空売り取引の実行"""
        try:
            # 記事の手法: 翌営業日の高値で約定
            entry_price = price_data['high']
            exit_price = price_data['close']
            
            # 取引コストの計算
            commission = self.article_position_size * entry_price * self.commission_rate
            slippage = self.article_position_size * entry_price * self.slippage_rate
            
            # 損益の計算
            pnl = (entry_price - exit_price) * self.article_position_size
            net_pnl = pnl - commission - slippage
            
            # 資本の更新
            new_capital = current_capital + net_pnl
            
            return {
                'executed': True,
                'direction': 'SELL',
                'entry_price': entry_price,
                'exit_price': exit_price,
                'position_size': self.article_position_size,
                'pnl': pnl,
                'net_pnl': net_pnl,
                'commission': commission,
                'slippage': slippage,
                'capital_after': new_capital,
                'prediction': prediction,
                'method': 'article'
            }
            
        except Exception as e:
            self.logger.error(f"空売り取引実行エラー: {e}")
            return {'executed': False, 'error': str(e)}
    
    def _execute_enhanced_buy_trade(self, price_data: Dict[str, Any], prediction: float, 
                                   confidence: float, current_capital: float) -> Dict[str, Any]:
        """改善された手法による買い取引の実行"""
        try:
            # 改善された手法: 信頼度に基づくポジションサイズ
            if self.enhanced_position_sizing:
                position_size = self._calculate_enhanced_position_size(confidence, current_capital, price_data['close'])
            else:
                position_size = self.article_position_size
            
            # 約定価格の計算（改善版）
            entry_price = self._calculate_enhanced_entry_price(price_data, 'BUY')
            exit_price = price_data['close']
            
            # 取引コストの計算
            commission = position_size * entry_price * self.commission_rate
            slippage = position_size * entry_price * self.slippage_rate
            
            # 損益の計算
            pnl = (exit_price - entry_price) * position_size
            net_pnl = pnl - commission - slippage
            
            # 資本の更新
            new_capital = current_capital + net_pnl
            
            return {
                'executed': True,
                'direction': 'BUY',
                'entry_price': entry_price,
                'exit_price': exit_price,
                'position_size': position_size,
                'pnl': pnl,
                'net_pnl': net_pnl,
                'commission': commission,
                'slippage': slippage,
                'capital_after': new_capital,
                'prediction': prediction,
                'confidence': confidence,
                'method': 'enhanced'
            }
            
        except Exception as e:
            self.logger.error(f"改善された買い取引実行エラー: {e}")
            return {'executed': False, 'error': str(e)}
    
    def _execute_enhanced_sell_trade(self, price_data: Dict[str, Any], prediction: float, 
                                    confidence: float, current_capital: float) -> Dict[str, Any]:
        """改善された手法による空売り取引の実行"""
        try:
            # 改善された手法: 信頼度に基づくポジションサイズ
            if self.enhanced_position_sizing:
                position_size = self._calculate_enhanced_position_size(confidence, current_capital, price_data['close'])
            else:
                position_size = self.article_position_size
            
            # 約定価格の計算（改善版）
            entry_price = self._calculate_enhanced_entry_price(price_data, 'SELL')
            exit_price = price_data['close']
            
            # 取引コストの計算
            commission = position_size * entry_price * self.commission_rate
            slippage = position_size * entry_price * self.slippage_rate
            
            # 損益の計算
            pnl = (entry_price - exit_price) * position_size
            net_pnl = pnl - commission - slippage
            
            # 資本の更新
            new_capital = current_capital + net_pnl
            
            return {
                'executed': True,
                'direction': 'SELL',
                'entry_price': entry_price,
                'exit_price': exit_price,
                'position_size': position_size,
                'pnl': pnl,
                'net_pnl': net_pnl,
                'commission': commission,
                'slippage': slippage,
                'capital_after': new_capital,
                'prediction': prediction,
                'confidence': confidence,
                'method': 'enhanced'
            }
            
        except Exception as e:
            self.logger.error(f"改善された空売り取引実行エラー: {e}")
            return {'executed': False, 'error': str(e)}
    
    def _calculate_enhanced_position_size(self, confidence: float, capital: float, price: float) -> float:
        """改善されたポジションサイズの計算"""
        try:
            # 信頼度に基づく基本ポジションサイズ
            base_size = confidence * 100  # 最大100株
            
            # 資本制限
            max_position_value = capital * 0.2  # 資本の20%まで
            max_size = max_position_value / price
            
            position_size = min(base_size, max_size)
            
            return max(0, position_size)
            
        except Exception as e:
            self.logger.error(f"ポジションサイズ計算エラー: {e}")
            return self.article_position_size
    
    def _calculate_enhanced_entry_price(self, price_data: Dict[str, Any], direction: str) -> float:
        """改善された約定価格の計算"""
        try:
            if direction == 'BUY':
                # 買い: 安値と終値の加重平均
                low_price = price_data['low']
                close_price = price_data['close']
                entry_price = (low_price * 0.7 + close_price * 0.3)
            else:  # SELL
                # 空売り: 高値と終値の加重平均
                high_price = price_data['high']
                close_price = price_data['close']
                entry_price = (high_price * 0.7 + close_price * 0.3)
            
            return entry_price
            
        except Exception as e:
            self.logger.error(f"約定価格計算エラー: {e}")
            return price_data.get('close', 0)
    
    def _calculate_performance_metrics(self, initial_capital: float, final_capital: float) -> Dict[str, Any]:
        """パフォーマンス指標の計算"""
        try:
            # 基本指標
            total_return = (final_capital - initial_capital) / initial_capital
            
            # 勝率の計算
            winning_trades = [t for t in self.trades if t.get('net_pnl', 0) > 0]
            win_rate = len(winning_trades) / len(self.trades) if self.trades else 0
            
            # 最大ドローダウンの計算
            max_drawdown = self._calculate_max_drawdown()
            
            # シャープレシオの計算
            sharpe_ratio = self._calculate_sharpe_ratio()
            
            return {
                'total_return': total_return,
                'win_rate': win_rate,
                'max_drawdown': max_drawdown,
                'sharpe_ratio': sharpe_ratio,
                'total_trades': len(self.trades),
                'winning_trades': len(winning_trades),
                'losing_trades': len(self.trades) - len(winning_trades)
            }
            
        except Exception as e:
            self.logger.error(f"パフォーマンス指標計算エラー: {e}")
            return {
                'total_return': 0,
                'win_rate': 0,
                'max_drawdown': 0,
                'sharpe_ratio': 0
            }
    
    def _calculate_max_drawdown(self) -> float:
        """最大ドローダウンの計算"""
        try:
            if not self.equity_curve:
                return 0.0
            
            equity_array = np.array(self.equity_curve)
            peak_prices = np.maximum.accumulate(equity_array)
            drawdowns = (equity_array - peak_prices) / peak_prices
            
            return abs(np.min(drawdowns))
            
        except Exception as e:
            self.logger.error(f"最大ドローダウン計算エラー: {e}")
            return 0.0
    
    def _calculate_sharpe_ratio(self) -> float:
        """シャープレシオの計算"""
        try:
            if len(self.equity_curve) < 2:
                return 0.0
            
            # リターンの計算
            returns = np.diff(self.equity_curve) / self.equity_curve[:-1]
            
            if len(returns) == 0 or np.std(returns) == 0:
                return 0.0
            
            # シャープレシオの計算
            sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252)  # 年率化
            
            return sharpe_ratio
            
        except Exception as e:
            self.logger.error(f"シャープレシオ計算エラー: {e}")
            return 0.0
    
    def compare_methods(self, predictions: List[float], prices: List[Dict[str, Any]], 
                       confidence_scores: List[float] = None) -> Dict[str, Any]:
        """記事の手法と改善された手法の比較"""
        try:
            # 記事の手法によるバックテスト
            article_result = self.run_article_method_backtest(predictions, prices)
            
            # 改善された手法によるバックテスト
            enhanced_result = self.run_enhanced_backtest(predictions, prices, confidence_scores)
            
            # 比較結果
            comparison = {
                'article_method': article_result,
                'enhanced_method': enhanced_result,
                'improvement': {
                    'return_improvement': enhanced_result.get('total_return', 0) - article_result.get('total_return', 0),
                    'win_rate_improvement': enhanced_result.get('win_rate', 0) - article_result.get('win_rate', 0),
                    'max_drawdown_improvement': article_result.get('max_drawdown', 0) - enhanced_result.get('max_drawdown', 0),
                    'sharpe_ratio_improvement': enhanced_result.get('sharpe_ratio', 0) - article_result.get('sharpe_ratio', 0)
                }
            }
            
            return comparison
            
        except Exception as e:
            self.logger.error(f"手法比較エラー: {e}")
            return {'error': str(e)}
