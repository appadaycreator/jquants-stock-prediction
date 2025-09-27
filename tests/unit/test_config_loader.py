"""
設定ローダーモジュールのユニットテスト
"""
import pytest
import yaml
import os
import tempfile
from unittest.mock import patch, mock_open
from config_loader import ConfigLoader

class TestConfigLoader:
    """ConfigLoaderクラスのテスト"""
    
    def test_init_with_existing_config(self):
        """既存の設定ファイルでの初期化テスト"""
        # 一時的な設定ファイルを作成
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_data = {
                'preprocessing': {
                    'input_file': 'test.csv',
                    'output_file': 'processed.csv'
                },
                'prediction': {
                    'features': ['feature1', 'feature2'],
                    'target': 'target'
                }
            }
            yaml.dump(config_data, f)
            config_path = f.name
        
        try:
            loader = ConfigLoader(config_path)
            assert loader is not None
            assert loader.config is not None
            assert 'preprocessing' in loader.config
            assert 'prediction' in loader.config
        finally:
            os.unlink(config_path)
    
    def test_init_with_nonexistent_config(self):
        """存在しない設定ファイルでの初期化テスト"""
        with patch('config_loader.ConfigLoader._create_default_config') as mock_create:
            loader = ConfigLoader('nonexistent.yaml')
            assert loader is not None
            mock_create.assert_called_once()
    
    def test_init_with_sample_config(self):
        """サンプル設定ファイルからの初期化テスト"""
        # サンプルファイルを作成
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml.sample', delete=False) as f:
            config_data = {
                'preprocessing': {
                    'input_file': 'sample.csv',
                    'output_file': 'processed.csv'
                }
            }
            yaml.dump(config_data, f)
            sample_path = f.name
        
        config_path = sample_path.replace('.sample', '')
        
        try:
            with patch('shutil.copy') as mock_copy:
                loader = ConfigLoader(config_path)
                assert loader is not None
                mock_copy.assert_called_once_with(sample_path, config_path)
        finally:
            os.unlink(sample_path)
    
    def test_get_preprocessing_config(self):
        """前処理設定の取得テスト"""
        config_data = {
            'preprocessing': {
                'input_file': 'input.csv',
                'output_file': 'output.csv',
                'features': ['feature1', 'feature2']
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            config_path = f.name
        
        try:
            loader = ConfigLoader(config_path)
            preprocessing_config = loader.get_preprocessing_config()
            
            assert preprocessing_config['input_file'] == 'input.csv'
            assert preprocessing_config['output_file'] == 'output.csv'
            assert preprocessing_config['features'] == ['feature1', 'feature2']
        finally:
            os.unlink(config_path)
    
    def test_get_prediction_config(self):
        """予測設定の取得テスト"""
        config_data = {
            'prediction': {
                'features': ['feature1', 'feature2'],
                'target': 'target',
                'test_size': 0.2,
                'random_state': 42
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            config_path = f.name
        
        try:
            loader = ConfigLoader(config_path)
            prediction_config = loader.get_prediction_config()
            
            assert prediction_config['features'] == ['feature1', 'feature2']
            assert prediction_config['target'] == 'target'
            assert prediction_config['test_size'] == 0.2
            assert prediction_config['random_state'] == 42
        finally:
            os.unlink(config_path)
    
    def test_get_config_section_missing(self):
        """存在しない設定セクションの取得テスト"""
        config_data = {
            'preprocessing': {
                'input_file': 'input.csv'
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            config_path = f.name
        
        try:
            loader = ConfigLoader(config_path)
            
            # 存在しないセクションは空の辞書を返す
            missing_config = loader.get_config_section('nonexistent')
            assert missing_config == {}
        finally:
            os.unlink(config_path)
    
    def test_get_config_section_with_default(self):
        """デフォルト値付き設定セクションの取得テスト"""
        config_data = {
            'preprocessing': {
                'input_file': 'input.csv'
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            config_path = f.name
        
        try:
            loader = ConfigLoader(config_path)
            
            # デフォルト値付きで取得
            default_config = loader.get_config_section('nonexistent', {'default_key': 'default_value'})
            assert default_config == {'default_key': 'default_value'}
        finally:
            os.unlink(config_path)
    
    def test_get_config_value(self):
        """設定値の取得テスト"""
        config_data = {
            'preprocessing': {
                'input_file': 'input.csv',
                'nested': {
                    'key': 'value'
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            config_path = f.name
        
        try:
            loader = ConfigLoader(config_path)
            
            # 単一キーの取得
            input_file = loader.get_config_value('preprocessing.input_file')
            assert input_file == 'input.csv'
            
            # ネストしたキーの取得
            nested_value = loader.get_config_value('preprocessing.nested.key')
            assert nested_value == 'value'
            
            # 存在しないキーの取得
            missing_value = loader.get_config_value('nonexistent.key')
            assert missing_value is None
            
            # デフォルト値付きの取得
            default_value = loader.get_config_value('nonexistent.key', 'default')
            assert default_value == 'default'
        finally:
            os.unlink(config_path)
    
    def test_create_default_config(self):
        """デフォルト設定の作成テスト"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_path = f.name
        
        try:
            loader = ConfigLoader(config_path)
            loader._create_default_config()
            
            # 設定ファイルが作成されていることを確認
            assert os.path.exists(config_path)
            
            # 設定内容を確認
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                assert 'preprocessing' in config
                assert 'prediction' in config
        finally:
            os.unlink(config_path)
    
    def test_invalid_yaml_file(self):
        """無効なYAMLファイルの処理テスト"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write('invalid: yaml: content: [')
            config_path = f.name
        
        try:
            with pytest.raises(yaml.YAMLError):
                ConfigLoader(config_path)
        finally:
            os.unlink(config_path)
    
    def test_empty_config_file(self):
        """空の設定ファイルの処理テスト"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write('')
            config_path = f.name
        
        try:
            loader = ConfigLoader(config_path)
            assert loader.config is None or loader.config == {}
        finally:
            os.unlink(config_path)
    
    def test_config_path_property(self):
        """設定パスのプロパティテスト"""
        config_path = 'test_config.yaml'
        loader = ConfigLoader(config_path)
        assert loader.config_path == config_path
    
    def test_logging_setup(self):
        """ログ設定のテスト"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({'preprocessing': {}}, f)
            config_path = f.name
        
        try:
            loader = ConfigLoader(config_path)
            assert hasattr(loader, 'logger')
            assert loader.logger is not None
        finally:
            os.unlink(config_path)
    
    def test_config_validation(self):
        """設定の検証テスト"""
        config_data = {
            'preprocessing': {
                'input_file': 'input.csv',
                'output_file': 'output.csv'
            },
            'prediction': {
                'features': ['feature1', 'feature2'],
                'target': 'target'
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            config_path = f.name
        
        try:
            loader = ConfigLoader(config_path)
            
            # 設定の検証（実装による）
            # ここでは基本的な構造の確認のみ
            assert isinstance(loader.config, dict)
            assert 'preprocessing' in loader.config
            assert 'prediction' in loader.config
        finally:
            os.unlink(config_path)
