/**
 * 観測性システム
 * 通信・スキーマ検証・日付変換失敗数を集計出力
 */

interface LogMetrics {
  communication: {
    totalRequests: number;
    successfulRequests: number;
    failedRequests: number;
    timeoutErrors: number;
    networkErrors: number;
    httpErrors: { [status: number]: number };
  };
  schemaValidation: {
    totalValidations: number;
    successfulValidations: number;
    failedValidations: number;
    validationErrors: { [field: string]: number };
  };
  dateConversion: {
    totalConversions: number;
    successfulConversions: number;
    failedConversions: number;
    invalidFormats: { [format: string]: number };
  };
  performance: {
    averageResponseTime: number;
    slowestRequests: Array<{ url: string; duration: number; timestamp: string }>;
    memoryUsage: number;
  };
}

class ObservabilityLogger {
  private metrics: LogMetrics;
  private startTime: number;
  private requestTimes: Map<string, number>;
  private slowestRequests: Array<{ url: string; duration: number; timestamp: string }>;

  constructor() {
    this.metrics = {
      communication: {
        totalRequests: 0,
        successfulRequests: 0,
        failedRequests: 0,
        timeoutErrors: 0,
        networkErrors: 0,
        httpErrors: {},
      },
      schemaValidation: {
        totalValidations: 0,
        successfulValidations: 0,
        failedValidations: 0,
        validationErrors: {},
      },
      dateConversion: {
        totalConversions: 0,
        successfulConversions: 0,
        failedConversions: 0,
        invalidFormats: {},
      },
      performance: {
        averageResponseTime: 0,
        slowestRequests: [],
        memoryUsage: 0,
      },
    };
    this.startTime = Date.now();
    this.requestTimes = new Map();
    this.slowestRequests = [];
  }

  /**
   * 通信エラーの記録
   */
  logCommunicationError(error: Error, context: { url: string; method: string; status?: number }) {
    this.metrics.communication.totalRequests++;
    this.metrics.communication.failedRequests++;

    if (error.name === "TimeoutError" || error.message.includes("timeout")) {
      this.metrics.communication.timeoutErrors++;
      console.warn("通信タイムアウト:", {
        url: context.url,
        method: context.method,
        error: error.message,
        timestamp: new Date().toISOString(),
      });
    } else if (error.name === "NetworkError" || error.message.includes("fetch")) {
      this.metrics.communication.networkErrors++;
      console.warn("ネットワークエラー:", {
        url: context.url,
        method: context.method,
        error: error.message,
        timestamp: new Date().toISOString(),
      });
    } else if (context.status) {
      this.metrics.communication.httpErrors[context.status] = 
        (this.metrics.communication.httpErrors[context.status] || 0) + 1;
      console.warn("HTTPエラー:", {
        url: context.url,
        method: context.method,
        status: context.status,
        error: error.message,
        timestamp: new Date().toISOString(),
      });
    }

    this.logMetricsSummary();
  }

  /**
   * 通信成功の記録
   */
  logCommunicationSuccess(context: { url: string; method: string; duration: number }) {
    this.metrics.communication.totalRequests++;
    this.metrics.communication.successfulRequests++;

    // レスポンス時間の記録
    this.updateResponseTime(context.duration);
    this.updateSlowestRequests(context.url, context.duration);

    console.info("通信成功:", {
      url: context.url,
      method: context.method,
      duration: `${context.duration}ms`,
      timestamp: new Date().toISOString(),
    });

    this.logMetricsSummary();
  }

  /**
   * スキーマ検証エラーの記録
   */
  logSchemaValidationError(field: string, value: any, expectedType: string, context?: string) {
    this.metrics.schemaValidation.totalValidations++;
    this.metrics.schemaValidation.failedValidations++;
    this.metrics.schemaValidation.validationErrors[field] = 
      (this.metrics.schemaValidation.validationErrors[field] || 0) + 1;

    console.warn("スキーマ検証エラー:", {
      field,
      value: typeof value === "object" ? JSON.stringify(value) : value,
      expectedType,
      context,
      timestamp: new Date().toISOString(),
    });

    this.logMetricsSummary();
  }

  /**
   * スキーマ検証成功の記録
   */
  logSchemaValidationSuccess(field: string, context?: string) {
    this.metrics.schemaValidation.totalValidations++;
    this.metrics.schemaValidation.successfulValidations++;

    console.info("スキーマ検証成功:", {
      field,
      context,
      timestamp: new Date().toISOString(),
    });
  }

  /**
   * 日付変換エラーの記録
   */
  logDateConversionError(dateString: string, error: Error, context?: string) {
    this.metrics.dateConversion.totalConversions++;
    this.metrics.dateConversion.failedConversions++;

    // 無効なフォーマットの記録
    const format = this.detectDateFormat(dateString);
    this.metrics.dateConversion.invalidFormats[format] = 
      (this.metrics.dateConversion.invalidFormats[format] || 0) + 1;

    console.warn("日付変換エラー:", {
      input: dateString,
      format,
      error: error.message,
      context,
      timestamp: new Date().toISOString(),
    });

    this.logMetricsSummary();
  }

  /**
   * 日付変換成功の記録
   */
  logDateConversionSuccess(dateString: string, result: string, context?: string) {
    this.metrics.dateConversion.totalConversions++;
    this.metrics.dateConversion.successfulConversions++;

    console.info("日付変換成功:", {
      input: dateString,
      output: result,
      context,
      timestamp: new Date().toISOString(),
    });
  }

