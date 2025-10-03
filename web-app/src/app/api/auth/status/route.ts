import { NextRequest, NextResponse } from 'next/server';
import { JQuantsAuthManager } from '@/lib/jquants-auth-manager';

export async function GET(request: NextRequest) {
  try {
    const authManager = new JQuantsAuthManager();
    
    // 環境変数の確認
    const envStatus = {
      hasIdToken: !!process.env.JQUANTS_ID_TOKEN,
      hasRefreshToken: !!process.env.JQUANTS_REFRESH_TOKEN,
      hasEmail: !!process.env.JQUANTS_EMAIL,
      hasPassword: !!process.env.JQUANTS_PASSWORD,
      hasPublicIdToken: !!process.env.NEXT_PUBLIC_JQUANTS_ID_TOKEN,
      hasPublicRefreshToken: !!process.env.NEXT_PUBLIC_JQUANTS_REFRESH_TOKEN,
      hasPublicEmail: !!process.env.NEXT_PUBLIC_JQUANTS_EMAIL,
      hasPublicPassword: !!process.env.NEXT_PUBLIC_JQUANTS_PASSWORD,
    };

    // トークンの有効性チェック
    const isTokenValid = await authManager.isTokenValid();
    
    // 有効なトークンの取得を試行
    const validToken = await authManager.getValidToken();

    return NextResponse.json({
      status: 'success',
      timestamp: new Date().toISOString(),
      environment: {
        nodeEnv: process.env.NODE_ENV,
        appEnv: process.env.NEXT_PUBLIC_APP_ENV,
      },
      credentials: envStatus,
      authentication: {
        isTokenValid,
        hasValidToken: !!validToken,
        tokenLength: validToken ? validToken.length : 0,
      },
      recommendations: generateRecommendations(envStatus, isTokenValid, !!validToken),
    });
  } catch (error) {
    console.error('認証ステータス確認エラー:', error);
    return NextResponse.json(
      {
        status: 'error',
        message: '認証ステータスの確認に失敗しました',
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    );
  }
}

function generateRecommendations(
  envStatus: Record<string, boolean>,
  isTokenValid: boolean,
  hasValidToken: boolean
): string[] {
  const recommendations: string[] = [];

  if (!envStatus.hasIdToken && !envStatus.hasEmail) {
    recommendations.push('JQUANTS_ID_TOKEN または JQUANTS_EMAIL を設定してください');
  }

  if (envStatus.hasEmail && !envStatus.hasPassword) {
    recommendations.push('JQUANTS_PASSWORD を設定してください');
  }

  if (!isTokenValid && !hasValidToken) {
    recommendations.push('認証情報が無効です。新しいトークンを取得してください');
  }

  if (envStatus.hasPublicIdToken || envStatus.hasPublicEmail) {
    recommendations.push('NEXT_PUBLIC_* 環境変数は機密情報を含むため、サーバーサイドでは使用しないでください');
  }

  if (recommendations.length === 0) {
    recommendations.push('認証設定は正常です');
  }

  return recommendations;
}