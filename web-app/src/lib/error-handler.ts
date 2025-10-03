/**
 * 統一エラーハンドラー（リファクタリング版）
 * 全エラーを一元管理し、適切な対応を実行
 */

export interface ErrorInfo {
  category: "network" | "api" | "data" | "validation" | "system" | "unknown";
  severity: "low" | "medium" | "high" | "critical";
  message: string;
  userMessage: string;
  autoRetry: boolean;
  retryDelay: number;
  fallbackAction: string;
  timestamp: string;
  context?: Record<string, any>;
}

export interface ErrorContext {
  operation: string;
  component: string;
  userId?: string;
  sessionId?: string;
}

class ErrorHandler {
  private errorHistory: ErrorInfo[] = [];
  private isRecovering = false;
  private errorCounts: Map<string, number> = new Map();
  private lastErrorTime: Map<string, number> = new Map();
  private maxErrorsPerMinute = 10;

  /**
   * エラーの分類
   */
  categorizeError(error: Error): ErrorInfo {
    const errorMessage = error.message.toLowerCase();
    
    // ネットワークエラー
    if (errorMessage.includes('network') || errorMessage.includes('fetch') || 
        errorMessage.includes('timeout') || errorMessage.includes('connection')) {
      return {
        category: "network",
        severity: "medium",
        message: error.message,
        userMessage: "ネットワーク接続に問題があります。しばらく待ってから再試行してください。",
        autoRetry: true,
        retryDelay: 3000,
        fallbackAction: "refresh",
        timestamp: new Date().toISOString(),
      };
    }

    // APIエラー
    if (errorMessage.includes('api') || errorMessage.includes('http') || 
        errorMessage.includes('status')) {
      return {
        category: "api",
        severity: "high",
        message: error.message,
        userMessage: "API接続に問題があります。管理者にお問い合わせください。",
        autoRetry: false,
        retryDelay: 0,
        fallbackAction: "none",
        timestamp: new Date().toISOString(),
      };
    }

    // データエラー
    if (errorMessage.includes('data') || errorMessage.includes('parse') || 
        errorMessage.includes('json')) {
      return {
        category: "data",
        severity: "medium",
        message: error.message,
        userMessage: "データの処理中にエラーが発生しました。",
        autoRetry: true,
        retryDelay: 1000,
        fallbackAction: "clear-cache",
        timestamp: new Date().toISOString(),
      };
    }

    // バリデーションエラー
    if (errorMessage.includes('validation') || errorMessage.includes('invalid') || 
        errorMessage.includes('required')) {
      return {
        category: "validation",
        severity: "low",
        message: error.message,
        userMessage: "入力データに問題があります。",
        autoRetry: false,
        retryDelay: 0,
        fallbackAction: "none",
        timestamp: new Date().toISOString(),
      };
    }

    // システムエラー
    if (errorMessage.includes('system') || errorMessage.includes('internal')) {
      return {
        category: "system",
        severity: "critical",
        message: error.message,
        userMessage: "システムエラーが発生しました。管理者にお問い合わせください。",
        autoRetry: false,
        retryDelay: 0,
        fallbackAction: "redirect",
        timestamp: new Date().toISOString(),
      };
    }

    // デフォルト
    return {
      category: "unknown",
      severity: "medium",
      message: error.message,
      userMessage: "予期しないエラーが発生しました。",
      autoRetry: false,
      retryDelay: 0,
      fallbackAction: "none",
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * エラーの処理
   */
  async handleError(error: Error, context?: ErrorContext): Promise<boolean> {
    const errorInfo = this.categorizeError(error);
    this.errorHistory.push(errorInfo);

    // エラーの重複チェック
    const errorKey = context ? `${context.operation}_${context.component}_${error.message}` : error.message;
    const now = Date.now();
    const lastTime = this.lastErrorTime.get(errorKey) || 0;
    const errorCount = this.errorCounts.get(errorKey) || 0;

    // 1分以内に同じエラーが10回以上発生した場合はログを制限
    if (now - lastTime < 60000 && errorCount >= this.maxErrorsPerMinute) {
      return false;
    }

    // エラーカウントを更新
    this.errorCounts.set(errorKey, errorCount + 1);
    this.lastErrorTime.set(errorKey, now);

    console.error("エラーハンドラー:", errorInfo);

    // 復旧処理
    if (this.isRecovering) {
      console.log("既に復旧処理中です");
      return false;
    }

    this.isRecovering = true;

    try {
      // 自動リトライ
      if (errorInfo.autoRetry) {
        await this.retryOperation(errorInfo);
      }

      // フォールバックアクション
      await this.executeFallbackAction(errorInfo);
      
      this.isRecovering = false;
      return true;
    } catch (recoveryError) {
      console.error("復旧処理エラー:", recoveryError);
      this.isRecovering = false;
      return false;
    }
  }

  private async retryOperation(errorInfo: ErrorInfo): Promise<void> {
    if (errorInfo.retryDelay > 0) {
      await new Promise(resolve => setTimeout(resolve, errorInfo.retryDelay));
    }
  }

  private async executeFallbackAction(errorInfo: ErrorInfo): Promise<void> {
    switch (errorInfo.fallbackAction) {
      case "refresh":
        if (typeof window !== 'undefined') {
          window.location.reload();
        }
        break;
      case "clear-cache":
        if (typeof window !== 'undefined') {
          localStorage.clear();
          sessionStorage.clear();
        }
        break;
      case "redirect":
        if (typeof window !== 'undefined') {
          window.location.href = '/error';
        }
        break;
      default:
        // 何もしない
        break;
    }
  }

  getErrorHistory(): ErrorInfo[] {
    return [...this.errorHistory];
  }

  getErrorStats(): { total: number; byCategory: Record<string, number>; bySeverity: Record<string, number> } {
    const byCategory: Record<string, number> = {};
    const bySeverity: Record<string, number> = {};

    this.errorHistory.forEach(error => {
      byCategory[error.category] = (byCategory[error.category] || 0) + 1;
      bySeverity[error.severity] = (bySeverity[error.severity] || 0) + 1;
    });

    return {
      total: this.errorHistory.length,
      byCategory,
      bySeverity,
    };
  }

  reset(): void {
    this.errorHistory = [];
    this.errorCounts.clear();
    this.lastErrorTime.clear();
    this.isRecovering = false;
  }
}

// シングルトンインスタンス
export const errorHandler = new ErrorHandler();

// エラーログの記録
export function logError(error: Error, context?: Record<string, any>): void {
  const errorInfo = errorHandler.categorizeError(error);
  const timestamp = new Date().toISOString();

  const logEntry = {
    timestamp,
    category: errorInfo.category,
    severity: errorInfo.severity,
    message: error.message,
    stack: error.stack,
    context,
    userAgent: typeof navigator !== "undefined" ? navigator.userAgent : "unknown",
    url: typeof window !== "undefined" ? window.location.href : "unknown",
  };

  // コンソールにログ出力
  console.error("Error:", logEntry);

  // ローカルストレージにエラーログを保存（最新10件）
  try {
    if (typeof window !== 'undefined') {
      const existingLogs = JSON.parse(localStorage.getItem("error_logs") || "[]");
      const newLogs = [logEntry, ...existingLogs].slice(0, 10);
      localStorage.setItem("error_logs", JSON.stringify(newLogs));
    }
  } catch (e) {
    console.warn("Failed to save error log:", e);
  }
}

// エラーメッセージの国際化
export function getLocalizedErrorMessage(error: Error, locale: string = "ja"): string {
  const errorInfo = errorHandler.categorizeError(error);
  return errorInfo.userMessage;
}

// エラー情報の取得
export function getErrorInfo(error: Error): ErrorInfo {
  return errorHandler.categorizeError(error);
}

// 最適化されたエラーハンドラー
export const optimizedErrorHandler = {
  handle: (error: Error, context?: ErrorContext) => errorHandler.handleError(error, context),
  categorize: (error: Error) => errorHandler.categorizeError(error),
  getHistory: () => errorHandler.getErrorHistory(),
  getStats: () => errorHandler.getErrorStats(),
  reset: () => errorHandler.reset(),
};
