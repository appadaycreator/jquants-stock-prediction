/**
 * 強化されたエラーハンドラー
 * ユーザーフレンドリーなエラーメッセージと復旧機能を提供
 */

interface ErrorContext {
  operation: string;
  component?: string;
  userId?: string;
  timestamp: number;
  userAgent?: string;
  url?: string;
}

interface ErrorRecovery {
  action: string;
  description: string;
  autoRetry?: boolean;
  retryDelay?: number;
  maxRetries?: number;
}

interface ErrorClassification {
  type: "network" | "api" | "validation" | "timeout" | "auth" | "unknown";
  severity: "low" | "medium" | "high" | "critical";
  recoverable: boolean;
  userMessage: string;
  technicalMessage: string;
  recovery?: ErrorRecovery;
}

class EnhancedErrorHandler {
  private errorLog: Array<{ error: Error; context: ErrorContext; classification: ErrorClassification }> = [];
  private retryAttempts: Map<string, number> = new Map();
  private maxRetryAttempts = 3;
  private errorCounts: Map<string, number> = new Map();
  private lastErrorTime: Map<string, number> = new Map();
  private maxErrorsPerMinute = 10; // 1分間に最大10回まで

  /**
   * エラーの分類と処理
   */
  handleError(error: Error, context: ErrorContext): ErrorClassification {
    const classification = this.classifyError(error, context);
    
    // エラーの重複チェック
    const errorKey = `${context.operation}_${context.component}_${error.message}`;
    const now = Date.now();
    const lastTime = this.lastErrorTime.get(errorKey) || 0;
    const errorCount = this.errorCounts.get(errorKey) || 0;
    
    // 1分以内に同じエラーが10回以上発生した場合はログを制限
    if (now - lastTime < 60000 && errorCount >= this.maxErrorsPerMinute) {
      // ログを出力せずに分類のみ返す
      return classification;
    }
    
    // エラーログに記録
    this.errorLog.push({ error, context, classification });
    
    // エラーカウントを更新
    this.errorCounts.set(errorKey, errorCount + 1);
    this.lastErrorTime.set(errorKey, now);
    
    // コンソールにログ出力
    this.logError(error, context, classification);
    
    // ユーザー通知
    this.notifyUser(classification, context);
    
    return classification;
  }

  /**
   * エラーの分類
   */
  private classifyError(error: Error, context: ErrorContext): ErrorClassification {
    const errorMessage = error.message.toLowerCase();
    
    // ネットワークエラー
    if (errorMessage.includes("fetch") || errorMessage.includes("network") || errorMessage.includes("connection")) {
      return {
        type: "network",
        severity: "medium",
        recoverable: true,
        userMessage: "ネットワーク接続に問題があります。しばらく待ってから再試行してください。",
        technicalMessage: `Network error: ${error.message}`,
        recovery: {
          action: "retry",
          description: "自動的に再試行します",
          autoRetry: true,
          retryDelay: 2000,
          maxRetries: 3,
        },
      };
    }

    // APIエラー
    if (errorMessage.includes("api") || errorMessage.includes("http")) {
      const statusMatch = errorMessage.match(/http (\d+)/);
      const status = statusMatch ? parseInt(statusMatch[1]) : 0;
      
      if (status >= 500) {
        return {
          type: "api",
          severity: "high",
          recoverable: true,
          userMessage: "サーバーに一時的な問題が発生しています。しばらく待ってから再試行してください。",
          technicalMessage: `API error: ${error.message}`,
          recovery: {
            action: "retry",
            description: "自動的に再試行します",
            autoRetry: true,
            retryDelay: 5000,
            maxRetries: 2,
          },
        };
      } else if (status === 401 || status === 403) {
        return {
          type: "auth",
          severity: "high",
          recoverable: false,
          userMessage: "認証に問題があります。ログインし直してください。",
          technicalMessage: `Authentication error: ${error.message}`,
        };
      } else if (status === 404) {
        return {
          type: "api",
          severity: "medium",
          recoverable: false,
          userMessage: "要求されたデータが見つかりません。",
          technicalMessage: `Not found: ${error.message}`,
        };
      }
    }

    // タイムアウトエラー
    if (errorMessage.includes("timeout") || errorMessage.includes("abort")) {
      return {
        type: "timeout",
        severity: "medium",
        recoverable: true,
        userMessage: "リクエストがタイムアウトしました。再試行してください。",
        technicalMessage: `Timeout error: ${error.message}`,
        recovery: {
          action: "retry",
          description: "自動的に再試行します",
          autoRetry: true,
          retryDelay: 3000,
          maxRetries: 2,
        },
      };
    }

    // バリデーションエラー
    if (errorMessage.includes("validation") || errorMessage.includes("invalid")) {
      return {
        type: "validation",
        severity: "low",
        recoverable: false,
        userMessage: "入力データに問題があります。入力内容を確認してください。",
        technicalMessage: `Validation error: ${error.message}`,
      };
    }

    // その他のエラー
    return {
      type: "unknown",
      severity: "medium",
      recoverable: true,
      userMessage: "予期しないエラーが発生しました。ページを再読み込みしてください。",
      technicalMessage: `Unknown error: ${error.message}`,
      recovery: {
        action: "reload",
        description: "ページを再読み込みします",
        autoRetry: false,
      },
    };
  }

