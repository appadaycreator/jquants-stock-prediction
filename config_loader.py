"""
設定ローダーモジュール
YAML設定ファイルの読み込みと管理を行う
"""

import os
import yaml
import logging
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, Union


class ConfigLoader:
    """設定ローダークラス"""

    def __init__(self, config_path: str = "config.yaml"):
        """
        初期化

        Args:
            config_path: 設定ファイルのパス
        """
        self.config_path = config_path
        self.logger = logging.getLogger(__name__)
        self.config: Optional[Dict[str, Any]] = None

        # ログ設定
        self._setup_logging()

        # 設定ファイルの読み込み
        self._load_config()

    def _setup_logging(self):
        """ログ設定のセットアップ"""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def _load_config(self):
        """設定ファイルの読み込み"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.config = yaml.safe_load(f)
                self.logger.info(f"設定ファイルを読み込みました: {self.config_path}")
            else:
                # サンプルファイルからコピーを試行
                sample_path = f"{self.config_path}.sample"
                if os.path.exists(sample_path):
                    shutil.copy(sample_path, self.config_path)
                    self.logger.info(
                        f"サンプルファイルから設定ファイルを作成しました: {sample_path} -> {self.config_path}"
                    )
                    with open(self.config_path, "r", encoding="utf-8") as f:
                        self.config = yaml.safe_load(f)
                else:
                    # デフォルト設定を作成
                    self._create_default_config()
                    self.logger.info(f"デフォルト設定ファイルを作成しました: {self.config_path}")
        except yaml.YAMLError as e:
            self.logger.error(f"YAMLファイルの解析に失敗しました: {e}")
            self._create_default_config()
        except Exception as e:
            self.logger.error(f"設定ファイルの読み込みに失敗しました: {e}")
            self._create_default_config()

    def _create_default_config(self):
        """デフォルト設定の作成"""
        default_config = {
            "preprocessing": {
                "input_file": "stock_data.csv",
                "output_file": "processed_stock_data.csv",
                "features": ["Close", "Volume"],
            },
            "prediction": {
                "features": ["Close", "Volume"],
                "target": "Close",
                "test_size": 0.2,
                "random_state": 42,
            },
        }

        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)
            self.config = default_config
            self.logger.info("デフォルト設定を作成しました")
        except Exception as e:
            self.logger.error(f"デフォルト設定の作成に失敗しました: {e}")
            self.config = default_config

    def get_preprocessing_config(self) -> Dict[str, Any]:
        """前処理設定の取得"""
        return self.get_config_section("preprocessing", {})

    def get_prediction_config(self) -> Dict[str, Any]:
        """予測設定の取得"""
        return self.get_config_section("prediction", {})

    def get_config_section(self, section: str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        設定セクションの取得

        Args:
            section: セクション名
            default: デフォルト値

        Returns:
            設定セクションの辞書
        """
        if self.config is None:
            return default or {}

        return self.config.get(section, default or {})

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """
        設定値の取得（ドット記法対応）

        Args:
            key: 設定キー（例: "preprocessing.input_file"）
            default: デフォルト値

        Returns:
            設定値
        """
        if self.config is None:
            return default

        keys = key.split('.')
        value = self.config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def update_config(self, section: str, key: str, value: Any):
        """
        設定値の更新

        Args:
            section: セクション名
            key: キー名
            value: 新しい値
        """
        if self.config is None:
            self.config = {}

        if section not in self.config:
            self.config[section] = {}

        self.config[section][key] = value
        self.logger.info(f"設定を更新しました: {section}.{key} = {value}")

    def save_config(self, path: Optional[str] = None):
        """
        設定の保存

        Args:
            path: 保存先パス（省略時は現在のパス）
        """
        save_path = path or self.config_path

        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
            self.logger.info(f"設定を保存しました: {save_path}")
        except Exception as e:
            self.logger.error(f"設定の保存に失敗しました: {e}")
            raise

    def reload_config(self):
        """設定の再読み込み"""
        self._load_config()
        self.logger.info("設定を再読み込みしました")

    def get_all_config(self) -> Dict[str, Any]:
        """全設定の取得"""
        return self.config or {}

    def validate_config(self) -> bool:
        """
        設定の検証

        Returns:
            検証結果
        """
        if self.config is None:
            return False

        # 基本的な検証
        required_sections = ["preprocessing", "prediction"]
        for section in required_sections:
            if section not in self.config:
                self.logger.warning(f"必須セクションが見つかりません: {section}")
                return False

        return True

    def __getitem__(self, key: str) -> Any:
        """辞書風のアクセス"""
        return self.get_config_value(key)

    def __setitem__(self, key: str, value: Any):
        """辞書風の設定"""
        if '.' in key:
            section, sub_key = key.split('.', 1)
            self.update_config(section, sub_key, value)
        else:
            if self.config is None:
                self.config = {}
            self.config[key] = value

    def __contains__(self, key: str) -> bool:
        """キーの存在確認"""
        if self.config is None:
            return False

        if '.' in key:
            keys = key.split('.')
            value = self.config
            try:
                for k in keys:
                    value = value[k]
                return True
            except (KeyError, TypeError):
                return False
        else:
            return key in self.config


# グローバル設定ローダーインスタンス
_global_config_loader: Optional[ConfigLoader] = None


def get_config_loader() -> ConfigLoader:
    """グローバル設定ローダーの取得"""
    global _global_config_loader
    if _global_config_loader is None:
        _global_config_loader = ConfigLoader()
    return _global_config_loader


def get_config(key: str, default: Any = None) -> Any:
    """
    設定値の取得（グローバル関数）

    Args:
        key: 設定キー
        default: デフォルト値

    Returns:
        設定値
    """
    loader = get_config_loader()
    return loader.get_config_value(key, default)


def reload_config():
    """設定の再読み込み（グローバル関数）"""
    loader = get_config_loader()
    loader.reload_config()


def validate_config() -> bool:
    """設定の検証（グローバル関数）"""
    loader = get_config_loader()
    return loader.validate_config()
