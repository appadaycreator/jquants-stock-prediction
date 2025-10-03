#!/usr/bin/env python3
"""
routine_api.py のテスト（リファクタリング版）
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import time
import threading
from datetime import datetime

# テスト対象のインポート
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from routine_api import (
    JobStatus, JobRecord, JobManager, PipelineExecutor,
    app
)


class TestJobStatus(unittest.TestCase):
    """JobStatus列挙型のテスト"""
    
    def test_job_status_values(self):
        """ステータス値のテスト"""
        self.assertEqual(JobStatus.QUEUED.value, "queued")
        self.assertEqual(JobStatus.RUNNING.value, "running")
        self.assertEqual(JobStatus.SUCCEEDED.value, "succeeded")
        self.assertEqual(JobStatus.FAILED.value, "failed")


class TestJobRecord(unittest.TestCase):
    """JobRecordクラスのテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.job_id = "test_job_123"
        self.client_token = "test_token_456"
    
    def test_job_record_initialization(self):
        """ジョブ記録の初期化テスト"""
        job = JobRecord(self.job_id, self.client_token)
        
        self.assertEqual(job.id, self.job_id)
        self.assertEqual(job.status, JobStatus.QUEUED)
        self.assertEqual(job.progress, 0)
        self.assertEqual(job.client_token, self.client_token)
        self.assertIsNone(job.error)
        self.assertIsNone(job.result_url)
        self.assertEqual(len(job.steps_completed), 0)
    
    def test_job_record_initialization_without_token(self):
        """トークンなしでのジョブ記録初期化テスト"""
        job = JobRecord(self.job_id)
        
        self.assertEqual(job.id, self.job_id)
        self.assertIsNone(job.client_token)
    
    def test_to_dict(self):
        """辞書形式出力のテスト"""
        job = JobRecord(self.job_id, self.client_token)
        result = job.to_dict()
        
        self.assertEqual(result["id"], self.job_id)
        self.assertEqual(result["status"], "queued")
        self.assertEqual(result["progress"], 0)
        self.assertEqual(result["error"], None)
        self.assertEqual(result["resultUrl"], None)
        self.assertEqual(result["stepsCompleted"], [])
    
    def test_update_status(self):
        """ステータス更新のテスト"""
        job = JobRecord(self.job_id)
        
        # ステータスとプログレスの更新
        job.update_status(JobStatus.RUNNING, progress=50)
        self.assertEqual(job.status, JobStatus.RUNNING)
        self.assertEqual(job.progress, 50)
        
        # エラーの設定
        job.update_status(JobStatus.FAILED, error="テストエラー")
        self.assertEqual(job.status, JobStatus.FAILED)
        self.assertEqual(job.error, "テストエラー")
        
        # 結果URLの設定
        job.update_status(JobStatus.SUCCEEDED, result_url="/test/result.json")
        self.assertEqual(job.status, JobStatus.SUCCEEDED)
        self.assertEqual(job.result_url, "/test/result.json")
    
    def test_add_completed_step(self):
        """完了ステップ追加のテスト"""
        job = JobRecord(self.job_id)
        
        # ステップの追加
        job.add_completed_step("データ取得")
        self.assertIn("データ取得", job.steps_completed)
        
        # 重複追加の防止
        job.add_completed_step("データ取得")
        self.assertEqual(job.steps_completed.count("データ取得"), 1)
        
        # 複数ステップの追加
        job.add_completed_step("前処理")
        self.assertEqual(len(job.steps_completed), 2)
        self.assertIn("前処理", job.steps_completed)


