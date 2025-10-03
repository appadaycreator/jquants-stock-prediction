import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import path from "path";

interface ListedStock {
  code: string;
  name: string;
  sector: string;
  market: string;
  updated_at: string;
  file_path: string;
}

interface ListedData {
  metadata: {
    generated_at: string;
    version: string;
    total_stocks: number;
    last_updated: string;
    data_type: string;
  };
  stocks: ListedStock[];
}

interface SuggestionItem {
  code: string;
  name: string;
  sector: string;
  market: string;
  displayText: string;
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const query = searchParams.get("q");
    const limit = parseInt(searchParams.get("limit") || "10");

    if (!query || query.trim().length < 1) {
      return NextResponse.json({ suggestions: [] });
    }

    // データファイルのパス
    const dataPath = path.join(process.cwd(), "public", "data", "listed_index.json");
    
    // ファイルが存在するかチェック
    if (!fs.existsSync(dataPath)) {
      return NextResponse.json({ 
        error: "データファイルが見つかりません", 
      }, { status: 404 });
    }

    // データを読み込み
    const rawData = fs.readFileSync(dataPath, "utf8");
    const data: ListedData = JSON.parse(rawData);

    if (!data.stocks || !Array.isArray(data.stocks)) {
      return NextResponse.json({ 
        error: "データ形式が正しくありません", 
      }, { status: 500 });
    }

    // 全角・半角を統一した検索用の関数
    const normalizeText = (text: string): string => {
      return text
        .toLowerCase()
        .trim()
        // 全角数字を半角に変換
        .replace(/[０-９]/g, (match) => String.fromCharCode(match.charCodeAt(0) - 0xFEE0))
        // 全角英字を半角に変換
        .replace(/[Ａ-Ｚａ-ｚ]/g, (match) => String.fromCharCode(match.charCodeAt(0) - 0xFEE0))
        // 全角記号を半角に変換
        .replace(/[（）]/g, (match) => match === "（" ? "(" : ")")
        .replace(/[　]/g, " "); // 全角スペースを半角に変換
    };

    const normalizedQuery = normalizeText(query);
    
    // 前方一致を優先（コード/名称）し、次に部分一致を追加
    const startsWithMatches: SuggestionItem[] = data.stocks
      .filter(stock => {
        const normalizedCode = normalizeText(stock.code);
        const normalizedName = normalizeText(stock.name);
        const codeStart = normalizedCode.startsWith(normalizedQuery);
        const nameStart = normalizedName.startsWith(normalizedQuery);
        return codeStart || nameStart;
      })
      .map(stock => ({
        code: stock.code,
        name: stock.name,
        sector: stock.sector,
        market: stock.market,
        displayText: `${stock.name} (${stock.code})`,
      }))
      .slice(0, limit);

    const partialMatches: SuggestionItem[] = data.stocks
      .filter(stock => {
        const normalizedCode = normalizeText(stock.code);
        const normalizedName = normalizeText(stock.name);
        const codeIncludes = normalizedCode.includes(normalizedQuery);
        const nameIncludes = normalizedName.includes(normalizedQuery);
        const codeStart = normalizedCode.startsWith(normalizedQuery);
        const nameStart = normalizedName.startsWith(normalizedQuery);
        // 既にstartsWithに含まれるものは除外
        return (codeIncludes || nameIncludes) && !(codeStart || nameStart);
      })
      .map(stock => ({
        code: stock.code,
        name: stock.name,
        sector: stock.sector,
        market: stock.market,
        displayText: `${stock.name} (${stock.code})`,
      }));

    let suggestions: SuggestionItem[] = [...startsWithMatches, ...partialMatches];

    // コードで始まるものを優先し、その後名前で始まるものを並べる
    suggestions.sort((a, b) => {
      const aCodeMatch = normalizeText(a.code).startsWith(normalizedQuery);
      const bCodeMatch = normalizeText(b.code).startsWith(normalizedQuery);
      const aNameMatch = normalizeText(a.name).startsWith(normalizedQuery);
      const bNameMatch = normalizeText(b.name).startsWith(normalizedQuery);
      
      // コードで始まるものを最優先
      if (aCodeMatch && !bCodeMatch) return -1;
      if (!aCodeMatch && bCodeMatch) return 1;
      
      // 名前で始まるものを次に優先
      if (aNameMatch && !bNameMatch && !aCodeMatch && !bCodeMatch) return -1;
      if (!aNameMatch && bNameMatch && !aCodeMatch && !bCodeMatch) return 1;
      
      // 同じ条件の場合は名前順でソート
      return a.name.localeCompare(b.name, "ja");
    });

    return NextResponse.json({ 
      suggestions: suggestions.slice(0, limit),
      total: suggestions.length,
      query: query,
    });

  } catch (error) {
    console.error("Suggestions API error:", error);
    return NextResponse.json({ 
      error: "サジェッションの取得に失敗しました", 
    }, { status: 500 });
  }
}
