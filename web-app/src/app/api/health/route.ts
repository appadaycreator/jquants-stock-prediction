import { NextResponse } from 'next/server';

// 静的エクスポート用の設定
export const dynamic = 'force-static';

export async function GET() {
  try {
    return NextResponse.json(
      {
        status: 'ok',
        message: 'API is healthy',
        timestamp: new Date().toISOString(),
      },
      { status: 200 }
    );
  } catch (error) {
    return NextResponse.json(
      {
        status: 'error',
        message: 'API health check failed',
        error: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}
