#!/usr/bin/env python3
"""
統合トレーディングシステムのテストスクリプト
依存関係の確認とシステムの動作テスト
"""

import sys
import importlib
import subprocess
import os
from datetime import datetime

def check_dependencies():
    """依存関係の確認"""
    print("🔍 依存関係の確認中...")
    
    required_packages = [
        'pandas', 'numpy', 'yfinance', 'requests', 
        'sklearn', 'matplotlib', 'yaml'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'sklearn':
                importlib.import_module('sklearn')
            elif package == 'yaml':
                importlib.import_module('yaml')
            else:
                importlib.import_module(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - インストールが必要")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ 不足しているパッケージ: {', '.join(missing_packages)}")
        print("以下のコマンドでインストールしてください:")
        print("pip install -r requirements.txt")
        return False
    else:
        print("\n✅ すべての依存関係がインストールされています")
        return True

def test_imports():
    """モジュールのインポートテスト"""
    print("\n🧪 モジュールインポートテスト...")
    
    try:
        # 基本モジュールのインポート
        import pandas as pd
        import numpy as np
        import yfinance as yf
        import requests
        from sklearn.ensemble import RandomForestRegressor
        import matplotlib.pyplot as plt
        import yaml
        
        print("  ✅ 基本モジュールのインポート成功")
        
        # 自作モジュールのインポートテスト
        try:
            from realtime_trading_signals import TradingSignalSystem
            print("  ✅ realtime_trading_signals インポート成功")
        except ImportError as e:
            print(f"  ❌ realtime_trading_signals インポートエラー: {e}")
        
        try:
            from risk_management_system import RiskManagementSystem
            print("  ✅ risk_management_system インポート成功")
        except ImportError as e:
            print(f"  ❌ risk_management_system インポートエラー: {e}")
        
        try:
            from multi_stock_monitor import MultiStockMonitor
            print("  ✅ multi_stock_monitor インポート成功")
        except ImportError as e:
            print(f"  ❌ multi_stock_monitor インポートエラー: {e}")
        
        try:
            from integrated_trading_system import IntegratedTradingSystem
            print("  ✅ integrated_trading_system インポート成功")
        except ImportError as e:
            print(f"  ❌ integrated_trading_system インポートエラー: {e}")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ インポートエラー: {e}")
        return False

def test_basic_functionality():
    """基本機能のテスト"""
    print("\n🔧 基本機能テスト...")
    
    try:
        # データ取得テスト
        import yfinance as yf
        ticker = yf.Ticker("7203.T")
        data = ticker.history(period="5d")
        
        if not data.empty:
            print("  ✅ 株価データ取得成功")
        else:
            print("  ❌ 株価データ取得失敗")
            return False
        
        # 技術指標計算テスト
        import pandas as pd
        import numpy as np
        
        close = data['Close']
        sma = close.rolling(window=5).mean()
        
        if not sma.empty:
            print("  ✅ 技術指標計算成功")
        else:
            print("  ❌ 技術指標計算失敗")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ 基本機能テストエラー: {e}")
        return False

def test_config_files():
    """設定ファイルのテスト"""
    print("\n📋 設定ファイルテスト...")
    
    config_files = [
        'trading_config.yaml',
        'requirements.txt'
    ]
    
    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"  ✅ {config_file} 存在")
        else:
            print(f"  ❌ {config_file} 不存在")
            return False
    
    # YAML設定ファイルの読み込みテスト
    try:
        import yaml
        with open('trading_config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        if 'symbols' in config and 'account' in config:
            print("  ✅ 設定ファイル読み込み成功")
        else:
            print("  ❌ 設定ファイル形式エラー")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ 設定ファイルテストエラー: {e}")
        return False

def run_simple_analysis():
    """簡単な分析テスト"""
    print("\n📊 簡単な分析テスト...")
    
    try:
        # サンプルデータでの分析テスト
        import pandas as pd
        import numpy as np
        from datetime import datetime, timedelta
        
        # サンプルデータ生成
        dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')
        np.random.seed(42)
        prices = 100 + np.cumsum(np.random.randn(len(dates)) * 0.02)
        
        sample_data = pd.DataFrame({
            'Date': dates,
            'Close': prices,
            'High': prices * 1.02,
            'Low': prices * 0.98,
            'Volume': np.random.randint(1000, 10000, len(dates))
        })
        
        # 簡単な技術指標計算
        sample_data['SMA_5'] = sample_data['Close'].rolling(window=5).mean()
        sample_data['SMA_20'] = sample_data['Close'].rolling(window=20).mean()
        
        # リターン計算
        sample_data['Return'] = sample_data['Close'].pct_change()
        
        print("  ✅ サンプルデータ生成成功")
        print(f"  📈 データ期間: {sample_data['Date'].min()} ～ {sample_data['Date'].max()}")
        print(f"  📊 データ件数: {len(sample_data)}件")
        print(f"  💰 価格範囲: ¥{sample_data['Close'].min():.2f} ～ ¥{sample_data['Close'].max():.2f}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 分析テストエラー: {e}")
        return False

def main():
    """メインテスト実行"""
    print("🚀 統合トレーディングシステム テスト開始")
    print("=" * 60)
    
    test_results = []
    
    # 1. 依存関係確認
    test_results.append(("依存関係確認", check_dependencies()))
    
    # 2. インポートテスト
    test_results.append(("モジュールインポート", test_imports()))
    
    # 3. 設定ファイルテスト
    test_results.append(("設定ファイル", test_config_files()))
    
    # 4. 基本機能テスト
    test_results.append(("基本機能", test_basic_functionality()))
    
    # 5. 分析テスト
    test_results.append(("分析機能", run_simple_analysis()))
    
    # 結果サマリー
    print("\n" + "=" * 60)
    print("📋 テスト結果サマリー")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 成功" if result else "❌ 失敗"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 総合結果: {passed}/{total} テスト通過")
    
    if passed == total:
        print("🎉 すべてのテストが成功しました！")
        print("\n📝 次のステップ:")
        print("1. python3 realtime_trading_signals.py  # シグナル生成テスト")
        print("2. python3 risk_management_system.py    # リスク管理テスト")
        print("3. python3 multi_stock_monitor.py      # 複数銘柄監視テスト")
        print("4. python3 integrated_trading_system.py # 統合システムテスト")
    else:
        print("⚠️ 一部のテストが失敗しました。")
        print("不足している依存関係をインストールしてください:")
        print("pip install -r requirements.txt")
    
    print("\n📚 詳細な使用方法は TRADING_SYSTEM_README.md を参照してください")

if __name__ == "__main__":
    main()
