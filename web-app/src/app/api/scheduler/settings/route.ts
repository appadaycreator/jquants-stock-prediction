import { NextRequest, NextResponse } from "next/server";

export async function GET(_request: NextRequest) {
  return NextResponse.json(
    {
      status: "unsupported",
      message: "Static hosting environment does not expose scheduler settings.",
    },
    { status: 400 },
  );
}

export async function PUT(_request: NextRequest) {
  return NextResponse.json(
    { status: "unsupported", message: "Static hosting environment does not support updating scheduler settings." },
    { status: 400 },
  );
}
