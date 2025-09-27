#!/usr/bin/env python3
"""
統合J-Quantsクライアント
シンプルで堅牢なメインクライアント
"""

import logging
from unified_data_fetcher import UnifiedDataFetcher
from unified_error_handler import get_unified_error_handler
from config_loader import get_config

logger = logging.getLogger(__name__)


class UnifiedJQuantsClient:
    """統合J-Quantsクライアント"""

    def __init__(self):
        """初期化"""
        self.error_handler = get_unified_error_handler("UnifiedJQuantsClient")
        self.data_fetcher = UnifiedDataFetcher()
        
        logger.info("✅ UnifiedJQuantsClient初期化完了")

    def fetch_stock_data(self, target_date: str):
        """株価データの取得（メイン処理）"""
        logger.info(f"📊 株価データ取得を開始: {target_date}")

        try:
            # データ取得
            df = self.data_fetcher.fetch_stock_data(target_date)
            logger.info(f"✅ データ取得完了: {len(df)}件")
            return df

        except Exception as e:
            self.error_handler.log_error(e, "株価データ取得エラー")
            raise

    def save_data(self, df, output_file: str):
        """データの保存"""
        logger.info(f"💾 データを保存中: {output_file}")

        try:
            self.data_fetcher.save_data(df, output_file)
            logger.info(f"✅ データ保存完了: {output_file}")

        except Exception as e:
            self.error_handler.handle_file_error(e, output_file, "write")
            raise


def main():
    """メイン処理"""
    error_handler = get_unified_error_handler("main")

    try:
        # クライアントの初期化
        client = UnifiedJQuantsClient()

        # 設定の取得
        config = get_config()
        data_fetch_config = config.get_data_fetch_config()

        target_date = data_fetch_config.get("target_date", "20240301")
        output_file = data_fetch_config.get("output_file", "stock_data.csv")

        logger.info(f"📅 対象日: {target_date}")
        logger.info(f"📁 出力ファイル: {output_file}")

        # データ取得
        df = client.fetch_stock_data(target_date)

        # データ保存
        client.save_data(df, output_file)

        logger.info("✅ データ取得処理完了")

    except ValueError as e:
        error_handler.log_error(e, "データ取得処理 - 値エラー")
        logger.error(f"❌ データ値エラー: {e}")
        raise

    except FileNotFoundError as e:
        error_handler.log_error(e, "データ取得処理 - ファイルエラー")
        logger.error(f"❌ ファイルが見つかりません: {e}")
        raise

    except PermissionError as e:
        error_handler.log_error(e, "データ取得処理 - 権限エラー")
        logger.error(f"❌ ファイルアクセス権限エラー: {e}")
        raise

    except ConnectionError as e:
        error_handler.log_error(e, "データ取得処理 - 接続エラー")
        logger.error(f"❌ ネットワーク接続エラー: {e}")
        raise

    except Exception as e:
        error_handler.log_error(e, "データ取得処理 - 予期しないエラー")
        logger.error(f"❌ データ取得処理で予期しないエラーが発生: {e}")
        raise


if __name__ == "__main__":
    main()
