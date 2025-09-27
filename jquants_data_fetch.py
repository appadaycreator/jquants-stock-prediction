import requests
import pandas as pd
import os
import time
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from dotenv import load_dotenv
from config_loader import get_config

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('jquants.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class JQuantsAPIClient:
    """J-Quants API接続の堅牢なクライアント"""
    
    def __init__(self):
        self.email = os.getenv("JQUANTS_EMAIL")
        self.password = os.getenv("JQUANTS_PASSWORD")
        self.refresh_token = None
        self.id_token = None
        self.token_expires_at = None
        self.session = requests.Session()
        
        # 設定を読み込み
        config = get_config()
        self.jquants_config = config.get_jquants_config()
        self.data_fetch_config = config.get_data_fetch_config()
        
        # セッション設定
        self.session.timeout = self.data_fetch_config.get('timeout', 30)
        
        # 認証情報の検証
        if not self.email or not self.password:
            logger.error("❌ 環境変数 JQUANTS_EMAIL と JQUANTS_PASSWORD を設定してください。")
            logger.error("💡 .env ファイルを作成し、認証情報を設定してください。")
            raise ValueError("認証情報が設定されていません")
        
        logger.info("✅ J-Quants API クライアントを初期化しました")

    def _make_request_with_retry(self, method: str, url: str, **kwargs) -> requests.Response:
        """リトライ機能付きHTTPリクエスト"""
        max_retries = self.data_fetch_config.get('max_retries', 3)
        retry_interval = self.data_fetch_config.get('retry_interval', 5)
        
        for attempt in range(max_retries + 1):
            try:
                logger.info(f"🔄 APIリクエスト実行 (試行 {attempt + 1}/{max_retries + 1}): {method} {url}")
                response = self.session.request(method, url, **kwargs)
                
                if response.status_code == 200:
                    logger.info(f"✅ APIリクエスト成功: {response.status_code}")
                    return response
                else:
                    logger.warning(f"⚠️ APIリクエスト失敗: {response.status_code} - {response.text}")
                    
            except requests.exceptions.Timeout:
                logger.warning(f"⏰ タイムアウト (試行 {attempt + 1}/{max_retries + 1})")
            except requests.exceptions.ConnectionError:
                logger.warning(f"🔌 接続エラー (試行 {attempt + 1}/{max_retries + 1})")
            except Exception as e:
                logger.warning(f"❌ 予期しないエラー (試行 {attempt + 1}/{max_retries + 1}): {e}")
            
            if attempt < max_retries:
                logger.info(f"⏳ {retry_interval}秒後にリトライします...")
                time.sleep(retry_interval)
        
        raise Exception(f"APIリクエストが{max_retries + 1}回失敗しました")
    
    def _get_refresh_token(self) -> str:
        """リフレッシュトークンの取得"""
        logger.info("🔑 リフレッシュトークンを取得中...")
        
        auth_url = "https://api.jquants.com/v1/token/auth_user"
        auth_payload = {"mailaddress": self.email, "password": self.password}
        
        response = self._make_request_with_retry("POST", auth_url, json=auth_payload)
        auth_data = response.json()
        
        if "refreshToken" not in auth_data:
            logger.error(f"❌ リフレッシュトークンが取得できませんでした: {auth_data}")
            raise ValueError("リフレッシュトークンの取得に失敗しました")
        
        self.refresh_token = auth_data["refreshToken"]
        logger.info("✅ リフレッシュトークンを取得しました")
        return self.refresh_token
    
    def _get_id_token(self) -> str:
        """IDトークンの取得"""
        logger.info("🎫 IDトークンを取得中...")
        
        if not self.refresh_token:
            self._get_refresh_token()
        
        id_token_url = "https://api.jquants.com/v1/token/auth_refresh"
        id_token_params = {"refreshtoken": self.refresh_token}
        
        response = self._make_request_with_retry("POST", id_token_url, params=id_token_params)
        id_token_data = response.json()
        
        if "idToken" not in id_token_data:
            logger.error(f"❌ IDトークンが取得できませんでした: {id_token_data}")
            raise ValueError("IDトークンの取得に失敗しました")
        
        self.id_token = id_token_data["idToken"]
        
        # トークンの有効期限を設定（通常24時間）
        self.token_expires_at = datetime.now() + timedelta(hours=23)
        logger.info("✅ IDトークンを取得しました")
        return self.id_token
    
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
        logger.info(f"✅ 株価データ取得完了: {len(df)}件")
        
        return df
    
    def save_data(self, df: pd.DataFrame, output_file: str) -> None:
        """データの保存"""
        logger.info(f"💾 データを保存中: {output_file}")
        
        try:
            df.to_csv(output_file, index=False)
            logger.info(f"✅ データ保存完了: {output_file} ({len(df)}件)")
        except Exception as e:
            logger.error(f"❌ データ保存エラー: {e}")
            raise

def main():
    """メイン処理"""
    try:
        # クライアントの初期化
        client = JQuantsAPIClient()
        
        # 設定の取得
        target_date = client.data_fetch_config.get('target_date', '20240301')
        output_file = client.data_fetch_config.get('output_file', 'stock_data.csv')
        
        # データ取得
        df = client.fetch_stock_data(target_date)
        
        # データ保存
        client.save_data(df, output_file)
        
        logger.info("🎉 データ取得処理が正常に完了しました")
        
    except Exception as e:
        logger.error(f"❌ データ取得処理でエラーが発生: {e}")
        raise

if __name__ == "__main__":
    main()
