#!/usr/bin/env python3
"""
リスク管理ダッシュボード用リアルタイム更新システム
ポジション価格の更新、リスク指標の再計算、アラート生成を自動化
"""

import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging
import numpy as np
from risk_management_system import RiskManagementSystem
from generate_risk_dashboard_data import RiskDashboardDataGenerator

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RiskDashboardRealtimeUpdater:
    """リスク管理ダッシュボード用リアルタイム更新システム"""
    
    def __init__(self, account_value: float = 1000000, update_interval: int = 30):
        self.account_value = account_value
        self.update_interval = update_interval  # 秒
        self.is_running = False
        self.risk_system = RiskManagementSystem(account_value)
        self.data_generator = RiskDashboardDataGenerator(account_value)
        self.setup_sample_positions()
        
        # 価格履歴（リアルタイム更新用）
        self.price_history = {}
        self.risk_history = []
        
        # アラート履歴
        self.alert_history = []
        
        # 更新スレッド
        self.update_thread = None
    
    def setup_sample_positions(self):
        """サンプルポジションの設定"""
        # サンプルポジション追加
        self.risk_system.add_position("7203.T", 2500.0, 100, "LONG", 0.25)
        self.risk_system.add_position("6758.T", 12000.0, 50, "LONG", 0.30)
        self.risk_system.add_position("9984.T", 8000.0, 75, "LONG", 0.35)
        self.risk_system.add_position("7974.T", 15000.0, 30, "LONG", 0.20)
        self.risk_system.add_position("6861.T", 5000.0, 80, "LONG", 0.40)
        
        # 初期価格履歴の設定
        for symbol in ["7203.T", "6758.T", "9984.T", "7974.T", "6861.T"]:
            self.price_history[symbol] = []
    
    def start_realtime_updates(self):
        """リアルタイム更新を開始"""
        if self.is_running:
            logger.warning("リアルタイム更新は既に実行中です")
            return
        
        self.is_running = True
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        logger.info(f"リアルタイム更新を開始しました（間隔: {self.update_interval}秒）")
    
    def stop_realtime_updates(self):
        """リアルタイム更新を停止"""
        self.is_running = False
        if self.update_thread:
            self.update_thread.join()
        logger.info("リアルタイム更新を停止しました")
    
    def _update_loop(self):
        """更新ループ"""
        while self.is_running:
            try:
                self._update_positions()
                self._update_risk_metrics()
                self._check_alerts()
                self._save_updated_data()
                
                logger.info(f"リスク管理データを更新しました: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
            except Exception as e:
                logger.error(f"更新エラー: {e}")
            
            time.sleep(self.update_interval)
    
    def _update_positions(self):
        """ポジション価格の更新"""
        for symbol, position in self.risk_system.positions.items():
            # 価格変動シミュレーション（実際の実装ではAPIから取得）
            current_price = self._simulate_price_movement(symbol, position.current_price)
            
            # 価格更新
            self.risk_system.update_position_price(symbol, current_price)
            
            # 価格履歴に追加
            self.price_history[symbol].append({
                'timestamp': datetime.now().isoformat(),
                'price': current_price
            })
            
            # 履歴を最新100件に制限
            if len(self.price_history[symbol]) > 100:
                self.price_history[symbol] = self.price_history[symbol][-100:]
    
    def _simulate_price_movement(self, symbol: str, current_price: float) -> float:
        """価格変動のシミュレーション"""
        # 銘柄別のボラティリティ設定
        volatility_map = {
            "7203.T": 0.02,  # トヨタ: 2%
            "6758.T": 0.03,  # ソニー: 3%
            "9984.T": 0.04,  # ソフトバンク: 4%
            "7974.T": 0.025, # 任天堂: 2.5%
            "6861.T": 0.015  # キーエンス: 1.5%
        }
        
        volatility = volatility_map.get(symbol, 0.02)
        
        # ランダムウォークで価格変動をシミュレーション
        change = np.random.normal(0, volatility)
        new_price = current_price * (1 + change)
        
        # 価格が負にならないように制限
        return max(new_price, current_price * 0.5)
    
    def _update_risk_metrics(self):
        """リスク指標の更新"""
        risk_report = self.risk_system.get_risk_report()
        
        # リスク履歴に追加
        self.risk_history.append({
            'timestamp': datetime.now().isoformat(),
            'risk_score': risk_report['risk_metrics']['risk_score'],
            'portfolio_value': risk_report['risk_metrics']['portfolio_value'],
            'max_drawdown': risk_report['risk_metrics']['max_drawdown'],
            'var_95': risk_report['risk_metrics']['var_95']
        })
        
        # 履歴を最新100件に制限
        if len(self.risk_history) > 100:
            self.risk_history = self.risk_history[-100:]
    
    def _check_alerts(self):
        """アラートのチェック"""
        risk_report = self.risk_system.get_risk_report()
        
        # ポートフォリオレベルアラート
        if risk_report['should_reduce_risk']:
            self._add_alert("portfolio_risk_high", "WARNING", 
                          "ポートフォリオリスクが高すぎます", 
                          "リスクスコアが閾値を超えています。ポジションサイズの縮小を検討してください。",
                          "HIGH")
        
        if risk_report['risk_metrics']['max_drawdown'] > 0.15:
            self._add_alert("max_drawdown_high", "WARNING",
                          "最大ドローダウンが15%を超えています",
                          "損失が拡大しています。損切りを厳格に実行してください。",
                          "HIGH")
        
        # 個別ポジションアラート
        for symbol, position in self.risk_system.positions.items():
            if position.risk_score > 0.8:
                self._add_alert(f"position_risk_{symbol}", "WARNING",
                              f"{symbol}のリスクが高すぎます",
                              f"{symbol}のリスクスコアが{position.risk_score:.2f}です。損切りを検討してください。",
                              "MEDIUM")
            
            if position.unrealized_pnl < -position.entry_price * position.quantity * 0.1:
                self._add_alert(f"position_loss_{symbol}", "ALERT",
                              f"{symbol}で10%以上の損失",
                              f"{symbol}で{position.unrealized_pnl:,.0f}円の損失が発生しています。",
                              "HIGH")
    
    def _add_alert(self, alert_id: str, alert_type: str, title: str, message: str, priority: str):
        """アラートを追加"""
        # 重複チェック（同じアラートIDが既に存在する場合はスキップ）
        existing_alert = next((alert for alert in self.alert_history if alert['id'] == alert_id), None)
        if existing_alert:
            # 既存のアラートのタイムスタンプを更新
            existing_alert['timestamp'] = datetime.now().isoformat()
            return
        
        alert = {
            'id': alert_id,
            'type': alert_type,
            'title': title,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'priority': priority,
            'color': self._get_alert_color(priority)
        }
        
        self.alert_history.append(alert)
        
        # アラート履歴を最新50件に制限
        if len(self.alert_history) > 50:
            self.alert_history = self.alert_history[-50:]
        
        logger.warning(f"アラート生成: {title}")
    
    def _get_alert_color(self, priority: str) -> str:
        """アラートの色を取得"""
        color_map = {
            'HIGH': '#DC2626',
            'MEDIUM': '#F59E0B',
            'LOW': '#10B981'
        }
        return color_map.get(priority, '#6B7280')
    
    def _save_updated_data(self):
        """更新されたデータを保存"""
        try:
            # データ生成器のポジションを更新
            self.data_generator.risk_system = self.risk_system
            
            # 全データを生成・保存
            self.data_generator.save_data_to_files()
            
            # リアルタイム更新用の追加データを保存
            self._save_realtime_data()
            
        except Exception as e:
            logger.error(f"データ保存エラー: {e}")
    
    def _save_realtime_data(self):
        """リアルタイム更新用データの保存"""
        realtime_data = {
            'price_history': self.price_history,
            'risk_history': self.risk_history,
            'alert_history': self.alert_history,
            'last_updated': datetime.now().isoformat(),
            'update_interval': self.update_interval,
            'is_running': self.is_running
        }
        
        with open('web-app/public/data/risk_realtime_data.json', 'w', encoding='utf-8') as f:
            json.dump(realtime_data, f, ensure_ascii=False, indent=2, default=str)
    
    def get_current_status(self) -> Dict[str, Any]:
        """現在のステータスを取得"""
        risk_report = self.risk_system.get_risk_report()
        
        return {
            'is_running': self.is_running,
            'update_interval': self.update_interval,
            'last_updated': datetime.now().isoformat(),
            'total_positions': len(self.risk_system.positions),
            'risk_score': risk_report['risk_metrics']['risk_score'],
            'portfolio_value': risk_report['risk_metrics']['portfolio_value'],
            'active_alerts': len(self.alert_history),
            'price_history_length': {symbol: len(prices) for symbol, prices in self.price_history.items()}
        }
    
    def force_update(self):
        """強制更新"""
        logger.info("強制更新を実行します")
        self._update_positions()
        self._update_risk_metrics()
        self._check_alerts()
        self._save_updated_data()
        logger.info("強制更新が完了しました")

def main():
    """メイン実行関数"""
    logger.info("リスク管理ダッシュボード用リアルタイム更新システムを開始...")
    
    # 更新システム初期化
    updater = RiskDashboardRealtimeUpdater(account_value=1000000, update_interval=30)
    
    # 初期データ生成
    updater.data_generator.save_data_to_files()
    
    # リアルタイム更新開始
    updater.start_realtime_updates()
    
    try:
        # メインループ
        while True:
            time.sleep(60)  # 1分ごとにステータス表示
            
            status = updater.get_current_status()
            logger.info(f"ステータス: 実行中={status['is_running']}, "
                       f"ポジション数={status['total_positions']}, "
                       f"リスクスコア={status['risk_score']:.2f}, "
                       f"アクティブアラート={status['active_alerts']}")
            
    except KeyboardInterrupt:
        logger.info("停止シグナルを受信しました")
        updater.stop_realtime_updates()
        logger.info("リアルタイム更新システムを停止しました")

if __name__ == "__main__":
    main()
