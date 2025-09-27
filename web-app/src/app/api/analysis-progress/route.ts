import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

// メモリ内での進捗管理（本番環境ではRedis等を使用）
const progressStore = new Map<string, {
  progress: number;
  status: string;
  startTime: number;
  endTime?: number;
  result?: any;
  error?: string;
}>();

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const analysisId = searchParams.get('id');
    
    if (!analysisId) {
      return NextResponse.json(
        { error: '分析IDが必要です' },
        { status: 400 }
      );
    }
    
    const progress = progressStore.get(analysisId);
    
    if (!progress) {
      return NextResponse.json({
        analysisId,
        progress: 0,
        status: 'not_found',
        message: '分析が見つかりません'
      });
    }
    
    const elapsed = Date.now() - progress.startTime;
    const elapsedMinutes = Math.floor(elapsed / 60000);
    const elapsedSeconds = Math.floor((elapsed % 60000) / 1000);
    
    return NextResponse.json({
      analysisId,
      progress: progress.progress,
      status: progress.status,
      message: progress.status,
      elapsed: `${elapsedMinutes}:${elapsedSeconds.toString().padStart(2, '0')}`,
      result: progress.result,
      error: progress.error,
      completed: !!progress.endTime
    });
    
  } catch (error) {
    console.error('進捗取得エラー:', error);
    return NextResponse.json(
      { error: '進捗取得エラー' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const { analysisId, progress, status, result, error } = await request.json();
    
    if (!analysisId) {
      return NextResponse.json(
        { error: '分析IDが必要です' },
        { status: 400 }
      );
    }
    
    const current = progressStore.get(analysisId) || {
      progress: 0,
      status: 'initializing',
      startTime: Date.now()
    };
    
    const updated = {
      ...current,
      progress: progress ?? current.progress,
      status: status ?? current.status,
      result: result ?? current.result,
      error: error ?? current.error,
      endTime: (result || error) ? Date.now() : current.endTime
    };
    
    progressStore.set(analysisId, updated);
    
    // 古い進捗データのクリーンアップ（1時間以上前）
    const oneHourAgo = Date.now() - 60 * 60 * 1000;
    for (const [id, data] of progressStore.entries()) {
      if (data.startTime < oneHourAgo) {
        progressStore.delete(id);
      }
    }
    
    return NextResponse.json({
      success: true,
      analysisId,
      progress: updated.progress,
      status: updated.status
    });
    
  } catch (error) {
    console.error('進捗更新エラー:', error);
    return NextResponse.json(
      { error: '進捗更新エラー' },
      { status: 500 }
    );
  }
}

export async function DELETE(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const analysisId = searchParams.get('id');
    
    if (!analysisId) {
      return NextResponse.json(
        { error: '分析IDが必要です' },
        { status: 400 }
      );
    }
    
    progressStore.delete(analysisId);
    
    return NextResponse.json({
      success: true,
      message: '進捗データを削除しました'
    });
    
  } catch (error) {
    console.error('進捗削除エラー:', error);
    return NextResponse.json(
      { error: '進捗削除エラー' },
      { status: 500 }
    );
  }
}
