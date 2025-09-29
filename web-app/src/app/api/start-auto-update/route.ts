import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';

export const dynamic = 'force-static';

export async function POST(request: NextRequest) {
  try {
    // 静的ホスティング環境ではサーバープロセス起動は不可
    if (process.env.NEXT_RUNTIME === 'edge' || process.env.NODE_ENV === 'production') {
      return NextResponse.json({
        success: false,
        error: '静的ホスティング環境では自動更新の開始はサポートされていません'
      }, { status: 400 });
    }

    const { schedule } = await request.json();
    
    // 自動更新スクリプトの実行
    const pythonScript = path.join(process.cwd(), '..', 'automated_scheduler.py');
    
    const pythonProcess = spawn('python3', [pythonScript, '--immediate'], {
      cwd: process.cwd(),
      stdio: 'pipe',
      env: { 
        ...process.env, 
        PYTHONPATH: process.cwd(),
        AUTO_UPDATE_ENABLED: 'true',
        SCHEDULE_MORNING: schedule?.morning_analysis || '09:00',
        SCHEDULE_EVENING: schedule?.evening_analysis || '15:00',
        TIMEZONE: schedule?.timezone || 'Asia/Tokyo'
      }
    });

    let stdout = '';
    let stderr = '';

    pythonProcess.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    return new Promise<Response>((resolve) => {
      pythonProcess.on('close', (code) => {
        if (code === 0) {
          resolve(NextResponse.json({ 
            success: true, 
            message: '自動更新を開始しました',
            output: stdout
          }));
        } else {
          resolve(NextResponse.json({ 
            success: false, 
            error: stderr || '自動更新の開始に失敗しました' 
          }, { status: 500 }));
        }
      });
    });

  } catch (error) {
    console.error('自動更新開始エラー:', error);
    return NextResponse.json({ 
      success: false, 
      error: '自動更新の開始に失敗しました' 
    }, { status: 500 });
  }
}
