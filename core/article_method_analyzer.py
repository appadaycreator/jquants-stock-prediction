"""
記事の手法を分析し、74%精度でも損失が発生する原因を特定するモジュール
記事: https://note.com/3day_programmer/n/nb78a10f653af
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
import logging
from sklearn.linear_model import LinearRegression
import warnings

warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)


@dataclass
class ArticleMethodResult:
    """記事の手法の結果"""

    accuracy: float
    total_return: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    max_drawdown: float
    sharpe_ratio: float
    profit_factor: float
    analysis_period: str
    method_name: str


@dataclass
class ImprovedMethodResult:
    """改善された手法の結果"""

    accuracy: float
    total_return: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    max_drawdown: float
    sharpe_ratio: float
    profit_factor: float
    analysis_period: str
    method_name: str
    reliability_threshold: float
    dynamic_stop_loss: bool
    position_sizing: str


@dataclass
class ComparisonResult:
    """比較結果"""

    article_method: ArticleMethodResult
    improved_method: ImprovedMethodResult
    improvement_metrics: Dict[str, float]
    recommendation: str


class ArticleMethodAnalyzer:
    """記事の手法を分析するクラス"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def analyze_article_method(self, data: pd.DataFrame) -> ArticleMethodResult:
        """
        記事の手法を再現・分析

        Args:
            data: 株価データ（日付、終値、出来高等）

        Returns:
            ArticleMethodResult: 記事の手法の結果
        """
        try:
            # 記事の手法: 単純な回帰分析
            result = self._implement_article_method(data)
            return result
        except Exception as e:
            self.logger.error(f"記事の手法分析でエラー: {e}")
            raise

    def _implement_article_method(self, data: pd.DataFrame) -> ArticleMethodResult:
        """記事の手法を実装"""
        # データの準備
        data = data.copy()
        data["Date"] = pd.to_datetime(data["Date"])
        data = data.sort_values("Date")

        # 最小データサイズのチェック
        if len(data) < 20:
            # 最小データの場合は、より単純な手法を使用
            return self._implement_simple_method(data)

        # 特徴量の作成（記事の手法に基づく）
        data["Price_Change"] = data["Close"].pct_change()
        data["Volume_Change"] = data["Volume"].pct_change()
        data["Price_MA5"] = data["Close"].rolling(window=5).mean()
        data["Price_MA20"] = data["Close"].rolling(window=20).mean()

        # 欠損値を除去
        data = data.dropna()

        # 十分なデータがあるかチェック
        if len(data) < 10:
            return self._implement_simple_method(data)

        # 特徴量とターゲットの準備
        features = ["Price_Change", "Volume_Change", "Price_MA5", "Price_MA20"]
        X = data[features]
        y = data["Close"].shift(-1)  # 翌日の終値

        # 最後の行を除去（NaNのため）
        X = X[:-1]
        y = y[:-1]

        # データを学習・テストに分割
        split_point = int(len(X) * 0.8)
        X_train, X_test = X[:split_point], X[split_point:]
        y_train, y_test = y[:split_point], y[split_point:]

        # 線形回帰モデルの学習
        model = LinearRegression()
        model.fit(X_train, y_train)

        # 予測
        y_pred = model.predict(X_test)

        # 精度計算
        accuracy = self._calculate_accuracy(y_test, y_pred)

        # バックテスト実行
        backtest_result = self._run_article_backtest(data, model, features)

        return ArticleMethodResult(
            accuracy=accuracy,
            total_return=backtest_result["total_return"],
            total_trades=backtest_result["total_trades"],
            winning_trades=backtest_result["winning_trades"],
            losing_trades=backtest_result["losing_trades"],
            max_drawdown=backtest_result["max_drawdown"],
            sharpe_ratio=backtest_result["sharpe_ratio"],
            profit_factor=backtest_result["profit_factor"],
            analysis_period=f"{data['Date'].min().strftime('%Y-%m-%d')} to {data['Date'].max().strftime('%Y-%m-%d')}",
            method_name="記事の手法（単純回帰）",
        )

    def _implement_simple_method(self, data: pd.DataFrame) -> ArticleMethodResult:
        """最小データ用の簡単な手法"""
        # 基本的な統計情報のみを使用
        data = data.copy()
        data["Date"] = pd.to_datetime(data["Date"])
        data = data.sort_values("Date")

        # 簡単な特徴量
        data["Price_Change"] = data["Close"].pct_change()
        data = data.dropna()

        if len(data) < 2:
            # データが不足している場合はデフォルト値を返す
            return ArticleMethodResult(
                accuracy=0.0,
                total_return=0.0,
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                max_drawdown=0.0,
                sharpe_ratio=0.0,
                profit_factor=0.0,
                analysis_period=f"{data['Date'].min().strftime('%Y-%m-%d')} to {data['Date'].max().strftime('%Y-%m-%d')}",
                method_name="記事の手法（最小データ）",
            )

        # 簡単なバックテスト
        backtest_result = self._run_simple_backtest(data)

        return ArticleMethodResult(
            accuracy=0.5,  # デフォルト精度
            total_return=backtest_result["total_return"],
            total_trades=backtest_result["total_trades"],
            winning_trades=backtest_result["winning_trades"],
            losing_trades=backtest_result["losing_trades"],
            max_drawdown=backtest_result["max_drawdown"],
            sharpe_ratio=backtest_result["sharpe_ratio"],
            profit_factor=backtest_result["profit_factor"],
            analysis_period=f"{data['Date'].min().strftime('%Y-%m-%d')} to {data['Date'].max().strftime('%Y-%m-%d')}",
            method_name="記事の手法（最小データ）",
        )

    def _run_simple_backtest(self, data: pd.DataFrame) -> Dict:
        """簡単なバックテスト"""
        if len(data) < 2:
            return {
                "total_return": 0.0,
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "max_drawdown": 0.0,
                "sharpe_ratio": 0.0,
                "profit_factor": 0.0,
            }

        # 簡単な買いシグナル（価格上昇時）
        signals = data["Price_Change"] > 0
        returns = data["Price_Change"]

        total_return = returns.sum()
        total_trades = signals.sum()
        winning_trades = (returns[signals] > 0).sum()
        losing_trades = (returns[signals] < 0).sum()

        return {
            "total_return": total_return,
            "total_trades": int(total_trades),
            "winning_trades": int(winning_trades),
            "losing_trades": int(losing_trades),
            "max_drawdown": 0.0,
            "sharpe_ratio": 0.0,
            "profit_factor": 1.0
            if losing_trades == 0
            else winning_trades / max(losing_trades, 1),
        }

    def _calculate_accuracy(self, y_true: pd.Series, y_pred: np.ndarray) -> float:
        """精度計算（記事の74%精度を再現）"""
        if len(y_true) == 0 or len(y_pred) == 0:
            return 0.0

        # 方向性の精度を計算
        direction_true = np.sign(y_true.diff().dropna())
        direction_pred = np.sign(np.diff(y_pred))

        # 長さを揃える
        min_len = min(len(direction_true), len(direction_pred))
        if min_len == 0:
            return 0.0

        direction_true = direction_true[:min_len]
        direction_pred = direction_pred[:min_len]

        accuracy = np.mean(direction_true == direction_pred)
        return accuracy

    def _run_article_backtest(
        self, data: pd.DataFrame, model, features: List[str]
    ) -> Dict:
        """記事の手法のバックテスト"""
        # バックテスト期間の設定
        test_start = int(len(data) * 0.8)
        test_data = data.iloc[test_start:].copy()

        # 特徴量が存在するかチェック
        available_features = [f for f in features if f in test_data.columns]
        if not available_features:
            return {
                "total_return": 0.0,
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "max_drawdown": 0.0,
                "sharpe_ratio": 0.0,
                "profit_factor": 0.0,
            }

        # 取引コスト（記事では考慮されていない）
        commission_rate = 0.001  # 0.1%

        # 初期設定
        initial_capital = 100000  # 10万円
        capital = initial_capital
        position = 0
        trades = []
        equity_curve = [initial_capital]

        # バックテスト実行
        for i in range(len(test_data) - 1):
            current_data = test_data.iloc[i]
            next_data = test_data.iloc[i + 1]

            # 特徴量の準備
            features_data = current_data[available_features].values.reshape(1, -1)

            # 予測
            predicted_price = model.predict(features_data)[0]
            current_price = current_data["Close"]
            next_price = next_data["Close"]

            # 取引判定（記事の手法: 0.5閾値）
            confidence = abs(predicted_price - current_price) / current_price

            if confidence > 0.5:  # 記事の閾値
                if predicted_price > current_price and position == 0:
                    # 買いシグナル
                    position = capital / current_price
                    capital = 0
                    trades.append(
                        {
                            "type": "BUY",
                            "price": current_price,
                            "date": current_data["Date"],
                            "confidence": confidence,
                        }
                    )
                elif predicted_price < current_price and position > 0:
                    # 売りシグナル
                    capital = position * current_price * (1 - commission_rate)
                    position = 0
                    trades.append(
                        {
                            "type": "SELL",
                            "price": current_price,
                            "date": current_data["Date"],
                            "confidence": confidence,
                        }
                    )

            # 現在の資産価値
            current_value = capital + (position * next_price if position > 0 else 0)
            equity_curve.append(current_value)

        # 最終的な資産価値
        final_value = capital + (
            position * test_data.iloc[-1]["Close"] if position > 0 else 0
        )

        # メトリクス計算
        total_return = (final_value - initial_capital) / initial_capital
        total_trades = len(trades)
        winning_trades = sum(1 for trade in trades if trade["type"] == "SELL")
        losing_trades = total_trades - winning_trades

        # 最大ドローダウン
        equity_series = pd.Series(equity_curve)
        rolling_max = equity_series.expanding().max()
        drawdown = (equity_series - rolling_max) / rolling_max
        max_drawdown = drawdown.min()

        # シャープレシオ
        returns = equity_series.pct_change().dropna()
        sharpe_ratio = (
            returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
        )

        # プロフィットファクター
        profit_factor = 1.0  # 記事では計算されていない

        return {
            "total_return": total_return,
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "max_drawdown": max_drawdown,
            "sharpe_ratio": sharpe_ratio,
            "profit_factor": profit_factor,
        }


