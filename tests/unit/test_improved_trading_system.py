"""
改善された取引システムのテスト
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime

from core.improved_trading_system import (
    ImprovedTradingSystem,
    TradingSignal,
    PortfolioPosition,
    RiskMetrics,
    create_sample_trading_data,
)


class TestImprovedTradingSystem:
    """改善された取引システムのテスト"""

    def setup_method(self):
        """テストのセットアップ"""
        self.trading_system = ImprovedTradingSystem(
            reliability_threshold=0.7,
            commission_rate=0.002,
            slippage_rate=0.001,
            max_position_size=0.1,
        )
        self.sample_data = create_sample_trading_data()

    def test_initialization(self):
        """初期化テスト"""
        assert self.trading_system.reliability_threshold == 0.7
        assert self.trading_system.commission_rate == 0.002
        assert self.trading_system.slippage_rate == 0.001
        assert self.trading_system.max_position_size == 0.1
        assert self.trading_system.total_cost_rate == 0.003
        assert hasattr(self.trading_system, "models")
        assert hasattr(self.trading_system, "trained_models")
        assert hasattr(self.trading_system, "feature_importance")

    def test_initialization_with_default_values(self):
        """デフォルト値での初期化テスト"""
        system = ImprovedTradingSystem()

        assert system.reliability_threshold == 0.7
        assert system.commission_rate == 0.002
        assert system.slippage_rate == 0.001
        assert system.max_position_size == 0.1

    def test_train_models_success(self):
        """モデル学習の成功テスト"""
        model_performance = self.trading_system.train_models(self.sample_data)

        assert isinstance(model_performance, dict)
        assert len(model_performance) > 0

        for model_name, performance in model_performance.items():
            assert isinstance(performance, dict)
            assert "mse" in performance
            assert "mae" in performance
            assert "r2" in performance
            assert isinstance(performance["mse"], (int, float))
            assert isinstance(performance["mae"], (int, float))
            assert isinstance(performance["r2"], (int, float))

    def test_train_models_with_invalid_data(self):
        """無効なデータでのモデル学習テスト"""
        invalid_data = pd.DataFrame()

        with pytest.raises(Exception):
            self.trading_system.train_models(invalid_data)

    def test_train_models_with_minimal_data(self):
        """最小限のデータでのモデル学習テスト"""
        minimal_data = pd.DataFrame(
            {
                "Date": pd.date_range("2023-01-01", periods=50, freq="D"),
                "Open": [100 + i for i in range(50)],
                "High": [101 + i for i in range(50)],
                "Low": [99 + i for i in range(50)],
                "Close": [100 + i for i in range(50)],
                "Volume": [1000] * 50,
            }
        )

        model_performance = self.trading_system.train_models(minimal_data)
        assert isinstance(model_performance, dict)

    def test_create_features(self):
        """特徴量作成のテスト"""
        features_data = self.trading_system._create_features(self.sample_data)

        assert isinstance(features_data, pd.DataFrame)
        assert len(features_data) == len(self.sample_data)

        # 基本特徴量の確認
        expected_features = [
            "Price_Change",
            "Price_Change_2",
            "Price_Change_5",
            "Price_Change_10",
            "MA_5",
            "MA_10",
            "MA_20",
            "MA_50",
            "MA5_Deviation",
            "MA20_Deviation",
            "MA50_Deviation",
            "Volatility_5",
            "Volatility_20",
            "Volatility_50",
            "Volume_Change",
            "Volume_MA_5",
            "Volume_MA_20",
            "Volume_Ratio",
            "RSI",
            "MACD",
            "MACD_Signal",
            "MACD_Histogram",
            "BB_Upper",
            "BB_Lower",
            "BB_Middle",
            "BB_Width",
            "BB_Position",
            "ATR",
            "Stoch_K",
            "Stoch_D",
            "Williams_R",
            "CCI",
            "ADX",
            "Price_Position_20",
            "Price_Position_50",
        ]

        for feature in expected_features:
            assert feature in features_data.columns

    def test_calculate_rsi(self):
        """RSI計算のテスト"""
        prices = pd.Series([100, 102, 101, 103, 105, 104, 106, 108, 107, 109])
        rsi = self.trading_system._calculate_rsi(prices)

        assert isinstance(rsi, pd.Series)
        assert len(rsi) == len(prices)
        assert rsi.isna().sum() > 0  # 初期値はNaN
        assert all(0 <= val <= 100 for val in rsi.dropna())

    def test_calculate_macd(self):
        """MACD計算のテスト"""
        prices = pd.Series([100, 102, 101, 103, 105, 104, 106, 108, 107, 109])
        macd = self.trading_system._calculate_macd(prices)

        assert isinstance(macd, pd.Series)
        assert len(macd) == len(prices)

    def test_calculate_bollinger_bands(self):
        """ボリンジャーバンド計算のテスト"""
        prices = pd.Series([100, 102, 101, 103, 105, 104, 106, 108, 107, 109])
        upper, lower, middle = self.trading_system._calculate_bollinger_bands(prices)

        assert isinstance(upper, pd.Series)
        assert isinstance(lower, pd.Series)
        assert isinstance(middle, pd.Series)
        assert len(upper) == len(prices)
        assert len(lower) == len(prices)
        assert len(middle) == len(prices)
        assert (upper > lower).all()
        assert (upper > middle).all()
        assert (lower < middle).all()

    def test_calculate_atr(self):
        """ATR計算のテスト"""
        data = pd.DataFrame(
            {
                "High": [101, 103, 102, 104, 106, 105, 107, 109, 108, 110],
                "Low": [99, 101, 100, 102, 104, 103, 105, 107, 106, 108],
                "Close": [100, 102, 101, 103, 105, 104, 106, 108, 107, 109],
            }
        )
        atr = self.trading_system._calculate_atr(data)

        assert isinstance(atr, pd.Series)
        assert len(atr) == len(data)
        assert all(atr >= 0)

    def test_calculate_stochastic(self):
        """ストキャスティクス計算のテスト"""
        data = pd.DataFrame(
            {
                "High": [101, 103, 102, 104, 106, 105, 107, 109, 108, 110],
                "Low": [99, 101, 100, 102, 104, 103, 105, 107, 106, 108],
                "Close": [100, 102, 101, 103, 105, 104, 106, 108, 107, 109],
            }
        )
        k_percent, d_percent = self.trading_system._calculate_stochastic(data)

        assert isinstance(k_percent, pd.Series)
        assert isinstance(d_percent, pd.Series)
        assert len(k_percent) == len(data)
        assert len(d_percent) == len(data)
        assert all(0 <= val <= 100 for val in k_percent.dropna())
        assert all(0 <= val <= 100 for val in d_percent.dropna())

    def test_calculate_williams_r(self):
        """ウィリアムズ%R計算のテスト"""
        data = pd.DataFrame(
            {
                "High": [101, 103, 102, 104, 106, 105, 107, 109, 108, 110],
                "Low": [99, 101, 100, 102, 104, 103, 105, 107, 106, 108],
                "Close": [100, 102, 101, 103, 105, 104, 106, 108, 107, 109],
            }
        )
        williams_r = self.trading_system._calculate_williams_r(data)

        assert isinstance(williams_r, pd.Series)
        assert len(williams_r) == len(data)
        assert all(-100 <= val <= 0 for val in williams_r.dropna())

    def test_calculate_cci(self):
        """CCI計算のテスト"""
        data = pd.DataFrame(
            {
                "High": [101, 103, 102, 104, 106, 105, 107, 109, 108, 110],
                "Low": [99, 101, 100, 102, 104, 103, 105, 107, 106, 108],
                "Close": [100, 102, 101, 103, 105, 104, 106, 108, 107, 109],
            }
        )
        cci = self.trading_system._calculate_cci(data)

        assert isinstance(cci, pd.Series)
        assert len(cci) == len(data)

    def test_calculate_adx(self):
        """ADX計算のテスト"""
        data = pd.DataFrame(
            {
                "High": [101, 103, 102, 104, 106, 105, 107, 109, 108, 110],
                "Low": [99, 101, 100, 102, 104, 103, 105, 107, 106, 108],
                "Close": [100, 102, 101, 103, 105, 104, 106, 108, 107, 109],
            }
        )
        adx = self.trading_system._calculate_adx(data)

        assert isinstance(adx, pd.Series)
        assert len(adx) == len(data)
        assert all(adx >= 0)

    def test_generate_signals_without_trained_models(self):
        """学習されていないモデルでのシグナル生成テスト"""
        with pytest.raises(ValueError, match="モデルが学習されていません"):
            self.trading_system.generate_signals(self.sample_data)

    def test_generate_signals_success(self):
        """シグナル生成の成功テスト"""
        # モデルの学習
        self.trading_system.train_models(self.sample_data)

        # シグナル生成
        signals = self.trading_system.generate_signals(self.sample_data)

        assert isinstance(signals, list)
        for signal in signals:
            assert isinstance(signal, TradingSignal)
            assert signal.symbol == "SAMPLE"
            assert signal.action in ["BUY", "SELL", "HOLD"]
            assert 0 <= signal.confidence <= 1
            assert signal.price > 0
            assert signal.target_price > 0
            assert signal.stop_loss > 0
            assert signal.take_profit > 0
            assert 0 < signal.position_size <= 1
            assert isinstance(signal.reason, str)
            assert isinstance(signal.timestamp, (datetime, str))

    def test_generate_signals_with_invalid_data(self):
        """無効なデータでのシグナル生成テスト"""
        self.trading_system.train_models(self.sample_data)
        invalid_data = pd.DataFrame()

        with pytest.raises(Exception):
            self.trading_system.generate_signals(invalid_data)

    def test_run_backtest_success(self):
        """バックテスト実行の成功テスト"""
        # モデルの学習
        self.trading_system.train_models(self.sample_data)

        # バックテスト実行
        result = self.trading_system.run_backtest(self.sample_data)

        assert isinstance(result, dict)
        assert "total_return" in result
        assert "total_trades" in result
        assert "winning_trades" in result
        assert "losing_trades" in result
        assert "win_rate" in result
        assert "max_drawdown" in result
        assert "sharpe_ratio" in result
        assert "sortino_ratio" in result
        assert "calmar_ratio" in result
        assert "profit_factor" in result
        assert "final_capital" in result
        assert "equity_curve" in result
        assert "trades" in result

        assert isinstance(result["total_return"], (int, float))
        assert isinstance(result["total_trades"], int)
        assert result["total_trades"] >= 0
        assert isinstance(result["winning_trades"], int)
        assert result["winning_trades"] >= 0
        assert isinstance(result["losing_trades"], int)
        assert result["losing_trades"] >= 0
        assert 0 <= result["win_rate"] <= 1
        assert isinstance(result["max_drawdown"], (int, float))
        assert isinstance(result["sharpe_ratio"], (int, float))
        assert isinstance(result["sortino_ratio"], (int, float))
        assert isinstance(result["calmar_ratio"], (int, float))
        assert isinstance(result["profit_factor"], (int, float))
        assert result["profit_factor"] >= 0
        assert isinstance(result["final_capital"], (int, float))
        assert isinstance(result["equity_curve"], list)
        assert len(result["equity_curve"]) > 0
        assert isinstance(result["trades"], list)

    def test_run_backtest_with_different_initial_capital(self):
        """異なる初期資本でのバックテストテスト"""
        self.trading_system.train_models(self.sample_data)

        initial_capitals = [50000, 100000, 200000]
        for initial_capital in initial_capitals:
            result = self.trading_system.run_backtest(self.sample_data, initial_capital)
            assert result["final_capital"] > 0

    def test_run_backtest_with_invalid_data(self):
        """無効なデータでのバックテストテスト"""
        self.trading_system.train_models(self.sample_data)
        invalid_data = pd.DataFrame()

        with pytest.raises(Exception):
            self.trading_system.run_backtest(invalid_data)

    def test_calculate_risk_metrics(self):
        """リスク指標計算のテスト"""
        returns = pd.Series(
            [0.01, -0.02, 0.03, -0.01, 0.02, -0.03, 0.01, 0.02, -0.01, 0.03]
        )
        risk_metrics = self.trading_system.calculate_risk_metrics(returns)

        assert isinstance(risk_metrics, RiskMetrics)
        assert hasattr(risk_metrics, "var_95")
        assert hasattr(risk_metrics, "max_drawdown")
        assert hasattr(risk_metrics, "sharpe_ratio")
        assert hasattr(risk_metrics, "sortino_ratio")
        assert hasattr(risk_metrics, "calmar_ratio")
        assert hasattr(risk_metrics, "volatility")
        assert hasattr(risk_metrics, "beta")

        assert isinstance(risk_metrics.var_95, (int, float))
        assert isinstance(risk_metrics.max_drawdown, (int, float))
        assert isinstance(risk_metrics.sharpe_ratio, (int, float))
        assert isinstance(risk_metrics.sortino_ratio, (int, float))
        assert isinstance(risk_metrics.calmar_ratio, (int, float))
        assert isinstance(risk_metrics.volatility, (int, float))
        assert isinstance(risk_metrics.beta, (int, float))
        assert risk_metrics.volatility >= 0
        assert risk_metrics.beta >= 0

    def test_calculate_risk_metrics_with_empty_returns(self):
        """空のリターンでのリスク指標計算テスト"""
        returns = pd.Series([], dtype=float)

        with pytest.raises(Exception):
            self.trading_system.calculate_risk_metrics(returns)

    def test_calculate_risk_metrics_with_constant_returns(self):
        """一定のリターンでのリスク指標計算テスト"""
        returns = pd.Series([0.01] * 10)
        risk_metrics = self.trading_system.calculate_risk_metrics(returns)

        assert isinstance(risk_metrics, RiskMetrics)
        assert risk_metrics.volatility == 0
        assert risk_metrics.sharpe_ratio == 0 or np.isinf(risk_metrics.sharpe_ratio)


class TestTradingSignal:
    """取引シグナルのテスト"""

    def test_trading_signal_creation(self):
        """取引シグナル作成のテスト"""
        signal = TradingSignal(
            symbol="TEST",
            action="BUY",
            confidence=0.8,
            price=100.0,
            target_price=110.0,
            stop_loss=95.0,
            take_profit=110.0,
            position_size=0.1,
            reason="上昇予測",
            timestamp=datetime.now(),
        )

        assert signal.symbol == "TEST"
        assert signal.action == "BUY"
        assert signal.confidence == 0.8
        assert signal.price == 100.0
        assert signal.target_price == 110.0
        assert signal.stop_loss == 95.0
        assert signal.take_profit == 110.0
        assert signal.position_size == 0.1
        assert signal.reason == "上昇予測"
        assert isinstance(signal.timestamp, datetime)

    def test_trading_signal_validation(self):
        """取引シグナル検証のテスト"""
        # 有効なシグナル
        valid_signal = TradingSignal(
            symbol="TEST",
            action="BUY",
            confidence=0.8,
            price=100.0,
            target_price=110.0,
            stop_loss=95.0,
            take_profit=110.0,
            position_size=0.1,
            reason="上昇予測",
            timestamp=datetime.now(),
        )

        assert valid_signal.confidence >= 0
        assert valid_signal.confidence <= 1
        assert valid_signal.price > 0
        assert valid_signal.target_price > 0
        assert valid_signal.stop_loss > 0
        assert valid_signal.take_profit > 0
        assert 0 < valid_signal.position_size <= 1


class TestPortfolioPosition:
    """ポートフォリオポジションのテスト"""

    def test_portfolio_position_creation(self):
        """ポートフォリオポジション作成のテスト"""
        position = PortfolioPosition(
            symbol="TEST",
            quantity=100.0,
            entry_price=100.0,
            current_price=105.0,
            unrealized_pnl=500.0,
            stop_loss=95.0,
            take_profit=110.0,
            confidence=0.8,
        )

        assert position.symbol == "TEST"
        assert position.quantity == 100.0
        assert position.entry_price == 100.0
        assert position.current_price == 105.0
        assert position.unrealized_pnl == 500.0
        assert position.stop_loss == 95.0
        assert position.take_profit == 110.0
        assert position.confidence == 0.8


class TestRiskMetrics:
    """リスク指標のテスト"""

    def test_risk_metrics_creation(self):
        """リスク指標作成のテスト"""
        risk_metrics = RiskMetrics(
            var_95=-0.05,
            max_drawdown=-0.1,
            sharpe_ratio=1.5,
            sortino_ratio=2.0,
            calmar_ratio=1.2,
            volatility=0.15,
            beta=1.0,
        )

        assert risk_metrics.var_95 == -0.05
        assert risk_metrics.max_drawdown == -0.1
        assert risk_metrics.sharpe_ratio == 1.5
        assert risk_metrics.sortino_ratio == 2.0
        assert risk_metrics.calmar_ratio == 1.2
        assert risk_metrics.volatility == 0.15
        assert risk_metrics.beta == 1.0


class TestCreateSampleTradingData:
    """サンプル取引データ作成のテスト"""

    def test_create_sample_trading_data(self):
        """サンプル取引データ作成のテスト"""
        data = create_sample_trading_data()

        assert isinstance(data, pd.DataFrame)
        assert "Date" in data.columns
        assert "Open" in data.columns
        assert "High" in data.columns
        assert "Low" in data.columns
        assert "Close" in data.columns
        assert "Volume" in data.columns

        assert len(data) > 0
        assert data["Date"].dtype == "datetime64[ns]"
        assert all(data["High"] >= data["Low"])
        assert all(data["High"] >= data["Open"])
        assert all(data["High"] >= data["Close"])
        assert all(data["Low"] <= data["Open"])
        assert all(data["Low"] <= data["Close"])
        assert all(data["Volume"] > 0)

    def test_create_sample_trading_data_consistency(self):
        """サンプル取引データの一貫性テスト"""
        data1 = create_sample_trading_data()
        data2 = create_sample_trading_data()

        # 同じシードを使用しているため、同じデータが生成される
        pd.testing.assert_frame_equal(data1, data2)

    def test_create_sample_trading_data_date_range(self):
        """サンプル取引データの日付範囲テスト"""
        data = create_sample_trading_data()

        assert data["Date"].min() >= pd.Timestamp("2023-01-01")
        assert data["Date"].max() <= pd.Timestamp("2024-12-31")
        assert len(data) >= 365  # 1年以上のデータ


class TestIntegration:
    """統合テスト"""

    def test_full_trading_system_pipeline(self):
        """完全な取引システムパイプラインのテスト"""
        data = create_sample_trading_data()

        # 取引システムの初期化
        trading_system = ImprovedTradingSystem()

        # モデルの学習
        model_performance = trading_system.train_models(data)
        assert isinstance(model_performance, dict)
        assert len(model_performance) > 0

        # シグナル生成
        signals = trading_system.generate_signals(data)
        assert isinstance(signals, list)

        # バックテスト実行
        backtest_result = trading_system.run_backtest(data)
        assert isinstance(backtest_result, dict)
        assert "total_return" in backtest_result

        # リスク指標計算
        returns = pd.Series(backtest_result["equity_curve"]).pct_change().dropna()
        risk_metrics = trading_system.calculate_risk_metrics(returns)
        assert isinstance(risk_metrics, RiskMetrics)

    def test_error_handling(self):
        """エラーハンドリングのテスト"""
        # 空のデータフレーム
        empty_data = pd.DataFrame()

        with pytest.raises(Exception):
            trading_system = ImprovedTradingSystem()
            trading_system.train_models(empty_data)

        # 不正なデータ型
        invalid_data = "invalid_data"

        with pytest.raises(Exception):
            trading_system = ImprovedTradingSystem()
            trading_system.train_models(invalid_data)

    def test_performance_requirements(self):
        """パフォーマンス要件のテスト"""
        data = create_sample_trading_data()

        # 取引システムの実行時間
        import time

        start_time = time.time()

        trading_system = ImprovedTradingSystem()
        trading_system.train_models(data)
        signals = trading_system.generate_signals(data)
        backtest_result = trading_system.run_backtest(data)

        execution_time = time.time() - start_time

        # 実行時間が60秒以内であることを確認
        assert execution_time < 60

        # 結果の妥当性確認
        assert isinstance(backtest_result, dict)
        assert "total_return" in backtest_result
        assert isinstance(backtest_result["total_return"], (int, float))
