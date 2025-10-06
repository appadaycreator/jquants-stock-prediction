#!/usr/bin/env python3
"""
jQuants認証管理機能デモ（最終版）
IDトークンを環境変数に設定せず、一時保存のみで管理
"""

import os
import json
from pathlib import Path


def demo_auth_final():
    """最終版認証管理機能のデモ"""
    print("jQuants認証管理機能デモ（最終版）")
    print("=" * 50)
    print("=== 最終版認証管理機能デモ ===")

    try:
        from jquants_auth_manager_final import JQuantsAuthManagerFinal

        # 認証管理クラスの初期化
        auth_manager = JQuantsAuthManagerFinal()
        print("✅ 認証管理クラスの初期化完了")
        print(f"   - メールアドレス: {auth_manager.email}")
        print(f"   - パスワード設定: {'あり' if auth_manager.password else 'なし'}")
        print(f"   - IDトークン: 一時保存のみ（環境変数非依存）")

        # 一時トークンキャッシュの確認
        print("\n=== 一時トークンキャッシュ機能 ===")
        cache = auth_manager.load_temp_token_cache()
        if cache:
            print("ℹ️  一時トークンキャッシュが見つかりました")
            print(f"   - キャッシュ日時: {cache.get('cached_at', '不明')}")
            print(f"   - 有効期限: {cache.get('expires_at', '不明')}")
        else:
            print("ℹ️  一時トークンキャッシュはありません")

        # トークン有効性チェック
        print("\n=== トークン有効性チェック ===")
        current_token = auth_manager.get_current_token()
        if current_token:
            is_valid = auth_manager.is_token_valid(current_token)
            print(f"トークン有効性: {'有効' if is_valid else '無効'}")
        else:
            print("トークン有効性: トークンなし")

        # 一時キャッシュクリア機能
        print("\n=== 一時キャッシュクリア機能 ===")
        if auth_manager.clear_temp_token_cache():
            print("✅ 一時トークンキャッシュをクリアしました")
        else:
            print("⚠️  一時トークンキャッシュのクリアに失敗しました")

        # 強化された認証管理機能の特徴
        print("\n=== 最終版認証管理機能の特徴 ===")
        features = [
            "IDトークンを環境変数に保存しない",
            "一時保存されたトークンの自動管理",
            "トークン無効時の自動再認証",
            "メールアドレスとパスワードでの再認証",
            "自動リトライ機能 (最大3回)",
            "一時トークンキャッシュ機能",
            "詳細なエラーハンドリング",
            "トークン有効期限の自動チェック",
            "セキュリティ強化: トークンの永続化を避ける",
        ]

        for feature in features:
            print(f"✅ {feature}")

        print("\n🎉 デモが正常に完了しました！")
        print("\n実際のjQuants APIを使用するには:")
        print("1. 正しい認証情報を.envファイルに設定")
        print("2. python scripts/sync_with_jquants_api.py --test を実行")
        print("3. トークンは一時保存のみで、環境変数には保存されません")

        return True

    except Exception as e:
        print(f"❌ デモ実行エラー: {e}")
        return False


def main():
    """メイン処理"""
    return 0 if demo_auth_final() else 1


if __name__ == "__main__":
    exit(main())
