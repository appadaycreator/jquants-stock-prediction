import time
import pytest


@pytest.fixture()
def routine_client():
    # Flask クライアントとインメモリ状態を初期化
    import routine_api as ra

    ra._jobs.clear()
    ra._client_to_job.clear()
    app = ra.app
    with app.test_client() as client:
        yield client


def _poll_job_until(client, job_id: str, expect: str, timeout_s: float = 3.0):
    deadline = time.time() + timeout_s
    last = None
    while time.time() < deadline:
        resp = client.get(f"/routine/jobs/{job_id}")
        assert resp.status_code == 200
        data = resp.get_json()
        last = data
        if data["status"] == expect:
            return data
        time.sleep(0.05)
    return last


@pytest.mark.api
def test_routine_success_fast(routine_client, monkeypatch):
    # 依存処理を高速化モック
    import routine_api as ra

    monkeypatch.setattr(ra, "_run_subprocess", lambda step: None)
    monkeypatch.setattr(
        ra.AutomatedScheduler,
        "run_ultra_fast_analysis",
        lambda self: {"status": "success"},
    )

    resp = routine_client.post("/routine/run-today", json={"client_token": "t1"})
    assert resp.status_code == 200
    job_id = resp.get_json()["job_id"]

    result = _poll_job_until(routine_client, job_id, expect="succeeded", timeout_s=2.0)
    assert result["status"] == "succeeded"
    assert result.get("resultUrl")


@pytest.mark.api
def test_routine_mid_error_fails(routine_client, monkeypatch):
    import routine_api as ra

    monkeypatch.setattr(ra, "_run_subprocess", lambda step: None)
    monkeypatch.setattr(
        ra.AutomatedScheduler,
        "run_ultra_fast_analysis",
        lambda self: {"status": "error", "error": "forced"},
    )

    resp = routine_client.post("/routine/run-today", json={"client_token": "t2"})
    assert resp.status_code == 200
    job_id = resp.get_json()["job_id"]

    result = _poll_job_until(routine_client, job_id, expect="failed", timeout_s=1.0)
    assert result["status"] == "failed"
    assert "forced" in (result.get("error") or "")


@pytest.mark.api
def test_routine_recovery_after_error_succeeds(routine_client, monkeypatch):
    import routine_api as ra

    # まず失敗させる
    monkeypatch.setattr(ra, "_run_subprocess", lambda step: None)
    monkeypatch.setattr(
        ra.AutomatedScheduler,
        "run_ultra_fast_analysis",
        lambda self: {"status": "error", "error": "first"},
    )
    resp1 = routine_client.post("/routine/run-today", json={"client_token": "t3"})
    job_id1 = resp1.get_json()["job_id"]
    failed = _poll_job_until(routine_client, job_id1, expect="failed", timeout_s=1.0)
    assert failed["status"] == "failed"

    # 復旧（次回成功）
    monkeypatch.setattr(
        ra.AutomatedScheduler,
        "run_ultra_fast_analysis",
        lambda self: {"status": "success"},
    )
    resp2 = routine_client.post("/routine/run-today", json={"client_token": "t4"})
    job_id2 = resp2.get_json()["job_id"]
    succeeded = _poll_job_until(
        routine_client, job_id2, expect="succeeded", timeout_s=2.0
    )
    assert succeeded["status"] == "succeeded"
    assert succeeded.get("resultUrl")
