import { NextRequest, NextResponse } from "next/server";
import { wrapHandler, jsonError } from "../_error";
import { withIdempotency } from "../_idempotency";
import fs from "fs";
import path from "path";

export const POST = withIdempotency(wrapHandler(async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { type, includeCharts, includeRecommendations } = body;

    // レポート生成のシミュレーション
    const report = {
      id: `report_${Date.now()}`,
      type,
      includeCharts,
      includeRecommendations,
      status: "completed",
      timestamp: new Date().toISOString(),
      content: {
        summary: {
          totalAnalysis: 15,
          successfulPredictions: 12,
          accuracy: 0.8,
          marketTrend: "bullish",
          riskLevel: "moderate",
        },
        recommendations: [
          {
            symbol: "7203.T",
            name: "トヨタ自動車",
            action: "buy",
            confidence: 0.85,
            targetPrice: 2500,
            currentPrice: 2400,
            reason: "技術的指標が良好で上昇トレンド継続",
          },
          {
            symbol: "6758.T",
            name: "ソニーグループ",
            action: "hold",
            confidence: 0.72,
            targetPrice: 12000,
            currentPrice: 11800,
            reason: "横ばい圏内で様子見推奨",
          },
          {
            symbol: "6861.T",
            name: "キーエンス",
            action: "sell",
            confidence: 0.78,
            targetPrice: 45000,
            currentPrice: 46000,
            reason: "高値圏で利益確定推奨",
          },
        ],
        marketInsights: {
          overallTrend: "上昇",
          volatility: "中程度",
          keyEvents: [
            "日銀政策金利発表",
            "企業業績発表週",
            "米国雇用統計発表",
          ],
          sectorPerformance: {
            "自動車": 2.3,
            "IT": 1.8,
            "金融": 0.9,
          },
        },
      },
    };

    // レポートをファイルに保存
    const dataPath = path.join(process.cwd(), "public", "data");
    const reportFile = path.join(dataPath, `report_${Date.now()}.json`);
    
    try {
      fs.writeFileSync(reportFile, JSON.stringify(report, null, 2));
    } catch (writeError) {
      console.warn("レポートファイル保存に失敗:", writeError);
    }

    return NextResponse.json(report);
  } catch (error: any) {
    console.error("レポート生成エラー:", error);
    return jsonError({
      error_code: "REPORT_GENERATION_FAILED",
      user_message: "レポート生成に失敗しました",
      retry_hint: "少し時間をおいてから再実行してください",
    }, { status: 500 });
  }
}));
