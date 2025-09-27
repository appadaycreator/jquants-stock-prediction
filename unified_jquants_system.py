#!/usr/bin/env python3
"""
統合J-Quantsシステム
完全に統合された、セキュアで堅牢なJ-Quants APIクライアントシステム
"""

import os
import logging
import requests
import pandas as pd
import numpy as np
import time
import re
import traceback
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
from unified_config_loader import get_unified_config
from unified_error_handler import get_unified_error_handler
from model_factory import ModelFactory, ModelEvaluator, ModelComparator
from technical_indicators import TechnicalIndicators, get_enhanced_features_list
from data_validator import DataValidator
from unified_error_logging_system import (
    get_unified_error_logging_system,
    ErrorCategory,
    LogCategory,
    configure_global_logging,
)
from type_safe_validator import TypeSafeValidator
from font_config import setup_japanese_font


class UnifiedJQuantsSystem:
    """統合J-Quantsシステム - 単一責任原則に基づく完全統合システム"""

    def __init__(self):
        """初期化"""
        self.logger = logging.getLogger(__name__)
        self.error_count = 0
        self.sensitive_keys = ["password", "token", "key", "secret", "auth", "email"]

        # 環境変数の読み込み
        load_dotenv()

        # 統合設定の読み込み
        try:
            self.config_loader = get_unified_config()
            self.jquants_config = self.config_loader.get_jquants_config()
            self.data_fetch_config = self.config_loader.get_data_fetch_config()
            self.preprocessing_config = self.config_loader.get_preprocessing_config()
            self.prediction_config = self.config_loader.get_prediction_config()

            # グローバルログ設定の適用
            configure_global_logging(self.config_loader.config)
        except Exception as e:
            self.logger.error(f"設定読み込みエラー: {e}")
            raise

        # 認証情報の安全な取得
        self._load_credentials()

        # セッション設定
        self.session = requests.Session()
        self.session.timeout = self.data_fetch_config.get("timeout", 30)

        # 認証状態
        self.refresh_token = None
        self.id_token = None
        self.token_expires_at = None

        # 機械学習コンポーネントの初期化
        self.model_factory = ModelFactory()
        self.model_evaluator = ModelEvaluator()
        self.model_comparator = ModelComparator()

        # 技術指標計算器の初期化
        self.technical_indicators = TechnicalIndicators()

        # データ検証器の初期化
        self.data_validator = DataValidator()

        # 型安全バリデーターの初期化
        self.type_safe_validator = TypeSafeValidator(strict_mode=True)

        # 日本語フォント設定
        setup_japanese_font()

        # 統合エラーハンドリング・ログシステムの初期化
        self.error_logger = get_unified_error_logging_system(
            "UnifiedJQuantsSystem", self.config_loader.config
        )

        self.logger.info("✅ 統合J-Quantsシステム初期化完了")

    def _load_credentials(self) -> None:
        """認証情報の安全な読み込み"""
        try:
            self.email = os.getenv("JQUANTS_EMAIL")
            self.password = os.getenv("JQUANTS_PASSWORD")

            # 認証情報の検証（機密情報はログに出力しない）
            if not self.email or not self.password:
                error_msg = "認証情報が設定されていません"
                masked_context = {
                    "email_set": bool(self.email),
                    "password_set": bool(self.password),
                    "env_file_exists": os.path.exists(".env"),
                }
                self._log_error(
                    ValueError(error_msg),
                    "認証情報検証エラー",
                    masked_context,
                )
                self.logger.error(
                    "❌ 環境変数 JQUANTS_EMAIL と JQUANTS_PASSWORD を設定してください。"
                )
                self.logger.error(
                    "💡 .env ファイルを作成し、認証情報を設定してください。"
                )
                raise ValueError(error_msg)

            self.logger.info("✅ 認証情報の読み込み完了")

        except Exception as e:
            self._log_error(e, "認証情報読み込みエラー")
            raise

    def _sanitize_message(self, message: str) -> str:
        """機密情報をマスキング"""
        sensitive_patterns = [
            r'password["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
            r'token["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
            r'key["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
            r'secret["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
            r'auth["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
            r'email["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
        ]

        sanitized = message
        for pattern in sensitive_patterns:
            sanitized = re.sub(
                pattern, r"\1***MASKED***", sanitized, flags=re.IGNORECASE
            )
        return sanitized

    def _mask_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """機密データのマスキング"""
        masked_data = data.copy()

        for key, value in masked_data.items():
            if any(
                sensitive_key in key.lower() for sensitive_key in self.sensitive_keys
            ):
                if isinstance(value, str) and len(value) > 4:
                    masked_data[key] = value[:2] + "*" * (len(value) - 4) + value[-2:]
                else:
                    masked_data[key] = "***"

        return masked_data

    def _log_error(
        self,
        error: Exception,
        context: str = "",
        additional_info: Dict[str, Any] = None,
        include_traceback: bool = True,
    ):
        """セキュアなエラーログ出力"""
        self.error_count += 1

        # 機密情報をマスキング
        sanitized_context = self._sanitize_message(context)
        sanitized_error_msg = self._sanitize_message(str(error))

        # 追加情報のマスキング
        masked_info = None
        if additional_info:
            masked_info = self._mask_sensitive_data(additional_info)

        # エラーログの出力
        self.logger.error(f"❌ エラー #{self.error_count}: {sanitized_context}")
        self.logger.error(f"エラー詳細: {sanitized_error_msg}")

        if masked_info:
            self.logger.error(f"追加情報: {masked_info}")

        if include_traceback:
            traceback_str = self._sanitize_message(
                "".join(
                    traceback.format_exception(type(error), error, error.__traceback__)
                )
            )
            self.logger.error(f"トレースバック: {traceback_str}")

    def _handle_api_error(
        self,
        error: Exception,
        api_name: str,
        url: str,
        status_code: int = None,
    ):
        """APIエラーの処理（統合システム使用）"""
        self.error_logger.handle_api_error(error, api_name, url, status_code)

    def _handle_file_error(
        self,
        error: Exception,
        file_path: str,
        operation: str,
    ):
        """ファイルエラーの処理（統合システム使用）"""
        self.error_logger.handle_file_error(error, file_path, operation)

    def get_refresh_token(self) -> str:
        """リフレッシュトークンの取得"""
        self.logger.info("🔑 リフレッシュトークンを取得中...")

        try:
            auth_url = "https://api.jquants.com/v1/token/auth_user"
            auth_payload = {"mailaddress": self.email, "password": self.password}

            response = self.session.post(auth_url, json=auth_payload, timeout=30)
            response.raise_for_status()

            auth_data = response.json()

            if "refreshToken" not in auth_data:
                error_msg = "リフレッシュトークンの取得に失敗しました"
                self._handle_api_error(
                    ValueError(error_msg),
                    "J-Quants API",
                    auth_url,
                    response.status_code,
                )
                raise ValueError(error_msg)

            self.refresh_token = auth_data["refreshToken"]
            self.logger.info("✅ リフレッシュトークンを取得しました")
            return self.refresh_token

        except requests.exceptions.RequestException as e:
            self._handle_api_error(e, "J-Quants API", auth_url)
            raise
        except Exception as e:
            self._log_error(e, "リフレッシュトークン取得エラー")
            raise

    def get_id_token(self) -> str:
        """IDトークンの取得"""
        self.logger.info("🎫 IDトークンを取得中...")

        try:
            if not self.refresh_token:
                self.get_refresh_token()

            id_token_url = "https://api.jquants.com/v1/token/auth_refresh"
            id_token_params = {"refreshtoken": self.refresh_token}

            response = self.session.post(
                id_token_url, params=id_token_params, timeout=30
            )
            response.raise_for_status()

            id_token_data = response.json()

            if "idToken" not in id_token_data:
                error_msg = "IDトークンの取得に失敗しました"
                self._handle_api_error(
                    ValueError(error_msg),
                    "J-Quants API",
                    id_token_url,
                    response.status_code,
                )
                raise ValueError(error_msg)

            self.id_token = id_token_data["idToken"]
            # トークンの有効期限を設定（通常24時間）
            self.token_expires_at = datetime.now() + timedelta(hours=23)
            self.logger.info("✅ IDトークンを取得しました")
            return self.id_token

        except requests.exceptions.RequestException as e:
            self._handle_api_error(e, "J-Quants API", id_token_url)
            raise
        except Exception as e:
            self._log_error(e, "IDトークン取得エラー")
            raise

    def ensure_valid_token(self) -> str:
        """有効なトークンの確保"""
        if (
            self.id_token is None
            or self.token_expires_at is None
            or datetime.now() >= self.token_expires_at
        ):
            self.logger.info("🔄 トークンの更新が必要です")
            self.get_id_token()

        return self.id_token

    def get_auth_headers(self) -> Dict[str, str]:
        """認証ヘッダーの取得"""
        token = self.ensure_valid_token()
        return {"Authorization": f"Bearer {token}"}

    def _make_request_with_retry(
        self, method: str, url: str, **kwargs
    ) -> requests.Response:
        """リトライ機能付きHTTPリクエスト"""
        max_retries = self.data_fetch_config.get("max_retries", 3)
        retry_interval = self.data_fetch_config.get("retry_interval", 5)

        for attempt in range(max_retries + 1):
            try:
                self.logger.info(
                    f"APIリクエスト (試行 {attempt + 1}/{max_retries + 1}): {method} {url}"
                )
                response = self.session.request(method, url, **kwargs)

                if response.status_code == 200:
                    self.logger.info(f"✅ APIリクエスト成功: {response.status_code}")
                    return response
                else:
                    # HTTPエラーの詳細ログ
                    self._handle_api_error(
                        requests.exceptions.HTTPError(
                            f"HTTP {response.status_code}: {response.text}"
                        ),
                        "J-Quants API",
                        url,
                        response.status_code,
                    )
                    self.logger.warning(f"⚠️ APIリクエスト失敗: {response.status_code}")

            except requests.exceptions.Timeout as e:
                if attempt < max_retries:
                    self.logger.warning(
                        f"⏰ タイムアウト (試行 {attempt + 1}/{max_retries + 1})"
                    )
                    self.logger.info(f"⏳ {retry_interval}秒後にリトライします...")
                    time.sleep(retry_interval)
                    continue
                else:
                    self._handle_api_error(e, "J-Quants API", url)
                    raise

            except requests.exceptions.ConnectionError as e:
                if attempt < max_retries:
                    self.logger.warning(
                        f"🔌 接続エラー (試行 {attempt + 1}/{max_retries + 1})"
                    )
                    self.logger.info(f"⏳ {retry_interval}秒後にリトライします...")
                    time.sleep(retry_interval)
                    continue
                else:
                    self._handle_api_error(e, "J-Quants API", url)
                    raise

            except requests.exceptions.RequestException as e:
                self._handle_api_error(e, "J-Quants API", url)
                if attempt < max_retries:
                    self.logger.info(f"⏳ {retry_interval}秒後にリトライします...")
                    time.sleep(retry_interval)
                    continue
                else:
                    raise

        # 全てのリトライが失敗した場合
        final_error = Exception(f"APIリクエストが{max_retries + 1}回失敗しました")
        self._log_error(
            final_error,
            "APIリクエスト最終失敗",
            {
                "method": method,
                "url": url,
                "max_retries": max_retries,
                "retry_interval": retry_interval,
            },
        )
        raise final_error

    def _validate_stock_data(self, data: Dict[str, Any]) -> bool:
        """取得した株価データの検証"""
        self.logger.info("🔍 データ検証を実行中...")

        # 基本的な構造チェック
        if not isinstance(data, dict):
            self.logger.error("❌ データが辞書形式ではありません")
            return False

        if "daily_quotes" not in data:
            self.logger.error("❌ daily_quotesキーが見つかりません")
            return False

        quotes = data["daily_quotes"]
        if not isinstance(quotes, list):
            self.logger.error("❌ daily_quotesがリスト形式ではありません")
            return False

        if len(quotes) == 0:
            self.logger.warning("⚠️ 取得データが空です")
            return False

        # 必須フィールドのチェック
        required_fields = ["Code", "Date", "Open", "High", "Low", "Close", "Volume"]
        sample_quote = quotes[0]
        missing_fields = [
            field for field in required_fields if field not in sample_quote
        ]

        if missing_fields:
            self.logger.error(f"❌ 必須フィールドが不足: {missing_fields}")
            return False

        # データ型の検証
        for i, quote in enumerate(quotes[:5]):  # 最初の5件をサンプルチェック
            try:
                float(quote.get("Close", 0))
                float(quote.get("Volume", 0))
                pd.to_datetime(quote.get("Date"))
            except (ValueError, TypeError) as e:
                self.logger.error(f"❌ データ型エラー (行{i}): {e}")
                return False

        self.logger.info(f"✅ データ検証完了: {len(quotes)}件のデータを確認")
        return True

    def fetch_stock_data(self, target_date: str) -> pd.DataFrame:
        """株価データの取得"""
        self.logger.info(f"📊 株価データ取得を開始: {target_date}")

        try:
            # 認証ヘッダーの取得
            headers = self.get_auth_headers()

            # 株価データの取得
            price_url = f"{self.jquants_config.get('base_url', 'https://api.jquants.com/v1')}/prices/daily_quotes"
            params = {"date": target_date}

            response = self._make_request_with_retry(
                "GET", price_url, headers=headers, params=params
            )
            data = response.json()

            # データ検証
            if not self._validate_stock_data(data):
                raise ValueError("取得データの検証に失敗しました")

            # DataFrameに変換
            df = pd.DataFrame(data["daily_quotes"])
            self.logger.info(f"✅ データ取得完了: {len(df)}件")

            return df

        except Exception as e:
            self._log_error(e, "株価データ取得エラー")
            raise

    def save_data(self, df: pd.DataFrame, output_file: str) -> None:
        """データの保存"""
        self.logger.info(f"💾 データを保存中: {output_file}")

        try:
            # データフレームの基本検証
            if df is None or df.empty:
                raise ValueError("保存するデータが空です")

            # 出力ディレクトリの確認・作成
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                self.logger.info(f"📁 出力ディレクトリを作成: {output_dir}")

            df.to_csv(output_file, index=False)
            self.logger.info(f"✅ データ保存完了: {output_file} ({len(df)}件)")

        except Exception as e:
            self._handle_file_error(e, output_file, "write")
            raise

    def preprocess_data(self, input_file: str, output_file: str = None) -> pd.DataFrame:
        """データの前処理（統合版）"""
        self.logger.info("🔧 データ前処理を開始")

        if output_file is None:
            output_file = self.preprocessing_config.get(
                "output_file", "processed_stock_data.csv"
            )

        try:
            # 1. データの読み込みとクリーニング
            self.logger.info("📁 ステップ1: データ読み込みとクリーニング")
            df = self._load_and_clean_data(input_file)

            # 2. 基本的な特徴量エンジニアリング
            self.logger.info("🔧 ステップ2: 基本特徴量エンジニアリング")
            df = self._engineer_basic_features(df)

            # 3. 高度な技術指標による特徴量エンジニアリング
            self.logger.info("🚀 ステップ3: 高度な技術指標計算")
            df = self._engineer_advanced_features(df)

            # 4. 特徴量選択と検証
            self.logger.info("🎯 ステップ4: 特徴量選択と検証")
            df, available_features = self._feature_selection_and_validation(df)

            # 5. 欠損値の最終処理
            self.logger.info("🧹 ステップ5: 欠損値の最終処理")
            initial_rows = len(df)
            df = df.dropna()
            final_rows = len(df)
            dropped_rows = initial_rows - final_rows

            if dropped_rows > 0:
                self.logger.info(
                    f"🗑️ 欠損値を含む行を削除: {initial_rows} -> {final_rows} 行 ({dropped_rows} 行削除)"
                )

            # 6. データ検証の実行
            self.logger.info("🔍 ステップ6: データ品質検証")
            if not self._validate_processed_data(df):
                self.logger.warning(
                    "⚠️ データ検証で問題が検出されましたが、処理を続行します"
                )

            # 7. データの保存
            self.logger.info("💾 ステップ7: データ保存")
            df.to_csv(output_file, index=False)
            self.logger.info(f"✅ 前処理済みデータを保存: {output_file}")

            # 8. 最終統計情報の表示
            self.logger.info("📊 最終データ統計:")
            self.logger.info(f"  📏 データ形状: {df.shape}")
            self.logger.info(
                f"  📅 データ期間: {df['Date'].min()} ～ {df['Date'].max()}"
            )
            self.logger.info(f"  📈 特徴量数: {len(df.columns)}個")
            self.logger.info(f"  🎯 推奨特徴量: {len(available_features)}個")

            return df

        except Exception as e:
            error_handler = get_unified_error_handler("preprocess_data")
            error_handler.log_error(
                e,
                "データ前処理エラー",
                {
                    "input_file": input_file,
                    "output_file": output_file,
                    "data_shape": (
                        df.shape if "df" in locals() and df is not None else None
                    ),
                },
            )
            self.logger.error(f"❌ データ前処理中にエラー: {e}")
            raise

    def predict_stock_prices(
        self, input_file: str, output_image: str = None
    ) -> Dict[str, Any]:
        """株価予測の実行（統合版）"""
        self.logger.info("🎯 株価予測を開始")

        if output_image is None:
            output_image = self.prediction_config.get(
                "output_image", "stock_prediction_result.png"
            )

        try:
            # データの読み込み
            self.logger.info(f"📁 データを読み込み中: {input_file}")
            df = pd.read_csv(input_file)

            # 特徴量と目的変数の設定
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

            # 利用可能な特徴量のみを選択
            available_features = [col for col in features if col in df.columns]
            missing_features = [col for col in features if col not in df.columns]

            if missing_features:
                self.logger.warning(f"⚠️ 不足している特徴量: {missing_features}")

            X = df[available_features]
            y = df[target]

            # 訓練データとテストデータに分割
            from sklearn.model_selection import train_test_split

            test_size = self.prediction_config.get("test_size", 0.2)
            random_state = self.prediction_config.get("random_state", 42)

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state
            )

            self.logger.info(
                f"訓練データ: {len(X_train)}行, テストデータ: {len(X_test)}行"
            )

            # モデル設定の取得
            model_selection = self.prediction_config.get("model_selection", {})
            compare_models = model_selection.get("compare_models", False)
            primary_model = model_selection.get("primary_model", "random_forest")

            if compare_models:
                self.logger.info("🔄 複数モデル比較を実行中...")
                models_config = self.prediction_config.get("models", {})

                if not models_config:
                    self.logger.warning(
                        "警告: モデル設定が見つかりません。デフォルト設定を使用します。"
                    )
                    from model_factory import get_default_models_config

                    models_config = get_default_models_config()

                # 複数モデルの比較実行
                comparison_results = self.model_comparator.compare_models(
                    models_config, X_train, X_test, y_train, y_test, available_features
                )

                if not comparison_results.empty:
                    self.logger.info("📊 モデル比較結果:")
                    for idx, row in comparison_results.iterrows():
                        self.logger.info(
                            f"{row['model_name']:<15} | MAE: {row['mae']:.4f} | RMSE: {row['rmse']:.4f} | R²: {row['r2']:.4f}"
                        )

                    # 最優秀モデルを選択
                    best_model_name = comparison_results.iloc[0]["model_name"]
                    self.logger.info(f"🏆 最優秀モデル: {best_model_name}")

                    # 比較結果をCSVに保存
                    comparison_csv = self.prediction_config.get(
                        "comparison_csv", "model_comparison_results.csv"
                    )
                    comparison_results.to_csv(comparison_csv, index=False)
                    self.logger.info(f"📁 比較結果を '{comparison_csv}' に保存しました")

                    # 最優秀モデルで再学習
                    best_config = models_config[best_model_name]
                    model = self.model_factory.create_model(
                        best_config["type"], best_config.get("params", {})
                    )
                else:
                    self.logger.error(
                        "❌ モデル比較で有効な結果が得られませんでした。デフォルトモデルを使用します。"
                    )
                    model = self.model_factory.create_model("random_forest")
                    best_model_name = "random_forest"
            else:
                self.logger.info(f"🎯 単一モデル実行: {primary_model}")
                models_config = self.prediction_config.get("models", {})
                if primary_model in models_config:
                    model_config = models_config[primary_model]
                    model = self.model_factory.create_model(
                        model_config["type"], model_config.get("params", {})
                    )
                else:
                    self.logger.warning(
                        f"警告: モデル '{primary_model}' の設定が見つかりません。デフォルト設定を使用します。"
                    )
                    model = self.model_factory.create_model(primary_model)

                best_model_name = primary_model

            # モデル学習
            self.logger.info(f"📚 モデル学習中: {best_model_name}")
            model.fit(X_train, y_train)

            # 予測と評価
            y_pred = model.predict(X_test)
            metrics = self.model_evaluator.evaluate_model(model, X_test, y_test, y_pred)

            self.logger.info(f"📊 最終評価結果:")
            self.logger.info(f"  MAE (平均絶対誤差): {metrics['mae']:.4f}")
            self.logger.info(f"  RMSE (平均平方根誤差): {metrics['rmse']:.4f}")
            self.logger.info(f"  R² (決定係数): {metrics['r2']:.4f}")

            # 特徴量重要度を取得
            feature_importance_df = self.model_evaluator.get_feature_importance(
                model, available_features
            )
            if not feature_importance_df.empty:
                self.logger.info("🎯 特徴量重要度:")
                for idx, row in feature_importance_df.iterrows():
                    self.logger.info(f"  {row['feature']}: {row['importance']:.4f}")

            # 結果の可視化
            self.logger.info(f"🎨 結果を '{output_image}' に保存中...")
            self._create_prediction_visualization(
                y_test, y_pred, feature_importance_df, best_model_name, output_image
            )

            return {
                "model_name": best_model_name,
                "metrics": metrics,
                "feature_importance": feature_importance_df,
                "output_image": output_image,
            }

        except Exception as e:
            error_handler = get_unified_error_handler("predict_stock_prices")
            error_handler.log_error(
                e,
                "株価予測エラー",
                {"input_file": input_file, "output_image": output_image},
            )
            self.logger.error(f"❌ 株価予測中にエラー: {e}")
            raise

    def get_system_status(self) -> Dict[str, Any]:
        """システム状態の取得"""
        return {
            "system_name": "統合J-Quantsシステム",
            "version": "2.0.0",
            "error_count": self.error_count,
            "has_valid_token": self.id_token is not None
            and (
                self.token_expires_at is None or datetime.now() < self.token_expires_at
            ),
            "token_expires_at": (
                self.token_expires_at.isoformat() if self.token_expires_at else None
            ),
            "config_loaded": bool(self.jquants_config and self.data_fetch_config),
            "features": [
                "データ取得",
                "データ前処理",
                "株価予測",
                "統合エラーハンドリング",
            ],
        }

    def _load_and_clean_data(self, input_file: str) -> pd.DataFrame:
        """データの読み込みとクリーニング（統合版）"""
        self.logger.info(f"📁 データを読み込み中: {input_file}")

        # 入力ファイルの検証
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"入力ファイルが見つかりません: {input_file}")

        # データの読み込み（エンコーディング自動検出）
        encodings = ["utf-8", "shift_jis", "cp932", "utf-8-sig"]
        df = None
        successful_encoding = None

        for encoding in encodings:
            try:
                df = pd.read_csv(input_file, encoding=encoding)
                successful_encoding = encoding
                self.logger.info(
                    f"✅ データ読み込み成功 (エンコーディング: {encoding})"
                )
                break
            except UnicodeDecodeError:
                continue

        if df is None:
            raise ValueError("ファイルのエンコーディングを特定できませんでした")

        if df.empty:
            raise ValueError("データファイルが空です")

        # 日付カラムの変換
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"])

        # 数値カラムの型変換
        numeric_columns = ["Open", "High", "Low", "Close", "Volume"]
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # 欠損値の処理
        df = self.type_safe_validator.safe_nan_handling(df, strategy="forward_fill")
        df = df.dropna()

        # 重複行の削除
        df = df.drop_duplicates()

        self.logger.info(f"📊 クリーニング後のデータ形状: {df.shape}")
        return df

    def _engineer_basic_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """基本的な特徴量エンジニアリング（統合版）"""
        self.logger.info("🔧 基本特徴量エンジニアリングを開始")

        # 基本的な移動平均
        basic_sma_windows = self.preprocessing_config.get(
            "sma_windows", [5, 10, 25, 50]
        )
        for window in basic_sma_windows:
            if f"SMA_{window}" not in df.columns:
                df[f"SMA_{window}"] = df["Close"].rolling(window=window).mean()

        # 基本的なラグ特徴量
        lag_days = self.preprocessing_config.get("lag_days", [1, 3, 5])
        for lag in lag_days:
            df[f"Close_lag_{lag}"] = df["Close"].shift(lag)

        self.logger.info("✅ 基本特徴量エンジニアリング完了")
        return df

    def _engineer_advanced_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """高度な技術指標による特徴量エンジニアリング（統合版）"""
        self.logger.info("🚀 高度な技術指標計算を開始")

        try:
            # 技術指標設定を取得
            technical_config = self.preprocessing_config.get(
                "technical_indicators", self.technical_indicators._get_default_config()
            )

            # 全ての技術指標を計算
            enhanced_df = self.technical_indicators.calculate_all_indicators(
                df, technical_config
            )

            # 新しく追加された指標をログ出力
            original_columns = set(df.columns)
            new_columns = [
                col for col in enhanced_df.columns if col not in original_columns
            ]

            self.logger.info(f"📈 追加された技術指標: {len(new_columns)}個")
            return enhanced_df

        except Exception as e:
            self.logger.error(f"❌ 技術指標計算中にエラー: {e}")
            self.logger.warning("🔄 基本特徴量のみで続行します")
            return df

    def _feature_selection_and_validation(self, df: pd.DataFrame) -> tuple:
        """特徴量選択と検証（統合版）"""
        self.logger.info("🎯 特徴量選択と検証を開始")

        # 利用可能な拡張特徴量リスト
        enhanced_features = get_enhanced_features_list()

        # 実際に存在する特徴量のみを選択
        available_features = [col for col in enhanced_features if col in df.columns]
        missing_features = [col for col in enhanced_features if col not in df.columns]

        self.logger.info(
            f"✅ 利用可能な特徴量: {len(available_features)}/{len(enhanced_features)}"
        )

        if missing_features:
            self.logger.warning(f"⚠️ 不足している特徴量: {len(missing_features)}個")

        # 型安全な無限値・異常値のチェック
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        validation_result = self.type_safe_validator.validate_numeric_columns(
            df, numeric_columns
        )

        if not validation_result["is_valid"]:
            self.logger.error("❌ 数値データの型安全性検証に失敗")
            for error in validation_result["errors"]:
                self.logger.error(f"  - {error}")
            raise ValueError("数値データの型安全性検証エラー")

        # 無限値の安全な処理
        inf_count = np.isinf(df.select_dtypes(include=[np.number])).sum().sum()
        if inf_count > 0:
            self.logger.warning(f"⚠️ 無限値を検出: {inf_count}個")
            df = df.replace([np.inf, -np.inf], np.nan)
            df = self.type_safe_validator.safe_nan_handling(df, strategy="forward_fill")

        return df, available_features

    def _validate_processed_data(self, df: pd.DataFrame) -> bool:
        """前処理済みデータの検証（統合版）"""
        self.logger.info("🔍 前処理済みデータの検証を開始")

        try:
            # データ検証の実行
            validation_results = self.data_validator.validate_stock_data(df)

            # 検証レポートの生成と表示
            report = self.data_validator.generate_validation_report(validation_results)
            self.logger.info(f"\n{report}")

            if not validation_results["is_valid"]:
                self.logger.error("❌ データ検証に失敗しました")
                return False

            self.logger.info("✅ データ検証が正常に完了しました")
            return True

        except Exception as e:
            self.logger.error(f"❌ データ検証中にエラー: {e}")
            return False

    def _create_prediction_visualization(
        self, y_test, y_pred, feature_importance_df, model_name: str, output_image: str
    ):
        """予測結果の可視化（統合版）"""
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

        # 特徴量重要度（上位10個）
        if not feature_importance_df.empty:
            plt.subplot(2, 2, 4)
            top_features = feature_importance_df.head(10)
            plt.barh(
                range(len(top_features)), top_features["importance"], color="skyblue"
            )
            plt.yticks(range(len(top_features)), top_features["feature"])
            plt.xlabel("重要度")
            plt.title("特徴量重要度 (Top 10)")
            plt.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(output_image, dpi=300, bbox_inches="tight")
        plt.close()  # メモリリークを防ぐ