  /**
   * エラーログの出力
   */
  private logError(error: Error, context: ErrorContext, classification: ErrorClassification): void {
    const errorKey = `${context.operation}_${context.component}_${error.message}`;
    const errorCount = this.errorCounts.get(errorKey) || 0;
    
    // 簡潔なログ出力
    if (errorCount === 1) {
      console.error(`[Error Handler] ${context.operation} in ${context.component}: ${error.message}`);
    } else if (errorCount <= 5) {
      console.warn(`[Error Handler] ${context.operation} in ${context.component}: ${error.message} (${errorCount}回目)`);
    } else if (errorCount === 6) {
      console.warn(`[Error Handler] ${context.operation} in ${context.component}: エラーが頻繁に発生しています。ログを制限します。`);
    }
    
    // 詳細ログは最初の1回のみ
    if (errorCount === 1) {
      const logData = {
        error: {
          name: error.name,
          message: error.message,
          stack: error.stack,
        },
        context,
        classification,
        timestamp: new Date().toISOString(),
      };

      console.error("Enhanced Error Handler:", logData);

      // 本番環境では外部ログサービスに送信
      if (process.env.NODE_ENV === "production") {
        this.sendToLogService(logData);
      }
    }
  }

  /**
   * ユーザー通知
   */
  private notifyUser(classification: ErrorClassification, context: ErrorContext): void {
    // トースト通知の表示
    if (typeof window !== "undefined") {
      this.showToast(classification.userMessage, classification.severity);
    }

    // 重大なエラーの場合はアラート表示
    if (classification.severity === "critical") {
      alert(`重大なエラーが発生しました: ${classification.userMessage}`);
    }
  }

  /**
   * トースト通知の表示
   */
  private showToast(message: string, severity: string): void {
    // 簡易的なトースト実装
    const toast = document.createElement("div");
    toast.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
      severity === "critical" ? "bg-red-500" :
      severity === "high" ? "bg-orange-500" :
      severity === "medium" ? "bg-yellow-500" : "bg-blue-500"
    } text-white`;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
      toast.remove();
    }, 5000);
  }

  /**
   * 自動復旧の実行
   */
  async attemptRecovery(classification: ErrorClassification, context: ErrorContext): Promise<boolean> {
    if (!classification.recovery || !classification.recovery.autoRetry) {
      return false;
    }

    const retryKey = `${context.operation}_${context.component || "unknown"}`;
    const currentAttempts = this.retryAttempts.get(retryKey) || 0;
    
    if (currentAttempts >= (classification.recovery.maxRetries || this.maxRetryAttempts)) {
      console.warn(`最大リトライ回数に達しました: ${retryKey}`);
      return false;
    }

    this.retryAttempts.set(retryKey, currentAttempts + 1);

    // リトライ遅延
    if (classification.recovery?.retryDelay) {
      await new Promise(resolve => setTimeout(resolve, classification.recovery!.retryDelay));
    }

    return true;
  }

  /**
   * エラー統計の取得
   */
  getErrorStats(): {
    totalErrors: number;
    errorsByType: Record<string, number>;
    errorsBySeverity: Record<string, number>;
    recentErrors: Array<{ error: string; timestamp: number; severity: string }>;
  } {
    const errorsByType: Record<string, number> = {};
    const errorsBySeverity: Record<string, number> = {};
    const recentErrors = this.errorLog
      .slice(-10) // 最新10件
      .map(log => ({
        error: log.error.message,
        timestamp: log.context.timestamp,
        severity: log.classification.severity,
      }));

    for (const log of this.errorLog) {
      errorsByType[log.classification.type] = (errorsByType[log.classification.type] || 0) + 1;
      errorsBySeverity[log.classification.severity] = (errorsBySeverity[log.classification.severity] || 0) + 1;
    }

    return {
      totalErrors: this.errorLog.length,
      errorsByType,
      errorsBySeverity,
      recentErrors,
    };
  }

  /**
   * エラーログのクリア
   */
  clearErrorLog(): void {
    this.errorLog = [];
    this.retryAttempts.clear();
  }

  /**
   * ログサービスの送信（本番環境用）
   */
  private sendToLogService(logData: any): void {
    // 実際の実装では、Sentry、LogRocket、DataDogなどのサービスを使用
    console.info("Log service integration:", logData);
  }

  /**
   * リトライカウンターのリセット
   */
  resetRetryCounters(): void {
    this.retryAttempts.clear();
  }

  /**
   * エラーカウンターのリセット
   */
  resetErrorCounters(): void {
    this.errorCounts.clear();
    this.lastErrorTime.clear();
  }

  /**
   * 全カウンターのリセット
   */
  resetAllCounters(): void {
    this.retryAttempts.clear();
    this.errorCounts.clear();
    this.lastErrorTime.clear();
    this.errorLog = [];
  }

  /**
   * デバッグ用：エラーカウンターの状態を取得
   */
  getDebugInfo(): any {
    return {
      errorCounts: Object.fromEntries(this.errorCounts),
      lastErrorTime: Object.fromEntries(this.lastErrorTime),
      retryAttempts: Object.fromEntries(this.retryAttempts),
      totalErrors: this.errorLog.length,
    };
  }
}

// シングルトンインスタンス
const errorHandler = new EnhancedErrorHandler();

export default errorHandler;
export type { ErrorContext, ErrorClassification, ErrorRecovery };
