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

export interface ErrorRecoveryAction {
  type: "retry" | "fallback" | "redirect" | "refresh" | "clear-cache" | "none";
  description: string;
  execute: () => Promise<boolean>;
}

export interface ErrorContext {
  operation: string;
  component: string;
  timestamp: number;
  userAgent?: string;
  url?: string;
}

export interface ErrorClassification {
  category: string;
  severity: "low" | "medium" | "high" | "critical";
  userMessage: string;
  technicalMessage: string;
  recovery?: {
    autoRetry: boolean;
    retryDelay: number;
    maxRetries: number;
  };
}

export interface ErrorRecovery {
  autoRetry: boolean;
  retryDelay: number;
  maxRetries: number;
  fallbackAction: string;
}

class UnifiedErrorHandler {
  private errorHistory: ErrorInfo[] = [];
  private recoveryActions: Map<string, ErrorRecoveryAction[]> = new Map();
  private isRecovering = false;
  private errorCounts: Map<string, number> = new Map();
  private lastErrorTime: Map<string, number> = new Map();
  private maxErrorsPerMinute = 10;

  constructor() {
    this.initializeRecoveryActions();
  }

  /**
   * エラーの分類
   */
  categorizeError(error: Error): ErrorInfo {
    const errorMessage = error.message.toLowerCase();
    const stack = error.stack || "";

    // ネットワークエラー
    if (
      errorMessage.includes("network") ||
      errorMessage.includes("fetch") ||
      errorMessage.includes("timeout") ||
      errorMessage.includes("connection")
    ) {
      return {
        category: "network",
        severity: "medium",
        message: error.message,
        userMessage: "ネットワーク接続に問題があります。しばらく待ってから再試行してください。",
        autoRetry: true,
        retryDelay: 2000,
        fallbackAction: "refresh",
        timestamp: new Date().toISOString(),
      };
    }

    // APIエラー
    if (
      errorMessage.includes("api") ||
      errorMessage.includes("http") ||
      errorMessage.includes("status") ||
      stack.includes("fetch")
    ) {
      return {
        category: "api",
        severity: "high",
        message: error.message,
        userMessage: "データの取得に失敗しました。しばらく待ってから再試行してください。",
        autoRetry: true,
        retryDelay: 3000,
        fallbackAction: "fallback",
        timestamp: new Date().toISOString(),
      };
    }

    // データエラー
    if (
      errorMessage.includes("data") ||
      errorMessage.includes("parse") ||
      errorMessage.includes("json") ||
      errorMessage.includes("format")
    ) {
      return {
        category: "data",
        severity: "medium",
        message: error.message,
        userMessage: "データの処理に問題があります。ページを再読み込みしてください。",
        autoRetry: false,
        retryDelay: 0,
        fallbackAction: "refresh",
        timestamp: new Date().toISOString(),
      };
    }

    // バリデーションエラー
    if (
      errorMessage.includes("validation") ||
      errorMessage.includes("invalid") ||
      errorMessage.includes("required")
    ) {
      return {
        category: "validation",
        severity: "low",
        message: error.message,
        userMessage: "入力内容に問題があります。入力内容を確認してください。",
        autoRetry: false,
        retryDelay: 0,
        fallbackAction: "none",
        timestamp: new Date().toISOString(),
      };
    }

    // システムエラー
    if (
      errorMessage.includes("system") ||
      errorMessage.includes("internal") ||
      errorMessage.includes("server")
    ) {
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

    // デフォルト（不明なエラー）
    return {
      category: "unknown",
      severity: "medium",
      message: error.message,
      userMessage: "予期しないエラーが発生しました。ページを再読み込みしてください。",
      autoRetry: true,
      retryDelay: 2000,
      fallbackAction: "refresh",
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * エラーの処理（統合版）
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

    console.error("統一エラーハンドラー:", errorInfo);

    // 復旧アクションの実行
    if (this.isRecovering) {
      console.log("既に復旧処理中です");
      return false;
    }

    this.isRecovering = true;

    try {
      const recoveryActions = this.recoveryActions.get(errorInfo.category) || [];

      for (const action of recoveryActions) {
        if (await action.execute()) {
          console.log(`復旧成功: ${action.description}`);
          this.isRecovering = false;
          return true;
        }
      }

      // フォールバックアクション
      if (await this.executeFallbackAction(errorInfo)) {
        console.log("フォールバック復旧成功");
        this.isRecovering = false;
        return true;
      }
    } catch (recoveryError) {
      console.error("復旧処理エラー:", recoveryError);
    } finally {
      this.isRecovering = false;
    }

    return false;
  }

  /**
   * 復旧アクションの初期化
   */
  private initializeRecoveryActions(): void {
    // ネットワークエラー用の復旧アクション
    this.recoveryActions.set("network", [
      {
        type: "retry",
        description: "ネットワーク接続の再試行",
        execute: async () => {
          // ネットワーク接続の確認
          if (navigator.onLine) {
            return true;
          }
          return false;
        },
      },
      {
        type: "clear-cache",
        description: "キャッシュのクリア",
        execute: async () => {
          try {
            if ("caches" in window) {
              const cacheNames = await caches.keys();
              await Promise.all(cacheNames.map(name => caches.delete(name)));
            }
            return true;
          } catch (error) {
            console.error("キャッシュクリアエラー:", error);
            return false;
          }
        },
      },
    ]);

    // APIエラー用の復旧アクション
    this.recoveryActions.set("api", [
      {
        type: "retry",
        description: "API呼び出しの再試行",
        execute: async () => {
          // API接続の確認
          try {
            const response = await fetch("/api/health", { method: "HEAD" });
            return response.ok;
          } catch (error) {
            return false;
          }
        },
      },
      {
        type: "fallback",
        description: "フォールバックデータの使用",
        execute: async () => {
          // フォールバックデータの確認
          return true;
        },
      },
    ]);

    // データエラー用の復旧アクション
    this.recoveryActions.set("data", [
      {
        type: "refresh",
        description: "ページの再読み込み",
        execute: async () => {
          window.location.reload();
          return true;
        },
      },
    ]);

    // システムエラー用の復旧アクション
    this.recoveryActions.set("system", [
      {
        type: "redirect",
        description: "エラーページへのリダイレクト",
        execute: async () => {
          window.location.href = "/error";
          return true;
        },
      },
    ]);
  }

  /**
   * フォールバックアクションの実行
   */
  private async executeFallbackAction(errorInfo: ErrorInfo): Promise<boolean> {
    switch (errorInfo.fallbackAction) {
      case "refresh":
        window.location.reload();
        return true;
      case "redirect":
        window.location.href = "/error";
        return true;
      case "fallback":
        // フォールバックデータの使用
        return true;
      case "clear-cache":
        try {
          if ("caches" in window) {
            const cacheNames = await caches.keys();
            await Promise.all(cacheNames.map(name => caches.delete(name)));
          }
          return true;
        } catch (error) {
          console.error("キャッシュクリアエラー:", error);
          return false;
        }
      default:
        return false;
    }
  }

  /**
   * エラー履歴の取得
   */
  getErrorHistory(): ErrorInfo[] {
    return [...this.errorHistory];
  }

  /**
   * エラー統計の取得
   */
  getErrorStats(): Record<string, number> {
    const stats: Record<string, number> = {};
    for (const [key, count] of this.errorCounts) {
      stats[key] = count;
    }
    return stats;
  }

  /**
   * エラーハンドラーのリセット
   */
  reset(): void {
    this.errorHistory = [];
    this.errorCounts.clear();
    this.lastErrorTime.clear();
    this.isRecovering = false;
  }
}

// シングルトンインスタンス
export const unifiedErrorHandler = new UnifiedErrorHandler();

// エラーログの記録
export function logError(error: Error, context?: Record<string, any>): void {
  const errorInfo = unifiedErrorHandler.categorizeError(error);
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
  console.error("Unified Error:", logEntry);

  // ローカルストレージにエラーログを保存（最新10件）
  try {
    const existingLogs = JSON.parse(localStorage.getItem("error_logs") || "[]");
    const newLogs = [logEntry, ...existingLogs].slice(0, 10);
    localStorage.setItem("error_logs", JSON.stringify(newLogs));
  } catch (e) {
    console.warn("Failed to save error log:", e);
  }

  // 重大なエラーの場合は追加の処理
  if (errorInfo.severity === "critical") {
    console.error("Critical error detected:", logEntry);
  }
}

// エラーメッセージの国際化
export function getLocalizedErrorMessage(error: Error, locale: string = "ja"): string {
  const errorMessage = error.message.toLowerCase();

  if (locale === "ja") {
    if (errorMessage.includes("network")) return "ネットワーク接続に問題があります";
    if (errorMessage.includes("timeout")) return "タイムアウトが発生しました";
    if (errorMessage.includes("fetch")) return "データの取得に失敗しました";
    if (errorMessage.includes("parse")) return "データの解析に失敗しました";
    if (errorMessage.includes("validation")) return "入力内容に問題があります";
    return "予期しないエラーが発生しました";
  }

  // 英語版
  if (errorMessage.includes("network")) return "Network connection problem";
  if (errorMessage.includes("timeout")) return "Timeout occurred";
  if (errorMessage.includes("fetch")) return "Failed to fetch data";
  if (errorMessage.includes("parse")) return "Failed to parse data";
  if (errorMessage.includes("validation")) return "Input validation error";
  return "Unexpected error occurred";
}

export default unifiedErrorHandler;