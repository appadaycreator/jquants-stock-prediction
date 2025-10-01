import { NextResponse } from "next/server";
import path from "path";
import { promises as fs } from "fs";

export async function GET() {
  try {
    // Next.jsの実行環境でのパス解決
    const baseDir = path.join(process.cwd(), "public", "data");
    try {
      // 日付フォルダ内のファイルを優先
      const datedFile = path.join(baseDir, "20250930", "today_actions_2025-09-30.json");
      const content = await fs.readFile(datedFile, "utf-8");
      return NextResponse.json(JSON.parse(content), { status: 200 });
    } catch {
      // フォールバック: トップレベルのファイル
      const filePath = path.join(baseDir, "today_actions_2025-09-30.json");
      const content = await fs.readFile(filePath, "utf-8");
      return NextResponse.json(JSON.parse(content), { status: 200 });
    }
  } catch (e: any) {
    console.error("today-actions error:", e);
    return NextResponse.json({ 
      ok: false, 
      message: e?.message || "failed",
      stack: process.env.NODE_ENV === "development" ? e?.stack : undefined
    }, { status: 500 });
  }
}


