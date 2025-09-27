#!/usr/bin/env python3
"""
統合データフェッチャーモジュール
シンプルで堅牢なデータ取得機能を提供
"""

import logging
import time
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from unified_error_handler import get_unified_error_handler
from secure_auth_manager import SecureAuthManager
from config_loader import get_config

logger = logging.getLogger(__name__)


class UnifiedDataFetcher:
    """統合データフェッチャークラス"""

    def __init__(self):
        """初期化"""
        self.error_handler = get_unified_error_handler("UnifiedDataFetcher")
        self.auth_manager = SecureAuthManager()
        self.session = requests.Session()
        
        # 設定の読み込み
        try:
            config = get_config()
            self.jquants_config = config.get_jquants_config()
            self.data_fetch_config = config.get_data_fetch_config()
            
            # セッション設定
            self.session.timeout = self.data_fetch_config.get("timeout", 30)
            
            logger.info("✅ UnifiedDataFetcher初期化完了")
            
        except Exception as e:
            self.error_handler.log_error(e, "UnifiedDataFetcher初期化エラー")
            raise

    def _make_request_with_retry(
        self, method: str, url: str, **kwargs
    ) -> requests.Response:
        """リトライ機能付きHTTPリクエスト"""
        max_retries = self.data_fetch_config.get("max_retries", 3)
        retry_interval = self.data_fetch_config.get("retry_interval", 5)

        for attempt in range(max_retries + 1):
            try:
                logger.info(f"APIリクエスト (試行 {attempt + 1}/{max_retries + 1}): {method} {url}")
                response = self.session.request(method, url, **kwargs)

                if response.status_code == 200:
                    logger.info(f"✅ APIリクエスト成功: {response.status_code}")
                    return response
                else:
                    # HTTPエラーの詳細ログ
                    self.error_handler.handle_api_error(
                        requests.exceptions.HTTPError(
                            f"HTTP {response.status_code}: {response.text}"
                        ),
                        "J-Quants API",
                        url,
                        response.status_code,
                    )
                    logger.warning(f"⚠️ APIリクエスト失敗: {response.status_code}")

            except requests.exceptions.Timeout as e:
                if attempt < max_retries:
                    logger.warning(f"⏰ タイムアウト (試行 {attempt + 1}/{max_retries + 1})")
                    logger.info(f"⏳ {retry_interval}秒後にリトライします...")
                    time.sleep(retry_interval)
                    continue
                else:
                    self.error_handler.handle_api_error(e, "J-Quants API", url)
                    raise

            except requests.exceptions.ConnectionError as e:
                if attempt < max_retries:
                    logger.warning(f"🔌 接続エラー (試行 {attempt + 1}/{max_retries + 1})")
                    logger.info(f"⏳ {retry_interval}秒後にリトライします...")
                    time.sleep(retry_interval)
                    continue
                else:
                    self.error_handler.handle_api_error(e, "J-Quants API", url)
                    raise

            except requests.exceptions.RequestException as e:
                self.error_handler.handle_api_error(e, "J-Quants API", url)
                if attempt < max_retries:
                    logger.info(f"⏳ {retry_interval}秒後にリトライします...")
                    time.sleep(retry_interval)
                    continue
                else:
                    raise

        # 全てのリトライが失敗した場合
        final_error = Exception(f"APIリクエストが{max_retries + 1}回失敗しました")
        self.error_handler.log_error(
            final_error,
            "APIリクエスト最終失敗",
            {
                "method": method,
                "url": url,
                "max_retries": max_retries,
                "retry_interval": retry_interval,
            },
        )
        raise final_error

    def _validate_stock_data(self, data: Dict[str, Any]) -> bool:
        """取得した株価データの検証"""
        logger.info("🔍 データ検証を実行中...")

        # 基本的な構造チェック
        if not isinstance(data, dict):
            logger.error("❌ データが辞書形式ではありません")
            return False

        if "daily_quotes" not in data:
            logger.error("❌ daily_quotesキーが見つかりません")
            return False

        quotes = data["daily_quotes"]
        if not isinstance(quotes, list):
            logger.error("❌ daily_quotesがリスト形式ではありません")
            return False

        if len(quotes) == 0:
            logger.warning("⚠️ 取得データが空です")
            return False

        # 必須フィールドのチェック
        required_fields = ["Code", "Date", "Open", "High", "Low", "Close", "Volume"]
        sample_quote = quotes[0]
        missing_fields = [
            field for field in required_fields if field not in sample_quote
        ]

        if missing_fields:
            logger.error(f"❌ 必須フィールドが不足: {missing_fields}")
            return False

        # データ型の検証
        for i, quote in enumerate(quotes[:5]):  # 最初の5件をサンプルチェック
            try:
                float(quote.get("Close", 0))
                float(quote.get("Volume", 0))
                pd.to_datetime(quote.get("Date"))
            except (ValueError, TypeError) as e:
                logger.error(f"❌ データ型エラー (行{i}): {e}")
                return False

        logger.info(f"✅ データ検証完了: {len(quotes)}件のデータを確認")
        return True

    def fetch_stock_data(self, target_date: str) -> pd.DataFrame:
        """株価データの取得"""
        logger.info(f"📊 株価データ取得を開始: {target_date}")

        try:
            # 認証ヘッダーの取得
            headers = self.auth_manager.get_auth_headers()

            # 株価データの取得
            price_url = f"{self.jquants_config.get('base_url', 'https://api.jquants.com/v1')}/prices/daily_quotes"
            params = {"date": target_date}

            response = self._make_request_with_retry(
                "GET", price_url, headers=headers, params=params
            )
            data = response.json()

            # データ検証
            if not self._validate_stock_data(data):
                raise ValueError("取得データの検証に失敗しました")

            # DataFrameに変換
            df = pd.DataFrame(data["daily_quotes"])
            logger.info(f"✅ データ取得完了: {len(df)}件")

            return df

        except Exception as e:
            self.error_handler.log_error(e, "株価データ取得エラー")
            raise

    def save_data(self, df: pd.DataFrame, output_file: str) -> None:
        """データの保存"""
        logger.info(f"💾 データを保存中: {output_file}")

        try:
            # データフレームの基本検証
            if df is None or df.empty:
                raise ValueError("保存するデータが空です")

            # 出力ディレクトリの確認・作成
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                logger.info(f"📁 出力ディレクトリを作成: {output_dir}")

            df.to_csv(output_file, index=False)
            logger.info(f"✅ データ保存完了: {output_file} ({len(df)}件)")

        except Exception as e:
            self.error_handler.handle_file_error(e, output_file, "write")
            raise
