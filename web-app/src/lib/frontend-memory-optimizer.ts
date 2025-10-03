// メモリ最適化ユーティリティの最小実装
// ランタイムでのフォールバックと互換のAPIを提供

export type ChartPoint = Record<string, any>;

function downsample(data: ChartPoint[], maxPoints: number): ChartPoint[] {
  if (!Array.isArray(data) || data.length <= maxPoints) return data;
  const step = Math.ceil(data.length / maxPoints);
  const sampled: ChartPoint[] = [];
  for (let i = 0; i < data.length; i += step) sampled.push(data[i]);
  return sampled;
}

function getMemoryUsageMb(): number {
  if (typeof performance !== "undefined" && (performance as any).memory) {
    const used = (performance as any).memory.usedJSHeapSize;
    return Math.round((used / (1024 * 1024)) * 100) / 100;
  }
  return 0;
}

export const frontendMemoryOptimizer = {
  downsampleChartData: (data: ChartPoint[], maxPoints: number) => downsample(data, maxPoints),
  getCurrentMemoryUsage: () => getMemoryUsageMb(),
  optimizeMemory: () => {
    // GCは明示的に呼べないため、参照を切る用途のフックだけ提供
  },
};

export default frontendMemoryOptimizer;


