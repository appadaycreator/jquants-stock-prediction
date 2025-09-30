/**
 * 強化されたエラーログシステム
 * 詳細なエラー情報の取得、分析、レポート機能
 */

import { getErrorInfo, type ErrorCategory, type ErrorSeverity } from './error-handler';

export interface ErrorLogEntry {
  id: string;
  timestamp: number;
  category: ErrorCategory;
  severity: ErrorSeverity;
  message: string;
  stack?: string;
  url: string;
  userAgent: string;
  viewport: { width: number; height: number };
  memory?: { used: number; total: number };
  performance?: {
    navigation: PerformanceNavigationTiming | null;
    paint: PerformancePaintTiming | null;
    load: PerformanceEventTiming | null;
  };
  context: {
    component?: string;
    action?: string;
    state?: Record<string, any>;
    props?: Record<string, any>;
  };
  user: {
    sessionId: string;
    userId?: string;
    isFirstVisit: boolean;
  };
  network: {
    online: boolean;
    connectionType?: string;
    effectiveType?: string;
  };
  browser: {
    name: string;
    version: string;
    platform: string;
    language: string;
  };
  environment: {
    nodeEnv: string;
    buildId?: string;
    version?: string;
  };
}

export interface ErrorAnalytics {
  totalErrors: number;
  errorsByCategory: Record<ErrorCategory, number>;
  errorsBySeverity: Record<ErrorSeverity, number>;
  errorsByComponent: Record<string, number>;
  errorsByTime: { hour: number; count: number }[];
  topErrors: { message: string; count: number }[];
  errorTrend: { date: string; count: number }[];
  userImpact: {
    affectedUsers: number;
    errorRate: number;
    recoveryRate: number;
  };
}

class ErrorLogger {
  private logs: ErrorLogEntry[] = [];
  private sessionId: string;
  private userId?: string;
  private isFirstVisit: boolean;

