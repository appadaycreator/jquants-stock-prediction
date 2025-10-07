#!/usr/bin/env python3
"""
環境に応じた認証情報管理システム
ローカル環境: .envファイル
本番環境: GitHub Secrets
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# ログ設定
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class EnvironmentAuthManager:
    """環境に応じた認証情報管理クラス"""

    def __init__(self):
        self.environment = self._detect_environment()
        self.auth_info = self._load_auth_info()

    def _detect_environment(self) -> str:
        """環境を検出"""
        # 環境変数で明示的に設定されている場合を最優先
        env = os.getenv("ENVIRONMENT", "").lower()
        if env in ["development", "staging", "production"]:
            return env

        # GitHub Actions環境かチェック
        if os.getenv("GITHUB_ACTIONS") == "true":
            return "production"

        # デフォルトは開発環境
        return "development"

    def _load_auth_info(self) -> Dict[str, Optional[str]]:
        """認証情報を環境に応じて読み込み"""
        auth_info = {
            "email": None,
            "password": None,
            "id_token": None,
            "refresh_token": None,
        }

        if self.environment == "production":
            # 本番環境: GitHub Secretsから読み込み
            auth_info = self._load_from_github_secrets()
        else:
            # ローカル環境: .envファイルから読み込み
            auth_info = self._load_from_env_file()

        return auth_info

    def _load_from_github_secrets(self) -> Dict[str, Optional[str]]:
        """GitHub Secretsから認証情報を読み込み"""
        logger.info("本番環境: GitHub Secretsから認証情報を読み込み")

        return {
            "email": os.getenv("JQUANTS_EMAIL"),
            "password": os.getenv("JQUANTS_PASSWORD"),
            "id_token": os.getenv("JQUANTS_ID_TOKEN"),
            "refresh_token": os.getenv("JQUANTS_REFRESH_TOKEN"),
        }

    def _load_from_env_file(self) -> Dict[str, Optional[str]]:
        """ローカル環境: .envファイルから認証情報を読み込み"""
        logger.info("ローカル環境: .envファイルから認証情報を読み込み")

        # .envファイルを読み込み
        env_file = Path(".env")
        if env_file.exists():
            try:
                from dotenv import load_dotenv

                load_dotenv()
            except (ImportError, OSError, IOError) as e:
                # dotenvがインストールされていない場合やエラーが発生した場合は手動で読み込み
                logger.warning(f".envファイル読み込みエラー: {e}")
                try:
                    self._load_env_manually(env_file)
                except (OSError, IOError) as manual_error:
                    logger.warning(f"手動読み込みも失敗: {manual_error}")

        return {
            "email": os.getenv("JQUANTS_EMAIL"),
            "password": os.getenv("JQUANTS_PASSWORD"),
            "id_token": os.getenv("JQUANTS_ID_TOKEN"),
            "refresh_token": os.getenv("JQUANTS_REFRESH_TOKEN"),
        }

    def _load_env_manually(self, env_file: Path):
        """手動で.envファイルを読み込み"""
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ[key] = value
        except Exception as e:
            logger.warning(f".envファイル読み込みエラー: {e}")

    def get_auth_info(self) -> Dict[str, Optional[str]]:
        """認証情報を取得"""
        return self.auth_info.copy()

    def get_email(self) -> Optional[str]:
        """メールアドレスを取得"""
        return self.auth_info.get("email")

    def get_password(self) -> Optional[str]:
        """パスワードを取得"""
        return self.auth_info.get("password")

    def get_id_token(self) -> Optional[str]:
        """IDトークンを取得"""
        return self.auth_info.get("id_token")

    def get_refresh_token(self) -> Optional[str]:
        """リフレッシュトークンを取得"""
        return self.auth_info.get("refresh_token")

    def is_auth_configured(self) -> bool:
        """認証情報が設定されているかチェック"""
        email = self.get_email()
        password = self.get_password()
        id_token = self.get_id_token()

        # メールアドレスとパスワード、またはIDトークンが設定されているかチェック
        return bool((email and password) or id_token)

    def is_dummy_auth(self) -> bool:
        """ダミーの認証情報かチェック"""
        email = self.get_email()
        password = self.get_password()
        id_token = self.get_id_token()
        refresh_token = self.get_refresh_token()

        dummy_values = [
            "test@example.com",
            "test_password",
            "demo_id_token_12345",
            "demo_refresh_token_67890",
        ]

        # ダミー値が含まれているかチェック
        return any(
            value in dummy_values
            for value in [email, password, id_token, refresh_token]
        )

    def validate_auth_info(self) -> Dict[str, Any]:
        """認証情報の検証結果を返す"""
        result = {
            "is_configured": self.is_auth_configured(),
            "is_dummy": self.is_dummy_auth(),
            "environment": self.environment,
            "has_email_password": bool(self.get_email() and self.get_password()),
            "has_id_token": bool(self.get_id_token()),
            "has_refresh_token": bool(self.get_refresh_token()),
        }

        return result

    def get_auth_status_message(self) -> str:
        """認証情報の状態メッセージを取得"""
        validation = self.validate_auth_info()

        if not validation["is_configured"]:
            return "❌ 認証情報が設定されていません"

        if validation["is_dummy"]:
            return "⚠️ ダミーの認証情報が設定されています。実際の認証情報を設定してください。"

        if validation["environment"] == "production":
            return "✅ 本番環境: GitHub Secretsから認証情報を読み込みました"
        else:
            return "✅ ローカル環境: .envファイルから認証情報を読み込みました"

    def create_env_template(self) -> str:
        """環境設定テンプレートを作成"""
        if self.environment == "production":
            return self._create_github_secrets_template()
        else:
            return self._create_local_env_template()

    def get_auth_status_summary(self) -> Dict[str, Any]:
        """認証ステータスのサマリーを取得"""
        validation = self.validate_auth_info()
        return {
            "is_configured": validation["is_configured"],
            "is_dummy": validation["is_dummy"],
            "environment": validation["environment"],
            "has_email": bool(self.get_email()),
            "has_password": bool(self.get_password()),
            "has_id_token": bool(self.get_id_token()),
            "has_refresh_token": bool(self.get_refresh_token()),
        }

    def _create_github_secrets_template(self) -> str:
        """GitHub Secrets設定テンプレート"""
        return """
