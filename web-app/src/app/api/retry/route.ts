import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  try {
    // リクエストボディの取得
    const body = await request.json();
    const { reason } = body;

    // 冪等性キーの確認
    const idempotencyKey = request.headers.get("Idempotency-Key");
    
    if (!idempotencyKey) {
      return NextResponse.json(
        { error: "Idempotency-Key header is required" },
        { status: 400 }
      );
    }

    // リトライ処理のログ
    console.log(`🔄 Retry request received: ${reason} (Idempotency-Key: ${idempotencyKey})`);

    // 実際のリトライ処理はここで実装
    // 現在は単純に成功レスポンスを返す
    return NextResponse.json({
      success: true,
      message: "Retry request processed successfully",
      timestamp: new Date().toISOString(),
      idempotencyKey,
      reason,
    });

  } catch (error) {
    console.error("Retry API error:", error);
    
    return NextResponse.json(
      { 
        error: "Internal server error",
        message: error instanceof Error ? error.message : "Unknown error"
      },
      { status: 500 }
    );
  }
}
