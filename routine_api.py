#!/usr/bin/env python3
"""
5分ルーティン API サーバ（リファクタリング版）

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
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
import logging

from flask import Flask, jsonify, request


class JobStatus(Enum):
    """ジョブステータス列挙型"""
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class JobRecord:
    """ジョブ記録クラス（リファクタリング版）"""
    
    def __init__(self, job_id: str, client_token: Optional[str] = None):
        """
        ジョブ記録の初期化
        
        Args:
            job_id: ジョブID
            client_token: クライアントトークン
        """
        now = int(time.time() * 1000)
        self.id = job_id
        self.status: JobStatus = JobStatus.QUEUED
        self.progress: int = 0
        self.created_at: int = now
        self.updated_at: int = now
        self.client_token: Optional[str] = client_token
        self.error: Optional[str] = None
        self.result_url: Optional[str] = None
        self.steps_completed: List[str] = []

    def to_dict(self) -> Dict[str, Any]:
        """辞書形式での出力"""
        return {
            "id": self.id,
            "status": self.status.value,
            "progress": self.progress,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "resultUrl": self.result_url,
            "error": self.error,
            "stepsCompleted": self.steps_completed,
        }
    
    def update_status(self, status: JobStatus, progress: Optional[int] = None, 
                     error: Optional[str] = None, result_url: Optional[str] = None) -> None:
        """ステータスの更新"""
        self.status = status
        if progress is not None:
            self.progress = progress
        if error is not None:
            self.error = error
        if result_url is not None:
            self.result_url = result_url
        self.updated_at = int(time.time() * 1000)
    
    def add_completed_step(self, step_name: str) -> None:
        """完了したステップの追加"""
        if step_name not in self.steps_completed:
            self.steps_completed.append(step_name)


class JobManager:
    """ジョブ管理クラス（リファクタリング版）"""
    
    def __init__(self):
        """初期化"""
        self._jobs: Dict[str, JobRecord] = {}
        self._client_to_job: Dict[str, str] = {}
        self._lock = threading.Lock()
        self._logger = logging.getLogger(__name__)
    
    def create_job(self, client_token: Optional[str] = None) -> JobRecord:
        """新しいジョブの作成"""
        job_id = f"job_{int(time.time()*1000)}_{uuid.uuid4().hex[:6]}"
        job = JobRecord(job_id, client_token)
        
        with self._lock:
            self._jobs[job_id] = job
            if client_token:
                self._client_to_job[client_token] = job_id
        
        return job
    
    def get_job(self, job_id: str) -> Optional[JobRecord]:
        """ジョブの取得"""
        with self._lock:
            return self._jobs.get(job_id)
    
    def get_job_by_client_token(self, client_token: str) -> Optional[JobRecord]:
        """クライアントトークンによるジョブの取得"""
        with self._lock:
            job_id = self._client_to_job.get(client_token)
            return self._jobs.get(job_id) if job_id else None
    
    def update_job(self, job_id: str, **kwargs) -> bool:
        """ジョブの更新"""
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return False
            
            for key, value in kwargs.items():
                if hasattr(job, key):
                    setattr(job, key, value)
            job.updated_at = int(time.time() * 1000)
            return True


class PipelineExecutor:
    """パイプライン実行クラス（リファクタリング版）"""
    
    def __init__(self, job_manager: JobManager):
        """初期化"""
        self.job_manager = job_manager
        self.logger = logging.getLogger(__name__)
    
    def run_today_pipeline(self, job_id: str) -> None:
        """今日のルーティンパイプラインの実行"""
        steps = [
            ("データ取得", 10, "fetch"),
            ("前処理", 30, "preprocess"),
            ("予測", 55, "predict"),
            ("シグナル", 70, "signals"),
            ("推奨", 85, "recommend"),
            ("実行記録", 95, "record"),
        ]

        # ジョブの開始
        if not self.job_manager.update_job(job_id, status=JobStatus.RUNNING, progress=5):
            self.logger.error(f"ジョブ {job_id} が見つかりません")
            return

        try:
            # 段階実行
            for step_name, progress, step_key in steps:
                self._execute_step(step_name, step_key)
                self._update_progress(job_id, progress, step_name)

            # 完了
            date_str = datetime.now().strftime("%Y%m%d")
            self.job_manager.update_job(
                job_id,
                status=JobStatus.SUCCEEDED,
                progress=100,
                result_url=f"/data/{date_str}/dashboard_summary.json",
            )
            self.logger.info(f"ジョブ {job_id} が正常に完了しました")
            
        except Exception as e:
            self.logger.error(f"ジョブ {job_id} の実行中にエラーが発生: {str(e)}")
            self.job_manager.update_job(
                job_id,
                status=JobStatus.FAILED,
                error=str(e)
            )
    
    def _execute_step(self, step_name: str, step_key: str) -> None:
        """ステップの実行"""
        self.logger.info(f"ステップ実行: {step_name}")
        self._run_subprocess(step_key)
    
    def _update_progress(self, job_id: str, progress: int, step_name: str) -> None:
        """進捗の更新"""
        job = self.job_manager.get_job(job_id)
        if job:
            job.update_status(JobStatus.RUNNING, progress=min(99, progress))
            job.add_completed_step(step_name)
    
    def _run_subprocess(self, step: str) -> None:
        """
        既存のPythonスクリプトを呼び出すためのプレースホルダ。
        ここでは短いスリープで疑似進行。必要に応じて個別スクリプト実行へ置換可能。
        """
        time.sleep(0.4)


# グローバルインスタンス
app = Flask(__name__)
job_manager = JobManager()
pipeline_executor = PipelineExecutor(job_manager)


@app.post("/routine/run-today")
def run_today():
    """今日のルーティン実行エンドポイント"""
    try:
        data = request.get_json(silent=True) or {}
        client_token: Optional[str] = data.get("client_token")

        # 既存のジョブをチェック
        if client_token:
            existing_job = job_manager.get_job_by_client_token(client_token)
            if existing_job:
                return jsonify({"job_id": existing_job.id})

        # 新しいジョブの作成
        job = job_manager.create_job(client_token)
        
        # バックグラウンドでパイプライン実行
        thread = threading.Thread(
            target=pipeline_executor.run_today_pipeline, 
            args=(job.id,), 
            daemon=True
        )
        thread.start()

        return jsonify({"job_id": job.id})
        
    except Exception as e:
        return jsonify({"error": f"ジョブ作成エラー: {str(e)}"}), 500


@app.get("/routine/jobs/<job_id>")
def get_job(job_id: str):
    """ジョブ状態取得エンドポイント"""
    try:
        job = job_manager.get_job(job_id)
        if not job:
            return jsonify({"error": "ジョブが見つかりません"}), 404
        return jsonify(job.to_dict())
        
    except Exception as e:
        return jsonify({"error": f"ジョブ取得エラー: {str(e)}"}), 500


@app.get("/routine/health")
def health_check():
    """ヘルスチェックエンドポイント"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_jobs": len(job_manager._jobs)
    })


if __name__ == "__main__":
    port = int(os.getenv("ROUTINE_API_PORT", "5057"))
    app.run(host="0.0.0.0", port=port)
