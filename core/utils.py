#!/usr/bin/env python3
"""
ユーティリティ関数群
"""

import re


def normalize_security_code(value) -> str:
    """
    証券コードを正規化して4桁の数値文字列にする。
    - 非数字は除去
    - 先頭から4桁を採用（それ以上は切り捨て）
    - 4桁未満は左ゼロ埋め（末尾ゼロ付与はしない）
    例:
      "07203" -> "7203"
      "72030" -> "7203"  # 末尾0が紛れたケースを防止（先頭4桁を採用）
      8035 -> "8035"
    """
    s = str(value) if value is not None else ""
    digits = re.sub(r"\D", "", s)
    # 先頭ゼロを除去してから解釈（例: "007203" -> "7203"）
    digits = digits.lstrip("0")
    if not digits:
        return "0000"
    first_four = digits[:4]
    return first_four.zfill(4)


