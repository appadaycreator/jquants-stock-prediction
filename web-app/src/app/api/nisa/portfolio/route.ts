import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  try {
    // 実際の実装では、NISA統合管理システムからポートフォリオデータを取得
    const mockPortfolio = {
      positions: [
        {
          symbol: "7203",
          symbol_name: "トヨタ自動車",
          quantity: 100,
          average_price: 2500,
          current_price: 2600,
          cost: 250000,
          current_value: 260000,
          unrealized_profit_loss: 10000,
          quota_type: "GROWTH",
          purchase_date: "2024-01-15",
        },
        {
          symbol: "6758",
          symbol_name: "ソニーグループ",
          quantity: 10,
          average_price: 12000,
          current_price: 12500,
          cost: 120000,
          current_value: 125000,
          unrealized_profit_loss: 5000,
          quota_type: "ACCUMULATION",
          purchase_date: "2024-02-01",
        },
      ],
      total_value: 385000,
      total_cost: 370000,
      unrealized_profit_loss: 15000,
      realized_profit_loss: 0,
      tax_free_profit_loss: 15000,
    };

    return NextResponse.json({
      success: true,
      data: mockPortfolio,
      metadata: {
        timestamp: new Date().toISOString(),
        version: "1.0.0",
      },
    });

  } catch (error) {
    console.error("NISA portfolio API error:", error);
    return NextResponse.json(
      {
        success: false,
        error: {
          code: "INTERNAL_ERROR",
          message: "ポートフォリオデータの取得に失敗しました",
          details: error instanceof Error ? error.message : "Unknown error",
        },
        metadata: {
          timestamp: new Date().toISOString(),
          version: "1.0.0",
        },
      },
      { status: 500 },
    );
  }
}