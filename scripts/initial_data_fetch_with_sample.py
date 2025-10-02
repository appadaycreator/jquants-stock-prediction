#!/usr/bin/env python3
"""
初回データ取得スクリプト（サンプルデータ版）
認証情報がない場合でもサンプルデータで動作確認が可能
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
import random

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# ログ設定
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/initial_data_fetch.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class InitialDataFetcherWithSample:
    """初回データ取得クラス（サンプルデータ版）"""

    def __init__(self):
        self.data_dir = Path("docs/data")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # ログディレクトリの作成
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # サンプル銘柄データ
        self.sample_stocks = [
            {"Code": "7203", "CompanyName": "トヨタ自動車", "Sector17Code": "自動車"},
            {
                "Code": "6758",
                "CompanyName": "ソニーグループ",
                "Sector17Code": "エレクトロニクス",
            },
            {
                "Code": "9984",
                "CompanyName": "ソフトバンクグループ",
                "Sector17Code": "情報通信",
            },
            {
                "Code": "6861",
                "CompanyName": "キーエンス",
                "Sector17Code": "エレクトロニクス",
            },
            {"Code": "4063", "CompanyName": "信越化学工業", "Sector17Code": "化学"},
            {
                "Code": "8035",
                "CompanyName": "東京エレクトロン",
                "Sector17Code": "エレクトロニクス",
            },
            {
                "Code": "8306",
                "CompanyName": "三菱UFJフィナンシャル・グループ",
                "Sector17Code": "銀行",
            },
            {"Code": "9432", "CompanyName": "日本電信電話", "Sector17Code": "情報通信"},
            {"Code": "4503", "CompanyName": "アステラス製薬", "Sector17Code": "医薬品"},
            {"Code": "7741", "CompanyName": "HOYA", "Sector17Code": "エレクトロニクス"},
        ]

    def generate_sample_price_data(
        self, code: str, name: str, days: int = 30
    ) -> List[Dict[str, Any]]:
        """サンプル価格データの生成"""
        base_price = random.randint(1000, 50000)
        price_data = []

        for i in range(days):
            date = datetime.now() - timedelta(days=days - i - 1)

            # 価格の変動をシミュレート
            if i == 0:
                price = base_price
            else:
                change_rate = random.uniform(-0.05, 0.05)  # ±5%の変動
                price = price_data[-1]["Close"] * (1 + change_rate)

            volume = random.randint(100000, 2000000)

            price_data.append(
                {
                    "Date": date.strftime("%Y-%m-%d"),
                    "Code": code,
                    "Open": round(price * random.uniform(0.98, 1.02), 2),
                    "High": round(price * random.uniform(1.01, 1.05), 2),
                    "Low": round(price * random.uniform(0.95, 0.99), 2),
                    "Close": round(price, 2),
                    "Volume": volume,
                    "AdjustmentFactor": 1.0,
                    "AdjustmentOpen": round(price * random.uniform(0.98, 1.02), 2),
                    "AdjustmentHigh": round(price * random.uniform(1.01, 1.05), 2),
                    "AdjustmentLow": round(price * random.uniform(0.95, 0.99), 2),
                    "AdjustmentClose": round(price, 2),
                    "AdjustmentVolume": volume,
                }
            )

        return price_data

    def process_stock_data(self, max_stocks: int = 10) -> Dict[str, Any]:
        """株価データの処理（サンプル版）"""
        logger.info(f"サンプル株価データの処理開始 (最大{max_stocks}銘柄)")

        processed_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "version": "2.0",
                "data_source": "jquants_sample",
                "total_stocks": 0,
                "structure_version": "2.0",
                "update_type": "initial_sample",
            },
            "stocks": {},
        }

        # サンプル銘柄の選択
        selected_stocks = self.sample_stocks[:max_stocks]

        for i, stock in enumerate(selected_stocks):
            code = stock.get("Code", "")
            name = stock.get("CompanyName", "")
            sector = stock.get("Sector17Code", "")

            logger.info(f"処理中: {i+1}/{len(selected_stocks)} - {name} ({code})")

            # サンプル価格データの生成
            price_data = self.generate_sample_price_data(code, name, days=30)

            if not price_data:
                logger.warning(f"銘柄 {code} の価格データが生成できませんでした")
                continue

            # 最新データの取得
            latest_data = price_data[-1] if price_data else {}

            # 技術指標の計算
            prices = [
                float(quote.get("Close", 0))
                for quote in price_data
                if quote.get("Close")
            ]
            volumes = [
                int(quote.get("Volume", 0))
                for quote in price_data
                if quote.get("Volume")
            ]

            # 移動平均の計算
            sma_5 = (
                sum(prices[-5:]) / 5
                if len(prices) >= 5
                else prices[-1] if prices else 0
            )
            sma_25 = (
                sum(prices[-25:]) / 25
                if len(prices) >= 25
                else prices[-1] if prices else 0
            )
            sma_75 = sum(prices[-75:]) / 75 if len(prices) >= 75 else sma_25

            # 変動率の計算
            if len(prices) >= 2:
                change_percent = ((prices[-1] - prices[-2]) / prices[-2]) * 100
            else:
                change_percent = 0

            # RSIの簡易計算
            if len(prices) >= 14:
                gains = []
                losses = []
                for j in range(1, min(14, len(prices))):
                    change = prices[j] - prices[j - 1]
                    if change > 0:
                        gains.append(change)
                    else:
                        losses.append(abs(change))

                avg_gain = sum(gains) / len(gains) if gains else 0
                avg_loss = sum(losses) / len(losses) if losses else 0

                if avg_loss == 0:
                    rsi = 100
                else:
                    rs = avg_gain / avg_loss
                    rsi = 100 - (100 / (1 + rs))
            else:
                rsi = 50

            # 構造化データの作成
            processed_data["stocks"][code] = {
                "code": code,
                "name": name,
                "sector": sector,
                "current_price": {
                    "last_price": float(latest_data.get("Close", 0)),
                    "change": float(latest_data.get("Close", 0))
                    - float(latest_data.get("Open", 0)),
                    "change_percent": round(change_percent, 2),
                    "updated_at": latest_data.get("Date", datetime.now().isoformat()),
                },
                "volume": {
                    "current_volume": int(latest_data.get("Volume", 0)),
                    "average_volume": (
                        round(sum(volumes) / len(volumes), 0) if volumes else 0
                    ),
                    "volume_ratio": round(random.uniform(0.8, 1.5), 2),
                },
                "technical_indicators": {
                    "sma_5": round(sma_5, 2),
                    "sma_25": round(sma_25, 2),
                    "sma_75": round(sma_75, 2),
                    "rsi": round(rsi, 2),
                    "macd": round(random.uniform(-10, 10), 2),
                    "bollinger_upper": round(sma_25 * 1.02, 2),
                    "bollinger_lower": round(sma_25 * 0.98, 2),
                },
                "prediction": {
                    "predicted_price": round(
                        float(latest_data.get("Close", 0)) * random.uniform(0.95, 1.05),
                        2,
                    ),
                    "confidence": round(random.uniform(0.6, 0.9), 2),
                    "model_used": "SampleModel",
                    "prediction_date": datetime.now().isoformat(),
                },
                "risk_metrics": {
                    "volatility": round(random.uniform(0.1, 0.4), 3),
                    "beta": round(random.uniform(0.8, 1.3), 2),
                    "sharpe_ratio": round(random.uniform(0.3, 2.0), 2),
                    "max_drawdown": round(random.uniform(-0.3, -0.05), 3),
                },
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "data_quality": "sample",
                    "last_trade_date": latest_data.get(
                        "Date", datetime.now().isoformat()
                    ),
                },
            }

        processed_data["metadata"]["total_stocks"] = len(processed_data["stocks"])
        logger.info(
            f"サンプル株価データの処理完了: {len(processed_data['stocks'])}銘柄"
        )

        return processed_data

    def save_structured_data(self, data: Dict[str, Any]):
        """構造化データの保存"""
        try:
            # メインファイルの保存
            main_file = self.data_dir / "stock_data.json"
            with open(main_file, "w", encoding="utf-8") as f:
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
                        "version": "2.0",
                    },
                    "stock": stock_info,
                }

                with open(individual_file, "w", encoding="utf-8") as f:
                    json.dump(individual_data, f, ensure_ascii=False, indent=2)

            logger.info(f"個別銘柄ファイル保存完了: {len(data['stocks'])}ファイル")

            # インデックスファイルの生成
            index_data = {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "version": "2.0",
                    "total_stocks": len(data["stocks"]),
                    "last_updated": data["metadata"]["generated_at"],
                },
                "stocks": [],
            }

            for code, stock_info in data["stocks"].items():
                index_data["stocks"].append(
                    {
                        "code": code,
                        "name": stock_info["name"],
                        "sector": stock_info["sector"],
                        "last_price": stock_info["current_price"]["last_price"],
                        "change_percent": stock_info["current_price"]["change_percent"],
                        "updated_at": stock_info["current_price"]["updated_at"],
                        "file_path": f"stocks/{code}.json",
                    }
                )

            # 価格順でソート
            index_data["stocks"].sort(key=lambda x: x["last_price"], reverse=True)

            index_file = self.data_dir / "index.json"
            with open(index_file, "w", encoding="utf-8") as f:
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
            }

            metadata_file = metadata_dir / "basic.json"
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(basic_metadata, f, ensure_ascii=False, indent=2)

            logger.info(f"メタデータファイル保存完了: {metadata_file}")

        except Exception as e:
            logger.error(f"データ保存エラー: {e}")
            raise

    def run_initial_fetch(self):
        """初回データ取得の実行（サンプル版）"""
        try:
            logger.info("=== サンプルデータ生成開始 ===")

            # 株価データの処理
            processed_data = self.process_stock_data(max_stocks=10)
            if not processed_data["stocks"]:
                logger.error("サンプル株価データの処理に失敗しました")
                return False

            # データの保存
            self.save_structured_data(processed_data)

            logger.info("=== サンプルデータ生成完了 ===")
            return True

        except Exception as e:
            logger.error(f"サンプルデータ生成エラー: {e}")
            return False


def main():
    """メイン処理"""
    fetcher = InitialDataFetcherWithSample()
    success = fetcher.run_initial_fetch()

    if success:
        logger.info("サンプルデータ生成が正常に完了しました")
        sys.exit(0)
    else:
        logger.error("サンプルデータ生成に失敗しました")
        sys.exit(1)


if __name__ == "__main__":
    main()