# GitHub Secrets設定
# 以下のSecretsをGitHubリポジトリに設定してください:
#
# JQUANTS_EMAIL: jQuants APIのメールアドレス
# JQUANTS_PASSWORD: jQuants APIのパスワード
# JQUANTS_ID_TOKEN: (オプション) IDトークンを直接設定
# JQUANTS_REFRESH_TOKEN: (オプション) リフレッシュトークン
#
# 設定方法:
# 1. GitHubリポジトリの Settings > Secrets and variables > Actions
# 2. "New repository secret" をクリック
# 3. 上記のSecretsを追加
"""

    def _create_local_env_template(self) -> str:
        """ローカル環境設定テンプレート"""
        return """
# ローカル開発環境用 .env ファイル
# このファイルを .env にコピーして実際の値を設定してください

# 環境設定
ENVIRONMENT=development
DEBUG=true

# J-Quants API認証情報
JQUANTS_EMAIL=your_email@example.com
JQUANTS_PASSWORD=your_password
JQUANTS_ID_TOKEN=
JQUANTS_REFRESH_TOKEN=

# ログ設定
LOG_LEVEL=INFO
TIMEZONE=Asia/Tokyo

# API設定
API_TIMEOUT=30
MAX_RETRIES=3
RATE_LIMIT=100
"""


def main():
    """メイン処理"""
    print("=== 環境認証情報管理システム ===")

    auth_manager = EnvironmentAuthManager()

    # 認証情報の状態を表示
    print(f"環境: {auth_manager.environment}")
    print(f"認証情報状態: {auth_manager.get_auth_status_message()}")

    # 詳細情報を表示
    validation = auth_manager.validate_auth_info()
    print("\n詳細情報:")
    for key, value in validation.items():
        print(f"  {key}: {value}")

    # 認証情報の概要を表示（セキュリティのため一部マスク）
    auth_info = auth_manager.get_auth_info()
    print("\n認証情報:")
    print(f"  メールアドレス: {auth_info['email'] or '未設定'}")
    print(f"  パスワード: {'設定済み' if auth_info['password'] else '未設定'}")
    print(f"  IDトークン: {'設定済み' if auth_info['id_token'] else '未設定'}")
    print(
        f"  リフレッシュトークン: {'設定済み' if auth_info['refresh_token'] else '未設定'}"
    )

    # 設定テンプレートを表示
    print("\n設定テンプレート:")
    print(auth_manager.create_env_template())

    return 0


if __name__ == "__main__":
    exit(main())
