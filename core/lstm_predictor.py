#!/usr/bin/env python3
"""
LSTM予測システム（個人投資用強化版）
参考記事のLSTMアプローチを統合システムに組み込み
"""

import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import MinMaxScaler
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta


class LSTMPredictor:
    """LSTM予測システム（個人投資用強化版）"""

    def __init__(self, logger=None, error_handler=None):
        """初期化"""
        self.logger = logger
        self.error_handler = error_handler
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.model = None
        self.sequence_length = 120  # 過去120日間のデータを使用

    def prepare_data(
        self, df: pd.DataFrame, target_column: str = "Close"
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        データの前処理（参考記事の手法を適用）
        """
        try:
            if self.logger:
                self.logger.log_info("LSTMデータ前処理開始")

            # 終値データを取得
            close_prices = df[target_column].values.reshape(-1, 1)

            # データを0-1の範囲に正規化
            scaled_data = self.scaler.fit_transform(close_prices)

            # 時系列データの作成
            X, y = [], []
            for i in range(self.sequence_length, len(scaled_data)):
                X.append(scaled_data[i - self.sequence_length : i, 0])
                y.append(scaled_data[i, 0])

            X, y = np.array(X), np.array(y)
            X = X.reshape((X.shape[0], X.shape[1], 1))  # LSTM用に形状を変換

            if self.logger:
                self.logger.log_info(f"LSTMデータ準備完了: {X.shape[0]}サンプル")

            return X, y

        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_data_processing_error(
                    e, "LSTMデータ前処理", {"target_column": target_column}
                )
            raise

    def build_model(self, input_shape: Tuple[int, int]) -> Sequential:
        """
        LSTMモデルの構築（参考記事のアーキテクチャを改良）
        """
        try:
            model = Sequential()

            # 第1層LSTM（return_sequences=Trueで次の層に出力）
            model.add(
                LSTM(25, return_sequences=True, input_shape=input_shape)
            )  # 50→25に削減
            model.add(Dropout(0.1))  # 0.2→0.1に削減

            # 第2層LSTM
            model.add(LSTM(25, return_sequences=False))  # 50→25に削減
            model.add(Dropout(0.1))  # 0.2→0.1に削減

            # 出力層
            model.add(Dense(1))

            # コンパイル
            model.compile(
                optimizer=Adam(learning_rate=0.01),  # 学習率を上げて高速化
                loss="mean_squared_error",
                metrics=["mae"],
            )

            if self.logger:
                self.logger.log_info("LSTMモデル構築完了")

            return model

        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_model_error(
                    e, "LSTMモデル構築", {"input_shape": input_shape}
                )
            raise

    def train_model(
        self, X: np.ndarray, y: np.ndarray, epochs: int = 10, batch_size: int = 32
    ) -> Dict[str, Any]:
        """
        モデルの訓練
        """
        try:
            if self.logger:
                self.logger.log_info(f"LSTMモデル訓練開始: {epochs}エポック")

            # データの分割（学習80%, 検証20%）
            split_index = int(len(X) * 0.8)
            X_train, X_val = X[:split_index], X[split_index:]
            y_train, y_val = y[:split_index], y[split_index:]

            # モデルの構築
            self.model = self.build_model((X.shape[1], 1))

            # 訓練
            history = self.model.fit(
                X_train,
                y_train,
                validation_data=(X_val, y_val),
                epochs=epochs,
                batch_size=batch_size,
                verbose=0,  # 出力を抑制して高速化
            )

            # 評価
            train_loss = self.model.evaluate(X_train, y_train, verbose=0)
            val_loss = self.model.evaluate(X_val, y_val, verbose=0)

            result = {
                "model": self.model,
                "history": history.history,
                "train_loss": train_loss[0],
                "val_loss": val_loss[0],
                "train_mae": train_loss[1],
                "val_mae": val_loss[1],
                "training_successful": True,
            }

            if self.logger:
                self.logger.log_info(
                    f"LSTM訓練完了: 訓練損失={train_loss[0]:.4f}, 検証損失={val_loss[0]:.4f}"
                )

            return result

        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_model_error(
                    e, "LSTMモデル訓練", {"epochs": epochs, "batch_size": batch_size}
                )
            raise

    def predict_future(self, last_sequence: np.ndarray, days: int = 22) -> List[float]:
        """
        未来の株価を予測（参考記事の手法）
        """
        try:
            if self.model is None:
                raise ValueError("モデルが訓練されていません")

            if self.logger:
                self.logger.log_info(f"LSTM未来予測開始: {days}日先")

            predictions = []
            current_sequence = last_sequence.copy()

            for _ in range(days):
                # 予測実行
                next_pred = self.model.predict(
                    current_sequence.reshape(1, -1, 1), verbose=0
                )
                predictions.append(next_pred[0, 0])

                # シーケンスを更新（最新の予測値を追加し、古い値を削除）
                current_sequence = np.roll(current_sequence, -1)
                current_sequence[-1] = next_pred[0, 0]

            # 正規化を元に戻す
            predictions = self.scaler.inverse_transform(
                np.array(predictions).reshape(-1, 1)
            ).flatten()

            if self.logger:
                self.logger.log_info(f"LSTM予測完了: {len(predictions)}日分")

            return predictions.tolist()

        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_model_error(e, "LSTM未来予測", {"days": days})
            raise

    def get_prediction_confidence(
        self, predictions: List[float], historical_volatility: float
    ) -> Dict[str, Any]:
        """
        予測の信頼度を計算
        """
        try:
            # 予測の変動性を計算
            prediction_volatility = np.std(np.diff(predictions))

            # 信頼度スコア（0-1）
            confidence = max(
                0, min(1, 1 - (prediction_volatility / historical_volatility))
            )

            # リスクレベル
            if confidence > 0.8:
                risk_level = "低"
            elif confidence > 0.6:
                risk_level = "中"
            else:
                risk_level = "高"

            return {
                "confidence": confidence,
                "risk_level": risk_level,
                "prediction_volatility": prediction_volatility,
                "historical_volatility": historical_volatility,
            }

        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_model_error(e, "LSTM信頼度計算", {})
            return {
                "confidence": 0.5,
                "risk_level": "中",
                "prediction_volatility": 0,
                "historical_volatility": 0,
            }

    def create_visualization_data(
        self,
        historical_data: pd.DataFrame,
        predictions: List[float],
        prediction_dates: List[str],
    ) -> Dict[str, Any]:
        """
        可視化用データの作成
        """
        try:
            # 過去データの準備
            historical_prices = historical_data["Close"].tolist()
            historical_dates = historical_data.index.strftime("%Y-%m-%d").tolist()

            # 予測データの準備
            prediction_prices = predictions
            prediction_dates = prediction_dates

            return {
                "historical": {"dates": historical_dates, "prices": historical_prices},
                "predictions": {"dates": prediction_dates, "prices": prediction_prices},
                "metadata": {
                    "model_type": "LSTM",
                    "sequence_length": self.sequence_length,
                    "prediction_days": len(predictions),
                    "generated_at": datetime.now().isoformat(),
                },
            }

        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_data_processing_error(
                    e, "LSTM可視化データ作成", {}
                )
            return {}

    def run_complete_prediction(
        self, df: pd.DataFrame, target_column: str = "Close", prediction_days: int = 22
    ) -> Dict[str, Any]:
        """
        完全なLSTM予測パイプラインの実行
        """
        try:
            if self.logger:
                self.logger.log_info("LSTM完全予測パイプライン開始")

            # データ準備
            X, y = self.prepare_data(df, target_column)

            # モデル訓練
            training_result = self.train_model(X, y)

            # 最後のシーケンスを取得
            last_sequence = X[-1]

            # 未来予測
            predictions = self.predict_future(last_sequence, prediction_days)

            # 信頼度計算
            historical_volatility = df[target_column].pct_change().std()
            confidence_info = self.get_prediction_confidence(
                predictions, historical_volatility
            )

            # 予測日付の生成
            last_date = df.index[-1]
            prediction_dates = [
                (last_date + timedelta(days=i)).strftime("%Y-%m-%d")
                for i in range(1, prediction_days + 1)
            ]

            # 可視化データ
            viz_data = self.create_visualization_data(df, predictions, prediction_dates)

            result = {
                "predictions": predictions,
                "prediction_dates": prediction_dates,
                "confidence": confidence_info,
                "training_result": training_result,
                "visualization_data": viz_data,
                "model_info": {
                    "type": "LSTM",
                    "sequence_length": self.sequence_length,
                    "prediction_days": prediction_days,
                },
            }

            if self.logger:
                self.logger.log_info("LSTM完全予測パイプライン完了")

            return result

        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_model_error(
                    e, "LSTM完全予測", {"prediction_days": prediction_days}
                )
            raise
