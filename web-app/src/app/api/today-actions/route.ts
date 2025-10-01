import { NextResponse } from "next/server";
import path from "path";
import { promises as fs } from "fs";

export async function GET() {
  try {
    // 直近の日付フォルダがあれば優先、それが無ければトップの today_actions_*.json を参照
    const baseDir = path.join(process.cwd(), "web-app", "public", "data");
    try {
      const datedDir = path.join(baseDir, "20250930", "");
      const alt = path.join(datedDir, "today_actions_2025-09-30.json");
      const content = await fs.readFile(alt, "utf-8");
      return NextResponse.json(JSON.parse(content), { status: 200 });
    } catch {
      const filePath = path.join(baseDir, "today_actions_2025-09-30.json");
      const content = await fs.readFile(filePath, "utf-8");
      return NextResponse.json(JSON.parse(content), { status: 200 });
    }
  } catch (e: any) {
    return NextResponse.json({ ok: false, message: e?.message || "failed" }, { status: 500 });
  }
}


