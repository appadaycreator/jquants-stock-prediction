#!/usr/bin/env python3
"""
Web表示用のデータ生成スクリプト（簡易版）
UnifiedSystemの循環参照を回避した独立スクリプト
"""

import json
import pandas as pd
import numpy as np
import os
import sys
import logging
import subprocess
import yaml
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_and_select_features(df, config_features, target):
    """利用可能な特徴量を検証・選択"""
    available_features = df.columns.tolist()
    logger.info(f"📁 利用可能なカラム: {available_features}")
    logger.info(f"🔧 設定ファイルの特徴量: {config_features}")

    # 利用可能な特徴量のみをフィルタリング
    valid_features = [f for f in config_features if f in available_features]

    if len(valid_features) == 0:
        # フォールバック: 数値型カラムを自動選択
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        valid_features = [
            col
            for col in numeric_cols
            if col != target and col not in ["Date", "Code", "CompanyName"]
        ]
        logger.warning(
            f"🔄 設定の特徴量が見つからないため、自動選択しました: {valid_features}"
        )

    logger.info(f"✅ 使用する特徴量: {valid_features}")
    return valid_features


def generate_web_data():
    """Web表示用データ生成のメイン関数"""
    # 直接設定ファイルを読み込み（UnifiedSystemの無限ループを回避）
    try:
        with open("config_final.yaml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
        prediction_config = config.get("prediction", {})
        preprocessing_config = config.get("preprocessing", {})
        logger.info("✅ 設定ファイル読み込み完了")
    except Exception as e:
        logger.error(f"設定ファイル読み込みエラー: {e}")
        # デフォルト設定を使用
        prediction_config = {
            "features": ["Close", "Volume", "Open", "High", "Low"],
            "target": "Close",
            "test_size": 0.2,
            "random_state": 42,
        }
        preprocessing_config = {"output_file": "processed_stock_data.csv"}

    output_dir = Path("web-app/public/data")
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("🌐 Web表示用データを生成中...")

    # 1. データ読み込み
    input_file = preprocessing_config.get("output_file", "processed_stock_data.csv")

    # ファイルが存在しない場合、サンプルデータを生成
    if not os.path.exists(input_file):
        logger.warning(f"データファイルが見つかりません: {input_file}")
        logger.info("サンプルデータを生成します...")
        subprocess.run([sys.executable, "create_sample_data.py"], check=True)

    df = pd.read_csv(input_file)

    # 2. 特徴量の検証と選択
    config_features = prediction_config.get("features", [])
    target = prediction_config.get("target", "Close")
    features = validate_and_select_features(df, config_features, target)

    if len(features) == 0:
        logger.error("❌ 使用可能な特徴量がありません")
        return

    # 3. データ分割
    X = df[features].dropna()
    y = df[target].iloc[: len(X)]

    test_size = prediction_config.get("test_size", 0.2)
    random_state = prediction_config.get("random_state", 42)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    # 4. モデル実行（Random Forestを使用）
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    # 5. 評価指標計算
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)

    metrics = {"mae": mae, "rmse": rmse, "r2": r2}

    # 6. Web用データ生成

    # 株価データ (時系列)
    try:
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"])
            stock_data = []
            for i, idx in enumerate(X_test.index):
                if idx < len(df) and i < len(y_test) and i < len(y_pred):
                    stock_data.append(
                        {
                            "Date": df.iloc[idx]["Date"].strftime("%Y-%m-%d"),
                            "Actual": float(y_test.iloc[i]),
                            "Predicted": float(y_pred[i]),
                        }
                    )
        else:
            stock_data = []
            for i, (actual, predicted) in enumerate(zip(y_test, y_pred)):
                stock_data.append(
                    {
                        "Date": f"2024-09-{i+1:02d}",
                        "Actual": float(actual),
                        "Predicted": float(predicted),
                    }
                )

        with open(output_dir / "stock_data.json", "w", encoding="utf-8") as f:
            json.dump(stock_data, f, indent=2, ensure_ascii=False)
        logger.info("✅ 株価データを生成しました")
    except Exception as e:
        logger.error(f"❌ 株価データ生成エラー: {e}")

    # 特徴量重要度
    try:
        feature_importance = pd.DataFrame(
            {"feature": features, "importance": model.feature_importances_}
        ).sort_values("importance", ascending=False)

        if not feature_importance.empty:
            total_importance = feature_importance["importance"].sum()
            feature_analysis = []
            for _, row in feature_importance.iterrows():
                feature_analysis.append(
                    {
                        "feature": row["feature"],
                        "importance": float(row["importance"]),
                        "percentage": (
                            float(row["importance"] / total_importance * 100)
                            if total_importance > 0
                            else 0
                        ),
                    }
                )

            with open(output_dir / "feature_analysis.json", "w", encoding="utf-8") as f:
                json.dump(feature_analysis, f, indent=2, ensure_ascii=False)
            logger.info("✅ 特徴量分析データを生成しました")
    except Exception as e:
        logger.error(f"❌ 特徴量分析データ生成エラー: {e}")

    # パフォーマンス指標
    try:
        performance_metrics = {
            "model_name": "Random Forest",
            "mae": float(metrics.get("mae", 0)),
            "rmse": float(metrics.get("rmse", 0)),
            "r2": float(metrics.get("r2", 0)),
            "data_points": len(y_test),
            "train_size": len(X_train),
            "test_size": len(X_test),
        }

        with open(output_dir / "performance_metrics.json", "w", encoding="utf-8") as f:
            json.dump(performance_metrics, f, indent=2, ensure_ascii=False)
        logger.info("✅ パフォーマンス指標を生成しました")
    except Exception as e:
        logger.error(f"❌ パフォーマンス指標生成エラー: {e}")

    # 予測結果 (散布図用)
    try:
        prediction_results = []
        for actual, predicted in zip(y_test, y_pred):
            prediction_results.append(
                {
                    "Actual": float(actual),
                    "Predicted": float(predicted),
                    "Residuals": float(actual - predicted),
                }
            )

        with open(output_dir / "prediction_results.json", "w", encoding="utf-8") as f:
            json.dump(prediction_results, f, indent=2, ensure_ascii=False)
        logger.info("✅ 予測結果データを生成しました")
    except Exception as e:
        logger.error(f"❌ 予測結果データ生成エラー: {e}")

    # モデル比較 (簡易版)
    try:
        model_comparison = [
            {
                "model_name": "primary_model",
                "model_type": "Random Forest",
                "mae": float(metrics.get("mae", 0)),
                "rmse": float(metrics.get("rmse", 0)),
                "r2": float(metrics.get("r2", 0)),
            }
        ]

        with open(output_dir / "model_comparison.json", "w", encoding="utf-8") as f:
            json.dump(model_comparison, f, indent=2, ensure_ascii=False)
        logger.info("✅ モデル比較データを生成しました")
    except Exception as e:
        logger.error(f"❌ モデル比較データ生成エラー: {e}")

    # ダッシュボードサマリー
    try:
        dashboard_summary = {
            "total_data_points": len(df),
            "prediction_period": (
                f"{df.index[0]} - {df.index[-1]}" if len(df) > 0 else "N/A"
            ),
            "best_model": "Random Forest",
            "mae": f"{metrics.get('mae', 0):.2f}",
            "r2": f"{metrics.get('r2', 0):.2f}",
            "last_updated": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        with open(output_dir / "dashboard_summary.json", "w", encoding="utf-8") as f:
            json.dump(dashboard_summary, f, indent=2, ensure_ascii=False)
        logger.info("✅ ダッシュボードサマリーを生成しました")
    except Exception as e:
        logger.error(f"❌ ダッシュボードサマリー生成エラー: {e}")

    logger.info(f"✅ 全てのデータが {output_dir} に生成されました")


if __name__ == "__main__":
    generate_web_data()
