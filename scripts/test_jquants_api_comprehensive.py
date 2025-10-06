#!/usr/bin/env python3
"""
jQuants API包括的テスト
実際の認証情報を使用してAPIの動作を確認
"""

import os
import pytest
import requests
import json
import time
from datetime import datetime
from pathlib import Path


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
    """認証情報の確認"""
    print("=== 認証情報確認 ===")

    email = os.getenv("JQUANTS_EMAIL")
    password = os.getenv("JQUANTS_PASSWORD")
    id_token = os.getenv("JQUANTS_ID_TOKEN")

    print(f"メールアドレス: {email}")
    print(f"パスワード: {'設定済み' if password else '未設定'}")
    print(f"IDトークン: {'設定済み' if id_token else '未設定'}")

    # 認証情報が設定されていない場合
    if not email and not password and not id_token:
        print("\n❌ 認証情報が設定されていません")
        print("設定方法:")
        print("1. .envファイルを編集してJQUANTS_EMAILとJQUANTS_PASSWORDを設定")
        print("2. または、JQUANTS_ID_TOKENを直接設定")
        print("3. GitHub Actionsの場合は、Repository Secretsに設定")
        return False

    # IDトークンが直接設定されている場合は、メール/パスワードは不要
    if id_token and (not email or not password):
        print("\n✅ IDトークンが直接設定されています")
        print("メール/パスワード認証はスキップします")
        return True

    # テスト用のダミー値かチェック
    is_dummy = (
        email == "test@example.com"
        or password == "test_password"
        or id_token == "demo_id_token_12345"
    )

    if is_dummy:
        print("\n⚠️  テスト用のダミー値が設定されています。")
        print("実際のjQuants APIの認証情報を設定してください。")
        return False

    return True


@pytest.mark.skipif(
    not os.getenv("JQUANTS_ID_TOKEN")
    and not (os.getenv("JQUANTS_EMAIL") and os.getenv("JQUANTS_PASSWORD")),
    reason="実環境の認証情報が未設定のためスキップ",
)
def test_id_token_validity():
    """IDトークンの有効性をテスト"""
    id_token = os.getenv("JQUANTS_ID_TOKEN")
    if not id_token:
        # メール/パスワードで取得を試みる
        email = os.getenv("JQUANTS_EMAIL")
        password = os.getenv("JQUANTS_PASSWORD")
        id_token = perform_email_password_auth(email, password) if email and password else None
        assert id_token, "IDトークン取得に失敗しました"
    try:
        headers = {
            "Authorization": f"Bearer {id_token}",
            "Content-Type": "application/json",
            "User-Agent": "jQuants-API-Test/1.0",
        }

        # 簡単なAPI呼び出しでトークンの有効性をテスト
        test_url = "https://api.jquants.com/v1/listed/info"
        response = requests.get(test_url, headers=headers, timeout=10)

        if response.status_code == 200:
            return True
        else:
            print(f"IDトークンテスト失敗: {response.status_code}")
            return False

    except Exception as e:
        print(f"IDトークンテストエラー: {e}")
        return False


def perform_email_password_auth(email, password):
    """メール/パスワード認証を実行"""
    try:
        print("1. 認証リクエスト送信...")
        auth_url = "https://api.jquants.com/v1/token/auth_user"
        auth_data = {"mailaddress": email, "password": password}

        response = requests.post(auth_url, json=auth_data, timeout=30)
        print(f"認証レスポンス: {response.status_code}")

        if response.status_code == 200:
            auth_result = response.json()
            print("✅ 認証成功")

            refresh_token = auth_result.get("refreshToken")
            if refresh_token:
                print(f"リフレッシュトークン: {refresh_token[:50]}...")

                # ステップ2: IDトークン取得
                print("\n2. IDトークン取得...")
                refresh_url = f"https://api.jquants.com/v1/token/auth_refresh?refreshtoken={refresh_token}"

                refresh_response = requests.post(refresh_url, timeout=30)
                print(f"IDトークン取得レスポンス: {refresh_response.status_code}")

                if refresh_response.status_code == 200:
                    refresh_result = refresh_response.json()
                    print("✅ IDトークン取得成功")

                    id_token = refresh_result.get("idToken")
                    if id_token:
                        print(f"IDトークン: {id_token[:50]}...")
                        return id_token
                    else:
                        print("❌ IDトークンが取得できませんでした")
                else:
                    print(f"❌ IDトークン取得失敗: {refresh_response.text}")
            else:
                print("❌ リフレッシュトークンが取得できませんでした")
        else:
            print(f"❌ 認証失敗: {response.text}")

    except Exception as e:
        print(f"❌ 認証エラー: {e}")

    return None


