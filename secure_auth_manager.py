#!/usr/bin/env python3
"""
セキュアな認証管理モジュール
機密情報の安全な管理と認証機能を提供
"""

import os
import requests
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from unified_error_handler import get_unified_error_handler

logger = logging.getLogger(__name__)


class SecureAuthManager:
    """セキュアな認証管理クラス"""

    def __init__(self):
        """初期化"""
        self.error_handler = get_unified_error_handler("SecureAuthManager")
        self.email = None
        self.password = None
        self.refresh_token = None
        self.id_token = None
        self.token_expires_at = None
        self.session = requests.Session()
        
        # 環境変数の読み込み
        load_dotenv()
        
        # 認証情報の安全な取得
        self._load_credentials()

    def _load_credentials(self) -> None:
        """認証情報の安全な読み込み"""
        try:
            self.email = os.getenv("JQUANTS_EMAIL")
            self.password = os.getenv("JQUANTS_PASSWORD")
            
            # 認証情報の検証（機密情報はログに出力しない）
            if not self.email or not self.password:
                error_msg = "認証情報が設定されていません"
                # 機密情報をマスキングしてログ出力
                masked_context = {
                    "email_set": bool(self.email),
                    "password_set": bool(self.password),
                    "env_file_exists": os.path.exists(".env"),
                }
                self.error_handler.log_error(
                    ValueError(error_msg),
                    "認証情報検証エラー",
                    masked_context,
                )
                logger.error("❌ 環境変数 JQUANTS_EMAIL と JQUANTS_PASSWORD を設定してください。")
                logger.error("💡 .env ファイルを作成し、認証情報を設定してください。")
                raise ValueError(error_msg)
                
            logger.info("✅ 認証情報の読み込み完了")
            
        except Exception as e:
            self.error_handler.log_error(e, "認証情報読み込みエラー")
            raise

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
                self.error_handler.handle_api_error(
                    ValueError(error_msg),
                    "J-Quants API",
                    auth_url,
                    response.status_code,
                )
                raise ValueError(error_msg)

            self.refresh_token = auth_data["refreshToken"]
            logger.info("✅ リフレッシュトークンを取得しました")
            return self.refresh_token

        except requests.exceptions.RequestException as e:
            self.error_handler.handle_api_error(e, "J-Quants API", auth_url)
            raise
        except Exception as e:
            self.error_handler.log_error(e, "リフレッシュトークン取得エラー")
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
                self.error_handler.handle_api_error(
                    ValueError(error_msg),
                    "J-Quants API",
                    id_token_url,
                    response.status_code,
                )
                raise ValueError(error_msg)

            self.id_token = id_token_data["idToken"]
            # トークンの有効期限を設定（通常24時間）
            self.token_expires_at = datetime.now() + timedelta(hours=23)
            logger.info("✅ IDトークンを取得しました")
            return self.id_token

        except requests.exceptions.RequestException as e:
            self.error_handler.handle_api_error(e, "J-Quants API", id_token_url)
            raise
        except Exception as e:
            self.error_handler.log_error(e, "IDトークン取得エラー")
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
