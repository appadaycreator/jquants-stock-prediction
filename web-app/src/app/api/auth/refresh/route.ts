import { NextRequest, NextResponse } from 'next/server';
import { JQuantsAuthManager } from '@/lib/jquants-auth-manager';

/**
 * トークンリフレッシュ用APIエンドポイント
 * POST /api/auth/refresh
 */
export async function POST(request: NextRequest) {
  try {
    const authManager = new JQuantsAuthManager();
    
    // 新しいトークンを取得
    const newToken = await authManager.getValidToken();
    
    if (!newToken) {
      return NextResponse.json(
        { 
          error: 'Token refresh failed',
          message: 'トークンの更新に失敗しました',
          retry_hint: 'check_credentials'
        },
        { status: 401 }
      );
    }

    return NextResponse.json({
      success: true,
      message: 'トークンの更新に成功しました',
      token_length: newToken.length,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('トークンリフレッシュエラー:', error);
    return NextResponse.json(
      { 
        error: 'Token refresh failed',
        message: 'トークンの更新に失敗しました',
        retry_hint: 'check_credentials'
      },
      { status: 500 }
    );
  }
}