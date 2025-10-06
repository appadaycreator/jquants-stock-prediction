#!/usr/bin/env python3
"""
実際の認証情報でjQuants APIをテスト
"""

import os
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


def test_authentication():
    """認証テスト"""
    print("=== 認証テスト ===")

    email = os.getenv("JQUANTS_EMAIL")
    password = os.getenv("JQUANTS_PASSWORD")

    if not email or not password:
        print("❌ 認証情報が設定されていません")
        return None

    print(f"メールアドレス: {email}")
    print(f"パスワード: {'*' * len(password)}")

    # 認証リクエスト
    auth_url = "https://api.jquants.com/v1/token/auth_user"
    auth_data = {"mailaddress": email, "password": password}

    try:
        print("認証中...")
        response = requests.post(auth_url, json=auth_data, timeout=30)
        print(f"認証レスポンス: {response.status_code}")

        if response.status_code == 200:
            auth_result = response.json()
            print("✅ 認証成功")
            print(f"レスポンス: {json.dumps(auth_result, indent=2, ensure_ascii=False)}")

            refresh_token = auth_result.get("refreshToken")
            if refresh_token:
                print(f"リフレッシュトークン: {refresh_token[:50]}...")
                return refresh_token
            else:
                print("❌ リフレッシュトークンが取得できませんでした")
        else:
            print(f"❌ 認証失敗: {response.text}")

    except Exception as e:
        print(f"❌ 認証エラー: {e}")

    return None


def get_id_token(refresh_token):
    """IDトークンを取得"""
    print("\n=== IDトークン取得 ===")

    refresh_url = (
        f"https://api.jquants.com/v1/token/auth_refresh?refreshtoken={refresh_token}"
    )

    try:
        print("IDトークン取得中...")
        response = requests.post(refresh_url, timeout=30)
        print(f"IDトークン取得レスポンス: {response.status_code}")

        if response.status_code == 200:
            refresh_result = response.json()
            print("✅ IDトークン取得成功")
            print(f"レスポンス: {json.dumps(refresh_result, indent=2, ensure_ascii=False)}")

            id_token = refresh_result.get("idToken")
            if id_token:
                print(f"IDトークン: {id_token[:50]}...")
                return id_token
            else:
                print("❌ IDトークンが取得できませんでした")
        else:
            print(f"❌ IDトークン取得失敗: {response.text}")

    except Exception as e:
        print(f"❌ IDトークン取得エラー: {e}")

    return None


def test_api_endpoints():
    """APIエンドポイントをテスト"""
    print("\n=== APIエンドポイントテスト ===")

    # IDトークンを取得（認証フローから取得）
    refresh_token = test_authentication()
    if not refresh_token:
        print("❌ 認証に失敗しました")
        return False
    id_token = get_id_token(refresh_token)
    if not id_token:
        print("❌ IDトークンが提供されていません")
        return False

    base_url = "https://api.jquants.com/v1"
    headers = {
        "Authorization": f"Bearer {id_token}",
        "Content-Type": "application/json",
        "User-Agent": "jQuants-API-Test/1.0",
    }

    # テストするエンドポイント
    endpoints = [
        "/listed/info",
        "/markets/calendar",
        "/markets/calendar/2024",
        "/markets/calendar/2024/01",
    ]

    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\n--- {endpoint} ---")
        print(f"URL: {url}")

        try:
            response = requests.get(url, headers=headers, timeout=30)
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


def test_data_endpoints():
    """データ取得エンドポイントをテスト"""
    print("\n=== データ取得エンドポイントテスト ===")

    # IDトークンを取得（認証フローから取得）
    refresh_token = test_authentication()
    if not refresh_token:
        print("❌ 認証に失敗しました")
        return False
    id_token = get_id_token(refresh_token)
    if not id_token:
        print("❌ IDトークンが提供されていません")
        return False

    base_url = "https://api.jquants.com/v1"
    headers = {
        "Authorization": f"Bearer {id_token}",
        "Content-Type": "application/json",
        "User-Agent": "jQuants-API-Test/1.0",
    }

    # 株価データ取得エンドポイント
    data_endpoints = [
        "/prices/daily_quotes",
        "/prices/prices_am",
        "/prices/prices_pm",
        "/prices/statements",
        "/prices/fins",
        "/prices/option",
        "/prices/index_option",
        "/prices/fx_rates",
    ]

    for endpoint in data_endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\n--- {endpoint} ---")

        try:
            # パラメータを付けてテスト
            params = {"date": "2024-01-01", "code": "7203"}  # トヨタ自動車

            response = requests.get(url, headers=headers, params=params, timeout=30)
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


def main():
    """メイン処理"""
    print("jQuants API実認証テスト")
    print("=" * 60)
    print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 環境変数を読み込み
    load_env()

    # 認証テスト
    refresh_token = test_authentication()
    if not refresh_token:
        print("\n❌ 認証に失敗しました。認証情報を確認してください。")
        return 1

    # IDトークン取得
    id_token = get_id_token(refresh_token)
    if not id_token:
        print("\n❌ IDトークンの取得に失敗しました。")
        return 1

    # APIエンドポイントテスト
    test_api_endpoints()

    # データ取得エンドポイントテスト
    test_data_endpoints()

    print("\n" + "=" * 60)
    print("テスト完了")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    exit(main())
