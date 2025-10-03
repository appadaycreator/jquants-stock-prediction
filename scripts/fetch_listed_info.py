#!/usr/bin/env python3
"""
jQuants API上場銘柄一覧取得スクリプト
/listed/info エンドポイントを使用して実際の銘柄データを取得
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
        logging.FileHandler("logs/fetch_listed_info.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class ListedInfoFetcher:
    """上場銘柄一覧取得クラス"""

    def __init__(self):
        self.data_dir = Path("docs/data")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # ログディレクトリの作成
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # 認証管理クラスを初期化
        self.auth_manager = JQuantsAuthManager()

        # 有効なトークンを取得
        self.id_token = self.auth_manager.get_valid_token()
        if not self.id_token:
            raise ValueError("有効なIDトークンの取得に失敗しました")

    def fetch_listed_info(self, date=None, code=None):
        """上場銘柄一覧を取得（ページング対応）"""
        url = "https://api.jquants.com/v1/listed/info"

        headers = {
            "Authorization": f"Bearer {self.id_token}",
            "Content-Type": "application/json",
            "User-Agent": "jQuants-Stock-Prediction/1.0",
        }

        params = {}
        if date:
            params["date"] = date
        if code:
            params["code"] = code

        logger.info(f"上場銘柄一覧取得開始: {url}")
        logger.info(f"パラメータ: {params}")

        all_info = []
        pagination_key = None
        page_count = 0
        max_pages = 50  # 最大ページ数を制限

        try:
            while page_count < max_pages:
                if pagination_key:
                    params["pagination_key"] = pagination_key
                
                response = requests.get(url, headers=headers, params=params, timeout=30)

                if response.status_code == 200:
                    data = response.json()
                    page_info = data.get('info', [])
                    all_info.extend(page_info)
                    
                    logger.info(f"ページ {page_count + 1} 取得成功: {len(page_info)}銘柄 (累計: {len(all_info)}銘柄)")
                    
                    # ページングキーをチェック
                    pagination_key = data.get('pagination_key')
                    if not pagination_key:
                        logger.info("ページング完了")
                        break
                    
                    page_count += 1
                else:
                    logger.error(f"取得エラー: HTTP {response.status_code}")
                    logger.error(f"レスポンス: {response.text}")
                    break

            if all_info:
                result = {"info": all_info}
                logger.info(f"全ページ取得成功: 総計 {len(all_info)}銘柄")
                return result
            else:
                logger.error("データが取得できませんでした")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"リクエストエラー: {e}")
            return None

    def get_stock_price_data(self, code, days=7):
        """個別銘柄の価格データ取得"""
        try:
            # 日付範囲の計算
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            start_str = start_date.strftime("%Y-%m-%d")
            end_str = end_date.strftime("%Y-%m-%d")

            headers = {
                "Authorization": f"Bearer {self.id_token}",
                "Content-Type": "application/json",
            }
            url = "https://api.jquants.com/v1/prices/daily_quotes"
            params = {"code": code, "from": start_str, "to": end_str}

            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            # HTTPステータスコードの詳細チェック
            if response.status_code == 200:
                data = response.json()
                quotes = data.get("daily_quotes", [])
                
                if quotes:
                    latest_quote = quotes[-1]
                    # データの妥当性チェック
                    close_price = latest_quote.get("Close")
                    open_price = latest_quote.get("Open")
                    volume = latest_quote.get("Volume")
                    
                    if close_price is not None and close_price > 0:
                        change = float(close_price) - float(open_price) if open_price else 0
                        change_percent = (change / float(open_price)) * 100 if open_price and open_price != 0 else 0
                        
                        return {
                            "current_price": float(close_price),
                            "change": change,
                            "change_percent": change_percent,
                            "volume": int(volume) if volume else 0,
                            "updated_at": latest_quote.get("Date", datetime.now().isoformat()),
                        }
                    else:
                        logger.warning(f"銘柄 {code}: 無効な価格データ")
                        return None
                else:
                    logger.warning(f"銘柄 {code}: 価格データが見つかりません")
                    return None
            elif response.status_code == 404:
                logger.warning(f"銘柄 {code}: データが見つかりません (404)")
                return None
            elif response.status_code == 429:
                logger.warning(f"銘柄 {code}: レート制限 (429) - 待機後に再試行")
                import time
                time.sleep(60)  # 1分待機
                return None
            else:
                logger.warning(f"銘柄 {code}: HTTP {response.status_code}")
                return None

        except requests.exceptions.Timeout:
            logger.warning(f"銘柄 {code}: タイムアウト")
            return None
        except requests.exceptions.ConnectionError:
            logger.warning(f"銘柄 {code}: 接続エラー")
            return None
        except Exception as e:
            logger.warning(f"銘柄 {code} の価格データ取得エラー: {e}")
            return None

    def process_listed_data(self, data):
        """上場銘柄データの処理"""
        if not data or "info" not in data:
            logger.error("データが空または無効です")
            return None

        info_list = data["info"]
        logger.info(f"処理開始: {len(info_list)}銘柄")

        # データの構造化
        processed_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "version": "2.0",
                "data_source": "jquants_listed_info",
                "total_stocks": len(info_list),
                "structure_version": "2.0",
                "update_type": "listed_info",
            },
            "stocks": {},
        }

        # 全銘柄を選択（制限を解除）
        all_stocks = []
        for stock in info_list:
            code = stock.get("Code", "")
            name = stock.get("CompanyName", "")
            sector = stock.get("Sector17CodeName", "")
            market = stock.get("MarketCodeName", "")

            # すべての銘柄を選択（市場制限を解除）
            all_stocks.append(
                {
                    "code": code,
                    "name": name,
                    "sector": sector,
                    "market": market,
                    "raw_data": stock,
                }
            )

        selected_stocks = all_stocks
        logger.info(f"全銘柄選択: {len(selected_stocks)}銘柄")

        # 構造化データの作成（バッチ処理対応）
        batch_size = 10  # バッチサイズを設定
        # テスト用に最初の100銘柄のみ処理
        test_stocks = selected_stocks[:100]
        logger.info(f"テスト用に最初の{len(test_stocks)}銘柄を処理します")
        for i, stock in enumerate(test_stocks):
            code = stock["code"]
            logger.info(f"処理中: {i+1}/{len(test_stocks)} - {stock['name']} ({code})")
            
            # 価格データの取得を一時的に無効化（テスト用）
            price_data = None
            # try:
            #     price_data = self.get_stock_price_data(code)
            # except Exception as e:
            #     logger.warning(f"銘柄 {code} の価格データ取得に失敗: {e}")
            #     price_data = None
            
            processed_data["stocks"][code] = {
                "code": code,
                "name": stock["name"],
                "sector": stock["sector"],
                "market": stock["market"],
                "currentPrice": price_data["current_price"] if price_data else None,
                "change": price_data["change"] if price_data else None,
                "changePercent": price_data["change_percent"] if price_data else None,
                "volume": price_data["volume"] if price_data else None,
                "updated_at": price_data["updated_at"] if price_data else datetime.now().isoformat(),
                "listed_info": stock["raw_data"],
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "data_quality": "jquants_official",
                    "source": "listed_info_api",
                    "price_data_available": price_data is not None,
                },
            }
            
            # API制限を考慮した待機（レート制限対応）
            import time
            time.sleep(0.1)  # 1000リクエスト/時間制限に基づく最適化

        processed_data["metadata"]["total_stocks"] = len(processed_data["stocks"])
        logger.info(f"処理完了: {len(processed_data['stocks'])}銘柄")

        return processed_data

    def save_structured_data(self, data):
        """構造化データの保存"""
        try:
            # メインファイルの保存
            main_file = self.data_dir / "listed_info.json"
            with open(main_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            logger.info(f"メインファイル保存完了: {main_file}")

            # 個別銘柄ファイルの保存
            stocks_dir = self.data_dir / "stocks"
            stocks_dir.mkdir(exist_ok=True)

            for code, stock_info in data["stocks"].items():
                individual_file = stocks_dir / f"{code}_listed.json"
                individual_data = {
                    "metadata": {
                        "code": code,
                        "generated_at": datetime.now().isoformat(),
                        "version": "2.0",
                        "type": "listed_info",
                    },
                    "stock": stock_info,
                }

                with open(individual_file, "w", encoding="utf-8") as f:
                    json.dump(individual_data, f, ensure_ascii=False, indent=2)

            logger.info(f"個別銘柄ファイル保存完了: {len(data['stocks'])}ファイル")

            # インデックスファイルの生成
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
                index_data["stocks"].append(
                    {
                        "code": code,
                        "name": stock_info["name"],
                        "sector": stock_info["sector"],
                        "market": stock_info["market"],
                        "currentPrice": stock_info.get("currentPrice"),
                        "change": stock_info.get("change"),
                        "changePercent": stock_info.get("changePercent"),
                        "volume": stock_info.get("volume"),
                        "updated_at": stock_info["metadata"]["updated_at"],
                        "file_path": f"stocks/{code}_listed.json",
                    }
                )

            # セクター順でソート
            index_data["stocks"].sort(key=lambda x: (x["sector"], x["name"]))

            index_file = self.data_dir / "listed_index.json"
            with open(index_file, "w", encoding="utf-8") as f:
                json.dump(index_data, f, ensure_ascii=False, indent=2)

            logger.info(f"インデックスファイル保存完了: {index_file}")

            # メタデータファイルの生成
            metadata_dir = self.data_dir / "metadata"
            metadata_dir.mkdir(exist_ok=True)

            basic_metadata = {
                "last_updated": data["metadata"]["generated_at"],
                "total_stocks": data["metadata"]["total_stocks"],
                "data_source": data["metadata"]["data_source"],
                "version": data["metadata"]["version"],
                "file_size": main_file.stat().st_size,
                "update_status": "success",
                "data_type": "listed_info",
            }

            metadata_file = metadata_dir / "listed_info.json"
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(basic_metadata, f, ensure_ascii=False, indent=2)

            logger.info(f"メタデータファイル保存完了: {metadata_file}")

        except Exception as e:
            logger.error(f"データ保存エラー: {e}")
            raise

    def run_fetch(self):
        """上場銘柄一覧取得の実行"""
        try:
            logger.info("=== 上場銘柄一覧取得開始 ===")

            # 上場銘柄一覧の取得
            listed_data = self.fetch_listed_info()
            if not listed_data:
                logger.error("上場銘柄一覧の取得に失敗しました")
                return False

            # データの処理
            processed_data = self.process_listed_data(listed_data)
            if not processed_data:
                logger.error("データの処理に失敗しました")
                return False

            # データの保存
            self.save_structured_data(processed_data)

            logger.info("=== 上場銘柄一覧取得完了 ===")
            return True

        except Exception as e:
            logger.error(f"上場銘柄一覧取得エラー: {e}")
            return False


def main():
    """メイン処理"""
    try:
        fetcher = ListedInfoFetcher()
        success = fetcher.run_fetch()

        if success:
            logger.info("上場銘柄一覧取得が正常に完了しました")
            return 0
        else:
            logger.error("上場銘柄一覧取得に失敗しました")
            return 1

    except Exception as e:
        logger.error(f"メイン処理エラー: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
