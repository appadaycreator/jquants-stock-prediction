import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    // 通知履歴を取得
    // 実際の実装では、データベースから取得することを推奨
    const history = [
      {
        type: 'analysis_complete',
        title: '📊 株価分析完了',
        message: '分析が完了しました。3件の買い候補、1件の売り候補が見つかりました。',
        timestamp: new Date().toISOString(),
        priority: 'high'
      }
    ];
    
    return NextResponse.json(history);

  } catch (error) {
    console.error('通知履歴取得エラー:', error);
    return NextResponse.json([], { status: 500 });
  }
}
