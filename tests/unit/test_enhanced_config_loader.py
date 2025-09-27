"""
強化された設定ローダーのテスト
"""

import pytest
import os
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch, mock_open
from enhanced_config_loader import (
    EnhancedConfigLoader,
    get_config_loader,
    get_config,
    validate_environment,
)
from config_validator import ConfigValidator


class TestEnhancedConfigLoader:
    """EnhancedConfigLoaderクラスのテスト"""

    def test_init(self):
        """初期化テスト"""
        loader = EnhancedConfigLoader()
        assert loader is not None
        assert hasattr(loader, "config_dir")
        assert hasattr(loader, "environment")
        assert hasattr(loader, "_config")

    def test_init_with_custom_config_dir(self):
        """カスタム設定ディレクトリでの初期化テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            loader = EnhancedConfigLoader(config_dir=temp_dir)
            assert str(loader.config_dir) == temp_dir

    def test_init_with_environment(self):
        """環境指定での初期化テスト"""
        loader = EnhancedConfigLoader(environment="development")
        assert loader.environment == "development"

    def test_load_config_files(self):
        """設定ファイルの読み込みテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)

            # 設定ファイルを作成
            core_config = {
                "system": {"name": "Test System", "version": "1.0.0"},
                "logging": {"level": "INFO"},
            }

            with open(config_dir / "core.yaml", "w") as f:
                yaml.dump(core_config, f)

            loader = EnhancedConfigLoader(config_dir=str(config_dir))
            assert "core" in loader._config
            assert loader._config["core"]["system"]["name"] == "Test System"

    def test_get_config_value(self):
        """設定値の取得テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)

            # 設定ファイルを作成
            core_config = {
                "system": {"name": "Test System"},
                "logging": {"level": "INFO"},
            }

            with open(config_dir / "core.yaml", "w") as f:
                yaml.dump(core_config, f)

            loader = EnhancedConfigLoader(config_dir=str(config_dir))

            # 設定値の取得
            assert loader.get("system.name") == "Test System"
            assert loader.get("logging.level") == "INFO"
            assert loader.get("nonexistent.key", "default") == "default"

    def test_get_section(self):
        """設定セクションの取得テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)

            # 設定ファイルを作成
            core_config = {
                "system": {"name": "Test System"},
                "logging": {"level": "INFO"},
            }

            with open(config_dir / "core.yaml", "w") as f:
                yaml.dump(core_config, f)

            loader = EnhancedConfigLoader(config_dir=str(config_dir))
            core_section = loader.get_section("core")

            assert "system" in core_section
            assert "logging" in core_section
            assert core_section["system"]["name"] == "Test System"

    def test_environment_variable_override(self):
        """環境変数での設定オーバーライドテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)

            # 設定ファイルを作成
            core_config = {"logging": {"level": "INFO"}, "system": {"debug": False}}

            with open(config_dir / "core.yaml", "w") as f:
                yaml.dump(core_config, f)

            # 環境変数を設定
            with patch.dict(os.environ, {"LOG_LEVEL": "DEBUG", "DEBUG": "true"}):
                loader = EnhancedConfigLoader(config_dir=str(config_dir))

                # 環境変数でオーバーライドされていることを確認
                assert loader.get("logging.level") == "DEBUG"
                assert loader.get("system.debug") is True

    def test_convert_env_value(self):
        """環境変数値の型変換テスト"""
        loader = EnhancedConfigLoader()

        # ブール値の変換
        assert loader._convert_env_value("true") is True
        assert loader._convert_env_value("false") is False

        # 整数の変換
        assert loader._convert_env_value("123") == 123

        # 浮動小数点数の変換
        assert loader._convert_env_value("123.45") == 123.45

        # 文字列の変換
        assert loader._convert_env_value("test_string") == "test_string"

    def test_validate_config_success(self):
        """設定検証成功テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)

            # 有効な設定ファイルを作成
            core_config = {
                "system": {"name": "Test System", "debug": False},
                "logging": {"level": "INFO"},
                "performance": {"max_workers": 4},
            }

            api_config = {
                "jquants": {
                    "base_url": "https://api.jquants.com/v1",
                    "timeout": 30,
                    "max_retries": 3,
                }
            }

            data_config = {
                "data_fetch": {"target_date": "20240301", "output_file": "data.csv"},
                "preprocessing": {
                    "columns": ["Code", "Date", "Close"],
                    "technical_indicators": {"sma_windows": [5, 10, 20]},
                },
            }

            models_config = {
                "prediction": {
                    "target": "Close",
                    "features": ["SMA_5", "SMA_10"],
                    "test_size": 0.2,
                    "models": {"linear_regression": {"type": "linear_regression"}},
                }
            }

            # 設定ファイルを保存
            with open(config_dir / "core.yaml", "w") as f:
                yaml.dump(core_config, f)
            with open(config_dir / "api.yaml", "w") as f:
                yaml.dump(api_config, f)
            with open(config_dir / "data.yaml", "w") as f:
                yaml.dump(data_config, f)
            with open(config_dir / "models.yaml", "w") as f:
                yaml.dump(models_config, f)

            # 環境変数を設定
            with patch.dict(
                os.environ,
                {
                    "JQUANTS_EMAIL": "test@example.com",
                    "JQUANTS_PASSWORD": "test_password",
                },
            ):
                loader = EnhancedConfigLoader(config_dir=str(config_dir))
                validation = loader.validate_config()

                assert validation.is_valid is True
                assert len(validation.errors) == 0

    def test_validate_config_failure(self):
        """設定検証失敗テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)

            # 不完全な設定ファイルを作成
            core_config = {
                "system": {"name": ""},  # 空の名前
                "logging": {"level": "INVALID_LEVEL"},  # 無効なログレベル
            }

            with open(config_dir / "core.yaml", "w") as f:
                yaml.dump(core_config, f)

            loader = EnhancedConfigLoader(config_dir=str(config_dir))
            validation = loader.validate_config()

            assert validation.is_valid is False
            assert len(validation.errors) > 0

    def test_get_environment_info(self):
        """環境情報の取得テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)

            # 設定ファイルを作成
            core_config = {"system": {"name": "Test System"}}
            with open(config_dir / "core.yaml", "w") as f:
                yaml.dump(core_config, f)

            loader = EnhancedConfigLoader(config_dir=str(config_dir))
            env_info = loader.get_environment_info()

            assert "environment" in env_info
            assert "config_dir" in env_info
            assert "config_files" in env_info
            assert "loaded_sections" in env_info

    def test_reload_config(self):
        """設定の再読み込みテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)

            # 初期設定ファイルを作成
            core_config = {"system": {"name": "Initial System"}}
            with open(config_dir / "core.yaml", "w") as f:
                yaml.dump(core_config, f)

            loader = EnhancedConfigLoader(config_dir=str(config_dir))
            assert loader.get("system.name") == "Initial System"

            # 設定ファイルを更新
            updated_config = {"system": {"name": "Updated System"}}
            with open(config_dir / "core.yaml", "w") as f:
                yaml.dump(updated_config, f)

            # 設定を再読み込み
            loader.reload_config()
            assert loader.get("system.name") == "Updated System"

    def test_export_config(self):
        """設定のエクスポートテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)

            # 設定ファイルを作成
            core_config = {"system": {"name": "Test System"}}
            with open(config_dir / "core.yaml", "w") as f:
                yaml.dump(core_config, f)

            loader = EnhancedConfigLoader(config_dir=str(config_dir))

            # 設定をエクスポート
            export_file = os.path.join(temp_dir, "exported_config.yaml")
            loader.export_config(export_file)

            assert os.path.exists(export_file)

            # エクスポートされたファイルの内容を確認
            with open(export_file, "r") as f:
                exported_config = yaml.safe_load(f)
                assert "core" in exported_config
                assert exported_config["core"]["system"]["name"] == "Test System"

    def test_update_config(self):
        """設定の更新テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)

            # 設定ファイルを作成
            core_config = {"system": {"name": "Test System"}}
            with open(config_dir / "core.yaml", "w") as f:
                yaml.dump(core_config, f)

            loader = EnhancedConfigLoader(config_dir=str(config_dir))

            # 設定を更新
            loader.update_config("core", "system.version", "2.0.0")
            assert loader.get("system.version") == "2.0.0"

            # ネストされた設定を更新
            loader.update_config("core", "logging.level", "DEBUG")
            assert loader.get("logging.level") == "DEBUG"

    def test_get_all_config(self):
        """全設定の取得テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)

            # 設定ファイルを作成
            core_config = {"system": {"name": "Test System"}}
            with open(config_dir / "core.yaml", "w") as f:
                yaml.dump(core_config, f)

            loader = EnhancedConfigLoader(config_dir=str(config_dir))
            all_config = loader.get_all_config()

            assert isinstance(all_config, dict)
            assert "core" in all_config
            assert all_config["core"]["system"]["name"] == "Test System"

    def test_global_config_loader(self):
        """グローバル設定ローダーのテスト"""
        # グローバル設定ローダーを取得
        loader1 = get_config_loader()
        loader2 = get_config_loader()

        # 同じインスタンスが返されることを確認
        assert loader1 is loader2

    def test_get_config_function(self):
        """get_config関数のテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)

            # 設定ファイルを作成
            core_config = {"system": {"name": "Test System"}}
            with open(config_dir / "core.yaml", "w") as f:
                yaml.dump(core_config, f)

            # グローバル設定ローダーをリセット
            import enhanced_config_loader

            enhanced_config_loader._config_loader = None

            with patch(
                "enhanced_config_loader.EnhancedConfigLoader"
            ) as mock_loader_class:
                mock_loader = mock_loader_class.return_value
                mock_loader.get.return_value = "Test System"

                result = get_config("system.name")
                assert result == "Test System"

    def test_validate_environment_function(self):
        """validate_environment関数のテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)

            # 有効な設定ファイルを作成
            core_config = {
                "system": {"name": "Test System"},
                "logging": {"level": "INFO"},
            }

            api_config = {
                "jquants": {"base_url": "https://api.jquants.com/v1", "timeout": 30}
            }

            with open(config_dir / "core.yaml", "w") as f:
                yaml.dump(core_config, f)
            with open(config_dir / "api.yaml", "w") as f:
                yaml.dump(api_config, f)

            # 環境変数を設定
            with patch.dict(
                os.environ,
                {
                    "JQUANTS_EMAIL": "test@example.com",
                    "JQUANTS_PASSWORD": "test_password",
                },
            ):
                # グローバル設定ローダーをリセット
                import enhanced_config_loader

                enhanced_config_loader._config_loader = None

                with patch(
                    "enhanced_config_loader.EnhancedConfigLoader"
                ) as mock_loader_class:
                    mock_loader = mock_loader_class.return_value
                    mock_validation = mock_loader.validate_config.return_value
                    mock_validation.is_valid = True
                    mock_validation.warnings = []

                    result = validate_environment()
                    assert result is True


