#!/usr/bin/env python3
"""
強化されたデータ評価・検証システム
- 適切な学習・検証・テスト分割
- クロスバリデーション
- 過学習検出
- 複数モデル比較
- 評価指標の詳細説明
"""

import json
import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from sklearn.model_selection import (
    train_test_split,
    cross_val_score,
    KFold,
    validation_curve,
)
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.svm import SVR
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    mean_absolute_percentage_error,
)
from sklearn.preprocessing import StandardScaler
import warnings

warnings.filterwarnings("ignore")

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedDataValidator:
    """強化されたデータ評価・検証クラス"""

    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.logger = logging.getLogger(__name__)

        # 評価指標の説明
        self.metrics_explanation = {
            "mae": {
                "name": "平均絶対誤差 (MAE)",
                "description": "予測値と実際の値の差の絶対値の平均。小さいほど良い。",
                "unit": "円",
                "interpretation": "予測が実際の値から平均的にどの程度ずれているかを示す",
            },
            "rmse": {
                "name": "平均平方根誤差 (RMSE)",
                "description": "予測値と実際の値の差の二乗の平均の平方根。MAEより大きな誤差を重く評価。",
                "unit": "円",
                "interpretation": "大きな誤差を重く評価する指標",
            },
            "r2": {
                "name": "決定係数 (R²)",
                "description": "モデルが説明できる分散の割合。1に近いほど良い（ただし1.0は過学習の可能性）。",
                "unit": "0-1の範囲",
                "interpretation": "モデルがデータの変動をどの程度説明できるかを示す",
            },
            "mape": {
                "name": "平均絶対パーセント誤差 (MAPE)",
                "description": "予測誤差の割合の平均。小さいほど良い。",
                "unit": "%",
                "interpretation": "予測誤差の相対的な大きさを示す",
            },
        }

    def create_models(self) -> Dict[str, Any]:
        """複数のモデルを作成"""
        return {
            "Random Forest": RandomForestRegressor(
                n_estimators=100,
                random_state=self.random_state,
                max_depth=10,  # 過学習防止
            ),
            "Gradient Boosting": GradientBoostingRegressor(
                n_estimators=100,
                random_state=self.random_state,
                max_depth=6,  # 過学習防止
            ),
            "Linear Regression": LinearRegression(),
            "Ridge Regression": Ridge(alpha=1.0),
            "Lasso Regression": Lasso(alpha=0.1),
            "SVR": SVR(kernel="rbf", C=1.0, gamma="scale"),
        }

    def split_data_properly(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        test_size: float = 0.2,
        val_size: float = 0.2,
    ) -> Tuple[
        pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, pd.Series
    ]:
        """
        データを学習・検証・テストに適切に分割

        Args:
            X: 特徴量
            y: 目的変数
            test_size: テストデータの割合
            val_size: 検証データの割合（学習データからの割合）

        Returns:
            X_train, X_val, X_test, y_train, y_val, y_test
        """
        # まず学習+検証とテストに分割
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y, test_size=test_size, random_state=self.random_state
        )

        # 学習+検証データを学習と検証に分割
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp, test_size=val_size, random_state=self.random_state
        )

        self.logger.info(f"データ分割完了:")
        self.logger.info(f"  学習データ: {len(X_train)} サンプル")
        self.logger.info(f"  検証データ: {len(X_val)} サンプル")
        self.logger.info(f"  テストデータ: {len(X_test)} サンプル")

        return X_train, X_val, X_test, y_train, y_val, y_test

    def evaluate_model_with_cv(
        self,
        model: Any,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: pd.DataFrame,
        y_val: pd.Series,
        cv_folds: int = 5,
    ) -> Dict[str, Any]:
        """クロスバリデーションを含むモデル評価"""

        # クロスバリデーション
        cv_scores = cross_val_score(
            model, X_train, y_train, cv=cv_folds, scoring="neg_mean_absolute_error"
        )

        # モデル学習
        model.fit(X_train, y_train)

        # 検証データでの評価
        y_val_pred = model.predict(X_val)

        # 評価指標計算
        metrics = {
            "mae": mean_absolute_error(y_val, y_val_pred),
            "rmse": np.sqrt(mean_squared_error(y_val, y_val_pred)),
            "r2": r2_score(y_val, y_val_pred),
            "mape": mean_absolute_percentage_error(y_val, y_val_pred) * 100,
            "cv_mae_mean": -cv_scores.mean(),
            "cv_mae_std": cv_scores.std(),
            "overfitting_risk": self._detect_overfitting(y_val, y_val_pred, cv_scores),
        }

        return metrics

    def _detect_overfitting(
        self, y_val: pd.Series, y_val_pred: np.ndarray, cv_scores: np.ndarray
    ) -> str:
        """過学習の検出"""
        val_mae = mean_absolute_error(y_val, y_val_pred)
        cv_mae_mean = -cv_scores.mean()

        # R²が0.99以上は過学習の可能性
        r2 = r2_score(y_val, y_val_pred)
        if r2 > 0.99:
            return "高リスク（R² > 0.99）"

        # 検証データとCVスコアの差が大きい場合は過学習
        if val_mae > cv_mae_mean * 1.5:
            return "中リスク（検証性能がCV性能より悪い）"

        if val_mae > cv_mae_mean * 1.2:
            return "低リスク（検証性能がCV性能よりやや悪い）"

        return "低リスク"

    def compare_models(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: pd.DataFrame,
        y_val: pd.Series,
        X_test: pd.DataFrame,
        y_test: pd.Series,
    ) -> Dict[str, Any]:
        """複数モデルの比較"""

        models = self.create_models()
        results = []

        self.logger.info("複数モデルの評価を開始...")

        for name, model in models.items():
            self.logger.info(f"評価中: {name}")

            try:
                # モデル評価
                metrics = self.evaluate_model_with_cv(
                    model, X_train, y_train, X_val, y_val
                )

                # テストデータでの最終評価
                model.fit(X_train, y_train)  # 全学習データで再学習
                y_test_pred = model.predict(X_test)

                test_metrics = {
                    "mae": mean_absolute_error(y_test, y_test_pred),
                    "rmse": np.sqrt(mean_squared_error(y_test, y_test_pred)),
                    "r2": r2_score(y_test, y_test_pred),
                    "mape": mean_absolute_percentage_error(y_test, y_test_pred) * 100,
                }

                result = {
                    "model_name": name,
                    "model_type": type(model).__name__,
                    "validation_metrics": metrics,
                    "test_metrics": test_metrics,
                    "rank": 0,  # 後で設定
                }

                results.append(result)

            except Exception as e:
                self.logger.error(f"モデル {name} の評価でエラー: {e}")
                continue

        # ランキング付け（MAE基準）
        results.sort(key=lambda x: x["validation_metrics"]["mae"])
        for i, result in enumerate(results):
            result["rank"] = i + 1

        return {
            "model_results": results,
            "best_model": results[0]["model_name"] if results else None,
            "total_models": len(results),
        }

    def generate_evaluation_report(
        self, comparison_results: Dict[str, Any], output_dir: Path
    ) -> None:
        """評価レポートの生成"""

        # モデル比較データ
        model_comparison = []
        for result in comparison_results["model_results"]:
            model_comparison.append(
                {
                    "model_name": result["model_name"],
                    "model_type": result["model_type"],
                    "mae": result["validation_metrics"]["mae"],
                    "rmse": result["validation_metrics"]["rmse"],
                    "r2": result["validation_metrics"]["r2"],
                    "mape": result["validation_metrics"]["mape"],
                    "rank": result["rank"],
                    "overfitting_risk": result["validation_metrics"][
                        "overfitting_risk"
                    ],
                }
            )

        # パフォーマンス指標（最良モデル）
        best_model = comparison_results["model_results"][0]
        performance_metrics = {
            "model_name": best_model["model_name"],
            "mae": best_model["test_metrics"]["mae"],
            "rmse": best_model["test_metrics"]["rmse"],
            "r2": best_model["test_metrics"]["r2"],
            "mape": best_model["test_metrics"]["mape"],
            "validation_mae": best_model["validation_metrics"]["mae"],
            "cv_mae_mean": best_model["validation_metrics"]["cv_mae_mean"],
            "cv_mae_std": best_model["validation_metrics"]["cv_mae_std"],
            "overfitting_risk": best_model["validation_metrics"]["overfitting_risk"],
        }

        # 評価サマリー
        evaluation_summary = {
            "total_models_evaluated": comparison_results["total_models"],
            "best_model": comparison_results["best_model"],
            "evaluation_method": "3分割（学習・検証・テスト）+ 5-fold CV",
            "overfitting_detection": "実装済み",
            "metrics_explanation": self.metrics_explanation,
            "recommendations": self._generate_recommendations(comparison_results),
        }

        # ファイル出力
        with open(output_dir / "model_comparison.json", "w", encoding="utf-8") as f:
            json.dump(model_comparison, f, indent=2, ensure_ascii=False)

        with open(output_dir / "performance_metrics.json", "w", encoding="utf-8") as f:
            json.dump(performance_metrics, f, indent=2, ensure_ascii=False)

        with open(output_dir / "evaluation_summary.json", "w", encoding="utf-8") as f:
            json.dump(evaluation_summary, f, indent=2, ensure_ascii=False)

        self.logger.info("✅ 評価レポートを生成しました")

    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """推奨事項の生成"""
        recommendations = []

        if not results["model_results"]:
            return ["モデル評価に失敗しました。データを確認してください。"]

        best_model = results["model_results"][0]

        # 過学習チェック
        if best_model["validation_metrics"]["overfitting_risk"] != "低リスク":
            recommendations.append(
                f"⚠️ 過学習のリスクが検出されました: {best_model['validation_metrics']['overfitting_risk']}"
            )

        # R²が高すぎる場合
        if best_model["validation_metrics"]["r2"] > 0.99:
            recommendations.append("⚠️ R²が0.99を超えています。データリークや過学習の可能性があります。")

        # モデル性能の評価
        mae = best_model["validation_metrics"]["mae"]
        if mae < 10:
            recommendations.append("✅ モデル性能は良好です（MAE < 10円）")
        elif mae < 50:
            recommendations.append("⚠️ モデル性能は中程度です（MAE < 50円）")
        else:
            recommendations.append("❌ モデル性能は改善が必要です（MAE > 50円）")

        # クロスバリデーションの安定性
        cv_std = best_model["validation_metrics"]["cv_mae_std"]
        if cv_std < 5:
            recommendations.append("✅ クロスバリデーション結果は安定しています")
        else:
            recommendations.append("⚠️ クロスバリデーション結果にばらつきがあります")

        return recommendations


