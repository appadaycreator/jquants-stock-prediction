import requests
import pandas as pd
import os
import time
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from dotenv import load_dotenv
from config_loader import get_config
from error_handler import get_error_handler, get_specific_error_handler

# 強化されたログ設定
from enhanced_logging import setup_enhanced_logging, LogLevel, LogCategory

enhanced_logger = setup_enhanced_logging("JQuantsDataFetch", LogLevel.INFO)
logger = enhanced_logger.get_logger()

class JQuantsAPIClient:
    """J-Quants API接続の堅牢なクライアント"""
    
    def __init__(self):
        self.email = os.getenv("JQUANTS_EMAIL")
        self.password = os.getenv("JQUANTS_PASSWORD")
        self.refresh_token = None
        self.id_token = None
        self.token_expires_at = None
        self.session = requests.Session()
        
        # エラーハンドラーの初期化
        self.error_handler = get_error_handler("JQuantsAPIClient")
        self.specific_error_handler = get_specific_error_handler("JQuantsAPIClient")
        
        try:
            # 設定を読み込み
            config = get_config()
            self.jquants_config = config.get_jquants_config()
            self.data_fetch_config = config.get_data_fetch_config()
            
            # セッション設定
            self.session.timeout = self.data_fetch_config.get('timeout', 30)
            
            # 認証情報の検証
            if not self.email or not self.password:
                error_msg = "認証情報が設定されていません"
                self.error_handler.log_error(
                    ValueError(error_msg), 
                    "認証情報検証エラー",
                    {
                        'email_set': bool(self.email),
                        'password_set': bool(self.password),
                        'env_file_exists': os.path.exists('.env')
                    }
                )
                logger.error("❌ 環境変数 JQUANTS_EMAIL と JQUANTS_PASSWORD を設定してください。")
                logger.error("💡 .env ファイルを作成し、認証情報を設定してください。")
                raise ValueError(error_msg)
            
            enhanced_logger.log_operation_end("JQuantsAPIClient初期化", success=True)
            
        except Exception as e:
            self.error_handler.log_error(e, "JQuantsAPIClient初期化エラー")
            raise

    def _make_request_with_retry(self, method: str, url: str, **kwargs) -> requests.Response:
        """リトライ機能付きHTTPリクエスト"""
        max_retries = self.data_fetch_config.get('max_retries', 3)
        retry_interval = self.data_fetch_config.get('retry_interval', 5)
        
        for attempt in range(max_retries + 1):
            try:
                enhanced_logger.log_operation_start(f"APIリクエスト (試行 {attempt + 1}/{max_retries + 1})", 
                                                   method=method, url=url)
                response = self.session.request(method, url, **kwargs)
                
                if response.status_code == 200:
                    enhanced_logger.log_operation_end("APIリクエスト", success=True, 
                                                    status_code=response.status_code)
                    return response
                else:
                    # HTTPエラーの詳細ログ
                    self.error_handler.handle_api_error(
                        requests.exceptions.HTTPError(f"HTTP {response.status_code}: {response.text}"),
                        "J-Quants API",
                        url,
                        response.status_code,
                        response.text[:500]  # レスポンスの最初の500文字
                    )
                    logger.warning(f"⚠️ APIリクエスト失敗: {response.status_code} - {response.text}")
                    
            except requests.exceptions.Timeout as e:
                if self.specific_error_handler.handle_connection_error(e, attempt, max_retries):
                    logger.warning(f"⏰ タイムアウト (試行 {attempt + 1}/{max_retries + 1})")
                    if attempt < max_retries:
                        logger.info(f"⏳ {retry_interval}秒後にリトライします...")
                        time.sleep(retry_interval)
                        continue
                else:
                    raise
                    
            except requests.exceptions.ConnectionError as e:
                if self.specific_error_handler.handle_connection_error(e, attempt, max_retries):
                    logger.warning(f"🔌 接続エラー (試行 {attempt + 1}/{max_retries + 1})")
                    if attempt < max_retries:
                        logger.info(f"⏳ {retry_interval}秒後にリトライします...")
                        time.sleep(retry_interval)
                        continue
                else:
                    raise
                    
            except requests.exceptions.RequestException as e:
                self.error_handler.handle_api_error(e, "J-Quants API", url)
                logger.error(f"❌ リクエストエラー (試行 {attempt + 1}/{max_retries + 1}): {e}")
                if attempt < max_retries:
                    logger.info(f"⏳ {retry_interval}秒後にリトライします...")
                    time.sleep(retry_interval)
                    continue
                else:
                    raise
                    
            except Exception as e:
                self.error_handler.log_error(
                    e, 
                    f"予期しないAPIエラー (試行 {attempt + 1}/{max_retries + 1})",
                    {
                        'method': method,
                        'url': url,
                        'attempt': attempt + 1,
                        'max_retries': max_retries,
                        'kwargs_keys': list(kwargs.keys()) if kwargs else []
                    }
                )
                logger.error(f"❌ 予期しないエラー (試行 {attempt + 1}/{max_retries + 1}): {e}")
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
                'method': method,
                'url': url,
                'max_retries': max_retries,
                'retry_interval': retry_interval
            }
        )
        raise final_error
    
    def _get_refresh_token(self) -> str:
        """リフレッシュトークンの取得"""
        logger.info("🔑 リフレッシュトークンを取得中...")
        
        try:
            auth_url = "https://api.jquants.com/v1/token/auth_user"
            auth_payload = {"mailaddress": self.email, "password": self.password}
            
            response = self._make_request_with_retry("POST", auth_url, json=auth_payload)
            auth_data = response.json()
            
            if "refreshToken" not in auth_data:
                error_msg = "リフレッシュトークンの取得に失敗しました"
                self.error_handler.handle_api_error(
                    ValueError(error_msg),
                    "J-Quants API",
                    auth_url,
                    response.status_code,
                    auth_data
                )
                logger.error(f"❌ リフレッシュトークンが取得できませんでした: {auth_data}")
                raise ValueError(error_msg)
            
            self.refresh_token = auth_data["refreshToken"]
            logger.info("✅ リフレッシュトークンを取得しました")
            return self.refresh_token
            
        except Exception as e:
            self.error_handler.log_error(
                e,
                "リフレッシュトークン取得エラー",
                {
                    'auth_url': auth_url,
                    'email_provided': bool(self.email),
                    'password_provided': bool(self.password)
                }
            )
            raise
    
    def _get_id_token(self) -> str:
        """IDトークンの取得"""
        logger.info("🎫 IDトークンを取得中...")
        
        try:
            if not self.refresh_token:
                self._get_refresh_token()
            
            id_token_url = "https://api.jquants.com/v1/token/auth_refresh"
            id_token_params = {"refreshtoken": self.refresh_token}
            
            response = self._make_request_with_retry("POST", id_token_url, params=id_token_params)
            id_token_data = response.json()
            
            if "idToken" not in id_token_data:
                error_msg = "IDトークンの取得に失敗しました"
                self.error_handler.handle_api_error(
                    ValueError(error_msg),
                    "J-Quants API",
                    id_token_url,
                    response.status_code,
                    id_token_data
                )
                logger.error(f"❌ IDトークンが取得できませんでした: {id_token_data}")
                raise ValueError(error_msg)
            
            self.id_token = id_token_data["idToken"]
            
            # トークンの有効期限を設定（通常24時間）
            self.token_expires_at = datetime.now() + timedelta(hours=23)
            logger.info("✅ IDトークンを取得しました")
            return self.id_token
            
        except Exception as e:
            self.error_handler.log_error(
                e,
                "IDトークン取得エラー",
                {
                    'id_token_url': id_token_url,
                    'refresh_token_available': bool(self.refresh_token)
                }
            )
            raise
    
    def _ensure_valid_token(self) -> str:
        """有効なトークンの確保"""
        if (self.id_token is None or 
            self.token_expires_at is None or 
            datetime.now() >= self.token_expires_at):
            logger.info("🔄 トークンの更新が必要です")
            self._get_id_token()
        
        return self.id_token
    
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
        missing_fields = [field for field in required_fields if field not in sample_quote]
        
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
        
        # 有効なトークンを確保
        id_token = self._ensure_valid_token()
        
        # 株価データの取得
        headers = {"Authorization": f"Bearer {id_token}"}
        price_url = f"{self.jquants_config.get('base_url', 'https://api.jquants.com/v1')}/prices/daily_quotes"
        params = {"date": target_date}
        
        response = self._make_request_with_retry("GET", price_url, headers=headers, params=params)
        data = response.json()
        
        # データ検証
        if not self._validate_stock_data(data):
            raise ValueError("取得データの検証に失敗しました")
        
        # DataFrameに変換
        df = pd.DataFrame(data["daily_quotes"])
        enhanced_logger.log_data_info("株価データ", shape=df.shape, records=len(df))
        
        return df
    
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
            
        except PermissionError as e:
            self.error_handler.handle_file_error(e, output_file, "write")
            logger.error(f"❌ ファイル書き込み権限エラー: {e}")
            logger.error("💡 出力ファイルの書き込み権限を確認してください")
            raise
            
        except OSError as e:
            self.error_handler.handle_file_error(e, output_file, "write")
            logger.error(f"❌ ファイルシステムエラー: {e}")
            raise
            
        except Exception as e:
            self.error_handler.log_error(
                e,
                "データ保存エラー",
                {
                    'output_file': output_file,
                    'data_shape': df.shape if df is not None else None,
                    'data_empty': df.empty if df is not None else None,
                    'output_dir_exists': os.path.exists(os.path.dirname(output_file)) if output_file else None
                }
            )
            logger.error(f"❌ データ保存エラー: {e}")
            raise

