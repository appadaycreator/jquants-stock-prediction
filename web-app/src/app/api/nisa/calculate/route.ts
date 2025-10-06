import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // 税務計算の実行
    const mockCalculation = {
      current_year: {
        growth_quota_used: 1200000,
        accumulation_quota_used: 200000,
        total_tax_free_amount: 1400000,
        hypothetical_tax: 420000,
        tax_savings: 420000,
      },
      next_year: {
        available_growth_quota: 2500000,
        available_accumulation_quota: 450000,
        reusable_quota: 150000,
        total_available: 2950000,
      },
      tax_savings: {
        estimated_tax_savings: 420000,
        tax_rate: 0.30,
        effective_tax_rate: 0.30,
        annual_savings: 420000,
        lifetime_savings: 2100000,
      },
      total_tax_free_amount: 1400000,
      effective_tax_rate: 0.30,
    };

    return NextResponse.json({
      success: true,
      data: mockCalculation,
      metadata: {
        timestamp: new Date().toISOString(),
        version: "1.0.0",
      },
    });

  } catch (error) {
    console.error("NISA calculate API error:", error);
    return NextResponse.json(
      {
        success: false,
        error: {
          code: "INTERNAL_ERROR",
          message: "税務計算の実行に失敗しました",
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