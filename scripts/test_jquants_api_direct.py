#!/usr/bin/env python3
"""
jQuants APIを直接叩いて動作確認
"""

import requests
import json
import time
from datetime import datetime

def test_jquants_api():
    """jQuants APIの直接テスト"""
    print("=== jQuants API直接テスト ===")
    print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 基本設定
    base_url = "https://api.jquants.com/v1"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "jQuants-API-Test/1.0"
    }
    
    # 1. 認証エンドポイントのテスト
    print("1. 認証エンドポイントのテスト")
    print("-" * 40)
    
    # 認証情報（テスト用）
    test_email = "test@example.com"
    test_password = "test_password"
    
    auth_url = f"{base_url}/token/auth_user"
    auth_data = {
        "mailaddress": test_email,
        "password": test_password
    }
    
    try:
        print(f"認証URL: {auth_url}")
        print(f"認証データ: {json.dumps(auth_data, indent=2)}")
        
        response = requests.post(auth_url, json=auth_data, headers=headers, timeout=30)
        print(f"レスポンスステータス: {response.status_code}")
        print(f"レスポンスヘッダー: {dict(response.headers)}")
        
        if response.status_code == 200:
            auth_result = response.json()
            print(f"認証成功: {json.dumps(auth_result, indent=2, ensure_ascii=False)}")
            
            # リフレッシュトークンでIDトークンを取得
            refresh_token = auth_result.get("refreshToken")
            if refresh_token:
                print(f"\nリフレッシュトークン取得: {refresh_token[:50]}...")
                
                # IDトークンを取得
                refresh_url = f"{base_url}/token/auth_refresh?refreshtoken={refresh_token}"
                print(f"リフレッシュURL: {refresh_url}")
                
                refresh_response = requests.post(refresh_url, headers=headers, timeout=30)
                print(f"リフレッシュレスポンス: {refresh_response.status_code}")
                
                if refresh_response.status_code == 200:
                    refresh_result = refresh_response.json()
                    print(f"IDトークン取得成功: {json.dumps(refresh_result, indent=2, ensure_ascii=False)}")
                    
                    id_token = refresh_result.get("idToken")
                    if id_token:
                        print(f"\nIDトークン: {id_token[:50]}...")
                        
                        # IDトークンでAPIをテスト
                        test_api_with_token(id_token, base_url)
                    else:
                        print("❌ IDトークンの取得に失敗しました")
                else:
                    print(f"❌ IDトークン取得エラー: {refresh_response.text}")
            else:
                print("❌ リフレッシュトークンの取得に失敗しました")
        else:
            print(f"❌ 認証エラー: {response.text}")
            
    except Exception as e:
        print(f"❌ 認証テストエラー: {e}")
    
    print("\n" + "=" * 60)
    
    # 2. 公開エンドポイントのテスト（認証不要）
    print("2. 公開エンドポイントのテスト（認証不要）")
    print("-" * 40)
    
    test_public_endpoints(base_url, headers)
    
    print("\n" + "=" * 60)
    
    # 3. 認証が必要なエンドポイントのテスト
    print("3. 認証が必要なエンドポイントのテスト")
    print("-" * 40)
    
    # 実際のIDトークンがある場合はテスト
    test_authenticated_endpoints(base_url, headers)

def test_api_with_token(id_token, base_url):
    """IDトークンでAPIをテスト"""
    print(f"\n--- IDトークンでAPIテスト ---")
    
    auth_headers = {
        "Authorization": f"Bearer {id_token}",
        "Content-Type": "application/json",
        "User-Agent": "jQuants-API-Test/1.0"
    }
    
    # 上場企業情報を取得
    test_url = f"{base_url}/listed/info"
    print(f"テストURL: {test_url}")
    
    try:
        response = requests.get(test_url, headers=auth_headers, timeout=30)
        print(f"レスポンスステータス: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ APIテスト成功")
            print(f"データ件数: {len(data.get('info', []))}")
            if data.get('info'):
                print(f"サンプルデータ: {json.dumps(data['info'][0], indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ APIテスト失敗: {response.text}")
            
    except Exception as e:
        print(f"❌ APIテストエラー: {e}")

def test_public_endpoints(base_url, headers):
    """公開エンドポイントをテスト"""
    public_endpoints = [
        "/markets/calendar",
        "/markets/calendar/2024",
        "/markets/calendar/2024/01"
    ]
    
    for endpoint in public_endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\nテストエンドポイント: {endpoint}")
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"ステータス: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 成功: {len(data.get('calendar', []))}件のデータ")
            else:
                print(f"❌ 失敗: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ エラー: {e}")
        
        time.sleep(1)  # API制限を考慮

def test_authenticated_endpoints(base_url, headers):
    """認証が必要なエンドポイントをテスト"""
    # 実際のIDトークンが設定されている場合のテスト
    print("認証が必要なエンドポイントのテストは、有効なIDトークンが必要です。")
    print("実際のjQuants APIの認証情報を設定してから実行してください。")

def test_api_limits():
    """API制限のテスト"""
    print("\n--- API制限のテスト ---")
    
    base_url = "https://api.jquants.com/v1"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "jQuants-API-Test/1.0"
    }
    
    # 連続リクエストのテスト
    for i in range(5):
        try:
            url = f"{base_url}/markets/calendar"
            response = requests.get(url, headers=headers, timeout=10)
            print(f"リクエスト {i+1}: ステータス {response.status_code}")
            
            if response.status_code == 429:
                print("⚠️ レート制限に達しました")
                break
                
        except Exception as e:
            print(f"リクエスト {i+1}: エラー {e}")
        
        time.sleep(0.5)  # 0.5秒間隔

def main():
    """メイン処理"""
    print("jQuants API直接テストツール")
    print("=" * 60)
    
    # 基本APIテスト
    test_jquants_api()
    
    # API制限テスト
    print("\n" + "=" * 60)
    print("4. API制限のテスト")
    print("-" * 40)
    test_api_limits()
    
    print("\n" + "=" * 60)
    print("テスト完了")
    print("=" * 60)

if __name__ == "__main__":
    main()
