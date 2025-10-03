#!/usr/bin/env python3
"""
jQuants認証管理機能デモスクリプト
強化された認証管理クラスの機能をデモンストレーション
"""

import os
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def demo_auth_features():
    """認証管理機能のデモ"""
    print("=== jQuants認証管理機能デモ ===")
    print("")
    
    try:
        from jquants_auth_manager_enhanced import JQuantsAuthManagerEnhanced
        
        # 認証管理クラスを初期化
        auth_manager = JQuantsAuthManagerEnhanced()
        
        print("✅ 認証管理クラスの初期化完了")
        print(f"   - メールアドレス: {auth_manager.email}")
        print(f"   - パスワード設定: {'あり' if auth_manager.password else 'なし'}")
        print(f"   - IDトークン設定: {'あり' if auth_manager.id_token else 'なし'}")
        print(f"   - リフレッシュトークン設定: {'あり' if auth_manager.refresh_token else 'なし'}")
        print("")
        
        # トークン有効性チェック
        print("=== トークン有効性チェック ===")
        is_valid = auth_manager.is_token_valid()
        print(f"トークン有効性: {'有効' if is_valid else '無効'}")
        print("")
        
        # キャッシュ機能のテスト
        print("=== トークンキャッシュ機能 ===")
        cache = auth_manager.load_token_cache()
        if cache:
            print("✅ トークンキャッシュを読み込みました")
            print(f"   - キャッシュ日時: {cache.get('cached_at', '不明')}")
            print(f"   - 有効期限: {cache.get('expires_at', '不明')}")
        else:
            print("ℹ️  トークンキャッシュはありません")
        print("")
        
        # 環境変数ファイル保存機能
        print("=== 環境変数ファイル保存機能 ===")
        test_tokens = {
            "id_token": "demo_id_token_12345",
            "refresh_token": "demo_refresh_token_67890"
        }
        
        if auth_manager.save_tokens_to_env(test_tokens):
            print("✅ テスト用トークンを環境変数ファイルに保存しました")
        else:
            print("❌ トークンの保存に失敗しました")
        print("")
        
        # キャッシュクリア機能
        print("=== キャッシュクリア機能 ===")
        if auth_manager.clear_token_cache():
            print("✅ トークンキャッシュをクリアしました")
        else:
            print("❌ キャッシュクリアに失敗しました")
        print("")
        
        print("=== 強化された認証管理機能の特徴 ===")
        print("✅ 自動リトライ機能 (最大3回)")
        print("✅ トークンキャッシュ機能")
        print("✅ 環境変数ファイル自動更新")
        print("✅ 詳細なエラーハンドリング")
        print("✅ トークン有効期限の自動チェック")
        print("✅ 複数の認証方法の自動切り替え")
        print("")
        
        return True
        
    except Exception as e:
        print(f"❌ デモ実行エラー: {e}")
        return False

def main():
    """メイン処理"""
    print("jQuants認証管理機能デモ")
    print("=" * 50)
    
    if demo_auth_features():
        print("🎉 デモが正常に完了しました！")
        print("")
        print("実際のjQuants APIを使用するには:")
        print("1. 正しい認証情報を.envファイルに設定")
        print("2. python scripts/sync_with_jquants_api.py --test を実行")
        return 0
    else:
        print("❌ デモの実行に失敗しました。")
        return 1

if __name__ == "__main__":
    exit(main())
