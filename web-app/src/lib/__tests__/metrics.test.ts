import { metrics } from "../metrics";
// Performance API のモック
const mockPerformance = {
  now: jest.fn(() => Date.now()),
  mark: jest.fn(),
  measure: jest.fn(),
  getEntriesByName: jest.fn(() => []),
  getEntriesByType: jest.fn(() => []),
  clearMarks: jest.fn(),
  clearMeasures: jest.fn(),
};
Object.defineProperty(window, "performance", {
  value: mockPerformance,
});
describe("metrics", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    metrics.clearMetrics();
  });
  describe("startTimer", () => {
    it("starts a timer", () => {
      const timer = metrics.startTimer("test-timer");
      expect(timer).toBeDefined();
      expect(typeof timer.stop).toBe("function");
    });
  });
  describe("measureTime", () => {
    it("measures execution time", async () => {
      const result = await metrics.measureTime("test-measure", async () => {
        await new Promise(resolve => setTimeout(resolve, 10));
        return "result";
      });
      
      expect(result).toBe("result");
      expect(mockPerformance.mark).toHaveBeenCalled();
      expect(mockPerformance.measure).toHaveBeenCalled();
    });
  });
  describe("incrementCounter", () => {
    it("increments a counter", () => {
      metrics.incrementCounter("test-counter");
      expect(metrics.getCounter("test-counter")).toBe(1);
      
      metrics.incrementCounter("test-counter");
      expect(metrics.getCounter("test-counter")).toBe(2);
    });
  });
  describe("decrementCounter", () => {
    it("decrements a counter", () => {
      metrics.incrementCounter("test-counter", 5);
      metrics.decrementCounter("test-counter");
      expect(metrics.getCounter("test-counter")).toBe(4);
    });
  });
  describe("setGauge", () => {
    it("sets a gauge value", () => {
      metrics.setGauge("test-gauge", 100);
      expect(metrics.getGauge("test-gauge")).toBe(100);
    });
  });
  describe("addHistogram", () => {
    it("adds a histogram value", () => {
      metrics.addHistogram("test-histogram", 50);
      const histogram = metrics.getHistogram("test-histogram");
      expect(histogram.values).toContain(50);
    });
  });
  describe("getAllMetrics", () => {
    it("returns all metrics", () => {
      metrics.incrementCounter("test-counter");
      metrics.setGauge("test-gauge", 100);
      
      const allMetrics = metrics.getAllMetrics();
      expect(allMetrics.counters).toHaveProperty("test-counter");
      expect(allMetrics.gauges).toHaveProperty("test-gauge");
    });
  });
  describe("clearMetrics", () => {
    it("clears all metrics", () => {
      metrics.incrementCounter("test-counter");
      metrics.setGauge("test-gauge", 100);
      
      metrics.clearMetrics();
      
      expect(metrics.getCounter("test-counter")).toBe(0);
      expect(metrics.getGauge("test-gauge")).toBe(0);
    });
  });
  describe("exportMetrics", () => {
    it("exports metrics in JSON format", () => {
      metrics.incrementCounter("test-counter");
      metrics.setGauge("test-gauge", 100);
      
      const exported = metrics.exportMetrics();
      expect(typeof exported).toBe("string");
      
      const parsed = JSON.parse(exported);
      expect(parsed.counters).toHaveProperty("test-counter");
      expect(parsed.gauges).toHaveProperty("test-gauge");
    });
  });
});
