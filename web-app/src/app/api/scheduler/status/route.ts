import { NextRequest, NextResponse } from "next/server";

export async function GET(_request: NextRequest) {
  return NextResponse.json(
    {
      status: "unsupported",
      message: "Static hosting environment does not expose scheduler status.",
    },
    { status: 400 },
  );
}
