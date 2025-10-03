#!/usr/bin/env python3
"""
サンプルキャッシュデータ生成スクリプト
オフライン運用用のサンプルJSONデータを生成
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List
import logging

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/generate_sample_cache.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class SampleCacheDataGenerator:
    """サンプルキャッシュデータ生成クラス"""

    def __init__(self):
        self.data_dir = Path("docs/data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # ログディレクトリの作成
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

    def generate_sample_daily_quotes(self) -> List[Dict[str, Any]]:
        """サンプル日足データの生成"""
        logger.info("サンプル日足データの生成を開始")
        
        # 主要銘柄のサンプルデータ
        stocks = [
            {"code": "7203", "name": "トヨタ自動車", "sector": "自動車"},
            {"code": "6758", "name": "ソニーグループ", "sector": "電気機器"},
            {"code": "9984", "name": "ソフトバンクグループ", "sector": "情報・通信"},
            {"code": "6861", "name": "キーエンス", "sector": "電気機器"},
            {"code": "4063", "name": "信越化学工業", "sector": "化学"},
            {"code": "8306", "name": "三菱UFJフィナンシャル・グループ", "sector": "銀行"},
            {"code": "9432", "name": "日本電信電話", "sector": "情報・通信"},
            {"code": "8035", "name": "東京エレクトロン", "sector": "電気機器"},
            {"code": "7741", "name": "HOYA", "sector": "精密機器"},
            {"code": "4519", "name": "中外製薬", "sector": "医薬品"}
        ]
        
        daily_quotes = []
        base_date = datetime.now() - timedelta(days=1)
        
        for stock in stocks:
            # ランダムな価格変動を生成
            import random
            base_price = random.randint(1000, 50000)
            change = random.randint(-500, 500)
            change_percent = (change / base_price) * 100
            volume = random.randint(100000, 2000000)
            
            quote = {
                "code": stock["code"],
                "name": stock["name"],
                "sector": stock["sector"],
                "date": base_date.strftime("%Y-%m-%d"),
                "open": base_price + random.randint(-100, 100),
                "high": base_price + random.randint(0, 200),
                "low": base_price - random.randint(0, 200),
                "close": base_price,
                "volume": volume,
                "turnover_value": base_price * volume,
                "adjustment_factor": 1.0,
                "adjustment_open": base_price + random.randint(-100, 100),
                "adjustment_high": base_price + random.randint(0, 200),
                "adjustment_low": base_price - random.randint(0, 200),
                "adjustment_close": base_price,
                "adjustment_volume": volume,
                "adjustment_turnover_value": base_price * volume,
                "change_percent": round(change_percent, 2),
                "timestamp": base_date.isoformat()
            }
            
            daily_quotes.append(quote)
        
        logger.info(f"サンプル日足データ生成完了: {len(daily_quotes)}銘柄")
        return daily_quotes

    def generate_sample_listed_data(self) -> List[Dict[str, Any]]:
        """サンプル上場銘柄データの生成"""
        logger.info("サンプル上場銘柄データの生成を開始")
        
        listed_data = [
            {
                "code": "7203",
                "name": "トヨタ自動車",
                "market": "東証プライム",
                "sector17_code": "15",
                "sector17_name": "自動車",
                "sector33_code": "1510",
                "sector33_name": "自動車",
                "scale_code": "10",
                "scale_name": "大型",
                "listing_date": "1949-05-16",
                "close_date": None
            },
            {
                "code": "6758",
                "name": "ソニーグループ",
                "market": "東証プライム",
                "sector17_code": "9",
                "sector17_name": "電気機器",
                "sector33_code": "9050",
                "sector33_name": "電気機器",
                "scale_code": "10",
                "scale_name": "大型",
                "listing_date": "1958-12-23",
                "close_date": None
            },
            {
                "code": "9984",
                "name": "ソフトバンクグループ",
                "market": "東証プライム",
                "sector17_code": "18",
                "sector17_name": "情報・通信",
                "sector33_code": "1850",
                "sector33_name": "情報・通信",
                "scale_code": "10",
                "scale_name": "大型",
                "listing_date": "1994-12-19",
                "close_date": None
            },
            {
                "code": "6861",
                "name": "キーエンス",
                "market": "東証プライム",
                "sector17_code": "9",
                "sector17_name": "電気機器",
                "sector33_code": "9050",
                "sector33_name": "電気機器",
                "scale_code": "10",
                "scale_name": "大型",
                "listing_date": "1989-12-21",
                "close_date": None
            },
            {
                "code": "4063",
                "name": "信越化学工業",
                "market": "東証プライム",
                "sector17_code": "3",
                "sector17_name": "化学",
                "sector33_code": "3050",
                "sector33_name": "化学",
                "scale_code": "10",
                "scale_name": "大型",
                "listing_date": "1949-05-16",
                "close_date": None
            }
        ]
        
        logger.info(f"サンプル上場銘柄データ生成完了: {len(listed_data)}銘柄")
        return listed_data

    def generate_sample_financial_data(self) -> List[Dict[str, Any]]:
        """サンプル財務データの生成"""
        logger.info("サンプル財務データの生成を開始")
        
        financial_data = [
            {
                "code": "7203",
                "name": "トヨタ自動車",
                "fiscal_year": "2024",
                "fiscal_period": "FY",
                "revenue": 37200000,
                "operating_income": 5000000,
                "ordinary_income": 4800000,
                "net_income": 3500000,
                "total_assets": 75000000,
                "total_equity": 25000000,
                "roe": 14.0,
                "roa": 4.7,
                "per": 12.5,
                "pbr": 1.2,
                "timestamp": datetime.now().isoformat()
            },
            {
                "code": "6758",
                "name": "ソニーグループ",
                "fiscal_year": "2024",
                "fiscal_period": "FY",
                "revenue": 12000000,
                "operating_income": 1200000,
                "ordinary_income": 1100000,
                "net_income": 800000,
                "total_assets": 25000000,
                "total_equity": 8000000,
                "roe": 10.0,
                "roa": 3.2,
                "per": 15.0,
                "pbr": 1.5,
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        logger.info(f"サンプル財務データ生成完了: {len(financial_data)}銘柄")
        return financial_data

    def generate_all_sample_data(self) -> Dict[str, Any]:
        """全サンプルデータの生成"""
        logger.info("全サンプルデータの生成を開始")
        
        return {
            "daily_quotes": self.generate_sample_daily_quotes(),
            "listed_data": self.generate_sample_listed_data(),
            "financial_data": self.generate_sample_financial_data(),
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "type": "sample_cache_data",
                "description": "オフライン運用用サンプルデータ",
                "cache_ttl": {
                    "daily_quotes": "24h",
                    "listed_data": "7d",
                    "financial_data": "7d"
                },
                "version": "1.0"
            }
        }

    def save_sample_data(self) -> None:
        """サンプルデータの保存"""
        logger.info("サンプルデータの保存を開始")
        
        # 全サンプルデータの生成
        all_data = self.generate_all_sample_data()
        
        # 個別ファイルとして保存
        sample_files = {
            "sample_daily_quotes.json": {
                "daily_quotes": all_data["daily_quotes"],
                "metadata": {
                    "generated_at": all_data["metadata"]["generated_at"],
                    "type": "daily_quotes",
                    "ttl": "24h",
                    "version": "1.0"
                }
            },
            "sample_listed_data.json": {
                "listed_data": all_data["listed_data"],
                "metadata": {
                    "generated_at": all_data["metadata"]["generated_at"],
                    "type": "listed_data",
                    "ttl": "7d",
                    "version": "1.0"
                }
            },
            "sample_financial_data.json": {
                "financial_data": all_data["financial_data"],
                "metadata": {
                    "generated_at": all_data["metadata"]["generated_at"],
                    "type": "financial_data",
                    "ttl": "7d",
                    "version": "1.0"
                }
            }
        }
        
        # 各ファイルを保存
        for filename, data in sample_files.items():
            file_path = self.data_dir / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"保存完了: {file_path}")
        
        # 統合ファイルも保存
        all_data_path = self.data_dir / "sample_all_data.json"
        with open(all_data_path, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        logger.info(f"統合ファイル保存完了: {all_data_path}")
        
        logger.info("サンプルデータの保存完了")


def main():
    """メイン実行関数"""
    try:
        generator = SampleCacheDataGenerator()
        generator.save_sample_data()
        logger.info("✅ サンプルキャッシュデータ生成完了")
    except Exception as e:
        logger.error(f"❌ サンプルキャッシュデータ生成エラー: {e}")
        raise


if __name__ == "__main__":
    main()
