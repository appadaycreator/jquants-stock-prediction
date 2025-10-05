#!/usr/bin/env python3
"""
期限管理機能
実行期限の管理とアラート機能
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import logging
import json
import threading
import time

class DeadlineStatus(Enum):
    """期限ステータス"""
    PENDING = "pending"  # 待機中
    APPROACHING = "approaching"  # 期限接近
    URGENT = "urgent"  # 緊急
    EXPIRED = "expired"  # 期限切れ
    COMPLETED = "completed"  # 完了

class AlertLevel(Enum):
    """アラートレベル"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class DeadlineInfo:
    """期限情報"""
    action_id: str
    symbol: str
    action_type: str
    deadline: datetime
    deadline_type: str
    status: DeadlineStatus
    priority: str
    created_at: datetime
    updated_at: datetime
    alert_sent: bool = False
    completion_status: str = "pending"
    notes: str = ""

@dataclass
class AlertInfo:
    """アラート情報"""
    alert_id: str
    action_id: str
    level: AlertLevel
    message: str
    created_at: datetime
    sent_at: Optional[datetime] = None
    acknowledged: bool = False

class DeadlineManager:
    """期限管理システム"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """初期化"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # 期限設定
        self.deadline_config = {
            'immediate': timedelta(hours=1),
            'this_week': timedelta(days=7),
            'this_month': timedelta(days=30),
            'next_quarter': timedelta(days=90)
        }
        
        # アラート設定
        self.alert_config = {
            'approaching_hours': 24,  # 24時間前
            'urgent_hours': 6,       # 6時間前
            'critical_hours': 1,     # 1時間前
            'emergency_hours': 0.5   # 30分前
        }
        
        # データストレージ
        self.deadlines: Dict[str, DeadlineInfo] = {}
        self.alerts: List[AlertInfo] = []
        
        # 監視スレッド
        self.monitoring_active = False
        self.monitor_thread = None
        
        # コールバック関数
        self.alert_callbacks = []
        
    def add_deadline(
        self, 
        action_id: str, 
        symbol: str, 
        action_type: str, 
        deadline: datetime,
        deadline_type: str,
        priority: str = "medium",
        notes: str = ""
    ) -> bool:
        """期限の追加"""
        try:
            deadline_info = DeadlineInfo(
                action_id=action_id,
                symbol=symbol,
                action_type=action_type,
                deadline=deadline,
                deadline_type=deadline_type,
                status=DeadlineStatus.PENDING,
                priority=priority,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                notes=notes
            )
            
            self.deadlines[action_id] = deadline_info
            self.logger.info(f"期限追加: {action_id} - {symbol} ({action_type})")
            return True
            
        except Exception as e:
            self.logger.error(f"期限追加エラー: {e}")
            return False
    
    def update_deadline_status(
        self, 
        action_id: str, 
        status: DeadlineStatus,
        completion_status: str = "pending",
        notes: str = ""
    ) -> bool:
        """期限ステータスの更新"""
        try:
            if action_id not in self.deadlines:
                self.logger.warning(f"期限が見つかりません: {action_id}")
                return False
            
            deadline = self.deadlines[action_id]
            deadline.status = status
            deadline.completion_status = completion_status
            deadline.updated_at = datetime.now()
            
            if notes:
                deadline.notes = notes
            
            self.logger.info(f"期限ステータス更新: {action_id} - {status.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"期限ステータス更新エラー: {e}")
            return False
    
    def get_deadlines_by_status(self, status: DeadlineStatus) -> List[DeadlineInfo]:
        """ステータス別の期限取得"""
        return [
            deadline for deadline in self.deadlines.values()
            if deadline.status == status
        ]
    
    def get_approaching_deadlines(self, hours: int = 24) -> List[DeadlineInfo]:
        """期限接近のアクション取得"""
        cutoff_time = datetime.now() + timedelta(hours=hours)
        
        approaching = []
        for deadline in self.deadlines.values():
            if (deadline.status == DeadlineStatus.PENDING and 
                deadline.deadline <= cutoff_time):
                approaching.append(deadline)
        
        return sorted(approaching, key=lambda x: x.deadline)
    
    def get_urgent_deadlines(self) -> List[DeadlineInfo]:
        """緊急期限の取得"""
        return self.get_approaching_deadlines(self.alert_config['urgent_hours'])
    
    def get_expired_deadlines(self) -> List[DeadlineInfo]:
        """期限切れの取得"""
        now = datetime.now()
        expired = []
        
        for deadline in self.deadlines.values():
            if (deadline.status == DeadlineStatus.PENDING and 
                deadline.deadline < now):
                deadline.status = DeadlineStatus.EXPIRED
                expired.append(deadline)
        
        return expired
    
    def start_monitoring(self) -> bool:
        """期限監視の開始"""
        try:
            if self.monitoring_active:
                self.logger.warning("期限監視は既に開始されています")
                return False
            
            self.monitoring_active = True
            self.monitor_thread = threading.Thread(target=self._monitor_deadlines)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            
            self.logger.info("期限監視を開始")
            return True
            
        except Exception as e:
            self.logger.error(f"期限監視開始エラー: {e}")
            return False
    
    def stop_monitoring(self) -> bool:
        """期限監視の停止"""
        try:
            self.monitoring_active = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=5)
            
            self.logger.info("期限監視を停止")
            return True
            
        except Exception as e:
            self.logger.error(f"期限監視停止エラー: {e}")
            return False
    
    def _monitor_deadlines(self):
        """期限監視の実行"""
        while self.monitoring_active:
            try:
                # 期限切れのチェック
                expired_deadlines = self.get_expired_deadlines()
                for deadline in expired_deadlines:
                    self._create_alert(
                        deadline.action_id,
                        AlertLevel.EMERGENCY,
                        f"期限切れ: {deadline.symbol} ({deadline.action_type})"
                    )
                
                # 緊急期限のチェック
                urgent_deadlines = self.get_urgent_deadlines()
                for deadline in urgent_deadlines:
                    if not deadline.alert_sent:
                        self._create_alert(
                            deadline.action_id,
                            AlertLevel.CRITICAL,
                            f"緊急期限: {deadline.symbol} ({deadline.action_type})"
                        )
                        deadline.alert_sent = True
                
                # 期限接近のチェック
                approaching_deadlines = self.get_approaching_deadlines()
                for deadline in approaching_deadlines:
                    if not deadline.alert_sent:
                        self._create_alert(
                            deadline.action_id,
                            AlertLevel.WARNING,
                            f"期限接近: {deadline.symbol} ({deadline.action_type})"
                        )
                        deadline.alert_sent = True
                
                # 30秒間隔でチェック
                time.sleep(30)
                
            except Exception as e:
                self.logger.error(f"期限監視エラー: {e}")
                time.sleep(60)  # エラー時は1分待機
    
    def _create_alert(
        self, 
        action_id: str, 
        level: AlertLevel, 
        message: str
    ) -> str:
        """アラートの作成"""
        try:
            alert_id = f"alert_{action_id}_{int(time.time())}"
            
            alert = AlertInfo(
                alert_id=alert_id,
                action_id=action_id,
                level=level,
                message=message,
                created_at=datetime.now()
            )
            
            self.alerts.append(alert)
            
            # コールバック関数の実行
            for callback in self.alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    self.logger.error(f"アラートコールバックエラー: {e}")
            
            self.logger.info(f"アラート作成: {alert_id} - {level.value}")
            return alert_id
            
        except Exception as e:
            self.logger.error(f"アラート作成エラー: {e}")
            return ""
    
    def add_alert_callback(self, callback_func):
        """アラートコールバックの追加"""
        self.alert_callbacks.append(callback_func)
        self.logger.info("アラートコールバックを追加")
    
    def get_deadline_summary(self) -> Dict[str, Any]:
        """期限サマリーの取得"""
        try:
            total_deadlines = len(self.deadlines)
            pending_count = len(self.get_deadlines_by_status(DeadlineStatus.PENDING))
            approaching_count = len(self.get_approaching_deadlines())
            urgent_count = len(self.get_urgent_deadlines())
            expired_count = len(self.get_deadlines_by_status(DeadlineStatus.EXPIRED))
            completed_count = len(self.get_deadlines_by_status(DeadlineStatus.COMPLETED))
            
            # アクション種別別の集計
            action_counts = {}
            for deadline in self.deadlines.values():
                action_type = deadline.action_type
                action_counts[action_type] = action_counts.get(action_type, 0) + 1
            
            # 優先度別の集計
            priority_counts = {}
            for deadline in self.deadlines.values():
                priority = deadline.priority
                priority_counts[priority] = priority_counts.get(priority, 0) + 1
            
            return {
                'total_deadlines': total_deadlines,
                'pending_count': pending_count,
                'approaching_count': approaching_count,
                'urgent_count': urgent_count,
                'expired_count': expired_count,
                'completed_count': completed_count,
                'action_counts': action_counts,
                'priority_counts': priority_counts,
                'monitoring_active': self.monitoring_active
            }
            
        except Exception as e:
            self.logger.error(f"期限サマリー取得エラー: {e}")
            return {}
    
    def get_deadline_timeline(self, days: int = 7) -> List[Dict[str, Any]]:
        """期限タイムラインの取得"""
        try:
            end_date = datetime.now() + timedelta(days=days)
            timeline = []
            
            for deadline in self.deadlines.values():
                if deadline.deadline <= end_date:
                    timeline.append({
                        'action_id': deadline.action_id,
                        'symbol': deadline.symbol,
                        'action_type': deadline.action_type,
                        'deadline': deadline.deadline.isoformat(),
                        'status': deadline.status.value,
                        'priority': deadline.priority,
                        'days_remaining': (deadline.deadline - datetime.now()).days,
                        'hours_remaining': (deadline.deadline - datetime.now()).total_seconds() / 3600
                    })
            
            return sorted(timeline, key=lambda x: x['deadline'])
            
        except Exception as e:
            self.logger.error(f"期限タイムライン取得エラー: {e}")
            return []
    
    def export_deadlines_to_json(self, filepath: str) -> bool:
        """期限データのJSONエクスポート"""
        try:
            export_data = {
                'deadlines': [],
                'alerts': [],
                'summary': self.get_deadline_summary(),
                'timeline': self.get_deadline_timeline(),
                'exported_at': datetime.now().isoformat()
            }
            
            # 期限データの追加
            for deadline in self.deadlines.values():
                deadline_dict = {
                    'action_id': deadline.action_id,
                    'symbol': deadline.symbol,
                    'action_type': deadline.action_type,
                    'deadline': deadline.deadline.isoformat(),
                    'deadline_type': deadline.deadline_type,
                    'status': deadline.status.value,
                    'priority': deadline.priority,
                    'created_at': deadline.created_at.isoformat(),
                    'updated_at': deadline.updated_at.isoformat(),
                    'alert_sent': deadline.alert_sent,
                    'completion_status': deadline.completion_status,
                    'notes': deadline.notes
                }
                export_data['deadlines'].append(deadline_dict)
            
            # アラートデータの追加
            for alert in self.alerts:
                alert_dict = {
                    'alert_id': alert.alert_id,
                    'action_id': alert.action_id,
                    'level': alert.level.value,
                    'message': alert.message,
                    'created_at': alert.created_at.isoformat(),
                    'sent_at': alert.sent_at.isoformat() if alert.sent_at else None,
                    'acknowledged': alert.acknowledged
                }
                export_data['alerts'].append(alert_dict)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"期限データを{filepath}にエクスポート")
            return True
            
        except Exception as e:
            self.logger.error(f"期限データエクスポートエラー: {e}")
            return False
    
    def cleanup_expired_data(self, days: int = 30) -> int:
        """期限切れデータのクリーンアップ"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            cleaned_count = 0
            
            # 期限切れデータの削除
            expired_actions = [
                action_id for action_id, deadline in self.deadlines.items()
                if deadline.status == DeadlineStatus.EXPIRED and 
                   deadline.updated_at < cutoff_date
            ]
            
            for action_id in expired_actions:
                del self.deadlines[action_id]
                cleaned_count += 1
            
            # 古いアラートの削除
            old_alerts = [
                alert for alert in self.alerts
                if alert.created_at < cutoff_date
            ]
            
            for alert in old_alerts:
                self.alerts.remove(alert)
                cleaned_count += 1
            
            self.logger.info(f"{cleaned_count}件の期限切れデータをクリーンアップ")
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"期限切れデータクリーンアップエラー: {e}")
            return 0
