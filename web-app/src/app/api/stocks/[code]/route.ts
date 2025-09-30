import { NextRequest, NextResponse } from 'next/server';
import path from 'path';
import fs from 'fs';
import { DateTime } from 'luxon';
import { enrichWithIndicators, toStocksApiResponse, sliceByRange, PriceBar } from '@/src/lib/indicators';

// stocks/{code}.json を返す API。JST 固定、未確定足除外、前回値フォワード、指標を同梱
export async function GET(request: NextRequest, { params }: { params: { code: string } }) {
  try {
    const code = decodeURIComponent(params.code);
    const { searchParams } = new URL(request.url);
    const range = (searchParams.get('range') as '5y' | '1y' | '3m' | '1m' | null) ?? null;

    // 価格データのソース: public/data/prices/{code}.json or stock_data.json fallback
    // まず個別ファイルを探す
    const dataDir = path.join(process.cwd(), 'public', 'data');
    const perCodePath = path.join(dataDir, 'prices', `${code}.json`);
    let prices: PriceBar[] = [];

    if (fs.existsSync(perCodePath)) {
      const raw = fs.readFileSync(perCodePath, 'utf-8');
      prices = JSON.parse(raw);
    } else {
      // 旧フォーマットの fallback: stock_data.json から code 別抽出
      const fallbackPath = path.join(dataDir, 'stock_data.json');
      if (fs.existsSync(fallbackPath)) {
        const raw = fs.readFileSync(fallbackPath, 'utf-8');
        const arr = JSON.parse(raw);
        prices = (arr as any[])
          .filter((r) => r.code === code)
          .map((r) => ({
            date: r.date,
            open: r.open,
            high: r.high,
            low: r.low,
            close: r.close,
            volume: r.volume,
            code: r.code,
          }));
      }
    }

    if (!prices || prices.length === 0) {
      return NextResponse.json({ error: 'no_data', message: '価格データが見つかりません' }, { status: 404 });
    }

    // スプリット等の補正: 既存処理があればここで適用予定（今回は素通し）

    // 指標付与
    const enriched = enrichWithIndicators(prices, { todayFinalOnly: true });

    // 範囲切替
    const ranged = range ? sliceByRange(enriched, range) : enriched;

    // エッジケース: 直近3本未満 → 価格のみ
    const output = ranged.length < 3
      ? toStocksApiResponse(code, ranged.map(d => ({ ...d, sma_5: undefined, sma_25: undefined, sma_75: undefined, ema_12: undefined, ema_26: undefined, macd: undefined, macd_signal: undefined, macd_hist: undefined, rsi_14: undefined } as any)), range ?? undefined)
      : toStocksApiResponse(code, ranged, range ?? undefined);

    return NextResponse.json(output, {
      headers: {
        'Cache-Control': 'public, max-age=300',
      },
    });
  } catch (error: any) {
    return NextResponse.json({ error: 'internal_error', message: error?.message ?? 'unknown error' }, { status: 500 });
  }
}


