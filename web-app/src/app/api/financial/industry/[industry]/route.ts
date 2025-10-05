/**
 * 業界比較分析取得API
 * GET /api/financial/industry/[industry]
 */

import { NextRequest, NextResponse } from "next/server";
import { FinancialAnalysisManager } from "@/lib/financial";
import { FinancialData } from "@/lib/financial/types";

export async function generateStaticParams() {
  return [
    { industry: "電気機器" },
    { industry: "自動車" },
    { industry: "銀行" },
    { industry: "小売業" },
    { industry: "製薬" },
  ];
}

export async function GET(
  request: NextRequest,
  { params }: { params: { industry: string } },
) {
  try {
    const { industry } = params;
    
    if (!industry) {
      return NextResponse.json({
        success: false,
        error: {
          code: "VALIDATION_ERROR",
          message: "業界名が必要です",
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
      symbol: "SAMPLE",
      companyName: "サンプル企業",
      industry,
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

    const metrics = await financialManager.calculateFinancialMetrics(sampleData);
    const industryComparison = await financialManager.calculateIndustryComparison(sampleData, metrics.metrics);

    return NextResponse.json({
      success: true,
      data: {
        industryComparison,
        industry: industry,
        companyCount: 0, // 実際の実装では業界内企業数を取得
      },
      metadata: {
        timestamp: new Date().toISOString(),
        version: "1.0.0",
        calculationTime: 0,
      },
    });

  } catch (error) {
    console.error("業界比較分析取得エラー:", error);
    return NextResponse.json({
      success: false,
      error: {
        code: "INDUSTRY_NOT_FOUND",
        message: "業界データが見つかりません",
        details: error instanceof Error ? error.message : "Unknown error",
      },
      metadata: {
        timestamp: new Date().toISOString(),
        version: "1.0.0",
      },
    }, { status: 404 });
  }
}
