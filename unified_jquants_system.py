#!/usr/bin/env python3
"""
統合J-Quantsシステム
完全に統合された、セキュアで堅牢なJ-Quants APIクライアントシステム
"""

import os
import logging
import requests
import pandas as pd
import time
import re
import traceback
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
from config_loader import get_config


class UnifiedJQuantsSystem:
    """統合J-Quantsシステム - 単一責任原則に基づく完全統合システム"""
    
    def __init__(self):
        """初期化"""
        self.logger = logging.getLogger(__name__)
        self.error_count = 0
        self.sensitive_keys = ["password", "token", "key", "secret", "auth", "email"]
        
        # 環境変数の読み込み
        load_dotenv()
        
        # 設定の読み込み
        try:
            config = get_config()
            self.jquants_config = config.get_jquants_config()
            self.data_fetch_config = config.get_data_fetch_config()
        except Exception as e:
            self.logger.error(f"設定読み込みエラー: {e}")
            raise
        
        # 認証情報の安全な取得
        self._load_credentials()
        
        # セッション設定
        self.session = requests.Session()
        self.session.timeout = self.data_fetch_config.get("timeout", 30)
        
        # 認証状態
        self.refresh_token = None
        self.id_token = None
        self.token_expires_at = None
        
        self.logger.info("✅ 統合J-Quantsシステム初期化完了")
    
    def _load_credentials(self) -> None:
        """認証情報の安全な読み込み"""
        try:
            self.email = os.getenv("JQUANTS_EMAIL")
            self.password = os.getenv("JQUANTS_PASSWORD")
            
            # 認証情報の検証（機密情報はログに出力しない）
            if not self.email or not self.password:
                error_msg = "認証情報が設定されていません"
                masked_context = {
                    "email_set": bool(self.email),
                    "password_set": bool(self.password),
                    "env_file_exists": os.path.exists(".env"),
                }
                self._log_error(
                    ValueError(error_msg),
                    "認証情報検証エラー",
                    masked_context,
                )
                self.logger.error("❌ 環境変数 JQUANTS_EMAIL と JQUANTS_PASSWORD を設定してください。")
                self.logger.error("💡 .env ファイルを作成し、認証情報を設定してください。")
                raise ValueError(error_msg)
                
            self.logger.info("✅ 認証情報の読み込み完了")
            
        except Exception as e:
            self._log_error(e, "認証情報読み込みエラー")
            raise
    
    def _sanitize_message(self, message: str) -> str:
        """機密情報をマスキング"""
        sensitive_patterns = [
            r'password["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
            r'token["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
            r'key["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
            r'secret["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
            r'auth["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
            r'email["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
        ]

        sanitized = message
        for pattern in sensitive_patterns:
            sanitized = re.sub(
                pattern, r"\1***MASKED***", sanitized, flags=re.IGNORECASE
            )
        return sanitized
    
    def _mask_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """機密データのマスキング"""
        masked_data = data.copy()
        
        for key, value in masked_data.items():
            if any(sensitive_key in key.lower() for sensitive_key in self.sensitive_keys):
                if isinstance(value, str) and len(value) > 4:
                    masked_data[key] = value[:2] + "*" * (len(value) - 4) + value[-2:]
                else:
                    masked_data[key] = "***"
        
        return masked_data
    
    def _log_error(
        self,
        error: Exception,
        context: str = "",
        additional_info: Dict[str, Any] = None,
        include_traceback: bool = True,
    ):
        """セキュアなエラーログ出力"""
        self.error_count += 1
        
        # 機密情報をマスキング
        sanitized_context = self._sanitize_message(context)
        sanitized_error_msg = self._sanitize_message(str(error))
        
        # 追加情報のマスキング
        masked_info = None
        if additional_info:
            masked_info = self._mask_sensitive_data(additional_info)
        
        # エラーログの出力
        self.logger.error(f"❌ エラー #{self.error_count}: {sanitized_context}")
        self.logger.error(f"エラー詳細: {sanitized_error_msg}")
        
        if masked_info:
            self.logger.error(f"追加情報: {masked_info}")
        
        if include_traceback:
            traceback_str = self._sanitize_message(
                "".join(traceback.format_exception(type(error), error, error.__traceback__))
            )
            self.logger.error(f"トレースバック: {traceback_str}")
    
    def _handle_api_error(
        self,
        error: Exception,
        api_name: str,
        url: str,
        status_code: int = None,
    ):
        """APIエラーの処理"""
        error_context = f"{api_name} API エラー"
        if status_code:
            error_context += f" (HTTP {status_code})"
        
        additional_info = {
            "api_name": api_name,
            "url": url,
            "status_code": status_code,
        }
        
        self._log_error(error, error_context, additional_info)
    
    def _handle_file_error(
        self,
        error: Exception,
        file_path: str,
        operation: str,
    ):
        """ファイルエラーの処理"""
        error_context = f"ファイル{operation}エラー"
        additional_info = {
            "file_path": file_path,
            "operation": operation,
        }
        
        self._log_error(error, error_context, additional_info)
    
    def get_refresh_token(self) -> str:
        """リフレッシュトークンの取得"""
        self.logger.info("🔑 リフレッシュトークンを取得中...")

        try:
            auth_url = "https://api.jquants.com/v1/token/auth_user"
            auth_payload = {"mailaddress": self.email, "password": self.password}

            response = self.session.post(auth_url, json=auth_payload, timeout=30)
            response.raise_for_status()

            auth_data = response.json()

            if "refreshToken" not in auth_data:
                error_msg = "リフレッシュトークンの取得に失敗しました"
                self._handle_api_error(
                    ValueError(error_msg),
                    "J-Quants API",
                    auth_url,
                    response.status_code,
                )
                raise ValueError(error_msg)

            self.refresh_token = auth_data["refreshToken"]
            self.logger.info("✅ リフレッシュトークンを取得しました")
            return self.refresh_token

        except requests.exceptions.RequestException as e:
            self._handle_api_error(e, "J-Quants API", auth_url)
            raise
        except Exception as e:
            self._log_error(e, "リフレッシュトークン取得エラー")
            raise

    def get_id_token(self) -> str:
        """IDトークンの取得"""
        self.logger.info("🎫 IDトークンを取得中...")

        try:
            if not self.refresh_token:
                self.get_refresh_token()

            id_token_url = "https://api.jquants.com/v1/token/auth_refresh"
            id_token_params = {"refreshtoken": self.refresh_token}

            response = self.session.post(
                id_token_url, params=id_token_params, timeout=30
            )
            response.raise_for_status()

            id_token_data = response.json()

            if "idToken" not in id_token_data:
                error_msg = "IDトークンの取得に失敗しました"
                self._handle_api_error(
                    ValueError(error_msg),
                    "J-Quants API",
                    id_token_url,
                    response.status_code,
                )
                raise ValueError(error_msg)

            self.id_token = id_token_data["idToken"]
            # トークンの有効期限を設定（通常24時間）
            self.token_expires_at = datetime.now() + timedelta(hours=23)
            self.logger.info("✅ IDトークンを取得しました")
            return self.id_token

        except requests.exceptions.RequestException as e:
            self._handle_api_error(e, "J-Quants API", id_token_url)
            raise
        except Exception as e:
            self._log_error(e, "IDトークン取得エラー")
            raise

    def ensure_valid_token(self) -> str:
        """有効なトークンの確保"""
        if (
            self.id_token is None
            or self.token_expires_at is None
            or datetime.now() >= self.token_expires_at
        ):
            self.logger.info("🔄 トークンの更新が必要です")
            self.get_id_token()

        return self.id_token

    def get_auth_headers(self) -> Dict[str, str]:
        """認証ヘッダーの取得"""
        token = self.ensure_valid_token()
        return {"Authorization": f"Bearer {token}"}

    def _make_request_with_retry(
        self, method: str, url: str, **kwargs
    ) -> requests.Response:
        """リトライ機能付きHTTPリクエスト"""
        max_retries = self.data_fetch_config.get("max_retries", 3)
        retry_interval = self.data_fetch_config.get("retry_interval", 5)

        for attempt in range(max_retries + 1):
            try:
                self.logger.info(f"APIリクエスト (試行 {attempt + 1}/{max_retries + 1}): {method} {url}")
                response = self.session.request(method, url, **kwargs)

                if response.status_code == 200:
                    self.logger.info(f"✅ APIリクエスト成功: {response.status_code}")
                    return response
                else:
                    # HTTPエラーの詳細ログ
                    self._handle_api_error(
                        requests.exceptions.HTTPError(
                            f"HTTP {response.status_code}: {response.text}"
                        ),
                        "J-Quants API",
                        url,
                        response.status_code,
                    )
                    self.logger.warning(f"⚠️ APIリクエスト失敗: {response.status_code}")

            except requests.exceptions.Timeout as e:
                if attempt < max_retries:
                    self.logger.warning(f"⏰ タイムアウト (試行 {attempt + 1}/{max_retries + 1})")
                    self.logger.info(f"⏳ {retry_interval}秒後にリトライします...")
                    time.sleep(retry_interval)
                    continue
                else:
                    self._handle_api_error(e, "J-Quants API", url)
                    raise

            except requests.exceptions.ConnectionError as e:
                if attempt < max_retries:
                    self.logger.warning(f"🔌 接続エラー (試行 {attempt + 1}/{max_retries + 1})")
                    self.logger.info(f"⏳ {retry_interval}秒後にリトライします...")
                    time.sleep(retry_interval)
                    continue
                else:
                    self._handle_api_error(e, "J-Quants API", url)
                    raise

            except requests.exceptions.RequestException as e:
                self._handle_api_error(e, "J-Quants API", url)
                if attempt < max_retries:
                    self.logger.info(f"⏳ {retry_interval}秒後にリトライします...")
                    time.sleep(retry_interval)
                    continue
                else:
                    raise

        # 全てのリトライが失敗した場合
        final_error = Exception(f"APIリクエストが{max_retries + 1}回失敗しました")
        self._log_error(
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
        self.logger.info("🔍 データ検証を実行中...")

        # 基本的な構造チェック
        if not isinstance(data, dict):
            self.logger.error("❌ データが辞書形式ではありません")
            return False

        if "daily_quotes" not in data:
            self.logger.error("❌ daily_quotesキーが見つかりません")
            return False

        quotes = data["daily_quotes"]
        if not isinstance(quotes, list):
            self.logger.error("❌ daily_quotesがリスト形式ではありません")
            return False

        if len(quotes) == 0:
            self.logger.warning("⚠️ 取得データが空です")
            return False

        # 必須フィールドのチェック
        required_fields = ["Code", "Date", "Open", "High", "Low", "Close", "Volume"]
        sample_quote = quotes[0]
        missing_fields = [
            field for field in required_fields if field not in sample_quote
        ]

        if missing_fields:
            self.logger.error(f"❌ 必須フィールドが不足: {missing_fields}")
            return False

        # データ型の検証
        for i, quote in enumerate(quotes[:5]):  # 最初の5件をサンプルチェック
            try:
                float(quote.get("Close", 0))
                float(quote.get("Volume", 0))
                pd.to_datetime(quote.get("Date"))
            except (ValueError, TypeError) as e:
                self.logger.error(f"❌ データ型エラー (行{i}): {e}")
                return False

        self.logger.info(f"✅ データ検証完了: {len(quotes)}件のデータを確認")
        return True

    def fetch_stock_data(self, target_date: str) -> pd.DataFrame:
        """株価データの取得"""
        self.logger.info(f"📊 株価データ取得を開始: {target_date}")

        try:
            # 認証ヘッダーの取得
            headers = self.get_auth_headers()

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
            self.logger.info(f"✅ データ取得完了: {len(df)}件")

            return df

        except Exception as e:
            self._log_error(e, "株価データ取得エラー")
            raise

    def save_data(self, df: pd.DataFrame, output_file: str) -> None:
        """データの保存"""
        self.logger.info(f"💾 データを保存中: {output_file}")

        try:
            # データフレームの基本検証
            if df is None or df.empty:
                raise ValueError("保存するデータが空です")

            # 出力ディレクトリの確認・作成
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                self.logger.info(f"📁 出力ディレクトリを作成: {output_dir}")

            df.to_csv(output_file, index=False)
            self.logger.info(f"✅ データ保存完了: {output_file} ({len(df)}件)")

        except Exception as e:
            self._handle_file_error(e, output_file, "write")
            raise

    def get_system_status(self) -> Dict[str, Any]:
        """システム状態の取得"""
        return {
            "system_name": "統合J-Quantsシステム",
            "version": "1.0.0",
            "error_count": self.error_count,
            "has_valid_token": self.id_token is not None and (
                self.token_expires_at is None or datetime.now() < self.token_expires_at
            ),
            "token_expires_at": self.token_expires_at.isoformat() if self.token_expires_at else None,
            "config_loaded": bool(self.jquants_config and self.data_fetch_config),
        }


def main():
    """メイン処理"""
    # ログ設定
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # 統合システムの初期化
        system = UnifiedJQuantsSystem()
        
        # システム状態の表示
        status = system.get_system_status()
        print(f"🚀 システム状態: {status}")
        
        # サンプルデータ取得（今日の日付）
        from datetime import datetime
        today = datetime.now().strftime("%Y%m%d")
        
        print(f"📊 株価データ取得テスト: {today}")
        df = system.fetch_stock_data(today)
        
        # データ保存
        output_file = f"stock_data_{today}.csv"
        system.save_data(df, output_file)
        
        print(f"✅ 処理完了: {output_file}")
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
