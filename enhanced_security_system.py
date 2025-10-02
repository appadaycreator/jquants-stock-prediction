#!/usr/bin/env python3
"""
セキュリティ強化システム
認証情報の暗号化、セキュアなログ出力、セッション管理を提供
"""

import os
import logging
import hashlib
import secrets
import base64
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
import re
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """セキュリティレベル"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityEvent:
    """セキュリティイベント"""
    timestamp: datetime
    event_type: str
    severity: SecurityLevel
    description: str
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None


class EnhancedSecuritySystem:
    """セキュリティ強化システム"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """初期化"""
        self.config = config or {}
        self.encryption_key = None
        self.sensitive_patterns = [
            r'password["\']?\s*[:=]\s*["\']?([^"\'\s]+)',
            r'token["\']?\s*[:=]\s*["\']?([^"\'\s]+)',
            r'key["\']?\s*[:=]\s*["\']?([^"\'\s]+)',
            r'secret["\']?\s*[:=]\s*["\']?([^"\'\s]+)',
            r'auth["\']?\s*[:=]\s*["\']?([^"\'\s]+)',
            r'api_key["\']?\s*[:=]\s*["\']?([^"\'\s]+)',
            r'access_token["\']?\s*[:=]\s*["\']?([^"\'\s]+)',
        ]
        self.security_events = []
        self.session_tokens = {}
        self.failed_login_attempts = {}
        
        # セキュリティ設定
        self.max_login_attempts = self.config.get("max_login_attempts", 5)
        self.session_timeout = self.config.get("session_timeout", 3600)  # 1時間
        self.password_min_length = self.config.get("password_min_length", 8)
        self.enable_encryption = self.config.get("enable_encryption", True)
        self.enable_audit_log = self.config.get("enable_audit_log", True)
        
        # 暗号化キーの初期化
        if self.enable_encryption:
            self._initialize_encryption()
        
        logger.info("🔐 セキュリティ強化システムを初期化しました")

    def _initialize_encryption(self):
        """暗号化キーの初期化"""
        try:
            # 環境変数からマスターキーを取得
            master_key = os.getenv('SECURITY_MASTER_KEY')
            if not master_key:
                # デフォルトのマスターキーを生成（本番環境では変更必須）
                master_key = self._generate_master_key()
                logger.warning("⚠️ デフォルトのマスターキーを使用しています。本番環境では変更してください。")
            
            # パスワードベースのキー導出
            password = master_key.encode()
            salt = b'jquants_security_salt'  # 本番環境ではランダムなソルトを使用
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password))
            self.encryption_key = Fernet(key)
            
        except Exception as e:
            logger.error(f"❌ 暗号化キーの初期化に失敗: {e}")
            self.encryption_key = None

    def _generate_master_key(self) -> str:
        """マスターキーの生成"""
        return secrets.token_urlsafe(32)

    def encrypt_sensitive_data(self, data: str) -> str:
        """機密データの暗号化"""
        if not self.enable_encryption or not self.encryption_key:
            return data
        
        try:
            encrypted_data = self.encryption_key.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error(f"❌ データの暗号化に失敗: {e}")
            return data

    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """機密データの復号化"""
        if not self.enable_encryption or not self.encryption_key:
            return encrypted_data
        
        try:
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.encryption_key.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"❌ データの復号化に失敗: {e}")
            return encrypted_data

    def mask_sensitive_info(self, text: str) -> str:
        """機密情報のマスキング"""
        masked_text = text
        
        for pattern in self.sensitive_patterns:
            matches = re.finditer(pattern, masked_text, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) > 0:
                    sensitive_value = match.group(1)
                    if len(sensitive_value) > 4:
                        masked_value = sensitive_value[:2] + "*" * (len(sensitive_value) - 4) + sensitive_value[-2:]
                    else:
                        masked_value = "*" * len(sensitive_value)
                    masked_text = masked_text.replace(sensitive_value, masked_value)
        
        return masked_text

    def create_secure_session(self, user_id: str, additional_data: Dict[str, Any] = None) -> str:
        """セキュアなセッションの作成"""
        # セッショントークンの生成
        session_token = secrets.token_urlsafe(32)
        
        # セッション情報の保存
        session_data = {
            "user_id": user_id,
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
            "ip_address": additional_data.get("ip_address") if additional_data else None,
            "user_agent": additional_data.get("user_agent") if additional_data else None,
            "additional_data": additional_data
        }
        
        self.session_tokens[session_token] = session_data
        
        # セキュリティイベントの記録
        self._log_security_event(
            "session_created",
            SecurityLevel.MEDIUM,
            f"セッションが作成されました: {user_id}",
            user_id,
            additional_data.get("ip_address") if additional_data else None
        )
        
        logger.info(f"🔑 セキュアなセッションを作成しました: {user_id}")
        return session_token

    def validate_session(self, session_token: str) -> Dict[str, Any]:
        """セッションの検証"""
        if session_token not in self.session_tokens:
            self._log_security_event(
                "invalid_session",
                SecurityLevel.HIGH,
                f"無効なセッショントークン: {session_token[:8]}...",
                None
            )
            return {"valid": False, "reason": "invalid_token"}
        
        session_data = self.session_tokens[session_token]
        current_time = datetime.now()
        
        # セッションタイムアウトのチェック
        if (current_time - session_data["last_activity"]).seconds > self.session_timeout:
            del self.session_tokens[session_token]
            self._log_security_event(
                "session_timeout",
                SecurityLevel.MEDIUM,
                f"セッションがタイムアウトしました: {session_data['user_id']}",
                session_data["user_id"]
            )
            return {"valid": False, "reason": "timeout"}
        
        # 最終アクティビティの更新
        session_data["last_activity"] = current_time
        
        return {
            "valid": True,
            "user_id": session_data["user_id"],
            "created_at": session_data["created_at"],
            "last_activity": session_data["last_activity"]
        }

    def invalidate_session(self, session_token: str) -> bool:
        """セッションの無効化"""
        if session_token in self.session_tokens:
            user_id = self.session_tokens[session_token]["user_id"]
            del self.session_tokens[session_token]
            
            self._log_security_event(
                "session_invalidated",
                SecurityLevel.MEDIUM,
                f"セッションが無効化されました: {user_id}",
                user_id
            )
            
            logger.info(f"🔒 セッションを無効化しました: {user_id}")
            return True
        
        return False

    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """パスワード強度の検証"""
        issues = []
        score = 0
        
        # 長さチェック
        if len(password) < self.password_min_length:
            issues.append(f"パスワードが短すぎます（最低{self.password_min_length}文字）")
        else:
            score += 1
        
        # 大文字チェック
        if not re.search(r'[A-Z]', password):
            issues.append("大文字が含まれていません")
        else:
            score += 1
        
        # 小文字チェック
        if not re.search(r'[a-z]', password):
            issues.append("小文字が含まれていません")
        else:
            score += 1
        
        # 数字チェック
        if not re.search(r'\d', password):
            issues.append("数字が含まれていません")
        else:
            score += 1
        
        # 特殊文字チェック
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            issues.append("特殊文字が含まれていません")
        else:
            score += 1
        
        # 強度レベルの判定
        if score >= 5:
            strength_level = "very_strong"
        elif score >= 4:
            strength_level = "strong"
        elif score >= 3:
            strength_level = "medium"
        elif score >= 2:
            strength_level = "weak"
        else:
            strength_level = "very_weak"
        
        return {
            "valid": len(issues) == 0,
            "score": score,
            "max_score": 5,
            "strength_level": strength_level,
            "issues": issues
        }

    def check_login_attempts(self, identifier: str) -> Dict[str, Any]:
        """ログイン試行回数のチェック"""
        current_time = datetime.now()
        
        # 古い試行記録をクリーンアップ
        if identifier in self.failed_login_attempts:
            self.failed_login_attempts[identifier] = [
                attempt for attempt in self.failed_login_attempts[identifier]
                if (current_time - attempt).seconds < 3600  # 1時間以内
            ]
        
        # 現在の試行回数を取得
        attempt_count = len(self.failed_login_attempts.get(identifier, []))
        
        if attempt_count >= self.max_login_attempts:
            self._log_security_event(
                "login_blocked",
                SecurityLevel.HIGH,
                f"ログインがブロックされました: {identifier}",
                identifier
            )
            return {
                "allowed": False,
                "attempt_count": attempt_count,
                "max_attempts": self.max_login_attempts,
                "blocked_until": current_time + timedelta(hours=1)
            }
        
        return {
            "allowed": True,
            "attempt_count": attempt_count,
            "max_attempts": self.max_login_attempts,
            "remaining_attempts": self.max_login_attempts - attempt_count
        }

    def record_failed_login(self, identifier: str):
        """失敗したログイン試行の記録"""
        if identifier not in self.failed_login_attempts:
            self.failed_login_attempts[identifier] = []
        
        self.failed_login_attempts[identifier].append(datetime.now())
        
        self._log_security_event(
            "failed_login",
            SecurityLevel.MEDIUM,
            f"ログインに失敗しました: {identifier}",
            identifier
        )

    def _log_security_event(
        self, 
        event_type: str, 
        severity: SecurityLevel, 
        description: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ):
        """セキュリティイベントの記録"""
        if not self.enable_audit_log:
            return
        
        event = SecurityEvent(
            timestamp=datetime.now(),
            event_type=event_type,
            severity=severity,
            description=description,
            user_id=user_id,
            ip_address=ip_address
        )
        
        self.security_events.append(event)
        
        # ログ出力
        log_message = f"🔐 セキュリティイベント [{severity.value.upper()}]: {description}"
        if user_id:
            log_message += f" (ユーザー: {user_id})"
        if ip_address:
            log_message += f" (IP: {ip_address})"
        
        if severity == SecurityLevel.CRITICAL:
            logger.critical(log_message)
        elif severity == SecurityLevel.HIGH:
            logger.error(log_message)
        elif severity == SecurityLevel.MEDIUM:
            logger.warning(log_message)
        else:
            logger.info(log_message)

    def get_security_report(self) -> Dict[str, Any]:
        """セキュリティレポートの生成"""
        current_time = datetime.now()
        
        # 直近24時間のイベント
        recent_events = [
            event for event in self.security_events
            if (current_time - event.timestamp).days < 1
        ]
        
        # イベントタイプ別の集計
        event_counts = {}
        severity_counts = {}
        
        for event in recent_events:
            event_counts[event.event_type] = event_counts.get(event.event_type, 0) + 1
            severity_counts[event.severity.value] = severity_counts.get(event.severity.value, 0) + 1
        
        # アクティブセッション数
        active_sessions = len(self.session_tokens)
        
        # ブロックされたログイン試行
        blocked_attempts = sum(
            1 for attempts in self.failed_login_attempts.values()
            if len(attempts) >= self.max_login_attempts
        )
        
        return {
            "report_generated_at": current_time,
            "active_sessions": active_sessions,
            "recent_events_count": len(recent_events),
            "event_type_counts": event_counts,
            "severity_counts": severity_counts,
            "blocked_login_attempts": blocked_attempts,
            "security_level": self._calculate_security_level(recent_events)
        }

    def _calculate_security_level(self, events: List[SecurityEvent]) -> str:
        """セキュリティレベルの計算"""
        if not events:
            return "low"
        
        critical_count = sum(1 for event in events if event.severity == SecurityLevel.CRITICAL)
        high_count = sum(1 for event in events if event.severity == SecurityLevel.HIGH)
        
        if critical_count > 0:
            return "critical"
        elif high_count > 3:
            return "high"
        elif high_count > 0:
            return "medium"
        else:
            return "low"

    def cleanup_expired_sessions(self):
        """期限切れセッションのクリーンアップ"""
        current_time = datetime.now()
        expired_tokens = []
        
        for token, session_data in self.session_tokens.items():
            if (current_time - session_data["last_activity"]).seconds > self.session_timeout:
                expired_tokens.append(token)
        
        for token in expired_tokens:
            del self.session_tokens[token]
        
        if expired_tokens:
            logger.info(f"🧹 期限切れセッションをクリーンアップしました: {len(expired_tokens)}件")

    def cleanup(self):
        """リソースのクリーンアップ"""
        self.session_tokens.clear()
        self.failed_login_attempts.clear()
        self.security_events.clear()
        logger.info("🧹 セキュリティ強化システムをクリーンアップしました")
