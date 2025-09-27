"""
高頻度取引アルゴリズムのテスト
Test cases for High Frequency Trading Algorithm
"""

import pytest
import time
from datetime import datetime
from unittest.mock import Mock, patch
import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from high_frequency_trading import (
    HighFrequencyTrading,
    ArbitrageOpportunity,
    Trade,
    MarketData,
    MockDataSource,
)


class TestHighFrequencyTrading:
    """高頻度取引システムのテストクラス"""

    def setup_method(self):
        """テスト前のセットアップ"""
        self.config = {
            "latency_threshold": 0.001,
            "profit_threshold": 0.001,
            "max_position_size": 100000,
            "risk_limit": 0.02,
        }
        self.hft = HighFrequencyTrading(self.config)

    def teardown_method(self):
        """テスト後のクリーンアップ"""
        self.hft.cleanup()

    def test_initialization(self):
        """初期化テスト"""
        assert self.hft.latency_threshold == 0.001
        assert self.hft.profit_threshold == 0.001
        assert self.hft.max_position_size == 100000
        assert self.hft.risk_limit == 0.02
        assert self.hft.profit_loss == 0.0
        assert self.hft.total_trades == 0

    def test_find_arbitrage_opportunities(self):
        """裁定取引機会発見テスト"""
        # テストデータ
        price_differences = {
            "BTC": {
                "Binance": 50000.0,
                "Coinbase": 50100.0,  # 100ドルの価格差
                "Kraken": 49950.0,
            },
            "ETH": {"Binance": 3000.0, "Coinbase": 3005.0},  # 5ドルの価格差
        }

        opportunities = self.hft._find_arbitrage_opportunities(price_differences)

        # 機会が発見されることを確認
        assert len(opportunities) > 0

        # BTCの機会をチェック
        btc_opportunities = [opp for opp in opportunities if opp.symbol == "BTC"]
        assert len(btc_opportunities) > 0

        # 利益率が閾値以上であることを確認
        for opp in opportunities:
            assert opp.profit_percentage >= self.hft.profit_threshold

    def test_execute_arbitrage(self):
        """裁定取引実行テスト"""
        # テストデータ
        price_differences = {"BTC": {"Binance": 50000.0, "Coinbase": 50100.0}}

        trades = self.hft.execute_arbitrage(price_differences)

        # 取引が実行されることを確認
        assert isinstance(trades, list)
        # 裁定取引なので買いと売りのペアが実行される
        if trades:
            assert len(trades) % 2 == 0  # 偶数個の取引

    def test_risk_limits(self):
        """リスク制限テスト"""
        # 大きなポジションサイズの機会を作成
        large_opportunity = ArbitrageOpportunity(
            symbol="BTC",
            buy_exchange="Binance",
            sell_exchange="Coinbase",
            buy_price=50000.0,
            sell_price=50100.0,
            profit=100.0,
            profit_percentage=0.002,
            volume=2000000,  # 最大ポジションサイズを超える
            timestamp=datetime.now(),
        )

        # リスク制限により拒否されることを確認
        assert not self.hft._check_risk_limits(large_opportunity)

    def test_position_update(self):
        """ポジション更新テスト"""
        symbol = "BTC"
        volume = 1000

        # 初期ポジションは0
        assert self.hft.positions.get(symbol, 0) == 0

        # ポジションを更新
        self.hft._update_position(symbol, volume)
        assert self.hft.positions[symbol] == volume

        # 追加でポジションを更新
        self.hft._update_position(symbol, -500)
        assert self.hft.positions[symbol] == 500

    def test_performance_metrics(self):
        """パフォーマンス指標テスト"""
        # 初期状態
        metrics = self.hft.get_performance_metrics()
        assert metrics["total_trades"] == 0
        assert metrics["profit_loss"] == 0.0

        # ダミーの実行時間を追加
        self.hft.execution_times = [0.0005, 0.0008, 0.0012]
        self.hft.total_trades = 6
        self.hft.profit_loss = 150.0

        metrics = self.hft.get_performance_metrics()
        assert metrics["total_trades"] == 6
        assert metrics["profit_loss"] == 150.0
        assert "avg_execution_time" in metrics
        assert "max_execution_time" in metrics
        assert "min_execution_time" in metrics

    def test_latency_threshold(self):
        """レイテンシー閾値テスト"""
        # 閾値を超える実行時間をシミュレート
        self.hft.execution_times = [0.002]  # 2ms (閾値1msを超える)

        # 警告がログに出力されることを確認（実際のテストでは難しいので、メトリクスで確認）
        metrics = self.hft.get_performance_metrics()
        assert metrics["max_execution_time"] > self.hft.latency_threshold

    @patch("high_frequency_trading.logger")
    def test_error_handling(self, mock_logger):
        """エラーハンドリングテスト"""
        # 無効なデータでテスト
        invalid_data = None

        trades = self.hft.execute_arbitrage(invalid_data)
        assert trades == []

        # エラーログが出力されることを確認
        mock_logger.error.assert_called()


