import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';

// 静的エクスポート用の設定
export const dynamic = 'force-static';

export async function POST(request: NextRequest) {
  try {
    const { symbols } = await request.json();
    
    if (!symbols || !Array.isArray(symbols) || symbols.length === 0) {
      return NextResponse.json(
        { error: '銘柄が指定されていません' },
        { status: 400 }
      );
    }

    // Pythonスクリプトの実行
    const pythonScript = path.join(process.cwd(), '..', 'web_symbol_analysis.py');
    const pythonProcess = spawn('python3', [pythonScript, ...symbols], {
      cwd: process.cwd(),
      stdio: 'pipe'
    });

    let stdout = '';
    let stderr = '';

    pythonProcess.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    return new Promise<NextResponse>((resolve) => {
      pythonProcess.on('close', (code) => {
        if (code === 0) {
          resolve(NextResponse.json({
            success: true,
            message: '分析が完了しました',
            symbols: symbols,
            output: stdout
          }));
        } else {
          resolve(NextResponse.json({
            success: false,
            error: '分析に失敗しました',
            details: stderr
          }, { status: 500 }));
        }
      });
    });

  } catch (error) {
    console.error('API エラー:', error);
    return NextResponse.json(
      { error: 'サーバーエラーが発生しました' },
      { status: 500 }
    );
  }
}
