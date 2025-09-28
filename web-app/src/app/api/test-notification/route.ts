import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';

export async function POST(request: NextRequest) {
  try {
    const { type } = await request.json();
    
    if (!type || !['email', 'slack'].includes(type)) {
      return NextResponse.json({ 
        success: false, 
        error: '無効な通知タイプです' 
      }, { status: 400 });
    }

    // テスト通知の実行
    const pythonScript = path.join(process.cwd(), '..', 'test_notification.py');
    
    const pythonProcess = spawn('python3', [pythonScript, type], {
      cwd: process.cwd(),
      stdio: 'pipe',
      env: { ...process.env, PYTHONPATH: process.cwd() }
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
            message: `${type}通知のテストが成功しました` 
          }));
        } else {
          resolve(NextResponse.json({ 
            success: false, 
            error: stderr || '通知テストに失敗しました' 
          }, { status: 500 }));
        }
      });
    });

  } catch (error) {
    console.error('通知テストエラー:', error);
    return NextResponse.json({ 
      success: false, 
      error: '通知テストの実行に失敗しました' 
    }, { status: 500 });
  }
}
