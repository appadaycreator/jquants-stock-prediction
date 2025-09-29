import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';

export const dynamic = 'force-static';

export async function POST(request: NextRequest) {
  try {
    // 静的ホスティング環境ではプロセス制御は不可
    if (process.env.NEXT_RUNTIME === 'edge' || process.env.NODE_ENV === 'production') {
      return NextResponse.json({ 
        success: false, 
        error: '静的ホスティング環境では自動更新の停止はサポートされていません' 
      }, { status: 400 });
    }

    // 自動更新プロセスの停止
    const killProcess = spawn('pkill', ['-f', 'automated_scheduler.py'], {
      stdio: 'pipe'
    });

    return new Promise<Response>((resolve) => {
      killProcess.on('close', (code) => {
        resolve(NextResponse.json({ 
          success: true, 
          message: '自動更新を停止しました'
        }));
      });
    });

  } catch (error) {
    console.error('自動更新停止エラー:', error);
    return NextResponse.json({ 
      success: false, 
      error: '自動更新の停止に失敗しました' 
    }, { status: 500 });
  }
}
