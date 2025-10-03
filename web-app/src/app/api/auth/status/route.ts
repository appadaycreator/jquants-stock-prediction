import { NextRequest, NextResponse } from 'next/server';
import { AuthService } from '@/lib/auth/AuthService';

export async function GET(request: NextRequest) {
  try {
    const status = await AuthService.checkAuthStatus();
    
    return NextResponse.json({
      success: true,
      status,
    });
  } catch (error) {
    console.error('認証状態確認エラー:', error);
    return NextResponse.json(
      {
        success: false,
        message: '認証状態の確認に失敗しました',
        error: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}
