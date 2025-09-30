import { NextResponse } from "next/server";
import { promises as fs } from "fs";
import path from "path";

export const dynamic = 'force-static';

export async function GET() {
  try {
    const filePath = path.join(process.cwd(), "public", "data", "model_health.json");
    const data = await fs.readFile(filePath, { encoding: "utf-8" });
    const json = JSON.parse(data);
    return NextResponse.json(json, { status: 200 });
  } catch (e) {
    // デフォルト（初期はOK）
    return NextResponse.json(
      {
        status: "ok",
        detail: {},
        reasons: [],
        checked_at: new Date().toISOString(),
      },
      { status: 200 }
    );
  }
}


