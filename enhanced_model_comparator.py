#!/usr/bin/env python3
"""
強化されたモデル比較システム
重複計算を大幅に削減し、高度なキャッシュ機能と並列処理を活用
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple, Any, Callable
from functools import lru_cache
import joblib
import hashlib
import os
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp
from sklearn.model_selection import cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import time
from dataclasses import dataclass
from unified_system import UnifiedSystem
import psutil
import gc

logger = logging.getLogger(__name__)


@dataclass
class EnhancedModelResult:
    """強化されたモデル結果データクラス"""
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
    cache_hit: bool = False
    parallel_processed: bool = False


class IntelligentCacheManager:
    """インテリジェントキャッシュ管理システム"""
    
    def __init__(self, cache_dir: str = "enhanced_model_cache", max_cache_size_mb: int = 2048):
        self.cache_dir = cache_dir
        self.max_cache_size_mb = max_cache_size_mb
        self.cache_stats = {"hits": 0, "misses": 0, "evictions": 0}
        self.cache_metadata = {}
        self.system = UnifiedSystem("IntelligentCacheManager")
        self.logger = logging.getLogger(__name__)
        
        os.makedirs(cache_dir, exist_ok=True)
    
    def _generate_enhanced_cache_key(self, model_name: str, X_hash: str, y_hash: str, 
                                   params: Dict, feature_names: List[str] = None) -> str:
        """強化されたキャッシュキーを生成"""
        feature_hash = hashlib.md5(str(feature_names).encode()).hexdigest()[:8] if feature_names else "none"
        key_string = f"{model_name}_{X_hash}_{y_hash}_{feature_hash}_{str(sorted(params.items()))}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _generate_data_hash(self, data: np.ndarray) -> str:
        """データのハッシュを生成（最適化版）"""
        # データのサンプリングでハッシュ計算を高速化
        if len(data) > 1000:
            sample_indices = np.random.choice(len(data), 1000, replace=False)
            sample_data = data[sample_indices]
        else:
            sample_data = data
        
        return hashlib.md5(sample_data.tobytes()).hexdigest()
    
    def get_cached_model(self, model_name: str, X_train: np.ndarray, y_train: np.ndarray, 
                        params: Dict, feature_names: List[str] = None) -> Optional[Any]:
        """キャッシュからモデルを取得（強化版）"""
        try:
            X_hash = self._generate_data_hash(X_train)
            y_hash = self._generate_data_hash(y_train)
            cache_key = self._generate_enhanced_cache_key(model_name, X_hash, y_hash, params, feature_names)
            cache_file = os.path.join(self.cache_dir, f"{cache_key}.joblib")
            
            if os.path.exists(cache_file):
                # ファイルの更新時間をチェック
                file_mtime = os.path.getmtime(cache_file)
                if file_mtime > time.time() - 3600:  # 1時間以内のキャッシュのみ有効
                    self.cache_stats["hits"] += 1
                    self.logger.debug(f"📋 キャッシュヒット: {model_name}")
                    return joblib.load(cache_file)
                else:
                    # 古いキャッシュを削除
                    os.remove(cache_file)
                    self.cache_stats["evictions"] += 1
            
            self.cache_stats["misses"] += 1
            return None
            
        except Exception as e:
            self.logger.warning(f"⚠️ キャッシュ取得エラー: {e}")
            self.cache_stats["misses"] += 1
            return None
    
    def save_model(self, model: Any, model_name: str, X_train: np.ndarray, y_train: np.ndarray, 
                  params: Dict, feature_names: List[str] = None):
        """モデルをキャッシュに保存（強化版）"""
        try:
            X_hash = self._generate_data_hash(X_train)
            y_hash = self._generate_data_hash(y_train)
            cache_key = self._generate_enhanced_cache_key(model_name, X_hash, y_hash, params, feature_names)
            cache_file = os.path.join(self.cache_dir, f"{cache_key}.joblib")
            
            # キャッシュサイズ制限チェック
            if self._check_cache_size_limit():
                self._evict_oldest_cache()
            
            joblib.dump(model, cache_file)
            
            # メタデータを保存
            self.cache_metadata[cache_key] = {
                "model_name": model_name,
                "timestamp": time.time(),
                "size_mb": os.path.getsize(cache_file) / 1024 / 1024
            }
            
            self.logger.debug(f"💾 モデルをキャッシュに保存: {model_name}")
            
        except Exception as e:
            self.logger.warning(f"⚠️ キャッシュ保存エラー: {e}")
    
    def _check_cache_size_limit(self) -> bool:
        """キャッシュサイズ制限をチェック"""
        total_size = 0
        for file in os.listdir(self.cache_dir):
            if file.endswith('.joblib'):
                total_size += os.path.getsize(os.path.join(self.cache_dir, file))
        
        return (total_size / 1024 / 1024) > self.max_cache_size_mb
    
    def _evict_oldest_cache(self):
        """最も古いキャッシュを削除"""
        if not self.cache_metadata:
            return
        
        oldest_key = min(self.cache_metadata.keys(), 
                        key=lambda k: self.cache_metadata[k]["timestamp"])
        
        cache_file = os.path.join(self.cache_dir, f"{oldest_key}.joblib")
        if os.path.exists(cache_file):
            os.remove(cache_file)
            del self.cache_metadata[oldest_key]
            self.cache_stats["evictions"] += 1
            self.logger.debug(f"🗑️ 古いキャッシュを削除: {oldest_key}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """キャッシュ統計を取得"""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (self.cache_stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "hits": self.cache_stats["hits"],
            "misses": self.cache_stats["misses"],
            "evictions": self.cache_stats["evictions"],
            "hit_rate": hit_rate,
            "total_requests": total_requests,
            "cache_files": len(self.cache_metadata)
        }


class ParallelModelProcessor:
    """並列モデル処理クラス"""
    
    def __init__(self, max_workers: int = None, use_processes: bool = True):
        self.max_workers = max_workers or min(4, mp.cpu_count())
        self.use_processes = use_processes
        self.system = UnifiedSystem("ParallelModelProcessor")
        self.logger = logging.getLogger(__name__)
    
    def process_models_parallel(self, models_config: Dict, X_train: np.ndarray, X_test: np.ndarray,
                               y_train: np.ndarray, y_test: np.ndarray, feature_names: List[str] = None,
                               cache_manager: IntelligentCacheManager = None) -> List[EnhancedModelResult]:
        """モデルを並列処理で評価"""
        self.logger.info(f"🚀 並列モデル処理開始 (ワーカー数: {self.max_workers}, プロセス: {self.use_processes})")
        
        start_time = time.time()
        
        # モデルを並列処理
        if self.use_processes:
            results = self._process_models_with_processes(
                models_config, X_train, X_test, y_train, y_test, feature_names, cache_manager
            )
        else:
            results = self._process_models_with_threads(
                models_config, X_train, X_test, y_train, y_test, feature_names, cache_manager
            )
        
        processing_time = time.time() - start_time
        self.logger.info(f"✅ 並列モデル処理完了: {processing_time:.2f}秒")
        
        return results
    
    def _process_models_with_processes(self, models_config: Dict, X_train: np.ndarray, X_test: np.ndarray,
                                     y_train: np.ndarray, y_test: np.ndarray, feature_names: List[str],
                                     cache_manager: IntelligentCacheManager) -> List[EnhancedModelResult]:
        """プロセス並列処理でモデルを評価"""
        results = []
        
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            
            for model_name, config in models_config.items():
                future = executor.submit(
                    self._evaluate_single_model_isolated,
                    model_name, config, X_train, X_test, y_train, y_test, feature_names
                )
                futures.append((model_name, future))
            
            # 結果を収集
            for model_name, future in futures:
                try:
                    result = future.result(timeout=300)  # 5分タイムアウト
                    if result:
                        results.append(result)
                except Exception as e:
                    self.logger.error(f"❌ モデル {model_name} の処理エラー: {e}")
        
        return results
    
    def _process_models_with_threads(self, models_config: Dict, X_train: np.ndarray, X_test: np.ndarray,
                                   y_train: np.ndarray, y_test: np.ndarray, feature_names: List[str],
                                   cache_manager: IntelligentCacheManager) -> List[EnhancedModelResult]:
        """スレッド並列処理でモデルを評価"""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            
            for model_name, config in models_config.items():
                future = executor.submit(
                    self._evaluate_single_model_with_cache,
                    model_name, config, X_train, X_test, y_train, y_test, feature_names, cache_manager
                )
                futures.append((model_name, future))
            
            # 結果を収集
            for model_name, future in futures:
                try:
                    result = future.result(timeout=300)  # 5分タイムアウト
                    if result:
                        results.append(result)
                except Exception as e:
                    self.logger.error(f"❌ モデル {model_name} の処理エラー: {e}")
        
        return results
    
    def _evaluate_single_model_isolated(self, model_name: str, config: Dict, X_train: np.ndarray,
                                       X_test: np.ndarray, y_train: np.ndarray, y_test: np.ndarray,
                                       feature_names: List[str]) -> Optional[EnhancedModelResult]:
        """単一モデルの評価（分離プロセス用）"""
        # この関数は分離プロセスで実行されるため、キャッシュは使用できない
        try:
            from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
            from sklearn.linear_model import LinearRegression, Ridge, Lasso
            from sklearn.svm import SVR
            from sklearn.neighbors import KNeighborsRegressor
            
            # モデル作成
            model_type = config.get("type", model_name)
            params = config.get("params", {})
            
            model = self._create_model(model_type, params)
            
            # 学習時間を測定
            train_start = time.time()
            model.fit(X_train, y_train)
            training_time = time.time() - train_start
            
            # 予測時間を測定
            pred_start = time.time()
            y_pred = model.predict(X_test)
            prediction_time = time.time() - pred_start
            
            # メトリクス計算
            mae = mean_absolute_error(y_test, y_pred)
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            r2 = r2_score(y_test, y_pred)
            
            # メモリ使用量
            memory_usage = psutil.Process().memory_info().rss / 1024 / 1024
            
            return EnhancedModelResult(
                model_name=model_name,
                model_type=model_type,
                mae=mae,
                mse=mse,
                rmse=rmse,
                r2=r2,
                training_time=training_time,
                prediction_time=prediction_time,
                memory_usage=memory_usage,
                parallel_processed=True
            )
            
        except Exception as e:
            self.logger.error(f"❌ モデル {model_name} の評価エラー: {e}")
            return None
    
    def _evaluate_single_model_with_cache(self, model_name: str, config: Dict, X_train: np.ndarray,
                                         X_test: np.ndarray, y_train: np.ndarray, y_test: np.ndarray,
                                         feature_names: List[str], cache_manager: IntelligentCacheManager) -> Optional[EnhancedModelResult]:
        """単一モデルの評価（キャッシュ付き）"""
        try:
            model_type = config.get("type", model_name)
            params = config.get("params", {})
            
            # キャッシュからモデルを取得
            cached_model = cache_manager.get_cached_model(model_name, X_train, y_train, params, feature_names)
            cache_hit = cached_model is not None
            
            if cached_model:
                model = cached_model
                training_time = 0.0  # キャッシュから取得した場合
                self.logger.debug(f"📋 キャッシュからモデル取得: {model_name}")
            else:
                # モデル作成
                model = self._create_model(model_type, params)
                
                # 学習時間を測定
                train_start = time.time()
                model.fit(X_train, y_train)
                training_time = time.time() - train_start
                
                # モデルをキャッシュに保存
                cache_manager.save_model(model, model_name, X_train, y_train, params, feature_names)
            
            # 予測時間を測定
            pred_start = time.time()
            y_pred = model.predict(X_test)
            prediction_time = time.time() - pred_start
            
            # メトリクス計算
            mae = mean_absolute_error(y_test, y_pred)
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            r2 = r2_score(y_test, y_pred)
            
            # メモリ使用量
            memory_usage = psutil.Process().memory_info().rss / 1024 / 1024
            
            return EnhancedModelResult(
                model_name=model_name,
                model_type=model_type,
                mae=mae,
                mse=mse,
                rmse=rmse,
                r2=r2,
                training_time=training_time,
                prediction_time=prediction_time,
                memory_usage=memory_usage,
                cache_hit=cache_hit,
                parallel_processed=True
            )
            
        except Exception as e:
            self.logger.error(f"❌ モデル {model_name} の評価エラー: {e}")
            return None
    
    def _create_model(self, model_type: str, params: Dict) -> Any:
        """モデルを作成"""
        from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
        from sklearn.linear_model import LinearRegression, Ridge, Lasso
        from sklearn.svm import SVR
        from sklearn.neighbors import KNeighborsRegressor
        
        model_map = {
            "random_forest": RandomForestRegressor,
            "gradient_boosting": GradientBoostingRegressor,
            "linear_regression": LinearRegression,
            "ridge": Ridge,
            "lasso": Lasso,
            "svr": SVR,
            "knn": KNeighborsRegressor
        }
        
        if model_type not in model_map:
            raise ValueError(f"未対応のモデルタイプ: {model_type}")
        
        return model_map[model_type](**params)


class EnhancedModelComparator:
    """強化されたモデル比較クラス"""
    
    def __init__(self, max_workers: int = None, use_cache: bool = True, use_parallel: bool = True):
        self.max_workers = max_workers or min(4, mp.cpu_count())
        self.use_cache = use_cache
        self.use_parallel = use_parallel
        self.cache_manager = IntelligentCacheManager() if use_cache else None
        self.parallel_processor = ParallelModelProcessor(self.max_workers) if use_parallel else None
        self.system = UnifiedSystem("EnhancedModelComparator")
        self.logger = logging.getLogger(__name__)
    
    def compare_models_enhanced(self, models_config: Dict[str, Dict], X_train: np.ndarray,
                               X_test: np.ndarray, y_train: np.ndarray, y_test: np.ndarray,
                               feature_names: List[str] = None, use_cross_validation: bool = False,
                               cv_folds: int = 5) -> pd.DataFrame:
        """強化されたモデル比較"""
        self.logger.info(f"🚀 強化されたモデル比較開始 (並列: {self.use_parallel}, キャッシュ: {self.use_cache})")
        
        start_time = time.time()
        
        if self.use_parallel and self.parallel_processor:
            results = self.parallel_processor.process_models_parallel(
                models_config, X_train, X_test, y_train, y_test, feature_names, self.cache_manager
            )
        else:
            results = self._compare_models_sequential(
                models_config, X_train, X_test, y_train, y_test, feature_names, use_cross_validation, cv_folds
            )
        
        processing_time = time.time() - start_time
        self.logger.info(f"✅ モデル比較完了: {processing_time:.2f}秒")
        
        if not results:
            self.logger.warning("⚠️ 評価できたモデルがありません")
            return pd.DataFrame()
        
        # 結果をDataFrameに変換
        df_results = pd.DataFrame([{
            "model_name": r.model_name,
            "model_type": r.model_type,
            "mae": r.mae,
            "mse": r.mse,
            "rmse": r.rmse,
            "r2": r.r2,
            "training_time": r.training_time,
            "prediction_time": r.prediction_time,
            "memory_usage": r.memory_usage,
            "cache_hit": r.cache_hit,
            "parallel_processed": r.parallel_processed
        } for r in results])
        
        df_results = df_results.sort_values("mae")
        
        # 統計情報をログ出力
        self._log_comparison_summary(df_results)
        
        return df_results
    
    def _compare_models_sequential(self, models_config: Dict, X_train: np.ndarray, X_test: np.ndarray,
                                  y_train: np.ndarray, y_test: np.ndarray, feature_names: List[str],
                                  use_cross_validation: bool, cv_folds: int) -> List[EnhancedModelResult]:
        """逐次処理でモデルを比較"""
        results = []
        
        for model_name, config in models_config.items():
            try:
                result = self._evaluate_single_model_with_cache(
                    model_name, config, X_train, X_test, y_train, y_test, feature_names
                )
                if result:
                    results.append(result)
            except Exception as e:
                self.logger.error(f"❌ モデル {model_name} の評価エラー: {e}")
        
        return results
    
    def _evaluate_single_model_with_cache(self, model_name: str, config: Dict, X_train: np.ndarray,
                                         X_test: np.ndarray, y_train: np.ndarray, y_test: np.ndarray,
                                         feature_names: List[str]) -> Optional[EnhancedModelResult]:
        """単一モデルの評価（キャッシュ付き）"""
        if self.parallel_processor:
            return self.parallel_processor._evaluate_single_model_with_cache(
                model_name, config, X_train, X_test, y_train, y_test, feature_names, self.cache_manager
            )
        else:
            # キャッシュなしの評価
            return self.parallel_processor._evaluate_single_model_isolated(
                model_name, config, X_train, X_test, y_train, y_test, feature_names
            )
    
    def _log_comparison_summary(self, df_results: pd.DataFrame):
        """比較結果のサマリーをログ出力"""
        if df_results.empty:
            return
        
        best_model = df_results.iloc[0]
        cache_hits = df_results["cache_hit"].sum() if "cache_hit" in df_results.columns else 0
        parallel_processed = df_results["parallel_processed"].sum() if "parallel_processed" in df_results.columns else 0
        
        self.logger.info("📊 モデル比較結果サマリー:")
        self.logger.info(f"  🏆 最良モデル: {best_model['model_name']} (MAE: {best_model['mae']:.4f})")
        self.logger.info(f"  📋 キャッシュヒット: {cache_hits}/{len(df_results)}モデル")
        self.logger.info(f"  🚀 並列処理: {parallel_processed}/{len(df_results)}モデル")
        self.logger.info(f"  ⏱️ 平均学習時間: {df_results['training_time'].mean():.2f}秒")
        self.logger.info(f"  💾 平均メモリ使用量: {df_results['memory_usage'].mean():.1f}MB")
        
        # キャッシュ統計
        if self.cache_manager:
            cache_stats = self.cache_manager.get_cache_stats()
            self.logger.info(f"  📈 キャッシュヒット率: {cache_stats['hit_rate']:.1f}%")


def create_enhanced_model_comparator(max_workers: int = None, use_cache: bool = True, 
                                   use_parallel: bool = True) -> EnhancedModelComparator:
    """強化されたモデル比較システムを作成"""
    return EnhancedModelComparator(max_workers, use_cache, use_parallel)


if __name__ == "__main__":
    # テスト用のサンプルデータ
    import pandas as pd
    import numpy as np
    from sklearn.model_selection import train_test_split
    
    # サンプルデータ生成
    np.random.seed(42)
    n_samples = 1000
    n_features = 10
    
    X = np.random.randn(n_samples, n_features)
    y = np.random.randn(n_samples)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # モデル設定
    models_config = {
        "random_forest": {
            "type": "random_forest",
            "params": {"n_estimators": 100, "random_state": 42}
        },
        "gradient_boosting": {
            "type": "gradient_boosting",
            "params": {"n_estimators": 100, "random_state": 42}
        },
        "linear_regression": {
            "type": "linear_regression",
            "params": {}
        }
    }
    
    # 強化されたモデル比較システムのテスト
    comparator = create_enhanced_model_comparator(use_cache=True, use_parallel=True)
    
    results = comparator.compare_models_enhanced(
        models_config, X_train, X_test, y_train, y_test
    )
    
    print("📊 モデル比較結果:")
    print(results[["model_name", "mae", "r2", "training_time", "cache_hit"]].to_string())
