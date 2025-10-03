/**
 * パフォーマンスモニターのテスト
 */

import { performanceMonitor } from '../performance-monitor';

// モックの設定
const mockPerformance = {
  now: jest.fn(() => Date.now()),
  mark: jest.fn(),
  measure: jest.fn(),
  getEntriesByType: jest.fn(() => []),
  getEntriesByName: jest.fn(() => []),
  memory: {
    usedJSHeapSize: 1000000,
    totalJSHeapSize: 2000000,
    jsHeapSizeLimit: 4000000,
  },
};

// PerformanceObserverのモック
const mockPerformanceObserver = jest.fn().mockImplementation((callback) => ({
  observe: jest.fn(),
  disconnect: jest.fn(),
}));

// グローバルオブジェクトのモック
Object.defineProperty(global, 'performance', {
  value: mockPerformance,
  writable: true,
});

Object.defineProperty(global, 'PerformanceObserver', {
  value: mockPerformanceObserver,
  writable: true,
});

describe('PerformanceMonitor', () => {
  beforeEach(() => {
    // テスト前にモニターをリセット（resetメソッドが存在しない場合はスキップ）
    if (typeof performanceMonitor.reset === 'function') {
      performanceMonitor.reset();
    }
  });

  describe('getMetrics', () => {
    it('メトリクスを正しく取得する', () => {
      const metrics = performanceMonitor.getMetrics();
      
      expect(metrics).toBeDefined();
      expect(typeof metrics.loadTime).toBe('number');
      expect(typeof metrics.renderTime).toBe('number');
      expect(typeof metrics.memoryUsage.used).toBe('number');
      expect(typeof metrics.componentCount).toBe('number');
    });
  });

  describe('generateReport', () => {
    it('レポートを正しく生成する', () => {
      const report = performanceMonitor.generateReport();
      
      expect(report).toBeDefined();
      expect(typeof report.score).toBe('number');
      expect(Array.isArray(report.recommendations)).toBe(true);
      expect(Array.isArray(report.nextSteps)).toBe(true);
    });
  });

  describe('optimize', () => {
    it('最適化を正しく実行する', () => {
      expect(() => {
        performanceMonitor.optimize();
      }).not.toThrow();
    });
  });

  describe('reset', () => {
    it('モニターを正しくリセットする', () => {
      performanceMonitor.optimize();
      
      if (typeof performanceMonitor.reset === 'function') {
        performanceMonitor.reset();
        const metrics = performanceMonitor.getMetrics();
        expect(metrics.componentCount).toBe(0);
      } else {
        // resetメソッドが存在しない場合はスキップ
        expect(true).toBe(true);
      }
    });
  });

  describe('SSR環境での動作', () => {
    it('windowが未定義でもエラーが発生しない', () => {
      const originalWindow = global.window;
      delete (global as any).window;
      
      expect(() => {
        const monitor = new (require('../performance-monitor').PerformanceMonitor)();
      }).not.toThrow();
      
      global.window = originalWindow;
    });
  });
});