class ImprovedMethodAnalyzer:
    """改善された手法を分析するクラス"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def analyze_improved_method(self, data: pd.DataFrame) -> ImprovedMethodResult:
        """
        改善された手法を実装・分析

        Args:
            data: 株価データ

        Returns:
            ImprovedMethodResult: 改善された手法の結果
        """
        try:
            result = self._implement_improved_method(data)
            return result
        except Exception as e:
            self.logger.error(f"改善手法分析でエラー: {e}")
            raise

    def _implement_improved_method(self, data: pd.DataFrame) -> ImprovedMethodResult:
        """改善された手法を実装"""
        # データの準備
        data = data.copy()
        data["Date"] = pd.to_datetime(data["Date"])
        data = data.sort_values("Date")

        # 高度な特徴量の作成
        data = self._create_advanced_features(data)

        # 欠損値を除去
        data = data.dropna()

        # 特徴量とターゲットの準備
        features = [
            "Price_Change",
            "Volume_Change",
            "Price_MA5",
            "Price_MA20",
            "RSI",
            "MACD",
            "BB_Upper",
            "BB_Lower",
            "ATR",
            "Volatility",
        ]
        X = data[features]
        y = data["Close"].shift(-1)

        # 最後の行を除去
        X = X[:-1]
        y = y[:-1]

        # データを学習・テストに分割
        split_point = int(len(X) * 0.8)
        X_train, X_test = X[:split_point], X[split_point:]
        y_train, y_test = y[:split_point], y[split_point:]

        # アンサンブルモデルの学習
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.ensemble import GradientBoostingRegressor
        from sklearn.linear_model import Ridge

        models = {
            "rf": RandomForestRegressor(n_estimators=100, random_state=42),
            "gb": GradientBoostingRegressor(n_estimators=100, random_state=42),
            "ridge": Ridge(alpha=1.0),
        }

        # 各モデルの学習
        for name, model in models.items():
            model.fit(X_train, y_train)

        # アンサンブル予測
        predictions = []
        for name, model in models.items():
            pred = model.predict(X_test)
            predictions.append(pred)

        # 重み付き平均
        y_pred = np.mean(predictions, axis=0)

        # 信頼度計算
        confidence_scores = self._calculate_confidence_scores(X_test, models)

        # 精度計算
        accuracy = self._calculate_improved_accuracy(y_test, y_pred, confidence_scores)

        # 改善されたバックテスト実行
        backtest_result = self._run_improved_backtest(
            data, models, features, confidence_scores
        )

        return ImprovedMethodResult(
            accuracy=accuracy,
            total_return=backtest_result["total_return"],
            total_trades=backtest_result["total_trades"],
            winning_trades=backtest_result["winning_trades"],
            losing_trades=backtest_result["losing_trades"],
            max_drawdown=backtest_result["max_drawdown"],
            sharpe_ratio=backtest_result["sharpe_ratio"],
            profit_factor=backtest_result["profit_factor"],
            analysis_period=f"{data['Date'].min().strftime('%Y-%m-%d')} to {data['Date'].max().strftime('%Y-%m-%d')}",
            method_name="改善された手法（アンサンブル）",
            reliability_threshold=0.7,  # 70%の信頼度閾値
            dynamic_stop_loss=True,
            position_sizing="動的",
        )

    def _create_advanced_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """高度な特徴量の作成"""
        # 基本特徴量
        data["Price_Change"] = data["Close"].pct_change()
        data["Volume_Change"] = data["Volume"].pct_change()
        data["Price_MA5"] = data["Close"].rolling(window=5).mean()
        data["Price_MA20"] = data["Close"].rolling(window=20).mean()

        # RSI
        data["RSI"] = self._calculate_rsi(data["Close"])

        # MACD
        data["MACD"] = self._calculate_macd(data["Close"])

        # ボリンジャーバンド
        bb_upper, bb_lower = self._calculate_bollinger_bands(data["Close"])
        data["BB_Upper"] = bb_upper
        data["BB_Lower"] = bb_lower

        # ATR
        data["ATR"] = self._calculate_atr(data)

        # ボラティリティ
        data["Volatility"] = data["Close"].rolling(window=20).std()

        return data

    def _calculate_rsi(self, prices: pd.Series, window: int = 14) -> pd.Series:
        """RSI計算"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _calculate_macd(
        self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
    ) -> pd.Series:
        """MACD計算"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        return macd

    def _calculate_bollinger_bands(
        self, prices: pd.Series, window: int = 20, num_std: float = 2
    ) -> Tuple[pd.Series, pd.Series]:
        """ボリンジャーバンド計算"""
        if len(prices) < window:
            # データが不足している場合は、適切な上下バンドを生成
            upper_band = prices * 1.1  # 10%上
            lower_band = prices * 0.9  # 10%下
            return upper_band, lower_band

        rolling_mean = prices.rolling(window=window).mean()
        rolling_std = prices.rolling(window=window).std()

        # NaN値を適切に処理
        rolling_std = rolling_std.fillna(
            rolling_std.mean() if not rolling_std.isna().all() else 0
        )

        upper_band = rolling_mean + (rolling_std * num_std)
        lower_band = rolling_mean - (rolling_std * num_std)

        # NaN値を適切に処理
        upper_band = upper_band.fillna(prices * 1.1)
        lower_band = lower_band.fillna(prices * 0.9)

        return upper_band, lower_band

    def _calculate_atr(self, data: pd.DataFrame, window: int = 14) -> pd.Series:
        """ATR計算"""
        high_low = data["High"] - data["Low"]
        high_close = np.abs(data["High"] - data["Close"].shift())
        low_close = np.abs(data["Low"] - data["Close"].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        atr = true_range.rolling(window=window).mean()
        return atr

    def _calculate_confidence_scores(
        self, X_test: pd.DataFrame, models: Dict
    ) -> np.ndarray:
        """信頼度スコアの計算"""
        # 各モデルの予測
        predictions = []
        for model in models.values():
            pred = model.predict(X_test)
            predictions.append(pred)

        # 予測の分散を信頼度の逆数として使用
        predictions_array = np.array(predictions)
        variance = np.var(predictions_array, axis=0)
        confidence = 1 / (1 + variance)

        return confidence

    def _calculate_improved_accuracy(
        self, y_true: pd.Series, y_pred: np.ndarray, confidence_scores: np.ndarray
    ) -> float:
        """改善された精度計算"""
        # 信頼度70%以上の予測のみを考慮
        high_confidence_mask = confidence_scores >= 0.7

        if np.sum(high_confidence_mask) == 0:
            return 0.0

        y_true_filtered = y_true[high_confidence_mask]
        y_pred_filtered = y_pred[high_confidence_mask]

        # 方向性の精度を計算
        direction_true = np.sign(y_true_filtered.diff().dropna())
        direction_pred = np.sign(np.diff(y_pred_filtered))

        # 長さを揃える
        min_len = min(len(direction_true), len(direction_pred))
        if min_len == 0:
            return 0.0

        direction_true = direction_true[:min_len]
        direction_pred = direction_pred[:min_len]

        accuracy = np.mean(direction_true == direction_pred)
        return accuracy

    def _run_improved_backtest(
        self,
        data: pd.DataFrame,
        models: Dict,
        features: List[str],
        confidence_scores: np.ndarray,
    ) -> Dict:
        """改善されたバックテスト"""
        # バックテスト期間の設定
        test_start = int(len(data) * 0.8)
        test_data = data.iloc[test_start:].copy()

        # 特徴量が存在するかチェック
        available_features = [f for f in features if f in test_data.columns]
        if not available_features:
            return {
                "total_return": 0.0,
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "max_drawdown": 0.0,
                "sharpe_ratio": 0.0,
                "profit_factor": 0.0,
            }

        # 現実的な取引コスト
        commission_rate = 0.002  # 0.2%
        slippage_rate = 0.001  # 0.1%
        total_cost_rate = commission_rate + slippage_rate

        # 初期設定
        initial_capital = 100000
        capital = initial_capital
        position = 0
        trades = []
        equity_curve = [initial_capital]
        stop_loss_price = None
        take_profit_price = None

        # バックテスト実行
        for i in range(len(test_data) - 1):
            current_data = test_data.iloc[i]
            next_data = test_data.iloc[i + 1]

            # 特徴量の準備
            features_data = current_data[available_features].values.reshape(1, -1)

            # アンサンブル予測
            predictions = []
            for model in models.values():
                pred = model.predict(features_data)[0]
                predictions.append(pred)

            predicted_price = np.mean(predictions)
            current_price = current_data["Close"]
            next_price = next_data["Close"]

            # 信頼度計算
            variance = np.var(predictions)
            confidence = 1 / (1 + variance)

            # 動的損切り・利確チェック
            if position > 0:
                if stop_loss_price and next_price <= stop_loss_price:
                    # 損切り
                    capital = position * next_price * (1 - total_cost_rate)
                    position = 0
                    trades.append(
                        {
                            "type": "STOP_LOSS",
                            "price": next_price,
                            "date": next_data["Date"],
                            "confidence": confidence,
                        }
                    )
                    stop_loss_price = None
                    take_profit_price = None
                elif take_profit_price and next_price >= take_profit_price:
                    # 利確
                    capital = position * next_price * (1 - total_cost_rate)
                    position = 0
                    trades.append(
                        {
                            "type": "TAKE_PROFIT",
                            "price": next_price,
                            "date": next_data["Date"],
                            "confidence": confidence,
                        }
                    )
                    stop_loss_price = None
                    take_profit_price = None

            # 信頼度70%以上での取引判定
            if confidence >= 0.7:
                if (
                    predicted_price > current_price * 1.02 and position == 0
                ):  # 2%以上の上昇予測
                    # 買いシグナル
                    position = capital / (current_price * (1 + total_cost_rate))
                    capital = 0
                    trades.append(
                        {
                            "type": "BUY",
                            "price": current_price,
                            "date": current_data["Date"],
                            "confidence": confidence,
                        }
                    )
                    # 動的損切り・利確設定
                    stop_loss_price = current_price * 0.95  # 5%損切り
                    take_profit_price = current_price * 1.10  # 10%利確
                elif (
                    predicted_price < current_price * 0.98 and position > 0
                ):  # 2%以上の下落予測
                    # 売りシグナル
                    capital = position * current_price * (1 - total_cost_rate)
                    position = 0
                    trades.append(
                        {
                            "type": "SELL",
                            "price": current_price,
                            "date": current_data["Date"],
                            "confidence": confidence,
                        }
                    )
                    stop_loss_price = None
                    take_profit_price = None

            # 現在の資産価値
            current_value = capital + (position * next_price if position > 0 else 0)
            equity_curve.append(current_value)

        # 最終的な資産価値
        final_value = capital + (
            position * test_data.iloc[-1]["Close"] if position > 0 else 0
        )

        # メトリクス計算
        total_return = (final_value - initial_capital) / initial_capital
        total_trades = len(trades)
        winning_trades = sum(
            1 for trade in trades if trade["type"] in ["SELL", "TAKE_PROFIT"]
        )
        losing_trades = sum(1 for trade in trades if trade["type"] in ["STOP_LOSS"])

        # 最大ドローダウン
        equity_series = pd.Series(equity_curve)
        rolling_max = equity_series.expanding().max()
        drawdown = (equity_series - rolling_max) / rolling_max
        max_drawdown = drawdown.min()

        # シャープレシオ
        returns = equity_series.pct_change().dropna()
        sharpe_ratio = (
            returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
        )

        # プロフィットファクター
        profits = [
            trade for trade in trades if trade["type"] in ["SELL", "TAKE_PROFIT"]
        ]
        losses = [trade for trade in trades if trade["type"] == "STOP_LOSS"]

        total_profit = sum(1 for trade in profits)  # 簡略化
        total_loss = sum(1 for trade in losses)  # 簡略化

        profit_factor = total_profit / total_loss if total_loss > 0 else float("inf")

        return {
            "total_return": total_return,
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "max_drawdown": max_drawdown,
            "sharpe_ratio": sharpe_ratio,
            "profit_factor": profit_factor,
        }


class MethodComparison:
    """手法比較クラス"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def compare_methods(self, data: pd.DataFrame) -> ComparisonResult:
        """
        記事の手法と改善手法を比較

        Args:
            data: 株価データ

        Returns:
            ComparisonResult: 比較結果
        """
        try:
            # 記事の手法の分析
            article_analyzer = ArticleMethodAnalyzer()
            article_result = article_analyzer.analyze_article_method(data)

            # 改善手法の分析
            improved_analyzer = ImprovedMethodAnalyzer()
            improved_result = improved_analyzer.analyze_improved_method(data)

            # 改善効果の計算
            improvement_metrics = self._calculate_improvement_metrics(
                article_result, improved_result
            )

            # 推奨事項の生成
            recommendation = self._generate_recommendation(improvement_metrics)

            return ComparisonResult(
                article_method=article_result,
                improved_method=improved_result,
                improvement_metrics=improvement_metrics,
                recommendation=recommendation,
            )

        except Exception as e:
            self.logger.error(f"手法比較でエラー: {e}")
            raise

    def _calculate_improvement_metrics(
        self, article_result: ArticleMethodResult, improved_result: ImprovedMethodResult
    ) -> Dict[str, float]:
        """改善効果の計算"""
        # ドローダウンの改善は、より小さな負の値（絶対値で言えばより小さい値）になること
        # 例: -0.1 → -0.05 の改善は 0.05 の改善
        drawdown_improvement = abs(article_result.max_drawdown) - abs(
            improved_result.max_drawdown
        )

        return {
            "accuracy_improvement": improved_result.accuracy - article_result.accuracy,
            "return_improvement": improved_result.total_return
            - article_result.total_return,
            "drawdown_improvement": drawdown_improvement,
            "sharpe_improvement": improved_result.sharpe_ratio
            - article_result.sharpe_ratio,
            "profit_factor_improvement": improved_result.profit_factor
            - article_result.profit_factor,
        }

    def _generate_recommendation(self, improvement_metrics: Dict[str, float]) -> str:
        """推奨事項の生成"""
        if improvement_metrics["return_improvement"] > 0.05:  # 5%以上の改善
            return "改善された手法を強く推奨します。大幅な利益向上が期待できます。"
        elif improvement_metrics["return_improvement"] > 0:
            return "改善された手法を推奨します。利益向上が期待できます。"
        else:
            return "さらなる改善が必要です。パラメータの調整を検討してください。"


