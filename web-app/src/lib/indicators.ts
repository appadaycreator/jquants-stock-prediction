// タイムシリーズ指標計算と欠損処理（JST固定）
import { DateTime } from 'luxon';

export type PriceBar = {
  date: string; // ISO 文字列または YYYY-MM-DD
  open: number;
  high: number;
  low: number;
  close: number;
  volume?: number;
  code?: string;
};

export type Indicators = {
  sma_5?: number;
  sma_25?: number;
  sma_75?: number;
  ema_12?: number;
  ema_26?: number;
  macd?: number;
  macd_signal?: number;
  macd_hist?: number;
  rsi_14?: number;
};

export type EnrichedBar = PriceBar & Indicators & {
  ts: number; // JST のミリ秒
};

const toJstDate = (input: string | Date): DateTime => {
  const dt = typeof input === 'string'
    ? DateTime.fromISO(input, { zone: 'Asia/Tokyo' })
    : DateTime.fromJSDate(input, { zone: 'Asia/Tokyo' });
  if (dt.isValid) return dt.set({ hour: 0, minute: 0, second: 0, millisecond: 0 });
  // フォールバック: YYYY-MM-DD 形式
  const alt = DateTime.fromFormat(String(input), 'yyyy-MM-dd', { zone: 'Asia/Tokyo' });
  return alt.isValid ? alt : DateTime.invalid('invalid-input');
};

export function forwardFillMissingDays(bars: PriceBar[]): PriceBar[] {
  if (!bars || bars.length === 0) return [];
  // 日付昇順に正規化
  const sorted = [...bars]
    .map(b => ({ ...b, _dt: toJstDate(b.date) }))
    .filter(b => b._dt.isValid)
    .sort((a, b) => a._dt.toMillis() - b._dt.toMillis());

  const filled: PriceBar[] = [];
  for (let i = 0; i < sorted.length; i++) {
    const cur = sorted[i];
    if (i === 0) {
      filled.push({ ...cur, date: cur._dt.toISODate() });
      continue;
    }
    const prev = sorted[i - 1];
    let d = prev._dt.plus({ days: 1 });
    while (d < cur._dt) {
      // 前回値フォワード
      const prevBar = filled[filled.length - 1];
      filled.push({
        date: d.toISODate(),
        open: prevBar.open,
        high: prevBar.high,
        low: prevBar.low,
        close: prevBar.close,
        volume: prevBar.volume ?? 0,
        code: prevBar.code,
      });
      d = d.plus({ days: 1 });
    }
    filled.push({ ...cur, date: cur._dt.toISODate() });
  }
  return filled;
}

function sma(values: number[], window: number): (number | undefined)[] {
  const out: (number | undefined)[] = new Array(values.length).fill(undefined);
  let sum = 0;
  for (let i = 0; i < values.length; i++) {
    sum += values[i];
    if (i >= window) sum -= values[i - window];
    if (i >= window - 1) out[i] = sum / window;
  }
  return out;
}

function ema(values: number[], span: number): (number | undefined)[] {
  const out: (number | undefined)[] = new Array(values.length).fill(undefined);
  if (values.length === 0) return out;
  const k = 2 / (span + 1);
  let prev: number | undefined = undefined;
  for (let i = 0; i < values.length; i++) {
    const v = values[i];
    prev = prev === undefined ? v : v * k + prev * (1 - k);
    out[i] = prev;
  }
  return out;
}

function rsi(values: number[], period = 14): (number | undefined)[] {
  const out: (number | undefined)[] = new Array(values.length).fill(undefined);
  if (values.length === 0) return out;
  let prev = values[0];
  let avgGain = 0;
  let avgLoss = 0;
  for (let i = 1; i < values.length; i++) {
    const change = values[i] - prev;
    const gain = Math.max(change, 0);
    const loss = Math.max(-change, 0);
    // Wilder の平滑化（EMAベース）
    avgGain = (avgGain * (period - 1) + gain) / period;
    avgLoss = (avgLoss * (period - 1) + loss) / period;
    if (i >= period) {
      const rs = avgLoss === 0 ? 100 : avgGain / avgLoss;
      out[i] = 100 - 100 / (1 + rs);
    }
    prev = values[i];
  }
  return out;
}