  /**
   * パフォーマンスメトリクスの記録
   */
  logPerformanceMetrics() {
    const memoryUsage = (performance as any).memory?.usedJSHeapSize || 0;
    this.metrics.performance.memoryUsage = memoryUsage;

    console.info("パフォーマンスメトリクス:", {
      uptime: `${Date.now() - this.startTime}ms`,
      memoryUsage: `${Math.round(memoryUsage / 1024 / 1024)}MB`,
      averageResponseTime: `${this.metrics.performance.averageResponseTime}ms`,
      slowestRequests: this.metrics.performance.slowestRequests.slice(0, 3),
      timestamp: new Date().toISOString(),
    });
  }

  /**
   * メトリクスサマリーの出力
   */
  private logMetricsSummary() {
    const uptime = Date.now() - this.startTime;
    const successRate = this.metrics.communication.totalRequests > 0 
      ? (this.metrics.communication.successfulRequests / this.metrics.communication.totalRequests * 100).toFixed(1)
      : "0";

    console.info("メトリクスサマリー:", {
      uptime: `${Math.round(uptime / 1000)}秒`,
      communication: {
        total: this.metrics.communication.totalRequests,
        success: this.metrics.communication.successfulRequests,
        failure: this.metrics.communication.failedRequests,
        successRate: `${successRate}%`,
        timeouts: this.metrics.communication.timeoutErrors,
        networkErrors: this.metrics.communication.networkErrors,
      },
      schemaValidation: {
        total: this.metrics.schemaValidation.totalValidations,
        success: this.metrics.schemaValidation.successfulValidations,
        failure: this.metrics.schemaValidation.failedValidations,
      },
      dateConversion: {
        total: this.metrics.dateConversion.totalConversions,
        success: this.metrics.dateConversion.successfulConversions,
        failure: this.metrics.dateConversion.failedConversions,
      },
    });
  }

  /**
   * レスポンス時間の更新
   */
  private updateResponseTime(duration: number) {
    const currentAvg = this.metrics.performance.averageResponseTime;
    const totalRequests = this.metrics.communication.totalRequests;
    
    this.metrics.performance.averageResponseTime = 
      (currentAvg * (totalRequests - 1) + duration) / totalRequests;
  }

  /**
   * 最も遅いリクエストの更新
   */
  private updateSlowestRequests(url: string, duration: number) {
    this.slowestRequests.push({
      url,
      duration,
      timestamp: new Date().toISOString(),
    });

    // 上位10件のみ保持
    this.slowestRequests = this.slowestRequests
      .sort((a, b) => b.duration - a.duration)
      .slice(0, 10);

    this.metrics.performance.slowestRequests = this.slowestRequests;
  }

  /**
   * 日付フォーマットの検出
   */
  private detectDateFormat(dateString: string): string {
    if (/^\d{4}-\d{2}-\d{2}$/.test(dateString)) return "YYYY-MM-DD";
    if (/^\d{8}$/.test(dateString)) return "YYYYMMDD";
    if (/^\d{4}\/\d{2}\/\d{2}$/.test(dateString)) return "YYYY/MM/DD";
    if (/^\d{2}\/\d{2}\/\d{4}$/.test(dateString)) return "MM/DD/YYYY";
    if (/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/.test(dateString)) return "ISO8601";
    return "unknown";
  }

  /**
   * メトリクスの取得
   */
  getMetrics(): LogMetrics {
    return { ...this.metrics };
  }

  /**
   * メトリクスのリセット
   */
  resetMetrics() {
    this.metrics = {
      communication: {
        totalRequests: 0,
        successfulRequests: 0,
        failedRequests: 0,
        timeoutErrors: 0,
        networkErrors: 0,
        httpErrors: {},
      },
      schemaValidation: {
        totalValidations: 0,
        successfulValidations: 0,
        failedValidations: 0,
        validationErrors: {},
      },
      dateConversion: {
        totalConversions: 0,
        successfulConversions: 0,
        failedConversions: 0,
        invalidFormats: {},
      },
      performance: {
        averageResponseTime: 0,
        slowestRequests: [],
        memoryUsage: 0,
      },
    };
    this.startTime = Date.now();
    this.requestTimes.clear();
    this.slowestRequests = [];
  }
}

// シングルトンインスタンス
export const observabilityLogger = new ObservabilityLogger();

// 便利な関数
export const logCommunicationError = (error: Error, context: { url: string; method: string; status?: number }) => {
  observabilityLogger.logCommunicationError(error, context);
};

export const logCommunicationSuccess = (context: { url: string; method: string; duration: number }) => {
  observabilityLogger.logCommunicationSuccess(context);
};

export const logSchemaValidationError = (field: string, value: any, expectedType: string, context?: string) => {
  observabilityLogger.logSchemaValidationError(field, value, expectedType, context);
};

export const logSchemaValidationSuccess = (field: string, context?: string) => {
  observabilityLogger.logSchemaValidationSuccess(field, context);
};

export const logDateConversionError = (dateString: string, error: Error, context?: string) => {
  observabilityLogger.logDateConversionError(dateString, error, context);
};

export const logDateConversionSuccess = (dateString: string, result: string, context?: string) => {
  observabilityLogger.logDateConversionSuccess(dateString, result, context);
};

export const logPerformanceMetrics = () => {
  observabilityLogger.logPerformanceMetrics();
};

export default observabilityLogger;
