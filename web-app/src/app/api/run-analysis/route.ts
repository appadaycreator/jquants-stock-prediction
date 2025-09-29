import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';

export const dynamic = 'force-static';

export async function POST(request: NextRequest) {
  try {
    const { 
      analysisType = 'comprehensive', 
      symbols = [],
      // 設定パラメータを追加
      prediction_days,
      primary_model,
      compare_models,
      auto_retrain,
      retrain_frequency,
      max_data_points,
      include_technical_indicators,
      selected_features,
      use_settings = false
    } = await request.json();
    
    console.log(`分析実行開始: ${analysisType}, 銘柄: ${symbols.join(', ')}`);
    if (use_settings) {
      console.log(`設定使用: 予測期間=${prediction_days}日, モデル=${primary_model}, 比較=${compare_models}, 再訓練=${auto_retrain}`);
    }
    
    // 分析タイプに応じてスクリプトを選択
    let pythonScript: string;
    let scriptArgs: string[] = [];
    
    // 設定が有効な場合は設定ファイルを生成
    if (use_settings) {
      const configData = {
        prediction: {
          days: prediction_days || 30
        },
        model: {
          type: "all",
          primary_model: primary_model || "xgboost",
          compare_models: compare_models || false,
          auto_retrain: auto_retrain || false,
          retrain_frequency: retrain_frequency || "weekly"
        },
        data: {
          refresh_interval: "daily",
          max_data_points: max_data_points || 1000,
          include_technical_indicators: include_technical_indicators !== false
        },
        features: {
          selected: selected_features || ["sma_5", "sma_10", "sma_25", "sma_50", "rsi", "macd"]
        }
      };
      
      // 設定ファイルを一時的に保存
      const fs = require('fs');
      const configPath = path.join(process.cwd(), '..', 'temp_analysis_config.json');
      fs.writeFileSync(configPath, JSON.stringify(configData, null, 2));
      console.log(`設定ファイル生成: ${configPath}`);
    }
    
    switch (analysisType) {
      case 'ultra_fast':
        // 超高速分析モード - 最適化された統合システム
        pythonScript = path.join(process.cwd(), '..', 'web_analysis_runner.py');
        scriptArgs = ['ultra_fast'];
        break;
      case 'comprehensive':
        // 統合システムを使用（新しいシステムに変更）
        pythonScript = path.join(process.cwd(), '..', 'unified_system.py');
        break;
      case 'symbols':
        // 銘柄分析システムを使用
        pythonScript = path.join(process.cwd(), '..', 'web_symbol_analysis.py');
        scriptArgs = symbols;
        break;
      case 'trading':
        // 統合トレーディングシステムを使用
        pythonScript = path.join(process.cwd(), '..', 'integrated_trading_system.py');
        break;
      case 'sentiment':
        // 感情分析システムを使用
        pythonScript = path.join(process.cwd(), '..', 'integrated_sentiment_enhancement.py');
        break;
      default:
        pythonScript = path.join(process.cwd(), '..', 'unified_system.py');
    }

    console.log(`実行スクリプト: ${pythonScript}`);
    console.log(`引数: ${scriptArgs.join(' ')}`);

    // Pythonスクリプトの実行（仮想環境のPythonを使用）
    const pythonProcess = spawn('/Users/masayukitokunaga/workspace/jquants-stock-prediction/venv/bin/python3', [pythonScript, ...scriptArgs], {
      cwd: path.join(process.cwd(), '..'), // プロジェクトルートに移動
      stdio: 'pipe',
      env: { ...process.env, PYTHONPATH: path.join(process.cwd(), '..') }
    });

    let stdout = '';
    let stderr = '';
    let progress = 0;

    // 進捗を追跡するための正規表現
    const progressPatterns = [
      /ステップ1|Step 1|データ取得|Data fetching/i,
      /ステップ2|Step 2|データ前処理|Data preprocessing/i,
      /ステップ3|Step 3|予測実行|Prediction/i,
      /ステップ4|Step 4|分析完了|Analysis complete/i
    ];

    pythonProcess.stdout.on('data', (data) => {
      const output = data.toString();
      stdout += output;
      
      // 進捗の検出
      for (let i = 0; i < progressPatterns.length; i++) {
        if (progressPatterns[i].test(output)) {
          progress = Math.max(progress, (i + 1) * 25);
          break;
        }
      }
      
      console.log(`[STDOUT] ${output.trim()}`);
    });

    pythonProcess.stderr.on('data', (data) => {
      const error = data.toString();
      stderr += error;
      console.error(`[STDERR] ${error.trim()}`);
    });

    return new Promise<NextResponse>((resolve) => {
      const timeout = setTimeout(() => {
        pythonProcess.kill('SIGTERM');
        resolve(NextResponse.json({
          success: false,
          error: '分析がタイムアウトしました（5分）',
          progress: 100
        }, { status: 408 }));
      }, 5 * 60 * 1000); // 5分のタイムアウト

      pythonProcess.on('close', (code) => {
        clearTimeout(timeout);
        
        if (code === 0) {
          // 成功時はWebデータも生成
          try {
            const generateWebData = spawn('python3', [
              path.join(process.cwd(), '..', 'generate_web_data.py')
            ], {
              cwd: process.cwd(),
              stdio: 'pipe'
            });

            generateWebData.on('close', (webCode) => {
              resolve(NextResponse.json({
                success: true,
                message: '分析が完了しました',
                analysisType,
                symbols,
                progress: 100,
                output: stdout,
                webDataGenerated: webCode === 0
              }));
            });
          } catch (webError) {
            resolve(NextResponse.json({
              success: true,
              message: '分析が完了しました（Webデータ生成でエラー）',
              analysisType,
              symbols,
              progress: 100,
              output: stdout,
              webDataGenerated: false,
              webError: webError instanceof Error ? webError.message : String(webError)
            }));
          }
        } else {
          resolve(NextResponse.json({
            success: false,
            error: '分析に失敗しました',
            details: stderr,
            progress: progress,
            output: stdout
          }, { status: 500 }));
        }
      });

      pythonProcess.on('error', (error) => {
        clearTimeout(timeout);
        resolve(NextResponse.json({
          success: false,
          error: 'Pythonプロセスの実行に失敗しました',
          details: error.message,
          progress: progress
        }, { status: 500 }));
      });
    });

  } catch (error) {
    console.error('API エラー:', error);
    return NextResponse.json(
      { 
        error: 'サーバーエラーが発生しました',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}

// 進捗取得用のGETエンドポイント
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const analysisId = searchParams.get('id');
    
    // 実際の実装では、Redisやメモリキャッシュから進捗を取得
    // ここでは簡易的な実装
    return NextResponse.json({
      analysisId,
      progress: 0,
      status: 'idle',
      message: '分析待機中'
    });
  } catch (error) {
    return NextResponse.json(
      { error: '進捗取得エラー' },
      { status: 500 }
    );
  }
}
