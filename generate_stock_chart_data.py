#!/usr/bin/env python3
"""
株価チャート表示用データ生成スクリプト
Webアプリケーションで株価推移と移動平均を表示するための正しい形式のデータを生成
"""

import json
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from pathlib import Path
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_stock_chart_data(symbols=None, output_dir="web-app/public/data"):
    """株価チャート表示用データの生成"""

    if symbols is None:
        symbols = ["7203.T", "6758.T", "9984.T"]  # トヨタ、ソニー、ソフトバンクG

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    all_stock_data = []

    for symbol in symbols:
        try:
            logger.info(f"データ取得中: {symbol}")

            # yfinanceでデータ取得
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1y")  # 1年間のデータ

            if data.empty:
                logger.warning(f"データが取得できませんでした: {symbol}")
                continue

            # データの前処理
            data = data.reset_index()
            data["Date"] = data["Date"].dt.strftime("%Y-%m-%d")

            # 技術指標の計算
            data = calculate_technical_indicators(data)

            # 移動平均が計算されたデータのみを保存（最初の50行は除外）
            filtered_data = data[data["SMA_50"].notna()].tail(100)  # 最後の100行のみ
            for _, row in filtered_data.iterrows():
                stock_data = {
                    "date": row["Date"],
                    "code": symbol,
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": int(row["Volume"]),
                    "sma_5": float(row["SMA_5"]),
                    "sma_10": float(row["SMA_10"]),
                    "sma_25": float(row["SMA_25"]),
                    "sma_50": float(row["SMA_50"]),
                }
                all_stock_data.append(stock_data)

            logger.info(f"データ取得完了: {symbol} ({len(data)}行)")

        except Exception as e:
            logger.error(f"データ取得エラー {symbol}: {e}")
            continue

    # データを保存
    stock_data_path = output_path / "stock_data.json"
    with open(stock_data_path, "w", encoding="utf-8") as f:
        json.dump(all_stock_data, f, ensure_ascii=False, indent=2)

    logger.info(f"株価データ保存完了: {stock_data_path} ({len(all_stock_data)}行)")

    # ダッシュボードサマリーも更新
    update_dashboard_summary(output_path, len(all_stock_data))

    return all_stock_data


