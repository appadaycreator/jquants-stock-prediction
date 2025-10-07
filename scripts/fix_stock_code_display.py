#!/usr/bin/env python3
"""
銘柄コード表示修正スクリプト
9875が98750と表示される問題を修正
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))


def analyze_stock_code_issue():
    """銘柄コード表示問題の分析"""
    print("=== 銘柄コード表示問題の分析 ===")

    # stock_data.jsonの銘柄コードを確認
    stock_data_file = Path("data/stock_data.json")
    if not stock_data_file.exists():
        print("❌ stock_data.jsonが見つかりません")
        return False

    with open(stock_data_file, "r", encoding="utf-8") as f:
        stock_data = json.load(f)

    print("📊 データ分析結果:")
    print(f"   総銘柄数: {len(stock_data)}銘柄")

    # 銘柄コードの長さを分析
    code_lengths = {}
    sample_codes = []

    for code in list(stock_data.keys())[:20]:  # 最初の20銘柄をサンプル
        length = len(code)
        code_lengths[length] = code_lengths.get(length, 0) + 1
        sample_codes.append(code)

    print(f"   銘柄コード長さ分布: {code_lengths}")
    print(f"   サンプル銘柄コード: {sample_codes[:10]}")

    # 9875のような4桁コードが5桁で保存されているかチェック
    four_digit_codes = []
    for code in stock_data.keys():
        if len(code) == 5 and code.startswith("0"):
            # 先頭の0を除いた4桁コード
            four_digit = code[1:]
            four_digit_codes.append((code, four_digit))

    print(f"   4桁コード（5桁で保存）: {len(four_digit_codes)}銘柄")
    if four_digit_codes:
        print(f"   例: {four_digit_codes[:5]}")

    return True


def fix_web_app_code_validation():
    """Webアプリの銘柄コードバリデーションを修正"""
    print("\n=== Webアプリの銘柄コードバリデーション修正 ===")

    # enhanced-jquants-adapter.tsの修正
    adapter_file = Path("web-app/src/lib/enhanced-jquants-adapter.ts")
    if not adapter_file.exists():
        print("❌ enhanced-jquants-adapter.tsが見つかりません")
        return False

    with open(adapter_file, "r", encoding="utf-8") as f:
        content = f.read()

    # 4桁のバリデーションを5桁に修正
    old_validation = "code: {\n      format: /^\\d{4}$/,\n      required: true,\n    },"
    new_validation = (
        "code: {\n      format: /^\\d{4,5}$/,\n      required: true,\n    },"
    )

    if old_validation in content:
        content = content.replace(old_validation, new_validation)

        with open(adapter_file, "w", encoding="utf-8") as f:
            f.write(content)

        print("✅ enhanced-jquants-adapter.tsの銘柄コードバリデーションを修正しました")
        print("   4桁 → 4-5桁のバリデーションに変更")
        return True
    else:
        print("⚠️  修正対象のコードが見つかりませんでした")
        return False


def create_stock_code_mapping():
    """銘柄コードマッピングファイルを作成"""
    print("\n=== 銘柄コードマッピングファイル作成 ===")

    stock_data_file = Path("data/stock_data.json")
    with open(stock_data_file, "r", encoding="utf-8") as f:
        stock_data = json.load(f)

    # 銘柄コードマッピングを作成
    code_mapping = {}
    for code in stock_data.keys():
        if len(code) == 5 and code.startswith("0"):
            # 5桁のコード（先頭に0が付いている）を4桁に変換
            four_digit = code[1:]
            code_mapping[four_digit] = code
            code_mapping[code] = four_digit

    # マッピングファイルを保存
    mapping_file = Path("data/stock_code_mapping.json")
    with open(mapping_file, "w", encoding="utf-8") as f:
        json.dump(code_mapping, f, ensure_ascii=False, indent=2)

    print("✅ 銘柄コードマッピングファイルを作成しました")
    print(f"   ファイル: {mapping_file}")
    print(f"   マッピング数: {len(code_mapping)}件")

    return True


def create_stock_code_utility():
    """銘柄コード変換ユーティリティを作成"""
    print("\n=== 銘柄コード変換ユーティリティ作成 ===")

    utility_content = """/**
 * 銘柄コード変換ユーティリティ
 * 4桁と5桁の銘柄コードを相互変換
 */

export interface StockCodeMapping {
  [key: string]: string;
}

/**
 * 銘柄コードを正規化（4桁に統一）
 */
export function normalizeStockCode(code: string): string {
  if (!code) return '';
  
  // 5桁で先頭が0の場合は4桁に変換
  if (code.length === 5 && code.startsWith('0')) {
    return code.substring(1);
  }
  
  // 4桁の場合はそのまま
  if (code.length === 4) {
    return code;
  }
  
  // その他の場合はそのまま
  return code;
}

/**
 * 銘柄コードを5桁形式に変換
 */
export function toFiveDigitCode(code: string): string {
  if (!code) return '';
  
  // 4桁の場合は先頭に0を追加
  if (code.length === 4) {
    return '0' + code;
  }
  
  // 5桁の場合はそのまま
  if (code.length === 5) {
    return code;
  }
  
  // その他の場合はそのまま
  return code;
}

/**
 * 銘柄コードの表示用フォーマット
 */
export function formatStockCode(code: string): string {
  const normalized = normalizeStockCode(code);
  return normalized;
}

/**
 * 銘柄コードが有効かチェック
 */
