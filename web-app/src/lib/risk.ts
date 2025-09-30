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


