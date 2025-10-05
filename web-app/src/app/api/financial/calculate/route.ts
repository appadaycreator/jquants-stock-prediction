/**
 * 財務指標計算実行API
 * POST /api/financial/calculate
 */

import { NextRequest, NextResponse } from "next/server";
import { FinancialAnalysisManager } from "@/lib/financial";
import { FinancialData } from "@/lib/financial/types";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { data, type = "all" } = body;

    if (!data) {
      return NextResponse.json({
        success: false,
        error: {
          code: "VALIDATION_ERROR",
          message: "財務データが必要です",
        },
        metadata: {
          timestamp: new Date().toISOString(),
          version: "1.0.0",
        },
      }, { status: 400 });
    }

    const financialManager = new FinancialAnalysisManager();
    const result = await financialManager.calculateFinancialMetrics(data as FinancialData);

    let responseData: any = {};

    switch (type) {
      case "metrics":
        responseData = { metrics: result.metrics };
        break;
      case "health":
        responseData = { healthScore: result.healthScore };
        break;
      case "industry":
        responseData = { industryComparison: result.industryComparison };
        break;
      case "historical":
        responseData = { historicalAnalysis: result.historicalAnalysis };
        break;
      case "all":
      default:
        responseData = result;
        break;
    }

    return NextResponse.json({
      success: true,
      data: responseData,
      metadata: {
        timestamp: new Date().toISOString(),
        version: "1.0.0",
        calculationType: type,
        calculationTime: 0,
      },
    });

  } catch (error) {
    console.error("財務指標計算エラー:", error);
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
