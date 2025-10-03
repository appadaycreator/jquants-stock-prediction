import { NextRequest, NextResponse } from 'next/server';
import { AuthService, AuthCredentials } from '@/lib/auth/AuthService';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const credentials: AuthCredentials = {
      email: body.email,
      password: body.password,
      refreshToken: body.refreshToken,
    };

    // 入力検証
    if (!credentials.refreshToken && (!credentials.email || !credentials.password)) {
      return NextResponse.json(
        {
          success: false,
          message: '認証情報が不足しています',
        },
        { status: 400 }
      );
    }

    // 認証情報の保存
    await AuthService.saveCredentials(credentials);
    
    return NextResponse.json({
      success: true,
      message: '認証情報が保存されました',
    });
  } catch (error) {
    console.error('認証情報保存エラー:', error);
    return NextResponse.json(
      {
        success: false,
        message: '認証情報の保存に失敗しました',
        error: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}