def test_authentication_flow():
    """認証フローのテスト"""
    print("\n=== 認証フローテスト ===")

    email = os.getenv("JQUANTS_EMAIL")
    password = os.getenv("JQUANTS_PASSWORD")
    id_token = os.getenv("JQUANTS_ID_TOKEN")

    # IDトークンが直接設定されている場合は、有効性をチェック
    if id_token:
        print("✅ IDトークンが直接設定されています")
        print("IDトークンの有効性をチェックします...")

        # IDトークンの有効性をテスト
        if test_id_token_validity(id_token):
            print("✅ IDトークンが有効です")
            return id_token
        else:
            print("⚠️ IDトークンが無効または期限切れです")
            print("メール/パスワード認証を試行します...")
            # メール/パスワード認証にフォールバック
            if email and password:
                return perform_email_password_auth(email, password)
            else:
                print("❌ メール/パスワード認証情報も設定されていません")
                return None

    if not email or not password:
        print("❌ 認証情報が設定されていません")
        return None

    # メール/パスワード認証を実行
    return perform_email_password_auth(email, password)


@pytest.mark.skipif(
    not os.getenv("JQUANTS_ID_TOKEN")
    and not (os.getenv("JQUANTS_EMAIL") and os.getenv("JQUANTS_PASSWORD")),
    reason="実環境の認証情報が未設定のためスキップ",
)
def test_api_endpoints():
    """APIエンドポイントのテスト"""
    print("\n=== APIエンドポイントテスト ===")

    # IDトークンを取得（認証フローから取得）
    id_token = test_authentication_flow()
    if not id_token:
        print("❌ IDトークンが提供されていません")
        assert False

    base_url = "https://api.jquants.com/v1"
    headers = {
        "Authorization": f"Bearer {id_token}",
        "Content-Type": "application/json",
        "User-Agent": "jQuants-API-Test/1.0",
    }

    # テストするエンドポイント
    endpoints = [
        {
            "name": "上場企業情報",
            "url": f"{base_url}/listed/info",
            "method": "GET",
            "params": None,
        },
        {
            "name": "市場カレンダー",
            "url": f"{base_url}/markets/calendar",
            "method": "GET",
            "params": None,
        },
        {
            "name": "2024年市場カレンダー",
            "url": f"{base_url}/markets/calendar/2024",
            "method": "GET",
            "params": None,
        },
        {
            "name": "2024年1月市場カレンダー",
            "url": f"{base_url}/markets/calendar/2024/01",
            "method": "GET",
            "params": None,
        },
    ]

    for endpoint in endpoints:
        print(f"\n--- {endpoint['name']} ---")
        print(f"URL: {endpoint['url']}")

        try:
            if endpoint["method"] == "GET":
                response = requests.get(endpoint["url"], headers=headers, timeout=30)
            else:
                response = requests.post(endpoint["url"], headers=headers, timeout=30)

            print(f"ステータス: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print("✅ 成功")

                # データの概要を表示
                if isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, list):
                            print(f"  {key}: {len(value)}件")
                        else:
                            print(f"  {key}: {value}")
                elif isinstance(data, list):
                    print(f"  データ件数: {len(data)}")

                # サンプルデータを表示（最初の1件）
                if isinstance(data, dict) and "info" in data and data["info"]:
                    print(
                        f"  サンプルデータ: {json.dumps(data['info'][0], indent=2, ensure_ascii=False)}"
                    )
                elif isinstance(data, list) and data:
                    print(
                        f"  サンプルデータ: {json.dumps(data[0], indent=2, ensure_ascii=False)}"
                    )

            elif response.status_code == 401:
                print("❌ 認証エラー (401)")
            elif response.status_code == 403:
                print("❌ アクセス拒否 (403)")
            elif response.status_code == 404:
                print("❌ エンドポイントが見つかりません (404)")
            else:
                print(f"❌ エラー: {response.text[:200]}")

        except Exception as e:
            print(f"❌ リクエストエラー: {e}")

        time.sleep(1)  # API制限を考慮


