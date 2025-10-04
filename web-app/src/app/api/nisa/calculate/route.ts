/**
 * 新NISA税務計算・最適化API
 * POST /api/nisa/calculate
 */

import { NextRequest, NextResponse } from 'next/server';
import { NisaManager } from '@/lib/nisa';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { type = 'all' } = body;

    const nisaManager = new NisaManager();
    await nisaManager.initialize();

    const calculationResult = await nisaManager.getCalculationResult();
    
    if (!calculationResult) {
      return NextResponse.json({
        success: false,
        error: {
          code: 'DATA_NOT_FOUND',
          message: '計算に必要なデータが見つかりません',
        },
        metadata: {
          timestamp: new Date().toISOString(),
          version: '1.0.0',
        },
      }, { status: 404 });
    }

    let responseData: any = {};

    switch (type) {
      case 'quotas':
        responseData = { quotas: calculationResult.quotas };
        break;
      case 'portfolio':
        responseData = { portfolio: calculationResult.portfolio };
        break;
      case 'optimization':
        responseData = { optimization: calculationResult.optimization };
        break;
      case 'tax':
        responseData = { taxCalculation: calculationResult.taxCalculation };
        break;
      case 'alerts':
        responseData = { alerts: calculationResult.alerts };
        break;
      case 'opportunities':
        responseData = { opportunities: calculationResult.opportunities };
        break;
      case 'all':
      default:
        responseData = calculationResult;
        break;
    }

    return NextResponse.json({
      success: true,
      data: responseData,
      metadata: {
        timestamp: new Date().toISOString(),
        version: '1.0.0',
        calculationType: type,
      },
    });

  } catch (error) {
    console.error('NISA計算エラー:', error);
    return NextResponse.json({
      success: false,
      error: {
        code: 'CALCULATION_ERROR',
        message: '計算処理でエラーが発生しました',
        details: error instanceof Error ? error.message : 'Unknown error',
      },
      metadata: {
        timestamp: new Date().toISOString(),
        version: '1.0.0',
      },
    }, { status: 500 });
  }
}
