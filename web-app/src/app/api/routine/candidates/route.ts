import { NextRequest, NextResponse } from 'next/server';
import { RankerService } from '@/lib/ranking/RankerService';

export async function GET(request: NextRequest) {
  try {
    const candidates = await RankerService.generateCandidates();
    
    return NextResponse.json({
      success: true,
      candidates,
      count: candidates.length,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('候補生成エラー:', error);
    return NextResponse.json(
      {
        success: false,
        message: '候補生成に失敗しました',
        error: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}
