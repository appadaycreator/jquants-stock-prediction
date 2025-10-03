#!/usr/bin/env python3
"""
銘柄数確認スクリプト
現在取得されている銘柄数を確認
"""

import json
import os
import logging
from pathlib import Path
from datetime import datetime

# ログ設定
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/check_stock_count.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def check_stock_count():
    """銘柄数の確認"""
    data_dir = Path("docs/data")

    try:
        # listed_info.jsonの確認
        with open(data_dir / "listed_info.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            total_stocks = data.get("metadata", {}).get("total_stocks", 0)
            last_updated = data.get("metadata", {}).get("last_updated", "")

            logger.info(f"📊 現在の銘柄数: {total_stocks}")
            logger.info(f"🕒 最終更新: {last_updated}")

            # セクター別統計
            sectors = {}
            markets = {}

            for code, stock_info in data.get("stocks", {}).items():
                sector = stock_info.get("sector", "不明")
                market = stock_info.get("market", "不明")

                sectors[sector] = sectors.get(sector, 0) + 1
                markets[market] = markets.get(market, 0) + 1

            logger.info("\n📈 セクター別銘柄数:")
            for sector, count in sorted(sectors.items()):
                logger.info(f"  {sector}: {count}銘柄")

            logger.info("\n🏢 市場別銘柄数:")
            for market, count in sorted(markets.items()):
                logger.info(f"  {market}: {count}銘柄")

            # 統計情報の保存
            stats = {
                "total_stocks": total_stocks,
                "last_updated": last_updated,
                "sectors": sectors,
                "markets": markets,
                "check_timestamp": datetime.now().isoformat(),
            }

            with open(data_dir / "stock_count_stats.json", "w", encoding="utf-8") as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)

    except FileNotFoundError:
        logger.error("❌ listed_info.jsonが見つかりません")
    except Exception as e:
        logger.error(f"❌ エラー: {e}")


if __name__ == "__main__":
    check_stock_count()