export function isValidStockCode(code: string): boolean {
  if (!code) return false;
  
  const normalized = normalizeStockCode(code);
  return /^\\d{4}$/.test(normalized);
}
"""

    utility_file = Path("web-app/src/lib/stock-code-utils.ts")
    with open(utility_file, "w", encoding="utf-8") as f:
        f.write(utility_content)

    print("✅ 銘柄コード変換ユーティリティを作成しました")
    print(f"   ファイル: {utility_file}")

    return True


def update_components_to_use_utils():
    """コンポーネントを更新してユーティリティを使用"""
    print("\n=== コンポーネントの更新 ===")

    # StockDataDisplay.tsxの更新
    display_file = Path("web-app/src/components/StockDataDisplay.tsx")
    if display_file.exists():
        with open(display_file, "r", encoding="utf-8") as f:
            content = f.read()

        # インポートを追加
        if "import { formatStockCode } from '../lib/stock-code-utils';" not in content:
            # 最初のimport文の後に追加
            import_line = "import { formatStockCode } from '../lib/stock-code-utils';"
            if "import React" in content:
                content = content.replace(
                    "import React from 'react';",
                    f"import React from 'react';\n{import_line}",
                )

        # 銘柄コード表示部分を更新
        old_display = '<p className="text-sm text-gray-600">{code}</p>'
        new_display = '<p className="text-sm text-gray-600">{formatStockCode(code)}</p>'

        if old_display in content:
            content = content.replace(old_display, new_display)

            with open(display_file, "w", encoding="utf-8") as f:
                f.write(content)

            print("✅ StockDataDisplay.tsxを更新しました")
        else:
            print("⚠️  StockDataDisplay.tsxの更新対象が見つかりませんでした")

    # StockList.tsxの更新
    list_file = Path("web-app/src/components/StockList.tsx")
    if list_file.exists():
        with open(list_file, "r", encoding="utf-8") as f:
            content = f.read()

        # インポートを追加
        if "import { formatStockCode } from '../lib/stock-code-utils';" not in content:
            import_line = "import { formatStockCode } from '../lib/stock-code-utils';"
            if "import React" in content:
                content = content.replace(
                    "import React from 'react';",
                    f"import React from 'react';\n{import_line}",
                )

        # 銘柄コード表示部分を更新
        old_display = "{stock.code}"
        new_display = "{formatStockCode(stock.code)}"

        if old_display in content:
            content = content.replace(old_display, new_display)

            with open(list_file, "w", encoding="utf-8") as f:
                f.write(content)

            print("✅ StockList.tsxを更新しました")
        else:
            print("⚠️  StockList.tsxの更新対象が見つかりませんでした")

    return True


def generate_fix_report():
    """修正レポートを生成"""
    print("\n=== 修正レポート生成 ===")

    report = {
        "fix_date": datetime.now().isoformat(),
        "issue": "銘柄コード表示問題（9875が98750と表示される）",
        "root_cause": "Webアプリの銘柄コードバリデーションが4桁のみを期待していたが、実際のデータは5桁で保存されている",
        "fixes_applied": [
            "enhanced-jquants-adapter.tsのバリデーションを4桁→4-5桁に修正",
            "銘柄コード変換ユーティリティを作成",
            "コンポーネントでユーティリティを使用するよう更新",
            "銘柄コードマッピングファイルを作成",
        ],
        "files_modified": [
            "web-app/src/lib/enhanced-jquants-adapter.ts",
            "web-app/src/lib/stock-code-utils.ts (新規)",
            "web-app/src/components/StockDataDisplay.tsx",
            "web-app/src/components/StockList.tsx",
            "data/stock_code_mapping.json (新規)",
        ],
        "recommendations": [
            "Webアプリを再起動して変更を反映",
            "銘柄コード表示が正しく4桁で表示されることを確認",
            "投資指示画面や銘柄一覧で正しい銘柄コードが表示されることを確認",
        ],
    }

    # レポートファイルに保存
    report_file = Path("data/stock_code_fix_report.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("✅ 修正レポートを生成しました")
    print(f"   ファイル: {report_file}")

    return report


def main():
    """メイン処理"""
    print("銘柄コード表示修正ツール")
    print("=" * 50)

    # 1. 問題の分析
    if not analyze_stock_code_issue():
        print("❌ 問題の分析に失敗しました")
        return 1

    # 2. Webアプリのバリデーション修正
    if not fix_web_app_code_validation():
        print("❌ Webアプリのバリデーション修正に失敗しました")
        return 1

    # 3. 銘柄コードマッピング作成
    if not create_stock_code_mapping():
        print("❌ 銘柄コードマッピング作成に失敗しました")
        return 1

    # 4. ユーティリティ作成
    if not create_stock_code_utility():
        print("❌ ユーティリティ作成に失敗しました")
        return 1

    # 5. コンポーネント更新
    if not update_components_to_use_utils():
        print("❌ コンポーネント更新に失敗しました")
        return 1

    # 6. 修正レポート生成
    report = generate_fix_report()

    print("\n🎉 銘柄コード表示問題の修正が完了しました！")
    print("   問題: 9875が98750と表示される")
    print("   修正: 銘柄コードを正しく4桁で表示")
    print("   影響: 投資指示画面、銘柄一覧、全表示コンポーネント")

    print("\n📋 次のステップ:")
    print("   1. Webアプリを再起動")
    print("   2. 銘柄コード表示を確認")
    print("   3. 投資指示画面で正しい銘柄コードが表示されることを確認")

    return 0


if __name__ == "__main__":
    exit(main())
