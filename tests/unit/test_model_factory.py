"""
モデルファクトリーモジュールのユニットテスト
"""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from model_factory import ModelFactory, ModelEvaluator, ModelComparator

class TestModelFactory:
    """ModelFactoryクラスのテスト"""
    
    def test_init(self):
        """初期化テスト"""
        factory = ModelFactory()
        assert factory is not None
        assert hasattr(factory, 'available_models')
        assert hasattr(factory, 'logger')
    
    def test_get_available_models(self):
        """利用可能なモデル一覧の取得テスト"""
        factory = ModelFactory()
        models = factory.get_available_models()
        
        assert isinstance(models, list)
        assert len(models) > 0
        assert 'random_forest' in models
        assert 'xgboost' in models
        assert 'linear_regression' in models
    
    def test_create_model_random_forest(self):
        """Random Forestモデルの作成テスト"""
        factory = ModelFactory()
        model = factory.create_model('random_forest')
        
        assert model is not None
        assert hasattr(model, 'fit')
        assert hasattr(model, 'predict')
    
    def test_create_model_random_forest_with_params(self):
        """パラメータ付きRandom Forestモデルの作成テスト"""
        factory = ModelFactory()
        params = {'n_estimators': 100, 'max_depth': 10}
        model = factory.create_model('random_forest', params)
        
        assert model is not None
        assert model.n_estimators == 100
        assert model.max_depth == 10
    
    def test_create_model_xgboost(self):
        """XGBoostモデルの作成テスト"""
        factory = ModelFactory()
        model = factory.create_model('xgboost')
        
        assert model is not None
        assert hasattr(model, 'fit')
        assert hasattr(model, 'predict')
    
    def test_create_model_linear_regression(self):
        """線形回帰モデルの作成テスト"""
        factory = ModelFactory()
        model = factory.create_model('linear_regression')
        
        assert model is not None
        assert hasattr(model, 'fit')
        assert hasattr(model, 'predict')
    
    def test_create_model_ridge(self):
        """Ridge回帰モデルの作成テスト"""
        factory = ModelFactory()
        model = factory.create_model('ridge')
        
        assert model is not None
        assert hasattr(model, 'fit')
        assert hasattr(model, 'predict')
    
    def test_create_model_lasso(self):
        """Lasso回帰モデルの作成テスト"""
        factory = ModelFactory()
        model = factory.create_model('lasso')
        
        assert model is not None
        assert hasattr(model, 'fit')
        assert hasattr(model, 'predict')
    
    def test_create_model_svr(self):
        """SVRモデルの作成テスト"""
        factory = ModelFactory()
        model = factory.create_model('svr')
        
        assert model is not None
        assert hasattr(model, 'fit')
        assert hasattr(model, 'predict')
    
    def test_create_model_invalid_type(self):
        """無効なモデルタイプのテスト"""
        factory = ModelFactory()
        
        with pytest.raises(ValueError, match="サポートされていないモデルタイプ"):
            factory.create_model('invalid_model')
    
    def test_create_model_with_none_params(self):
        """Noneパラメータでのモデル作成テスト"""
        factory = ModelFactory()
        model = factory.create_model('random_forest', None)
        
        assert model is not None
    
    def test_create_model_with_empty_params(self):
        """空のパラメータでのモデル作成テスト"""
        factory = ModelFactory()
        model = factory.create_model('random_forest', {})
        
        assert model is not None

class TestModelEvaluator:
    """ModelEvaluatorクラスのテスト"""
    
    def test_init(self):
        """初期化テスト"""
        evaluator = ModelEvaluator()
        assert evaluator is not None
        assert hasattr(evaluator, 'logger')
    
    def test_evaluate_model_basic(self, sample_stock_data):
        """基本的なモデル評価テスト"""
        evaluator = ModelEvaluator()
        factory = ModelFactory()
        
        # サンプルデータを準備
        X = sample_stock_data[['Open', 'High', 'Low', 'Volume']].dropna()
        y = sample_stock_data['Close'].dropna()
        
        # データサイズを揃える
        min_len = min(len(X), len(y))
        X = X.iloc[:min_len]
        y = y.iloc[:min_len]
        
        if len(X) > 0:
            model = factory.create_model('linear_regression')
            model.fit(X, y)
            
            metrics = evaluator.evaluate_model(model, X, y)
            
            assert isinstance(metrics, dict)
            assert 'mae' in metrics
            assert 'mse' in metrics
            assert 'rmse' in metrics
            assert 'r2' in metrics
            
            # メトリクスの値が適切な範囲であることを確認
            assert metrics['mae'] >= 0
            assert metrics['mse'] >= 0
            assert metrics['rmse'] >= 0
    
    def test_evaluate_model_with_predictions(self, sample_stock_data):
        """予測値を使ったモデル評価テスト"""
        evaluator = ModelEvaluator()
        factory = ModelFactory()
        
        # サンプルデータを準備
        X = sample_stock_data[['Open', 'High', 'Low', 'Volume']].dropna()
        y = sample_stock_data['Close'].dropna()
        
        # データサイズを揃える
        min_len = min(len(X), len(y))
        X = X.iloc[:min_len]
        y = y.iloc[:min_len]
        
        if len(X) > 0:
            model = factory.create_model('linear_regression')
            model.fit(X, y)
            predictions = model.predict(X)
            
            metrics = evaluator.evaluate_model(model, X, y, predictions)
            
            assert isinstance(metrics, dict)
            assert 'mae' in metrics
            assert 'mse' in metrics
            assert 'rmse' in metrics
            assert 'r2' in metrics
    
    def test_evaluate_model_empty_data(self):
        """空のデータでの評価テスト"""
        evaluator = ModelEvaluator()
        factory = ModelFactory()
        
        X = pd.DataFrame()
        y = pd.Series(dtype=float)
        
        model = factory.create_model('linear_regression')
        
        with pytest.raises(ValueError):
            evaluator.evaluate_model(model, X, y)
    
    def test_evaluate_model_mismatched_data(self):
        """データサイズが一致しない場合のテスト"""
        evaluator = ModelEvaluator()
        factory = ModelFactory()
        
        X = pd.DataFrame({'feature1': [1, 2, 3]})
        y = pd.Series([1, 2])  # サイズが異なる
        
        model = factory.create_model('linear_regression')
        
        with pytest.raises(ValueError):
            evaluator.evaluate_model(model, X, y)

