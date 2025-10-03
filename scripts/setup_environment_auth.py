#!/usr/bin/env python3
"""
環境認証情報設定スクリプト
ローカル環境と本番環境の認証情報を適切に設定
"""

import os
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def setup_environment_auth():
    """環境認証情報の設定"""
    print("=== 環境認証情報設定 ===")
    print("ローカル環境と本番環境の認証情報を設定します。")
    print()
    
    # 環境認証管理システムをインポート
    try:
        from core.environment_auth_manager import EnvironmentAuthManager
        auth_manager = EnvironmentAuthManager()
    except ImportError:
        print("❌ 環境認証管理システムが見つかりません。")
        return False
    
    # 現在の環境を表示
    print(f"現在の環境: {auth_manager.environment}")
    print(f"認証情報状態: {auth_manager.get_auth_status_message()}")
    print()
    
    # 環境に応じた設定方法を表示
    if auth_manager.environment == "production":
        print("=== 本番環境設定 ===")
        print("本番環境ではGitHub Secretsを使用します。")
        print()
        print("GitHub Secrets設定方法:")
        print("1. GitHubリポジトリの Settings > Secrets and variables > Actions")
        print("2. 'New repository secret' をクリック")
        print("3. 以下のSecretsを追加:")
        print("   - JQUANTS_EMAIL: jQuants APIのメールアドレス")
        print("   - JQUANTS_PASSWORD: jQuants APIのパスワード")
        print("   - JQUANTS_ID_TOKEN: (オプション) IDトークンを直接設定")
        print("   - JQUANTS_REFRESH_TOKEN: (オプション) リフレッシュトークン")
        print()
        print("設定後、GitHub Actionsワークフローで自動的に認証情報が読み込まれます。")
        
    else:
        print("=== ローカル環境設定 ===")
        print("ローカル環境では.envファイルを使用します。")
        print()
        
        # .envファイルの存在確認
        env_file = Path(".env")
        if env_file.exists():
            print("既存の.envファイルが見つかりました。")
            overwrite = input("上書きしますか？ (y/N): ").strip().lower()
            if overwrite != 'y':
                print("設定をキャンセルしました。")
                return False
        
        # 認証情報の入力
        print("jQuants APIの認証情報を入力してください:")
        email = input("メールアドレス: ").strip()
        password = input("パスワード: ").strip()
        
        if not email or not password:
            print("メールアドレスとパスワードは必須です。")
            return False
        
        # .envファイルの作成
        env_content = f"""# J-Quants API認証情報
# ローカル開発環境用の設定ファイル

# 環境設定
ENVIRONMENT=development
DEBUG=true

# J-Quants API認証情報
JQUANTS_EMAIL={email}
JQUANTS_PASSWORD={password}
JQUANTS_ID_TOKEN=
JQUANTS_REFRESH_TOKEN=

# ログ設定
LOG_LEVEL=INFO
TIMEZONE=Asia/Tokyo

# API設定
API_TIMEOUT=30
MAX_RETRIES=3
RATE_LIMIT=100

# データ取得設定
TARGET_DATE=20240301
OUTPUT_FILE=stock_data.csv

# パフォーマンス設定
MAX_WORKERS=4
MEMORY_LIMIT=2GB

# 予測設定
TEST_SIZE=0.2
RANDOM_STATE=42
PRIMARY_MODEL=xgboost
COMPARE_MODELS=false

# セキュリティ設定
ENABLE_SSL=true
ALLOWED_ORIGINS=localhost:3000,*.github.io
"""
        
        try:
            with open(env_file, "w", encoding="utf-8") as f:
                f.write(env_content)
            print(f"✅ .envファイルを作成しました")
        except Exception as e:
            print(f"❌ .envファイル作成エラー: {e}")
            return False
    
    return True

def test_auth_setup():
    """認証設定のテスト"""
    print("\n=== 認証設定テスト ===")
    
    try:
        from core.environment_auth_manager import EnvironmentAuthManager
        auth_manager = EnvironmentAuthManager()
        
        print(f"環境: {auth_manager.environment}")
        print(f"認証情報状態: {auth_manager.get_auth_status_message()}")
        
        # ダミー認証情報のチェック
        if auth_manager.is_dummy_auth():
            print("⚠️ ダミーの認証情報が設定されています。")
            return False
        
        # 認証情報の設定確認
        if not auth_manager.is_auth_configured():
            print("❌ 認証情報が設定されていません。")
            return False
        
        print("✅ 認証情報が正しく設定されています。")
        return True
        
    except Exception as e:
        print(f"❌ 認証設定テストエラー: {e}")
        return False

def main():
    """メイン処理"""
    print("環境認証情報設定ツール")
    print("=" * 50)
    
    # 環境認証情報の設定
    if not setup_environment_auth():
        print("認証情報の設定に失敗しました。")
        return 1
    
    # 認証設定のテスト
    if test_auth_setup():
        print("\n🎉 認証情報の設定が完了しました！")
        print("これで jQuants API を使用できます。")
        return 0
    else:
        print("\n⚠️ 認証情報の設定は完了しましたが、テストに失敗しました。")
        print("設定した認証情報を確認してください。")
        return 1

if __name__ == "__main__":
    exit(main())
