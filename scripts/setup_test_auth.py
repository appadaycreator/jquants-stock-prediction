#!/usr/bin/env python3
"""
jQuants認証情報設定スクリプト（テスト用）
テスト用の認証情報を設定する
"""

import os
from pathlib import Path

def setup_test_auth():
    """テスト用認証情報を設定"""
    print("=== テスト用認証情報設定 ===")
    
    # テスト用の認証情報
    test_config = {
        "JQUANTS_EMAIL": "test@example.com",
        "JQUANTS_PASSWORD": "test_password",
        "JQUANTS_ID_TOKEN": "test_token_for_demo"
    }
    
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
            for key, value in test_config.items():
                if line.startswith(f"{key}="):
                    updated_lines.append(f"{key}={value}\n")
                    updated = True
                    break
            if not updated:
                updated_lines.append(line)
        
        # 新しい設定を追加
        for key, value in test_config.items():
            if not any(line.startswith(f"{key}=") for line in updated_lines):
                updated_lines.append(f"{key}={value}\n")
        
        # ファイルに書き込み
        with open(env_file, "w", encoding="utf-8") as f:
            f.writelines(updated_lines)
        
        print("✅ テスト用認証情報を設定しました")
        print("注意: これは実際のAPIには接続されません")
        return True
        
    except Exception as e:
        print(f"❌ 設定エラー: {e}")
        return False

def main():
    """メイン処理"""
    if setup_test_auth():
        print("")
        print("🎉 テスト用認証情報の設定が完了しました！")
        print("実際のAPIを使用するには、正しい認証情報を設定してください。")
        return 0
    else:
        print("❌ テスト用認証情報の設定に失敗しました。")
        return 1

if __name__ == "__main__":
    exit(main())
