import { NextRequest, NextResponse } from 'next/server';
import { JQuantsAuthManager } from '@/lib/jquants-auth-manager';

/**
 * 認証テスト用APIエンドポイント
 * GET /api/auth/test
 */
export async function GET(request: NextRequest) {
  try {
    const authManager = new JQuantsAuthManager();
    
    // トークンの有効性をチェック
    const isValid = await authManager.isTokenValid();
    
    if (!isValid) {
      return NextResponse.json(
        { 
          error: 'Authentication failed',
          message: '認証トークンが無効です',
          retry_hint: 'refresh_token'
        },
        { status: 401 }
      );
    }

    // 有効なトークンを取得
    const token = await authManager.getValidToken();
    
    if (!token) {
      return NextResponse.json(
        { 
          error: 'Token retrieval failed',
          message: 'トークンの取得に失敗しました',
          retry_hint: 'check_credentials'
        },
        { status: 401 }
      );
    }

    return NextResponse.json({
      success: true,
      message: '認証が成功しました',
      token_length: token.length,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('認証テストエラー:', error);
    return NextResponse.json(
      { 
        error: 'Authentication test failed',
        message: '認証テストに失敗しました',
        retry_hint: 'check_credentials'
      },
      { status: 500 }
    );
  }
}