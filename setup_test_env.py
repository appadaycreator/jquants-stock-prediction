#!/usr/bin/env python3
"""
テスト環境セットアップスクリプト
ログディレクトリの作成とテスト環境の初期化
"""

import os
import sys
from pathlib import Path


def setup_test_environment():
    """テスト環境のセットアップ"""
    print("テスト環境をセットアップ中...")
    
    # ログディレクトリの作成
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    print(f"ログディレクトリを作成: {logs_dir.absolute()}")
    
    # テスト用のディレクトリの作成
    test_dirs = [
        "tests/temp",
        "tests/fixtures",
        "tests/data"
    ]
    
    for test_dir in test_dirs:
        Path(test_dir).mkdir(parents=True, exist_ok=True)
        print(f"テストディレクトリを作成: {test_dir}")
    
    # 環境変数の設定
    os.environ["TEST_MODE"] = "true"
    os.environ["LOG_LEVEL"] = "DEBUG"
    
    print("テスト環境のセットアップが完了しました")


if __name__ == "__main__":
    setup_test_environment()
    sys.exit(0)
