#!/usr/bin/env python3
"""
銘柄数確認スクリプト
現在取得されている銘柄数を確認
"""

import json
import os
from pathlib import Path


def check_stock_count():
    """銘柄数の確認"""
    data_dir = Path("docs/data")

    try:
        # listed_info.jsonの確認
        with open(data_dir / "listed_info.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            total_stocks = data.get("metadata", {}).get("total_stocks", 0)
            last_updated = data.get("metadata", {}).get("last_updated", "")

            print(f"📊 現在の銘柄数: {total_stocks}")
            print(f"🕒 最終更新: {last_updated}")

            # セクター別統計
            sectors = {}
            markets = {}

            for code, stock_info in data.get("stocks", {}).items():
                sector = stock_info.get("sector", "不明")
                market = stock_info.get("market", "不明")

                sectors[sector] = sectors.get(sector, 0) + 1
                markets[market] = markets.get(market, 0) + 1

            print("\n📈 セクター別銘柄数:")
            for sector, count in sorted(sectors.items()):
                print(f"  {sector}: {count}銘柄")

            print("\n🏢 市場別銘柄数:")
            for market, count in sorted(markets.items()):
                print(f"  {market}: {count}銘柄")

    except FileNotFoundError:
        print("❌ listed_info.jsonが見つかりません")
    except Exception as e:
        print(f"❌ エラー: {e}")


if __name__ == "__main__":
    check_stock_count()
