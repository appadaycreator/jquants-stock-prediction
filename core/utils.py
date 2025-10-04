#!/usr/bin/env python3
"""
ユーティリティ関数群
"""

import re


def normalize_security_code(value) -> str:
    """
    証券コードを正規化する（2024年1月以降の新形式対応）。
    - 数字のみのコード: 4桁に正規化（従来通り）
    - アルファベット含むコード: そのまま返す（新形式）
    - 空文字やNoneの場合は"0000"を返す
    
    例:
      "07203" -> "7203"  # 従来の4桁数字
      "72030" -> "7203"  # 5桁数字は4桁に正規化
      "8035" -> "8035"   # 4桁数字はそのまま
      "A1234" -> "A1234" # 新形式（アルファベット含む）
      "B001" -> "B001"   # 新形式
    """
    if value is None:
        return "0000"
    
    s = str(value).strip()
    if not s:
        return "0000"
    
    # アルファベットが含まれている場合は新形式として扱う
    if re.search(r'[A-Za-z]', s):
        return s.upper()  # 大文字に統一
    
    # 数字のみの場合は従来の処理
    digits = re.sub(r"\D", "", s)
    if not digits:
        return "0000"
    
    # 先頭ゼロを除去してから解釈
    digits = digits.lstrip("0")
    if not digits:
        return "0000"
    
    # 4桁に正規化（5桁の場合は先頭4桁を採用）
    first_four = digits[:4]
    return first_four.zfill(4)


