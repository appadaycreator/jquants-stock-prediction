/**
 * 新NISA枠利用状況取得API
 * GET /api/nisa/status
 */

import { NextRequest, NextResponse } from 'next/server';
import { NisaManager } from '@/lib/nisa';

export async function GET(request: NextRequest) {
  try {
    const nisaManager = new NisaManager();
    await nisaManager.initialize();

    const calculationResult = await nisaManager.getCalculationResult();
    
    if (!calculationResult) {
      return NextResponse.json({
        success: false,
        error: {
          code: 'DATA_NOT_FOUND',
          message: 'NISAデータが見つかりません',
        },
        metadata: {
          timestamp: new Date().toISOString(),
          version: '1.0.0',
        },
      }, { status: 404 });
    }

    return NextResponse.json({
      success: true,
      data: {
        quotas: calculationResult.quotas,
        portfolio: calculationResult.portfolio,
        alerts: calculationResult.alerts,
        opportunities: calculationResult.opportunities,
      },
      metadata: {
        timestamp: new Date().toISOString(),
        version: '1.0.0',
      },
    });

  } catch (error) {
    console.error('NISA枠状況取得エラー:', error);
    return NextResponse.json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: 'サーバー内部エラーが発生しました',
        details: error instanceof Error ? error.message : 'Unknown error',
      },
      metadata: {
        timestamp: new Date().toISOString(),
        version: '1.0.0',
      },
    }, { status: 500 });
  }
}
