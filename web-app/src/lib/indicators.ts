// タイムシリーズ指標計算と欠損処理（JST固定）
import { DateTime } from "luxon";

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
  const dt = typeof input === "string"
    ? DateTime.fromISO(input, { zone: "Asia/Tokyo" })
    : DateTime.fromJSDate(input, { zone: "Asia/Tokyo" });
  if (dt.isValid) return dt.set({ hour: 0, minute: 0, second: 0, millisecond: 0 });
  // フォールバック: YYYY-MM-DD 形式
  const alt = DateTime.fromFormat(String(input), "yyyy-MM-dd", { zone: "Asia/Tokyo" });
  return alt.isValid ? alt : DateTime.invalid("invalid-input");
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
      filled.push({ ...cur, date: cur._dt.toISODate() ?? cur._dt.toFormat("yyyy-LL-dd") });
      continue;
    }
    const prev = sorted[i - 1];
    let d = prev._dt.plus({ days: 1 });
    while (d < cur._dt) {
      // 前回値フォワード
      const prevBar = filled[filled.length - 1];
      filled.push({
        date: d.toISODate() ?? d.toFormat("yyyy-LL-dd"),
        open: prevBar.open,
        high: prevBar.high,
        low: prevBar.low,
        close: prevBar.close,
        volume: prevBar.volume ?? 0,
        code: prevBar.code,
      });
      d = d.plus({ days: 1 });
    }
    filled.push({ ...cur, date: cur._dt.toISODate() ?? cur._dt.toFormat("yyyy-LL-dd") });
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
  const jstToday = DateTime.now().setZone("Asia/Tokyo").startOf("day");
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

export function sliceByRange(data: EnrichedBar[], range: "5y" | "1y" | "3m" | "1m"): EnrichedBar[] {
  if (!data.length) return data;
  const last = DateTime.fromMillis(data[data.length - 1].ts, { zone: "Asia/Tokyo" });
  const from = {
    "5y": last.minus({ years: 5 }),
    "1y": last.minus({ years: 1 }),
    "3m": last.minus({ months: 3 }),
    "1m": last.minus({ months: 1 }),
  }[range] ?? last.minus({ years: 1 });
  return data.filter(b => b.ts >= from.toMillis());
}

export type StocksApiResponse = {
  code: string;
  prices: Array<Pick<EnrichedBar, "date" | "open" | "high" | "low" | "close" | "volume">>;
  indicators: Array<Pick<EnrichedBar, "date" | "sma_5" | "sma_25" | "sma_75" | "ema_12" | "ema_26" | "macd" | "macd_signal" | "macd_hist" | "rsi_14">>;
  meta: {
    timezone: "Asia/Tokyo";
    latestBarPolicy: "finalized_only";
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
      timezone: "Asia/Tokyo",
      latestBarPolicy: "finalized_only",
      filledGaps: true,
      range,
    },
  };
}



// ---- テスト互換API: 単体関数のエクスポート ----
export function calculateSMA(values: number[], window: number): number[] {
  if (!Array.isArray(values) || values.length < window) return [];
  const out: number[] = [];
  let sum = 0;
  for (let i = 0; i < values.length; i++) {
    sum += values[i];
    if (i >= window) sum -= values[i - window];
    if (i >= window - 1) out.push(sum / window);
  }
  return out;
}

export function calculateEMA(values: number[], span: number): number[] {
  if (!Array.isArray(values) || values.length === 0) return [];
  const out: number[] = [];
  const k = 2 / (span + 1);
  let prev: number | undefined = undefined;
  for (let i = 0; i < values.length; i++) {
    const v = values[i];
    prev = prev === undefined ? v : v * k + prev * (1 - k);
    out.push(prev);
  }
  return out;
}

export function calculateRSI(values: number[], period = 14): number[] {
  if (!Array.isArray(values) || values.length === 0) return [];
  const out: number[] = [];
  let prev = values[0];
  let avgGain = 0;
  let avgLoss = 0;
  for (let i = 1; i < values.length; i++) {
    const change = values[i] - prev;
    const gain = Math.max(change, 0);
    const loss = Math.max(-change, 0);
    avgGain = (avgGain * (period - 1) + gain) / period;
    avgLoss = (avgLoss * (period - 1) + loss) / period;
    const rs = avgLoss === 0 ? 100 : avgGain / avgLoss;
    out.push(100 - 100 / (1 + rs));
    prev = values[i];
  }
  // 先頭はそのまま
  return [values[0], ...out].slice(0, values.length);
}

