import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';

export async function POST(request: NextRequest) {
  try {
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
