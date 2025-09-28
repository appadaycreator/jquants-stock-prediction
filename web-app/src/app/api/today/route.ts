import { NextRequest, NextResponse } from 'next/server';
import { readFile } from 'fs/promises';
import { join } from 'path';
import { TodaySummary } from '../../../types/today';

export const dynamic = 'force-static';

export async function GET(request: NextRequest) {
  try {
    // 静的ファイルからデータを読み込み
    const filePath = join(process.cwd(), 'public', 'data', 'today_summary.json');
    const fileContent = await readFile(filePath, 'utf-8');
    const data: TodaySummary = JSON.parse(fileContent);

    // キャッシュヘッダーを設定（5分間キャッシュ）
    const headers = new Headers();
    headers.set('Cache-Control', 'public, max-age=300, s-maxage=300');
    headers.set('Content-Type', 'application/json');

    return NextResponse.json(data, { headers });
  } catch (error) {
    console.error('Error reading today_summary.json:', error);
    
    // エラー時は空のデータを返す
    const emptyData: TodaySummary = {
      generated_at: new Date().toISOString(),
      market_phase: 'preopen',
      overview: {
        buy_candidates: 0,
        sell_candidates: 0,
        warnings: 0,
      },
      candidates: [],
      warnings: [],
      todos: [],
    };

    return NextResponse.json(emptyData, {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache',
      },
    });
  }
}
