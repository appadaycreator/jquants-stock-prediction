import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // 取引データの検証
    const requiredFields = ["type", "symbol", "symbol_name", "quantity", "price", "amount", "quota_type"];
    for (const field of requiredFields) {
      if (!body[field]) {
        return NextResponse.json(
          {
            success: false,
            error: {
              code: "VALIDATION_ERROR",
              message: `必須フィールド${field}が不足しています`,
              details: `Field ${field} is required`,
            },
            metadata: {
              timestamp: new Date().toISOString(),
              version: "1.0.0",
            },
          },
          { status: 400 },
        );
      }
    }

    // 取引タイプの検証
    if (!["BUY", "SELL"].includes(body.type)) {
      return NextResponse.json(
        {
          success: false,
          error: {
            code: "VALIDATION_ERROR",
            message: "取引タイプはBUYまたはSELLである必要があります",
            details: "Invalid transaction type",
          },
          metadata: {
            timestamp: new Date().toISOString(),
            version: "1.0.0",
          },
        },
        { status: 400 },
      );
    }

    // 枠タイプの検証
    if (!["GROWTH", "ACCUMULATION"].includes(body.quota_type)) {
      return NextResponse.json(
        {
          success: false,
          error: {
            code: "VALIDATION_ERROR",
            message: "枠タイプはGROWTHまたはACCUMULATIONである必要があります",
            details: "Invalid quota type",
          },
          metadata: {
            timestamp: new Date().toISOString(),
            version: "1.0.0",
          },
        },
        { status: 400 },
      );
    }

    // 数値の検証
    if (body.quantity <= 0 || body.price <= 0 || body.amount <= 0) {
      return NextResponse.json(
        {
          success: false,
          error: {
            code: "VALIDATION_ERROR",
            message: "数量、価格、金額は0より大きい必要があります",
            details: "Invalid numeric values",
          },
          metadata: {
            timestamp: new Date().toISOString(),
            version: "1.0.0",
          },
        },
        { status: 400 },
      );
    }

    // 実際の実装では、NISA統合管理システムに取引を追加
    const transactionId = `TXN_${Date.now()}`;
    
    // モックレスポンス
    const mockResponse = {
      success: true,
      data: {
        transaction_id: transactionId,
        transaction: {
          id: transactionId,
          type: body.type,
          symbol: body.symbol,
          symbol_name: body.symbol_name,
          quantity: body.quantity,
          price: body.price,
          amount: body.amount,
          quota_type: body.quota_type,
          transaction_date: body.transaction_date || new Date().toISOString(),
          profit_loss: body.profit_loss,
          tax_free_amount: body.tax_free_amount,
        },
      },
      metadata: {
        timestamp: new Date().toISOString(),
        version: "1.0.0",
      },
    };

    return NextResponse.json(mockResponse, { status: 201 });

  } catch (error) {
    console.error("NISA transaction API error:", error);
    return NextResponse.json(
      {
        success: false,
        error: {
          code: "INTERNAL_ERROR",
          message: "取引の追加に失敗しました",
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

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const limit = parseInt(searchParams.get("limit") || "100");
    
    // 実際の実装では、NISA統合管理システムから取引履歴を取得
    const mockTransactions = [
      {
        id: "TXN_001",
        type: "BUY",
        symbol: "7203",
        symbol_name: "トヨタ自動車",
        quantity: 100,
        price: 2500,
        amount: 250000,
        quota_type: "GROWTH",
        transaction_date: "2024-01-15T10:30:00Z",
        profit_loss: null,
        tax_free_amount: null,
      },
      {
        id: "TXN_002",
        type: "BUY",
        symbol: "6758",
        symbol_name: "ソニーグループ",
        quantity: 10,
        price: 12000,
        amount: 120000,
        quota_type: "ACCUMULATION",
        transaction_date: "2024-02-01T14:15:00Z",
        profit_loss: null,
        tax_free_amount: null,
      },
    ];

    return NextResponse.json({
      success: true,
      data: {
        transactions: mockTransactions.slice(0, limit),
        total_count: mockTransactions.length,
      },
      metadata: {
        timestamp: new Date().toISOString(),
        version: "1.0.0",
      },
    });

  } catch (error) {
    console.error("NISA transactions API error:", error);
    return NextResponse.json(
      {
        success: false,
        error: {
          code: "INTERNAL_ERROR",
          message: "取引履歴の取得に失敗しました",
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