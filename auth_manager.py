#!/usr/bin/env python3
"""
認証管理モジュール
J-Quants APIの認証機能を担当する独立したクラス
"""

import os
import requests
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from security_config import SecurityConfig, validate_security_requirements

logger = logging.getLogger(__name__)


class AuthManager:
    """J-Quants API認証管理クラス"""

    def __init__(self):
        """初期化"""
        # セキュリティ検証の実行
        if not validate_security_requirements():
            raise ValueError("セキュリティ要件を満たしていません")

        self.security_config = SecurityConfig()
        self.email = os.getenv("JQUANTS_EMAIL")
        self.password = os.getenv("JQUANTS_PASSWORD")
        self.refresh_token = None
        self.id_token = None
        self.token_expires_at = None
        self.session = requests.Session()

        # 認証情報の検証（セキュアな方法）
        self._validate_credentials()

    def _validate_credentials(self) -> None:
        """認証情報の検証（セキュアな方法）"""
        if not self.email or not self.password:
            error_msg = "認証情報が設定されていません"
            # 機密情報をマスキングしてログ出力
            masked_context = self.security_config.mask_sensitive_data(
                {
                    "email_set": bool(self.email),
                    "password_set": bool(self.password),
                    "env_file_exists": os.path.exists(".env"),
                }
            )
            logger.error(
                f"❌ 環境変数 JQUANTS_EMAIL と JQUANTS_PASSWORD を設定してください。"
            )
            logger.error("💡 .env ファイルを作成し、認証情報を設定してください。")
            raise ValueError(error_msg)

    def get_refresh_token(self) -> str:
        """リフレッシュトークンの取得"""
        logger.info("🔑 リフレッシュトークンを取得中...")

        try:
            auth_url = "https://api.jquants.com/v1/token/auth_user"
            auth_payload = {"mailaddress": self.email, "password": self.password}

            response = self.session.post(auth_url, json=auth_payload, timeout=30)
            response.raise_for_status()

            auth_data = response.json()

            if "refreshToken" not in auth_data:
                error_msg = "リフレッシュトークンの取得に失敗しました"
                logger.error(f"❌ リフレッシュトークンが取得できませんでした")
                raise ValueError(error_msg)

            self.refresh_token = auth_data["refreshToken"]
            logger.info("✅ リフレッシュトークンを取得しました")
            return self.refresh_token

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ リフレッシュトークン取得エラー: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ 予期しないエラー: {e}")
            raise

    def get_id_token(self) -> str:
        """IDトークンの取得"""
        logger.info("🎫 IDトークンを取得中...")

        try:
            if not self.refresh_token:
                self.get_refresh_token()

            id_token_url = "https://api.jquants.com/v1/token/auth_refresh"
            id_token_params = {"refreshtoken": self.refresh_token}

            response = self.session.post(
                id_token_url, params=id_token_params, timeout=30
            )
            response.raise_for_status()

            id_token_data = response.json()

            if "idToken" not in id_token_data:
                error_msg = "IDトークンの取得に失敗しました"
                logger.error(f"❌ IDトークンが取得できませんでした")
                raise ValueError(error_msg)

            self.id_token = id_token_data["idToken"]
            # トークンの有効期限を設定（通常24時間）
            self.token_expires_at = datetime.now() + timedelta(hours=23)
            logger.info("✅ IDトークンを取得しました")
            return self.id_token

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ IDトークン取得エラー: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ 予期しないエラー: {e}")
            raise

    def ensure_valid_token(self) -> str:
        """有効なトークンの確保"""
        if (
            self.id_token is None
            or self.token_expires_at is None
            or datetime.now() >= self.token_expires_at
        ):
            logger.info("🔄 トークンの更新が必要です")
            self.get_id_token()

        return self.id_token

    def get_auth_headers(self) -> Dict[str, str]:
        """認証ヘッダーの取得"""
        token = self.ensure_valid_token()
        return {"Authorization": f"Bearer {token}"}
