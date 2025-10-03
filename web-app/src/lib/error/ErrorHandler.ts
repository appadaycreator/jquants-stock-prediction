'use client';

export interface ErrorContext {
  component: string;
  action: string;
  timestamp: number;
  userId?: string;
  sessionId?: string;
}

export interface UserFriendlyError {
  title: string;
  message: string;
  action: string;
  canRetry: boolean;
  canUseSample: boolean;
  canGoToSettings: boolean;
  severity: 'low' | 'medium' | 'high' | 'critical';
}

export class ErrorHandler {
  private static errorLog: Array<{
    error: Error;
    context: ErrorContext;
    userFriendly: UserFriendlyError;
  }> = [];

  static categorizeError(error: Error, context: ErrorContext): UserFriendlyError {
    const message = error.message.toLowerCase();
    
    // 401/403 認証エラー
    if (message.includes('401') || message.includes('403') || message.includes('unauthorized')) {
      return {
        title: '認証エラー',
        message: 'ログイン情報が無効または期限切れです',
        action: '設定画面で認証情報を確認してください',
        canRetry: true,
        canUseSample: true,
        canGoToSettings: true,
        severity: 'high'
      };
    }

    // 429 レート制限
    if (message.includes('429') || message.includes('rate limit')) {
      return {
        title: 'API制限',
        message: 'API呼び出し制限に達しました',
        action: 'しばらく待ってから再試行してください',
        canRetry: true,
        canUseSample: true,
        canGoToSettings: false,
        severity: 'medium'
      };
    }

    // 5xx サーバーエラー
    if (message.includes('5') || message.includes('server error') || message.includes('internal server')) {
      return {
        title: 'サーバーエラー',
        message: 'サーバー側で問題が発生しています',
        action: 'しばらく待ってから再試行してください',
        canRetry: true,
        canUseSample: true,
        canGoToSettings: false,
        severity: 'high'
      };
    }

    // ネットワークエラー
    if (message.includes('network') || message.includes('fetch') || message.includes('timeout') || message.includes('connection')) {
      return {
        title: 'ネットワークエラー',
        message: 'インターネット接続を確認してください',
        action: '接続が回復すると自動的に再試行します',
        canRetry: true,
        canUseSample: true,
        canGoToSettings: false,
        severity: 'medium'
      };
    }

    // スキーマエラー
    if (message.includes('schema') || message.includes('validation') || message.includes('parse')) {
      return {
        title: 'データ形式エラー',
        message: '受信したデータの形式が正しくありません',
        action: 'サンプルデータに切り替えます',
        canRetry: false,
        canUseSample: true,
        canGoToSettings: false,
        severity: 'medium'
      };
    }

    // その他のエラー
    return {
      title: '予期しないエラー',
      message: 'システムで予期しない問題が発生しました',
      action: 'ページを再読み込みしてください',
      canRetry: true,
      canUseSample: true,
      canGoToSettings: false,
      severity: 'critical'
    };
  }

  static handleError(error: Error, context: ErrorContext): UserFriendlyError {
    const userFriendly = this.categorizeError(error, context);
    
    // エラーログに記録
    this.errorLog.push({
      error,
      context,
      userFriendly
    });

    // 技術ログの出力
    console.error('ErrorHandler:', {
      error: error.message,
      stack: error.stack,
      context,
      userFriendly
    });

    // 重大なエラーの場合は追加の処理
    if (userFriendly.severity === 'critical') {
      // エラー報告の送信（実装例）
      this.reportCriticalError(error, context);
    }

    return userFriendly;
  }

  static getErrorHistory(): Array<{
    error: Error;
    context: ErrorContext;
    userFriendly: UserFriendlyError;
  }> {
    return [...this.errorLog];
  }

  static clearErrorHistory(): void {
    this.errorLog = [];
  }

  static getErrorStats(): {
    total: number;
    bySeverity: Record<string, number>;
    byComponent: Record<string, number>;
    recentErrors: number;
  } {
    const now = Date.now();
    const oneHourAgo = now - (60 * 60 * 1000);
    
    const recentErrors = this.errorLog.filter(
      entry => entry.context.timestamp > oneHourAgo
    ).length;

    const bySeverity = this.errorLog.reduce((acc, entry) => {
      const severity = entry.userFriendly.severity;
      acc[severity] = (acc[severity] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const byComponent = this.errorLog.reduce((acc, entry) => {
      const component = entry.context.component;
      acc[component] = (acc[component] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return {
      total: this.errorLog.length,
      bySeverity,
      byComponent,
      recentErrors
    };
  }

  private static reportCriticalError(error: Error, context: ErrorContext): void {
    // 重大なエラーの報告処理
    // 実際の実装では、エラー報告サービスに送信
    console.error('Critical error reported:', {
      error: error.message,
      context,
      timestamp: new Date().toISOString()
    });
  }

  static createRetryStrategy(
    maxRetries: number = 3,
    baseDelay: number = 1000,
    exponentialBackoff: boolean = true
  ) {
    return {
      maxRetries,
      baseDelay,
      exponentialBackoff,
      getDelay: (attempt: number) => {
        if (exponentialBackoff) {
          return baseDelay * Math.pow(2, attempt);
        }
        return baseDelay;
      }
    };
  }

  static async withRetry<T>(
    operation: () => Promise<T>,
    strategy: ReturnType<typeof ErrorHandler.createRetryStrategy>
  ): Promise<T> {
    let lastError: Error;
    
    for (let attempt = 0; attempt <= strategy.maxRetries; attempt++) {
      try {
        return await operation();
      } catch (error) {
        lastError = error instanceof Error ? error : new Error(String(error));
        
        if (attempt === strategy.maxRetries) {
          throw lastError;
        }
        
        const delay = strategy.getDelay(attempt);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
    
    throw lastError!;
  }
}
