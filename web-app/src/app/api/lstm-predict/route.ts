import { NextRequest, NextResponse } from "next/server";
import { spawn } from "child_process";
import path from "path";
import fs from "fs";

interface LSTMPredictionRequest {
  symbol: string;
  prediction_days?: number;
}

export async function POST(request: NextRequest) {
  try {
    const body: LSTMPredictionRequest = await request.json();
    const { symbol, prediction_days = 22 } = body;

    if (!symbol) {
      return NextResponse.json(
        { error: "銘柄コードが必要です" },
        { status: 400 },
      );
    }

    // Pythonスクリプトの実行
    const projectRoot = path.join(process.cwd(), "..");
    const pythonScript = path.join(projectRoot, "core", "lstm_predictor.py");
    const venvPython = path.join(projectRoot, "venv", "bin", "python3");
    
    // 仮想環境のPythonが存在するかチェック
    const pythonPath = fs.existsSync(venvPython) ? venvPython : "python3";

    return new Promise((resolve) => {
      const pythonProcess = spawn(pythonPath, [
        "-c",
        `
import sys
import os
import io

# 標準エラー出力を抑制
sys.stderr = io.StringIO()

sys.path.append('${projectRoot}')

# TensorFlowのログレベルを設定（インポート前に設定）
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import tensorflow as tf
tf.get_logger().setLevel('ERROR')

from core.lstm_predictor import LSTMPredictor
import pandas as pd
import json
from datetime import datetime, timedelta
import numpy as np

# サンプルデータの生成（実際の運用ではJ-Quants APIから取得）
def generate_sample_data(symbol, days=365):
    """サンプル株価データを生成"""
    np.random.seed(42)  # 再現性のため
    dates = pd.date_range(start=datetime.now() - timedelta(days=days), end=datetime.now(), freq='D')
    
    # 基本的な株価トレンドを生成
    base_price = 2000 + hash(symbol) % 3000  # 銘柄ごとに異なる基本価格
    trend = np.linspace(0, 0.2, len(dates))  # 上昇トレンド
    noise = np.random.normal(0, 0.02, len(dates))  # ランダムノイズ
    
    prices = base_price * (1 + trend + noise)
    
    return pd.DataFrame({
        'Close': prices,
        'Open': prices * (1 + np.random.normal(0, 0.01, len(dates))),
        'High': prices * (1 + np.abs(np.random.normal(0, 0.02, len(dates)))),
        'Low': prices * (1 - np.abs(np.random.normal(0, 0.02, len(dates)))),
        'Volume': np.random.randint(100000, 1000000, len(dates))
    }, index=dates)

# ログ設定（API用にログを抑制）
class SimpleLogger:
    def log_info(self, message):
        pass  # ログを抑制
    
    def log_error(self, message):
        pass  # ログを抑制

class SimpleErrorHandler:
    def handle_data_processing_error(self, error, context, details):
        raise error
    
    def handle_model_error(self, error, context, details):
        raise error

# LSTMPredictorをオーバーライドしてverbose=0に設定
class SilentLSTMPredictor(LSTMPredictor):
    def train_model(self, X, y, epochs=20, batch_size=32):
        # データの分割（学習80%, 検証20%）
        split_index = int(len(X) * 0.8)
        X_train, X_val = X[:split_index], X[split_index:]
        y_train, y_val = y[:split_index], y[split_index:]
        
        # モデルの構築
        self.model = self.build_model((X.shape[1], 1))
        
        # 訓練（verbose=0で実行）
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            verbose=0  # ログを抑制
        )
        
        # 評価
        train_loss = self.model.evaluate(X_train, y_train, verbose=0)
        val_loss = self.model.evaluate(X_val, y_val, verbose=0)
        
        result = {
            'model': self.model,
            'history': history.history,
            'train_loss': train_loss[0],
            'val_loss': val_loss[0],
            'train_mae': train_loss[1],
            'val_mae': val_loss[1]
        }
        
        return result

# メイン処理
try:
    logger = SimpleLogger()
    error_handler = SimpleErrorHandler()
    
    # LSTM予測器の初期化（verboseを抑制したバージョン）
    lstm_predictor = SilentLSTMPredictor(logger, error_handler)
    
    # サンプルデータの生成
    df = generate_sample_data('${symbol}')
    
    # LSTM予測の実行
    result = lstm_predictor.run_complete_prediction(df, 'Close', ${prediction_days})
    
    # 結果をJSONで出力（JSONのみを出力）
    print(json.dumps(result, default=str, ensure_ascii=False))
    
except Exception as e:
    print(json.dumps({
        'error': str(e),
        'type': 'LSTM_PREDICTION_ERROR'
    }, ensure_ascii=False))
    sys.exit(1)
        `,
      ]);

      let output = "";
      let errorOutput = "";

      pythonProcess.stdout.on("data", (data) => {
        output += data.toString();
      });

      pythonProcess.stderr.on("data", (data) => {
        errorOutput += data.toString();
      });

      pythonProcess.on("close", (code) => {
        if (code === 0) {
          try {
            const result = JSON.parse(output);
            resolve(NextResponse.json(result));
          } catch (parseError) {
            console.error("JSON解析エラー:", parseError);
            console.error("出力:", output);
            resolve(NextResponse.json(
              { 
                error: "予測結果の解析に失敗しました",
                details: output,
                parseError: parseError.message,
              },
              { status: 500 },
            ));
          }
        } else {
          console.error("Python実行エラー:", errorOutput);
          resolve(NextResponse.json(
            { 
              error: "LSTM予測の実行に失敗しました",
              details: errorOutput,
              exitCode: code,
            },
            { status: 500 },
          ));
        }
      });

      pythonProcess.on("error", (error) => {
        console.error("Pythonプロセスエラー:", error);
        resolve(NextResponse.json(
          { 
            error: "Pythonプロセスの起動に失敗しました",
            details: error.message,
          },
          { status: 500 },
        ));
      });
    });

  } catch (error) {
    console.error("LSTM予測APIエラー:", error);
    return NextResponse.json(
      { 
        error: "LSTM予測APIでエラーが発生しました",
        details: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 },
    );
  }
}
