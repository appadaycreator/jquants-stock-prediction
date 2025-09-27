#!/usr/bin/env python3
"""
高頻度取引システム実行スクリプト
High Frequency Trading System Runner
"""

import sys
import os
import yaml
import argparse
import logging
import signal
import time
from datetime import datetime
from typing import Dict, Any

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from high_frequency_trading import HighFrequencyTrading, MockDataSource


class HFTRunner:
    """高頻度取引システム実行クラス"""
    
    def __init__(self, config_path: str = "hft_config.yaml"):
        """
        初期化
        
        Args:
            config_path: 設定ファイルのパス
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.hft = None
        self.data_source = None
        self.is_running = False
        
        # シグナルハンドラー設定
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # ログ設定
        self._setup_logging()
    
    def _load_config(self) -> Dict[str, Any]:
        """設定ファイルを読み込み"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config
        except FileNotFoundError:
            print(f"設定ファイルが見つかりません: {self.config_path}")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"設定ファイルの解析エラー: {e}")
            sys.exit(1)
    
    def _setup_logging(self):
        """ログ設定"""
        log_config = self.config.get('logging', {})
        
        # ログレベル設定
        level = getattr(logging, log_config.get('level', 'INFO').upper())
        
        # ログフォーマット設定
        format_str = log_config.get('format', 
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # ログファイル設定
        log_file = log_config.get('file', 'logs/hft.log')
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # ログ設定
        logging.basicConfig(
            level=level,
            format=format_str,
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("ログ設定を完了しました")
    
    def _signal_handler(self, signum, frame):
        """シグナルハンドラー"""
        self.logger.info(f"シグナル {signum} を受信しました。システムを停止します...")
        self.stop()
    
    def initialize(self):
        """システム初期化"""
        try:
            # 高頻度取引システム初期化
            hft_config = {
                'latency_threshold': self.config.get('latency', {}).get('threshold', 0.001),
                'profit_threshold': self.config.get('profit', {}).get('threshold', 0.001),
                'max_position_size': self.config.get('risk', {}).get('max_position_size', 1000000),
                'risk_limit': self.config.get('risk', {}).get('risk_limit', 0.02)
            }
            
            self.hft = HighFrequencyTrading(hft_config)
            
            # データソース初期化
            self.data_source = MockDataSource()
            
            self.logger.info("高頻度取引システムを初期化しました")
            return True
            
        except Exception as e:
            self.logger.error(f"システム初期化エラー: {e}")
            return False
    
    def start(self):
        """システム開始"""
        if not self.initialize():
            return False
        
        try:
            self.is_running = True
            self.logger.info("高頻度取引システムを開始しました")
            
            # 市場データフィード開始
            self.hft.start_market_data_feed(self.data_source)
            
            # メインループ
            self._main_loop()
            
        except Exception as e:
            self.logger.error(f"システム実行エラー: {e}")
            return False
        finally:
            self.stop()
    
    def _main_loop(self):
        """メインループ"""
        iteration = 0
        start_time = time.time()
        
        while self.is_running:
            try:
                iteration += 1
                loop_start = time.time()
                
                # 価格差データを取得
                price_differences = self.data_source.get_latest_data()
                
                if price_differences:
                    # 裁定取引を実行
                    trades = self.hft.execute_arbitrage(price_differences)
                    
                    if trades:
                        self.logger.info(f"取引実行: {len(trades)}件")
                
                # パフォーマンス監視
                if iteration % 100 == 0:
                    self._log_performance_metrics()
                
                # 実行時間調整
                loop_time = time.time() - loop_start
                sleep_time = max(0, 0.001 - loop_time)  # 1ms間隔
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
                # 実行時間チェック
                if loop_time > self.config.get('latency', {}).get('threshold', 0.001):
                    self.logger.warning(f"ループ実行時間が閾値を超過: {loop_time:.4f}s")
                
            except KeyboardInterrupt:
                self.logger.info("キーボード割り込みを受信しました")
                break
            except Exception as e:
                self.logger.error(f"メインループエラー: {e}")
                time.sleep(0.1)  # エラー時の待機時間
    
    def _log_performance_metrics(self):
        """パフォーマンス指標をログ出力"""
        metrics = self.hft.get_performance_metrics()
        
        self.logger.info("=== パフォーマンス指標 ===")
        self.logger.info(f"総取引数: {metrics.get('total_trades', 0)}")
        self.logger.info(f"損益: {metrics.get('profit_loss', 0):.2f}")
        
        if 'avg_execution_time' in metrics:
            self.logger.info(f"平均実行時間: {metrics['avg_execution_time']:.4f}s")
        if 'max_execution_time' in metrics:
            self.logger.info(f"最大実行時間: {metrics['max_execution_time']:.4f}s")
        if 'min_execution_time' in metrics:
            self.logger.info(f"最小実行時間: {metrics['min_execution_time']:.4f}s")
    
    def stop(self):
        """システム停止"""
        if self.hft:
            self.hft.cleanup()
        
        self.is_running = False
        self.logger.info("高頻度取引システムを停止しました")


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='高頻度取引システム実行スクリプト')
    parser.add_argument('--config', '-c', default='hft_config.yaml',
                       help='設定ファイルのパス (デフォルト: hft_config.yaml)')
    parser.add_argument('--test', '-t', action='store_true',
                       help='テストモードで実行')
    parser.add_argument('--simulation', '-s', action='store_true',
                       help='シミュレーションモードで実行')
    
    args = parser.parse_args()
    
    # 設定ファイルの存在確認
    if not os.path.exists(args.config):
        print(f"設定ファイルが見つかりません: {args.config}")
        sys.exit(1)
    
    # 実行モード設定
    if args.test:
        print("テストモードで実行します...")
        # テスト用の設定を適用
        os.environ['HFT_TEST_MODE'] = 'true'
    elif args.simulation:
        print("シミュレーションモードで実行します...")
        # シミュレーション用の設定を適用
        os.environ['HFT_SIMULATION_MODE'] = 'true'
    
    # システム実行
    runner = HFTRunner(args.config)
    
    try:
        success = runner.start()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nシステムを停止します...")
    except Exception as e:
        print(f"予期しないエラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
