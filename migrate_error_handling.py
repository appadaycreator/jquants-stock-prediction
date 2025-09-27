#!/usr/bin/env python3
"""
自動移行スクリプト
エラーハンドリングシステムの自動移行を実行
"""

import os
import re
from pathlib import Path


def migrate_imports(file_path: str):
    """インポート文の移行"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 旧インポート文の置換
    replacements = [
        (
            r"from unified_error_handler import.*",
            "from unified_error_handling_system import get_unified_error_handler, ErrorCategory, ErrorSeverity",
        ),
        (
            r"from unified_error_logging_system import.*",
            "from unified_error_handling_system import get_unified_error_handler, ErrorCategory, ErrorSeverity",
        ),
        (
            r"import unified_error_handler",
            "from unified_error_handling_system import get_unified_error_handler, ErrorCategory, ErrorSeverity",
        ),
        (
            r"import unified_error_logging_system",
            "from unified_error_handling_system import get_unified_error_handler, ErrorCategory, ErrorSeverity",
        ),
    ]

    modified = False
    for pattern, replacement in replacements:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            modified = True

    if modified:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ 移行完了: {file_path}")
        return True

    return False


def main():
    """メイン処理"""
    project_root = Path(__file__).parent

    # 移行対象ファイル
    target_files = [
        "/Users/masayukitokunaga/workspace/jquants-stock-prediction/enhanced_logging.py",
        "/Users/masayukitokunaga/workspace/jquants-stock-prediction/jquants_data_preprocessing.py",
        "/Users/masayukitokunaga/workspace/jquants-stock-prediction/tests/unit/test_edge_cases_comprehensive.py",
        "/Users/masayukitokunaga/workspace/jquants-stock-prediction/unified_jquants_system.py",
    ]

    migrated_count = 0
    for file_path in target_files:
        if os.path.exists(file_path):
            if migrate_imports(file_path):
                migrated_count += 1

    print(f"移行完了: {migrated_count}ファイル")
    print("移行後は手動でエラーハンドリングロジックを確認してください。")


if __name__ == "__main__":
    main()