class TestMockDataSource:
    """モックデータソースのテストクラス"""

    def setup_method(self):
        """テスト前のセットアップ"""
        self.data_source = MockDataSource()

    def test_initialization(self):
        """初期化テスト"""
        assert len(self.data_source.symbols) > 0
        assert len(self.data_source.exchanges) > 0
        assert len(self.data_source.base_prices) > 0

    def test_get_latest_data(self):
        """最新データ取得テスト"""
        data = self.data_source.get_latest_data()

        # データが取得されることを確認
        assert data is not None
        assert isinstance(data, dict)

        # シンボルが含まれることを確認
        symbol = list(data.keys())[0]
        assert symbol in self.data_source.symbols

        # 取引所データが含まれることを確認
        exchanges = data[symbol]
        assert isinstance(exchanges, dict)
        assert len(exchanges) > 0


class TestArbitrageOpportunity:
    """裁定取引機会クラスのテスト"""

    def test_arbitrage_opportunity_creation(self):
        """裁定取引機会作成テスト"""
        opportunity = ArbitrageOpportunity(
            symbol="BTC",
            buy_exchange="Binance",
            sell_exchange="Coinbase",
            buy_price=50000.0,
            sell_price=50100.0,
            profit=100.0,
            profit_percentage=0.002,
            volume=1000,
            timestamp=datetime.now(),
        )

        assert opportunity.symbol == "BTC"
        assert opportunity.buy_exchange == "Binance"
        assert opportunity.sell_exchange == "Coinbase"
        assert opportunity.buy_price == 50000.0
        assert opportunity.sell_price == 50100.0
        assert opportunity.profit == 100.0
        assert opportunity.profit_percentage == 0.002
        assert opportunity.volume == 1000


class TestTrade:
    """取引クラスのテスト"""

    def test_trade_creation(self):
        """取引作成テスト"""
        trade = Trade(
            symbol="BTC",
            side="buy",
            price=50000.0,
            volume=1000,
            exchange="Binance",
            timestamp=datetime.now(),
            order_id="BTC_buy_1234567890",
        )

        assert trade.symbol == "BTC"
        assert trade.side == "buy"
        assert trade.price == 50000.0
        assert trade.volume == 1000
        assert trade.exchange == "Binance"
        assert trade.order_id == "BTC_buy_1234567890"


def test_integration():
    """統合テスト"""
    # 設定
    config = {
        "latency_threshold": 0.001,
        "profit_threshold": 0.0005,
        "max_position_size": 100000,
        "risk_limit": 0.01,
    }

    # システムを初期化
    hft = HighFrequencyTrading(config)
    data_source = MockDataSource()

    try:
        # 複数回の裁定取引をテスト
        total_trades = 0

        for i in range(5):
            price_differences = data_source.get_latest_data()
            if price_differences:
                trades = hft.execute_arbitrage(price_differences)
                total_trades += len(trades)

        # パフォーマンス指標を取得
        metrics = hft.get_performance_metrics()

        # 基本的な動作を確認
        assert isinstance(metrics, dict)
        assert "total_trades" in metrics
        assert "profit_loss" in metrics

    finally:
        hft.cleanup()


if __name__ == "__main__":
    # テスト実行
    pytest.main([__file__, "-v"])
