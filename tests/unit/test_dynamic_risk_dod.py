import pandas as pd
import numpy as np

from core.dynamic_risk_management import DynamicRiskManager, RiskMetrics, RiskLevel


def _make_series(n=60, start=100.0, drift=-0.0005, vol=0.01):
    prices = [start]
    for _ in range(n - 1):
        prices.append(prices[-1] * (1.0 + np.random.normal(drift, vol)))
    return pd.Series(prices)


def _make_df(n=60, start=100.0, drift=-0.0005, vol=0.01):
    s = _make_series(n=n, start=start, drift=drift, vol=vol)
    return pd.DataFrame(
        {"Close": s, "Volume": np.random.randint(1000, 10000, size=len(s))}
    )


def test_dod_enforced_close_when_mdd_exceeds_30_percent():
    mgr = DynamicRiskManager()
    stock_df = _make_df()
    market_df = _make_df(drift=0.0)

    # max_drawdownを30%超にしたメトリクスを直接指定
    metrics = RiskMetrics(
        var_95=0.02,
        var_99=0.04,
        max_drawdown=0.31,  # 31% → DoD違反
        sharpe_ratio=1.0,
        sortino_ratio=1.0,
        calmar_ratio=1.0,
        volatility=0.20,
        beta=1.0,
        correlation=0.2,
        risk_level=RiskLevel.HIGH,
        position_size=0.10,
        stop_loss=0.0,
        take_profit=0.0,
    )

    decision = mgr.should_adjust_position(
        metrics, previous_metrics=None, market_conditions={}
    )
    assert decision["should_close"] is True
    assert decision["new_position_size"] == 0.0
    assert "DoD" in decision["adjustment_reason"]
