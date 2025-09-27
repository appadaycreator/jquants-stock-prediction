"""
pytest設定と共通フィクスチャ
"""
import pytest
import pandas as pd
import numpy as np
import os
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture
def sample_stock_data():
    """サンプル株価データのフィクスチャ"""
    dates = pd.date_range('2023-01-01', periods=100, freq='D')
    np.random.seed(42)
    
    # ランダムウォークで株価を生成
    price = 100
    prices = [price]
    for _ in range(99):
        price += np.random.normal(0, 2)
        prices.append(max(price, 1))  # 負の価格を防ぐ
    
    data = {
        'Date': dates,
        'Open': prices,
        'High': [p * (1 + abs(np.random.normal(0, 0.02))) for p in prices],
        'Low': [p * (1 - abs(np.random.normal(0, 0.02))) for p in prices],
        'Close': prices,
        'Volume': np.random.randint(1000, 10000, 100)
    }
    
    df = pd.DataFrame(data)
    # High >= Low を保証
    df['High'] = np.maximum(df['High'], df['Low'])
    return df

@pytest.fixture
def sample_config():
    """サンプル設定のフィクスチャ"""
    return {
        'preprocessing': {
            'input_file': 'test_data.csv',
            'output_file': 'processed_test_data.csv',
            'features': ['SMA_5', 'SMA_25', 'Close_1d_ago']
        },
        'prediction': {
            'features': ['SMA_5', 'SMA_25', 'Close_1d_ago'],
            'target': 'Close',
            'test_size': 0.2,
            'random_state': 42
        }
    }

@pytest.fixture
def temp_csv_file(tmp_path, sample_stock_data):
    """一時的なCSVファイルのフィクスチャ"""
    file_path = tmp_path / "test_stock_data.csv"
    sample_stock_data.to_csv(file_path, index=False)
    return str(file_path)

@pytest.fixture(autouse=True)
def setup_test_environment():
    """テスト環境のセットアップ"""
    # テスト用のログレベルを設定
    import logging
    logging.getLogger().setLevel(logging.WARNING)
    
    # テスト用の環境変数を設定
    os.environ['TESTING'] = 'true'
    
    yield
    
    # クリーンアップ
    if 'TESTING' in os.environ:
        del os.environ['TESTING']
