from datetime import datetime

from core.realtime_risk_monitor import RealtimeRiskMonitor, AlertLevel, RiskEvent


def test_emergency_alert_when_mdd_exceeds_30_percent():
    monitor = RealtimeRiskMonitor()

    risk = {
        "var_95": 0.01,
        "var_99": 0.02,
        "max_drawdown": 0.305,  # 30.5% -> EMERGENCY
        "volatility": 0.18,
        "beta": 1.0,
        "correlation": 0.2,
        "risk_level": "MEDIUM",
    }

    monitor.update_risk_data(
        symbol="7203",
        current_price=2000.0,
        position_size=0.05,
        risk_metrics=risk,
        market_data=None,
    )

    alerts = monitor.get_risk_alerts(symbol="7203")
    assert any(a.alert_level == AlertLevel.EMERGENCY for a in alerts)
    assert any(a.event_type == RiskEvent.EMERGENCY_DRAWDOWN for a in alerts)


