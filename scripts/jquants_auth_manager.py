#!/usr/bin/env python3
"""
jQuants認証管理クラス
IDトークンの有効性チェックと自動再取得機能
"""

import os
import json
import requests
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

# ログ設定
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class JQuantsAuthManager:
    """jQuants認証管理クラス"""

    def __init__(self):
        self.email = os.getenv("JQUANTS_EMAIL")
        self.password = os.getenv("JQUANTS_PASSWORD")
        self.id_token = os.getenv("JQUANTS_ID_TOKEN")
        self.refresh_token = os.getenv("JQUANTS_REFRESH_TOKEN")

        # APIエンドポイント
        self.auth_url = "https://api.jquants.com/v1/token/auth_user"
        self.refresh_url = "https://api.jquants.com/v1/token/auth_refresh"
        self.test_url = "https://api.jquants.com/v1/listed/info"

        # トークン有効期限（秒）
        self.token_expiry_buffer = 300  # 5分前から更新

    def is_token_valid(self) -> bool:
        """IDトークンの有効性をチェック"""
        if not self.id_token:
            logger.warning("IDトークンが設定されていません")
            return False

        try:
            # JWTトークンのペイロードをデコード（簡易版）
            import base64
            import json as json_lib

            # JWTのペイロード部分を取得
            parts = self.id_token.split(".")
            if len(parts) != 3:
                logger.error("無効なJWTトークン形式")
                return False

            # ペイロードをデコード
            payload = parts[1]
            # パディングを追加
            missing_padding = len(payload) % 4
            if missing_padding:
                payload += "=" * (4 - missing_padding)

            decoded_payload = base64.urlsafe_b64decode(payload)
            payload_data = json_lib.loads(decoded_payload)

            # 有効期限をチェック
            exp_timestamp = payload_data.get("exp", 0)
            current_timestamp = datetime.now().timestamp()

            # バッファ時間を考慮
            if exp_timestamp - current_timestamp < self.token_expiry_buffer:
                logger.warning(
                    f"トークンの有効期限が近いです (残り: {exp_timestamp - current_timestamp:.0f}秒)"
                )
                return False

            logger.info("IDトークンは有効です")
            return True

        except Exception as e:
            logger.error(f"トークン有効性チェックエラー: {e}")
            return False

    def test_token_with_api(self) -> bool:
        """APIエンドポイントでトークンをテスト"""
        if not self.id_token:
            return False

        try:
            headers = {"Authorization": f"Bearer {self.id_token}"}
            response = requests.get(self.test_url, headers=headers, timeout=10)

            if response.status_code == 200:
                logger.info("APIテスト成功: トークンは有効です")
                return True
            else:
                logger.warning(f"APIテスト失敗: HTTP {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"APIテストエラー: {e}")
            return False

    def get_new_tokens(self) -> Optional[Dict[str, str]]:
        """メールアドレスとパスワードで新しいトークンを取得"""
        if not self.email or not self.password:
            logger.error(
                "認証情報が設定されていません (JQUANTS_EMAIL, JQUANTS_PASSWORD)"
            )
            return None

        try:
            logger.info("新しいトークンを取得中...")

            # 認証リクエスト
            auth_data = {"mailaddress": self.email, "password": self.password}

            response = requests.post(self.auth_url, json=auth_data, timeout=30)
            response.raise_for_status()

            auth_result = response.json()
            refresh_token = auth_result.get("refreshToken")

            if not refresh_token:
                logger.error("リフレッシュトークンの取得に失敗しました")
                return None

            logger.info("リフレッシュトークンを取得しました")

            # IDトークンを取得
            refresh_data = {"refreshtoken": refresh_token}
            refresh_response = requests.post(
                self.refresh_url, json=refresh_data, timeout=30
            )
            refresh_response.raise_for_status()

            refresh_result = refresh_response.json()
            id_token = refresh_result.get("idToken")

            if not id_token:
                logger.error("IDトークンの取得に失敗しました")
                return None

            logger.info("IDトークンを取得しました")

            return {"id_token": id_token, "refresh_token": refresh_token}

        except requests.exceptions.RequestException as e:
            logger.error(f"認証エラー: {e}")
            return None
        except Exception as e:
            logger.error(f"予期しないエラー: {e}")
            return None

    def refresh_id_token(self) -> Optional[str]:
        """リフレッシュトークンでIDトークンを更新"""
        if not self.refresh_token:
            logger.warning("リフレッシュトークンが設定されていません")
            return None

        try:
            logger.info("リフレッシュトークンでIDトークンを更新中...")

            refresh_data = {"refreshtoken": self.refresh_token}
            response = requests.post(self.refresh_url, json=refresh_data, timeout=30)
            response.raise_for_status()

            result = response.json()
            new_id_token = result.get("idToken")

            if new_id_token:
                logger.info("IDトークンの更新に成功しました")
                return new_id_token
            else:
                logger.error("IDトークンの更新に失敗しました")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"トークン更新エラー: {e}")
            return None
        except Exception as e:
            logger.error(f"予期しないエラー: {e}")
            return None

    def get_valid_token(self) -> Optional[str]:
        """有効なIDトークンを取得（必要に応じて更新）"""
        # 1. 現在のトークンが有効かチェック
        if self.is_token_valid() and self.test_token_with_api():
            logger.info("現在のトークンは有効です")
            return self.id_token

        # 2. リフレッシュトークンで更新を試行
        if self.refresh_token:
            logger.info("リフレッシュトークンで更新を試行...")
            new_id_token = self.refresh_id_token()
            if new_id_token:
                # 更新されたトークンをテスト
                self.id_token = new_id_token
                if self.test_token_with_api():
                    logger.info("リフレッシュトークンでの更新に成功しました")
                    return new_id_token

        # 3. メールアドレスとパスワードで新規取得
        logger.info("メールアドレスとパスワードで新規認証を試行...")
        new_tokens = self.get_new_tokens()
        if new_tokens:
            self.id_token = new_tokens["id_token"]
            self.refresh_token = new_tokens["refresh_token"]

            # 新しいトークンをテスト
            if self.test_token_with_api():
                logger.info("新規認証に成功しました")
                return self.id_token

        logger.error("すべての認証方法が失敗しました")
        return None

    def save_tokens_to_env(self, tokens: Dict[str, str]) -> bool:
        """トークンを環境変数ファイルに保存"""
        try:
            env_file = ".env"
            env_content = []

            # 既存の.envファイルを読み込み
            if os.path.exists(env_file):
                with open(env_file, "r", encoding="utf-8") as f:
                    env_content = f.readlines()

            # トークンを更新
            token_updated = False
            refresh_updated = False

            for i, line in enumerate(env_content):
                if line.startswith("JQUANTS_ID_TOKEN="):
                    env_content[i] = f"JQUANTS_ID_TOKEN={tokens['id_token']}\n"
                    token_updated = True
                elif line.startswith("JQUANTS_REFRESH_TOKEN="):
                    env_content[i] = (
                        f"JQUANTS_REFRESH_TOKEN={tokens['refresh_token']}\n"
                    )
                    refresh_updated = True

            # 新しいトークンを追加
            if not token_updated:
                env_content.append(f"JQUANTS_ID_TOKEN={tokens['id_token']}\n")
            if not refresh_updated:
                env_content.append(f"JQUANTS_REFRESH_TOKEN={tokens['refresh_token']}\n")

            # ファイルに書き込み
            with open(env_file, "w", encoding="utf-8") as f:
                f.writelines(env_content)

            logger.info("トークンを環境変数ファイルに保存しました")
            return True

        except Exception as e:
            logger.error(f"トークン保存エラー: {e}")
            return False


def main():
    """メイン処理"""
    logger.info("=== jQuants認証管理開始 ===")

    auth_manager = JQuantsAuthManager()

    # 有効なトークンを取得
    valid_token = auth_manager.get_valid_token()

    if valid_token:
        logger.info("✅ 有効なトークンを取得しました")

        # トークンを環境変数ファイルに保存
        tokens = {"id_token": valid_token, "refresh_token": auth_manager.refresh_token}

        if auth_manager.save_tokens_to_env(tokens):
            logger.info("✅ トークンを環境変数ファイルに保存しました")
        else:
            logger.error("❌ トークンの保存に失敗しました")

    else:
        logger.error("❌ 有効なトークンの取得に失敗しました")
        return 1

    logger.info("=== jQuants認証管理完了 ===")
    return 0


if __name__ == "__main__":
    exit(main())
