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
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/fetch_listed_info.log'),
        logging.StreamHandler()
    ]
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
        """上場銘柄一覧を取得"""
        url = "https://api.jquants.com/v1/listed/info"
        
        headers = {
            "Authorization": f"Bearer {self.id_token}",
            "Content-Type": "application/json",
            "User-Agent": "jQuants-Stock-Prediction/1.0"
        }
        
        params = {}
        if date:
            params["date"] = date
        if code:
            params["code"] = code
        
        logger.info(f"上場銘柄一覧取得開始: {url}")
        logger.info(f"パラメータ: {params}")
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"取得成功: {len(data.get('info', []))}銘柄")
                return data
            else:
                logger.error(f"取得エラー: HTTP {response.status_code}")
                logger.error(f"レスポンス: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"リクエストエラー: {e}")
            return None
    
    def process_listed_data(self, data):
        """上場銘柄データの処理"""
        if not data or 'info' not in data:
            logger.error("データが空または無効です")
            return None
        
        info_list = data['info']
        logger.info(f"処理開始: {len(info_list)}銘柄")
        
        # データの構造化
        processed_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "version": "2.0",
                "data_source": "jquants_listed_info",
                "total_stocks": len(info_list),
                "structure_version": "2.0",
                "update_type": "listed_info"
            },
            "stocks": {}
        }
        
        # 主要銘柄の選択（時価総額上位など）
        major_stocks = []
        for stock in info_list:
            code = stock.get('Code', '')
            name = stock.get('CompanyName', '')
            sector = stock.get('Sector17CodeName', '')
            market = stock.get('MarketCodeName', '')
            
            # 主要市場の銘柄を選択
            if market in ['プライム', 'スタンダード', 'グロース']:
                major_stocks.append({
                    'code': code,
                    'name': name,
                    'sector': sector,
                    'market': market,
                    'raw_data': stock
                })
        
        # 全銘柄を選択（制限を解除）
        selected_stocks = major_stocks
        logger.info(f"全銘柄選択: {len(selected_stocks)}銘柄")
        
        # 構造化データの作成
        for stock in selected_stocks:
            code = stock['code']
            processed_data["stocks"][code] = {
                "code": code,
                "name": stock['name'],
                "sector": stock['sector'],
                "market": stock['market'],
                "listed_info": stock['raw_data'],
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "data_quality": "jquants_official",
                    "source": "listed_info_api"
                }
            }
        
        processed_data["metadata"]["total_stocks"] = len(processed_data["stocks"])
        logger.info(f"処理完了: {len(processed_data['stocks'])}銘柄")
        
        return processed_data
    
    def save_structured_data(self, data):
        """構造化データの保存"""
        try:
            # メインファイルの保存
            main_file = self.data_dir / "listed_info.json"
            with open(main_file, 'w', encoding='utf-8') as f:
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
                        "type": "listed_info"
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
                    "last_updated": data["metadata"]["generated_at"],
                    "data_type": "listed_info"
                },
                "stocks": []
            }
            
            for code, stock_info in data["stocks"].items():
                index_data["stocks"].append({
                    "code": code,
                    "name": stock_info["name"],
                    "sector": stock_info["sector"],
                    "market": stock_info["market"],
                    "updated_at": stock_info["metadata"]["updated_at"],
                    "file_path": f"stocks/{code}_listed.json"
                })
            
            # セクター順でソート
            index_data["stocks"].sort(key=lambda x: (x["sector"], x["name"]))
            
            index_file = self.data_dir / "listed_index.json"
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
                "update_status": "success",
                "data_type": "listed_info"
            }
            
            metadata_file = metadata_dir / "listed_info.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
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
