#!/usr/bin/env python3
"""
テスト実行スクリプト
開発環境でのテスト実行を簡素化する
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """コマンドを実行し、結果を表示"""
    print(f"\n🔄 {description}...")
    print(f"実行コマンド: {command}")
    print("-" * 50)

    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        print(result.stdout)
        if result.stderr:
            print("警告:", result.stderr)
        print(f"✅ {description} 完了")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失敗")
        print("エラー出力:", e.stderr)
        return False


def main():
    """メイン実行関数"""
    print("🧪 J-Quants株価予測システム テスト実行")
    print("=" * 60)

    # プロジェクトルートに移動
    project_root = Path(__file__).parent
    os.chdir(project_root)

    # テスト実行のオプション
    test_types = {
        "unit": "ユニットテスト",
        "integration": "統合テスト",
        "all": "全テスト",
        "coverage": "カバレッジ付きテスト",
        "lint": "リンターチェック",
        "format": "コードフォーマット",
    }

    if len(sys.argv) > 1:
        test_type = sys.argv[1]
    else:
        print("利用可能なテストタイプ:")
        for key, desc in test_types.items():
            print(f"  {key}: {desc}")
        print("\n使用例: python run_tests.py unit")
        return

    if test_type not in test_types:
        print(f"❌ 無効なテストタイプ: {test_type}")
        return

    success = True

    if test_type == "unit":
        success = run_command(
            "pytest tests/unit/test_technical_indicators.py tests/unit/test_model_factory_simple.py tests/unit/test_data_preprocessing_simple.py -v",
            "ユニットテスト実行",
        )

    elif test_type == "integration":
        success = run_command("pytest tests/integration/ -v", "統合テスト実行")

    elif test_type == "all":
        success = run_command(
            "pytest tests/unit/test_technical_indicators.py tests/unit/test_model_factory_simple.py tests/unit/test_data_preprocessing_simple.py tests/integration/test_data_pipeline.py -v",
            "全テスト実行",
        )

    elif test_type == "coverage":
        success = run_command(
            "pytest tests/unit/test_technical_indicators.py tests/unit/test_model_factory_simple.py tests/unit/test_data_preprocessing_simple.py tests/integration/test_data_pipeline.py -v --cov=. --cov-report=html --cov-report=term-missing",
            "カバレッジ付きテスト実行",
        )
        if success:
            print("\n📊 カバレッジレポートが htmlcov/index.html に生成されました")

    elif test_type == "lint":
        success = run_command(
            "flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics",
            "リンターチェック",
        )
        if success:
            success = run_command(
                "black --check --diff .", "コードフォーマットチェック"
            )

    elif test_type == "format":
        success = run_command("black .", "コードフォーマット実行")
        if success:
            print("✅ コードフォーマット完了")

    # 結果の表示
    print("\n" + "=" * 60)
    if success:
        print("🎉 すべてのテストが正常に完了しました")
    else:
        print("❌ テストの実行中にエラーが発生しました")
        sys.exit(1)


if __name__ == "__main__":
    main()