export function enrichWithIndicators(input: PriceBar[], options?: { todayFinalOnly?: boolean }): EnrichedBar[] {
  if (!input || input.length === 0) return [];

  // 未確定足排除: 当日途中は前日終値まで
  const jstToday = DateTime.now().setZone('Asia/Tokyo').startOf('day');
  const trimmed = (options?.todayFinalOnly ?? true)
    ? input.filter(b => toJstDate(b.date) < jstToday.plus({ days: 0 }))
    : input;

  const filled = forwardFillMissingDays(trimmed);
  const closes = filled.map(b => b.close);

  const sma5 = sma(closes, 5);
  const sma25 = sma(closes, 25);
  const sma75 = sma(closes, 75);
  const ema12 = ema(closes, 12);
  const ema26 = ema(closes, 26);
  const macdLine = closes.map((_, i) => {
    const e12 = ema12[i];
    const e26 = ema26[i];
    return e12 !== undefined && e26 !== undefined ? e12 - e26 : undefined;
  });
  const macdSignal = ema(macdLine.map(v => v ?? NaN).map(v => (Number.isFinite(v) ? (v as number) : 0)), 9);
  const macdHist = macdLine.map((v, i) => (v !== undefined && macdSignal[i] !== undefined ? v - (macdSignal[i] as number) : undefined));
  const rsi14 = rsi(closes, 14);

  const enriched: EnrichedBar[] = filled.map((b, i) => {
    const dt = toJstDate(b.date);
    return {
      ...b,
      ts: dt.toMillis(),
      sma_5: sma5[i],
      sma_25: sma25[i],
      sma_75: sma75[i],
      ema_12: ema12[i],
      ema_26: ema26[i],
      macd: macdLine[i],
      macd_signal: macdSignal[i],
      macd_hist: macdHist[i],
      rsi_14: rsi14[i],
    };
  });

  return enriched;
}

export function sliceByRange(data: EnrichedBar[], range: '5y' | '1y' | '3m' | '1m'): EnrichedBar[] {
  if (!data.length) return data;
  const last = DateTime.fromMillis(data[data.length - 1].ts, { zone: 'Asia/Tokyo' });
  const from = {
    '5y': last.minus({ years: 5 }),
    '1y': last.minus({ years: 1 }),
    '3m': last.minus({ months: 3 }),
    '1m': last.minus({ months: 1 }),
  }[range] ?? last.minus({ years: 1 });
  return data.filter(b => b.ts >= from.toMillis());
}

export type StocksApiResponse = {
  code: string;
  prices: Array<Pick<EnrichedBar, 'date' | 'open' | 'high' | 'low' | 'close' | 'volume'>>;
  indicators: Array<Pick<EnrichedBar, 'date' | 'sma_5' | 'sma_25' | 'sma_75' | 'ema_12' | 'ema_26' | 'macd' | 'macd_signal' | 'macd_hist' | 'rsi_14'>>;
  meta: {
    timezone: 'Asia/Tokyo';
    latestBarPolicy: 'finalized_only';
    filledGaps: boolean;
    range?: string;
  };
};

export function toStocksApiResponse(code: string, data: EnrichedBar[], range?: string): StocksApiResponse {
  return {
    code,
    prices: data.map(d => ({
      date: d.date,
      open: d.open,
      high: d.high,
      low: d.low,
      close: d.close,
      volume: d.volume ?? 0,
    })),
    indicators: data.map(d => ({
      date: d.date,
      sma_5: d.sma_5,
      sma_25: d.sma_25,
      sma_75: d.sma_75,
      ema_12: d.ema_12,
      ema_26: d.ema_26,
      macd: d.macd,
      macd_signal: d.macd_signal,
      macd_hist: d.macd_hist,
      rsi_14: d.rsi_14,
    })),
    meta: {
      timezone: 'Asia/Tokyo',
      latestBarPolicy: 'finalized_only',
      filledGaps: true,
      range,
    },
  };
}