@pytest.mark.skipif(
    not os.getenv("JQUANTS_ID_TOKEN")
    and not (os.getenv("JQUANTS_EMAIL") and os.getenv("JQUANTS_PASSWORD")),
    reason="実環境の認証情報が未設定のためスキップ",
)
def test_data_endpoints():
    """データ取得エンドポイントのテスト"""
    print("\n=== データ取得エンドポイントテスト ===")

    # IDトークンを取得（認証フローから取得）
    id_token = test_authentication_flow()
    if not id_token:
        print("❌ IDトークンが提供されていません")
        assert False

    base_url = "https://api.jquants.com/v1"
    headers = {
        "Authorization": f"Bearer {id_token}",
        "Content-Type": "application/json",
        "User-Agent": "jQuants-API-Test/1.0",
    }

    # 株価データ取得エンドポイント
    data_endpoints = [
        {
            "name": "日次株価データ",
            "url": f"{base_url}/prices/daily_quotes",
            "params": {"date": "2024-01-01", "code": "7203"},
        },
        {
            "name": "午前株価データ",
            "url": f"{base_url}/prices/prices_am",
            "params": {"date": "2024-01-01", "code": "7203"},
        },
        {
            "name": "午後株価データ",
            "url": f"{base_url}/prices/prices_pm",
            "params": {"date": "2024-01-01", "code": "7203"},
        },
        {
            "name": "財務データ",
            "url": f"{base_url}/prices/fins",
            "params": {"date": "2024-01-01", "code": "7203"},
        },
    ]

    for endpoint in data_endpoints:
        print(f"\n--- {endpoint['name']} ---")
        print(f"URL: {endpoint['url']}")
        print(f"パラメータ: {endpoint['params']}")

        try:
            response = requests.get(
                endpoint["url"], headers=headers, params=endpoint["params"], timeout=30
            )
            print(f"ステータス: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print("✅ 成功")

                if isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, list):
                            print(f"  {key}: {len(value)}件")
                        else:
                            print(f"  {key}: {value}")

            elif response.status_code == 401:
                print("❌ 認証エラー (401)")
            elif response.status_code == 403:
                print("❌ アクセス拒否 (403)")
            elif response.status_code == 404:
                print("❌ エンドポイントが見つかりません (404)")
            else:
                print(f"❌ エラー: {response.text[:200]}")

        except Exception as e:
            print(f"❌ リクエストエラー: {e}")

        time.sleep(2)  # API制限を考慮


@pytest.mark.skipif(
    not os.getenv("JQUANTS_ID_TOKEN")
    and not (os.getenv("JQUANTS_EMAIL") and os.getenv("JQUANTS_PASSWORD")),
    reason="実環境の認証情報が未設定のためスキップ",
)
def test_rate_limits():
    """レート制限のテスト"""
    print("\n=== レート制限テスト ===")

    # IDトークンを取得（認証フローから取得）
    id_token = test_authentication_flow()
    if not id_token:
        print("❌ IDトークンが提供されていません")
        assert False

    base_url = "https://api.jquants.com/v1"
    headers = {
        "Authorization": f"Bearer {id_token}",
        "Content-Type": "application/json",
        "User-Agent": "jQuants-API-Test/1.0",
    }

    # 連続リクエストのテスト
    url = f"{base_url}/listed/info"

    for i in range(5):
        try:
            print(f"リクエスト {i+1}/5...")
            response = requests.get(url, headers=headers, timeout=10)
            print(f"  ステータス: {response.status_code}")

            if response.status_code == 429:
                print("⚠️ レート制限に達しました")
                break
            elif response.status_code == 200:
                data = response.json()
                print(f"  データ件数: {len(data.get('info', []))}")

        except Exception as e:
            print(f"  エラー: {e}")

        time.sleep(0.5)  # 0.5秒間隔


def main():
    """メイン処理"""
    print("jQuants API包括的テスト")
    print("=" * 60)
    print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 環境変数を読み込み
    load_env()

    # 認証情報の確認
    if not check_auth_info():
        print("\n実際のjQuants APIの認証情報を設定してください。")
        print("設定方法:")
        print("1. .envファイルを編集してJQUANTS_EMAILとJQUANTS_PASSWORDを設定")
        print("2. または、JQUANTS_ID_TOKENを直接設定")
        print("3. GitHub Actionsの場合は、Repository Secretsに設定")
        return 1

    # 認証フローのテスト
    id_token = test_authentication_flow()
    if not id_token:
        print("\n❌ 認証に失敗しました。認証情報を確認してください。")
        return 1

    # APIエンドポイントのテスト
    test_api_endpoints()

    # データ取得エンドポイントのテスト
    test_data_endpoints()

    # レート制限のテスト
    test_rate_limits()

    print("\n" + "=" * 60)
    print("テスト完了")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    exit(main())
