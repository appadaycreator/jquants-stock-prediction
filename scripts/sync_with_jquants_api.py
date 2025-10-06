#!/usr/bin/env python3
"""
jQuants APIデータと完全同期するスクリプト
実際のAPIから最新データを取得してstock_data.jsonを更新
"""

import json
import os
import sys
import requests
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# 認証管理クラスのインポート
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from jquants_auth_manager_final import JQuantsAuthManagerFinal

# ログ設定
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/sync_with_jquants_api.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class JQuantsAPISyncer:
    """jQuants APIデータ同期クラス"""

    def __init__(self):
        self.data_dir = Path("data")
        self.docs_data_dir = Path("docs/data")
        self.listed_index_file = self.docs_data_dir / "listed_index.json"

        # 認証管理クラスを初期化
        self.auth_manager = JQuantsAuthManagerFinal()

        # 有効なトークンを取得
        self.id_token = self.auth_manager.get_valid_token()
        if not self.id_token:
            raise ValueError("有効なIDトークンの取得に失敗しました")

        # API設定
        self.base_url = "https://api.jquants.com/v1"
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.id_token}",
                "Content-Type": "application/json",
                "User-Agent": "jQuants-Stock-Prediction/1.0",
            }
        )

        # レート制限設定
        self.rate_limit_delay = 0.1  # 100ms間隔
        self.max_retries = 3

    def load_listed_index(self) -> Dict[str, Any]:
        """listed_index.jsonを読み込み"""
        try:
            with open(self.listed_index_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info(f"listed_index.json読み込み完了: {len(data.get('stocks', []))}銘柄")
            return data
        except Exception as e:
            logger.error(f"listed_index.json読み込みエラー: {e}")
            return {}

    def get_stock_prices_from_api(
        self, code: str, days: int = 30
    ) -> List[Dict[str, Any]]:
        """jQuants APIから実際の株価データを取得"""
        try:
            # 日付範囲の計算
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            start_str = start_date.strftime("%Y-%m-%d")
            end_str = end_date.strftime("%Y-%m-%d")

            logger.info(f"銘柄 {code} のAPIデータ取得中 ({start_str} - {end_str})")

            url = f"{self.base_url}/prices/daily_quotes"
            params = {"code": code, "from": start_str, "to": end_str}

            # リトライ機能付きAPI呼び出し
            for attempt in range(self.max_retries):
                try:
                    response = self.session.get(url, params=params, timeout=30)

                    if response.status_code == 200:
                        data = response.json()
                        quotes = data.get("daily_quotes", [])

                        # データ形式を統一
                        formatted_quotes = []
                        for quote in quotes:
                            formatted_quote = {
                                "date": quote.get("Date", ""),
                                "code": quote.get("Code", code),
                                "open": float(quote.get("Open", 0)),
                                "high": float(quote.get("High", 0)),
                                "low": float(quote.get("Low", 0)),
                                "close": float(quote.get("Close", 0)),
                                "volume": int(quote.get("Volume", 0)),
                            }
                            formatted_quotes.append(formatted_quote)

                        logger.info(f"銘柄 {code} のAPIデータ取得成功: {len(formatted_quotes)}件")
                        return formatted_quotes

                    elif response.status_code == 429:  # レート制限
                        wait_time = 2**attempt
                        logger.warning(f"レート制限エラー、{wait_time}秒待機...")
                        time.sleep(wait_time)
                        continue

                    else:
                        logger.warning(f"API呼び出しエラー: HTTP {response.status_code}")
                        if attempt == self.max_retries - 1:
                            return []
                        continue

                except requests.exceptions.RequestException as e:
                    logger.warning(
                        f"API呼び出しエラー (試行 {attempt + 1}/{self.max_retries}): {e}"
                    )
                    if attempt == self.max_retries - 1:
                        return []
                    time.sleep(1)
                    continue

            return []

        except Exception as e:
            logger.error(f"銘柄 {code} のAPIデータ取得エラー: {e}")
            return []

    def sync_stock_data(self, max_stocks: int = None) -> Dict[str, Any]:
        """jQuants APIデータと同期"""
        logger.info("=== jQuants APIデータ同期開始 ===")

        # listed_index.jsonを読み込み
        listed_data = self.load_listed_index()
        stocks = listed_data.get("stocks", [])

        if not stocks:
            logger.error("銘柄データが見つかりません")
            return {}

        logger.info(f"処理対象銘柄数: {len(stocks)}")

        # 最大銘柄数の制限
        if max_stocks:
            stocks = stocks[:max_stocks]
            logger.info(f"最大銘柄数制限: {max_stocks}")

        synced_data = {}
        processed_count = 0
        error_count = 0
        api_success_count = 0

        for i, stock in enumerate(stocks):
            code = stock.get("code", "")
            name = stock.get("name", "")

            if not code:
                logger.warning("銘柄コードが空です")
                continue

            try:
                # jQuants APIから実際のデータを取得
                api_data = self.get_stock_prices_from_api(code)

                if api_data:
                    synced_data[code] = api_data
                    api_success_count += 1
                    logger.info(f"銘柄 {code} ({name}) のAPIデータ同期成功: {len(api_data)}件")
                else:
                    # APIデータが取得できない場合は、既存のサンプルデータを使用
                    logger.warning(f"銘柄 {code} ({name}) のAPIデータ取得失敗、スキップ")
                    error_count += 1

                processed_count += 1

                # レート制限対応
                time.sleep(self.rate_limit_delay)

                # 進捗表示
                if processed_count % 50 == 0:
                    logger.info(
                        f"進捗: {processed_count}/{len(stocks)}銘柄処理完了 (API成功: {api_success_count})"
                    )

            except Exception as e:
                logger.error(f"銘柄 {code} の処理エラー: {e}")
                error_count += 1
                continue

        logger.info(f"=== API同期完了 ===")
        logger.info(f"処理済み銘柄数: {processed_count}")
        logger.info(f"API成功銘柄数: {api_success_count}")
        logger.info(f"エラー数: {error_count}")
        logger.info(f"同期後データ銘柄数: {len(synced_data)}")

        return synced_data

    def save_synced_data(self, data: Dict[str, Any]):
        """同期されたデータを保存"""
        try:
            # バックアップを作成
            original_file = self.data_dir / "stock_data.json"
            if original_file.exists():
                backup_file = (
                    self.data_dir
                    / f"stock_data_api_sync_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                )
                original_file.rename(backup_file)
                logger.info(f"バックアップファイル作成: {backup_file}")

            # 同期されたデータを保存
            with open(original_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            logger.info(f"jQuants API同期データを保存: {original_file}")

            # メタデータを保存
            metadata = {
                "generated_at": datetime.now().isoformat(),
                "version": "3.0",
                "total_stocks": len(data),
                "data_type": "jquants_api_synced",
                "description": "jQuants APIから取得した実際の株価データ",
                "api_sync": True,
                "data_source": "jquants_api",
            }

            metadata_file = self.data_dir / "stock_data_metadata.json"
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

            logger.info(f"メタデータファイル保存: {metadata_file}")

        except Exception as e:
            logger.error(f"データ保存エラー: {e}")
            raise

    def run_sync(self, max_stocks: int = None):
        """API同期処理を実行"""
        try:
            # jQuants APIデータと同期
            synced_data = self.sync_stock_data(max_stocks)

            if not synced_data:
                logger.error("同期されたデータが生成されませんでした")
                return False

            # データを保存
            self.save_synced_data(synced_data)

            logger.info("=== jQuants APIデータ同期完了 ===")
            return True

        except Exception as e:
            logger.error(f"API同期処理エラー: {e}")
            return False


def main():
    """メイン処理"""
    import argparse

    parser = argparse.ArgumentParser(description="jQuants APIデータ同期スクリプト")
    parser.add_argument("--max-stocks", type=int, help="処理する最大銘柄数（テスト用）")
    parser.add_argument("--test", action="store_true", help="テストモード（5銘柄のみ処理）")

    args = parser.parse_args()

    # テストモードの場合は5銘柄のみ処理
    max_stocks = 5 if args.test else args.max_stocks

    try:
        syncer = JQuantsAPISyncer()
        success = syncer.run_sync(max_stocks)

        if success:
            print("✅ jQuants APIデータ同期が完了しました")
        else:
            print("❌ jQuants APIデータ同期に失敗しました")
            sys.exit(1)

    except Exception as e:
        print(f"❌ エラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
