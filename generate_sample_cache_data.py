#!/usr/bin/env python3
"""
サンプルキャッシュデータ生成スクリプト
GitHub Actions用のサンプルデータ生成
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
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# ログ設定
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/generate_sample_cache_data.log"),
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

    def generate_sample_stocks(self) -> Dict[str, Any]:
        """サンプル株価データの生成"""
        try:
            logger.info("サンプル株価データを生成中...")

            # 主要銘柄のサンプルデータ
            sample_stocks = {
                "7203": {
                    "code": "7203",
                    "name": "トヨタ自動車",
                    "sector": "自動車",
                    "current_price": {
                        "last_price": 2500.0 + random.uniform(-100, 100),
                        "change": random.uniform(-50, 50),
                        "change_percent": random.uniform(-2, 2),
                        "updated_at": datetime.now().isoformat(),
                    },
                    "volume": {
                        "current_volume": random.randint(500000, 2000000),
                        "average_volume": random.randint(400000, 1500000),
                        "volume_ratio": random.uniform(0.5, 2.0),
                    },
                    "technical_indicators": {
                        "sma_5": 2480.0 + random.uniform(-50, 50),
                        "sma_25": 2450.0 + random.uniform(-50, 50),
                        "rsi": random.uniform(30, 70),
                        "macd": random.uniform(-20, 20),
                    },
                    "prediction": {
                        "predicted_price": 2550.0 + random.uniform(-100, 100),
                        "confidence": random.uniform(0.7, 0.95),
                        "model_used": "Random Forest",
                        "prediction_date": datetime.now().isoformat(),
                    },
                },
                "6758": {
                    "code": "6758",
                    "name": "ソニーグループ",
                    "sector": "電気機器",
                    "current_price": {
                        "last_price": 12000.0 + random.uniform(-500, 500),
                        "change": random.uniform(-200, 200),
                        "change_percent": random.uniform(-2, 2),
                        "updated_at": datetime.now().isoformat(),
                    },
                    "volume": {
                        "current_volume": random.randint(200000, 800000),
                        "average_volume": random.randint(300000, 700000),
                        "volume_ratio": random.uniform(0.5, 2.0),
                    },
                    "technical_indicators": {
                        "sma_5": 12100.0 + random.uniform(-200, 200),
                        "sma_25": 12200.0 + random.uniform(-200, 200),
                        "rsi": random.uniform(30, 70),
                        "macd": random.uniform(-50, 50),
                    },
                    "prediction": {
                        "predicted_price": 11800.0 + random.uniform(-300, 300),
                        "confidence": random.uniform(0.7, 0.95),
                        "model_used": "XGBoost",
                        "prediction_date": datetime.now().isoformat(),
                    },
                },
                "9984": {
                    "code": "9984",
                    "name": "ソフトバンクグループ",
                    "sector": "情報・通信業",
                    "current_price": {
                        "last_price": 8000.0 + random.uniform(-200, 200),
                        "change": random.uniform(-100, 100),
                        "change_percent": random.uniform(-2, 2),
                        "updated_at": datetime.now().isoformat(),
                    },
                    "volume": {
                        "current_volume": random.randint(300000, 1000000),
                        "average_volume": random.randint(400000, 800000),
                        "volume_ratio": random.uniform(0.5, 2.0),
                    },
                    "technical_indicators": {
                        "sma_5": 8100.0 + random.uniform(-100, 100),
                        "sma_25": 8200.0 + random.uniform(-100, 100),
                        "rsi": random.uniform(30, 70),
                        "macd": random.uniform(-30, 30),
                    },
                    "prediction": {
                        "predicted_price": 8200.0 + random.uniform(-200, 200),
                        "confidence": random.uniform(0.7, 0.95),
                        "model_used": "Linear Regression",
                        "prediction_date": datetime.now().isoformat(),
                    },
                },
                "9432": {
                    "code": "9432",
                    "name": "日本電信電話",
                    "sector": "情報・通信業",
                    "current_price": {
                        "last_price": 4500.0 + random.uniform(-100, 100),
                        "change": random.uniform(-50, 50),
                        "change_percent": random.uniform(-2, 2),
                        "updated_at": datetime.now().isoformat(),
                    },
                    "volume": {
                        "current_volume": random.randint(200000, 600000),
                        "average_volume": random.randint(300000, 500000),
                        "volume_ratio": random.uniform(0.5, 2.0),
                    },
                    "technical_indicators": {
                        "sma_5": 4550.0 + random.uniform(-50, 50),
                        "sma_25": 4600.0 + random.uniform(-50, 50),
                        "rsi": random.uniform(30, 70),
                        "macd": random.uniform(-20, 20),
                    },
                    "prediction": {
                        "predicted_price": 4600.0 + random.uniform(-100, 100),
                        "confidence": random.uniform(0.7, 0.95),
                        "model_used": "Random Forest",
                        "prediction_date": datetime.now().isoformat(),
                    },
                },
                "8306": {
                    "code": "8306",
                    "name": "三菱UFJフィナンシャル・グループ",
                    "sector": "銀行業",
                    "current_price": {
                        "last_price": 1200.0 + random.uniform(-50, 50),
                        "change": random.uniform(-25, 25),
                        "change_percent": random.uniform(-2, 2),
                        "updated_at": datetime.now().isoformat(),
                    },
                    "volume": {
                        "current_volume": random.randint(1000000, 3000000),
                        "average_volume": random.randint(800000, 2000000),
                        "volume_ratio": random.uniform(0.5, 2.0),
                    },
                    "technical_indicators": {
                        "sma_5": 1210.0 + random.uniform(-25, 25),
                        "sma_25": 1220.0 + random.uniform(-25, 25),
                        "rsi": random.uniform(30, 70),
                        "macd": random.uniform(-10, 10),
                    },
                    "prediction": {
                        "predicted_price": 1220.0 + random.uniform(-50, 50),
                        "confidence": random.uniform(0.7, 0.95),
                        "model_used": "XGBoost",
                        "prediction_date": datetime.now().isoformat(),
                    },
                },
            }

            sample_data = {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "version": "1.0",
                    "data_source": "sample_cache",
                    "total_stocks": len(sample_stocks),
                },
                "stocks": sample_stocks,
            }

            logger.info(f"サンプル株価データ生成完了: {len(sample_stocks)}銘柄")
            return sample_data

        except Exception as e:
            logger.error(f"サンプル株価データ生成エラー: {e}")
            return {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "version": "1.0",
                    "data_source": "sample_cache",
                    "total_stocks": 0,
                },
                "stocks": {},
            }

    def generate_dashboard_summary(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """ダッシュボードサマリーの生成"""
        try:
            stocks = stock_data.get("stocks", {})
            if not stocks:
                return {
                    "metadata": {
                        "generated_at": datetime.now().isoformat(),
                        "version": "1.0",
                    },
                    "summary": {
                        "total_stocks": 0,
                        "market_status": "closed",
                        "last_updated": datetime.now().isoformat(),
                    },
                }

            # 市場統計の計算
            total_stocks = len(stocks)
            gainers = 0
            losers = 0
            unchanged = 0

            for stock_info in stocks.values():
                change_percent = stock_info.get("current_price", {}).get(
                    "change_percent", 0
                )
                if change_percent > 0:
                    gainers += 1
                elif change_percent < 0:
                    losers += 1
                else:
                    unchanged += 1

            # トップゲイナーとトップローザーの取得
            sorted_stocks = sorted(
                stocks.values(),
                key=lambda x: x.get("current_price", {}).get("change_percent", 0),
                reverse=True,
            )

            top_gainers = [
                {
                    "code": stock.get("code", ""),
                    "name": stock.get("name", ""),
                    "change_percent": stock.get("current_price", {}).get(
                        "change_percent", 0
                    ),
                    "last_price": stock.get("current_price", {}).get("last_price", 0),
                }
                for stock in sorted_stocks[:5]
            ]

            top_losers = [
                {
                    "code": stock.get("code", ""),
                    "name": stock.get("name", ""),
                    "change_percent": stock.get("current_price", {}).get(
                        "change_percent", 0
                    ),
                    "last_price": stock.get("current_price", {}).get("last_price", 0),
                }
                for stock in sorted_stocks[-5:]
            ]

            summary = {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "version": "1.0",
                    "data_source": "sample_cache",
                },
                "summary": {
                    "total_stocks": total_stocks,
                    "gainers": gainers,
                    "losers": losers,
                    "unchanged": unchanged,
                    "market_status": "open" if datetime.now().hour < 15 else "closed",
                    "last_updated": datetime.now().isoformat(),
                },
                "top_gainers": top_gainers,
                "top_losers": top_losers,
            }

            logger.info(f"ダッシュボードサマリー生成完了: {total_stocks}銘柄")
            return summary

        except Exception as e:
            logger.error(f"ダッシュボードサマリー生成エラー: {e}")
            return {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "version": "1.0",
                },
                "summary": {
                    "total_stocks": 0,
                    "market_status": "error",
                    "last_updated": datetime.now().isoformat(),
                },
            }

    def generate_today_summary(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """今日のサマリー生成"""
        try:
            stocks = stock_data.get("stocks", {})
            if not stocks:
                return {
                    "metadata": {
                        "generated_at": datetime.now().isoformat(),
                        "version": "1.0",
                    },
                    "today_summary": {
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "total_stocks": 0,
                        "market_status": "closed",
                    },
                }

            # 今日の市場状況
            total_stocks = len(stocks)
            gainers = sum(
                1
                for stock in stocks.values()
                if stock.get("current_price", {}).get("change_percent", 0) > 0
            )
            losers = sum(
                1
                for stock in stocks.values()
                if stock.get("current_price", {}).get("change_percent", 0) < 0
            )

            # 平均変動率
            changes = [
                stock.get("current_price", {}).get("change_percent", 0)
                for stock in stocks.values()
            ]
            avg_change = sum(changes) / len(changes) if changes else 0

            today_summary = {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "version": "1.0",
                },
                "today_summary": {
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "total_stocks": total_stocks,
                    "gainers": gainers,
                    "losers": losers,
                    "unchanged": total_stocks - gainers - losers,
                    "average_change": round(avg_change, 2),
                    "market_status": "open" if datetime.now().hour < 15 else "closed",
                    "last_updated": datetime.now().isoformat(),
                },
            }

            logger.info("今日のサマリー生成完了")
            return today_summary

        except Exception as e:
            logger.error(f"今日のサマリー生成エラー: {e}")
            return {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "version": "1.0",
                },
                "today_summary": {
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "total_stocks": 0,
                    "market_status": "error",
                },
            }

    def generate_predictions(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """予測データの生成"""
        try:
            stocks = stock_data.get("stocks", {})
            if not stocks:
                return {
                    "metadata": {
                        "generated_at": datetime.now().isoformat(),
                        "version": "1.0",
                    },
                    "predictions": [],
                }

            predictions = []
            for code, stock_info in stocks.items():
                current_price = stock_info.get("current_price", {}).get("last_price", 0)
                prediction_data = stock_info.get("prediction", {})

                prediction = {
                    "code": code,
                    "name": stock_info.get("name", ""),
                    "current_price": current_price,
                    "predicted_price": prediction_data.get(
                        "predicted_price", current_price * 1.02
                    ),
                    "confidence": prediction_data.get("confidence", 0.75),
                    "change_percent": prediction_data.get("change_percent", 2.0),
                    "model_used": prediction_data.get("model_used", "Random Forest"),
                    "prediction_date": prediction_data.get(
                        "prediction_date", datetime.now().isoformat()
                    ),
                }
                predictions.append(prediction)

            result = {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "version": "1.0",
                    "total_predictions": len(predictions),
                },
                "predictions": predictions,
            }

            logger.info(f"予測データ生成完了: {len(predictions)}件")
            return result

        except Exception as e:
            logger.error(f"予測データ生成エラー: {e}")
            return {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "version": "1.0",
                },
                "predictions": [],
            }

    def generate_model_comparison(self) -> Dict[str, Any]:
        """モデル比較データの生成"""
        try:
            models = [
                {
                    "name": "Random Forest",
                    "accuracy": round(random.uniform(0.80, 0.90), 3),
                    "mae": round(random.uniform(0.10, 0.20), 3),
                    "rmse": round(random.uniform(0.15, 0.25), 3),
                    "r2": round(random.uniform(0.75, 0.85), 3),
                    "status": "active",
                },
                {
                    "name": "XGBoost",
                    "accuracy": round(random.uniform(0.78, 0.88), 3),
                    "mae": round(random.uniform(0.12, 0.22), 3),
                    "rmse": round(random.uniform(0.18, 0.28), 3),
                    "r2": round(random.uniform(0.73, 0.83), 3),
                    "status": "active",
                },
                {
                    "name": "Linear Regression",
                    "accuracy": round(random.uniform(0.70, 0.80), 3),
                    "mae": round(random.uniform(0.15, 0.25), 3),
                    "rmse": round(random.uniform(0.20, 0.30), 3),
                    "r2": round(random.uniform(0.65, 0.75), 3),
                    "status": "active",
                },
            ]

            result = {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "version": "1.0",
                    "total_models": len(models),
                },
                "models": models,
                "best_model": "Random Forest",
                "comparison_date": datetime.now().isoformat(),
            }

            logger.info("モデル比較データ生成完了")
            return result

        except Exception as e:
            logger.error(f"モデル比較データ生成エラー: {e}")
            return {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "version": "1.0",
                },
                "models": [],
            }

    def generate_feature_analysis(self) -> Dict[str, Any]:
        """特徴量分析データの生成"""
        try:
            features = [
                {
                    "name": "Price Change",
                    "importance": round(random.uniform(0.30, 0.40), 3),
                    "type": "technical",
                },
                {
                    "name": "Volume Ratio",
                    "importance": round(random.uniform(0.20, 0.30), 3),
                    "type": "volume",
                },
                {
                    "name": "RSI",
                    "importance": round(random.uniform(0.15, 0.25), 3),
                    "type": "momentum",
                },
                {
                    "name": "Moving Average",
                    "importance": round(random.uniform(0.10, 0.20), 3),
                    "type": "trend",
                },
                {
                    "name": "Volatility",
                    "importance": round(random.uniform(0.05, 0.15), 3),
                    "type": "risk",
                },
            ]

            result = {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "version": "1.0",
                    "total_features": len(features),
                },
                "features": features,
                "analysis_date": datetime.now().isoformat(),
            }

            logger.info("特徴量分析データ生成完了")
            return result

        except Exception as e:
            logger.error(f"特徴量分析データ生成エラー: {e}")
            return {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "version": "1.0",
                },
                "features": [],
            }

    def generate_performance_metrics(self) -> Dict[str, Any]:
        """性能指標データの生成"""
        try:
            metrics = {
                "overall": {
                    "accuracy": round(random.uniform(0.80, 0.90), 3),
                    "precision": round(random.uniform(0.75, 0.85), 3),
                    "recall": round(random.uniform(0.80, 0.90), 3),
                    "f1_score": round(random.uniform(0.80, 0.90), 3),
                },
                "regression": {
                    "mae": round(random.uniform(0.10, 0.20), 3),
                    "rmse": round(random.uniform(0.15, 0.25), 3),
                    "r2": round(random.uniform(0.75, 0.85), 3),
                    "mape": round(random.uniform(0.10, 0.20), 3),
                },
                "classification": {
                    "accuracy": round(random.uniform(0.80, 0.90), 3),
                    "precision": round(random.uniform(0.75, 0.85), 3),
                    "recall": round(random.uniform(0.80, 0.90), 3),
                    "f1_score": round(random.uniform(0.80, 0.90), 3),
                },
            }

            result = {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "version": "1.0",
                },
                "metrics": metrics,
                "evaluation_date": datetime.now().isoformat(),
            }

            logger.info("性能指標データ生成完了")
            return result

        except Exception as e:
            logger.error(f"性能指標データ生成エラー: {e}")
            return {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "version": "1.0",
                },
                "metrics": {},
            }

    def save_json_file(self, data: Dict[str, Any], filename: str):
        """JSONファイルの保存"""
        try:
            file_path = self.data_dir / filename
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"ファイル保存完了: {file_path}")
        except Exception as e:
            logger.error(f"ファイル保存エラー ({filename}): {e}")

    def run_sample_data_generation(self):
        """サンプルキャッシュデータ生成の実行"""
        try:
            logger.info("=== サンプルキャッシュデータ生成開始 ===")

            # サンプル株価データの生成
            sample_data = self.generate_sample_stocks()

            # 各種データの生成
            dashboard_summary = self.generate_dashboard_summary(sample_data)
            today_summary = self.generate_today_summary(sample_data)
            predictions = self.generate_predictions(sample_data)
            model_comparison = self.generate_model_comparison()
            feature_analysis = self.generate_feature_analysis()
            performance_metrics = self.generate_performance_metrics()

            # ファイルの保存
            self.save_json_file(sample_data, "stock_data.json")
            self.save_json_file(dashboard_summary, "dashboard_summary.json")
            self.save_json_file(today_summary, "today_summary.json")
            self.save_json_file(predictions, "predictions.json")
            self.save_json_file(model_comparison, "model_comparison.json")
            self.save_json_file(feature_analysis, "feature_analysis.json")
            self.save_json_file(performance_metrics, "performance_metrics.json")

            # サンプルデータのメタデータ
            sample_metadata = {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "version": "1.0",
                    "data_source": "sample_cache",
                    "description": "GitHub Actions用サンプルキャッシュデータ",
                },
                "files_generated": [
                    "stock_data.json",
                    "dashboard_summary.json",
                    "today_summary.json",
                    "predictions.json",
                    "model_comparison.json",
                    "feature_analysis.json",
                    "performance_metrics.json",
                ],
            }

            self.save_json_file(sample_metadata, "sample_cache_metadata.json")

            logger.info("=== サンプルキャッシュデータ生成完了 ===")
            return True

        except Exception as e:
            logger.error(f"サンプルキャッシュデータ生成エラー: {e}")
            return False


def main():
    """メイン処理"""
    generator = SampleCacheDataGenerator()
    success = generator.run_sample_data_generation()

    if success:
        logger.info("サンプルキャッシュデータ生成が正常に完了しました")
        sys.exit(0)
    else:
        logger.error("サンプルキャッシュデータ生成に失敗しました")
        sys.exit(1)


if __name__ == "__main__":
    main()
