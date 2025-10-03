export const performanceValidator = {
  recordChartRenderTime(_ms: number) {},
  recordFinalMemoryUsage() {},
  validate() {
    return {
      success: true,
      score: 100,
      metrics: {
        initialLoadTime: 0,
        chartRenderTime: 0,
        memoryUsage: { after: 0, reduction: 0 },
        coreWebVitals: { lcp: 0, fid: 0, cls: 0 },
      },
      recommendations: [],
    } as any;
  },
  cleanup() {},
};

export default performanceValidator;

