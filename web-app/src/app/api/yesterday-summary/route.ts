import { NextResponse } from "next/server";
import path from "path";
import { promises as fs } from "fs";

export async function GET() {
  try {
    const filePath = path.join(process.cwd(), "web-app", "public", "data", "today_summary.json");
    const content = await fs.readFile(filePath, "utf-8");
    const json = JSON.parse(content);
    return NextResponse.json(json, { status: 200 });
  } catch (e: any) {
    return NextResponse.json({ ok: false, message: e?.message || "failed" }, { status: 500 });
  }
}


