#!/usr/bin/env python3
"""
すべての絶対パスを相対パスに変換するスクリプト
GitHub Pagesで生成されたHTMLファイル内のすべての絶対パスを相対パスに変換する
"""

import os
import re
import glob
from pathlib import Path


def convert_all_absolute_to_relative_path(file_path, content):
    """
    すべての絶対パスを相対パスに変換する
    """
    # ファイルの深さを計算
    relative_path = str(file_path)
    if "docs/web-app/" in relative_path:
        depth = relative_path.count("/") - 2  # docs/web-app/ を除く
    elif "docs/" in relative_path:
        depth = relative_path.count("/") - 1  # docs/ を除く
    else:
        depth = 0

    # 相対パスのプレフィックスを生成
    relative_prefix = "../" * depth if depth > 0 else "./"

    # すべての絶対パスを相対パスに変換
    patterns = [
        # スラッシュで始まるパス（絶対パス）
        (r'href="/', f'href="{relative_prefix}'),
        (r'src="/', f'src="{relative_prefix}'),
        (r'"/', f'"{relative_prefix}'),
        (r"'/", f"'{relative_prefix}"),
        # 特定のパターン
        (r'href="/_next/', f'href="{relative_prefix}_next/'),
        (r'src="/_next/', f'src="{relative_prefix}_next/'),
        (r'href="/favicon.ico"', f'href="{relative_prefix}favicon.ico"'),
        (r'src="/favicon.ico"', f'src="{relative_prefix}favicon.ico"'),
    ]

    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)

    return content


def process_all_files():
    """
    すべてのHTMLファイルとJSファイルを処理
    """
    target_dirs = ["docs/web-app", "docs"]

    processed_files = []

    for target_dir in target_dirs:
        if not os.path.exists(target_dir):
            continue

        # HTMLファイルを検索
        html_files = glob.glob(f"{target_dir}/**/*.html", recursive=True)

        for html_file in html_files:
            try:
                with open(html_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # 絶対パスが含まれているかチェック
                if 'href="/' in content or 'src="/' in content or '"/' in content:
                    # 相対パスに変換
                    new_content = convert_all_absolute_to_relative_path(
                        html_file, content
                    )

                    # ファイルに書き戻し
                    with open(html_file, "w", encoding="utf-8") as f:
                        f.write(new_content)

                    processed_files.append(html_file)
                    print(f"✓ HTML修正完了: {html_file}")

            except Exception as e:
                print(f"✗ HTMLエラー: {html_file} - {e}")

        # JSファイルを検索
        js_files = glob.glob(f"{target_dir}/**/*.js", recursive=True)

        for js_file in js_files:
            try:
                with open(js_file, "r", encoding="utf-8") as f:
                    content = f.read()

                if '"/' in content or "'/" in content:
                    # 相対パスに変換
                    new_content = convert_all_absolute_to_relative_path(
                        js_file, content
                    )

                    with open(js_file, "w", encoding="utf-8") as f:
                        f.write(new_content)

                    processed_files.append(js_file)
                    print(f"✓ JS修正完了: {js_file}")

            except Exception as e:
                print(f"✗ JSエラー: {js_file} - {e}")

    return processed_files


def main():
    """
    メイン処理
    """
    print("🔧 包括的相対パス修正スクリプトを開始...")

    # すべてのファイルを処理
    print("\n📄 すべてのファイルを処理中...")
    processed_files = process_all_files()

    # 結果を表示
    print(f"\n✅ 処理完了!")
    print(f"   - 修正ファイル: {len(processed_files)}件")

    if processed_files:
        print("\n🎉 すべての絶対パスが相対パスに変換されました!")
        print("   GitHub Pagesのどの階層からでも正しく遷移できるようになりました。")
    else:
        print("\n⚠️  修正が必要なファイルが見つかりませんでした。")


if __name__ == "__main__":
    main()
