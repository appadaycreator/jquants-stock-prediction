import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    // 環境変数からJ-Quants IDトークンを取得
    const idToken = process.env.JQUANTS_ID_TOKEN;
    
    if (!idToken) {
      return NextResponse.json(
        { error: 'J-Quants IDトークンが設定されていません' },
        { status: 404 }
      );
    }

    return NextResponse.json({ token: idToken });
  } catch (error) {
    console.error('トークン取得エラー:', error);
    return NextResponse.json(
      { error: 'トークンの取得に失敗しました' },
      { status: 500 }
    );
  }
}