def main():
    """メイン実行関数"""
    logger.info("🚀 強化されたデータ評価・検証システムを開始")

    # 設定
    output_dir = Path("web-app/public/data")
    output_dir.mkdir(parents=True, exist_ok=True)

    # データ読み込み
    input_file = "processed_stock_data.csv"
    if not Path(input_file).exists():
        logger.error(f"データファイルが見つかりません: {input_file}")
        return

    df = pd.read_csv(input_file)
    logger.info(f"データ読み込み完了: {len(df)} 行")

    # 特徴量と目的変数の設定
    features = ["Close", "Volume", "Open", "High", "Low", "SMA_5", "SMA_25", "SMA_50"]
    target = "Close"

    # 利用可能な特徴量のみを選択
    available_features = [col for col in features if col in df.columns]
    if not available_features:
        logger.error("利用可能な特徴量がありません")
        return

    X = df[available_features].dropna()
    y = df[target].iloc[: len(X)]

    logger.info(f"使用特徴量: {available_features}")
    logger.info(f"データサイズ: {len(X)} サンプル")

    # 評価システムの実行
    validator = EnhancedDataValidator()

    # データ分割
    X_train, X_val, X_test, y_train, y_val, y_test = validator.split_data_properly(
        X, y, test_size=0.2, val_size=0.2
    )

    # モデル比較
    comparison_results = validator.compare_models(
        X_train, y_train, X_val, y_val, X_test, y_test
    )

    # レポート生成
    validator.generate_evaluation_report(comparison_results, output_dir)

    logger.info("✅ データ評価・検証システム完了")


if __name__ == "__main__":
    main()
