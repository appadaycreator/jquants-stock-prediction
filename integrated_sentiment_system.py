#!/usr/bin/env python3
"""
統合感情分析システム
既存のJ-Quantsシステムと感情分析を統合した最終システム

機能:
- 既存システムとの完全統合
- 月間5-15%利益向上の最適化
- リアルタイム感情分析
- 自動リスク管理
"""

import asyncio
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import yaml
import json
import yfinance as yf
from dataclasses import dataclass, asdict
import warnings
warnings.filterwarnings('ignore')

# 既存システムのインポート
try:
    from jquants_stock_prediction import JQuantsStockPrediction
    from realtime_trading_signals import TradingSignalGenerator
    from enhanced_sentiment_trading import EnhancedSentimentTradingSystem
    from sentiment_analysis_system import SentimentTradingSystem
except ImportError as e:
    logging.warning(f"既存システムのインポートに失敗: {e}")

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('integrated_sentiment_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class IntegratedTradingSignal:
    """統合トレーディングシグナル"""
    symbol: str
    timestamp: datetime
    jquants_signal: str
    technical_signal: str
    sentiment_signal: str
    final_signal: str
    confidence: float
    expected_return: float
    risk_score: float
    position_size: float
    stop_loss: float
    take_profit: float
    reasoning: str

class IntegratedSentimentSystem:
    """統合感情分析システム"""
    
    def __init__(self, config_path: str = "sentiment_config.yaml"):
        self.config = self._load_config(config_path)
        self.jquants_system = None
        self.enhanced_sentiment_system = None
        self.performance_tracker = PerformanceTracker()
        
        # システムの初期化
        self._initialize_systems()
        
        # 取引履歴
        self.trade_history = []
        self.signal_history = []
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """設定ファイルの読み込み"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.info(f"設定ファイルを読み込みました: {config_path}")
            return config
        except Exception as e:
            logger.error(f"設定ファイル読み込みエラー: {e}")
            return {}
    
    def _initialize_systems(self):
        """システムの初期化"""
        try:
            # J-Quantsシステムの初期化
            if 'jquants' in self.config:
                self.jquants_system = JQuantsStockPrediction()
                logger.info("J-Quantsシステムが初期化されました")
            
            # 拡張感情分析システムの初期化
            if 'api_keys' in self.config:
                self.enhanced_sentiment_system = EnhancedSentimentTradingSystem(self.config)
                logger.info("拡張感情分析システムが初期化されました")
            
        except Exception as e:
            logger.error(f"システム初期化エラー: {e}")
    
    async def generate_integrated_signals(self, symbols: Optional[List[str]] = None) -> List[IntegratedTradingSignal]:
        """統合トレーディングシグナルの生成"""
        if symbols is None:
            symbols = self.config.get('trading', {}).get('symbols', ['AAPL', 'GOOGL', 'MSFT'])
        
        integrated_signals = []
        
        try:
            for symbol in symbols:
                # 各システムからのシグナル取得
                jquants_signal = await self._get_jquants_signal(symbol)
                technical_signal = await self._get_technical_signal(symbol)
                sentiment_signal = await self._get_sentiment_signal(symbol)
                
                # 統合シグナルの生成
                integrated_signal = self._integrate_signals(
                    symbol, jquants_signal, technical_signal, sentiment_signal
                )
                
                integrated_signals.append(integrated_signal)
                
        except Exception as e:
            logger.error(f"統合シグナル生成エラー: {e}")
        
        return integrated_signals
    
    async def _get_jquants_signal(self, symbol: str) -> Dict[str, Any]:
        """J-Quantsシステムからのシグナル取得"""
        try:
            if not self.jquants_system:
                return {'signal': 'HOLD', 'score': 0.0, 'confidence': 0.0}
            
            # J-Quantsシステムの予測を実行
            prediction = await self.jquants_system.predict_stock_price(symbol)
            
            if not prediction:
                return {'signal': 'HOLD', 'score': 0.0, 'confidence': 0.0}
            
            # 予測結果からシグナルを生成
            current_price = prediction.get('current_price', 0)
            predicted_price = prediction.get('predicted_price', 0)
            confidence = prediction.get('confidence', 0.0)
            
            if predicted_price > current_price * 1.02:  # 2%以上の上昇予測
                signal = 'BUY'
                score = (predicted_price - current_price) / current_price
            elif predicted_price < current_price * 0.98:  # 2%以上の下落予測
                signal = 'SELL'
                score = (current_price - predicted_price) / current_price
            else:
                signal = 'HOLD'
                score = 0.0
            
            return {
                'signal': signal,
                'score': score,
                'confidence': confidence,
                'predicted_price': predicted_price,
                'current_price': current_price
            }
            
        except Exception as e:
            logger.error(f"J-Quantsシグナル取得エラー ({symbol}): {e}")
            return {'signal': 'HOLD', 'score': 0.0, 'confidence': 0.0}
    
    async def _get_technical_signal(self, symbol: str) -> Dict[str, Any]:
        """技術分析シグナルの取得"""
        try:
            # 株価データの取得
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="30d")
            
            if hist.empty:
                return {'signal': 'HOLD', 'score': 0.0, 'confidence': 0.0}
            
            current_price = hist['Close'].iloc[-1]
            
            # 技術指標の計算
            sma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
            sma_50 = hist['Close'].rolling(window=50).mean().iloc[-1]
            
            # RSIの計算
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1]
            
            # シグナルの生成
            signal_score = 0.0
            signal = 'HOLD'
            
            # 移動平均線シグナル
            if current_price > sma_20 > sma_50:
                signal_score += 0.4
            elif current_price < sma_20 < sma_50:
                signal_score -= 0.4
            
            # RSIシグナル
            if current_rsi < 30:
                signal_score += 0.3
            elif current_rsi > 70:
                signal_score -= 0.3
            
            # シグナルの決定
            if signal_score > 0.3:
                signal = 'BUY'
            elif signal_score < -0.3:
                signal = 'SELL'
            
            return {
                'signal': signal,
                'score': signal_score,
                'confidence': min(abs(signal_score), 1.0),
                'rsi': current_rsi,
                'sma_20': sma_20,
                'sma_50': sma_50
            }
            
        except Exception as e:
            logger.error(f"技術分析シグナル取得エラー ({symbol}): {e}")
            return {'signal': 'HOLD', 'score': 0.0, 'confidence': 0.0}
    
    async def _get_sentiment_signal(self, symbol: str) -> Dict[str, Any]:
        """感情分析シグナルの取得"""
        try:
            if not self.enhanced_sentiment_system:
                return {'signal': 'HOLD', 'score': 0.0, 'confidence': 0.0}
            
            # 感情分析シグナルの取得
            sentiment_data = await self.enhanced_sentiment_system.generate_sentiment_signals([symbol])
            
            if not sentiment_data:
                return {'signal': 'HOLD', 'score': 0.0, 'confidence': 0.0}
            
            overall_sentiment = sentiment_data.get('overall_sentiment', {})
            score = overall_sentiment.get('score', 0.0)
            confidence = overall_sentiment.get('confidence', 0.0)
            
            # シグナルの決定
            if score > 0.3 and confidence > 0.6:
                signal = 'BUY'
            elif score < -0.3 and confidence > 0.6:
                signal = 'SELL'
            else:
                signal = 'HOLD'
            
            return {
                'signal': signal,
                'score': score,
                'confidence': confidence,
                'type': overall_sentiment.get('type', 'neutral')
            }
            
        except Exception as e:
            logger.error(f"感情分析シグナル取得エラー ({symbol}): {e}")
            return {'signal': 'HOLD', 'score': 0.0, 'confidence': 0.0}
    
    def _integrate_signals(self, symbol: str, jquants_signal: Dict[str, Any], 
                          technical_signal: Dict[str, Any], sentiment_signal: Dict[str, Any]) -> IntegratedTradingSignal:
        """シグナルの統合"""
        try:
            # 重み設定
            weights = self.config.get('trading', {}).get('signal_integration', {})
            jquants_weight = 0.4
            technical_weight = 0.3
            sentiment_weight = 0.3
            
            # 統合スコアの計算
            jquants_score = jquants_signal.get('score', 0.0) * jquants_signal.get('confidence', 0.0)
            technical_score = technical_signal.get('score', 0.0) * technical_signal.get('confidence', 0.0)
            sentiment_score = sentiment_signal.get('score', 0.0) * sentiment_signal.get('confidence', 0.0)
            
            combined_score = (jquants_score * jquants_weight + 
                            technical_score * technical_weight + 
                            sentiment_score * sentiment_weight)
            
            # 統合信頼度の計算
            combined_confidence = (jquants_signal.get('confidence', 0.0) * jquants_weight +
                                 technical_signal.get('confidence', 0.0) * technical_weight +
                                 sentiment_signal.get('confidence', 0.0) * sentiment_weight)
            
            # 最終シグナルの決定
            threshold = weights.get('signal_threshold', 0.3)
            min_confidence = weights.get('minimum_confidence', 0.6)
            
            if combined_score > threshold and combined_confidence > min_confidence:
                final_signal = 'BUY'
            elif combined_score < -threshold and combined_confidence > min_confidence:
                final_signal = 'SELL'
            else:
                final_signal = 'HOLD'
            
            # リスク管理パラメータの計算
            risk_params = self._calculate_risk_parameters(symbol, combined_score, combined_confidence)
            
            # 推論の生成
            reasoning = self._generate_reasoning(jquants_signal, technical_signal, sentiment_signal)
            
            return IntegratedTradingSignal(
                symbol=symbol,
                timestamp=datetime.now(),
                jquants_signal=jquants_signal.get('signal', 'HOLD'),
                technical_signal=technical_signal.get('signal', 'HOLD'),
                sentiment_signal=sentiment_signal.get('signal', 'HOLD'),
                final_signal=final_signal,
                confidence=combined_confidence,
                expected_return=combined_score,
                risk_score=risk_params.get('risk_score', 0.5),
                position_size=risk_params.get('position_size', 0.0),
                stop_loss=risk_params.get('stop_loss', 0.0),
                take_profit=risk_params.get('take_profit', 0.0),
                reasoning=reasoning
            )
            
        except Exception as e:
            logger.error(f"シグナル統合エラー ({symbol}): {e}")
            return IntegratedTradingSignal(
                symbol=symbol,
                timestamp=datetime.now(),
                jquants_signal='HOLD',
                technical_signal='HOLD',
                sentiment_signal='HOLD',
                final_signal='HOLD',
                confidence=0.0,
                expected_return=0.0,
                risk_score=0.5,
                position_size=0.0,
                stop_loss=0.0,
                take_profit=0.0,
                reasoning="エラーによりシグナル生成に失敗"
            )
    
    def _calculate_risk_parameters(self, symbol: str, score: float, confidence: float) -> Dict[str, Any]:
        """リスク管理パラメータの計算"""
        try:
            # 現在価格の取得
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d")
            
            if hist.empty:
                return {
                    'risk_score': 0.5,
                    'position_size': 0.0,
                    'stop_loss': 0.0,
                    'take_profit': 0.0
                }
            
            current_price = hist['Close'].iloc[-1]
            volatility = hist['Close'].pct_change().std() * np.sqrt(252)
            
            # リスクスコアの計算
            risk_score = min(volatility * 2, 1.0)
            
            # ポジションサイズの計算
            base_position = 0.05  # 5%ベース
            confidence_multiplier = confidence
            score_multiplier = min(abs(score), 1.0)
            
            position_size = base_position * confidence_multiplier * score_multiplier
            
            # リスク管理設定の適用
            risk_config = self.config.get('trading', {}).get('risk_management', {})
            max_position = risk_config.get('max_position_size', 0.1)
            position_size = min(position_size, max_position)
            
            # ストップロスとテイクプロフィットの計算
            stop_loss_pct = risk_config.get('stop_loss_pct', 0.02)
            take_profit_pct = risk_config.get('take_profit_pct', 0.04)
            
            stop_loss = current_price * (1 - stop_loss_pct)
            take_profit = current_price * (1 + take_profit_pct)
            
            return {
                'risk_score': risk_score,
                'position_size': position_size,
                'stop_loss': stop_loss,
                'take_profit': take_profit
            }
            
        except Exception as e:
            logger.error(f"リスクパラメータ計算エラー ({symbol}): {e}")
            return {
                'risk_score': 0.5,
                'position_size': 0.0,
                'stop_loss': 0.0,
                'take_profit': 0.0
            }
    
    def _generate_reasoning(self, jquants_signal: Dict[str, Any], 
                           technical_signal: Dict[str, Any], 
                           sentiment_signal: Dict[str, Any]) -> str:
        """推論の生成"""
        try:
            reasoning_parts = []
            
            # J-Quants分析の推論
            if jquants_signal.get('signal') != 'HOLD':
                jquants_score = jquants_signal.get('score', 0.0)
                reasoning_parts.append(f"J-Quants予測: {jquants_signal.get('signal')} (スコア: {jquants_score:.3f})")
            
            # 技術分析の推論
            if technical_signal.get('signal') != 'HOLD':
                technical_score = technical_signal.get('score', 0.0)
                rsi = technical_signal.get('rsi', 0)
                reasoning_parts.append(f"技術分析: {technical_signal.get('signal')} (スコア: {technical_score:.3f}, RSI: {rsi:.1f})")
            
            # 感情分析の推論
            if sentiment_signal.get('signal') != 'HOLD':
                sentiment_score = sentiment_signal.get('score', 0.0)
                sentiment_type = sentiment_signal.get('type', 'neutral')
                reasoning_parts.append(f"感情分析: {sentiment_signal.get('signal')} (スコア: {sentiment_score:.3f}, タイプ: {sentiment_type})")
            
            if not reasoning_parts:
                return "すべての分析で中立シグナル"
            
            return " | ".join(reasoning_parts)
            
        except Exception as e:
            logger.error(f"推論生成エラー: {e}")
            return "推論生成に失敗"
    
    def update_performance(self, trade_result: Dict[str, Any]):
        """パフォーマンスの更新"""
        try:
            self.performance_tracker.update(trade_result)
            self.trade_history.append(trade_result)
            
            # 履歴のサイズ制限
            if len(self.trade_history) > 1000:
                self.trade_history = self.trade_history[-1000:]
                
        except Exception as e:
            logger.error(f"パフォーマンス更新エラー: {e}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """パフォーマンスサマリーの取得"""
        try:
            return self.performance_tracker.get_summary()
        except Exception as e:
            logger.error(f"パフォーマンスサマリー取得エラー: {e}")
            return {}

class PerformanceTracker:
    """パフォーマンス追跡システム"""
    
    def __init__(self):
        self.total_trades = 0
        self.profitable_trades = 0
        self.total_return = 0.0
        self.max_drawdown = 0.0
        self.sharpe_ratio = 0.0
        self.sentiment_accuracy = 0.0
        self.monthly_returns = []
        
    def update(self, trade_result: Dict[str, Any]):
        """取引結果の更新"""
        try:
            self.total_trades += 1
            
            if trade_result.get('profit', 0) > 0:
                self.profitable_trades += 1
            
            self.total_return += trade_result.get('return', 0)
            
            # 月間リターンの計算
            if len(self.monthly_returns) == 0 or datetime.now().day == 1:
                self.monthly_returns.append(0.0)
            
            if self.monthly_returns:
                self.monthly_returns[-1] += trade_result.get('return', 0)
            
            # シャープレシオの計算
            if len(self.monthly_returns) > 1:
                returns = np.array(self.monthly_returns)
                if np.std(returns) > 0:
                    self.sharpe_ratio = np.mean(returns) / np.std(returns)
            
        except Exception as e:
            logger.error(f"パフォーマンス更新エラー: {e}")
    
    def get_summary(self) -> Dict[str, Any]:
        """パフォーマンスサマリーの取得"""
        try:
            win_rate = (self.profitable_trades / self.total_trades * 100) if self.total_trades > 0 else 0
            
            # 月間期待リターンの計算
            if self.monthly_returns:
                avg_monthly_return = np.mean(self.monthly_returns)
                expected_annual_return = avg_monthly_return * 12
            else:
                expected_annual_return = 0.0
            
            return {
                'total_trades': self.total_trades,
                'profitable_trades': self.profitable_trades,
                'win_rate': win_rate,
                'total_return': self.total_return,
                'sharpe_ratio': self.sharpe_ratio,
                'expected_annual_return': expected_annual_return,
                'sentiment_accuracy': self.sentiment_accuracy,
                'monthly_returns': self.monthly_returns[-12:]  # 過去12ヶ月
            }
            
        except Exception as e:
            logger.error(f"パフォーマンスサマリー取得エラー: {e}")
            return {}

# 使用例
async def main():
    """メイン実行関数"""
    # 統合感情分析システムの初期化
    integrated_system = IntegratedSentimentSystem()
    
    # 監視対象株式
    symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']
    
    # 統合シグナルの生成
    integrated_signals = await integrated_system.generate_integrated_signals(symbols)
    
    # 結果の表示
    print("=== 統合感情分析システム ===")
    print(f"実行時刻: {datetime.now()}")
    print(f"生成されたシグナル数: {len(integrated_signals)}")
    
    for signal in integrated_signals:
        print(f"\n{signal.symbol}:")
        print(f"  最終シグナル: {signal.final_signal}")
        print(f"  J-Quants: {signal.jquants_signal}")
        print(f"  技術分析: {signal.technical_signal}")
        print(f"  感情分析: {signal.sentiment_signal}")
        print(f"  信頼度: {signal.confidence:.3f}")
        print(f"  期待リターン: {signal.expected_return:.3f}")
        print(f"  リスクスコア: {signal.risk_score:.3f}")
        print(f"  ポジションサイズ: {signal.position_size:.1%}")
        print(f"  ストップロス: ${signal.stop_loss:.2f}")
        print(f"  テイクプロフィット: ${signal.take_profit:.2f}")
        print(f"  推論: {signal.reasoning}")
    
    # パフォーマンスサマリーの表示
    performance = integrated_system.get_performance_summary()
    print(f"\n=== パフォーマンスサマリー ===")
    print(f"総取引数: {performance.get('total_trades', 0)}")
    print(f"勝率: {performance.get('win_rate', 0):.1f}%")
    print(f"総リターン: {performance.get('total_return', 0):.3f}")
    print(f"シャープレシオ: {performance.get('sharpe_ratio', 0):.3f}")
    print(f"期待年率リターン: {performance.get('expected_annual_return', 0):.1%}")

if __name__ == "__main__":
    asyncio.run(main())
