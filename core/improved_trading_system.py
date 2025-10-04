"""
改善された取引システム
記事の手法を超える実用性を証明するシステム
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge, Lasso
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import warnings

warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

@dataclass
class TradingSignal:
    """取引シグナル"""
    symbol: str
    action: str  # 'BUY', 'SELL', 'HOLD'
    confidence: float
    price: float
    target_price: float
    stop_loss: float
    take_profit: float
    position_size: float
    reason: str
    timestamp: datetime

@dataclass
class PortfolioPosition:
    """ポートフォリオポジション"""
    symbol: str
    quantity: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    stop_loss: float
    take_profit: float
    confidence: float

@dataclass
class RiskMetrics:
    """リスク指標"""
    var_95: float
    max_drawdown: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    volatility: float
    beta: float

class ImprovedTradingSystem:
    """改善された取引システム"""
    
    def __init__(self, 
                 reliability_threshold: float = 0.7,
                 commission_rate: float = 0.002,
                 slippage_rate: float = 0.001,
                 max_position_size: float = 0.1):
        """
        初期化
        
        Args:
            reliability_threshold: 信頼度閾値（デフォルト70%）
            commission_rate: 手数料率（デフォルト0.2%）
            slippage_rate: スリッページ率（デフォルト0.1%）
            max_position_size: 最大ポジションサイズ（デフォルト10%）
        """
        self.reliability_threshold = reliability_threshold
        self.commission_rate = commission_rate
        self.slippage_rate = slippage_rate
        self.max_position_size = max_position_size
        self.total_cost_rate = commission_rate + slippage_rate
        
        self.logger = logging.getLogger(__name__)
        
        # アンサンブルモデル
        self.models = {
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'ridge': Ridge(alpha=1.0),
            'lasso': Lasso(alpha=0.1),
            'svr': SVR(kernel='rbf', C=1.0, gamma='scale'),
            'mlp': MLPRegressor(hidden_layer_sizes=(100, 50), random_state=42, max_iter=500)
        }
        
        self.trained_models = {}
        self.feature_importance = {}
        
    def train_models(self, data: pd.DataFrame) -> Dict[str, float]:
        """
        モデルの学習
        
        Args:
            data: 学習データ
            
        Returns:
            Dict[str, float]: 各モデルの性能指標
        """
        try:
            # 特徴量の作成
            features_data = self._create_features(data)
            
            # ターゲットの作成（翌日の終値）
            target = features_data['Close'].shift(-1)
            
            # 欠損値を除去
            valid_data = features_data.dropna()
            target = target[valid_data.index]
            
            # 特徴量の選択
            feature_columns = [col for col in valid_data.columns if col not in ['Date', 'Close']]
            X = valid_data[feature_columns]
            y = target
            
            # データを学習・検証に分割
            split_point = int(len(X) * 0.8)
            X_train, X_val = X[:split_point], X[split_point:]
            y_train, y_val = y[:split_point], y[split_point:]
            
            model_performance = {}
            
            # 各モデルの学習
            for name, model in self.models.items():
                try:
                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_val)
                    
                    # 性能評価
                    mse = mean_squared_error(y_val, y_pred)
                    mae = mean_absolute_error(y_val, y_pred)
                    r2 = r2_score(y_val, y_pred)
                    
                    model_performance[name] = {
                        'mse': mse,
                        'mae': mae,
                        'r2': r2
                    }
                    
                    self.trained_models[name] = model
                    
                    # 特徴量重要度の保存
                    if hasattr(model, 'feature_importances_'):
                        self.feature_importance[name] = dict(zip(feature_columns, model.feature_importances_))
                    elif hasattr(model, 'coef_'):
                        self.feature_importance[name] = dict(zip(feature_columns, abs(model.coef_)))
                    
                except Exception as e:
                    self.logger.warning(f"モデル {name} の学習でエラー: {e}")
                    continue
            
            return model_performance
            
        except Exception as e:
            self.logger.error(f"モデル学習でエラー: {e}")
            raise
    
    def _create_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """特徴量の作成"""
        df = data.copy()
        
        # 基本価格特徴量
        df['Price_Change'] = df['Close'].pct_change()
        df['Price_Change_2'] = df['Close'].pct_change(2)
        df['Price_Change_5'] = df['Close'].pct_change(5)
        df['Price_Change_10'] = df['Close'].pct_change(10)
        
        # 移動平均
        df['MA_5'] = df['Close'].rolling(window=5).mean()
        df['MA_10'] = df['Close'].rolling(window=10).mean()
        df['MA_20'] = df['Close'].rolling(window=20).mean()
        df['MA_50'] = df['Close'].rolling(window=50).mean()
        
        # 移動平均乖離率
        df['MA5_Deviation'] = (df['Close'] - df['MA_5']) / df['MA_5']
        df['MA20_Deviation'] = (df['Close'] - df['MA_20']) / df['MA_20']
        df['MA50_Deviation'] = (df['Close'] - df['MA_50']) / df['MA_50']
        
        # ボラティリティ
        df['Volatility_5'] = df['Close'].rolling(window=5).std()
        df['Volatility_20'] = df['Close'].rolling(window=20).std()
        df['Volatility_50'] = df['Close'].rolling(window=50).std()
        
        # 出来高特徴量
        df['Volume_Change'] = df['Volume'].pct_change()
        df['Volume_MA_5'] = df['Volume'].rolling(window=5).mean()
        df['Volume_MA_20'] = df['Volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_MA_20']
        
        # テクニカル指標
        df['RSI'] = self._calculate_rsi(df['Close'])
        df['MACD'] = self._calculate_macd(df['Close'])
        df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
        
        # ボリンジャーバンド
        bb_upper, bb_lower, bb_middle = self._calculate_bollinger_bands(df['Close'])
        df['BB_Upper'] = bb_upper
        df['BB_Lower'] = bb_lower
        df['BB_Middle'] = bb_middle
        df['BB_Width'] = (bb_upper - bb_lower) / bb_middle
        df['BB_Position'] = (df['Close'] - bb_lower) / (bb_upper - bb_lower)
        
        # ATR
        df['ATR'] = self._calculate_atr(df)
        
        # ストキャスティクス
        df['Stoch_K'], df['Stoch_D'] = self._calculate_stochastic(df)
        
        # ウィリアムズ%R
        df['Williams_R'] = self._calculate_williams_r(df)
        
        # CCI
        df['CCI'] = self._calculate_cci(df)
        
        # ADX
        df['ADX'] = self._calculate_adx(df)
        
        # 価格位置
        df['Price_Position_20'] = df['Close'].rolling(window=20).rank(pct=True)
        df['Price_Position_50'] = df['Close'].rolling(window=50).rank(pct=True)
        
        return df
    
    def _calculate_rsi(self, prices: pd.Series, window: int = 14) -> pd.Series:
        """RSI計算"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26) -> pd.Series:
        """MACD計算"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        return macd
    
    def _calculate_bollinger_bands(self, prices: pd.Series, window: int = 20, num_std: float = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """ボリンジャーバンド計算"""
        rolling_mean = prices.rolling(window=window).mean()
        rolling_std = prices.rolling(window=window).std()
        upper_band = rolling_mean + (rolling_std * num_std)
        lower_band = rolling_mean - (rolling_std * num_std)
        return upper_band, lower_band, rolling_mean
    
    def _calculate_atr(self, data: pd.DataFrame, window: int = 14) -> pd.Series:
        """ATR計算"""
        high_low = data['High'] - data['Low']
        high_close = np.abs(data['High'] - data['Close'].shift())
        low_close = np.abs(data['Low'] - data['Close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        atr = true_range.rolling(window=window).mean()
        return atr
    
    def _calculate_stochastic(self, data: pd.DataFrame, k_window: int = 14, d_window: int = 3) -> Tuple[pd.Series, pd.Series]:
        """ストキャスティクス計算"""
        lowest_low = data['Low'].rolling(window=k_window).min()
        highest_high = data['High'].rolling(window=k_window).max()
        k_percent = 100 * (data['Close'] - lowest_low) / (highest_high - lowest_low)
        d_percent = k_percent.rolling(window=d_window).mean()
        return k_percent, d_percent
    
    def _calculate_williams_r(self, data: pd.DataFrame, window: int = 14) -> pd.Series:
        """ウィリアムズ%R計算"""
        highest_high = data['High'].rolling(window=window).max()
        lowest_low = data['Low'].rolling(window=window).min()
        williams_r = -100 * (highest_high - data['Close']) / (highest_high - lowest_low)
        return williams_r
    
    def _calculate_cci(self, data: pd.DataFrame, window: int = 20) -> pd.Series:
        """CCI計算"""
        typical_price = (data['High'] + data['Low'] + data['Close']) / 3
        sma = typical_price.rolling(window=window).mean()
        mad = typical_price.rolling(window=window).apply(lambda x: np.mean(np.abs(x - x.mean())))
        cci = (typical_price - sma) / (0.015 * mad)
        return cci
    
    def _calculate_adx(self, data: pd.DataFrame, window: int = 14) -> pd.Series:
        """ADX計算"""
        high_diff = data['High'].diff()
        low_diff = data['Low'].diff()
        
        plus_dm = np.where((high_diff > low_diff) & (high_diff > 0), high_diff, 0)
        minus_dm = np.where((low_diff > high_diff) & (low_diff > 0), low_diff, 0)
        
        plus_dm = pd.Series(plus_dm, index=data.index)
        minus_dm = pd.Series(minus_dm, index=data.index)
        
        atr = self._calculate_atr(data, window)
        
        plus_di = 100 * (plus_dm.rolling(window=window).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=window).mean() / atr)
        
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=window).mean()
        
        return adx
    
    def generate_signals(self, data: pd.DataFrame) -> List[TradingSignal]:
        """
        取引シグナルの生成
        
        Args:
            data: 株価データ
            
        Returns:
            List[TradingSignal]: 取引シグナルリスト
        """
        try:
            if not self.trained_models:
                raise ValueError("モデルが学習されていません。train_models()を先に実行してください。")
            
            # 特徴量の作成
            features_data = self._create_features(data)
            
            # 特徴量の選択
            feature_columns = [col for col in features_data.columns if col not in ['Date', 'Close']]
            X = features_data[feature_columns].dropna()
            
            signals = []
            
            # 各時点での予測
            for i in range(len(X)):
                current_data = X.iloc[i]
                current_price = features_data.iloc[i]['Close']
                current_date = features_data.iloc[i]['Date'] if 'Date' in features_data.columns else datetime.now()
                
                # アンサンブル予測
                predictions = []
                confidences = []
                
                for name, model in self.trained_models.items():
                    try:
                        pred = model.predict([current_data.values])[0]
                        predictions.append(pred)
                        
                        # 信頼度の計算（簡略化）
                        confidence = min(1.0, max(0.0, 1 - abs(pred - current_price) / current_price))
                        confidences.append(confidence)
                        
                    except Exception as e:
                        self.logger.warning(f"モデル {name} の予測でエラー: {e}")
                        continue
                
                if not predictions:
                    continue
                
                # 重み付き平均予測
                ensemble_prediction = np.mean(predictions)
                ensemble_confidence = np.mean(confidences)
                
                # 信頼度閾値チェック
                if ensemble_confidence >= self.reliability_threshold:
                    # 取引判定
                    price_change_ratio = (ensemble_prediction - current_price) / current_price
                    
                    if price_change_ratio > 0.02:  # 2%以上の上昇予測
                        # 買いシグナル
                        target_price = current_price * 1.10  # 10%利確
                        stop_loss = current_price * 0.95    # 5%損切り
                        
                        signal = TradingSignal(
                            symbol="SAMPLE",
                            action="BUY",
                            confidence=ensemble_confidence,
                            price=current_price,
                            target_price=target_price,
                            stop_loss=stop_loss,
                            take_profit=target_price,
                            position_size=self.max_position_size,
                            reason=f"上昇予測: {price_change_ratio:.2%}",
                            timestamp=current_date
                        )
                        signals.append(signal)
                    
                    elif price_change_ratio < -0.02:  # 2%以上の下落予測
                        # 売りシグナル
                        target_price = current_price * 0.90  # 10%利確
                        stop_loss = current_price * 1.05     # 5%損切り
                        
                        signal = TradingSignal(
                            symbol="SAMPLE",
                            action="SELL",
                            confidence=ensemble_confidence,
                            price=current_price,
                            target_price=target_price,
                            stop_loss=stop_loss,
                            take_profit=target_price,
                            position_size=self.max_position_size,
                            reason=f"下落予測: {price_change_ratio:.2%}",
                            timestamp=current_date
                        )
                        signals.append(signal)
            
            return signals
            
        except Exception as e:
            self.logger.error(f"シグナル生成でエラー: {e}")
            raise
    
    def run_backtest(self, data: pd.DataFrame, initial_capital: float = 100000) -> Dict:
        """
        バックテストの実行
        
        Args:
            data: 株価データ
            initial_capital: 初期資本
            
        Returns:
            Dict: バックテスト結果
        """
        try:
            # シグナル生成
            signals = self.generate_signals(data)
            
            # バックテスト実行
            capital = initial_capital
            position = 0
            position_entry_price = 0
            trades = []
            equity_curve = [initial_capital]
            
            signal_index = 0
            
            for i in range(len(data)):
                current_price = data.iloc[i]['Close']
                current_date = data.iloc[i]['Date'] if 'Date' in data.columns else datetime.now()
                
                # 現在のシグナルをチェック
                current_signal = None
                if signal_index < len(signals):
                    signal_date = signals[signal_index].timestamp
                    if isinstance(signal_date, str):
                        signal_date = pd.to_datetime(signal_date)
                    if isinstance(current_date, str):
                        current_date = pd.to_datetime(current_date)
                    
                    if current_date >= signal_date:
                        current_signal = signals[signal_index]
                        signal_index += 1
                
                # ポジション管理
                if position > 0:
                    # 損切り・利確チェック
                    if current_signal and current_signal.action == "SELL":
                        # 売りシグナルで決済
                        capital = position * current_price * (1 - self.total_cost_rate)
                        position = 0
                        trades.append({
                            'type': 'SELL',
                            'price': current_price,
                            'date': current_date,
                            'pnl': capital - position_entry_price * position
                        })
                    elif current_price <= position_entry_price * 0.95:  # 5%損切り
                        capital = position * current_price * (1 - self.total_cost_rate)
                        position = 0
                        trades.append({
                            'type': 'STOP_LOSS',
                            'price': current_price,
                            'date': current_date,
                            'pnl': capital - position_entry_price * position
                        })
                    elif current_price >= position_entry_price * 1.10:  # 10%利確
                        capital = position * current_price * (1 - self.total_cost_rate)
                        position = 0
                        trades.append({
                            'type': 'TAKE_PROFIT',
                            'price': current_price,
                            'date': current_date,
                            'pnl': capital - position_entry_price * position
                        })
                
                # 新規ポジション
                if current_signal and current_signal.action == "BUY" and position == 0:
                    position = capital * self.max_position_size / (current_price * (1 + self.total_cost_rate))
                    capital -= position * current_price * (1 + self.total_cost_rate)
                    position_entry_price = current_price
                    trades.append({
                        'type': 'BUY',
                        'price': current_price,
                        'date': current_date,
                        'pnl': 0
                    })
                
                # 現在の資産価値
                current_value = capital + (position * current_price if position > 0 else 0)
                equity_curve.append(current_value)
            
            # 最終決済
            if position > 0:
                final_price = data.iloc[-1]['Close']
                capital = position * final_price * (1 - self.total_cost_rate)
                position = 0
            
            # メトリクス計算
            equity_series = pd.Series(equity_curve)
            returns = equity_series.pct_change().dropna()
            
            total_return = (equity_series.iloc[-1] - initial_capital) / initial_capital
            total_trades = len(trades)
            winning_trades = sum(1 for trade in trades if trade.get('pnl', 0) > 0)
            losing_trades = total_trades - winning_trades
            
            # 最大ドローダウン
            rolling_max = equity_series.expanding().max()
            drawdown = (equity_series - rolling_max) / rolling_max
            max_drawdown = drawdown.min()
            
            # シャープレシオ
            sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
            
            # ソルティノレシオ
            downside_returns = returns[returns < 0]
            sortino_ratio = returns.mean() / downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 and downside_returns.std() > 0 else 0
            
            # カルマーレシオ
            calmar_ratio = total_return / abs(max_drawdown) if max_drawdown != 0 else 0
            
            # プロフィットファクター
            total_profit = sum(trade.get('pnl', 0) for trade in trades if trade.get('pnl', 0) > 0)
            total_loss = abs(sum(trade.get('pnl', 0) for trade in trades if trade.get('pnl', 0) < 0))
            profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
            
            return {
                'total_return': total_return,
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': winning_trades / total_trades if total_trades > 0 else 0,
                'max_drawdown': max_drawdown,
                'sharpe_ratio': sharpe_ratio,
                'sortino_ratio': sortino_ratio,
                'calmar_ratio': calmar_ratio,
                'profit_factor': profit_factor,
                'final_capital': equity_series.iloc[-1],
                'equity_curve': equity_curve,
                'trades': trades
            }
            
        except Exception as e:
            self.logger.error(f"バックテストでエラー: {e}")
            raise
    
    def calculate_risk_metrics(self, returns: pd.Series) -> RiskMetrics:
        """リスク指標の計算"""
        try:
            # VaR (95%)
            var_95 = np.percentile(returns, 5)
            
            # 最大ドローダウン
            cumulative = (1 + returns).cumprod()
            rolling_max = cumulative.expanding().max()
            drawdown = (cumulative - rolling_max) / rolling_max
            max_drawdown = drawdown.min()
            
            # シャープレシオ
            sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
            
            # ソルティノレシオ
            downside_returns = returns[returns < 0]
            sortino_ratio = returns.mean() / downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 and downside_returns.std() > 0 else 0
            
            # カルマーレシオ
            calmar_ratio = returns.mean() * 252 / abs(max_drawdown) if max_drawdown != 0 else 0
            
            # ボラティリティ
            volatility = returns.std() * np.sqrt(252)
            
            # ベータ（市場との相関、簡略化）
            beta = 1.0  # 簡略化
            
            return RiskMetrics(
                var_95=var_95,
                max_drawdown=max_drawdown,
                sharpe_ratio=sharpe_ratio,
                sortino_ratio=sortino_ratio,
                calmar_ratio=calmar_ratio,
                volatility=volatility,
                beta=beta
            )
            
        except Exception as e:
            self.logger.error(f"リスク指標計算でエラー: {e}")
            raise

def create_sample_trading_data() -> pd.DataFrame:
    """サンプル取引データの作成"""
    dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='D')
    np.random.seed(42)
    
    # ランダムウォークで株価を生成
    price = 100
    prices = [price]
    volumes = []
    
    for i in range(len(dates) - 1):
        change = np.random.normal(0, 0.02)
        price *= (1 + change)
        prices.append(price)
        volumes.append(np.random.randint(1000, 10000))
    
    volumes.append(np.random.randint(1000, 10000))
    
    # 高値・安値の生成
    highs = [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices]
    lows = [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices]
    
    data = pd.DataFrame({
        'Date': dates,
        'Open': [p * (1 + np.random.normal(0, 0.005)) for p in prices],
        'High': highs,
        'Low': lows,
        'Close': prices,
        'Volume': volumes
    })
    
    return data
