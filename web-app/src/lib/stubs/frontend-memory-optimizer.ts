export const frontendMemoryOptimizer = {
  optimizeMemory() {},
  downsampleChartData<T>(data: T[], maxPoints: number) {
    if (!Array.isArray(data)) return [] as T[];
    if (data.length <= maxPoints) return data;
    const step = Math.ceil(data.length / maxPoints);
    const result: T[] = [];
    for (let i = 0; i < data.length; i += step) result.push(data[i]);
    return result;
  },
  getCurrentMemoryUsage() {
    return 0;
  },
  cleanup() {},
};

export default frontendMemoryOptimizer;

