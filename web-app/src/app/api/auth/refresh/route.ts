import { NextRequest, NextResponse } from 'next/server';
import { AuthService } from '@/lib/auth/AuthService';

export async function POST(request: NextRequest) {
  try {
    // 自動更新の実行
    const success = await AuthService.autoRefresh();
    
    if (success) {
      return NextResponse.json({
        success: true,
        message: 'トークンの更新が成功しました',
      });
    } else {
      return NextResponse.json(
        {
          success: false,
          message: 'トークンの更新に失敗しました',
        },
        { status: 401 }
      );
    }
  } catch (error) {
    console.error('トークン更新エラー:', error);
    return NextResponse.json(
      {
        success: false,
        message: 'トークンの更新中にエラーが発生しました',
        error: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}
