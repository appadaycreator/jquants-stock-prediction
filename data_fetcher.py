#!/usr/bin/env python3
"""
データ取得モジュール
J-Quants APIからのデータ取得機能を担当する独立したクラス
"""

import requests
import pandas as pd
import logging
import time
from typing import Dict, Any, Optional
from auth_manager import AuthManager
from config_loader import get_config

logger = logging.getLogger(__name__)


class DataFetcher:
    """J-Quants APIデータ取得クラス"""

    def __init__(self):
        """初期化"""
        self.auth_manager = AuthManager()
        self.session = requests.Session()

        # 設定を読み込み
        config = get_config()
        self.jquants_config = config.get_jquants_config()
        self.data_fetch_config = config.get_data_fetch_config()

        # セッション設定
        self.session.timeout = self.data_fetch_config.get("timeout", 30)

    def _make_request_with_retry(
        self, method: str, url: str, **kwargs
    ) -> requests.Response:
        """リトライ機能付きHTTPリクエスト"""
        max_retries = self.data_fetch_config.get("max_retries", 3)
        retry_interval = self.data_fetch_config.get("retry_interval", 5)

        for attempt in range(max_retries + 1):
            try:
                logger.info(f"APIリクエスト (試行 {attempt + 1}/{max_retries + 1})")
                response = self.session.request(method, url, **kwargs)

                if response.status_code == 200:
                    logger.info("✅ APIリクエスト成功")
                    return response
                else:
                    logger.warning(f"⚠️ APIリクエスト失敗: {response.status_code}")

            except requests.exceptions.Timeout as e:
                logger.warning(
                    f"⏰ タイムアウト (試行 {attempt + 1}/{max_retries + 1})"
                )
                if attempt < max_retries:
                    logger.info(f"⏳ {retry_interval}秒後にリトライします...")
                    time.sleep(retry_interval)
                    continue
                else:
                    raise

            except requests.exceptions.ConnectionError as e:
                logger.warning(f"🔌 接続エラー (試行 {attempt + 1}/{max_retries + 1})")
                if attempt < max_retries:
                    logger.info(f"⏳ {retry_interval}秒後にリトライします...")
                    time.sleep(retry_interval)
                    continue
                else:
                    raise

            except requests.exceptions.RequestException as e:
                logger.error(
                    f"❌ リクエストエラー (試行 {attempt + 1}/{max_retries + 1}): {e}"
                )
                if attempt < max_retries:
                    logger.info(f"⏳ {retry_interval}秒後にリトライします...")
                    time.sleep(retry_interval)
                    continue
                else:
                    raise

        # 全てのリトライが失敗した場合
        raise Exception(f"APIリクエストが{max_retries + 1}回失敗しました")

    def fetch_stock_data(self, target_date: str) -> pd.DataFrame:
        """株価データの取得"""
        logger.info(f"📊 株価データ取得を開始: {target_date}")

        # 認証ヘッダーの取得
        headers = self.auth_manager.get_auth_headers()

        # 株価データの取得
        price_url = f"{self.jquants_config.get('base_url', 'https://api.jquants.com/v1')}/prices/daily_quotes"
        params = {"date": target_date}

        response = self._make_request_with_retry(
            "GET", price_url, headers=headers, params=params
        )
        data = response.json()

        # DataFrameに変換
        df = pd.DataFrame(data["daily_quotes"])
        logger.info(f"✅ データ取得完了: {len(df)}件")

        return df

    def save_data(self, df: pd.DataFrame, output_file: str) -> None:
        """データの保存"""
        logger.info(f"💾 データを保存中: {output_file}")

        try:
            # データフレームの基本検証
            if df is None or df.empty:
                raise ValueError("保存するデータが空です")

            # 出力ディレクトリの確認・作成
            import os

            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                logger.info(f"📁 出力ディレクトリを作成: {output_dir}")

            df.to_csv(output_file, index=False)
            logger.info(f"✅ データ保存完了: {output_file} ({len(df)}件)")

        except Exception as e:
            logger.error(f"❌ データ保存エラー: {e}")
            raise
