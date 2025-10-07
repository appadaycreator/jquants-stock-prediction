#!/usr/bin/env python3
"""
銘柄コード最適化のテスト
2024年1月以降の新形式（アルファベット含む）に対応
"""

import unittest
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.utils import normalize_security_code


class TestStockCodeOptimization(unittest.TestCase):
    """銘柄コード最適化のテストクラス"""

    def test_legacy_format_normalization(self):
        """従来形式（4桁数字）の正規化テスト"""
        test_cases = [
            ("7203", "7203"),  # 4桁数字
            ("07203", "7203"),  # 5桁数字（先頭0）
            ("72030", "7203"),  # 5桁数字（末尾0）
            ("8035", "8035"),  # 4桁数字
            ("6758", "6758"),  # 4桁数字
        ]

        for input_code, expected in test_cases:
            with self.subTest(input_code=input_code):
                result = normalize_security_code(input_code)
                self.assertEqual(
                    result,
                    expected,
                    f"入力: {input_code}, 期待値: {expected}, 実際: {result}",
                )

    def test_new_format_normalization(self):
        """新形式（アルファベット含む）の正規化テスト"""
        test_cases = [
            ("A1234", "A1234"),  # 新形式（大文字）
            ("a1234", "A1234"),  # 新形式（小文字→大文字）
            ("B0001", "B0001"),  # 新形式
            ("C9999", "C9999"),  # 新形式
            ("Z0000", "Z0000"),  # 新形式
        ]

        for input_code, expected in test_cases:
            with self.subTest(input_code=input_code):
                result = normalize_security_code(input_code)
                self.assertEqual(
                    result,
                    expected,
                    f"入力: {input_code}, 期待値: {expected}, 実際: {result}",
                )

    def test_edge_cases(self):
        """エッジケースのテスト"""
        test_cases = [
            (None, "0000"),  # None
            ("", "0000"),  # 空文字
            ("   ", "0000"),  # 空白のみ
            ("0000", "0000"),  # 全て0
            ("000", "0000"),  # 3桁
            ("12345", "1234"),  # 5桁数字
        ]

        for input_code, expected in test_cases:
            with self.subTest(input_code=input_code):
                result = normalize_security_code(input_code)
                self.assertEqual(
                    result,
                    expected,
                    f"入力: {input_code}, 期待値: {expected}, 実際: {result}",
                )

    def test_mixed_format_handling(self):
        """混合形式の処理テスト"""
        test_cases = [
            ("A1234", "A1234"),  # 新形式
            ("7203", "7203"),  # 従来形式
            ("B0001", "B0001"),  # 新形式
            ("8035", "8035"),  # 従来形式
        ]

        for input_code, expected in test_cases:
            with self.subTest(input_code=input_code):
                result = normalize_security_code(input_code)
                self.assertEqual(
                    result,
                    expected,
                    f"入力: {input_code}, 期待値: {expected}, 実際: {result}",
                )

    def test_invalid_formats(self):
        """無効な形式のテスト"""
        invalid_cases = [
            "123",  # 3桁数字
            "123456",  # 6桁数字
            "AB1234",  # 2文字アルファベット
            "A123",  # 3桁数字
            "A12345",  # 5桁数字
            "1234A",  # 末尾アルファベット
            "A1B2C",  # 複数アルファベット
        ]

        for invalid_code in invalid_cases:
            with self.subTest(invalid_code=invalid_code):
                result = normalize_security_code(invalid_code)
                # 無効な形式はそのまま返されるか、適切に処理される
                self.assertIsInstance(result, str)
                self.assertGreater(len(result), 0)

    def test_consistency_with_legacy_system(self):
        """従来システムとの一貫性テスト"""
        # 従来の4桁数字は同じ結果になることを確認
        legacy_codes = ["7203", "8035", "6758", "9875"]

        for code in legacy_codes:
            with self.subTest(code=code):
                result = normalize_security_code(code)
                self.assertEqual(
                    result,
                    code,
                    f"従来コード {code} の処理結果が一致しません: {result}",
                )

    def test_new_format_uppercase_conversion(self):
        """新形式の大文字変換テスト"""
        test_cases = [
            ("a1234", "A1234"),
            ("b0001", "B0001"),
            ("c9999", "C9999"),
            ("A1234", "A1234"),  # 既に大文字
        ]

        for input_code, expected in test_cases:
            with self.subTest(input_code=input_code):
                result = normalize_security_code(input_code)
                self.assertEqual(
                    result,
                    expected,
                    f"入力: {input_code}, 期待値: {expected}, 実際: {result}",
                )


class TestStockCodeValidation(unittest.TestCase):
    """銘柄コードバリデーションのテストクラス"""

    def test_valid_legacy_codes(self):
        """有効な従来形式コードのテスト"""
        valid_codes = ["7203", "8035", "6758", "9875"]

        for code in valid_codes:
            with self.subTest(code=code):
                result = normalize_security_code(code)
                self.assertTrue(
                    len(result) == 4 and result.isdigit(),
                    f"従来形式コード {code} が正しく処理されませんでした: {result}",
                )

    def test_valid_new_codes(self):
        """有効な新形式コードのテスト"""
        valid_codes = ["A1234", "B0001", "C9999"]

        for code in valid_codes:
            with self.subTest(code=code):
                result = normalize_security_code(code)
                self.assertTrue(
                    len(result) == 5 and result[0].isalpha() and result[1:].isdigit(),
                    f"新形式コード {code} が正しく処理されませんでした: {result}",
                )

    def test_code_format_detection(self):
        """コード形式の検出テスト"""
        # 従来形式の検出
        legacy_codes = ["7203", "8035", "6758"]
        for code in legacy_codes:
            with self.subTest(code=code):
                result = normalize_security_code(code)
                self.assertTrue(
                    result.isdigit() and len(result) == 4,
                    f"従来形式として認識されませんでした: {code} -> {result}",
                )

        # 新形式の検出
        new_codes = ["A1234", "B0001", "C9999"]
        for code in new_codes:
            with self.subTest(code=code):
                result = normalize_security_code(code)
                self.assertTrue(
                    result[0].isalpha() and result[1:].isdigit() and len(result) == 5,
                    f"新形式として認識されませんでした: {code} -> {result}",
                )


if __name__ == "__main__":
    unittest.main()
