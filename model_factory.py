#!/usr/bin/env python3
"""
機械学習モデルファクトリー
複数のモデルを設定ファイルから選択・作成できるモジュール
"""

import logging
from typing import Dict, Any, Tuple, List
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.svm import SVR
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
import pandas as pd
import numpy as np


class ModelFactory:
    """機械学習モデルのファクトリークラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.available_models = {
            'random_forest': self._create_random_forest,
            'xgboost': self._create_xgboost,
            'linear_regression': self._create_linear_regression,
            'ridge': self._create_ridge,
            'lasso': self._create_lasso,
            'svr': self._create_svr
        }
    
    def get_available_models(self) -> List[str]:
        """利用可能なモデル一覧を取得"""
        return list(self.available_models.keys())
    
    def create_model(self, model_type: str, params: Dict[str, Any] = None):
        """
        指定されたタイプのモデルを作成
        
        Args:
            model_type (str): モデルタイプ
            params (Dict[str, Any]): モデルパラメータ
            
        Returns:
            機械学習モデルインスタンス
        """
        if model_type not in self.available_models:
            raise ValueError(f"サポートされていないモデルタイプ: {model_type}")
        
        params = params or {}
        self.logger.info(f"モデル作成: {model_type}, パラメータ: {params}")
        
        return self.available_models[model_type](params)
    
    def _create_random_forest(self, params: Dict[str, Any]):
        """ランダムフォレスト回帰モデルを作成"""
        default_params = {
            'n_estimators': 100,
            'random_state': 42,
            'max_depth': None,
            'min_samples_split': 2,
            'min_samples_leaf': 1
        }
        default_params.update(params)
        return RandomForestRegressor(**default_params)
    
    def _create_xgboost(self, params: Dict[str, Any]):
        """XGBoost回帰モデルを作成"""
        default_params = {
            'n_estimators': 100,
            'random_state': 42,
            'max_depth': 6,
            'learning_rate': 0.1,
            'subsample': 1.0,
            'colsample_bytree': 1.0
        }
        default_params.update(params)
        return xgb.XGBRegressor(**default_params)
    
    def _create_linear_regression(self, params: Dict[str, Any]):
        """線形回帰モデルを作成"""
        default_params = {
            'fit_intercept': True
        }
        default_params.update(params)
        return LinearRegression(**default_params)
    
    def _create_ridge(self, params: Dict[str, Any]):
        """Ridge回帰モデルを作成"""
        default_params = {
            'alpha': 1.0,
            'random_state': 42
        }
        default_params.update(params)
        return Ridge(**default_params)
    
    def _create_lasso(self, params: Dict[str, Any]):
        """Lasso回帰モデルを作成"""
        default_params = {
            'alpha': 1.0,
            'random_state': 42,
            'max_iter': 1000
        }
        default_params.update(params)
        return Lasso(**default_params)
    
    def _create_svr(self, params: Dict[str, Any]):
        """サポートベクター回帰モデルを作成"""
        default_params = {
            'kernel': 'rbf',
            'C': 1.0,
            'gamma': 'scale'
        }
        default_params.update(params)
        return SVR(**default_params)


class ModelEvaluator:
    """モデル評価クラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def evaluate_model(self, model, X_test, y_test, y_pred=None) -> Dict[str, float]:
        """
        モデルの評価を行う
        
        Args:
            model: 学習済みモデル
            X_test: テストデータの特徴量
            y_test: テストデータの正解値
            y_pred: 予測値（Noneの場合は自動で予測）
            
        Returns:
            Dict[str, float]: 評価指標辞書
        """
        if y_pred is None:
            y_pred = model.predict(X_test)
        
        metrics = {
            'mae': mean_absolute_error(y_test, y_pred),
            'mse': mean_squared_error(y_test, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
            'r2': r2_score(y_test, y_pred)
        }
        
        self.logger.info(f"モデル評価結果: {metrics}")
        return metrics
    
    def get_feature_importance(self, model, feature_names: List[str]) -> pd.DataFrame:
        """
        特徴量重要度を取得
        
        Args:
            model: 学習済みモデル
            feature_names: 特徴量名のリスト
            
        Returns:
            pd.DataFrame: 特徴量重要度DataFrame
        """
        try:
            if hasattr(model, 'feature_importances_'):
                importance = model.feature_importances_
            elif hasattr(model, 'coef_'):
                # 線形モデルの場合は係数の絶対値を重要度とする
                importance = np.abs(model.coef_)
            else:
                self.logger.warning(f"モデル {type(model).__name__} は特徴量重要度をサポートしていません")
                return pd.DataFrame()
            
            df = pd.DataFrame({
                'feature': feature_names,
                'importance': importance
            }).sort_values('importance', ascending=False)
            
            return df
            
        except Exception as e:
            self.logger.error(f"特徴量重要度の取得に失敗: {e}")
            return pd.DataFrame()


class ModelComparator:
    """複数モデル比較クラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.factory = ModelFactory()
        self.evaluator = ModelEvaluator()
    
    def compare_models(self, models_config: Dict[str, Dict], X_train, X_test, y_train, y_test, 
                      feature_names: List[str]) -> pd.DataFrame:
        """
        複数モデルの性能比較
        
        Args:
            models_config: モデル設定辞書
            X_train, X_test, y_train, y_test: 学習・テストデータ
            feature_names: 特徴量名リスト
            
        Returns:
            pd.DataFrame: 比較結果DataFrame
        """
        results = []
        
        for model_name, config in models_config.items():
            try:
                self.logger.info(f"モデル比較開始: {model_name}")
                
                # モデル作成・学習
                model_type = config.get('type', model_name)
                params = config.get('params', {})
                
                model = self.factory.create_model(model_type, params)
                model.fit(X_train, y_train)
                
                # 予測・評価
                y_pred = model.predict(X_test)
                metrics = self.evaluator.evaluate_model(model, X_test, y_test, y_pred)
                
                # 結果記録
                result = {
                    'model_name': model_name,
                    'model_type': model_type,
                    **metrics
                }
                results.append(result)
                
                self.logger.info(f"モデル {model_name} 完了: MAE={metrics['mae']:.4f}")
                
            except Exception as e:
                self.logger.error(f"モデル {model_name} でエラー: {e}")
                continue
        
        if not results:
            self.logger.warning("評価できたモデルがありません")
            return pd.DataFrame()
        
        df_results = pd.DataFrame(results).sort_values('mae')
        return df_results


def get_default_models_config() -> Dict[str, Dict]:
    """デフォルトのモデル設定を取得"""
    return {
        'random_forest': {
            'type': 'random_forest',
            'params': {
                'n_estimators': 100,
                'max_depth': 10,
                'random_state': 42
            }
        },
        'xgboost': {
            'type': 'xgboost',
            'params': {
                'n_estimators': 100,
                'max_depth': 6,
                'learning_rate': 0.1,
                'random_state': 42
            }
        },
        'linear_regression': {
            'type': 'linear_regression',
            'params': {}
        },
        'ridge': {
            'type': 'ridge',
            'params': {
                'alpha': 1.0,
                'random_state': 42
            }
        }
    }


if __name__ == "__main__":
    # テスト実行
    logging.basicConfig(level=logging.INFO)
    
    factory = ModelFactory()
    print("利用可能なモデル:")
    for model in factory.get_available_models():
        print(f"  - {model}")
    
    # サンプルデータで各モデルをテスト
    from sklearn.datasets import make_regression
    from sklearn.model_selection import train_test_split
    
    X, y = make_regression(n_samples=1000, n_features=10, noise=0.1, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 各モデルをテスト
    for model_type in factory.get_available_models():
        try:
            model = factory.create_model(model_type)
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)
            print(f"  {model_type}: MAE = {mae:.4f}")
        except Exception as e:
            print(f"  {model_type}: エラー - {e}")
