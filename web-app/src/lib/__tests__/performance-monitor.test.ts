import { 
  startPerformanceMonitoring, 
  stopPerformanceMonitoring, 
  getPerformanceMetrics,
  getPerformanceReport,
  clearPerformanceMetrics,
  setPerformanceThresholds,
  getPerformanceThresholds,
  isPerformanceMonitoringActive,
  getPerformanceAlerts,
  clearPerformanceAlerts,
  exportPerformanceData,
  importPerformanceData
} from "../performance-monitor";

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

describe("performance-monitor", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("startPerformanceMonitoring", () => {
    it("starts performance monitoring", () => {
      startPerformanceMonitoring();
      expect(isPerformanceMonitoringActive()).toBe(true);
    });

    it("handles already active monitoring", () => {
      startPerformanceMonitoring();
      startPerformanceMonitoring(); // Should not throw
      expect(isPerformanceMonitoringActive()).toBe(true);
    });
  });

  describe("stopPerformanceMonitoring", () => {
    it("stops performance monitoring", () => {
      startPerformanceMonitoring();
      stopPerformanceMonitoring();
      expect(isPerformanceMonitoringActive()).toBe(false);
    });

    it("handles already stopped monitoring", () => {
      stopPerformanceMonitoring(); // Should not throw
      expect(isPerformanceMonitoringActive()).toBe(false);
    });
  });

  describe("getPerformanceMetrics", () => {
    it("returns performance metrics", () => {
      const metrics = getPerformanceMetrics();
      expect(metrics).toHaveProperty("cpu");
      expect(metrics).toHaveProperty("memory");
      expect(metrics).toHaveProperty("network");
      expect(metrics).toHaveProperty("rendering");
    });

    it("includes timing information", () => {
      const metrics = getPerformanceMetrics();
      expect(metrics).toHaveProperty("timing");
      expect(metrics.timing).toHaveProperty("domContentLoaded");
      expect(metrics.timing).toHaveProperty("loadComplete");
    });
  });

  describe("getPerformanceReport", () => {
    it("generates performance report", () => {
      const report = getPerformanceReport();
      expect(report).toHaveProperty("summary");
      expect(report).toHaveProperty("metrics");
      expect(report).toHaveProperty("recommendations");
    });

    it("includes performance score", () => {
      const report = getPerformanceReport();
      expect(report.summary).toHaveProperty("score");
      expect(report.summary.score).toBeGreaterThanOrEqual(0);
      expect(report.summary.score).toBeLessThanOrEqual(100);
    });
  });

  describe("clearPerformanceMetrics", () => {
    it("clears performance metrics", () => {
      clearPerformanceMetrics();
      const metrics = getPerformanceMetrics();
      expect(metrics.cpu.usage).toBe(0);
      expect(metrics.memory.used).toBe(0);
    });
  });

  describe("setPerformanceThresholds", () => {
    it("sets performance thresholds", () => {
      const thresholds = {
        cpu: 80,
        memory: 90,
        network: 1000,
        rendering: 16,
      };
      setPerformanceThresholds(thresholds);
      expect(getPerformanceThresholds()).toEqual(thresholds);
    });

    it("validates threshold values", () => {
      expect(() => setPerformanceThresholds({ cpu: -1 })).toThrow();
      expect(() => setPerformanceThresholds({ cpu: 101 })).toThrow();
    });
  });

  describe("getPerformanceThresholds", () => {
    it("returns current thresholds", () => {
      const thresholds = getPerformanceThresholds();
      expect(thresholds).toHaveProperty("cpu");
      expect(thresholds).toHaveProperty("memory");
      expect(thresholds).toHaveProperty("network");
      expect(thresholds).toHaveProperty("rendering");
    });
  });

  describe("isPerformanceMonitoringActive", () => {
    it("returns monitoring status", () => {
      const active = isPerformanceMonitoringActive();
      expect(typeof active).toBe("boolean");
    });
  });

  describe("getPerformanceAlerts", () => {
    it("returns performance alerts", () => {
      const alerts = getPerformanceAlerts();
      expect(Array.isArray(alerts)).toBe(true);
    });
  });

  describe("clearPerformanceAlerts", () => {
    it("clears performance alerts", () => {
      clearPerformanceAlerts();
      const alerts = getPerformanceAlerts();
      expect(alerts).toHaveLength(0);
    });
  });

  describe("exportPerformanceData", () => {
    it("exports performance data", () => {
      const data = exportPerformanceData();
      expect(typeof data).toBe("string");
      
      const parsed = JSON.parse(data);
      expect(parsed).toHaveProperty("metrics");
      expect(parsed).toHaveProperty("timestamp");
    });
  });

  describe("importPerformanceData", () => {
    it("imports performance data", () => {
      const data = {
        metrics: { cpu: { usage: 50 } },
        timestamp: Date.now(),
      };
      importPerformanceData(JSON.stringify(data));
      
      const metrics = getPerformanceMetrics();
      expect(metrics.cpu.usage).toBe(50);
    });

    it("handles invalid data", () => {
      expect(() => importPerformanceData("invalid")).toThrow();
    });
  }),
});
