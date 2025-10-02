"""
テスト用のセットアップファイル
ログディレクトリの作成とテスト環境の初期化
"""

import os
import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """テスト環境のセットアップ"""
    # ログディレクトリの作成
    os.makedirs("logs", exist_ok=True)
    
    # テスト用の一時ディレクトリの作成
    test_dir = tempfile.mkdtemp()
    os.environ["TEST_DIR"] = test_dir
    
    yield
    
    # テスト後のクリーンアップ
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)


@pytest.fixture(autouse=True)
def ensure_logs_directory():
    """各テスト実行前にログディレクトリを確実に作成"""
    os.makedirs("logs", exist_ok=True)
    yield
    # テスト後のクリーンアップは行わない（他のテストで使用される可能性があるため）


@pytest.fixture
def temp_log_file():
    """テスト用の一時ログファイル"""
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
        temp_log_path = f.name
    
    yield temp_log_path
    
    # テスト後のクリーンアップ
    if os.path.exists(temp_log_path):
        os.unlink(temp_log_path)