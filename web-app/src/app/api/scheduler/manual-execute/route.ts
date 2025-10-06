import { NextRequest, NextResponse } from "next/server";

// NOTE: 静的ホスティング環境ではサーバーサイド実行不可のためNO-OP応答
export async function POST(_request: NextRequest) {
  return NextResponse.json(
    {
      status: "unsupported",
      message: "Static hosting environment does not support scheduler execution.",
    },
    { status: 400 },
  );
}
