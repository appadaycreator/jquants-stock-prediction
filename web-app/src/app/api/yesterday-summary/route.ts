import { NextResponse } from "next/server";
import path from "path";
import { promises as fs } from "fs";

export async function GET() {
  try {
    // Next.jsの実行環境でのパス解決
    const filePath = path.join(process.cwd(), "public", "data", "today_summary.json");
    const content = await fs.readFile(filePath, "utf-8");
    const json = JSON.parse(content);
    return NextResponse.json(json, { status: 200 });
  } catch (e: any) {
    console.error("yesterday-summary error:", e);
    return NextResponse.json({ 
      ok: false, 
      message: e?.message || "failed",
      stack: process.env.NODE_ENV === "development" ? e?.stack : undefined
    }, { status: 500 });
  }
}


