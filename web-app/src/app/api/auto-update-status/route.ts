import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';

// GitHub Pagesの静的エクスポート環境ではSSR/Edgeは無効のため静的化
export const dynamic = 'force-static';

export async function GET(request: NextRequest) {
  try {
    // 静的エクスポート（GitHub Pages）ではプロセス確認はできないため固定レスポンス
    if (process.env.NEXT_RUNTIME === 'edge' || process.env.NODE_ENV === 'production') {
      return NextResponse.json({
        status: 'unsupported',
        message: '静的ホスティング環境ではステータス確認はサポートされていません'
      });
    }

    // 自動更新プロセスの状態を確認
    const checkProcess = spawn('pgrep', ['-f', 'automated_scheduler.py'], {
      stdio: 'pipe'
    });

    return new Promise<Response>((resolve) => {
      checkProcess.on('close', (code) => {
        if (code === 0) {
          // プロセスが実行中
          resolve(NextResponse.json({ 
            status: 'running',
            message: '自動更新が実行中です'
          }));
        } else {
          // プロセスが停止中
          resolve(NextResponse.json({ 
            status: 'stopped',
            message: '自動更新が停止中です'
          }));
        }
      });
    });

  } catch (error) {
    console.error('自動更新ステータス確認エラー:', error);
    return NextResponse.json({ 
      status: 'unknown',
      message: 'ステータスの確認に失敗しました'
    }, { status: 500 });
  }
}
