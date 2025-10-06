#!/usr/bin/env python3
"""
jQuants認証情報設定スクリプト
認証情報の設定とテストを行う
"""

import os
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))


def setup_auth_interactive():
    """対話的に認証情報を設定"""
    print("=== jQuants認証情報設定 ===")
    print("jQuants APIの認証情報を設定してください。")
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
    print("1. メールアドレスとパスワード")
    print("2. IDトークン（直接設定）")
    print("3. テスト用のサンプル設定")

    choice = input("選択 (1-3): ").strip()

    if choice == "1":
        return setup_email_password()
    elif choice == "2":
        return setup_id_token()
    elif choice == "3":
        return setup_test_config()
    else:
        print("無効な選択です。")
        return False


def setup_email_password():
    """メールアドレスとパスワードで設定"""
    print("")
    print("メールアドレスとパスワードを入力してください:")
    email = input("メールアドレス: ").strip()
    password = input("パスワード: ").strip()

    if not email or not password:
        print("メールアドレスとパスワードは必須です。")
        return False

    return save_env_config({"JQUANTS_EMAIL": email, "JQUANTS_PASSWORD": password})


def setup_id_token():
    """IDトークンで設定"""
    print("")
    print("IDトークンを入力してください:")
    id_token = input("IDトークン: ").strip()

    if not id_token:
        print("IDトークンは必須です。")
        return False

    return save_env_config({"JQUANTS_ID_TOKEN": id_token})


def setup_test_config():
    """テスト用設定"""
    print("")
    print("テスト用の設定を行います。")
    print("注意: これは実際のAPIには接続されません。")

    return save_env_config(
        {
            "JQUANTS_EMAIL": "test@example.com",
            "JQUANTS_PASSWORD": "test_password",
            "JQUANTS_ID_TOKEN": "test_token",
        }
    )


def save_env_config(config: dict) -> bool:
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


def test_auth():
    """認証情報をテスト"""
    print("")
    print("=== 認証情報テスト ===")

    try:
        from jquants_auth_manager_enhanced import JQuantsAuthManagerEnhanced

        auth_manager = JQuantsAuthManagerEnhanced()
        valid_token = auth_manager.get_valid_token()

        if valid_token:
            print("✅ 認証テスト成功: 有効なトークンを取得しました")
            return True
        else:
            print("❌ 認証テスト失敗: 有効なトークンを取得できませんでした")
            return False

    except Exception as e:
        print(f"❌ 認証テストエラー: {e}")
        return False


def main():
    """メイン処理"""
    print("jQuants認証情報設定ツール")
    print("=" * 40)

    # 認証情報を設定
    if not setup_auth_interactive():
        print("認証情報の設定に失敗しました。")
        return 1

    # 認証情報をテスト
    if test_auth():
        print("")
        print("🎉 認証情報の設定が完了しました！")
        print("これで jQuants API を使用できます。")
        return 0
    else:
        print("")
        print("⚠️  認証情報の設定は完了しましたが、テストに失敗しました。")
        print("設定した認証情報を確認してください。")
        return 1


if __name__ == "__main__":
    exit(main())
