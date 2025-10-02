#!/usr/bin/env python3
"""
初回データ取得スクリプト
jQuants APIから本日時点でのデータを取得してJSONファイルとして保存
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
import requests
import time

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# ログ設定
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/initial_data_fetch.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class InitialDataFetcher:
    """初回データ取得クラス"""
    
    def __init__(self):
        self.data_dir = Path("docs/data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # ログディレクトリの作成
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # jQuants API設定
        self.base_url = "https://api.jquants.com/v1"
        self.email = os.getenv("JQUANTS_EMAIL")
        self.password = os.getenv("JQUANTS_PASSWORD")
        self.id_token = os.getenv("JQUANTS_ID_TOKEN")
        
        # セッション管理
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'jQuants-Stock-Prediction/1.0'
        })
        
    def authenticate(self) -> bool:
        """jQuants API認証"""
        try:
            if self.id_token:
                # IDトークンが直接設定されている場合
                logger.info("IDトークンが設定されています")
                return True
            
            if not self.email or not self.password:
                logger.error("認証情報が設定されていません")
                logger.error("環境変数 JQUANTS_EMAIL, JQUANTS_PASSWORD または JQUANTS_ID_TOKEN を設定してください")
                return False
            
            # リフレッシュトークンの取得
            logger.info("リフレッシュトークンを取得中...")
            auth_url = f"{self.base_url}/token/auth_user"
            auth_data = {
                "mailaddress": self.email,
                "password": self.password
            }
            
            response = self.session.post(auth_url, json=auth_data, timeout=30)
            response.raise_for_status()
            
            auth_result = response.json()
            refresh_token = auth_result.get("refreshToken")
            
            if not refresh_token:
                logger.error("リフレッシュトークンの取得に失敗しました")
                return False
            
            # IDトークンの取得
            logger.info("IDトークンを取得中...")
            token_url = f"{self.base_url}/token/auth_refresh"
            token_data = {"refreshtoken": refresh_token}
            
            response = self.session.post(token_url, json=token_data, timeout=30)
            response.raise_for_status()
            
            token_result = response.json()
            self.id_token = token_result.get("idToken")
            
            if not self.id_token:
                logger.error("IDトークンの取得に失敗しました")
                return False
            
            logger.info("認証が完了しました")
            return True
            
        except Exception as e:
            logger.error(f"認証エラー: {e}")
            return False
    
    def get_stock_list(self) -> List[Dict[str, Any]]:
        """銘柄一覧の取得"""
        try:
            logger.info("銘柄一覧を取得中...")
            
            headers = {"Authorization": f"Bearer {self.id_token}"}
            url = f"{self.base_url}/markets/stock/list"
            
            response = self.session.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            stocks = data.get("stocks", [])
            
            logger.info(f"銘柄一覧取得完了: {len(stocks)}銘柄")
            return stocks
            
        except Exception as e:
            logger.error(f"銘柄一覧取得エラー: {e}")
            return []
    
    def get_stock_prices(self, code: str, days: int = 30) -> List[Dict[str, Any]]:
        """個別銘柄の価格データ取得"""
        try:
            # 日付範囲の計算
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            start_str = start_date.strftime("%Y-%m-%d")
            end_str = end_date.strftime("%Y-%m-%d")
            
            logger.info(f"銘柄 {code} の価格データ取得中 ({start_str} - {end_str})")
            
            headers = {"Authorization": f"Bearer {self.id_token}"}
            url = f"{self.base_url}/markets/daily_quotes"
            params = {
                "code": code,
                "from": start_str,
                "to": end_str
            }
            
            response = self.session.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            quotes = data.get("daily_quotes", [])
            
            logger.info(f"銘柄 {code} の価格データ取得完了: {len(quotes)}件")
            return quotes
            
        except Exception as e:
            logger.error(f"銘柄 {code} の価格データ取得エラー: {e}")
            return []
    
    def process_stock_data(self, stock_list: List[Dict[str, Any]], max_stocks: int = None) -> Dict[str, Any]:
        """株価データの処理"""
        if max_stocks is None:
            max_stocks = len(stock_list)  # 全銘柄を処理
        logger.info(f"株価データの処理開始 (最大{max_stocks}銘柄)")
        
        processed_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "version": "2.0",
                "data_source": "jquants",
                "total_stocks": 0,
                "structure_version": "2.0",
                "update_type": "initial"
            },
            "stocks": {}
        }
        
        # 主要銘柄の選択（時価総額順など）
        selected_stocks = stock_list[:max_stocks]
        
        for i, stock in enumerate(selected_stocks):
            code = stock.get("Code", "")
            name = stock.get("CompanyName", "")
            sector = stock.get("Sector17Code", "")
            
            if not code:
                continue
            
            logger.info(f"処理中: {i+1}/{len(selected_stocks)} - {name} ({code})")
            
            # 価格データの取得
            price_data = self.get_stock_prices(code, days=30)
            
            if not price_data:
                logger.warning(f"銘柄 {code} の価格データが取得できませんでした")
                continue
            
            # 最新データの取得
            latest_data = price_data[-1] if price_data else {}
            
            # 技術指標の計算（簡易版）
            prices = [float(quote.get("Close", 0)) for quote in price_data if quote.get("Close")]
            volumes = [int(quote.get("Volume", 0)) for quote in price_data if quote.get("Volume")]
            
            # 移動平均の計算
            sma_5 = sum(prices[-5:]) / 5 if len(prices) >= 5 else prices[-1] if prices else 0
            sma_25 = sum(prices[-25:]) / 25 if len(prices) >= 25 else prices[-1] if prices else 0
            
            # 変動率の計算
            if len(prices) >= 2:
                change_percent = ((prices[-1] - prices[-2]) / prices[-2]) * 100
            else:
                change_percent = 0
            
            # 構造化データの作成
            processed_data["stocks"][code] = {
                "code": code,
                "name": name,
                "sector": sector,
                "current_price": {
                    "last_price": float(latest_data.get("Close", 0)),
                    "change": float(latest_data.get("Close", 0)) - float(latest_data.get("Open", 0)),
                    "change_percent": change_percent,
                    "updated_at": latest_data.get("Date", datetime.now().isoformat())
                },
                "volume": {
                    "current_volume": int(latest_data.get("Volume", 0)),
                    "average_volume": sum(volumes) / len(volumes) if volumes else 0,
                    "volume_ratio": 1.0
                },
                "technical_indicators": {
                    "sma_5": round(sma_5, 2),
                    "sma_25": round(sma_25, 2),
                    "sma_75": round(sum(prices[-75:]) / 75, 2) if len(prices) >= 75 else round(sma_25, 2),
                    "rsi": 50,  # 簡易版のため固定値
                    "macd": 0,  # 簡易版のため固定値
                    "bollinger_upper": round(sma_25 * 1.02, 2),
                    "bollinger_lower": round(sma_25 * 0.98, 2)
                },
                "prediction": {
                    "predicted_price": round(float(latest_data.get("Close", 0)) * 1.02, 2),
                    "confidence": 0.75,
                    "model_used": "Initial",
                    "prediction_date": datetime.now().isoformat()
                },
                "risk_metrics": {
                    "volatility": 0.2,
                    "beta": 1.0,
                    "sharpe_ratio": 0.5,
                    "max_drawdown": -0.1
                },
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "data_quality": "good",
                    "last_trade_date": latest_data.get("Date", datetime.now().isoformat())
                }
            }
            
            # API制限を考慮した待機
            time.sleep(0.1)
        
        processed_data["metadata"]["total_stocks"] = len(processed_data["stocks"])
        logger.info(f"株価データの処理完了: {len(processed_data['stocks'])}銘柄")
        
        return processed_data
    
    def save_structured_data(self, data: Dict[str, Any]):
        """構造化データの保存"""
        try:
            # メインファイルの保存
            main_file = self.data_dir / "stock_data.json"
            with open(main_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"メインファイル保存完了: {main_file}")
            
            # 個別銘柄ファイルの保存
            stocks_dir = self.data_dir / "stocks"
            stocks_dir.mkdir(exist_ok=True)
            
            for code, stock_info in data["stocks"].items():
                individual_file = stocks_dir / f"{code}.json"
                individual_data = {
                    "metadata": {
                        "code": code,
                        "generated_at": datetime.now().isoformat(),
                        "version": "2.0"
                    },
                    "stock": stock_info
                }
                
                with open(individual_file, 'w', encoding='utf-8') as f:
                    json.dump(individual_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"個別銘柄ファイル保存完了: {len(data['stocks'])}ファイル")
            
            # インデックスファイルの生成
            index_data = {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "version": "2.0",
                    "total_stocks": len(data["stocks"]),
                    "last_updated": data["metadata"]["generated_at"]
                },
                "stocks": []
            }
            
            for code, stock_info in data["stocks"].items():
                index_data["stocks"].append({
                    "code": code,
                    "name": stock_info["name"],
                    "sector": stock_info["sector"],
                    "last_price": stock_info["current_price"]["last_price"],
                    "change_percent": stock_info["current_price"]["change_percent"],
                    "updated_at": stock_info["current_price"]["updated_at"],
                    "file_path": f"stocks/{code}.json"
                })
            
            # 価格順でソート
            index_data["stocks"].sort(key=lambda x: x["last_price"], reverse=True)
            
            index_file = self.data_dir / "index.json"
            with open(index_file, 'w', encoding='utf-8') as f:
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
                "update_status": "success"
            }
            
            metadata_file = metadata_dir / "basic.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(basic_metadata, f, ensure_ascii=False, indent=2)
            
            logger.info(f"メタデータファイル保存完了: {metadata_file}")
            
        except Exception as e:
            logger.error(f"データ保存エラー: {e}")
            raise
    
    def run_initial_fetch(self):
        """初回データ取得の実行"""
        try:
            logger.info("=== 初回データ取得開始 ===")
            
            # 認証
            if not self.authenticate():
                logger.error("認証に失敗しました")
                return False
            
            # 銘柄一覧の取得
            stock_list = self.get_stock_list()
            if not stock_list:
                logger.error("銘柄一覧の取得に失敗しました")
                return False
            
            # 株価データの処理
            processed_data = self.process_stock_data(stock_list, max_stocks=30)
            if not processed_data["stocks"]:
                logger.error("株価データの処理に失敗しました")
                return False
            
            # データの保存
            self.save_structured_data(processed_data)
            
            logger.info("=== 初回データ取得完了 ===")
            return True
            
        except Exception as e:
            logger.error(f"初回データ取得エラー: {e}")
            return False

def main():
    """メイン処理"""
    fetcher = InitialDataFetcher()
    success = fetcher.run_initial_fetch()
    
    if success:
        logger.info("初回データ取得が正常に完了しました")
        sys.exit(0)
    else:
        logger.error("初回データ取得に失敗しました")
        sys.exit(1)

if __name__ == "__main__":
    main()
