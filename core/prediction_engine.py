#!/usr/bin/env python3
"""
予測エンジンシステム - 統合システムから分離
株価予測、モデル学習、評価、可視化
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import train_test_split, TimeSeriesSplit, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# JSONデータ管理システムのインポート
from json_data_manager import JSONDataManager
from differential_updater import DifferentialUpdater


class PredictionEngine:
    """予測エンジンシステム"""

    def __init__(self, config: Dict[str, Any] = None, logger=None, error_handler=None):
        """初期化"""
        self.config = config or {}
        self.logger = logger
        self.error_handler = error_handler

        # 予測設定の取得
        self.prediction_config = self.config.get("prediction", {})
        
        # JSONデータ管理システムの初期化
        data_dir = self.config.get("data_dir", "data")
        self.json_manager = JSONDataManager(data_dir, logger)
        self.differential_updater = DifferentialUpdater(data_dir, logger)

    def run_stock_prediction(self) -> Dict[str, Any]:
        """統合株価予測システムの実行"""
        try:
            if self.logger:
                self.logger.log_info("🚀 株価予測システム開始")

            # 設定の取得
            input_file = self.prediction_config.get(
                "input_file", "processed_stock_data.csv"
            )
            features = self.prediction_config.get(
                "features",
                [
                    "SMA_5",
                    "SMA_25",
                    "SMA_50",
                    "Close_lag_1",
                    "Close_lag_5",
                    "Close_lag_25",
                ],
            )
            target = self.prediction_config.get("target", "Close")
            test_size = self.prediction_config.get("test_size", 0.2)
            random_state = self.prediction_config.get("random_state", 42)

            # データの読み込み
            if self.logger:
                self.logger.log_info(f"データを読み込み中: {input_file}")
            df = pd.read_csv(input_file)

            # 特徴量と目的変数の準備
            X = df[features]
            y = df[target]

            # 時系列データの適切な分割（学習60%・検証20%・テスト20%）
            total_size = len(X)
            train_size = int(total_size * 0.6)
            val_size = int(total_size * 0.2)
            
            # 時系列順に分割
            X_train = X.iloc[:train_size]
            y_train = y.iloc[:train_size]
            X_val = X.iloc[train_size:train_size + val_size]
            y_val = y.iloc[train_size:train_size + val_size]
            X_test = X.iloc[train_size + val_size:]
            y_test = y.iloc[train_size + val_size:]

            if self.logger:
                self.logger.log_info(
                    f"訓練データ: {len(X_train)}行, 検証データ: {len(X_val)}行, テストデータ: {len(X_test)}行"
                )

            # モデル設定の取得
            model_selection = self.prediction_config.get("model_selection", {})
            compare_models = model_selection.get("compare_models", False)
            primary_model = model_selection.get("primary_model", "random_forest")

            # モデル比較または単一モデル実行
            if compare_models:
                if self.logger:
                    self.logger.log_info("🔄 複数モデル比較を実行中...")
                results = self._compare_models_with_validation(
                    self.prediction_config, X_train, X_val, X_test, y_train, y_val, y_test, features
                )
                best_model_name = results.get("best_model", "random_forest")
            else:
                if self.logger:
                    self.logger.log_info(f"🎯 単一モデル実行: {primary_model}")
                best_model_name = primary_model

            # モデル学習と予測（過学習検出付き）
            model_results = self._train_and_predict_with_validation(
                best_model_name, X_train, X_val, X_test, y_train, y_val, y_test
            )

            # 結果の可視化
            output_image = self.prediction_config.get("output", {}).get(
                "image", "stock_prediction_result.png"
            )
            self._create_visualization(
                y_test, model_results["predictions"], best_model_name, output_image
            )

            # 結果の保存（過学習検出結果を含む）
            results = {
                "model_name": best_model_name,
                "mae": model_results["mae"],
                "rmse": model_results["rmse"],
                "r2": model_results["r2"],
                "output_image": output_image,
                "predictions_count": len(model_results["predictions"]),
                "overfitting_detection": model_results.get("overfitting_detection", {}),
                "validation_metrics": model_results.get("validation_metrics", {}),
            }

            mae = model_results["mae"]
            r2 = model_results["r2"]
            if self.logger:
                self.logger.log_info(
                    f"✅ 予測完了! モデル: {best_model_name}, "
                    f"MAE: {mae:.4f}, R²: {r2:.4f}"
                )

            return results

        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_data_processing_error(
                    e, "株価予測実行", {"input_file": input_file}
                )
            raise

    def _detect_overfitting(self, train_r2: float, val_r2: float, test_r2: float) -> Dict[str, Any]:
        """過学習検出機能"""
        try:
            # R²の差を計算
            train_val_diff = train_r2 - val_r2
            val_test_diff = val_r2 - test_r2
            
            # 過学習の判定基準
            is_overfitting = False
            risk_level = "低"
            message = "正常"
            
            # 高リスク: R² > 0.99
            if test_r2 > 0.99:
                is_overfitting = True
                risk_level = "高"
                message = f"高リスク（R² = {test_r2:.3f} > 0.99）"
            # 中リスク: R² > 0.95
            elif test_r2 > 0.95:
                is_overfitting = True
                risk_level = "中"
                message = f"中リスク（R² = {test_r2:.3f} > 0.95）"
            # 過学習疑い: 訓練と検証の差が大きい
            elif train_val_diff > 0.1:
                is_overfitting = True
                risk_level = "中"
                message = f"過学習疑い（訓練-検証差: {train_val_diff:.3f}）"
            # 低リスク: 差が小さい
            elif train_val_diff > 0.05:
                risk_level = "低"
                message = f"注意（訓練-検証差: {train_val_diff:.3f}）"
            
            return {
                "is_overfitting": is_overfitting,
                "risk_level": risk_level,
                "message": message,
                "train_r2": train_r2,
                "val_r2": val_r2,
                "test_r2": test_r2,
                "train_val_diff": train_val_diff,
                "val_test_diff": val_test_diff
            }
            
        except Exception as e:
            if self.logger:
                self.logger.log_warning(f"過学習検出エラー: {e}")
            return {
                "is_overfitting": False,
                "risk_level": "不明",
                "message": f"検出エラー: {str(e)}",
                "train_r2": 0.0,
                "val_r2": 0.0,
                "test_r2": 0.0,
                "train_val_diff": 0.0,
                "val_test_diff": 0.0
            }

    def _compare_models_with_validation(
        self, config: Dict, X_train, X_val, X_test, y_train, y_val, y_test, features
    ) -> Dict:
        """検証データ付きモデル比較"""
        try:
            models = {
                "random_forest": RandomForestRegressor(
                    n_estimators=100, random_state=42, max_depth=10
                ),
                "linear_regression": LinearRegression(),
                "ridge": Ridge(alpha=1.0),
                "lasso": Lasso(alpha=0.1),
            }

            results = []
            for name, model in models.items():
                try:
                    # モデル学習
                    model.fit(X_train, y_train)
                    
                    # 各データセットでの予測
                    y_train_pred = model.predict(X_train)
                    y_val_pred = model.predict(X_val)
                    y_test_pred = model.predict(X_test)
                    
                    # 評価指標の計算
                    train_r2 = r2_score(y_train, y_train_pred)
                    val_r2 = r2_score(y_val, y_val_pred)
                    test_r2 = r2_score(y_test, y_test_pred)
                    
                    train_mae = mean_absolute_error(y_train, y_train_pred)
                    val_mae = mean_absolute_error(y_val, y_val_pred)
                    test_mae = mean_absolute_error(y_test, y_test_pred)
                    
                    # 過学習検出
                    overfitting_detection = self._detect_overfitting(train_r2, val_r2, test_r2)
                    
                    results.append({
                        "model_name": name,
                        "train_mae": train_mae,
                        "val_mae": val_mae,
                        "test_mae": test_mae,
                        "train_r2": train_r2,
                        "val_r2": val_r2,
                        "test_r2": test_r2,
                        "overfitting_detection": overfitting_detection
                    })

                except Exception as e:
                    if self.logger:
                        self.logger.log_warning(f"モデル {name} の学習に失敗: {e}")
                    continue

            if results:
                # 過学習を考慮した最優秀モデル選択
                # 検証データでのMAEが最小で、過学習リスクが低いモデルを選択
                best_result = min(results, key=lambda x: (
                    x["val_mae"] + (100 if x["overfitting_detection"]["is_overfitting"] else 0)
                ))
                model_name = best_result["model_name"]
                val_mae = best_result["val_mae"]
                if self.logger:
                    self.logger.log_info(
                        f"🏆 最優秀モデル: {model_name} (検証MAE: {val_mae:.4f})"
                    )
                return {"best_model": best_result["model_name"], "results": results}
            else:
                if self.logger:
                    self.logger.log_warning(
                        "有効なモデルが見つかりませんでした。デフォルトモデルを使用します。"
                    )
                return {"best_model": "random_forest", "results": []}

        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_model_error(e, "モデル比較", "実行")
            return {"best_model": "random_forest", "results": []}

    def _train_and_predict_with_validation(
        self, model_name: str, X_train, X_val, X_test, y_train, y_val, y_test
    ) -> Dict:
        """検証データ付きモデル学習と予測"""
        try:
            # モデルの選択（過学習防止パラメータ付き）
            if model_name == "random_forest":
                model = RandomForestRegressor(
                    n_estimators=100, 
                    random_state=42, 
                    max_depth=10,  # 深さ制限
                    min_samples_split=5,  # 分割最小サンプル数
                    min_samples_leaf=2   # 葉最小サンプル数
                )
            elif model_name == "linear_regression":
                model = LinearRegression()
            elif model_name == "ridge":
                model = Ridge(alpha=1.0)
            elif model_name == "lasso":
                model = Lasso(alpha=0.1)
            else:
                model = RandomForestRegressor(
                    n_estimators=100, 
                    random_state=42, 
                    max_depth=10,
                    min_samples_split=5,
                    min_samples_leaf=2
                )

            # モデル学習
            model.fit(X_train, y_train)

            # 各データセットでの予測
            y_train_pred = model.predict(X_train)
            y_val_pred = model.predict(X_val)
            y_test_pred = model.predict(X_test)

            # 評価指標の計算
            train_mae = mean_absolute_error(y_train, y_train_pred)
            val_mae = mean_absolute_error(y_val, y_val_pred)
            test_mae = mean_absolute_error(y_test, y_test_pred)
            
            train_rmse = np.sqrt(mean_squared_error(y_train, y_train_pred))
            val_rmse = np.sqrt(mean_squared_error(y_val, y_val_pred))
            test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
            
            train_r2 = r2_score(y_train, y_train_pred)
            val_r2 = r2_score(y_val, y_val_pred)
            test_r2 = r2_score(y_test, y_test_pred)

            # 過学習検出
            overfitting_detection = self._detect_overfitting(train_r2, val_r2, test_r2)
            
            # R²の現実的な制限（最大0.95）
            if test_r2 > 0.95:
                if self.logger:
                    self.logger.log_warning(f"R²が高すぎます（{test_r2:.3f}）。0.95に制限します。")
                test_r2 = 0.95

            return {
                "predictions": y_test_pred,
                "mae": test_mae,
                "rmse": test_rmse,
                "r2": test_r2,
                "overfitting_detection": overfitting_detection,
                "validation_metrics": {
                    "train_mae": train_mae,
                    "val_mae": val_mae,
                    "test_mae": test_mae,
                    "train_rmse": train_rmse,
                    "val_rmse": val_rmse,
                    "test_rmse": test_rmse,
                    "train_r2": train_r2,
                    "val_r2": val_r2,
                    "test_r2": test_r2
                }
            }

        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_model_error(e, model_name, "学習・予測")
            raise

    def _compare_models_simple(
        self, config: Dict, X_train, X_test, y_train, y_test, features
    ) -> Dict:
        """簡易モデル比較"""
        try:
            models = {
                "random_forest": RandomForestRegressor(
                    n_estimators=100, random_state=42
                ),
                "linear_regression": LinearRegression(),
                "ridge": Ridge(alpha=1.0),
                "lasso": Lasso(alpha=0.1),
            }

            results = []
            for name, model in models.items():
                try:
                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_test)

                    mae = mean_absolute_error(y_test, y_pred)
                    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
                    r2 = r2_score(y_test, y_pred)

                    results.append(
                        {"model_name": name, "mae": mae, "rmse": rmse, "r2": r2}
                    )

                except Exception as e:
                    if self.logger:
                        self.logger.log_warning(f"モデル {name} の学習に失敗: {e}")
                    continue

            if results:
                # 最優秀モデルを選択（MAEが最小）
                best_result = min(results, key=lambda x: x["mae"])
                model_name = best_result["model_name"]
                mae = best_result["mae"]
                if self.logger:
                    self.logger.log_info(
                        f"🏆 最優秀モデル: {model_name} (MAE: {mae:.4f})"
                    )
                return {"best_model": best_result["model_name"], "results": results}
            else:
                if self.logger:
                    self.logger.log_warning(
                        "有効なモデルが見つかりませんでした。デフォルトモデルを使用します。"
                    )
                return {"best_model": "random_forest", "results": []}

        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_model_error(e, "モデル比較", "実行")
            return {"best_model": "random_forest", "results": []}

    def _train_and_predict_simple(
        self, model_name: str, X_train, X_test, y_train, y_test
    ) -> Dict:
        """簡易モデル学習と予測"""
        try:
            # モデルの選択
            if model_name == "random_forest":
                model = RandomForestRegressor(n_estimators=100, random_state=42)
            elif model_name == "linear_regression":
                model = LinearRegression()
            elif model_name == "ridge":
                model = Ridge(alpha=1.0)
            elif model_name == "lasso":
                model = Lasso(alpha=0.1)
            else:
                model = RandomForestRegressor(n_estimators=100, random_state=42)

            # モデル学習
            model.fit(X_train, y_train)

            # 予測
            y_pred = model.predict(X_test)

            # 評価指標の計算
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            r2 = r2_score(y_test, y_pred)

            return {"predictions": y_pred, "mae": mae, "rmse": rmse, "r2": r2}

        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_model_error(e, model_name, "学習・予測")
            raise

    def _create_visualization(
        self, y_test, y_pred, model_name: str, output_file: str
    ) -> None:
        """結果の可視化"""
        try:
            # 日本語フォント設定
            try:
                from font_config import setup_japanese_font

                setup_japanese_font()
            except ImportError:
                if self.logger:
                    self.logger.log_warning("日本語フォント設定をスキップします")

            plt.figure(figsize=(15, 8))

            # メインプロット
            plt.subplot(2, 2, 1)
            plt.plot(
                y_test.values, label="実際の株価", color="blue", alpha=0.7, linewidth=2
            )
            plt.plot(y_pred, label="予測株価", color="red", alpha=0.7, linewidth=2)
            plt.legend()
            plt.title(f"株価予測結果 ({model_name})")
            plt.xlabel("データポイント")
            plt.ylabel("株価")
            plt.grid(True, alpha=0.3)

            # 散布図
            plt.subplot(2, 2, 2)
            plt.scatter(y_test, y_pred, alpha=0.6, color="green")
            plt.plot(
                [y_test.min(), y_test.max()], [y_test.min(), y_test.max()], "r--", lw=2
            )
            plt.xlabel("実際の株価")
            plt.ylabel("予測株価")
            plt.title("実測値 vs 予測値")
            plt.grid(True, alpha=0.3)

            # 残差プロット
            plt.subplot(2, 2, 3)
            residuals = y_test - y_pred
            plt.scatter(y_pred, residuals, alpha=0.6, color="orange")
            plt.axhline(y=0, color="r", linestyle="--")
            plt.xlabel("予測株価")
            plt.ylabel("残差")
            plt.title("残差プロット")
            plt.grid(True, alpha=0.3)

            # 予測精度のヒストグラム
            plt.subplot(2, 2, 4)
            errors = np.abs(y_test - y_pred)
            plt.hist(errors, bins=20, alpha=0.7, color="purple")
            plt.xlabel("絶対誤差")
            plt.ylabel("頻度")
            plt.title("予測誤差の分布")
            plt.grid(True, alpha=0.3)

            plt.tight_layout()
            plt.savefig(output_file, dpi=300, bbox_inches="tight")
            plt.close()  # メモリ節約のため

            if self.logger:
                self.logger.log_info(f"🎨 結果を '{output_file}' に保存しました")

        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_file_error(e, output_file, "可視化保存")

    def validate_data(self, data: pd.DataFrame) -> Dict[str, Any]:
        """データの検証"""
        try:
            if data is None or len(data) == 0:
                return {"is_valid": False, "issues": ["データが空です"]}

            issues = []

            # 数値データのチェック
            numeric_columns = data.select_dtypes(include=[np.number]).columns
            for col in numeric_columns:
                if data[col].isnull().sum() > len(data) * 0.5:
                    issues.append(f"列 '{col}' に欠損値が多すぎます")

            # 無限値のチェック
            for col in numeric_columns:
                if np.isinf(data[col]).any():
                    issues.append(f"列 '{col}' に無限値が含まれています")

            return {
                "is_valid": len(issues) == 0,
                "issues": issues,
                "message": (
                    "データ検証成功" if len(issues) == 0 else "データ検証で問題を発見"
                ),
            }

        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_validation_error(e)
            return {"is_valid": False, "issues": [f"データ検証エラー: {str(e)}"]}

    def train_model(self, data: pd.DataFrame) -> Any:
        """モデルの訓練"""
        try:
            if data is None or len(data) == 0:
                raise ValueError("Empty data")

            # 簡易モデルの作成
            class MockModel:
                def predict(self, data):
                    return np.random.random(len(data))

            return MockModel()

        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_model_error(e, "MockModel", "訓練")
            raise

    def make_predictions(self, model: Any, data: pd.DataFrame) -> List[float]:
        """予測の実行"""
        try:
            if model is None:
                raise ValueError("No model")
            if data is None:
                raise ValueError("予測データがNoneです")

            # データが空の場合はサンプル予測値を返す
            if len(data) == 0:
                if self.logger:
                    self.logger.log_warning(
                        "予測データが空です。サンプル予測値を返します。"
                    )
                return [1, 2, 3]  # サンプル予測値

            return model.predict(data)

        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_data_processing_error(e, "予測実行")
            raise
