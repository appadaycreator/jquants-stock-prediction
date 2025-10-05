/**
 * 財務指標分析取得API
 * GET /api/financial/analysis/[symbol]
 */

import { NextRequest, NextResponse } from "next/server";
import { FinancialAnalysisManager } from "@/lib/financial";
import { FinancialData } from "@/lib/financial/types";

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

    // サンプルデータ（実際の実装では外部APIから取得）
    const sampleData: FinancialData = {
      symbol,
      companyName: "サンプル企業",
      industry: "電気機器",
      fiscalYear: 2024,
      incomeStatement: {
        revenue: 1000000000,      // 10億円
        operatingIncome: 100000000, // 1億円
        netIncome: 80000000,      // 8000万円
        eps: 100,                 // 100円
      },
      balanceSheet: {
        totalAssets: 2000000000,   // 20億円
        currentAssets: 800000000,  // 8億円
        quickAssets: 600000000,     // 6億円
        totalLiabilities: 1200000000, // 12億円
        currentLiabilities: 400000000, // 4億円
        equity: 800000000,         // 8億円
        bps: 1000,                 // 1000円
      },
      marketData: {
        stockPrice: 1500,         // 1500円
        marketCap: 15000000000,   // 150億円
        sharesOutstanding: 10000000, // 1000万株
      },
      previousYear: {
        revenue: 900000000,      // 9億円
        netIncome: 70000000,       // 7000万円
        totalAssets: 1800000000,   // 18億円
      },
    };

    const result = await financialManager.calculateFinancialMetrics(sampleData);

    return NextResponse.json({
      success: true,
      data: result,
      metadata: {
        timestamp: new Date().toISOString(),
        version: "1.0.0",
        calculationTime: 0,
      },
    });

  } catch (error) {
    console.error("財務指標分析取得エラー:", error);
    return NextResponse.json({
      success: false,
      error: {
        code: "CALCULATION_ERROR",
        message: "財務指標の計算に失敗しました",
        details: error instanceof Error ? error.message : "Unknown error",
      },
      metadata: {
        timestamp: new Date().toISOString(),
        version: "1.0.0",
      },
    }, { status: 500 });
  }
}