export function calculateMACD(values: number[], shortSpan = 12, longSpan = 26, signalSpan = 9): { macd: number[]; signal: number[]; histogram: number[] } {
  const emaShort = calculateEMA(values, shortSpan);
  const emaLong = calculateEMA(values, longSpan);
  const macd = values.map((_, i) => (emaShort[i] ?? 0) - (emaLong[i] ?? 0));
  const signal = calculateEMA(macd, signalSpan);
  const histogram = macd.map((v, i) => v - (signal[i] ?? 0));
  return { macd, signal, histogram };
}

export function calculateBollingerBands(values: number[], window = 20, k = 2): { upper: number[]; middle: number[]; lower: number[] } {
  if (!Array.isArray(values) || values.length === 0) return { upper: [], middle: [], lower: [] };
  const middle = calculateSMA(values, window);
  const upper: number[] = [];
  const lower: number[] = [];
  for (let i = window - 1; i < values.length; i++) {
    const slice = values.slice(i - window + 1, i + 1);
    const mean = middle[i - window + 1];
    const variance = slice.reduce((s, v) => s + Math.pow(v - mean, 2), 0) / window;
    const std = Math.sqrt(variance);
    upper.push(mean + k * std);
    lower.push(mean - k * std);
  }
  return { upper, middle, lower };
}

export function calculateStochastic(highs: number[], lows: number[], closes: number[], period = 14): { k: number[]; d: number[] } {
  const k: number[] = [];
  for (let i = period - 1; i < closes.length; i++) {
    const hh = Math.max(...highs.slice(i - period + 1, i + 1));
    const ll = Math.min(...lows.slice(i - period + 1, i + 1));
    const c = closes[i];
    const val = hh === ll ? 0 : ((c - ll) / (hh - ll)) * 100;
    k.push(val);
  }
  const d = calculateSMA(k, 3);
  return { k, d };
}

export function calculateWilliamsR(highs: number[], lows: number[], closes: number[], period = 14): number[] {
  const out: number[] = [];
  for (let i = period - 1; i < closes.length; i++) {
    const hh = Math.max(...highs.slice(i - period + 1, i + 1));
    const ll = Math.min(...lows.slice(i - period + 1, i + 1));
    const c = closes[i];
    const val = hh === ll ? 0 : ((hh - c) / (hh - ll)) * 100 * -1; // -100..0
    out.push(val);
  }
  return out;
}

export function calculateCCI(highs: number[], lows: number[], closes: number[], period = 20): number[] {
  const out: number[] = [];
  for (let i = period - 1; i < closes.length; i++) {
    const typical = closes.slice(i - period + 1, i + 1).map((_, idx) => (highs[i - period + 1 + idx] + lows[i - period + 1 + idx] + closes[i - period + 1 + idx]) / 3);
    const sma = typical.reduce((s, v) => s + v, 0) / period;
    const meanDev = typical.reduce((s, v) => s + Math.abs(v - sma), 0) / period;
    const cci = meanDev === 0 ? 0 : (typical[typical.length - 1] - sma) / (0.015 * meanDev);
    out.push(cci);
  }
  return out;
}

export function calculateATR(highs: number[], lows: number[], closes: number[], period = 14): number[] {
  const trs: number[] = [];
  for (let i = 1; i < closes.length; i++) {
    const tr = Math.max(highs[i] - lows[i], Math.abs(highs[i] - closes[i - 1]), Math.abs(lows[i] - closes[i - 1]));
    trs.push(tr);
  }
  return calculateEMA(trs, period);
}

export function calculateADX(highs: number[], lows: number[], closes: number[], period = 14): number[] {
  // 簡易的なADX: TRとDMからの近似
  const plusDM: number[] = [];
  const minusDM: number[] = [];
  const tr: number[] = [];
  for (let i = 1; i < highs.length; i++) {
    const upMove = highs[i] - highs[i - 1];
    const downMove = lows[i - 1] - lows[i];
    plusDM.push(upMove > downMove && upMove > 0 ? upMove : 0);
    minusDM.push(downMove > upMove && downMove > 0 ? downMove : 0);
    tr.push(Math.max(highs[i] - lows[i], Math.abs(highs[i] - closes[i - 1]), Math.abs(lows[i] - closes[i - 1])));
  }
  const smoothTR = calculateEMA(tr, period);
  const smoothPlusDM = calculateEMA(plusDM, period);
  const smoothMinusDM = calculateEMA(minusDM, period);
  const plusDI = smoothTR.map((v, i) => (v ? (smoothPlusDM[i] ?? 0) / v * 100 : 0));
  const minusDI = smoothTR.map((v, i) => (v ? (smoothMinusDM[i] ?? 0) / v * 100 : 0));
  const dx = plusDI.map((v, i) => {
    const m = minusDI[i] ?? 0;
    const denom = v + m;
    return denom === 0 ? 0 : (Math.abs(v - m) / denom) * 100;
  });
  return calculateEMA(dx, period);
}
