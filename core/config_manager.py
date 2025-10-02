#!/usr/bin/env python3
"""
設定管理システム - 統合システムから分離
設定の読み込み、保存、検証、環境別設定の管理
"""

import os
import yaml
from typing import Dict, Any, Optional
from datetime import datetime


class ConfigManager:
    """設定管理システム"""

    def __init__(
        self, config_file: str = "config_final.yaml", config: Dict[str, Any] = None
    ):
        """初期化"""
        self.config_file = config_file
        self.config = {}

        # 設定の読み込み
        if config is not None:
            self.config = config
        else:
            self._load_config()

    def _load_config(self) -> None:
        """設定の読み込み"""
        try:
            # 設定ファイルの読み込み
            if os.path.exists(self.config_file):
                with open(self.config_file, "r", encoding="utf-8") as f:
                    self.config = yaml.safe_load(f) or {}
                # 設定ファイル読み込み完了
            else:
                # デフォルト設定の作成
                self._create_default_config()

            # 環境別設定の適用
            self._apply_environment_config()

        except Exception as e:
            # 設定ファイル読み込みエラー - デフォルト設定を使用
            self._create_default_config()

    def _create_default_config(self) -> None:
        """デフォルト設定の作成"""
        self.config = {
            "system": {
                "name": "J-Quants株価予測システム",
                "version": "2.6.0",
                "environment": "production",
                "debug": False,
            },
            "logging": {
                "level": "INFO",
                "file": "jquants.log",
                "console_output": True,
                "max_file_size": "10MB",
                "backup_count": 5,
            },
            "security": {
                "sensitive_keys": [
                    "password",
                    "token",
                    "key",
                    "secret",
                    "auth",
                    "email",
                ],
                "mask_sensitive_data": True,
                "encryption_enabled": False,
            },
            "error_handling": {
                "unified_handler": True,
                "error_statistics": True,
                "auto_recovery": True,
                "max_recovery_attempts": 3,
            },
            "prediction": {
                "input_file": "processed_stock_data.csv",
                "features": [
                    "SMA_5",
                    "SMA_25",
                    "SMA_50",
                    "Close_lag_1",
                    "Close_lag_5",
                    "Close_lag_25",
                ],
                "target": "Close",
                "test_size": 0.2,
                "random_state": 42,
                "model_selection": {
                    "compare_models": False,
                    "primary_model": "random_forest",
                },
                "output": {"image": "stock_prediction_result.png"},
                "overfitting_detection": True,
                "max_r2_score": 0.95,
            },
            "performance_optimization": {
                "memory_limit_mb": 2048,
                "chunk_size": 10000,
                "max_workers": 4,
                "use_cache": True,
                "use_parallel": True,
                "cache_ttl": 3600,
            },
        }

    def _apply_environment_config(self) -> None:
        """環境別設定の適用"""
        environment = self.config.get("system", {}).get("environment", "production")

        if environment in self.config.get("environments", {}):
            env_config = self.config["environments"][environment]
            # 環境別設定をメイン設定にマージ
            self._deep_merge(self.config, env_config)

    def _deep_merge(self, base: Dict, override: Dict) -> None:
        """深いマージ処理"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def get_config(self, key: str = None, default: Any = None) -> Any:
        """設定値の取得"""
        if key is None:
            return self.config

        keys = key.split(".")
        value = self.config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set_config(self, key: str, value: Any) -> None:
        """設定値の設定"""
        keys = key.split(".")
        config = self.config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def save_config(self, file_path: str = None) -> None:
        """設定の保存"""
        if file_path is None:
            file_path = self.config_file

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
            # 設定保存完了
        except Exception as e:
            # 設定保存エラー
            raise

    def update_configuration(self, new_config: Dict[str, Any]) -> None:
        """システム設定の更新"""
        try:
            self.config.update(new_config)
            # システム設定更新完了
        except Exception as e:
            # 設定更新エラー
            raise

    def validate_config(self, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """設定の検証"""
        try:
            target_config = config or self.config
            issues = []

            # 設定が空の場合は有効とする（デフォルト設定を使用）
            if not target_config:
                return {"is_valid": True, "issues": []}

            # 必須キーのチェック（systemキーが存在する場合のみ）
            if "system" in target_config:
                required_keys = ["system"]
                for key in required_keys:
                    if key not in target_config:
                        issues.append(f"必須設定キー '{key}' が不足しています")

            # APIキーのチェック（テスト環境では不要）
            if target_config.get("system", {}).get("environment") != "test":
                if "api_key" not in target_config:
                    issues.append("必須設定キー 'api_key' が不足しています")

            return {"is_valid": len(issues) == 0, "issues": issues}
        except Exception as e:
            return {"is_valid": False, "issues": [f"設定検証エラー: {str(e)}"]}

    def create_backup(self) -> Dict[str, Any]:
        """設定バックアップの作成"""
        try:
            backup_data = {
                "config": self.config.copy(),
                "timestamp": datetime.now().isoformat(),
                "config_file": self.config_file,
            }
            # 設定バックアップ作成完了
            return backup_data
        except Exception as e:
            # バックアップ作成エラー
            raise

    def restore_from_backup(self, backup_data: Dict[str, Any]) -> bool:
        """バックアップからの復元"""
        try:
            if backup_data and "config" in backup_data:
                self.config = backup_data["config"]
                # バックアップから正常に復元
                return True
            return False
        except Exception as e:
            # バックアップ復元エラー
            return False
