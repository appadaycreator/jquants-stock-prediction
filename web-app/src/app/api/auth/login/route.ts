import { NextRequest, NextResponse } from 'next/server';

// 静的エクスポート用の設定
export const dynamic = 'force-static';

/**
 * J-Quants API認証エンドポイント
 * ローカル環境での認証をサポート
 */

export async function POST(request: NextRequest) {
  try {
    const { email, password } = await request.json();

    if (!email || !password) {
      return NextResponse.json(
        { error: 'メールアドレスとパスワードが必要です' },
        { status: 400 }
      );
    }

    // J-Quants APIにログイン
    const loginResponse = await fetch('https://api.jquants.com/v1/token/auth_user', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        mailaddress: email,
        password: password,
      }),
    });

    if (!loginResponse.ok) {
      return NextResponse.json(
        { error: 'J-Quants API認証に失敗しました' },
        { status: 401 }
      );
    }

    const loginData = await loginResponse.json();

    // リフレッシュトークンを使用してIDトークンを取得
    const tokenResponse = await fetch('https://api.jquants.com/v1/token/auth_refresh', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        refreshtoken: loginData.refreshtoken,
      }),
    });

    if (!tokenResponse.ok) {
      return NextResponse.json(
        { error: 'IDトークンの取得に失敗しました' },
        { status: 401 }
      );
    }

    const tokenData = await tokenResponse.json();

    return NextResponse.json({
      id_token: tokenData.idtoken,
      refresh_token: loginData.refreshtoken,
      expires_in: 86400, // 24時間
    });

  } catch (error) {
    console.error('認証エラー:', error);
    return NextResponse.json(
      { error: '認証処理中にエラーが発生しました' },
      { status: 500 }
    );
  }
}
