#!/usr/bin/env python3
"""
セクター別銘柄取得スクリプト
特定のセクターから追加銘柄を取得
"""

import requests
import json
import os
import sys
from datetime import datetime
from pathlib import Path
import logging

# 認証管理クラスのインポート
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from jquants_auth_manager import JQuantsAuthManager

# ログ設定
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/fetch_stocks_by_sector.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class SectorBasedStockFetcher:
    """セクター別銘柄取得クラス"""

    def __init__(self):
        self.data_dir = Path("docs/data")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # 認証管理クラスを初期化
        self.auth_manager = JQuantsAuthManager()
        self.id_token = self.auth_manager.get_valid_token()
        if not self.id_token:
            raise ValueError("有効なIDトークンの取得に失敗しました")

        # 追加取得対象セクター（現在少ないセクターを優先）
        self.target_sectors = [
            "情報通信・サービスその他",
            "医薬品",
            "素材・化学",
            "電気・ガス",
            "金融（除く銀行）",
            "商社・卸売",
            "小売",
            "不動産",
            "エネルギー資源",
            "鉄鋼・非鉄",
        ]

    def fetch_all_listed_info(self):
        """全上場銘柄一覧を取得"""
        url = "https://api.jquants.com/v1/listed/info"

        headers = {
            "Authorization": f"Bearer {self.id_token}",
            "Content-Type": "application/json",
            "User-Agent": "jQuants-Stock-Prediction/1.0",
        }

        logger.info(f"全上場銘柄一覧取得開始: {url}")

        try:
            response = requests.get(url, headers=headers, timeout=30)

            if response.status_code == 200:
                data = response.json()
                logger.info(f"取得成功: {len(data.get('info', []))}銘柄")
                return data
            else:
                logger.error(f"取得エラー: HTTP {response.status_code}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"リクエストエラー: {e}")
            return None

    def load_existing_stocks(self):
        """既存の銘柄データを読み込み"""
        try:
            with open(self.data_dir / "listed_info.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                return set(data.get("stocks", {}).keys())
        except FileNotFoundError:
            logger.warning("既存の銘柄データが見つかりません")
            return set()

    def select_additional_stocks(self, all_stocks, target_count=100):
        """追加銘柄の選択"""
        existing_codes = self.load_existing_stocks()
        logger.info(f"既存銘柄数: {len(existing_codes)}")

        # セクター別に銘柄を分類
        sector_stocks = {}
        for stock in all_stocks.get("info", []):
            sector = stock.get("Sector17CodeName", "")
            if sector in self.target_sectors:
                if sector not in sector_stocks:
                    sector_stocks[sector] = []
                sector_stocks[sector].append(stock)

        logger.info("セクター別銘柄数:")
        for sector, stocks in sector_stocks.items():
            logger.info(f"  {sector}: {len(stocks)}銘柄")

        # 各セクターから均等に選択
        new_stocks = {}
        stocks_per_sector = max(1, target_count // len(self.target_sectors))

        for sector in self.target_sectors:
            if sector not in sector_stocks:
                continue

            sector_stock_list = sector_stocks[sector]
            selected_count = 0

            for stock in sector_stock_list:
                if len(new_stocks) >= target_count:
                    break

                code = stock.get("Code", "")
                if not code or code in existing_codes or code in new_stocks:
                    continue

                # 主要市場の銘柄のみ選択
                market = stock.get("MarketCodeName", "")
                if market in ["プライム", "スタンダード", "グロース"]:
                    new_stocks[code] = {
                        "code": code,
                        "name": stock.get("CompanyName", ""),
                        "sector": sector,
                        "market": market,
                        "listed_info": stock,
                        "metadata": {
                            "created_at": datetime.now().isoformat(),
                            "updated_at": datetime.now().isoformat(),
                            "data_quality": "jquants_official",
                            "source": "listed_info_api",
                        },
                    }
                    selected_count += 1

                    if selected_count >= stocks_per_sector:
                        break

        logger.info(f"新規銘柄選択完了: {len(new_stocks)}銘柄")
        return new_stocks

    def merge_with_existing_data(self, new_stocks):
        """既存データと新規データをマージ"""
        try:
            # 既存データの読み込み
            with open(self.data_dir / "listed_info.json", "r", encoding="utf-8") as f:
                existing_data = json.load(f)

            # 新規銘柄を追加
            existing_data["stocks"].update(new_stocks)
            existing_data["metadata"]["total_stocks"] = len(existing_data["stocks"])
            existing_data["metadata"]["last_updated"] = datetime.now().isoformat()

            # 更新されたデータを保存
            with open(self.data_dir / "listed_info.json", "w", encoding="utf-8") as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)

            logger.info(f"データマージ完了: 総銘柄数 {existing_data['metadata']['total_stocks']}")
            return existing_data

        except Exception as e:
            logger.error(f"データマージエラー: {e}")
            return None

    def run_fetch_by_sector(self, target_count=100):
        """セクター別銘柄取得の実行"""
        try:
            logger.info("=== セクター別銘柄取得開始 ===")

            # 全上場銘柄一覧の取得
            all_stocks = self.fetch_all_listed_info()
            if not all_stocks:
                logger.error("全上場銘柄一覧の取得に失敗しました")
                return False

            # 追加銘柄の選択
            new_stocks = self.select_additional_stocks(all_stocks, target_count)
            if not new_stocks:
                logger.error("追加銘柄の選択に失敗しました")
                return False

            # 既存データとのマージ
            merged_data = self.merge_with_existing_data(new_stocks)
            if not merged_data:
                logger.error("データのマージに失敗しました")
                return False

            logger.info("=== セクター別銘柄取得完了 ===")
            return True

        except Exception as e:
            logger.error(f"セクター別銘柄取得エラー: {e}")
            return False


def main():
    """メイン処理"""
    try:
        fetcher = SectorBasedStockFetcher()
        success = fetcher.run_fetch_by_sector(target_count=100)

        if success:
            logger.info("セクター別銘柄取得が正常に完了しました")
            return 0
        else:
            logger.error("セクター別銘柄取得に失敗しました")
            return 1

    except Exception as e:
        logger.error(f"メイン処理エラー: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
