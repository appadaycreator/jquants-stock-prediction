import { NextResponse } from "next/server";
import path from "path";
import { promises as fs } from "fs";

export async function GET() {
  try {
    const filePath = path.join(process.cwd(), "web-app", "public", "data", "performance_metrics.json");
    const content = await fs.readFile(filePath, "utf-8");
    const json = JSON.parse(content);
    const health = {
      status: "ok",
      updatedAt: new Date().toISOString(),
      metrics: json,
    };
    return NextResponse.json(health, { status: 200 });
  } catch (e: any) {
    return NextResponse.json({ status: "error", message: e?.message || "failed" }, { status: 500 });
  }
}


