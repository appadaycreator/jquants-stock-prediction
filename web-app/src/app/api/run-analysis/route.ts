import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';

export const dynamic = 'force-static';

export async function POST(request: NextRequest) {
  try {
    const { analysisType = 'comprehensive', symbols = [] } = await request.json();
    
    console.log(`分析実行開始: ${analysisType}, 銘柄: ${symbols.join(', ')}`);
    
    // 分析タイプに応じてスクリプトを選択
    let pythonScript: string;
    let scriptArgs: string[] = [];
    
    switch (analysisType) {
      case 'comprehensive':
        // 統合システムを使用
        pythonScript = path.join(process.cwd(), '..', 'unified_jquants_system.py');
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
        pythonScript = path.join(process.cwd(), '..', 'unified_jquants_system.py');
    }

    console.log(`実行スクリプト: ${pythonScript}`);
    console.log(`引数: ${scriptArgs.join(' ')}`);

    // Pythonスクリプトの実行
    const pythonProcess = spawn('python3', [pythonScript, ...scriptArgs], {
      cwd: process.cwd(),
      stdio: 'pipe',
      env: { ...process.env, PYTHONPATH: process.cwd() }
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
