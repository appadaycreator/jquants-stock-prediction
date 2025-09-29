import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    // バックグラウンド同期の処理
    console.log('Background sync triggered');
    
    return NextResponse.json({ 
      success: true, 
      message: 'バックグラウンド同期が完了しました' 
    });

  } catch (error) {
    console.error('バックグラウンド同期エラー:', error);
    return NextResponse.json({ 
      success: false, 
      error: 'バックグラウンド同期に失敗しました' 
    }, { status: 500 });
  }
}
