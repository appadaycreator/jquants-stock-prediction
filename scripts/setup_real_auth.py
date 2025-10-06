#!/usr/bin/env python3
"""
実際のjQuants API認証情報を設定するスクリプト
"""

import os
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))


def setup_real_auth():
    """実際の認証情報を設定"""
    print("=== jQuants API認証情報設定 ===")
    print("実際のjQuants APIの認証情報を設定してください。")
    print("")
    print("注意: この情報は.envファイルに保存されます。")
    print("")

    # 現在の.envファイルを確認
    env_file = Path(".env")
    if env_file.exists():
        print("既存の.envファイルが見つかりました。")
        with open(env_file, "r", encoding="utf-8") as f:
            content = f.read()
            if "JQUANTS_EMAIL" in content:
                print("既に認証情報が設定されているようです。")
                overwrite = input("上書きしますか？ (y/N): ").strip().lower()
                if overwrite != "y":
                    print("設定をキャンセルしました。")
                    return False

    print("")
    print("認証方法を選択してください:")
    print("1. メールアドレスとパスワード（推奨）")
    print("2. IDトークン（直接設定）")

    choice = input("選択 (1-2): ").strip()

    if choice == "1":
        return setup_email_password()
    elif choice == "2":
        return setup_id_token()
    else:
        print("無効な選択です。")
        return False


def setup_email_password():
    """メールアドレスとパスワードで設定"""
    print("")
    print("jQuants APIの認証情報を入力してください:")
    print("（jQuants APIに登録済みのメールアドレスとパスワード）")
    print("")

    email = input("メールアドレス: ").strip()
    password = input("パスワード: ").strip()

    if not email or not password:
        print("メールアドレスとパスワードは必須です。")
        return False

    # 認証情報をテスト
    print("")
    print("認証情報をテスト中...")
    if test_credentials(email, password):
        print("✅ 認証情報のテストに成功しました")
        return save_env_config({"JQUANTS_EMAIL": email, "JQUANTS_PASSWORD": password})
    else:
        print("❌ 認証情報のテストに失敗しました")
        print("入力した認証情報を確認してください。")
        return False


def setup_id_token():
    """IDトークンで設定"""
    print("")
    print("IDトークンを入力してください:")
    print("（jQuants APIから取得したIDトークン）")
    print("")

    id_token = input("IDトークン: ").strip()

    if not id_token:
        print("IDトークンは必須です。")
        return False

    # IDトークンをテスト
    print("")
    print("IDトークンをテスト中...")
    if test_id_token(id_token):
        print("✅ IDトークンのテストに成功しました")
        return save_env_config({"JQUANTS_ID_TOKEN": id_token})
    else:
        print("❌ IDトークンのテストに失敗しました")
        print("入力したIDトークンを確認してください。")
        return False


def test_credentials(email, password):
    """認証情報をテスト"""
    try:
        import requests

        # 認証リクエスト
        auth_data = {"mailaddress": email, "password": password}
        response = requests.post(
            "https://api.jquants.com/v1/token/auth_user", json=auth_data, timeout=30
        )

        if response.status_code == 200:
            auth_result = response.json()
            refresh_token = auth_result.get("refreshToken")

            if refresh_token:
                # IDトークンを取得
                refresh_response = requests.post(
                    f"https://api.jquants.com/v1/token/auth_refresh?refreshtoken={refresh_token}",
                    timeout=30,
                )

                if refresh_response.status_code == 200:
                    refresh_result = refresh_response.json()
                    id_token = refresh_result.get("idToken")

                    if id_token:
                        # トークンを保存
                        save_env_config(
                            {
                                "JQUANTS_EMAIL": email,
                                "JQUANTS_PASSWORD": password,
                                "JQUANTS_ID_TOKEN": id_token,
                                "JQUANTS_REFRESH_TOKEN": refresh_token,
                            }
                        )
                        return True

        print(f"認証エラー: HTTP {response.status_code}")
        print(f"レスポンス: {response.text}")
        return False

    except Exception as e:
        print(f"認証エラー: {e}")
        return False


def test_id_token(id_token):
    """IDトークンをテスト"""
    try:
        import requests

        headers = {"Authorization": f"Bearer {id_token}"}
        response = requests.get(
            "https://api.jquants.com/v1/listed/info", headers=headers, timeout=10
        )

        if response.status_code == 200:
            return True
        else:
            print(f"APIテスト失敗: HTTP {response.status_code}")
            return False

    except Exception as e:
        print(f"APIテストエラー: {e}")
        return False


def save_env_config(config):
    """環境変数ファイルに設定を保存"""
    try:
        env_file = Path(".env")
        env_content = []

        # 既存の.envファイルを読み込み
        if env_file.exists():
            with open(env_file, "r", encoding="utf-8") as f:
                env_content = f.readlines()

        # 設定を更新
        updated_lines = []
        for line in env_content:
            updated = False
            for key, value in config.items():
                if line.startswith(f"{key}="):
                    updated_lines.append(f"{key}={value}\n")
                    updated = True
                    break
            if not updated:
                updated_lines.append(line)

        # 新しい設定を追加
        for key, value in config.items():
            if not any(line.startswith(f"{key}=") for line in updated_lines):
                updated_lines.append(f"{key}={value}\n")

        # ファイルに書き込み
        with open(env_file, "w", encoding="utf-8") as f:
            f.writelines(updated_lines)

        print(f"✅ 認証情報を.envファイルに保存しました")
        return True

    except Exception as e:
        print(f"❌ 設定保存エラー: {e}")
        return False


def main():
    """メイン処理"""
    print("jQuants API認証情報設定ツール")
    print("=" * 40)

    # 認証情報を設定
    if setup_real_auth():
        print("")
        print("🎉 認証情報の設定が完了しました！")
        print("これで jQuants API を使用できます。")
        return 0
    else:
        print("")
        print("❌ 認証情報の設定に失敗しました。")
        return 1


if __name__ == "__main__":
    exit(main())
