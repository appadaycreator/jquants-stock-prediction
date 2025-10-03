import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

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
    const query = searchParams.get('q');
    const limit = parseInt(searchParams.get('limit') || '10');

    if (!query || query.trim().length < 1) {
      return NextResponse.json({ suggestions: [] });
    }

    // データファイルのパス
    const dataPath = path.join(process.cwd(), 'public', 'data', 'listed_index.json');
    
    // ファイルが存在するかチェック
    if (!fs.existsSync(dataPath)) {
      return NextResponse.json({ 
        error: 'データファイルが見つかりません' 
      }, { status: 404 });
    }

    // データを読み込み
    const rawData = fs.readFileSync(dataPath, 'utf8');
    const data: ListedData = JSON.parse(rawData);

    if (!data.stocks || !Array.isArray(data.stocks)) {
      return NextResponse.json({ 
        error: 'データ形式が正しくありません' 
      }, { status: 500 });
    }

    const queryLower = query.toLowerCase().trim();
    
    // 部分一致で候補を検索
    const suggestions: SuggestionItem[] = data.stocks
      .filter(stock => {
        const codeMatch = stock.code.toLowerCase().includes(queryLower);
        const nameMatch = stock.name.toLowerCase().includes(queryLower);
        return codeMatch || nameMatch;
      })
      .map(stock => ({
        code: stock.code,
        name: stock.name,
        sector: stock.sector,
        market: stock.market,
        displayText: `${stock.name} (${stock.code})`
      }))
      .slice(0, limit);

    // コードで始まるものを優先し、その後名前で始まるものを並べる
    suggestions.sort((a, b) => {
      const aCodeMatch = a.code.toLowerCase().startsWith(queryLower);
      const bCodeMatch = b.code.toLowerCase().startsWith(queryLower);
      const aNameMatch = a.name.toLowerCase().startsWith(queryLower);
      const bNameMatch = b.name.toLowerCase().startsWith(queryLower);
      
      // コードで始まるものを最優先
      if (aCodeMatch && !bCodeMatch) return -1;
      if (!aCodeMatch && bCodeMatch) return 1;
      
      // 名前で始まるものを次に優先
      if (aNameMatch && !bNameMatch && !aCodeMatch && !bCodeMatch) return -1;
      if (!aNameMatch && bNameMatch && !aCodeMatch && !bCodeMatch) return 1;
      
      // 同じ条件の場合は名前順でソート
      return a.name.localeCompare(b.name, 'ja');
    });

    return NextResponse.json({ 
      suggestions,
      total: suggestions.length,
      query: query
    });

  } catch (error) {
    console.error('Suggestions API error:', error);
    return NextResponse.json({ 
      error: 'サジェッションの取得に失敗しました' 
    }, { status: 500 });
  }
}
