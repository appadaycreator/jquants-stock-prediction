/**
 * 最適化された統合エラーハンドラー
 * 重複したエラーハンドリング機能を統合し、パフォーマンスを最適化
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
  type: "network" | "api" | "validation" | "timeout" | "auth" | "data" | "system" | "unknown";
  severity: "low" | "medium" | "high" | "critical";
  recoverable: boolean;
  userMessage: string;
  technicalMessage: string;
  recovery?: ErrorRecovery;
}

interface ErrorInfo {
  id: string;
  category: string;
  severity: string;
  message: string;
  stack?: string;
  context?: ErrorContext;
  timestamp: string;
}

interface RecoveryStrategy {
  name: string;
  condition: (error: Error) => boolean;
  action: () => Promise<boolean>;
  priority: number;
  maxAttempts: number;
}

class OptimizedErrorHandler {
  private errorHistory: ErrorInfo[] = [];
  private errorCounts: Map<string, number> = new Map();
  private lastErrorTime: Map<string, number> = new Map();
  private retryAttempts: Map<string, number> = new Map();
  private recoveryStrategies: RecoveryStrategy[] = [];
  private isRecovering = false;
  private maxErrorsPerMinute = 10;
  private maxRetryAttempts = 3;

  constructor() {
    this.initializeRecoveryStrategies();
    this.setupGlobalErrorHandling();
  }

  /**
   * エラーの分類と処理（統合版）
   */
  async handleError(error: Error, context?: ErrorContext): Promise<boolean> {
    const errorInfo = this.categorizeError(error, context);
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

    console.error("統合エラーハンドラー:", errorInfo);

    // 復旧アクションの実行
    if (this.isRecovering) {
      console.log("既に復旧処理中です");
      return false;
    }

    this.isRecovering = true;

    try {
      const recoveryActions = this.recoveryStrategies.filter(strategy => 
        strategy.condition(error)
      );

      for (const strategy of recoveryActions) {
        if (await this.executeRecoveryStrategy(strategy, error)) {
          console.log(`復旧成功: ${strategy.name}`);
          this.isRecovering = false;
          return true;
        }
      }

      // フォールバックアクション
      if (await this.executeFallbackAction(error)) {
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
   * エラーの分類
   */
  private categorizeError(error: Error, context?: ErrorContext): ErrorInfo {
    const errorMessage = error.message.toLowerCase();
    let category = "unknown";
    let severity = "medium";

    // ネットワークエラー
    if (errorMessage.includes("fetch") || errorMessage.includes("network") || errorMessage.includes("connection")) {
      category = "network";
      severity = "medium";
    }
    // APIエラー
    else if (errorMessage.includes("api") || errorMessage.includes("http")) {
      category = "api";
      const statusMatch = errorMessage.match(/http (\d+)/);
      const status = statusMatch ? parseInt(statusMatch[1]) : 0;
      severity = status >= 500 ? "high" : status >= 400 ? "medium" : "low";
    }
    // 認証エラー
    else if (errorMessage.includes("auth") || errorMessage.includes("unauthorized") || errorMessage.includes("forbidden")) {
      category = "auth";
      severity = "high";
    }
    // データエラー
    else if (errorMessage.includes("data") || errorMessage.includes("json") || errorMessage.includes("parse")) {
      category = "data";
      severity = "medium";
    }
    // タイムアウトエラー
    else if (errorMessage.includes("timeout") || errorMessage.includes("abort")) {
      category = "timeout";
      severity = "medium";
    }
    // バリデーションエラー
    else if (errorMessage.includes("validation") || errorMessage.includes("invalid")) {
      category = "validation";
      severity = "low";
    }
    // システムエラー
    else if (errorMessage.includes("rsc payload") || errorMessage.includes("server component")) {
      category = "system";
      severity = "high";
    }

    return {
      id: `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      category,
      severity,
      message: error.message,
      stack: error.stack,
      context,
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * 復旧戦略の初期化
   */
  private initializeRecoveryStrategies(): void {
    // RSC Payload エラーの復旧戦略
    this.recoveryStrategies.push({
      name: "rsc-payload-recovery",
      condition: (error) => {
        const message = error.message.toLowerCase();
        return message.includes("rsc payload") || 
               message.includes("server component") ||
               message.includes("connection closed");
      },
      action: async () => {
        console.log("RSC Payload復旧を実行中...");
        await this.clearCaches();
        return true;
      },
      priority: 1,
      maxAttempts: 1,
    });

    // ネットワークエラーの復旧戦略
    this.recoveryStrategies.push({
      name: "network-recovery",
      condition: (error) => {
        const message = error.message.toLowerCase();
        return message.includes("network") || 
               message.includes("fetch") || 
               message.includes("connection") ||
               message.includes("timeout");
      },
      action: async () => {
        console.log("ネットワーク復旧を実行中...");
        if (!navigator.onLine) {
          await this.waitForOnline();
        }
        await this.clearCaches();
        return true;
      },
      priority: 2,
      maxAttempts: 5,
    });

    // データエラーの復旧戦略
    this.recoveryStrategies.push({
      name: "data-recovery",
      condition: (error) => {
        const message = error.message.toLowerCase();
        return message.includes("data") || 
               message.includes("json") || 
               message.includes("parse");
      },
      action: async () => {
        console.log("データ復旧を実行中...");
        await this.clearLocalStorage();
        await this.restoreDefaultData();
        return true;
      },
      priority: 3,
      maxAttempts: 2,
    });

    // コンポーネントエラーの復旧戦略
    this.recoveryStrategies.push({
      name: "component-recovery",
      condition: (error) => {
        const stack = error.stack?.toLowerCase() || "";
        return stack.includes("react") || 
               stack.includes("component") ||
               error.message.includes("render");
      },
      action: async () => {
        console.log("コンポーネント復旧を実行中...");
        await this.resetComponentState();
        return true;
      },
      priority: 4,
      maxAttempts: 1,
    });
  }

  /**
   * グローバルエラーハンドリングの設定
   */
  private setupGlobalErrorHandling(): void {
    if (typeof window === "undefined") return;

    window.addEventListener("error", (event) => {
      this.handleError(event.error);
    });

    window.addEventListener("unhandledrejection", (event) => {
      this.handleError(event.reason);
    });
  }

  /**
   * 復旧戦略の実行
   */
  private async executeRecoveryStrategy(strategy: RecoveryStrategy, error: Error): Promise<boolean> {
    const retryKey = `${strategy.name}_${error.message}`;
    const currentAttempts = this.retryAttempts.get(retryKey) || 0;
    
    if (currentAttempts >= strategy.maxAttempts) {
      console.warn(`最大リトライ回数に達しました: ${strategy.name}`);
      return false;
    }

    this.retryAttempts.set(retryKey, currentAttempts + 1);

    try {
      return await strategy.action();
    } catch (recoveryError) {
      console.error(`復旧戦略 ${strategy.name} でエラー:`, recoveryError);
      return false;
    }
  }

  /**
   * フォールバックアクションの実行
   */
  private async executeFallbackAction(error: Error): Promise<boolean> {
    try {
      // 基本的な復旧処理
      await this.clearCaches();
      await this.clearLocalStorage();
      return true;
    } catch (fallbackError) {
      console.error("フォールバック復旧エラー:", fallbackError);
      return false;
    }
  }

  /**
   * キャッシュのクリア
   */
  private async clearCaches(): Promise<void> {
    if ("caches" in window) {
      const cacheNames = await caches.keys();
      await Promise.all(
        cacheNames.map(name => caches.delete(name))
      );
    }
  }

  /**
   * ローカルストレージのクリア
   */
  private async clearLocalStorage(): Promise<void> {
    try {
      const keys = Object.keys(localStorage);
      keys.forEach(key => {
        if (key.startsWith("app_cache:") || 
            key.startsWith("next:") || 
            key.startsWith("error_")) {
          localStorage.removeItem(key);
        }
      });
    } catch (e) {
      console.warn("ローカルストレージのクリアに失敗:", e);
    }
  }

  /**
   * デフォルトデータの復元
   */
  private async restoreDefaultData(): Promise<void> {
    try {
      const defaultSettings = {
        theme: "light",
        language: "ja",
        notifications: true,
        autoRefresh: true,
      };
      
      localStorage.setItem("app_settings", JSON.stringify(defaultSettings));
    } catch (e) {
      console.warn("デフォルトデータの復元に失敗:", e);
    }
  }

  /**
   * コンポーネント状態のリセット
   */
  private async resetComponentState(): Promise<void> {
    try {
      const stateKeys = Object.keys(localStorage).filter(key => 
        key.startsWith("component_") || key.startsWith("react_")
      );
      
      stateKeys.forEach(key => {
        localStorage.removeItem(key);
      });
    } catch (e) {
      console.warn("コンポーネント状態のリセットに失敗:", e);
    }
  }

  /**
   * オンライン状態の待機
   */
  private async waitForOnline(): Promise<void> {
    return new Promise((resolve) => {
      if (navigator.onLine) {
        resolve();
        return;
      }
      
      const handleOnline = () => {
        window.removeEventListener("online", handleOnline);
        resolve();
      };
      
      window.addEventListener("online", handleOnline);
    });
  }

  /**
   * エラー統計の取得
   */
  getErrorStats(): {
    totalErrors: number;
    errorsByCategory: Record<string, number>;
    errorsBySeverity: Record<string, number>;
    recentErrors: Array<{ error: string; timestamp: string; severity: string }>;
    recoveryStats: {
      totalRecoveries: number;
      successfulRecoveries: number;
      failedRecoveries: number;
      successRate: number;
    };
  } {
    const errorsByCategory: Record<string, number> = {};
    const errorsBySeverity: Record<string, number> = {};
    const recentErrors = this.errorHistory
      .slice(-10)
      .map(log => ({
        error: log.message,
        timestamp: log.timestamp,
        severity: log.severity,
      }));

    for (const log of this.errorHistory) {
      errorsByCategory[log.category] = (errorsByCategory[log.category] || 0) + 1;
      errorsBySeverity[log.severity] = (errorsBySeverity[log.severity] || 0) + 1;
    }

    const totalRecoveries = Array.from(this.retryAttempts.values()).reduce((sum, count) => sum + count, 0);
    const successfulRecoveries = this.errorHistory.filter(log => log.category !== "unknown").length;
    const failedRecoveries = totalRecoveries - successfulRecoveries;
    const successRate = totalRecoveries > 0 ? (successfulRecoveries / totalRecoveries) * 100 : 0;

    return {
      totalErrors: this.errorHistory.length,
      errorsByCategory,
      errorsBySeverity,
      recentErrors,
      recoveryStats: {
        totalRecoveries,
        successfulRecoveries,
        failedRecoveries,
        successRate,
      },
    };
  }

  /**
   * エラーログのクリア
   */
  clearErrorLog(): void {
    this.errorHistory = [];
    this.retryAttempts.clear();
    this.errorCounts.clear();
    this.lastErrorTime.clear();
  }

  /**
   * ヘルスチェックの実行
   */
  async performHealthCheck(): Promise<{
    isHealthy: boolean;
    issues: string[];
    recommendations: string[];
  }> {
    const issues: string[] = [];
    const recommendations: string[] = [];

    // ネットワーク接続の確認
    if (!navigator.onLine) {
      issues.push("ネットワーク接続がありません");
      recommendations.push("ネットワーク接続を確認してください");
    }

    // ローカルストレージの確認
    try {
      localStorage.setItem("health_check", "test");
      localStorage.removeItem("health_check");
    } catch (e) {
      issues.push("ローカルストレージが利用できません");
      recommendations.push("ブラウザの設定を確認してください");
    }

    // キャッシュの確認
    if ("caches" in window) {
      try {
        const cacheNames = await caches.keys();
        if (cacheNames.length > 10) {
          issues.push("キャッシュが多すぎます");
          recommendations.push("キャッシュをクリアしてください");
        }
      } catch (e) {
        issues.push("キャッシュAPIが利用できません");
      }
    }

    // メモリ使用量の確認
    if ("memory" in performance) {
      const memory = (performance as any).memory;
      const usedMB = memory.usedJSHeapSize / 1024 / 1024;
      if (usedMB > 100) {
        issues.push("メモリ使用量が高いです");
        recommendations.push("ページを再読み込みしてください");
      }
    }

    return {
      isHealthy: issues.length === 0,
      issues,
      recommendations,
    };
  }
}

// シングルトンインスタンス
const optimizedErrorHandler = new OptimizedErrorHandler();

export default optimizedErrorHandler;
export type { ErrorContext, ErrorClassification, ErrorRecovery, ErrorInfo };
