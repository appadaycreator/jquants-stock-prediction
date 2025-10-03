import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const health = {
      status: 'ok',
      timestamp: new Date().toISOString(),
      environment: {
        nodeEnv: process.env.NODE_ENV,
        hasIdToken: !!process.env.JQUANTS_ID_TOKEN,
        hasRefreshToken: !!process.env.JQUANTS_REFRESH_TOKEN,
        hasEmail: !!process.env.JQUANTS_EMAIL,
        hasPassword: !!process.env.JQUANTS_PASSWORD,
        // デバッグ用（実際の値は表示しない）
        envVars: {
          JQUANTS_ID_TOKEN: process.env.JQUANTS_ID_TOKEN ? '***設定済み***' : '未設定',
          JQUANTS_REFRESH_TOKEN: process.env.JQUANTS_REFRESH_TOKEN ? '***設定済み***' : '未設定',
          JQUANTS_EMAIL: process.env.JQUANTS_EMAIL ? '***設定済み***' : '未設定',
          JQUANTS_PASSWORD: process.env.JQUANTS_PASSWORD ? '***設定済み***' : '未設定',
        }
      },
      api: {
        jquantsProxy: '/api/jquants-proxy',
        health: '/api/health'
      }
    };

    return NextResponse.json(health, { status: 200 });
  } catch (error) {
    console.error('ヘルスチェックエラー:', error);
    return NextResponse.json(
      { 
        status: 'error',
        error: error instanceof Error ? error.message : String(error),
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    );
  }
}