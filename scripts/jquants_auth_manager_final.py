#!/usr/bin/env python3
"""
jQuants認証管理クラス（最終版）
IDトークンを環境変数に保存せず、一時保存のみで再認証機能を実装
"""

import os
import json
import requests
import logging
import time
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

# 環境変数読み込み
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # dotenvがインストールされていない場合は手動で.envファイルを読み込み
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key] = value

# ログ設定
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class JQuantsAuthManagerFinal:
    """jQuants認証管理クラス（最終版）"""

    def __init__(self):
        # 認証情報（IDトークンは環境変数に設定しない）
        self.email = os.getenv("JQUANTS_EMAIL")
        self.password = os.getenv("JQUANTS_PASSWORD")

        # 一時保存されたトークン（環境変数からは取得しない）
        self.temp_id_token = None
        self.temp_refresh_token = None

        # APIエンドポイント
        self.auth_url = "https://api.jquants.com/v1/token/auth_user"
        self.refresh_url = "https://api.jquants.com/v1/token/auth_refresh"
        self.test_url = "https://api.jquants.com/v1/listed/info"

        # トークン有効期限（秒）
        self.token_expiry_buffer = 300  # 5分前から更新

        # リトライ設定
        self.max_retries = 3
        self.retry_delay = 2  # 秒

        # 一時トークンキャッシュファイル（環境変数に保存しない）
        self.temp_token_cache_file = Path("data/temp_token_cache.json")
        self.data_dir = Path("data")
        if not self.data_dir.exists():
            self.data_dir.mkdir(parents=True, exist_ok=True)

        # セッション管理
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "User-Agent": "jQuants-Stock-Prediction/1.0",
            }
        )

    def load_temp_token_cache(self) -> Optional[Dict[str, Any]]:
        """一時トークンキャッシュを読み込み"""
        try:
            if self.temp_token_cache_file.exists():
                with open(self.temp_token_cache_file, "r", encoding="utf-8") as f:
                    cache = json.load(f)
                logger.info("一時トークンキャッシュを読み込みました")
                return cache
        except Exception as e:
            logger.warning(f"一時トークンキャッシュ読み込みエラー: {e}")
        return None

    def save_temp_token_cache(self, tokens: Dict[str, str]) -> bool:
        """一時トークンキャッシュを保存（環境変数には保存しない）"""
        try:
            cache_data = {
                "id_token": tokens.get("id_token", ""),
                "refresh_token": tokens.get("refresh_token", ""),
                "cached_at": datetime.now().isoformat(),
                "expires_at": self._calculate_token_expiry(tokens.get("id_token", "")),
            }

            with open(self.temp_token_cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)

            logger.info("一時トークンキャッシュを保存しました")
            return True
        except Exception as e:
            logger.error(f"一時トークンキャッシュ保存エラー: {e}")
            return False

    def _calculate_token_expiry(self, id_token: str) -> str:
        """トークンの有効期限を計算"""
        try:
            import base64
            import json as json_lib

            parts = id_token.split(".")
            if len(parts) != 3:
                return ""

            payload = parts[1]
            missing_padding = len(payload) % 4
            if missing_padding:
                payload += "=" * (4 - missing_padding)

            decoded_payload = base64.urlsafe_b64decode(payload)
            payload_data = json_lib.loads(decoded_payload)

            exp_timestamp = payload_data.get("exp", 0)
            exp_datetime = datetime.fromtimestamp(exp_timestamp)
            return exp_datetime.isoformat()
        except Exception:
            return ""

    def is_token_valid(self, id_token: str) -> bool:
        """IDトークンの有効性をチェック"""
        if not id_token:
            logger.warning("IDトークンが設定されていません")
            return False

        try:
            # JWTトークンのペイロードをデコード
            import base64
            import json as json_lib

            parts = id_token.split(".")
            if len(parts) != 3:
                logger.error("無効なJWTトークン形式")
                return False

            payload = parts[1]
            missing_padding = len(payload) % 4
            if missing_padding:
                payload += "=" * (4 - missing_padding)

            decoded_payload = base64.urlsafe_b64decode(payload)
            payload_data = json_lib.loads(decoded_payload)

            # 有効期限をチェック
            exp_timestamp = payload_data.get("exp", 0)
            current_timestamp = datetime.now().timestamp()

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

    def test_token_with_api(self, id_token: str) -> bool:
        """APIエンドポイントでトークンをテスト"""
        if not id_token:
            return False

        for attempt in range(self.max_retries):
            try:
                headers = {"Authorization": f"Bearer {id_token}"}
                response = self.session.get(self.test_url, headers=headers, timeout=10)

                if response.status_code == 200:
                    logger.info("APIテスト成功: トークンは有効です")
                    return True
                elif response.status_code == 401:
                    logger.warning("APIテスト失敗: 認証エラー (401)")
                    return False
                else:
                    logger.warning(f"APIテスト失敗: HTTP {response.status_code}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                        continue
                    return False

            except requests.exceptions.RequestException as e:
                logger.error(
                    f"APIテストエラー (試行 {attempt + 1}/{self.max_retries}): {e}"
                )
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                return False

        return False

    def get_new_tokens(self) -> Optional[Dict[str, str]]:
        """メールアドレスとパスワードで新しいトークンを取得"""
        if not self.email or not self.password:
            logger.error(
                "認証情報が設定されていません (JQUANTS_EMAIL, JQUANTS_PASSWORD)"
            )
            return None

        for attempt in range(self.max_retries):
            try:
                logger.info(
                    f"新しいトークンを取得中... (試行 {attempt + 1}/{self.max_retries})"
                )

                # 認証リクエスト
                auth_data = {"mailaddress": self.email, "password": self.password}
                response = self.session.post(self.auth_url, json=auth_data, timeout=30)

                if response.status_code == 200:
                    auth_result = response.json()
                    refresh_token = auth_result.get("refreshToken")

                    if not refresh_token:
                        logger.error("リフレッシュトークンの取得に失敗しました")
                        return None

                    logger.info("リフレッシュトークンを取得しました")

                    # IDトークンを取得
                    refresh_response = self.session.post(
                        f"{self.refresh_url}?refreshtoken={refresh_token}", timeout=30
                    )

                    if refresh_response.status_code == 200:
                        refresh_result = refresh_response.json()
                        id_token = refresh_result.get("idToken")

                        if id_token:
                            logger.info("IDトークンを取得しました")
                            tokens = {
                                "id_token": id_token,
                                "refresh_token": refresh_token,
                            }

                            # 一時トークンをキャッシュに保存（環境変数には保存しない）
                            self.save_temp_token_cache(tokens)

                            return tokens
                        else:
                            logger.error("IDトークンの取得に失敗しました")
                    else:
                        logger.error(
                            f"IDトークン取得エラー: HTTP {refresh_response.status_code}"
                        )
                else:
                    logger.error(f"認証エラー: HTTP {response.status_code}")

                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue

            except requests.exceptions.RequestException as e:
                logger.error(f"認証エラー (試行 {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
            except Exception as e:
                logger.error(
                    f"予期しないエラー (試行 {attempt + 1}/{self.max_retries}): {e}"
                )
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue

        logger.error("すべての認証試行が失敗しました")
        return None

    def refresh_id_token(self, refresh_token: str) -> Optional[str]:
        """リフレッシュトークンでIDトークンを更新"""
        if not refresh_token:
            logger.warning("リフレッシュトークンが設定されていません")
            return None

        for attempt in range(self.max_retries):
            try:
                logger.info(
                    f"リフレッシュトークンでIDトークンを更新中... (試行 {attempt + 1}/{self.max_retries})"
                )

                response = self.session.post(
                    f"{self.refresh_url}?refreshtoken={refresh_token}", timeout=30
                )

                if response.status_code == 200:
                    result = response.json()
                    new_id_token = result.get("idToken")

                    if new_id_token:
                        logger.info("IDトークンの更新に成功しました")
                        return new_id_token
                    else:
                        logger.error("IDトークンの更新に失敗しました")
                else:
                    logger.error(f"トークン更新エラー: HTTP {response.status_code}")

                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue

            except requests.exceptions.RequestException as e:
                logger.error(
                    f"トークン更新エラー (試行 {attempt + 1}/{self.max_retries}): {e}"
                )
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
            except Exception as e:
                logger.error(
                    f"予期しないエラー (試行 {attempt + 1}/{self.max_retries}): {e}"
                )
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue

        logger.error("すべてのトークン更新試行が失敗しました")
        return None

    def get_valid_token(self) -> Optional[str]:
        """有効なIDトークンを取得（環境変数に保存せず、一時保存のみ）"""
        logger.info("=== 有効なトークン取得開始（環境変数非依存版） ===")

        # 1. 一時キャッシュからトークンを取得
        cache = self.load_temp_token_cache()
        if cache and cache.get("id_token"):
            self.temp_id_token = cache["id_token"]
            self.temp_refresh_token = cache.get("refresh_token")
            logger.info("一時キャッシュからトークンを取得しました")

        # 2. 現在のトークンが有効かチェック
        if (
            self.temp_id_token
            and self.is_token_valid(self.temp_id_token)
            and self.test_token_with_api(self.temp_id_token)
        ):
            logger.info("一時保存されたトークンは有効です")
            return self.temp_id_token

        # 3. リフレッシュトークンで更新を試行
        if self.temp_refresh_token:
            logger.info("リフレッシュトークンで更新を試行...")
            new_id_token = self.refresh_id_token(self.temp_refresh_token)
            if new_id_token:
                self.temp_id_token = new_id_token
                if self.test_token_with_api(new_id_token):
                    logger.info("リフレッシュトークンでの更新に成功しました")
                    # 更新されたトークンを一時キャッシュに保存
                    self.save_temp_token_cache(
                        {
                            "id_token": new_id_token,
                            "refresh_token": self.temp_refresh_token,
                        }
                    )
                    return new_id_token

        # 4. メールアドレスとパスワードで新規取得
        logger.info("メールアドレスとパスワードで新規認証を試行...")
        new_tokens = self.get_new_tokens()
        if new_tokens:
            self.temp_id_token = new_tokens["id_token"]
            self.temp_refresh_token = new_tokens["refresh_token"]

            if self.test_token_with_api(self.temp_id_token):
                logger.info("新規認証に成功しました")
                return self.temp_id_token

        logger.error("すべての認証方法が失敗しました")
        return None

    def clear_temp_token_cache(self) -> bool:
        """一時トークンキャッシュをクリア"""
        try:
            if self.temp_token_cache_file.exists():
                self.temp_token_cache_file.unlink()
                logger.info("一時トークンキャッシュをクリアしました")
            return True
        except Exception as e:
            logger.error(f"一時トークンキャッシュクリアエラー: {e}")
            return False

    def get_current_token(self) -> Optional[str]:
        """現在の一時保存されたトークンを取得"""
        return self.temp_id_token


def main():
    """メイン処理"""
    logger.info("=== jQuants認証管理開始（環境変数非依存版） ===")

    auth_manager = JQuantsAuthManagerFinal()

    # 有効なトークンを取得
    valid_token = auth_manager.get_valid_token()

    if valid_token:
        logger.info("✅ 有効なトークンを取得しました")
        logger.info("注意: トークンは一時保存のみで、環境変数には保存されません")
        return 0
    else:
        logger.error("❌ 有効なトークンの取得に失敗しました")
        return 1


if __name__ == "__main__":
    exit(main())