def create_sample_data() -> pd.DataFrame:
    """サンプルデータの作成"""
    # データ期間を短縮してテスト高速化
    dates = pd.date_range(start="2023-01-01", end="2023-06-30", freq="D")
    np.random.seed(42)

    # ランダムウォークで株価を生成
    price = 100
    prices = [price]
    volumes = []

    for i in range(len(dates) - 1):
        change = np.random.normal(0, 0.02)  # 2%の標準偏差
        price *= 1 + change
        prices.append(price)
        volumes.append(np.random.randint(1000, 10000))

    volumes.append(np.random.randint(1000, 10000))

    # 高値・安値・始値の生成（OHLCの関係を保つ）
    data_rows = []
    for i, price in enumerate(prices):
        # 始値の生成
        open_price = price * (1 + np.random.normal(0, 0.005))

        # 高値・安値の生成（始値と終値を基準に）
        high_variation = abs(np.random.normal(0, 0.01))
        low_variation = abs(np.random.normal(0, 0.01))

        high_price = max(open_price, price) * (1 + high_variation)
        low_price = min(open_price, price) * (1 - low_variation)

        # OHLCの関係を保つ
        high_price = max(high_price, open_price, price)
        low_price = min(low_price, open_price, price)

        data_rows.append(
            {
                "Date": dates[i],
                "Open": open_price,
                "High": high_price,
                "Low": low_price,
                "Close": price,
                "Volume": volumes[i],
            }
        )

    data = pd.DataFrame(data_rows)

    return data
