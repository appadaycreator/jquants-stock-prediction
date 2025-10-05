/**
 * 時系列分析取得API
 * GET /api/financial/trend/[symbol]
 */

import { NextRequest, NextResponse } from "next/server";
import { FinancialAnalysisManager } from "@/lib/financial";

export async function generateStaticParams() {
  return [
    { symbol: "7203" },
    { symbol: "6758" },
    { symbol: "9984" },
    { symbol: "8306" },
    { symbol: "6861" },
  ];
}

export async function GET(
  request: NextRequest,
  { params }: { params: { symbol: string } },
) {
  try {
    const { symbol } = params;
    
    if (!symbol) {
      return NextResponse.json({
        success: false,
        error: {
          code: "VALIDATION_ERROR",
          message: "銘柄コードが必要です",
        },
        metadata: {
          timestamp: new Date().toISOString(),
          version: "1.0.0",
        },
      }, { status: 400 });
    }

    const financialManager = new FinancialAnalysisManager();
    const historicalAnalysis = await financialManager.calculateHistoricalAnalysis(symbol);

    return NextResponse.json({
      success: true,
      data: {
        historicalAnalysis,
        symbol,
        period: "5年間",
      },
      metadata: {
        timestamp: new Date().toISOString(),
        version: "1.0.0",
        calculationTime: 0,
      },
    });

  } catch (error) {
    console.error("時系列分析取得エラー:", error);
    return NextResponse.json({
      success: false,
      error: {
        code: "DATA_NOT_FOUND",
        message: "時系列データが見つかりません",
        details: error instanceof Error ? error.message : "Unknown error",
      },
      metadata: {
        timestamp: new Date().toISOString(),
        version: "1.0.0",
      },
    }, { status: 404 });
  }
}
