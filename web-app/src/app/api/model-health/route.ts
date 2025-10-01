import { NextResponse } from "next/server";
import path from "path";
import { promises as fs } from "fs";

export async function GET() {
  try {
    // Next.jsの実行環境でのパス解決
    const filePath = path.join(process.cwd(), "public", "data", "performance_metrics.json");
    const content = await fs.readFile(filePath, "utf-8");
    const json = JSON.parse(content);
    const health = {
      status: "ok",
      updatedAt: new Date().toISOString(),
      metrics: json,
    };
    return NextResponse.json(health, { status: 200 });
  } catch (e: any) {
    console.error("model-health error:", e);
    return NextResponse.json({ 
      status: "error", 
      message: e?.message || "failed",
      stack: process.env.NODE_ENV === "development" ? e?.stack : undefined
    }, { status: 500 });
  }
}


