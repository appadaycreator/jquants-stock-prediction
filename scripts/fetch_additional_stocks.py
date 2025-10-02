#!/usr/bin/env python3
"""
追加銘柄取得スクリプト
既存の100銘柄に加えて、さらに100銘柄を追加取得
"""

import requests
import json
import os
import sys
from datetime import datetime, timedelta
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
        logging.FileHandler("logs/fetch_additional_stocks.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class AdditionalStocksFetcher:
    """追加銘柄取得クラス"""

    def __init__(self):
        self.data_dir = Path("docs/data")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # 認証管理クラスを初期化
        self.auth_manager = JQuantsAuthManager()
        self.id_token = self.auth_manager.get_valid_token()
        if not self.id_token:
            raise ValueError("有効なIDトークンの取得に失敗しました")

    def fetch_listed_info_with_date(self, date_str):
        """指定日付の上場銘柄一覧を取得"""
        url = "https://api.jquants.com/v1/listed/info"
        
        headers = {
            "Authorization": f"Bearer {self.id_token}",
            "Content-Type": "application/json",
            "User-Agent": "jQuants-Stock-Prediction/1.0",
        }
        
        params = {"date": date_str}
        
        logger.info(f"上場銘柄一覧取得開始: {url} (日付: {date_str})")
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
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

    def fetch_additional_stocks(self, target_count=100):
        """追加銘柄の取得"""
        logger.info(f"追加銘柄取得開始 (目標: {target_count}銘柄)")
        
        # 既存銘柄の読み込み
        existing_codes = self.load_existing_stocks()
        logger.info(f"既存銘柄数: {len(existing_codes)}")
        
        # 過去30日間の日付リストを生成
        dates = []
        for i in range(30):
            date = datetime.now() - timedelta(days=i)
            dates.append(date.strftime("%Y-%m-%d"))
        
        new_stocks = {}
        attempts = 0
        max_attempts = 10
        
        for date_str in dates:
            if len(new_stocks) >= target_count:
                break
                
            attempts += 1
            if attempts > max_attempts:
                logger.warning("最大試行回数に達しました")
                break
                
            logger.info(f"日付 {date_str} の銘柄データを取得中...")
            data = self.fetch_listed_info_with_date(date_str)
            
            if not data or "info" not in data:
                continue
                
            for stock in data["info"]:
                code = stock.get("Code", "")
                if not code or code in existing_codes or code in new_stocks:
                    continue
                    
                # 主要市場の銘柄のみ選択
                market = stock.get("MarketCodeName", "")
                if market in ["プライム", "スタンダード", "グロース"]:
                    new_stocks[code] = {
                        "code": code,
                        "name": stock.get("CompanyName", ""),
                        "sector": stock.get("Sector17CodeName", ""),
                        "market": market,
                        "listed_info": stock,
                        "metadata": {
                            "created_at": datetime.now().isoformat(),
                            "updated_at": datetime.now().isoformat(),
                            "data_quality": "jquants_official",
                            "source": "listed_info_api",
                        },
                    }
                    
                    if len(new_stocks) >= target_count:
                        break
        
        logger.info(f"新規銘柄取得完了: {len(new_stocks)}銘柄")
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

    def run_fetch_additional(self, target_count=100):
        """追加銘柄取得の実行"""
        try:
            logger.info("=== 追加銘柄取得開始 ===")
            
            # 追加銘柄の取得
            new_stocks = self.fetch_additional_stocks(target_count)
            if not new_stocks:
                logger.error("追加銘柄の取得に失敗しました")
                return False
            
            # 既存データとのマージ
            merged_data = self.merge_with_existing_data(new_stocks)
            if not merged_data:
                logger.error("データのマージに失敗しました")
                return False
            
            # インデックスファイルの更新
            self.update_index_file(merged_data)
            
            logger.info("=== 追加銘柄取得完了 ===")
            return True
            
        except Exception as e:
            logger.error(f"追加銘柄取得エラー: {e}")
            return False

    def update_index_file(self, data):
        """インデックスファイルの更新"""
        try:
            index_data = {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "version": "2.0",
                    "total_stocks": len(data["stocks"]),
                    "last_updated": data["metadata"]["generated_at"],
                    "data_type": "listed_info",
                },
                "stocks": [],
            }
            
            for code, stock_info in data["stocks"].items():
                index_data["stocks"].append({
                    "code": code,
                    "name": stock_info["name"],
                    "sector": stock_info["sector"],
                    "market": stock_info["market"],
                    "updated_at": stock_info["metadata"]["updated_at"],
                    "file_path": f"stocks/{code}_listed.json",
                })
            
            # セクター順でソート
            index_data["stocks"].sort(key=lambda x: (x["sector"], x["name"]))
            
            # インデックスファイルの保存
            index_file = self.data_dir / "listed_index.json"
            with open(index_file, "w", encoding="utf-8") as f:
                json.dump(index_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"インデックスファイル更新完了: {index_file}")
            
        except Exception as e:
            logger.error(f"インデックスファイル更新エラー: {e}")


def main():
    """メイン処理"""
    try:
        fetcher = AdditionalStocksFetcher()
        success = fetcher.run_fetch_additional(target_count=100)
        
        if success:
            logger.info("追加銘柄取得が正常に完了しました")
            return 0
        else:
            logger.error("追加銘柄取得に失敗しました")
            return 1
            
    except Exception as e:
        logger.error(f"メイン処理エラー: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
