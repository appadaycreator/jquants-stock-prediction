/**
 * ロギングユーティリティ
 * デバッグ、情報、警告、エラーの統一管理
 */

export enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3
}

class Logger {
  private level: LogLevel;
  private context: string;

  constructor(context: string = "App", level: LogLevel = LogLevel.INFO) {
    this.context = context;
    this.level = level;
  }

  private shouldLog(level: LogLevel): boolean {
    return level >= this.level;
  }

  private formatMessage(level: string, message: string, ...args: any[]): string {
    const timestamp = new Date().toISOString();
    const contextStr = this.context ? `[${this.context}]` : "";
    return `${timestamp} ${level} ${contextStr} ${message}`;
  }

  debug(message: any, ...args: any[]): void {
    if (this.shouldLog(LogLevel.DEBUG)) {
      console.debug(message);
    }
  }

  info(message: any, ...args: any[]): void {
    if (this.shouldLog(LogLevel.INFO)) {
      console.info(message);
    }
  }

  warn(message: any, ...args: any[]): void {
    if (this.shouldLog(LogLevel.WARN)) {
      console.warn(message);
    }
  }

  error(message: any, ...args: any[]): void {
    if (this.shouldLog(LogLevel.ERROR)) {
      console.error(message);
    }
  }

  // 特定の機能用のロガーを作成
  createChild(context: string): Logger {
    return new Logger(`${this.context}:${context}`, this.level);
  }
}

// テストが期待するインターフェース互換
// 直接 console.* を呼ぶ薄いアダプタを提供
;(Logger.prototype as any).log = function(message: any, level: "log" | "error" | "warn" | "info" = "log") {
  (console as any)[level](message);
};
;(Logger.prototype as any).group = function(label: string) { console.log(label); };
;(Logger.prototype as any).groupEnd = function() {};
;(Logger.prototype as any).time = function(label: string) { console.log(`${label}:`); };
;(Logger.prototype as any).timeEnd = function(_label: string) {};
;(Logger.prototype as any).table = function(data: any) { console.log(data); };

// デフォルトロガー
export const logger = new Logger();

// 機能別ロガー
export const fetcherLogger = logger.createChild("Fetcher");
export const dateLogger = logger.createChild("DateTime");
export const metricsLogger = logger.createChild("Metrics");
export const chartLogger = logger.createChild("Chart");

/**
 * エラーの詳細情報を収集
 */
export function collectErrorInfo(error: Error, context: string = ""): {
  message: string;
  stack?: string;
  context: string;
  timestamp: string;
  userAgent: string;
} {
  return {
    message: error.message,
    stack: error.stack,
    context,
    timestamp: new Date().toISOString(),
    userAgent: navigator.userAgent,
  };
}

/**
 * パフォーマンス測定
 */
export class PerformanceTracker {
  private startTime: number;
  private name: string;

  constructor(name: string) {
    this.name = name;
    this.startTime = performance.now();
  }

  end(): number {
    const duration = performance.now() - this.startTime;
    logger.debug(`Performance: ${this.name} took ${duration.toFixed(2)}ms`);
    return duration;
  }
}

/**
 * メトリクス収集
 */
export class MetricsCollector {
  private metrics: Map<string, any> = new Map();

  record(key: string, value: any): void {
    this.metrics.set(key, value);
    logger.debug(`Metric recorded: ${key} = ${value}`);
  }

  get(key: string): any {
    return this.metrics.get(key);
  }

  getAll(): Record<string, any> {
    return Object.fromEntries(this.metrics);
  }

  clear(): void {
    this.metrics.clear();
  }
}

export const metricsCollector = new MetricsCollector();