class TestModelComparator:
    """ModelComparatorクラスのテスト"""
    
    def test_init(self):
        """初期化テスト"""
        comparator = ModelComparator()
        assert comparator is not None
        assert hasattr(comparator, 'logger')
    
    def test_compare_models_basic(self, sample_stock_data):
        """基本的なモデル比較テスト"""
        comparator = ModelComparator()
        factory = ModelFactory()
        
        # サンプルデータを準備
        X = sample_stock_data[['Open', 'High', 'Low', 'Volume']].dropna()
        y = sample_stock_data['Close'].dropna()
        
        # データサイズを揃える
        min_len = min(len(X), len(y))
        X = X.iloc[:min_len]
        y = y.iloc[:min_len]
        
        if len(X) > 0:
            models_config = {
                'linear_regression': {},
                'ridge': {'alpha': 1.0}
            }
            
            results = comparator.compare_models(models_config, X, y)
            
            assert isinstance(results, pd.DataFrame)
            assert 'linear_regression' in results['model_name'].values
            assert 'ridge' in results
            
            # 各モデルの結果に必要なメトリクスが含まれていることを確認
            for model_name, metrics in results.items():
                assert 'mae' in metrics
                assert 'mse' in metrics
                assert 'rmse' in metrics
                assert 'r2' in metrics
    
    def test_compare_models_single_model(self, sample_stock_data):
        """単一モデルの比較テスト"""
        comparator = ModelComparator()
        
        # サンプルデータを準備
        X = sample_stock_data[['Open', 'High', 'Low', 'Volume']].dropna()
        y = sample_stock_data['Close'].dropna()
        
        # データサイズを揃える
        min_len = min(len(X), len(y))
        X = X.iloc[:min_len]
        y = y.iloc[:min_len]
        
        if len(X) > 0:
            models_config = {
                'linear_regression': {}
            }
            
            results = comparator.compare_models(models_config, X, y)
            
            assert isinstance(results, pd.DataFrame)
            assert len(results) == 1
            assert 'linear_regression' in results['model_name'].values
    
    def test_compare_models_empty_config(self):
        """空の設定での比較テスト"""
        comparator = ModelComparator()
        X = pd.DataFrame({'feature1': [1, 2, 3]})
        y = pd.Series([1, 2, 3])
        
        results = comparator.compare_models({}, X, y)
        assert results.empty
    
    def test_compare_models_invalid_model(self, sample_stock_data):
        """無効なモデル設定での比較テスト"""
        comparator = ModelComparator()
        
        # サンプルデータを準備
        X = sample_stock_data[['Open', 'High', 'Low', 'Volume']].dropna()
        y = sample_stock_data['Close'].dropna()
        
        # データサイズを揃える
        min_len = min(len(X), len(y))
        X = X.iloc[:min_len]
        y = y.iloc[:min_len]
        
        if len(X) > 0:
            models_config = {
                'invalid_model': {}
            }
            
            results = comparator.compare_models(models_config, X, y)
            assert results.empty
    
    def test_get_best_model(self, sample_stock_data):
        """最良モデルの取得テスト"""
        comparator = ModelComparator()
        
        # サンプルデータを準備
        X = sample_stock_data[['Open', 'High', 'Low', 'Volume']].dropna()
        y = sample_stock_data['Close'].dropna()
        
        # データサイズを揃える
        min_len = min(len(X), len(y))
        X = X.iloc[:min_len]
        y = y.iloc[:min_len]
        
        if len(X) > 0:
            models_config = {
                'linear_regression': {},
                'ridge': {'alpha': 1.0}
            }
            
            results = comparator.compare_models(models_config, X, y)
            best_model_name = comparator.get_best_model(results, metric='mae')
            
            assert best_model_name in results['model_name'].values
    
    def test_get_best_model_invalid_metric(self, sample_stock_data):
        """無効なメトリクスでの最良モデル取得テスト"""
        comparator = ModelComparator()
        
        # サンプルデータを準備
        X = sample_stock_data[['Open', 'High', 'Low', 'Volume']].dropna()
        y = sample_stock_data['Close'].dropna()
        
        # データサイズを揃える
        min_len = min(len(X), len(y))
        X = X.iloc[:min_len]
        y = y.iloc[:min_len]
        
        if len(X) > 0:
            models_config = {
                'linear_regression': {}
            }
            
            results = comparator.compare_models(models_config, X, y)
            
            best_model = comparator.get_best_model(results, metric='invalid_metric')
            assert best_model is not None
