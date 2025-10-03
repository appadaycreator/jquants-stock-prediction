// リスク指標ユーティリティ
// 注意: クライアントサイドで軽量に動作する簡易実装

export function computeDailyReturns(prices: number[]): number[] {
  if (!prices || prices.length < 2) return [];
  const returns: number[] = [];
  for (let i = 1; i < prices.length; i++) {
    const prev = prices[i - 1];
    const curr = prices[i];
    if (prev > 0) {
      returns.push((curr - prev) / prev);
    }
  }
  return returns;
}

export function computeMaxDrawdown(prices: number[]): number {
  if (!prices || prices.length < 2) return 0;
  let peak = prices[0];
  let maxDrawdown = 0;
  for (let i = 1; i < prices.length; i++) {
    const price = prices[i];
    if (price > peak) {
      peak = price;
    } else if (peak > 0) {
      const drawdown = (peak - price) / peak;
      if (drawdown > maxDrawdown) maxDrawdown = drawdown;
    }
  }
  return maxDrawdown; // 比率 (0-1)
}

export function computeHistoricalVaR95(prices: number[]): number {
  const returns = computeDailyReturns(prices);
  if (returns.length === 0) return 0;
  // 5パーセンタイル（下側テール）
  const sorted = [...returns].sort((a, b) => a - b);
  const idx = Math.floor(0.05 * (sorted.length - 1));
  const p5 = sorted[idx];
  // VaRは損失の大きさとして正の値で返す
  return Math.max(0, -p5);
}

export function computeAnnualizedVolatility(prices: number[]): number {
  const returns = computeDailyReturns(prices);
  if (returns.length === 0) return 0;
  const mean = returns.reduce((s, r) => s + r, 0) / returns.length;
  const variance =
    returns.reduce((s, r) => s + (r - mean) * (r - mean), 0) /
    (returns.length - 1 || 1);
  const dailyStd = Math.sqrt(variance);
  return dailyStd * Math.sqrt(252);
}

export function toPercent(value: number, digits = 2): string {
  return `${(value * 100).toFixed(digits)}%`;
}

// ---- テスト互換API（../__tests__/risk.test.ts が期待）----
export function calculateVaR(returns: number[], confidence: number): number {
  if (!returns || returns.length === 0) return 0;
  const sorted = [...returns].sort((a, b) => a - b);
  const alpha = 1 - confidence;
  const idx = Math.floor(alpha * (sorted.length - 1));
  return sorted[idx]; // 下側テールは負方向
}

export function calculateCVaR(returns: number[], confidence: number): number {
  if (!returns || returns.length === 0) return 0;
  const varValue = calculateVaR(returns, confidence);
  const tail = returns.filter((r) => r <= varValue);
  if (tail.length === 0) return varValue;
  const avg = tail.reduce((s, v) => s + v, 0) / tail.length;
  return avg;
}

export function calculateVolatility(returns: number[]): number {
  if (!returns || returns.length === 0) return 0;
  const mean = returns.reduce((s, r) => s + r, 0) / returns.length;
  const variance = returns.reduce((s, r) => s + (r - mean) * (r - mean), 0) / (returns.length || 1);
  return Math.sqrt(variance);
}

export function calculateSharpeRatio(returns: number[], riskFreeRate: number): number {
  if (!returns || returns.length === 0) return 0;
  const mean = returns.reduce((s, r) => s + r, 0) / returns.length;
  const vol = calculateVolatility(returns);
  return vol === 0 ? 0 : (mean - riskFreeRate / 252) / vol;
}

export function calculateSortinoRatio(returns: number[], riskFreeRate: number): number {
  if (!returns || returns.length === 0) return 0;
  const mean = returns.reduce((s, r) => s + r, 0) / returns.length;
  const downside = returns.filter((r) => r < riskFreeRate / 252);
  if (downside.length === 0) return 0;
  const dsMean = downside.reduce((s, r) => s + r, 0) / downside.length;
  const dsVar = downside.reduce((s, r) => s + (r - dsMean) * (r - dsMean), 0) / downside.length;
  const dsDev = Math.sqrt(dsVar);
  return dsDev === 0 ? 0 : (mean - riskFreeRate / 252) / dsDev;
}

export function calculateMaxDrawdown(prices: number[]): number {
  const dd = computeMaxDrawdown(prices);
  // 小数誤差で -0 を返さないように正規化
  const v = -dd;
  return Object.is(v, -0) ? 0 : v;
}

export function calculateBeta(returns: number[], benchmark: number[]): number {
  if (!returns.length || returns.length !== benchmark.length) return 0;
  const meanR = returns.reduce((s, r) => s + r, 0) / returns.length;
  const meanB = benchmark.reduce((s, r) => s + r, 0) / benchmark.length;
  let cov = 0;
  let varB = 0;
  for (let i = 0; i < returns.length; i++) {
    cov += (returns[i] - meanR) * (benchmark[i] - meanB);
    varB += (benchmark[i] - meanB) * (benchmark[i] - meanB);
  }
  cov /= returns.length;
  varB /= returns.length;
  return varB === 0 ? 0 : cov / varB;
}

export function calculateCorrelation(a: number[], b: number[]): number {
  if (!a.length || a.length !== b.length) return 0;
  const meanA = a.reduce((s, r) => s + r, 0) / a.length;
  const meanB = b.reduce((s, r) => s + r, 0) / b.length;
  let num = 0, denA = 0, denB = 0;
  for (let i = 0; i < a.length; i++) {
    const da = a[i] - meanA;
    const db = b[i] - meanB;
    num += da * db;
    denA += da * da;
    denB += db * db;
  }
  const den = Math.sqrt(denA) * Math.sqrt(denB);
  return den === 0 ? 0 : num / den;
}

export function calculateSkewness(returns: number[]): number {
  if (!returns.length) return 0;
  const mean = returns.reduce((s, r) => s + r, 0) / returns.length;
  const sd = calculateVolatility(returns);
  if (sd === 0) return 0;
  const m3 = returns.reduce((s, r) => s + Math.pow(r - mean, 3), 0) / returns.length;
  return m3 / Math.pow(sd, 3);
}

export function calculateKurtosis(returns: number[]): number {
  if (!returns.length) return 0;
  const mean = returns.reduce((s, r) => s + r, 0) / returns.length;
  const sd = calculateVolatility(returns);
  if (sd === 0) return 0;
  const m4 = returns.reduce((s, r) => s + Math.pow(r - mean, 4), 0) / returns.length;
  return m4 / Math.pow(sd, 4);
}

