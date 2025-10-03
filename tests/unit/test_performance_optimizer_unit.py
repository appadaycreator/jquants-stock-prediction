from core.performance_optimizer import PerformanceOptimizer


class DummyLogger:
    def __init__(self):
        self.messages = []

    def log_info(self, msg):
        self.messages.append(("info", msg))

    def log_warning(self, msg):
        self.messages.append(("warn", msg))

    def log_error(self, msg):
        self.messages.append(("error", msg))


def test_collect_and_summary():
    po = PerformanceOptimizer(logger=DummyLogger())
    m = po.collect_system_metrics()
    assert "cpu_percent" in m
    po.metrics_history.append({"cpu_percent": 50.0, "memory_percent": 60.0, "disk_percent": 70.0})
    summary = po.get_performance_summary()
    assert summary["average_cpu"] >= 0
    assert summary["total_metrics"] >= 1


def test_issue_detection_and_auto_optimize():
    logger = DummyLogger()
    po = PerformanceOptimizer(logger=logger)
    metrics = {"cpu_percent": 95.0, "memory_percent": 10.0, "disk_percent": 10.0}
    po._detect_performance_issues(metrics)
    # 高CPUの警告情報が何らかログに残る
    assert any("警告" in msg for lvl, msg in logger.messages)


def test_reset_metrics_and_recommendations():
    logger = DummyLogger()
    po = PerformanceOptimizer(logger=logger)
    po.metrics_history.append({"cpu_percent": 85.0, "memory_percent": 10.0, "disk_percent": 10.0})
    recs = po.get_optimization_recommendations()
    assert isinstance(recs, list)
    po.reset_metrics()
    assert po.get_performance_summary()["total_metrics"] == 0


