import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import path from "path";

type ListedStock = {
  code: string;
  name: string;
  sector: string;
  market: string;
  updated_at?: string;
  file_path?: string;
};

type ListedIndex = {
  metadata: Record<string, unknown>;
  stocks: ListedStock[];
};

// 静的エクスポート対応
export const dynamic = "force-static";

export async function GET(request: NextRequest) {
  // 静的エクスポート時は固定レスポンスを返す
  if (process.env.NODE_ENV === "production") {
    return NextResponse.json(
      { suggestions: [], total: 0, query: "", message: "Static export mode - suggestions not available" },
      { status: 200 },
    );
  }

  const { searchParams } = new URL(request.url);
  const q = (searchParams.get("q") || "").trim();
  const limitParam = searchParams.get("limit");
  const limit = limitParam ? Math.max(1, Number(limitParam)) : 10;

  // クエリが空や1文字未満なら空配列
  if (!q || q.length < 1) {
    return NextResponse.json(
      { suggestions: [], total: 0, query: q },
      { status: 200 },
    );
  }

  // データファイルパス（静的出力でも参照しやすいようにweb-app/data配下を想定）
  const dataFilePath = path.join(process.cwd(), "public", "data", "listed_index.json");

  if (!fs.existsSync(dataFilePath)) {
    return NextResponse.json(
      { error: "データファイルが見つかりません" },
      { status: 404 },
    );
  }

  try {
    const raw = fs.readFileSync(dataFilePath, "utf-8");
    const parsed: unknown = JSON.parse(raw);

    if (
      !parsed ||
      typeof parsed !== "object" ||
      !("stocks" in parsed) ||
      !Array.isArray((parsed as ListedIndex).stocks)
    ) {
      return NextResponse.json(
        { error: "データ形式が正しくありません" },
        { status: 500 },
      );
    }

    const index = parsed as ListedIndex;
    const lowerQ = q.toLowerCase();

    // 前方一致優先: コード前方一致 → 名前部分一致
    const codeMatches = index.stocks.filter((s) => s.code.startsWith(q));
    const nameMatches = index.stocks.filter((s) =>
      s.name.toLowerCase().includes(lowerQ),
    );

    const merged: ListedStock[] = [];
    const seen = new Set<string>();

    for (const s of codeMatches) {
      if (!seen.has(s.code)) {
        merged.push(s);
        seen.add(s.code);
      }
    }
    for (const s of nameMatches) {
      if (!seen.has(s.code)) {
        merged.push(s);
        seen.add(s.code);
      }
    }

    const suggestions = merged.slice(0, limit).map((s) => ({
      ...s,
      displayText: `${s.code} ${s.name}`,
    }));

    return NextResponse.json(
      { suggestions, total: merged.length, query: q },
      { status: 200 },
    );
  } catch (e) {
    return NextResponse.json(
      { error: "サジェッションの取得に失敗しました" },
      { status: 500 },
    );
  }
}