def main():
    """メイン処理"""
    error_handler = get_error_handler("main")
    
    try:
        # クライアントの初期化
        client = JQuantsAPIClient()
        
        # 設定の取得
        target_date = client.data_fetch_config.get('target_date', '20240301')
        output_file = client.data_fetch_config.get('output_file', 'stock_data.csv')
        
        logger.info(f"📅 対象日: {target_date}")
        logger.info(f"📁 出力ファイル: {output_file}")
        
        # データ取得
        df = client.fetch_stock_data(target_date)
        
        # データ保存
        client.save_data(df, output_file)
        
        enhanced_logger.log_operation_end("データ取得処理", success=True, 
                                         target_date=target_date, output_file=output_file)
        
    except ValueError as e:
        error_handler.log_error(e, "データ取得処理 - 値エラー")
        logger.error(f"❌ データ値エラー: {e}")
        logger.error("💡 入力データの形式や設定を確認してください")
        raise
        
    except FileNotFoundError as e:
        error_handler.log_error(e, "データ取得処理 - ファイルエラー")
        logger.error(f"❌ ファイルが見つかりません: {e}")
        logger.error("💡 設定ファイルや出力ディレクトリのパスを確認してください")
        raise
        
    except PermissionError as e:
        error_handler.log_error(e, "データ取得処理 - 権限エラー")
        logger.error(f"❌ ファイルアクセス権限エラー: {e}")
        logger.error("💡 ファイルの読み書き権限を確認してください")
        raise
        
    except ConnectionError as e:
        error_handler.log_error(e, "データ取得処理 - 接続エラー")
        logger.error(f"❌ ネットワーク接続エラー: {e}")
        logger.error("💡 インターネット接続とAPIエンドポイントを確認してください")
        raise
        
    except Exception as e:
        error_handler.log_error(
            e, 
            "データ取得処理 - 予期しないエラー",
            {
                'target_date': target_date if 'target_date' in locals() else None,
                'output_file': output_file if 'output_file' in locals() else None,
                'client_initialized': 'client' in locals()
            }
        )
        logger.error(f"❌ データ取得処理で予期しないエラーが発生: {e}")
        logger.error("💡 ログファイルを確認して詳細なエラー情報を確認してください")
        raise

if __name__ == "__main__":
    main()
