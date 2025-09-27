#!/usr/bin/env python3
"""
設定ファイル読み込みモジュール
YAMLファイルから設定を動的に読み込み、各スクリプトで共通利用する
"""

import yaml
import os
import logging
from typing import Dict, Any
from pathlib import Path


class ConfigLoader:
    """設定ファイル読み込みクラス"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        初期化
        
        Args:
            config_path (str): 設定ファイルのパス
        """
        self.config_path = config_path
        self.config = None
        self._load_config()
        self._setup_logging()
    
    def _load_config(self) -> None:
        """設定ファイルを読み込む"""
        try:
            if not os.path.exists(self.config_path):
                raise FileNotFoundError(f"設定ファイルが見つかりません: {self.config_path}")
            
            with open(self.config_path, 'r', encoding='utf-8') as file:
                self.config = yaml.safe_load(file)
            
            print(f"設定ファイルを読み込みました: {self.config_path}")
            
        except Exception as e:
            print(f"設定ファイルの読み込みに失敗しました: {e}")
            raise
    
    def _setup_logging(self) -> None:
        """ログ設定をセットアップ"""
        if not self.config:
            return
        
        log_config = self.config.get('logging', {})
        
        logging.basicConfig(
            level=getattr(logging, log_config.get('level', 'INFO')),
            format=log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            handlers=[
                logging.FileHandler(log_config.get('file', 'jquants.log')),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("ログ設定を初期化しました")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        設定値を取得（ドット記法でネストした値にアクセス可能）
        
        Args:
            key_path (str): 取得するキーのパス（例: "data_fetch.target_date"）
            default (Any): デフォルト値
            
        Returns:
            Any: 設定値
        """
        if not self.config:
            return default
        
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_data_fetch_config(self) -> Dict[str, Any]:
        """データ取得設定を取得"""
        return self.config.get('data_fetch', {})
    
    def get_preprocessing_config(self) -> Dict[str, Any]:
        """データ前処理設定を取得"""
        return self.config.get('preprocessing', {})
    
    def get_prediction_config(self) -> Dict[str, Any]:
        """予測設定を取得"""
        return self.config.get('prediction', {})
    
    def get_jquants_config(self) -> Dict[str, Any]:
        """J-Quants API設定を取得"""
        return self.config.get('jquants', {})
    
    def validate_config(self) -> bool:
        """設定ファイルの妥当性をチェック"""
        required_sections = ['data_fetch', 'preprocessing', 'prediction']
        
        for section in required_sections:
            if section not in self.config:
                self.logger.error(f"必須セクションが見つかりません: {section}")
                return False
        
        # データ取得設定のチェック
        data_fetch = self.get_data_fetch_config()
        if not data_fetch.get('target_date'):
            self.logger.error("data_fetch.target_date が設定されていません")
            return False
        
        # 前処理設定のチェック
        preprocessing = self.get_preprocessing_config()
        if not preprocessing.get('columns'):
            self.logger.error("preprocessing.columns が設定されていません")
            return False
        
        # 予測設定のチェック
        prediction = self.get_prediction_config()
        if not prediction.get('features'):
            self.logger.error("prediction.features が設定されていません")
            return False
        
        self.logger.info("設定ファイルの妥当性チェックが完了しました")
        return True
    
    def update_config(self, key_path: str, value: Any) -> None:
        """
        設定値を更新（動的に設定を変更する場合に使用）
        
        Args:
            key_path (str): 更新するキーのパス
            value (Any): 新しい値
        """
        if not self.config:
            self.config = {}
        
        keys = key_path.split('.')
        current = self.config
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
        self.logger.info(f"設定を更新しました: {key_path} = {value}")
    
    def save_config(self, output_path: str = None) -> None:
        """
        設定をファイルに保存
        
        Args:
            output_path (str): 出力ファイルパス（Noneの場合は元のファイルを上書き）
        """
        output_file = output_path or self.config_path
        
        try:
            with open(output_file, 'w', encoding='utf-8') as file:
                yaml.dump(self.config, file, default_flow_style=False, 
                         allow_unicode=True, indent=2)
            
            self.logger.info(f"設定ファイルを保存しました: {output_file}")
        
        except Exception as e:
            self.logger.error(f"設定ファイルの保存に失敗しました: {e}")
            raise


# シングルトンパターンでグローバル設定インスタンスを作成
_config_instance = None

def get_config(config_path: str = "config.yaml") -> ConfigLoader:
    """
    設定インスタンスを取得（シングルトンパターン）
    
    Args:
        config_path (str): 設定ファイルのパス
        
    Returns:
        ConfigLoader: 設定ローダーインスタンス
    """
    global _config_instance
    
    if _config_instance is None:
        _config_instance = ConfigLoader(config_path)
    
    return _config_instance


# 便利関数
def get_setting(key_path: str, default: Any = None) -> Any:
    """設定値を取得する便利関数"""
    return get_config().get(key_path, default)


if __name__ == "__main__":
    # テスト実行
    try:
        config = get_config()
        
        if config.validate_config():
            print("✅ 設定ファイルは正常です")
            
            # 設定例の表示
            print(f"取得日付: {config.get('data_fetch.target_date')}")
            print(f"移動平均期間: {config.get('preprocessing.sma_windows')}")
            print(f"特徴量: {config.get('prediction.features')}")
            print(f"モデルパラメータ: {config.get('prediction.random_forest')}")
        else:
            print("❌ 設定ファイルにエラーがあります")
            
    except Exception as e:
        print(f"❌ エラー: {e}")