  constructor() {
    this.sessionId = this.generateSessionId();
    this.isFirstVisit = !localStorage.getItem('app_visited');
    
    if (this.isFirstVisit) {
      localStorage.setItem('app_visited', 'true');
    }
    
    this.loadStoredLogs();
    this.setupPerformanceMonitoring();
  }

  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`;
  }

  private loadStoredLogs(): void {
    try {
      const stored = localStorage.getItem('error_logs');
      if (stored) {
        this.logs = JSON.parse(stored);
      }
    } catch (e) {
      console.warn('Failed to load stored error logs:', e);
    }
  }

  private saveLogs(): void {
    try {
      // 最新100件のみ保存
      const recentLogs = this.logs.slice(-100);
      localStorage.setItem('error_logs', JSON.stringify(recentLogs));
    } catch (e) {
      console.warn('Failed to save error logs:', e);
    }
  }

  private setupPerformanceMonitoring(): void {
    // パフォーマンス監視の設定
    if ('performance' in window) {
      // メモリ使用量の監視
      if ('memory' in performance) {
        setInterval(() => {
          const memory = (performance as any).memory;
          if (memory) {
            // メモリ使用量が高い場合の警告
            if (memory.usedJSHeapSize > 100 * 1024 * 1024) { // 100MB
              console.warn('High memory usage detected:', {
                used: memory.usedJSHeapSize,
                total: memory.totalJSHeapSize,
                limit: memory.jsHeapSizeLimit
              });
            }
          }
        }, 30000); // 30秒間隔
      }
    }
  }

  public logError(
    error: Error,
    context: {
      component?: string;
      action?: string;
      state?: Record<string, any>;
      props?: Record<string, any>;
    } = {}
  ): string {
    const errorInfo = getErrorInfo(error);
    const timestamp = Date.now();
    const id = `error_${timestamp}_${Math.random().toString(36).slice(2, 10)}`;

    // パフォーマンス情報の取得
    const performanceInfo = this.getPerformanceInfo();
    
    // ブラウザ情報の取得
    const browserInfo = this.getBrowserInfo();
    
    // ネットワーク情報の取得
    const networkInfo = this.getNetworkInfo();

    const logEntry: ErrorLogEntry = {
      id,
      timestamp,
      category: errorInfo.category,
      severity: errorInfo.severity,
      message: error.message,
      stack: error.stack,
      url: window.location.href,
      userAgent: navigator.userAgent,
      viewport: {
        width: window.innerWidth,
        height: window.innerHeight
      },
      memory: performanceInfo.memory,
      performance: performanceInfo.performance,
      context,
      user: {
        sessionId: this.sessionId,
        userId: this.userId,
        isFirstVisit: this.isFirstVisit
      },
      network: networkInfo,
      browser: browserInfo,
      environment: {
        nodeEnv: process.env.NODE_ENV || 'unknown',
        buildId: process.env.NEXT_PUBLIC_BUILD_ID,
        version: process.env.NEXT_PUBLIC_VERSION
      }
    };

    this.logs.push(logEntry);
    this.saveLogs();

    // コンソールに詳細ログを出力
    console.group(`🚨 Error Logged: ${errorInfo.title}`);
    console.error('Error Details:', {
      id,
      category: errorInfo.category,
      severity: errorInfo.severity,
      message: error.message,
      stack: error.stack,
      context,
      timestamp: new Date(timestamp).toISOString()
    });
    console.error('Environment:', logEntry.environment);
    console.error('Performance:', logEntry.performance);
    console.error('Network:', logEntry.network);
    console.groupEnd();

    // 重大なエラーの場合は追加の処理
    if (errorInfo.severity === 'critical') {
      this.handleCriticalError(logEntry);
    }

    return id;
  }

  private getPerformanceInfo(): {
    memory?: { used: number; total: number };
    performance: {
      navigation: PerformanceNavigationTiming | null;
      paint: PerformancePaintTiming | null;
      load: PerformanceEventTiming | null;
    };
  } {
    const performance: any = {
      navigation: null,
      paint: null,
      load: null
    };

    let memory: { used: number; total: number } | undefined;

    try {
      // ナビゲーション情報
      const navEntries = performance.getEntriesByType('navigation');
      if (navEntries.length > 0) {
        performance.navigation = navEntries[0];
      }

      // ペイント情報
      const paintEntries = performance.getEntriesByType('paint');
      if (paintEntries.length > 0) {
        performance.paint = paintEntries[0];
      }

      // ロード情報
      const loadEntries = performance.getEntriesByType('load');
      if (loadEntries.length > 0) {
        performance.load = loadEntries[0];
      }

      // メモリ情報
      if ('memory' in performance) {
        const mem = (performance as any).memory;
        memory = {
          used: mem.usedJSHeapSize,
          total: mem.totalJSHeapSize
        };
      }
    } catch (e) {
      console.warn('Failed to get performance info:', e);
    }

    return { memory, performance };
  }

  private getBrowserInfo(): {
    name: string;
    version: string;
    platform: string;
    language: string;
  } {
    const ua = navigator.userAgent;
    let name = 'Unknown';
    let version = 'Unknown';

    if (ua.includes('Chrome')) {
      name = 'Chrome';
      const match = ua.match(/Chrome\/(\d+)/);
      if (match) version = match[1];
    } else if (ua.includes('Firefox')) {
      name = 'Firefox';
      const match = ua.match(/Firefox\/(\d+)/);
      if (match) version = match[1];
    } else if (ua.includes('Safari')) {
      name = 'Safari';
      const match = ua.match(/Version\/(\d+)/);
      if (match) version = match[1];
    } else if (ua.includes('Edge')) {
      name = 'Edge';
      const match = ua.match(/Edge\/(\d+)/);
      if (match) version = match[1];
    }

    return {
      name,
      version,
      platform: navigator.platform,
      language: navigator.language
    };
  }

  private getNetworkInfo(): {
    online: boolean;
    connectionType?: string;
    effectiveType?: string;
  } {
    const info: any = {
      online: navigator.onLine
    };

    try {
      // ネットワーク接続情報（対応ブラウザのみ）
      if ('connection' in navigator) {
        const connection = (navigator as any).connection;
        info.connectionType = connection.type;
        info.effectiveType = connection.effectiveType;
      }
    } catch (e) {
      console.warn('Failed to get network info:', e);
    }

    return info;
  }

  private handleCriticalError(logEntry: ErrorLogEntry): void {
    console.error('🚨 Critical error detected:', logEntry);
    
    // 必要に応じて外部エラー追跡サービスに送信
    // 例: Sentry, LogRocket, Bugsnag など
    
    // ユーザーへの通知
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification('システムエラーが発生しました', {
        body: '重大なエラーが検出されました。ページを再読み込みしてください。',
        icon: '/favicon.ico'
      });
    }
  }

  public getAnalytics(): ErrorAnalytics {
    const now = Date.now();
    const oneDayAgo = now - 24 * 60 * 60 * 1000;
    const recentLogs = this.logs.filter(log => log.timestamp > oneDayAgo);

    const errorsByCategory: Record<ErrorCategory, number> = {} as any;
    const errorsBySeverity: Record<ErrorSeverity, number> = {} as any;
    const errorsByComponent: Record<string, number> = {};
    const errorsByTime: { hour: number; count: number }[] = [];
    const errorMessages: Record<string, number> = {};

    // 時間別エラー分布（24時間）
    for (let i = 0; i < 24; i++) {
      errorsByTime.push({ hour: i, count: 0 });
    }

    recentLogs.forEach(log => {
      // カテゴリ別
      errorsByCategory[log.category] = (errorsByCategory[log.category] || 0) + 1;
      
      // 重要度別
      errorsBySeverity[log.severity] = (errorsBySeverity[log.severity] || 0) + 1;
      
      // コンポーネント別
      if (log.context.component) {
        errorsByComponent[log.context.component] = (errorsByComponent[log.context.component] || 0) + 1;
      }
      
      // 時間別
      const hour = new Date(log.timestamp).getHours();
      errorsByTime[hour].count++;
      
      // メッセージ別
      errorMessages[log.message] = (errorMessages[log.message] || 0) + 1;
    });

    // トップエラー
    const topErrors = Object.entries(errorMessages)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 10)
      .map(([message, count]) => ({ message, count }));

    // エラートレンド（過去7日）
    const errorTrend: { date: string; count: number }[] = [];
    for (let i = 6; i >= 0; i--) {
      const date = new Date(now - i * 24 * 60 * 60 * 1000);
      const dateStr = date.toISOString().split('T')[0];
      const dayStart = date.getTime();
      const dayEnd = dayStart + 24 * 60 * 60 * 1000;
      
      const dayErrors = this.logs.filter(log => 
        log.timestamp >= dayStart && log.timestamp < dayEnd
      );
      
      errorTrend.push({ date: dateStr, count: dayErrors.length });
    }

    // ユーザー影響度
    const uniqueUsers = new Set(this.logs.map(log => log.user.sessionId)).size;
    const totalSessions = this.logs.length;
    const errorRate = totalSessions > 0 ? (recentLogs.length / totalSessions) * 100 : 0;
    
    // 復旧率（自動復旧されたエラーの割合）
    const recoveredErrors = this.logs.filter(log => 
      log.severity === 'low' || log.severity === 'medium'
    ).length;
    const recoveryRate = recentLogs.length > 0 ? (recoveredErrors / recentLogs.length) * 100 : 0;

    return {
      totalErrors: recentLogs.length,
      errorsByCategory,
      errorsBySeverity,
      errorsByComponent,
      errorsByTime,
      topErrors,
      errorTrend,
      userImpact: {
        affectedUsers: uniqueUsers,
        errorRate,
        recoveryRate
      }
    };
  }

  public getRecentErrors(limit: number = 10): ErrorLogEntry[] {
    return this.logs
      .sort((a, b) => b.timestamp - a.timestamp)
      .slice(0, limit);
  }

  public clearLogs(): void {
    this.logs = [];
    localStorage.removeItem('error_logs');
  }

  public exportLogs(): string {
    return JSON.stringify(this.logs, null, 2);
  }

  public setUserId(userId: string): void {
    this.userId = userId;
  }
}

// シングルトンインスタンス
export const errorLogger = new ErrorLogger();

// グローバルエラーハンドリングの設定
export function setupGlobalErrorHandling(): void {
  // 未処理のエラー
  window.addEventListener('error', (event) => {
    errorLogger.logError(event.error, {
      component: 'Global',
      action: 'UnhandledError'
    });
  });

  // 未処理のPromise拒否
  window.addEventListener('unhandledrejection', (event) => {
    const error = event.reason instanceof Error 
      ? event.reason 
      : new Error(String(event.reason));
    
    errorLogger.logError(error, {
      component: 'Global',
      action: 'UnhandledRejection'
    });
  });

  // リソース読み込みエラー
  window.addEventListener('error', (event) => {
    if (event.target !== window) {
      const error = new Error(`Resource load error: ${event.target}`);
      errorLogger.logError(error, {
        component: 'Resource',
        action: 'LoadError',
        props: { target: event.target }
      });
    }
  }, true);
}
