#!/usr/bin/env python3
"""
jQuants API利用可能エンドポイント調査スクリプト
実際にアクセス可能なエンドポイントを調査
"""

import requests
import json
import os
from datetime import datetime
import logging

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/endpoint_investigation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class JQuantsEndpointInvestigator:
    """jQuants APIエンドポイント調査クラス"""
    
    def __init__(self):
        self.id_token = os.getenv("JQUANTS_ID_TOKEN")
        if not self.id_token:
            raise ValueError("JQUANTS_ID_TOKEN が設定されていません")
        
        self.headers = {
            "Authorization": f"Bearer {self.id_token}",
            "Content-Type": "application/json",
            "User-Agent": "jQuants-Stock-Prediction/1.0"
        }
    
    def test_endpoint(self, name, url, params=None):
        """エンドポイントのテスト"""
        logger.info(f"テスト中: {name}")
        logger.info(f"URL: {url}")
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            result = {
                "name": name,
                "url": url,
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "response_size": len(response.content),
                "headers": dict(response.headers)
            }
            
            if response.status_code == 200:
                logger.info(f"✅ 成功: HTTP {response.status_code}")
                try:
                    data = response.json()
                    if isinstance(data, dict):
                        result["data_keys"] = list(data.keys())
                        result["data_sample"] = str(data)[:500] + "..." if len(str(data)) > 500 else str(data)
                    logger.info(f"📊 データキー: {result['data_keys']}")
                except json.JSONDecodeError:
                    logger.warning(f"⚠️ JSON解析エラー: {response.text[:100]}...")
                    result["json_error"] = True
            else:
                logger.error(f"❌ エラー: HTTP {response.status_code}")
                logger.error(f"📄 レスポンス: {response.text[:200]}...")
                result["error_message"] = response.text[:200]
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"🚫 リクエストエラー: {e}")
            return {
                "name": name,
                "url": url,
                "status_code": "ERROR",
                "success": False,
                "error": str(e)
            }
    
    def investigate_all_endpoints(self):
        """全エンドポイントの調査"""
        logger.info("=== jQuants APIエンドポイント調査開始 ===")
        
        # 調査するエンドポイント
        endpoints = [
            # 基本情報系
            {
                "name": "上場銘柄一覧",
                "url": "https://api.jquants.com/v1/listed/info",
                "params": None
            },
            {
                "name": "上場銘柄一覧（特定銘柄）",
                "url": "https://api.jquants.com/v1/listed/info",
                "params": {"code": "7203"}
            },
            
            # 株価データ系
            {
                "name": "株価四本値",
                "url": "https://api.jquants.com/v1/prices/daily_quotes",
                "params": {"code": "7203", "from": "2025-09-01", "to": "2025-10-01"}
            },
            {
                "name": "前場四本値",
                "url": "https://api.jquants.com/v1/prices/prices_am",
                "params": {"code": "7203", "date": "2025-10-01"}
            },
            
            # 市場データ系
            {
                "name": "投資部門別情報",
                "url": "https://api.jquants.com/v1/markets/trades_spec",
                "params": {"from": "2025-09-01", "to": "2025-10-01"}
            },
            {
                "name": "信用取引週末残高",
                "url": "https://api.jquants.com/v1/markets/weekly_margin_interest",
                "params": {"from": "2025-09-01", "to": "2025-10-01"}
            },
            {
                "name": "業種別空売り比率",
                "url": "https://api.jquants.com/v1/markets/short_selling",
                "params": {"from": "2025-09-01", "to": "2025-10-01"}
            },
            {
                "name": "空売り残高報告",
                "url": "https://api.jquants.com/v1/markets/short_selling_positions",
                "params": {"from": "2025-09-01", "to": "2025-10-01"}
            },
            {
                "name": "日々公表信用取引残高",
                "url": "https://api.jquants.com/v1/markets/daily_margin_interest",
                "params": {"from": "2025-09-01", "to": "2025-10-01"}
            },
            {
                "name": "売買内訳データ",
                "url": "https://api.jquants.com/v1/markets/breakdown",
                "params": {"from": "2025-09-01", "to": "2025-10-01"}
            },
            {
                "name": "取引カレンダー",
                "url": "https://api.jquants.com/v1/markets/trading_calendar",
                "params": {"from": "2025-09-01", "to": "2025-10-01"}
            },
            
            # 指数データ系
            {
                "name": "指数四本値",
                "url": "https://api.jquants.com/v1/indices",
                "params": {"from": "2025-09-01", "to": "2025-10-01"}
            },
            {
                "name": "TOPIX指数四本値",
                "url": "https://api.jquants.com/v1/indices/topix",
                "params": {"from": "2025-09-01", "to": "2025-10-01"}
            },
            
            # 財務情報系
            {
                "name": "財務情報",
                "url": "https://api.jquants.com/v1/fins/statements",
                "params": {"code": "7203"}
            },
            {
                "name": "財務諸表(BS/PL)",
                "url": "https://api.jquants.com/v1/fins/fs_details",
                "params": {"code": "7203"}
            },
            {
                "name": "配当金情報",
                "url": "https://api.jquants.com/v1/fins/dividend",
                "params": {"code": "7203"}
            },
            {
                "name": "決算発表予定日",
                "url": "https://api.jquants.com/v1/fins/announcement",
                "params": {"from": "2025-09-01", "to": "2025-10-01"}
            },
            
            # デリバティブ系
            {
                "name": "日経225オプション四本値",
                "url": "https://api.jquants.com/v1/option/index_option",
                "params": {"from": "2025-09-01", "to": "2025-10-01"}
            },
            {
                "name": "先物四本値",
                "url": "https://api.jquants.com/v1/derivatives/futures",
                "params": {"from": "2025-09-01", "to": "2025-10-01"}
            },
            {
                "name": "オプション四本値",
                "url": "https://api.jquants.com/v1/derivatives/options",
                "params": {"from": "2025-09-01", "to": "2025-10-01"}
            }
        ]
        
        results = []
        
        for endpoint in endpoints:
            result = self.test_endpoint(
                endpoint["name"], 
                endpoint["url"], 
                endpoint["params"]
            )
            results.append(result)
            logger.info("")  # 空行
        
        # 結果サマリー
        logger.info("=== 調査結果サマリー ===")
        successful_tests = [r for r in results if r.get('success', False)]
        failed_tests = [r for r in results if not r.get('success', False)]
        
        logger.info(f"✅ 成功: {len(successful_tests)}/{len(results)}")
        logger.info(f"❌ 失敗: {len(failed_tests)}/{len(results)}")
        
        if successful_tests:
            logger.info("\n✅ 成功したエンドポイント:")
            for result in successful_tests:
                logger.info(f"  - {result['name']}: HTTP {result['status_code']}")
        
        if failed_tests:
            logger.info("\n❌ 失敗したエンドポイント:")
            for result in failed_tests:
                logger.info(f"  - {result['name']}: {result.get('status_code', 'ERROR')}")
        
        # 詳細結果をJSONファイルに保存
        output_file = "jquants_endpoints_investigation.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "investigation_time": datetime.now().isoformat(),
                "total_endpoints": len(results),
                "successful_endpoints": len(successful_tests),
                "failed_endpoints": len(failed_tests),
                "results": results
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"\n💾 詳細結果を保存: {output_file}")
        
        return results

def main():
    """メイン処理"""
    try:
        investigator = JQuantsEndpointInvestigator()
        results = investigator.investigate_all_endpoints()
        
        successful_count = len([r for r in results if r.get('success', False)])
        logger.info(f"\n🎉 調査完了: {successful_count}個のエンドポイントが利用可能です")
        
        return 0
        
    except Exception as e:
        logger.error(f"調査エラー: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
