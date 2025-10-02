#!/usr/bin/env python3
"""
テスト用サンプルデータ生成スクリプト
実装した機能のテストと動作確認用のサンプルデータを生成
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import random


def create_sample_stock_data():
    """サンプル株価データの作成"""
    sample_stocks = {
        "7203": {
            "name": "トヨタ自動車",
            "sector": "自動車",
            "last_price": 2500 + random.randint(-100, 100),
            "change": random.randint(-50, 50),
            "change_percent": round(random.uniform(-2, 2), 2),
            "volume": random.randint(500000, 2000000),
            "sma_5": 2480 + random.randint(-50, 50),
            "sma_25": 2450 + random.randint(-100, 100),
            "sma_75": 2400 + random.randint(-150, 150),
            "rsi": random.randint(30, 70),
            "macd": round(random.uniform(-10, 10), 2),
            "bollinger_upper": 2600 + random.randint(-100, 100),
            "bollinger_lower": 2400 + random.randint(-100, 100),
            "predicted_price": 2550 + random.randint(-100, 100),
            "confidence": round(random.uniform(0.6, 0.95), 2),
            "volatility": round(random.uniform(0.1, 0.3), 3),
            "beta": round(random.uniform(0.8, 1.2), 2),
            "sharpe_ratio": round(random.uniform(0.5, 2.0), 2),
            "max_drawdown": round(random.uniform(-0.2, -0.05), 3),
            "data_quality": "good",
            "created_at": (datetime.now() - timedelta(days=1)).isoformat(),
            "updated_at": datetime.now().isoformat(),
            "last_trade_date": datetime.now().isoformat(),
        },
        "6758": {
            "name": "ソニーグループ",
            "sector": "エレクトロニクス",
            "last_price": 12000 + random.randint(-500, 500),
            "change": random.randint(-300, 300),
            "change_percent": round(random.uniform(-3, 3), 2),
            "volume": random.randint(200000, 800000),
            "sma_5": 12100 + random.randint(-200, 200),
            "sma_25": 12200 + random.randint(-300, 300),
            "sma_75": 11800 + random.randint(-500, 500),
            "rsi": random.randint(25, 75),
            "macd": round(random.uniform(-20, 20), 2),
            "bollinger_upper": 12500 + random.randint(-300, 300),
            "bollinger_lower": 11500 + random.randint(-300, 300),
            "predicted_price": 11800 + random.randint(-500, 500),
            "confidence": round(random.uniform(0.7, 0.9), 2),
            "volatility": round(random.uniform(0.15, 0.35), 3),
            "beta": round(random.uniform(0.9, 1.3), 2),
            "sharpe_ratio": round(random.uniform(0.3, 1.8), 2),
            "max_drawdown": round(random.uniform(-0.25, -0.08), 3),
            "data_quality": "good",
            "created_at": (datetime.now() - timedelta(days=2)).isoformat(),
            "updated_at": datetime.now().isoformat(),
            "last_trade_date": datetime.now().isoformat(),
        },
        "9984": {
            "name": "ソフトバンクグループ",
            "sector": "情報通信",
            "last_price": 8000 + random.randint(-200, 200),
            "change": random.randint(-100, 100),
            "change_percent": round(random.uniform(-2, 2), 2),
            "volume": random.randint(300000, 1200000),
            "sma_5": 8100 + random.randint(-100, 100),
            "sma_25": 8200 + random.randint(-200, 200),
            "sma_75": 8000 + random.randint(-300, 300),
            "rsi": random.randint(35, 65),
            "macd": round(random.uniform(-15, 15), 2),
            "bollinger_upper": 8500 + random.randint(-200, 200),
            "bollinger_lower": 7500 + random.randint(-200, 200),
            "predicted_price": 8200 + random.randint(-300, 300),
            "confidence": round(random.uniform(0.65, 0.88), 2),
            "volatility": round(random.uniform(0.2, 0.4), 3),
            "beta": round(random.uniform(1.0, 1.5), 2),
            "sharpe_ratio": round(random.uniform(0.2, 1.5), 2),
            "max_drawdown": round(random.uniform(-0.3, -0.1), 3),
            "data_quality": "good",
            "created_at": (datetime.now() - timedelta(days=3)).isoformat(),
            "updated_at": datetime.now().isoformat(),
            "last_trade_date": datetime.now().isoformat(),
        },
    }

    return sample_stocks


def generate_structured_sample_data():
    """構造化されたサンプルデータの生成"""
    sample_stocks = create_sample_stock_data()

    # メインデータ構造
    structured_data = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "version": "2.0",
            "data_source": "jquants",
            "total_stocks": len(sample_stocks),
            "structure_version": "2.0",
            "update_type": "sample",
        },
        "stocks": {},
    }

    # 各銘柄の構造化
    for code, stock_info in sample_stocks.items():
        structured_data["stocks"][code] = {
            "code": code,
            "name": stock_info["name"],
            "sector": stock_info["sector"],
            "current_price": {
                "last_price": stock_info["last_price"],
                "change": stock_info["change"],
                "change_percent": stock_info["change_percent"],
                "updated_at": stock_info["updated_at"],
            },
            "volume": {
                "current_volume": stock_info["volume"],
                "average_volume": stock_info["volume"] * random.uniform(0.8, 1.2),
                "volume_ratio": round(random.uniform(0.5, 2.0), 2),
            },
            "technical_indicators": {
                "sma_5": stock_info["sma_5"],
                "sma_25": stock_info["sma_25"],
                "sma_75": stock_info["sma_75"],
                "rsi": stock_info["rsi"],
                "macd": stock_info["macd"],
                "bollinger_upper": stock_info["bollinger_upper"],
                "bollinger_lower": stock_info["bollinger_lower"],
            },
            "prediction": {
                "predicted_price": stock_info["predicted_price"],
                "confidence": stock_info["confidence"],
                "model_used": "RandomForest",
                "prediction_date": datetime.now().isoformat(),
            },
            "risk_metrics": {
                "volatility": stock_info["volatility"],
                "beta": stock_info["beta"],
                "sharpe_ratio": stock_info["sharpe_ratio"],
                "max_drawdown": stock_info["max_drawdown"],
            },
            "metadata": {
                "created_at": stock_info["created_at"],
                "updated_at": stock_info["updated_at"],
                "data_quality": stock_info["data_quality"],
                "last_trade_date": stock_info["last_trade_date"],
            },
        }

    return structured_data


def save_sample_data():
    """サンプルデータの保存"""
    # ディレクトリの作成
    data_dir = Path("docs/data")
    data_dir.mkdir(parents=True, exist_ok=True)

    stocks_dir = data_dir / "stocks"
    stocks_dir.mkdir(exist_ok=True)

    metadata_dir = data_dir / "metadata"
    metadata_dir.mkdir(exist_ok=True)

    # 構造化データの生成
    structured_data = generate_structured_sample_data()

    # メインファイルの保存
    main_file = data_dir / "stock_data.json"
    with open(main_file, "w", encoding="utf-8") as f:
        json.dump(structured_data, f, ensure_ascii=False, indent=2)

    print(f"メインファイル保存: {main_file}")

    # 個別銘柄ファイルの保存
    for code, stock_info in structured_data["stocks"].items():
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

        print(f"個別ファイル保存: {individual_file}")

    # インデックスファイルの生成
    index_data = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "version": "2.0",
            "total_stocks": len(structured_data["stocks"]),
            "last_updated": structured_data["metadata"]["generated_at"],
        },
        "stocks": [],
    }

    for code, stock_info in structured_data["stocks"].items():
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

    index_file = data_dir / "index.json"
    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)

    print(f"インデックスファイル保存: {index_file}")

    # メタデータファイルの生成
    basic_metadata = {
        "last_updated": structured_data["metadata"]["generated_at"],
        "total_stocks": structured_data["metadata"]["total_stocks"],
        "data_source": structured_data["metadata"]["data_source"],
        "version": structured_data["metadata"]["version"],
        "file_size": main_file.stat().st_size,
        "update_status": "success",
    }

    metadata_file = metadata_dir / "basic.json"
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(basic_metadata, f, ensure_ascii=False, indent=2)

    print(f"メタデータファイル保存: {metadata_file}")

    print("\n=== サンプルデータ生成完了 ===")
    print(f"総ファイル数: {len(list(data_dir.rglob('*.json')))}")
    print(f"総サイズ: {sum(f.stat().st_size for f in data_dir.rglob('*.json'))} bytes")


def main():
    """メイン処理"""
    print("サンプルデータ生成開始...")
    save_sample_data()


if __name__ == "__main__":
    main()
