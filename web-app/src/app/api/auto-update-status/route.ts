import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';

export async function GET(request: NextRequest) {
  try {
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
