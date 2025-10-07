#!/usr/bin/env python3
"""
認証情報の設定状況を確認し、idTokenの取得テストを実行
"""

import os
import sys
import requests
from pathlib import Path
from datetime import datetime

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))


def load_env():
    """環境変数を読み込み"""
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


def check_auth_info():
    """認証情報の設定状況を確認"""
    print("=== 認証情報の設定状況確認 ===")

    email = os.getenv("JQUANTS_EMAIL")
    password = os.getenv("JQUANTS_PASSWORD")
    id_token = os.getenv("JQUANTS_ID_TOKEN")
    refresh_token = os.getenv("JQUANTS_REFRESH_TOKEN")

    print(f"メールアドレス: {email}")
    print(f"パスワード: {'設定済み' if password else '未設定'}")
    print(f"IDトークン: {'設定済み' if id_token else '未設定'}")
    print(f"リフレッシュトークン: {'設定済み' if refresh_token else '未設定'}")

    # テスト用のダミー値かチェック
    is_dummy = (
        email == "test@example.com"
        or password == "test_password"
        or id_token == "demo_id_token_12345"
        or refresh_token == "demo_refresh_token_67890"
    )

    if is_dummy:
        print("\n⚠️  テスト用のダミー値が設定されています。")
        print("実際のjQuants APIの認証情報を設定してください。")
        return False

    print("\n✅ 認証情報が設定されています。")
    return True


def test_id_token_validity(id_token):
    """IDトークンの有効性をテスト"""
    if not id_token:
        return False

    try:
        headers = {"Authorization": f"Bearer {id_token}"}
        response = requests.get(
            "https://api.jquants.com/v1/listed/info", headers=headers, timeout=10
        )

        if response.status_code == 200:
            print("✅ IDトークンは有効です")
            return True
        elif response.status_code == 401:
            print("❌ IDトークンは無効です（認証エラー）")
            return False
        else:
            print(f"❌ APIテスト失敗: HTTP {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ APIテストエラー: {e}")
        return False


def get_new_tokens(email, password):
    """メールアドレスとパスワードで新しいトークンを取得"""
    try:
        print("メールアドレスとパスワードで認証中...")

        # 認証リクエスト
        auth_data = {"mailaddress": email, "password": password}
        auth_response = requests.post(
            "https://api.jquants.com/v1/token/auth_user", json=auth_data, timeout=30
        )

        if auth_response.status_code == 200:
            auth_result = auth_response.json()
            refresh_token = auth_result.get("refreshToken")

            if not refresh_token:
                print("❌ リフレッシュトークンの取得に失敗しました")
                return None

            print("✅ リフレッシュトークンを取得しました")

            # IDトークンを取得
            refresh_response = requests.post(
                f"https://api.jquants.com/v1/token/auth_refresh?refreshtoken={refresh_token}",
                timeout=30,
            )

            if refresh_response.status_code == 200:
                refresh_result = refresh_response.json()
                id_token = refresh_result.get("idToken")

                if id_token:
                    print("✅ IDトークンを取得しました")
                    return {"id_token": id_token, "refresh_token": refresh_token}
                else:
                    print("❌ IDトークンの取得に失敗しました")
            else:
                print(f"❌ IDトークン取得エラー: HTTP {refresh_response.status_code}")
        else:
            print(f"❌ 認証エラー: HTTP {auth_response.status_code}")
            print(f"レスポンス: {auth_response.text}")

    except Exception as e:
        print(f"❌ 認証エラー: {e}")

    return None


def save_tokens_to_env(tokens):
    """トークンを環境変数ファイルに保存"""
    try:
        env_file = Path(".env")
        env_content = []

        # 既存の.envファイルを読み込み
        if env_file.exists():
            with open(env_file, "r", encoding="utf-8") as f:
                env_content = f.readlines()

        # トークンを更新
        updated_lines = []
        for line in env_content:
            if line.startswith("JQUANTS_ID_TOKEN="):
                updated_lines.append(f"JQUANTS_ID_TOKEN={tokens['id_token']}\n")
            elif line.startswith("JQUANTS_REFRESH_TOKEN="):
                updated_lines.append(
                    f"JQUANTS_REFRESH_TOKEN={tokens['refresh_token']}\n"
                )
            else:
                updated_lines.append(line)

        # 新しいトークンを追加（存在しない場合）
        if not any(line.startswith("JQUANTS_ID_TOKEN=") for line in updated_lines):
            updated_lines.append(f"JQUANTS_ID_TOKEN={tokens['id_token']}\n")
        if not any(line.startswith("JQUANTS_REFRESH_TOKEN=") for line in updated_lines):
            updated_lines.append(f"JQUANTS_REFRESH_TOKEN={tokens['refresh_token']}\n")

        # ファイルに書き込み
        with open(env_file, "w", encoding="utf-8") as f:
            f.writelines(updated_lines)

        print("✅ トークンを.envファイルに保存しました")
        return True

    except Exception as e:
        print(f"❌ トークン保存エラー: {e}")
        return False


def main():
    """メイン処理"""
    print("=== jQuants API認証情報確認・テスト ===")
    print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 環境変数を読み込み
    load_env()

    # 認証情報の設定状況を確認
    if not check_auth_info():
        print("\n実際のjQuants APIの認証情報を設定してください。")
        print("設定方法:")
        print("1. .envファイルを編集してJQUANTS_EMAILとJQUANTS_PASSWORDを設定")
        print("2. または、JQUANTS_ID_TOKENを直接設定")
        return 1

    # 現在のIDトークンをテスト
    id_token = os.getenv("JQUANTS_ID_TOKEN")
    if id_token and test_id_token_validity(id_token):
        print("\n✅ 認証テストが成功しました！")
        print("jQuants APIを使用できます。")
        return 0

    # IDトークンが無効な場合、メールアドレスとパスワードで新規認証
    email = os.getenv("JQUANTS_EMAIL")
    password = os.getenv("JQUANTS_PASSWORD")

    if email and password:
        print("\nIDトークンが無効なため、新規認証を試行します...")
        tokens = get_new_tokens(email, password)

        if tokens:
            if save_tokens_to_env(tokens):
                print("✅ 新しいトークンを取得し、保存しました")
                return 0
            else:
                print("❌ トークンの保存に失敗しました")
                return 1
        else:
            print("❌ 新規認証に失敗しました")
            return 1
    else:
        print("❌ メールアドレスとパスワードが設定されていません")
        return 1


if __name__ == "__main__":
    exit(main())
