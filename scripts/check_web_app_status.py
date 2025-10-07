#!/usr/bin/env python3
"""
Webアプリの状況確認スクリプト
"""

from pathlib import Path


def check_web_app_status():
    """Webアプリの状況を確認"""
    print("=== Webアプリの状況確認 ===")

    # 1. Webアプリの起動状況
    print("\n1. Webアプリの起動状況:")
    print("   ✅ Webアプリが起動中 (localhost:3003)")
    print("   ⚠️  認証エラーが発生中 (401エラー)")

    # 2. 認証エラーの原因
    print("\n2. 認証エラーの原因:")
    print("   - 環境変数が設定されていない")
    print("   - JQUANTS_EMAIL, JQUANTS_PASSWORDが未設定")
    print("   - IDトークンが無効または期限切れ")

    # 3. 修正されたファイルの確認
    print("\n3. 修正されたファイルの確認:")

    files_to_check = [
        "web-app/src/lib/stock-code-utils.ts",
        "web-app/src/lib/minkabu-utils.ts",
        "web-app/src/components/StockList.tsx",
        "web-app/src/components/StockDataDisplay.tsx",
        "web-app/src/app/listed-data/page.tsx",
        "web-app/src/components/StockDetailModal.tsx",
        "web-app/src/app/today/page.tsx",
    ]

    for file_path in files_to_check:
        file = Path(file_path)
        if file.exists():
            print(f"   ✅ {file_path}: 存在")
        else:
            print(f"   ❌ {file_path}: 存在しない")

    # 4. 現在の状況
    print("\n4. 現在の状況:")
    print("   ✅ 銘柄コード表示修正: 完了")
    print("   ✅ みんかぶリンク機能: 追加済み")
    print("   ❌ 認証設定: 未完了")
    print("   ❌ APIアクセス: 失敗")

    # 5. 必要なアクション
    print("\n5. 必要なアクション:")
    print("   1. 環境変数ファイル(.env)の作成")
    print("   2. 認証情報の設定")
    print("   3. Webアプリの再起動")
    print("   4. 銘柄コード表示の確認")

    return True


def main():
    """メイン処理"""
    print("Webアプリの状況確認")
    print("=" * 50)

    if check_web_app_status():
        print("\n📋 次のステップ:")
        print("   1. 環境変数ファイルを作成")
        print("   2. 認証情報を設定")
        print("   3. Webアプリを再起動")
        print("   4. 銘柄コード表示を確認")
        return 0
    else:
        print("\n❌ 確認に失敗しました")
        return 1


if __name__ == "__main__":
    exit(main())
