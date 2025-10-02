/**
 * サーバーサイドでJ-Quants API呼び出しを仲介するエンドポイント
 * ブラウザから安全にJ-QuantsデータへアクセスするためのAPI
 */

import { NextRequest, NextResponse } from "next/server";
import {
  testConnection,
  getAllSymbols,
  getStockData,
  getIncrementalData,
  clearCache,
  getCacheStats,
} from "@/lib/jquants-client";

export const dynamic = "force-dynamic";

interface JQuantsRequestBody {
  action?: string;
  payload?: Record<string, unknown>;
}

export async function POST(request: NextRequest) {
  try {
    const { action, payload }: JQuantsRequestBody = await request.json();

    if (!action) {
      return NextResponse.json({ error: "action is required" }, { status: 400 });
    }

    switch (action) {
      case "testConnection": {
        const result = await testConnection();
        return NextResponse.json(result);
      }

      case "getAllSymbols": {
        const symbols = await getAllSymbols();
        return NextResponse.json(symbols);
      }

      case "getStockData": {
        const { symbol, startDate, endDate, useCache } = payload ?? {};
        if (typeof symbol !== "string" || typeof startDate !== "string" || typeof endDate !== "string") {
          return NextResponse.json({ error: "symbol, startDate, endDate are required" }, { status: 400 });
        }
        const data = await getStockData(symbol, startDate, endDate, useCache !== false);
        return NextResponse.json(data);
      }

      case "getIncrementalData": {
        const { symbol } = payload ?? {};
        if (typeof symbol !== "string") {
          return NextResponse.json({ error: "symbol is required" }, { status: 400 });
        }
        const data = await getIncrementalData(symbol);
        return NextResponse.json(data);
      }

      case "clearCache": {
        const { symbol } = payload ?? {};
        await clearCache(typeof symbol === "string" ? symbol : undefined);
        return NextResponse.json({ success: true });
      }

      case "getCacheStats": {
        const stats = await getCacheStats();
        return NextResponse.json(stats);
      }

      default:
        return NextResponse.json({ error: `Unknown action: ${action}` }, { status: 400 });
    }
  } catch (error) {
    console.error("J-Quants API route error:", error);
    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 },
    );
  }
}
