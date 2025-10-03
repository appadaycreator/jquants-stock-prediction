#!/usr/bin/env python3
"""
routine_api.pyの正しいテスト
"""

import pytest
import time
from datetime import datetime
from routine_api import JobRecord


class TestRoutineAPICorrect:
    """ルーティンAPIの正しいテストクラス"""

    def test_job_record_creation(self):
        """ジョブレコードの作成テスト"""
        job_id = "test-job-123"
        job_record = JobRecord(job_id=job_id)
        
        assert job_record.id == job_id
        assert job_record.status == "queued"
        assert job_record.progress == 0
        assert job_record.client_token is None
        assert job_record.error is None
        assert job_record.result_url is None

    def test_job_record_with_client_token(self):
        """クライアントトークン付きジョブレコードのテスト"""
        job_id = "test-job-123"
        client_token = "client-token-456"
        job_record = JobRecord(job_id=job_id, client_token=client_token)
        
        assert job_record.id == job_id
        assert job_record.client_token == client_token
        assert job_record.status == "queued"

    def test_job_record_status_update(self):
        """ジョブレコードのステータス更新テスト"""
        job_id = "test-job-123"
        job_record = JobRecord(job_id=job_id)
        
        # ステータス更新
        job_record.status = "running"
        job_record.progress = 50
        
        assert job_record.status == "running"
        assert job_record.progress == 50

    def test_job_record_created_at(self):
        """ジョブレコードの作成時刻テスト"""
        job_id = "test-job-123"
        job_record = JobRecord(job_id=job_id)
        
        # 作成時刻が現在時刻に近いことを確認
        current_time = int(time.time() * 1000)
        assert abs(job_record.created_at - current_time) < 1000  # 1秒以内

    def test_job_record_to_dict(self):
        """ジョブレコードの辞書変換テスト"""
        job_id = "test-job-123"
        client_token = "client-token-456"
        job_record = JobRecord(job_id=job_id, client_token=client_token)
        
        result_dict = job_record.to_dict()
        
        assert result_dict["id"] == job_id
        assert result_dict["status"] == "queued"
        assert result_dict["progress"] == 0
        assert result_dict["resultUrl"] is None
        assert result_dict["error"] is None
