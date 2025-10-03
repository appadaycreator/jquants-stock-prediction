#!/usr/bin/env python3
"""
jQuants認証情報設定スクリプト（最終版）
IDトークンを環境変数に設定せず、メールアドレスとパスワードのみ設定
"""

import os
from pathlib import Path

def setup_auth_final():
    """最終版認証情報を設定（IDトークンなし）"""
    print("=== 最終版認証情報設定 ===")
    print("IDトークンは環境変数に設定せず、一時保存のみで管理します")
    print("")
    
    # メールアドレスとパスワードのみ設定
    auth_config = {
        "JQUANTS_EMAIL": "test@example.com",
        "JQUANTS_PASSWORD": "test_password"
    }
    
    try:
        env_file = Path(".env")
        env_content = []
        
        # 既存の.envファイルを読み込み
        if env_file.exists():
            with open(env_file, "r", encoding="utf-8") as f:
                env_content = f.readlines()
        
        # 設定を更新（IDトークンは設定しない）
        updated_lines = []
        for line in env_content:
            updated = False
            for key, value in auth_config.items():
                if line.startswith(f"{key}="):
                    updated_lines.append(f"{key}={value}\n")
                    updated = True
                    break
            if not updated:
                updated_lines.append(line)
        
        # 新しい設定を追加（IDトークンは追加しない）
        for key, value in auth_config.items():
            if not any(line.startswith(f"{key}=") for line in updated_lines):
                updated_lines.append(f"{key}={value}\n")
        
        # ファイルに書き込み
        with open(env_file, "w", encoding="utf-8") as f:
            f.writelines(updated_lines)
        
        print("✅ 認証情報を設定しました（IDトークンは環境変数に設定しません）")
        print("   設定項目:")
        print("   - JQUANTS_EMAIL: メールアドレス")
        print("   - JQUANTS_PASSWORD: パスワード")
        print("   - IDトークン: 一時保存のみ（環境変数非依存）")
        return True
        
    except Exception as e:
        print(f"❌ 設定エラー: {e}")
        return False

def test_auth_final():
    """最終版認証機能をテスト"""
    print("")
    print("=== 最終版認証機能テスト ===")
    
    try:
        from jquants_auth_manager_final import JQuantsAuthManagerFinal
        
        auth_manager = JQuantsAuthManagerFinal()
        valid_token = auth_manager.get_valid_token()
        
        if valid_token:
            print("✅ 認証テスト成功: 有効なトークンを取得しました")
            print("   注意: トークンは一時保存のみで、環境変数には保存されません")
            return True
        else:
            print("❌ 認証テスト失敗: 有効なトークンを取得できませんでした")
            print("   実際のjQuants認証情報が必要です")
            return False
            
    except Exception as e:
        print(f"❌ 認証テストエラー: {e}")
        return False

def main():
    """メイン処理"""
    print("jQuants認証情報設定ツール（最終版）")
    print("=" * 50)
    print("特徴:")
    print("- IDトークンを環境変数に設定しません")
    print("- 一時保存されたトークンが利用できない場合、メールアドレスとパスワードで再認証")
    print("- セキュリティ向上: トークンの永続化を避ける")
    print("")
    
    if setup_auth_final():
        print("")
        if test_auth_final():
            print("")
            print("🎉 最終版認証情報の設定が完了しました！")
            print("")
            print("=== 使用方法 ===")
            print("1. 実際のjQuants認証情報を.envファイルに設定")
            print("2. python scripts/sync_with_jquants_api.py --test を実行")
            print("3. トークンは一時保存のみで、環境変数には保存されません")
            return 0
        else:
            print("⚠️  認証情報の設定は完了しましたが、テストに失敗しました。")
            print("実際のjQuants認証情報を設定してください。")
            return 1
    else:
        print("❌ 認証情報の設定に失敗しました。")
        return 1

if __name__ == "__main__":
    exit(main())
