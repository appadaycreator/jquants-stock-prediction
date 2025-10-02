#!/usr/bin/env python3
"""
jQuants IDトークン再発行スクリプト
このスクリプトを使用してjQuantsのIDトークンを再発行し、環境変数に設定します。
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class JQuantsTokenReissuer:
    """jQuants IDトークン再発行クラス"""
    
    def __init__(self):
        self.base_url = "https://api.jquants.com/v1"
        self.email = None
        self.password = None
        self.refresh_token = None
        self.id_token = None
        
    def get_credentials(self) -> bool:
        """認証情報を取得"""
        print("🔐 jQuants認証情報を入力してください")
        print("=" * 50)
        
        # 環境変数から取得を試行
        self.email = os.getenv("JQUANTS_EMAIL")
        self.password = os.getenv("JQUANTS_PASSWORD")
        
        if self.email and self.password:
            print(f"✅ 環境変数から認証情報を取得しました: {self.email}")
            return True
        
        # 手動入力
        if not self.email:
            self.email = input("📧 メールアドレス: ").strip()
        if not self.password:
            self.password = input("🔑 パスワード: ").strip()
        
        if not self.email or not self.password:
            print("❌ メールアドレスとパスワードが必要です")
            return False
            
        return True
    
    def get_refresh_token(self) -> bool:
        """リフレッシュトークンを取得"""
        print("\n🔄 リフレッシュトークンを取得中...")
        
        try:
            auth_url = f"{self.base_url}/token/auth_user"
            auth_data = {
                "mailaddress": self.email,
                "password": self.password
            }
            
            response = requests.post(auth_url, json=auth_data, timeout=30)
            response.raise_for_status()
            
            auth_result = response.json()
            
            if "refreshToken" not in auth_result:
                print("❌ リフレッシュトークンの取得に失敗しました")
                print(f"レスポンス: {auth_result}")
                return False
            
            self.refresh_token = auth_result["refreshToken"]
            print("✅ リフレッシュトークンを取得しました")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ リフレッシュトークン取得エラー: {e}")
            return False
        except Exception as e:
            print(f"❌ 予期しないエラー: {e}")
            return False
    
    def get_id_token(self) -> bool:
        """IDトークンを取得"""
        print("\n🎫 IDトークンを取得中...")
        
        try:
            token_url = f"{self.base_url}/token/auth_refresh"
            token_data = {
                "refreshtoken": self.refresh_token
            }
            
            response = requests.post(token_url, json=token_data, timeout=30)
            response.raise_for_status()
            
            token_result = response.json()
            
            if "idToken" not in token_result:
                print("❌ IDトークンの取得に失敗しました")
                print(f"レスポンス: {token_result}")
                return False
            
            self.id_token = token_result["idToken"]
            print("✅ IDトークンを取得しました")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ IDトークン取得エラー: {e}")
            return False
        except Exception as e:
            print(f"❌ 予期しないエラー: {e}")
            return False
    
    def test_token(self) -> bool:
        """取得したトークンをテスト"""
        print("\n🧪 トークンをテスト中...")
        
        try:
            test_url = f"{self.base_url}/listed/info"
            headers = {
                "Authorization": f"Bearer {self.id_token}"
            }
            
            response = requests.get(test_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            print("✅ トークンテスト成功")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ トークンテストエラー: {e}")
            return False
        except Exception as e:
            print(f"❌ 予期しないエラー: {e}")
            return False
    
    def save_to_env_file(self) -> bool:
        """環境変数ファイルに保存"""
        print("\n💾 環境変数ファイルに保存中...")
        
        try:
            # .envファイルのパス
            env_file = os.path.join(os.getcwd(), ".env")
            
            # 既存の.envファイルを読み込み
            env_vars = {}
            if os.path.exists(env_file):
                with open(env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            env_vars[key] = value
            
            # 新しいトークンを設定
            env_vars['JQUANTS_ID_TOKEN'] = self.id_token
            env_vars['JQUANTS_EMAIL'] = self.email
            env_vars['JQUANTS_PASSWORD'] = self.password
            
            # .envファイルに書き込み
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write("# jQuants API設定\n")
                f.write(f"JQUANTS_EMAIL={self.email}\n")
                f.write(f"JQUANTS_PASSWORD={self.password}\n")
                f.write(f"JQUANTS_ID_TOKEN={self.id_token}\n")
                f.write("\n# その他の設定\n")
                for key, value in env_vars.items():
                    if not key.startswith('JQUANTS_'):
                        f.write(f"{key}={value}\n")
            
            print(f"✅ 環境変数ファイルに保存しました: {env_file}")
            return True
            
        except Exception as e:
            print(f"❌ 環境変数ファイル保存エラー: {e}")
            return False
    
    def display_token_info(self):
        """トークン情報を表示"""
        print("\n" + "=" * 60)
        print("🎉 jQuants IDトークン再発行完了")
        print("=" * 60)
        print(f"📧 メールアドレス: {self.email}")
        print(f"🎫 IDトークン: {self.id_token[:20]}...")
        print(f"🔄 リフレッシュトークン: {self.refresh_token[:20]}...")
        print(f"⏰ 取得時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏳ 有効期限: 約24時間")
        print("\n💡 使用方法:")
        print("   1. 環境変数が自動的に設定されました")
        print("   2. アプリケーションを再起動してください")
        print("   3. トークンは24時間で期限切れになります")
        print("=" * 60)
    
    def reissue_token(self) -> bool:
        """トークン再発行のメイン処理"""
        print("🚀 jQuants IDトークン再発行を開始します")
        print("=" * 50)
        
        # 1. 認証情報取得
        if not self.get_credentials():
            return False
        
        # 2. リフレッシュトークン取得
        if not self.get_refresh_token():
            return False
        
        # 3. IDトークン取得
        if not self.get_id_token():
            return False
        
        # 4. トークンテスト
        if not self.test_token():
            return False
        
        # 5. 環境変数ファイルに保存
        if not self.save_to_env_file():
            return False
        
        # 6. 結果表示
        self.display_token_info()
        
        return True

def main():
    """メイン関数"""
    print("🔐 jQuants IDトークン再発行ツール")
    print("=" * 50)
    
    reissuer = JQuantsTokenReissuer()
    
    try:
        success = reissuer.reissue_token()
        
        if success:
            print("\n✅ トークン再発行が正常に完了しました")
            sys.exit(0)
        else:
            print("\n❌ トークン再発行に失敗しました")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️ 処理が中断されました")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 予期しないエラーが発生しました: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