def calculate_technical_indicators(df):
    """技術指標の計算"""
    try:
        # 移動平均
        df["SMA_5"] = df["Close"].rolling(window=5).mean()
        df["SMA_10"] = df["Close"].rolling(window=10).mean()
        df["SMA_25"] = df["Close"].rolling(window=25).mean()
        df["SMA_50"] = df["Close"].rolling(window=50).mean()

        # RSI
        delta = df["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df["RSI"] = 100 - (100 / (1 + rs))

        # MACD
        exp1 = df["Close"].ewm(span=12).mean()
        exp2 = df["Close"].ewm(span=26).mean()
        df["MACD"] = exp1 - exp2
        df["MACD_Signal"] = df["MACD"].ewm(span=9).mean()
        df["MACD_Histogram"] = df["MACD"] - df["MACD_Signal"]

        # ボリンジャーバンド
        df["BB_Middle"] = df["Close"].rolling(window=20).mean()
        bb_std = df["Close"].rolling(window=20).std()
        df["BB_Upper"] = df["BB_Middle"] + (bb_std * 2)
        df["BB_Lower"] = df["BB_Middle"] - (bb_std * 2)
        df["BB_Percent"] = (df["Close"] - df["BB_Lower"]) / (
            df["BB_Upper"] - df["BB_Lower"]
        )

        return df

    except Exception as e:
        logger.error(f"技術指標計算エラー: {e}")
        return df


def update_dashboard_summary(output_path, data_count):
    """ダッシュボードサマリーの更新"""
    try:
        summary = {
            "total_data_points": data_count,
            "prediction_period": "1年",
            "best_model": "株価チャート表示",
            "mae": "N/A",
            "r2": "N/A",
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        summary_path = output_path / "dashboard_summary.json"
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        logger.info(f"ダッシュボードサマリー更新完了: {summary_path}")

    except Exception as e:
        logger.error(f"サマリー更新エラー: {e}")


def generate_sample_prediction_data(output_dir="web-app/public/data"):
    """サンプル予測データの生成"""
    try:
        output_path = Path(output_dir)

        # サンプル予測結果データ
        predictions = []
        for i in range(50):
            actual = 1000 + np.random.normal(0, 100)
            predicted = actual + np.random.normal(0, 50)
            error = abs(actual - predicted)
            error_percentage = (error / actual) * 100

            predictions.append(
                {
                    "index": i,
                    "actual": round(actual, 2),
                    "predicted": round(predicted, 2),
                    "error": round(error, 2),
                    "error_percentage": round(error_percentage, 2),
                }
            )

        # 予測結果を保存
        pred_path = output_path / "prediction_results.json"
        with open(pred_path, "w", encoding="utf-8") as f:
            json.dump(predictions, f, ensure_ascii=False, indent=2)

        logger.info(f"サンプル予測データ生成完了: {pred_path}")

    except Exception as e:
        logger.error(f"サンプル予測データ生成エラー: {e}")


def generate_sample_model_comparison(output_dir="web-app/public/data"):
    """サンプルモデル比較データの生成"""
    try:
        output_path = Path(output_dir)

        models = [
            {
                "name": "XGBoost",
                "type": "Gradient Boosting",
                "mae": 15.2,
                "mse": 350.5,
                "rmse": 18.7,
                "r2": 0.95,
                "rank": 1,
            },
            {
                "name": "Random Forest",
                "type": "Ensemble",
                "mae": 18.3,
                "mse": 420.8,
                "rmse": 20.5,
                "r2": 0.92,
                "rank": 2,
            },
            {
                "name": "Linear Regression",
                "type": "Linear",
                "mae": 25.1,
                "mse": 680.2,
                "rmse": 26.1,
                "r2": 0.85,
                "rank": 3,
            },
            {
                "name": "SVM",
                "type": "Support Vector",
                "mae": 22.4,
                "mse": 580.3,
                "rmse": 24.1,
                "r2": 0.88,
                "rank": 4,
            },
        ]

        model_path = output_path / "model_comparison.json"
        with open(model_path, "w", encoding="utf-8") as f:
            json.dump(models, f, ensure_ascii=False, indent=2)

        logger.info(f"サンプルモデル比較データ生成完了: {model_path}")

    except Exception as e:
        logger.error(f"サンプルモデル比較データ生成エラー: {e}")


def generate_sample_feature_analysis(output_dir="web-app/public/data"):
    """サンプル特徴量分析データの生成"""
    try:
        output_path = Path(output_dir)

        features = [
            {"feature": "SMA_5", "importance": 0.25, "percentage": 25.0},
            {"feature": "SMA_10", "importance": 0.20, "percentage": 20.0},
            {"feature": "SMA_25", "importance": 0.18, "percentage": 18.0},
            {"feature": "SMA_50", "importance": 0.15, "percentage": 15.0},
            {"feature": "RSI", "importance": 0.12, "percentage": 12.0},
            {"feature": "MACD", "importance": 0.10, "percentage": 10.0},
        ]

        feature_path = output_path / "feature_analysis.json"
        with open(feature_path, "w", encoding="utf-8") as f:
            json.dump(features, f, ensure_ascii=False, indent=2)

        logger.info(f"サンプル特徴量分析データ生成完了: {feature_path}")

    except Exception as e:
        logger.error(f"サンプル特徴量分析データ生成エラー: {e}")


def main():
    """メイン実行関数"""
    logger.info("株価チャート表示用データ生成開始")

    # 株価データ生成
    stock_data = generate_stock_chart_data()

    # サンプルデータ生成
    generate_sample_prediction_data()
    generate_sample_model_comparison()
    generate_sample_feature_analysis()

    logger.info("データ生成完了")
    print(f"生成されたデータ: {len(stock_data)}行の株価データ")


if __name__ == "__main__":
    main()