class TestJobManager(unittest.TestCase):
    """JobManagerクラスのテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.job_manager = JobManager()
    
    def test_create_job(self):
        """ジョブ作成のテスト"""
        client_token = "test_token"
        job = self.job_manager.create_job(client_token)
        
        self.assertIsInstance(job, JobRecord)
        self.assertEqual(job.client_token, client_token)
        self.assertEqual(job.status, JobStatus.QUEUED)
    
    def test_create_job_without_token(self):
        """トークンなしでのジョブ作成テスト"""
        job = self.job_manager.create_job()
        
        self.assertIsInstance(job, JobRecord)
        self.assertIsNone(job.client_token)
    
    def test_get_job(self):
        """ジョブ取得のテスト"""
        job = self.job_manager.create_job("test_token")
        retrieved_job = self.job_manager.get_job(job.id)
        
        self.assertEqual(retrieved_job.id, job.id)
        self.assertEqual(retrieved_job.client_token, "test_token")
    
    def test_get_nonexistent_job(self):
        """存在しないジョブの取得テスト"""
        result = self.job_manager.get_job("nonexistent_id")
        self.assertIsNone(result)
    
    def test_get_job_by_client_token(self):
        """クライアントトークンによるジョブ取得のテスト"""
        client_token = "test_token"
        job = self.job_manager.create_job(client_token)
        retrieved_job = self.job_manager.get_job_by_client_token(client_token)
        
        self.assertEqual(retrieved_job.id, job.id)
        self.assertEqual(retrieved_job.client_token, client_token)
    
    def test_get_job_by_nonexistent_token(self):
        """存在しないトークンでのジョブ取得テスト"""
        result = self.job_manager.get_job_by_client_token("nonexistent_token")
        self.assertIsNone(result)
    
    def test_update_job(self):
        """ジョブ更新のテスト"""
        job = self.job_manager.create_job()
        
        # ステータスの更新
        result = self.job_manager.update_job(job.id, status=JobStatus.RUNNING, progress=50)
        self.assertTrue(result)
        
        updated_job = self.job_manager.get_job(job.id)
        self.assertEqual(updated_job.status, JobStatus.RUNNING)
        self.assertEqual(updated_job.progress, 50)
    
    def test_update_nonexistent_job(self):
        """存在しないジョブの更新テスト"""
        result = self.job_manager.update_job("nonexistent_id", status=JobStatus.RUNNING)
        self.assertFalse(result)


class TestPipelineExecutor(unittest.TestCase):
    """PipelineExecutorクラスのテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.job_manager = JobManager()
        self.pipeline_executor = PipelineExecutor(self.job_manager)
    
    @patch('time.sleep')
    def test_run_today_pipeline_success(self, mock_sleep):
        """パイプライン成功実行のテスト"""
        job = self.job_manager.create_job("test_token")
        
        # パイプライン実行
        self.pipeline_executor.run_today_pipeline(job.id)
        
        # 結果の確認
        updated_job = self.job_manager.get_job(job.id)
        self.assertEqual(updated_job.status, JobStatus.SUCCEEDED)
        self.assertEqual(updated_job.progress, 100)
        self.assertIsNotNone(updated_job.result_url)
        self.assertEqual(len(updated_job.steps_completed), 6)
    
    @patch('time.sleep')
    def test_run_today_pipeline_failure(self, mock_sleep):
        """パイプライン失敗実行のテスト"""
        job = self.job_manager.create_job("test_token")
        
        # エラーを発生させる
        with patch.object(self.pipeline_executor, '_execute_step', side_effect=Exception("テストエラー")):
            self.pipeline_executor.run_today_pipeline(job.id)
        
        # 結果の確認
        updated_job = self.job_manager.get_job(job.id)
        self.assertEqual(updated_job.status, JobStatus.FAILED)
        self.assertIsNotNone(updated_job.error)
        self.assertIn("テストエラー", updated_job.error)
    
    def test_run_today_pipeline_nonexistent_job(self):
        """存在しないジョブでのパイプライン実行テスト"""
        # 存在しないジョブIDで実行
        self.pipeline_executor.run_today_pipeline("nonexistent_id")
        # エラーが発生しないことを確認（ログ出力のみ）
    
    @patch('time.sleep')
    def test_execute_step(self, mock_sleep):
        """ステップ実行のテスト"""
        with patch.object(self.pipeline_executor, '_run_subprocess') as mock_run:
            self.pipeline_executor._execute_step("テストステップ", "test_step")
            mock_run.assert_called_once_with("test_step")
    
    def test_update_progress(self):
        """進捗更新のテスト"""
        job = self.job_manager.create_job()
        
        self.pipeline_executor._update_progress(job.id, 50, "テストステップ")
        
        updated_job = self.job_manager.get_job(job.id)
        self.assertEqual(updated_job.progress, 50)
        self.assertIn("テストステップ", updated_job.steps_completed)
    
    def test_update_progress_max_value(self):
        """進捗最大値制限のテスト"""
        job = self.job_manager.create_job()
        
        # 99を超える値を設定
        self.pipeline_executor._update_progress(job.id, 150, "テストステップ")
        
        updated_job = self.job_manager.get_job(job.id)
        self.assertEqual(updated_job.progress, 99)  # 99に制限される
    
    @patch('time.sleep')
    def test_run_subprocess(self, mock_sleep):
        """サブプロセス実行のテスト"""
        self.pipeline_executor._run_subprocess("test_step")
        mock_sleep.assert_called_once_with(0.4)


class TestFlaskEndpoints(unittest.TestCase):
    """Flaskエンドポイントのテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_run_today_endpoint(self):
        """今日のルーティン実行エンドポイントのテスト"""
        response = self.client.post('/routine/run-today', json={'client_token': 'test_token'})
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('job_id', data)
        self.assertIsInstance(data['job_id'], str)
    
    def test_run_today_endpoint_without_token(self):
        """トークンなしでのルーティン実行テスト"""
        response = self.client.post('/routine/run-today')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('job_id', data)
    
    def test_run_today_endpoint_duplicate_token(self):
        """重複トークンでのルーティン実行テスト"""
        # 最初のリクエスト
        response1 = self.client.post('/routine/run-today', json={'client_token': 'duplicate_token'})
        self.assertEqual(response1.status_code, 200)
        job_id1 = response1.get_json()['job_id']
        
        # 同じトークンでの2回目のリクエスト
        response2 = self.client.post('/routine/run-today', json={'client_token': 'duplicate_token'})
        self.assertEqual(response2.status_code, 200)
        job_id2 = response2.get_json()['job_id']
        
        # 同じジョブIDが返されることを確認
        self.assertEqual(job_id1, job_id2)
    
    def test_get_job_endpoint(self):
        """ジョブ取得エンドポイントのテスト"""
        # ジョブの作成
        create_response = self.client.post('/routine/run-today', json={'client_token': 'test_token'})
        job_id = create_response.get_json()['job_id']
        
        # ジョブの取得
        response = self.client.get(f'/routine/jobs/{job_id}')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['id'], job_id)
        # ジョブは作成後すぐに実行されるため、queuedまたはrunningの状態になる
        self.assertIn(data['status'], ['queued', 'running'])
    
    def test_get_nonexistent_job_endpoint(self):
        """存在しないジョブ取得のテスト"""
        response = self.client.get('/routine/jobs/nonexistent_id')
        
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertIn('error', data)
    
    def test_health_check_endpoint(self):
        """ヘルスチェックエンドポイントのテスト"""
        response = self.client.get('/routine/health')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('timestamp', data)
        self.assertIn('active_jobs', data)


if __name__ == '__main__':
    unittest.main()