class TestConfigValidator:
    """ConfigValidatorクラスのテスト"""

    def test_init(self):
        """初期化テスト"""
        validator = ConfigValidator()
        assert validator is not None
        assert hasattr(validator, "config_dir")
        assert hasattr(validator, "results")

    def test_validate_config_files(self):
        """設定ファイルの検証テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)

            # 一部のファイルのみ作成
            core_config = {"system": {"name": "Test System"}}
            with open(config_dir / "core.yaml", "w") as f:
                yaml.dump(core_config, f)

            validator = ConfigValidator(config_dir=str(config_dir))
            validator._validate_config_files()

            # 結果を確認
            assert len(validator.results) > 0
            error_results = [r for r in validator.results if r.level.value == "error"]
            assert len(error_results) > 0

    def test_validate_core_config(self):
        """コア設定の検証テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)

            # 無効な設定ファイルを作成
            core_config = {
                "system": {"name": ""},  # 空の名前
                "logging": {"level": "INVALID_LEVEL"},  # 無効なログレベル
            }

            with open(config_dir / "core.yaml", "w") as f:
                yaml.dump(core_config, f)

            validator = ConfigValidator(config_dir=str(config_dir))
            validator._validate_core_config()

            # エラーが検出されることを確認
            error_results = [r for r in validator.results if r.level.value == "error"]
            assert len(error_results) > 0

    def test_validate_api_config(self):
        """API設定の検証テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)

            # 無効なAPI設定を作成
            api_config = {
                "jquants": {
                    "base_url": "invalid_url",  # 無効なURL
                    "timeout": -1,  # 無効なタイムアウト
                    "max_retries": 20,  # 無効なリトライ回数
                }
            }

            with open(config_dir / "api.yaml", "w") as f:
                yaml.dump(api_config, f)

            validator = ConfigValidator(config_dir=str(config_dir))
            validator._validate_api_config()

            # エラーが検出されることを確認
            error_results = [r for r in validator.results if r.level.value == "error"]
            warning_results = [
                r for r in validator.results if r.level.value == "warning"
            ]
            assert len(error_results) > 0 or len(warning_results) > 0

    def test_validate_environment_variables(self):
        """環境変数の検証テスト"""
        validator = ConfigValidator()

        # 必須環境変数が設定されていない場合
        with patch.dict(os.environ, {}, clear=True):
            validator._validate_environment_variables()

            error_results = [r for r in validator.results if r.level.value == "error"]
            assert len(error_results) > 0

    def test_get_summary(self):
        """検証結果のサマリー取得テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)

            validator = ConfigValidator(config_dir=str(config_dir))
            validator._validate_config_files()

            summary = validator.get_summary()

            assert "total_issues" in summary
            assert "errors" in summary
            assert "warnings" in summary
            assert "info" in summary
            assert "is_valid" in summary
            assert isinstance(summary["total_issues"], int)

    def test_export_report(self):
        """検証レポートのエクスポートテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)

            validator = ConfigValidator(config_dir=str(config_dir))
            validator._validate_config_files()

            report_file = os.path.join(temp_dir, "validation_report.yaml")
            validator.export_report(report_file)

            assert os.path.exists(report_file)

            # レポートファイルの内容を確認
            with open(report_file, "r") as f:
                report = yaml.safe_load(f)
                assert "summary" in report
                assert "results" in report
