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


@pytest.fixture
def temp_csv_file():
    """テスト用の一時CSVファイル"""
    import tempfile
    import pandas as pd
    
    # サンプルデータの作成
    sample_data = pd.DataFrame({
        'Date': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'Open': [100.0, 101.0, 102.0],
        'High': [105.0, 106.0, 107.0],
        'Low': [95.0, 96.0, 97.0],
        'Close': [103.0, 104.0, 105.0],
        'Volume': [1000, 1100, 1200]
    })
    
    # 一時ファイルの作成
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        sample_data.to_csv(f.name, index=False)
        temp_csv_path = f.name
    
    yield temp_csv_path
    
    # テスト後のクリーンアップ
    if os.path.exists(temp_csv_path):
        os.unlink(temp_csv_path)


@pytest.fixture
def sample_stock_data():
    """テスト用のサンプル株価データ"""
    import pandas as pd
    
    return pd.DataFrame({
        'Date': pd.date_range('2024-01-01', periods=10, freq='D'),
        'Open': [100.0, 101.0, 102.0, 103.0, 104.0, 105.0, 106.0, 107.0, 108.0, 109.0],
        'High': [105.0, 106.0, 107.0, 108.0, 109.0, 110.0, 111.0, 112.0, 113.0, 114.0],
        'Low': [95.0, 96.0, 97.0, 98.0, 99.0, 100.0, 101.0, 102.0, 103.0, 104.0],
        'Close': [103.0, 104.0, 105.0, 106.0, 107.0, 108.0, 109.0, 110.0, 111.0, 112.0],
        'Volume': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900]
    })