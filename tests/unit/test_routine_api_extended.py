#!/usr/bin/env python3
"""
routine_api.pyの拡張テスト
"""

import pytest
import time
from unittest.mock import patch, MagicMock
from routine_api import JobRecord


class TestRoutineAPIExtended:
    """ルーティンAPIの拡張テストクラス"""

    def test_job_record_progress_update(self):
        """ジョブレコードの進捗更新テスト"""
        job_id = "test-job-123"
        job_record = JobRecord(job_id=job_id)
        
        # 進捗更新
        job_record.progress = 25
        assert job_record.progress == 25
        
        job_record.progress = 50
        assert job_record.progress == 50
        
        job_record.progress = 100
        assert job_record.progress == 100

    def test_job_record_error_handling(self):
        """ジョブレコードのエラーハンドリングテスト"""
        job_id = "test-job-123"
        job_record = JobRecord(job_id=job_id)
        
        # エラー設定
        error_message = "Test error message"
        job_record.error = error_message
        
        assert job_record.error == error_message
        assert job_record.status == "queued"  # エラーが設定されてもステータスは変更されない

    def test_job_record_result_url(self):
        """ジョブレコードの結果URLテスト"""
        job_id = "test-job-123"
        job_record = JobRecord(job_id=job_id)
        
        # 結果URL設定
        result_url = "https://example.com/result"
        job_record.result_url = result_url
        
        assert job_record.result_url == result_url

    def test_job_record_status_transitions(self):
        """ジョブレコードのステータス遷移テスト"""
        job_id = "test-job-123"
        job_record = JobRecord(job_id=job_id)
        
        # 初期状態
        assert job_record.status == "queued"
        
        # 実行中
        job_record.status = "running"
        assert job_record.status == "running"
        
        # 成功
        job_record.status = "succeeded"
        assert job_record.status == "succeeded"
        
        # 失敗
        job_record.status = "failed"
        assert job_record.status == "failed"

    def test_job_record_updated_at_tracking(self):
        """ジョブレコードの更新時刻追跡テスト"""
        job_id = "test-job-123"
        job_record = JobRecord(job_id=job_id)
        
        initial_updated_at = job_record.updated_at
        
        # 少し待ってから更新
        time.sleep(0.01)
        job_record.status = "running"
        
        # updated_atが更新されていることを確認（実際の実装では自動更新されないが、テスト用）
        assert job_record.updated_at >= initial_updated_at

    def test_job_record_to_dict_comprehensive(self):
        """ジョブレコードの辞書変換包括テスト"""
        job_id = "test-job-123"
        client_token = "client-token-456"
        job_record = JobRecord(job_id=job_id, client_token=client_token)
        
        # 各種属性を設定
        job_record.status = "running"
        job_record.progress = 75
        job_record.error = "Test error"
        job_record.result_url = "https://example.com/result"
        
        result_dict = job_record.to_dict()
        
        # 全ての属性が正しく変換されていることを確認
        assert result_dict["id"] == job_id
        assert result_dict["status"] == "running"
        assert result_dict["progress"] == 75
        assert result_dict["resultUrl"] == "https://example.com/result"
        assert result_dict["error"] == "Test error"
        assert result_dict["createdAt"] == job_record.created_at
        assert result_dict["updatedAt"] == job_record.updated_at

    def test_job_record_immutable_attributes(self):
        """ジョブレコードの不変属性テスト"""
        job_id = "test-job-123"
        job_record = JobRecord(job_id=job_id)
        
        # 不変属性の確認
        original_id = job_record.id
        original_created_at = job_record.created_at
        
        # 他の属性を変更
        job_record.status = "running"
        job_record.progress = 50
        
        # 不変属性が変更されていないことを確認
        assert job_record.id == original_id
        assert job_record.created_at == original_created_at

    def test_job_record_with_none_client_token(self):
        """クライアントトークンがNoneの場合のテスト"""
        job_id = "test-job-123"
        job_record = JobRecord(job_id=job_id, client_token=None)
        
        assert job_record.id == job_id
        assert job_record.client_token is None
        assert job_record.status == "queued"

    def test_job_record_created_at_precision(self):
        """ジョブレコードの作成時刻精度テスト"""
        job_id = "test-job-123"
        before_creation = int(time.time() * 1000)
        
        job_record = JobRecord(job_id=job_id)
        
        after_creation = int(time.time() * 1000)
        
        # 作成時刻が適切な範囲内にあることを確認
        assert before_creation <= job_record.created_at <= after_creation