def main():
    """メイン処理 - 完全統合システム"""
    # ログ設定
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    try:
        # 統合システムの初期化
        system = UnifiedJQuantsSystem()

        # システム状態の表示
        status = system.get_system_status()
        print(f"🚀 システム状態: {status}")

        # 完全統合パイプラインの実行
        from datetime import datetime

        today = datetime.now().strftime("%Y%m%d")

        print(f"\n🔄 完全統合パイプラインを開始...")

        # ステップ1: データ取得
        print(f"\n📊 ステップ1: 株価データ取得 ({today})")
        raw_data = system.fetch_stock_data(today)
        raw_output_file = f"stock_data_{today}.csv"
        system.save_data(raw_data, raw_output_file)
        print(f"✅ 生データ保存完了: {raw_output_file}")

        # ステップ2: データ前処理
        print(f"\n🔧 ステップ2: データ前処理")
        processed_data = system.preprocess_data(raw_output_file)
        processed_output_file = f"processed_stock_data_{today}.csv"
        processed_data.to_csv(processed_output_file, index=False)
        print(f"✅ 前処理完了: {processed_output_file}")

        # ステップ3: 株価予測
        print(f"\n🎯 ステップ3: 株価予測")
        prediction_result = system.predict_stock_prices(processed_output_file)
        print(f"✅ 予測完了: {prediction_result['output_image']}")
        print(
            f"📊 予測精度: MAE={prediction_result['metrics']['mae']:.4f}, R²={prediction_result['metrics']['r2']:.4f}"
        )

        print(f"\n🎉 完全統合パイプライン完了!")
        print(f"📁 出力ファイル:")
        print(f"  - 生データ: {raw_output_file}")
        print(f"  - 前処理済み: {processed_output_file}")
        print(f"  - 予測結果: {prediction_result['output_image']}")

    except Exception as e:
        print(f"❌ エラー: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
