#!/usr/bin/env python3
"""
構造化されたJSONデータ生成スクリプト
jQuantsデータを効率的に管理するための構造化されたJSONファイルを生成
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StructuredDataGenerator:
    """構造化されたデータ生成クラス"""

    def __init__(self):
        self.data_dir = Path("docs/data")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # サブディレクトリの作成
        self.stocks_dir = self.data_dir / "stocks"
        self.stocks_dir.mkdir(exist_ok=True)

        self.metadata_dir = self.data_dir / "metadata"
        self.metadata_dir.mkdir(exist_ok=True)

    def generate_stock_data_structure(
        self, stock_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """株価データの構造化"""
        structured_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "version": "2.0",
                "data_source": "jquants",
                "total_stocks": len(stock_data),
                "structure_version": "2.0",
                "update_type": "full",
            },
            "stocks": {},
        }

        for code, stock_info in stock_data.items():
            structured_data["stocks"][code] = {
                "code": code,
                "name": stock_info.get("name", ""),
                "sector": stock_info.get("sector", ""),
                "current_price": {
                    "last_price": stock_info.get("last_price", 0),
                    "change": stock_info.get("change", 0),
                    "change_percent": stock_info.get("change_percent", 0),
                    "updated_at": stock_info.get(
                        "updated_at", datetime.now().isoformat()
                    ),
                },
                "volume": {
                    "current_volume": stock_info.get("volume", 0),
                    "average_volume": stock_info.get("average_volume", 0),
                    "volume_ratio": stock_info.get("volume_ratio", 1.0),
                },
                "technical_indicators": {
                    "sma_5": stock_info.get("sma_5", 0),
                    "sma_25": stock_info.get("sma_25", 0),
                    "sma_75": stock_info.get("sma_75", 0),
                    "rsi": stock_info.get("rsi", 50),
                    "macd": stock_info.get("macd", 0),
                    "bollinger_upper": stock_info.get("bollinger_upper", 0),
                    "bollinger_lower": stock_info.get("bollinger_lower", 0),
                },
                "prediction": {
                    "predicted_price": stock_info.get("predicted_price", 0),
                    "confidence": stock_info.get("confidence", 0),
                    "model_used": stock_info.get("model_used", ""),
                    "prediction_date": stock_info.get(
                        "prediction_date", datetime.now().isoformat()
                    ),
                },
                "risk_metrics": {
                    "volatility": stock_info.get("volatility", 0),
                    "beta": stock_info.get("beta", 1.0),
                    "sharpe_ratio": stock_info.get("sharpe_ratio", 0),
                    "max_drawdown": stock_info.get("max_drawdown", 0),
                },
                "metadata": {
                    "created_at": stock_info.get(
                        "created_at", datetime.now().isoformat()
                    ),
                    "updated_at": stock_info.get(
                        "updated_at", datetime.now().isoformat()
                    ),
                    "data_quality": stock_info.get("data_quality", "good"),
                    "last_trade_date": stock_info.get(
                        "last_trade_date", datetime.now().isoformat()
                    ),
                },
            }

        return structured_data

    def generate_individual_stock_files(self, structured_data: Dict[str, Any]):
        """個別銘柄ファイルの生成"""
        stocks = structured_data.get("stocks", {})

        for code, stock_info in stocks.items():
            individual_file = self.stocks_dir / f"{code}.json"

            individual_data = {
                "metadata": {
                    "code": code,
                    "generated_at": datetime.now().isoformat(),
                    "version": "2.0",
                },
                "stock": stock_info,
            }

            with open(individual_file, "w", encoding="utf-8") as f:
                json.dump(individual_data, f, ensure_ascii=False, indent=2)

            logger.info(f"個別ファイル生成: {code}.json")

    def generate_index_file(self, structured_data: Dict[str, Any]):
        """インデックスファイルの生成"""
        index_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "version": "2.0",
                "total_stocks": len(structured_data.get("stocks", {})),
                "last_updated": structured_data.get("metadata", {}).get(
                    "generated_at", ""
                ),
            },
            "stocks": [],
        }

        for code, stock_info in structured_data.get("stocks", {}).items():
            index_data["stocks"].append(
                {
                    "code": code,
                    "name": stock_info.get("name", ""),
                    "sector": stock_info.get("sector", ""),
                    "last_price": stock_info.get("current_price", {}).get(
                        "last_price", 0
                    ),
                    "change_percent": stock_info.get("current_price", {}).get(
                        "change_percent", 0
                    ),
                    "updated_at": stock_info.get("current_price", {}).get(
                        "updated_at", ""
                    ),
                    "file_path": f"stocks/{code}.json",
                }
            )

        # 価格順でソート
        index_data["stocks"].sort(key=lambda x: x["last_price"], reverse=True)

        index_file = self.data_dir / "index.json"
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)

        logger.info("インデックスファイル生成: index.json")

    def generate_metadata_files(self, structured_data: Dict[str, Any]):
        """メタデータファイルの生成"""
        metadata = structured_data.get("metadata", {})

        # 基本メタデータ
        basic_metadata = {
            "last_updated": metadata.get("generated_at", ""),
            "total_stocks": metadata.get("total_stocks", 0),
            "data_source": metadata.get("data_source", ""),
            "version": metadata.get("version", ""),
            "file_size": self._calculate_total_size(),
            "update_status": "success",
        }

        metadata_file = self.metadata_dir / "basic.json"
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(basic_metadata, f, ensure_ascii=False, indent=2)

        # 統計メタデータ
        stats = self._calculate_statistics(structured_data)
        stats_file = self.metadata_dir / "statistics.json"
        with open(stats_file, "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)

        logger.info("メタデータファイル生成完了")

    def _calculate_total_size(self) -> int:
        """総ファイルサイズの計算"""
        total_size = 0
        for file_path in self.data_dir.rglob("*.json"):
            total_size += file_path.stat().st_size
        return total_size

    def _calculate_statistics(self, structured_data: Dict[str, Any]) -> Dict[str, Any]:
        """統計データの計算"""
        stocks = structured_data.get("stocks", {})

        if not stocks:
            return {"error": "データがありません"}

        prices = []
        changes = []
        volumes = []
        sectors = {}

        for stock_info in stocks.values():
            current_price = stock_info.get("current_price", {})
            volume_info = stock_info.get("volume", {})

            price = current_price.get("last_price", 0)
            change = current_price.get("change_percent", 0)
            volume = volume_info.get("current_volume", 0)
            sector = stock_info.get("sector", "Unknown")

            if price > 0:
                prices.append(price)
            if change != 0:
                changes.append(change)
            if volume > 0:
                volumes.append(volume)

            sectors[sector] = sectors.get(sector, 0) + 1

        return {
            "price_statistics": {
                "min_price": min(prices) if prices else 0,
                "max_price": max(prices) if prices else 0,
                "avg_price": sum(prices) / len(prices) if prices else 0,
                "median_price": sorted(prices)[len(prices) // 2] if prices else 0,
            },
            "change_statistics": {
                "positive_changes": len([c for c in changes if c > 0]),
                "negative_changes": len([c for c in changes if c < 0]),
                "avg_change": sum(changes) / len(changes) if changes else 0,
                "max_gain": max(changes) if changes else 0,
                "max_loss": min(changes) if changes else 0,
            },
            "volume_statistics": {
                "total_volume": sum(volumes) if volumes else 0,
                "avg_volume": sum(volumes) / len(volumes) if volumes else 0,
                "max_volume": max(volumes) if volumes else 0,
            },
            "sector_distribution": sectors,
            "total_stocks": len(stocks),
        }

    def generate_all_files(self, stock_data: Dict[str, Any]):
        """全ファイルの生成"""
        logger.info("構造化データ生成開始")

        # 構造化データの生成
        structured_data = self.generate_stock_data_structure(stock_data)

        # メインファイルの保存
        main_file = self.data_dir / "stock_data.json"
        with open(main_file, "w", encoding="utf-8") as f:
            json.dump(structured_data, f, ensure_ascii=False, indent=2)

        # 個別ファイルの生成
        self.generate_individual_stock_files(structured_data)

        # インデックスファイルの生成
        self.generate_index_file(structured_data)

        # メタデータファイルの生成
        self.generate_metadata_files(structured_data)

        logger.info("構造化データ生成完了")


def main():
    """メイン処理"""
    # サンプルデータ（実際の実装ではjQuantsから取得）
    sample_data = {
        "7203": {
            "name": "トヨタ自動車",
            "sector": "自動車",
            "last_price": 2500,
            "change": 50,
            "change_percent": 2.04,
            "volume": 1000000,
            "sma_5": 2480,
            "sma_25": 2450,
            "rsi": 65,
            "predicted_price": 2550,
            "confidence": 0.85,
        },
        "6758": {
            "name": "ソニーグループ",
            "sector": "エレクトロニクス",
            "last_price": 12000,
            "change": -200,
            "change_percent": -1.64,
            "volume": 500000,
            "sma_5": 12100,
            "sma_25": 12200,
            "rsi": 45,
            "predicted_price": 11800,
            "confidence": 0.78,
        },
    }

    generator = StructuredDataGenerator()
    generator.generate_all_files(sample_data)


if __name__ == "__main__":
    main()
