import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const subscription = await request.json();
    
    // プッシュ通知の購読情報を保存
    // 実際の実装では、データベースに保存することを推奨
    console.log('Push subscription received:', subscription);
    
    return NextResponse.json({ 
      success: true, 
      message: 'プッシュ通知の購読を登録しました' 
    });

  } catch (error) {
    console.error('プッシュ通知購読エラー:', error);
    return NextResponse.json({ 
      success: false, 
      error: 'プッシュ通知の購読に失敗しました' 
    }, { status: 500 });
  }
}
