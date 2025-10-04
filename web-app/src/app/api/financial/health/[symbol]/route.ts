/**
 * 財務健全性スコア取得API
 * GET /api/financial/health/[symbol]
 */

import { NextRequest, NextResponse } from 'next/server';
import { FinancialAnalysisManager } from '@/lib/financial';
import { FinancialData } from '@/lib/financial/types';

export async function generateStaticParams() {
  return [
    { symbol: '7203' },
    { symbol: '6758' },
    { symbol: '9984' },
    { symbol: '8306' },
    { symbol: '6861' },
  ];
}

export async function GET(
  request: NextRequest,
  { params }: { params: { symbol: string } }
) {
  try {
    const { symbol } = params;
    
    if (!symbol) {
      return NextResponse.json({
        success: false,
        error: {
          code: 'VALIDATION_ERROR',
          message: '銘柄コードが必要です',
        },
        metadata: {
          timestamp: new Date().toISOString(),
          version: '1.0.0',
        },
      }, { status: 400 });
    }

    const financialManager = new FinancialAnalysisManager();

    // サンプルデータ（実際の実装では外部APIから取得）
    const sampleData: FinancialData = {
      symbol,
      companyName: 'サンプル企業',
      industry: '電気機器',
      fiscalYear: 2024,
      incomeStatement: {
        revenue: 1000000000,
        operatingIncome: 100000000,
        netIncome: 80000000,
        eps: 100,
      },
      balanceSheet: {
        totalAssets: 2000000000,
        currentAssets: 800000000,
        quickAssets: 600000000,
        totalLiabilities: 1200000000,
        currentLiabilities: 400000000,
        equity: 800000000,
        bps: 1000,
      },
      marketData: {
        stockPrice: 1500,
        marketCap: 15000000000,
        sharesOutstanding: 10000000,
      },
      previousYear: {
        revenue: 900000000,
        netIncome: 70000000,
        totalAssets: 1800000000,
      },
    };

    const result = await financialManager.calculateFinancialMetrics(sampleData);

    return NextResponse.json({
      success: true,
      data: {
        healthScore: result.healthScore,
        symbol,
        calculatedAt: new Date().toISOString(),
      },
      metadata: {
        timestamp: new Date().toISOString(),
        version: '1.0.0',
        calculationTime: 0,
      },
    });

  } catch (error) {
    console.error('財務健全性スコア取得エラー:', error);
    return NextResponse.json({
      success: false,
      error: {
        code: 'CALCULATION_ERROR',
        message: '財務健全性スコアの計算に失敗しました',
        details: error instanceof Error ? error.message : 'Unknown error',
      },
      metadata: {
        timestamp: new Date().toISOString(),
        version: '1.0.0',
      },
    }, { status: 500 });
  }
}
