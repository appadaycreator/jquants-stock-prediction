#!/usr/bin/env python3
"""
5分ルーティン API サーバ

エンドポイント:
- POST /routine/run-today: 今日のルーティンを順次実行（データ取得→前処理→予測→シグナル→推奨→実行記録→完了）
- GET  /routine/jobs/<job_id>: ジョブの進捗・状態を返却

静的ホスティングと両立できるよう、Web表示用JSONの生成は既存スクリプトに委譲。
「途中中断→再開」に備え、サーバ起動中はインメモリで状態管理する。
"""

from __future__ import annotations

import os
import threading
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from flask import Flask, jsonify, request

from automated_scheduler import AutomatedScheduler


JobStatus = str  # 'queued' | 'running' | 'succeeded' | 'failed'


class JobRecord:
    def __init__(self, job_id: str, client_token: Optional[str] = None):
        now = int(time.time() * 1000)
        self.id = job_id
        self.status: JobStatus = "queued"
        self.progress: int = 0
        self.created_at: int = now
        self.updated_at: int = now
        self.client_token: Optional[str] = client_token
        self.error: Optional[str] = None
        self.result_url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "status": self.status,
            "progress": self.progress,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "resultUrl": self.result_url,
            "error": self.error,
        }


app = Flask(__name__)

_jobs: Dict[str, JobRecord] = {}
_client_to_job: Dict[str, str] = {}
_lock = threading.Lock()


def _update(job: JobRecord, **patch: Any) -> None:
    for k, v in patch.items():
        setattr(job, k, v)
    job.updated_at = int(time.time() * 1000)


def _run_today_pipeline(job_id: str) -> None:
    scheduler = AutomatedScheduler()

    steps = [
        ("データ取得", 10, lambda: _run_subprocess("fetch")),
        ("前処理", 30, lambda: _run_subprocess("preprocess")),
        ("予測", 55, lambda: _run_subprocess("predict")),
        ("シグナル", 70, lambda: _run_subprocess("signals")),
        ("推奨", 85, lambda: _run_subprocess("recommend")),
        ("実行記録", 95, lambda: _run_subprocess("record")),
    ]

    with _lock:
        job = _jobs.get(job_id)
        if not job:
            return
        _update(job, status="running", progress=5)

    try:
        # 既存の超高速分析（webデータ生成まで含む）を先行実行
        # これにより静的サイト用JSONが生成される
        result = scheduler.run_ultra_fast_analysis()
        if result.get("status") != "success":
            raise RuntimeError(result.get("error") or "ultra_fast 分析失敗")
        _bump_progress(job_id, 8)

        # 段階実行（疑似ステップ）。実処理は既存スクリプト群に委譲。
        for _, prog, fn in steps:
            fn()
            _set_progress(job_id, prog)

        # 完了
        date_str = datetime.now().strftime("%Y%m%d")
        with _lock:
            job = _jobs.get(job_id)
            if job:
                _update(
                    job,
                    status="succeeded",
                    progress=100,
                    result_url=f"/data/{date_str}/dashboard_summary.json",
                )
    except Exception as e:
        with _lock:
            job = _jobs.get(job_id)
            if job:
                _update(job, status="failed", error=str(e))


def _bump_progress(job_id: str, inc: int) -> None:
    with _lock:
        job = _jobs.get(job_id)
        if job:
            _update(job, progress=min(95, job.progress + inc))


def _set_progress(job_id: str, value: int) -> None:
    with _lock:
        job = _jobs.get(job_id)
        if job:
            _update(job, progress=min(99, value))


def _run_subprocess(step: str) -> None:
    """
    既存のPythonスクリプトを呼び出すためのプレースホルダ。
    ここでは短いスリープで疑似進行。必要に応じて個別スクリプト実行へ置換可能。
    """
    time.sleep(0.4)


@app.post("/routine/run-today")
def run_today():
    data = request.get_json(silent=True) or {}
    client_token: Optional[str] = data.get("client_token")

    with _lock:
        if client_token and client_token in _client_to_job:
            job_id = _client_to_job[client_token]
            return jsonify({"job_id": job_id})

        job_id = f"job_{int(time.time()*1000)}_{uuid.uuid4().hex[:6]}"
        job = JobRecord(job_id, client_token)
        _jobs[job_id] = job
        if client_token:
            _client_to_job[client_token] = job_id

    t = threading.Thread(target=_run_today_pipeline, args=(job_id,), daemon=True)
    t.start()

    return jsonify({"job_id": job_id})


@app.get("/routine/jobs/<job_id>")
def get_job(job_id: str):
    with _lock:
        job = _jobs.get(job_id)
        if not job:
            return jsonify({"error": "Not Found"}), 404
        return jsonify(job.to_dict())


if __name__ == "__main__":
    port = int(os.getenv("ROUTINE_API_PORT", "5057"))
    app.run(host="0.0.0.0", port=port)
