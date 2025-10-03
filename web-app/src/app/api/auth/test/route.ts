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
    if (!credentials.email && !credentials.password && !credentials.refreshToken) {
      return NextResponse.json(
        {
          success: false,
          message: '認証情報が不足しています',
        },
        { status: 400 }
      );
    }

    // 接続テスト
    const isConnected = await AuthService.testConnection(credentials);
    
    if (isConnected) {
      return NextResponse.json({
        success: true,
        message: '接続テストが成功しました',
      });
    } else {
      return NextResponse.json(
        {
          success: false,
          message: '接続テストに失敗しました。認証情報を確認してください。',
        },
        { status: 401 }
      );
    }
  } catch (error) {
    console.error('接続テストエラー:', error);
    return NextResponse.json(
      {
        success: false,
        message: '接続テスト中にエラーが発生しました',
        error: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}
