#!/usr/bin/env python3
"""
実際の認証情報でjQuants APIの認証テストを実行
"""

import os
import sys
import requests
import json
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def test_jquants_auth():
    """jQuants APIの認証テスト"""
    print("=== jQuants API認証テスト ===")
    
    # 環境変数から認証情報を取得
    email = os.getenv("JQUANTS_EMAIL")
    password = os.getenv("JQUANTS_PASSWORD")
    id_token = os.getenv("JQUANTS_ID_TOKEN")
    
    print(f"メールアドレス: {email}")
    print(f"パスワード: {'*' * len(password) if password else 'None'}")
    print(f"IDトークン: {id_token[:50] + '...' if id_token else 'None'}")
    print()
    
    # 1. 既存のIDトークンが有効かテスト
    if id_token and id_token != "demo_id_token_12345":
        print("1. 既存のIDトークンでテスト...")
        if test_id_token(id_token):
            print("✅ 既存のIDトークンは有効です")
            assert True
        else:
            print("❌ 既存のIDトークンは無効です")
            assert False
    
    # 2. メールアドレスとパスワードで新規認証
    if email and password and email != "test@example.com":
        print("2. メールアドレスとパスワードで新規認証...")
        tokens = get_new_tokens(email, password)
        if tokens:
            print("✅ 新規認証に成功しました")
            print(f"IDトークン: {tokens['id_token'][:50]}...")
            print(f"リフレッシュトークン: {tokens['refresh_token'][:50]}...")
            assert True
        else:
            print("❌ 新規認証に失敗しました")
            assert False
    
    print("❌ すべての認証方法が失敗しました")
    assert False

def test_id_token():
    """IDトークンの有効性をテスト"""
    # 環境変数からIDトークンを取得
    id_token = os.getenv("JQUANTS_ID_TOKEN")
    if not id_token:
        print("❌ JQUANTS_ID_TOKEN環境変数が設定されていません")
        assert False
        
    try:
        headers = {"Authorization": f"Bearer {id_token}"}
        response = requests.get(
            "https://api.jquants.com/v1/listed/info",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("  APIテスト成功: トークンは有効です")
            assert True
        elif response.status_code == 401:
            print("  APIテスト失敗: 認証エラー (401)")
            assert False
        else:
            print(f"  APIテスト失敗: HTTP {response.status_code}")
            assert False
            
    except Exception as e:
        print(f"  APIテストエラー: {e}")
        assert False

def get_new_tokens(email, password):
    """メールアドレスとパスワードで新しいトークンを取得"""
    try:
        # 認証リクエスト
        auth_data = {"mailaddress": email, "password": password}
        auth_response = requests.post(
            "https://api.jquants.com/v1/token/auth_user",
            json=auth_data,
            timeout=30
        )
        
        if auth_response.status_code == 200:
            auth_result = auth_response.json()
            refresh_token = auth_result.get("refreshToken")
            
            if not refresh_token:
                print("  リフレッシュトークンの取得に失敗しました")
                return None
            
            print("  リフレッシュトークンを取得しました")
            
            # IDトークンを取得
            refresh_response = requests.post(
                f"https://api.jquants.com/v1/token/auth_refresh?refreshtoken={refresh_token}",
                timeout=30
            )
            
            if refresh_response.status_code == 200:
                refresh_result = refresh_response.json()
                id_token = refresh_result.get("idToken")
                
                if id_token:
                    print("  IDトークンを取得しました")
                    return {
                        "id_token": id_token,
                        "refresh_token": refresh_token
                    }
                else:
                    print("  IDトークンの取得に失敗しました")
            else:
                print(f"  IDトークン取得エラー: HTTP {refresh_response.status_code}")
        else:
            print(f"  認証エラー: HTTP {auth_response.status_code}")
            print(f"  レスポンス: {auth_response.text}")
            
    except Exception as e:
        print(f"  認証エラー: {e}")
    
    return None

def main():
    """メイン処理"""
    # 環境変数を読み込み
    from dotenv import load_dotenv
    load_dotenv()
    
    success = test_jquants_auth()
    
    if success:
        print("\n🎉 認証テストが成功しました！")
        return 0
    else:
        print("\n❌ 認証テストが失敗しました。")
        print("認証情報を確認してください。")
        return 1

if __name__ == "__main__":
    exit(main())
