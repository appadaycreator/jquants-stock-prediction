import { NextRequest, NextResponse } from "next/server";
import { wrapHandler, jsonError } from "../_error";
import { withIdempotency } from "../_idempotency";
import fs from "fs";
import path from "path";

export const POST = withIdempotency(wrapHandler(async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { type, symbols, timeframe } = body;

    // 分析実行のシミュレーション
    const analysisResult = {
      id: `analysis_${Date.now()}`,
      type,
      symbols,
      timeframe,
      status: "completed",
      timestamp: new Date().toISOString(),
      results: {
        totalSymbols: symbols.length,
        successfulPredictions: symbols.length,
        averageAccuracy: 0.85,
        topPerformers: symbols.map((symbol: string, index: number) => ({
          symbol,
          predictedReturn: (Math.random() * 6 - 3).toFixed(2),
          confidence: (0.7 + Math.random() * 0.3).toFixed(2),
          recommendation: Math.random() > 0.5 ? "buy" : "hold",
        })),
        marketInsights: {
          volatility: "medium",
          trend: "bullish",
          riskLevel: "moderate",
        },
      },
    };

    // 結果をファイルに保存
    const dataPath = path.join(process.cwd(), "public", "data");
    const analysisFile = path.join(dataPath, `analysis_${Date.now()}.json`);
    
    try {
      fs.writeFileSync(analysisFile, JSON.stringify(analysisResult, null, 2));
    } catch (writeError) {
      console.warn("分析結果ファイル保存に失敗:", writeError);
    }

    return NextResponse.json(analysisResult);
  } catch (error: any) {
    console.error("分析実行エラー:", error);
    return jsonError({
      error_code: "ANALYSIS_EXECUTION_FAILED",
      user_message: "分析の実行に失敗しました",
      retry_hint: "数十秒後に再実行してください",
    }, { status: 500 });
  }
}));
