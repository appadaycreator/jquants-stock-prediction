#!/usr/bin/env python3
"""
セキュリティ設定管理モジュール
認証情報の安全な管理と環境変数の検証を提供
"""

import os
import logging
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
import base64
import hashlib

logger = logging.getLogger(__name__)


class SecurityConfig:
    """セキュリティ設定管理クラス"""
    
    def __init__(self):
        self.required_env_vars = [
            "JQUANTS_EMAIL",
            "JQUANTS_PASSWORD"
        ]
        self.sensitive_keys = [
            "password", "token", "key", "secret", "auth"
        ]
    
    def validate_environment(self) -> Dict[str, Any]:
        """環境変数の検証"""
        logger.info("🔐 環境変数のセキュリティ検証を開始")
        
        validation_result = {
            "is_valid": True,
            "missing_vars": [],
            "security_issues": [],
            "recommendations": []
        }
        
        # 必須環境変数の確認
        for var in self.required_env_vars:
            if not os.getenv(var):
                validation_result["missing_vars"].append(var)
                validation_result["is_valid"] = False
        
        # セキュリティチェック
        self._check_password_strength(validation_result)
        self._check_environment_security(validation_result)
        
        if validation_result["is_valid"]:
            logger.info("✅ 環境変数のセキュリティ検証完了")
        else:
            logger.error("❌ 環境変数のセキュリティ検証に問題があります")
            
        return validation_result
    
    def _check_password_strength(self, result: Dict[str, Any]) -> None:
        """パスワード強度のチェック"""
        password = os.getenv("JQUANTS_PASSWORD")
        if not password:
            return
            
        issues = []
        
        # 長さチェック
        if len(password) < 8:
            issues.append("パスワードが8文字未満です")
        
        # 複雑性チェック
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        if not has_upper:
            issues.append("大文字が含まれていません")
        if not has_lower:
            issues.append("小文字が含まれていません")
        if not has_digit:
            issues.append("数字が含まれていません")
        if not has_special:
            issues.append("特殊文字が含まれていません")
        
        if issues:
            result["security_issues"].extend(issues)
            result["recommendations"].append("強力なパスワードを使用してください")
    
    def _check_environment_security(self, result: Dict[str, Any]) -> None:
        """環境のセキュリティチェック"""
        # .envファイルの存在チェック
        if os.path.exists(".env"):
            result["recommendations"].append(".envファイルは.gitignoreに含まれていることを確認してください")
        
        # 本番環境のチェック
        if os.getenv("ENVIRONMENT") == "production":
            result["recommendations"].append("本番環境では追加のセキュリティ対策を実施してください")
    
    def mask_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """機密データのマスキング"""
        masked_data = data.copy()
        
        for key, value in masked_data.items():
            if any(sensitive_key in key.lower() for sensitive_key in self.sensitive_keys):
                if isinstance(value, str) and len(value) > 4:
                    masked_data[key] = value[:2] + "*" * (len(value) - 4) + value[-2:]
                else:
                    masked_data[key] = "***"
        
        return masked_data
    
    def get_secure_config(self) -> Dict[str, Any]:
        """セキュアな設定の取得"""
        config = {}
        
        for var in self.required_env_vars:
            value = os.getenv(var)
            if value:
                # 機密情報はマスキングして返す
                if any(sensitive_key in var.lower() for sensitive_key in self.sensitive_keys):
                    config[var] = "***MASKED***"
                else:
                    config[var] = value
        
        return config


def validate_security_requirements() -> bool:
    """セキュリティ要件の検証"""
    security_config = SecurityConfig()
    validation_result = security_config.validate_environment()
    
    if not validation_result["is_valid"]:
        logger.error("❌ セキュリティ要件を満たしていません")
        for issue in validation_result["security_issues"]:
            logger.error(f"  - {issue}")
        return False
    
    logger.info("✅ セキュリティ要件を満たしています")
    return True
