#!/usr/bin/env python3
"""
最適化されたモデル比較システム
重複計算を排除し、キャッシュ機能を活用した効率的なモデル比較
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple, Any, Callable
from functools import lru_cache
import joblib
import hashlib
import os
from unified_parallel_processing_system import (
    execute_parallel,
    get_parallel_config,
    set_parallel_config
)
from unified_system import get_unified_system
import multiprocessing as mp
from sklearn.model_selection import cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import time
from dataclasses import dataclass
from unified_system import UnifiedSystem

logger = logging.getLogger(__name__)


@dataclass
class ModelResult:
    """モデル結果データクラス"""

    model_name: str
    model_type: str
    mae: float
    mse: float
    rmse: float
    r2: float
    training_time: float
    prediction_time: float
    memory_usage: float
    cross_val_scores: Optional[List[float]] = None
    feature_importance: Optional[Dict[str, float]] = None


class ModelCache:
    """モデルキャッシュ管理クラス"""

    def __init__(self, cache_dir: str = "model_cache"):
        self.cache_dir = cache_dir
        self.logger = logging.getLogger(__name__)
        os.makedirs(cache_dir, exist_ok=True)

    def _generate_cache_key(
        self, model_name: str, X_hash: str, y_hash: str, params: Dict
    ) -> str:
        """キャッシュキーを生成"""
        key_string = f"{model_name}_{X_hash}_{y_hash}_{str(sorted(params.items()))}"
        return hashlib.md5(key_string.encode()).hexdigest()

    def _generate_data_hash(self, data: np.ndarray) -> str:
        """データのハッシュを生成"""
        return hashlib.md5(data.tobytes()).hexdigest()

    def get_cached_model(
        self, model_name: str, X_train: np.ndarray, y_train: np.ndarray, params: Dict
    ) -> Optional[Any]:
        """キャッシュからモデルを取得"""
        try:
            X_hash = self._generate_data_hash(X_train)
            y_hash = self._generate_data_hash(y_train)
            cache_key = self._generate_cache_key(model_name, X_hash, y_hash, params)
            cache_file = os.path.join(self.cache_dir, f"{cache_key}.joblib")

            if os.path.exists(cache_file):
                self.logger.debug(f"📋 キャッシュヒット: {model_name}")
                return joblib.load(cache_file)
            return None
        except Exception as e:
            self.logger.warning(f"⚠️ キャッシュ取得エラー: {e}")
            return None

    def save_model(
        self,
        model: Any,
        model_name: str,
        X_train: np.ndarray,
        y_train: np.ndarray,
        params: Dict,
    ):
        """モデルをキャッシュに保存"""
        try:
            X_hash = self._generate_data_hash(X_train)
            y_hash = self._generate_data_hash(y_train)
            cache_key = self._generate_cache_key(model_name, X_hash, y_hash, params)
            cache_file = os.path.join(self.cache_dir, f"{cache_key}.joblib")

            joblib.dump(model, cache_file)
            self.logger.debug(f"💾 モデルをキャッシュに保存: {model_name}")
        except Exception as e:
            self.logger.warning(f"⚠️ キャッシュ保存エラー: {e}")

    def clear_cache(self):
        """キャッシュをクリア"""
        try:
            for file in os.listdir(self.cache_dir):
                if file.endswith(".joblib"):
                    os.remove(os.path.join(self.cache_dir, file))
            self.logger.info("🧹 モデルキャッシュをクリアしました")
        except Exception as e:
            self.logger.warning(f"⚠️ キャッシュクリアエラー: {e}")


class FeatureCache:
    """特徴量計算キャッシュ"""

    def __init__(self, max_size: int = 1000):
        self.cache = {}
        self.max_size = max_size
        self.access_order = []
        self.logger = logging.getLogger(__name__)

    @lru_cache(maxsize=100)
    def get_cached_features(
        self, data_hash: str, feature_func_name: str, *args, **kwargs
    ):
        """キャッシュから特徴量を取得"""
        cache_key = f"{data_hash}_{feature_func_name}_{hash(str(args))}_{hash(str(sorted(kwargs.items())))}"

        if cache_key in self.cache:
            self.access_order.remove(cache_key)
            self.access_order.append(cache_key)
            self.logger.debug(f"📋 特徴量キャッシュヒット: {feature_func_name}")
            return self.cache[cache_key]

        return None

    def save_features(
        self, data_hash: str, feature_func_name: str, result: Any, *args, **kwargs
    ):
        """特徴量をキャッシュに保存"""
        cache_key = f"{data_hash}_{feature_func_name}_{hash(str(args))}_{hash(str(sorted(kwargs.items())))}"

        # キャッシュサイズ制限
        if len(self.cache) >= self.max_size:
            oldest_key = self.access_order.pop(0)
            del self.cache[oldest_key]

        self.cache[cache_key] = result
        self.access_order.append(cache_key)
        self.logger.debug(f"💾 特徴量をキャッシュに保存: {feature_func_name}")


class OptimizedModelComparator:
    """最適化されたモデル比較クラス"""

    def __init__(self, max_workers: int = None, use_cache: bool = True):
        # 設定ファイルからmax_workersを読み込み
        try:
            import yaml

            with open("config_final.yaml", "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            self.max_workers = max_workers or config.get("performance", {}).get(
                "max_workers", 4
            )
        except Exception:
            self.max_workers = max_workers or min(4, mp.cpu_count())
        self.use_cache = use_cache
        self.model_cache = ModelCache() if use_cache else None
        self.feature_cache = FeatureCache()
        self.system = UnifiedSystem("OptimizedModelComparator")
        self.logger = logging.getLogger(__name__)

        # 計算済みメトリクスをキャッシュ
        self.metrics_cache = {}

    def compare_models_optimized(
        self,
        models_config: Dict[str, Dict],
        X_train: np.ndarray,
        X_test: np.ndarray,
        y_train: np.ndarray,
        y_test: np.ndarray,
        feature_names: List[str] = None,
        use_parallel: bool = True,
        use_cross_validation: bool = False,
        cv_folds: int = 5,
    ) -> pd.DataFrame:
        """最適化されたモデル比較"""
        self.logger.info(f"🚀 最適化されたモデル比較開始 (並列処理: {use_parallel})")

        start_time = time.time()
        results = []

        # データハッシュを生成（キャッシュ用）
        data_hash = self._generate_data_hash(X_train, y_train)

        if use_parallel:
            results = self._compare_models_parallel(
                models_config,
                X_train,
                X_test,
                y_train,
                y_test,
                feature_names,
                data_hash,
                use_cross_validation,
                cv_folds,
            )
        else:
            results = self._compare_models_sequential(
                models_config,
                X_train,
                X_test,
                y_train,
                y_test,
                feature_names,
                data_hash,
                use_cross_validation,
                cv_folds,
            )

        processing_time = time.time() - start_time
        self.logger.info(f"✅ モデル比較完了: {processing_time:.2f}秒")

        if not results:
            self.logger.warning("⚠️ 評価できたモデルがありません")
            return pd.DataFrame()

        df_results = pd.DataFrame(results)
        df_results = df_results.sort_values("mae")

        # 結果の統計情報をログ出力
        self._log_comparison_summary(df_results)

        return df_results

    def _compare_models_parallel(
        self,
        models_config: Dict,
        X_train: np.ndarray,
        X_test: np.ndarray,
        y_train: np.ndarray,
        y_test: np.ndarray,
        feature_names: List[str],
        data_hash: str,
        use_cross_validation: bool,
        cv_folds: int,
    ) -> List[ModelResult]:
        """並列処理によるモデル比較"""
        results = []

        with get_unified_system().execute_parallel(self.max_workers) as executor:
            # 各モデルの処理を並列実行
            futures = []
            for model_name, config in models_config.items():
                future = executor.submit(
                    self._evaluate_single_model,
                    model_name,
                    config,
                    X_train,
                    X_test,
                    y_train,
                    y_test,
                    feature_names,
                    data_hash,
                    use_cross_validation,
                    cv_folds,
                )
                futures.append(future)

            # 結果を収集
            for future in futures:
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                except Exception as e:
                    self.logger.error(f"❌ 並列処理エラー: {e}")
                    continue

        return results

    def _compare_models_sequential(
        self,
        models_config: Dict,
        X_train: np.ndarray,
        X_test: np.ndarray,
        y_train: np.ndarray,
        y_test: np.ndarray,
        feature_names: List[str],
        data_hash: str,
        use_cross_validation: bool,
        cv_folds: int,
    ) -> List[ModelResult]:
        """逐次処理によるモデル比較"""
        results = []

        for model_name, config in models_config.items():
            try:
                result = self._evaluate_single_model(
                    model_name,
                    config,
                    X_train,
                    X_test,
                    y_train,
                    y_test,
                    feature_names,
                    data_hash,
                    use_cross_validation,
                    cv_folds,
                )
                if result:
                    results.append(result)
            except Exception as e:
                self.logger.error(f"❌ モデル {model_name} の評価エラー: {e}")
                continue

        return results

    def _evaluate_single_model(
        self,
        model_name: str,
        config: Dict,
        X_train: np.ndarray,
        X_test: np.ndarray,
        y_train: np.ndarray,
        y_test: np.ndarray,
        feature_names: List[str],
        data_hash: str,
        use_cross_validation: bool,
        cv_folds: int,
    ) -> Optional[ModelResult]:
        """単一モデルの評価"""
        try:
            self.logger.info(f"🔧 モデル評価開始: {model_name}")

            # モデル作成
            model_type = config.get("type", model_name)
            params = config.get("params", {})

            # キャッシュからモデルを取得
            cached_model = None
            if self.model_cache:
                cached_model = self.model_cache.get_cached_model(
                    model_name, X_train, y_train, params
                )

            if cached_model:
                model = cached_model
                self.logger.debug(f"📋 キャッシュからモデル取得: {model_name}")
            else:
                # モデル作成
                model = self._create_model(model_type, params)

                # 学習時間を測定
                train_start = time.time()
                model.fit(X_train, y_train)
                training_time = time.time() - train_start

                # モデルをキャッシュに保存
                if self.model_cache:
                    self.model_cache.save_model(
                        model, model_name, X_train, y_train, params
                    )
                training_time = 0.0  # キャッシュから取得した場合

            # 予測時間を測定
            pred_start = time.time()
            y_pred = model.predict(X_test)
            prediction_time = time.time() - pred_start

            # メトリクス計算（キャッシュ活用）
            metrics = self._calculate_metrics_cached(
                y_test, y_pred, data_hash, model_name
            )

            # クロスバリデーション（オプション）
            cv_scores = None
            if use_cross_validation:
                cv_scores = self._calculate_cross_validation(
                    model, X_train, y_train, cv_folds
                )

            # 特徴量重要度（可能な場合）
            feature_importance = None
            if feature_names and hasattr(model, "feature_importances_"):
                feature_importance = dict(
                    zip(feature_names, model.feature_importances_)
                )

            # メモリ使用量の推定
            memory_usage = self._estimate_memory_usage(model, X_train, X_test)

            result = ModelResult(
                model_name=model_name,
                model_type=model_type,
                mae=metrics["mae"],
                mse=metrics["mse"],
                rmse=metrics["rmse"],
                r2=metrics["r2"],
                training_time=training_time,
                prediction_time=prediction_time,
                memory_usage=memory_usage,
                cross_val_scores=cv_scores,
                feature_importance=feature_importance,
            )

            self.logger.info(
                f"✅ {model_name} 完了: MAE={metrics['mae']:.4f}, 時間={training_time:.2f}s"
            )
            return result

        except Exception as e:
            self.system.log_error(
                e,
                f"{model_name}評価エラー",
                additional_info={
                    "model_type": model_type,
                    "params": params,
                    "X_train_shape": X_train.shape,
                    "y_train_shape": y_train.shape,
                },
            )
            self.logger.error(f"❌ モデル {model_name} でエラー: {e}")
            return None

    def _create_model(self, model_type: str, params: Dict) -> Any:
        """モデルを作成"""
        from model_factory import ModelFactory

        factory = ModelFactory()
        return factory.create_model(model_type, params)

    def _calculate_metrics_cached(
        self, y_test: np.ndarray, y_pred: np.ndarray, data_hash: str, model_name: str
    ) -> Dict[str, float]:
        """キャッシュを活用したメトリクス計算"""
        # キャッシュキーを生成
        cache_key = f"{data_hash}_{model_name}_{hash(y_test.tobytes())}_{hash(y_pred.tobytes())}"

        if cache_key in self.metrics_cache:
            self.logger.debug(f"📋 メトリクスキャッシュヒット: {model_name}")
            return self.metrics_cache[cache_key]

        # メトリクス計算
        metrics = {
            "mae": mean_absolute_error(y_test, y_pred),
            "mse": mean_squared_error(y_test, y_pred),
            "rmse": np.sqrt(mean_squared_error(y_test, y_pred)),
            "r2": r2_score(y_test, y_pred),
        }

        # キャッシュに保存
        self.metrics_cache[cache_key] = metrics
        return metrics

    def _calculate_cross_validation(
        self, model: Any, X: np.ndarray, y: np.ndarray, cv_folds: int
    ) -> List[float]:
        """クロスバリデーションスコアを計算"""
        try:
            scores = cross_val_score(
                model, X, y, cv=cv_folds, scoring="neg_mean_absolute_error"
            )
            return (-scores).tolist()  # 負の値を正の値に変換
        except Exception as e:
            self.logger.warning(f"⚠️ クロスバリデーションエラー: {e}")
            return None

    def _estimate_memory_usage(
        self, model: Any, X_train: np.ndarray, X_test: np.ndarray
    ) -> float:
        """メモリ使用量を推定（MB）"""
        try:
            import sys

            model_size = sys.getsizeof(model)
            data_size = (X_train.nbytes + X_test.nbytes) / 1024 / 1024
            return model_size / 1024 / 1024 + data_size
        except:
            return 0.0

    def _generate_data_hash(self, X: np.ndarray, y: np.ndarray) -> str:
        """データのハッシュを生成"""
        combined = np.concatenate([X.flatten(), y.flatten()])
        return hashlib.md5(combined.tobytes()).hexdigest()

    def _log_comparison_summary(self, df_results: pd.DataFrame):
        """比較結果のサマリーをログ出力"""
        if df_results.empty:
            return

        self.logger.info("📊 モデル比較結果サマリー:")
        self.logger.info(
            f"  🏆 最優秀モデル: {df_results.iloc[0]['model_name']} (MAE: {df_results.iloc[0]['mae']:.4f})"
        )
        self.logger.info(f"  📈 平均MAE: {df_results['mae'].mean():.4f}")
        self.logger.info(
            f"  ⏱️ 平均学習時間: {df_results['training_time'].mean():.2f}秒"
        )
        self.logger.info(
            f"  💾 平均メモリ使用量: {df_results['memory_usage'].mean():.1f}MB"
        )

        # 上位3モデルを表示
        top_3 = df_results.head(3)
        self.logger.info("🥇 上位3モデル:")
        for i, (_, row) in enumerate(top_3.iterrows(), 1):
            self.logger.info(
                f"  {i}. {row['model_name']}: MAE={row['mae']:.4f}, R²={row['r2']:.4f}"
            )

    def clear_all_caches(self):
        """全てのキャッシュをクリア"""
        if self.model_cache:
            self.model_cache.clear_cache()
        self.feature_cache.cache.clear()
        self.metrics_cache.clear()
        self.logger.info("🧹 全てのキャッシュをクリアしました")


class BatchModelProcessor:
    """バッチモデル処理クラス"""

    def __init__(self, comparator: OptimizedModelComparator):
        self.comparator = comparator
        self.logger = logging.getLogger(__name__)

    def process_multiple_datasets(
        self,
        datasets: List[Tuple[str, np.ndarray, np.ndarray, np.ndarray, np.ndarray]],
        models_config: Dict[str, Dict],
        output_dir: str = "batch_results",
    ) -> Dict[str, pd.DataFrame]:
        """複数データセットの一括処理"""
        self.logger.info(f"📊 バッチ処理開始: {len(datasets)}データセット")

        os.makedirs(output_dir, exist_ok=True)
        results = {}

        for dataset_name, X_train, X_test, y_train, y_test in datasets:
            try:
                self.logger.info(f"🔧 データセット処理: {dataset_name}")

                # モデル比較実行
                comparison_results = self.comparator.compare_models_optimized(
                    models_config, X_train, X_test, y_train, y_test
                )

                # 結果を保存
                output_file = os.path.join(output_dir, f"{dataset_name}_results.csv")
                comparison_results.to_csv(output_file, index=False)

                results[dataset_name] = comparison_results
                self.logger.info(f"✅ {dataset_name} 完了: {output_file}")

            except Exception as e:
                self.logger.error(f"❌ {dataset_name} 処理エラー: {e}")
                continue

        self.logger.info(f"✅ バッチ処理完了: {len(results)}/{len(datasets)} 成功")
        return results


def create_optimized_comparator(
    max_workers: int = None, use_cache: bool = True
) -> OptimizedModelComparator:
    """最適化されたモデル比較器を作成"""
    return OptimizedModelComparator(max_workers=max_workers, use_cache=use_cache)


if __name__ == "__main__":
    # テスト実行
    logging.basicConfig(level=logging.INFO)

    # サンプルデータ生成
    from sklearn.datasets import make_regression
    from sklearn.model_selection import train_test_split

    X, y = make_regression(n_samples=1000, n_features=10, noise=0.1, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # モデル設定
    models_config = {
        "random_forest": {"type": "random_forest", "params": {"n_estimators": 100}},
        "xgboost": {"type": "xgboost", "params": {"n_estimators": 100}},
        "linear_regression": {"type": "linear_regression", "params": {}},
        "ridge": {"type": "ridge", "params": {"alpha": 1.0}},
    }

    # 最適化された比較器を作成
    comparator = create_optimized_comparator(use_cache=True)

    # モデル比較実行
    results = comparator.compare_models_optimized(
        models_config, X_train, X_test, y_train, y_test, use_parallel=True
    )

    print("\n📊 比較結果:")
    print(results[["model_name", "mae", "r2", "training_time"]].to_string(index=False))
