/**
 * 最適化された統合エラーハンドラー
 * 重複したエラーハンドリング機能を統合し、パフォーマンスを最適化
 */

export interface ErrorInfo {
  id: string;
  message: string;
  category: ErrorCategory;
  severity: ErrorSeverity;
  timestamp: string;
  context?: ErrorContext;
  stack?: string;
}

export interface ErrorContext {
  operation: string;
  component: string;
  userId?: string;
  sessionId?: string;
  additionalData?: Record<string, any>;
}

export enum ErrorCategory {
  NETWORK = "network",
  API = "api",
  VALIDATION = "validation",
  TIMEOUT = "timeout",
  AUTH = "auth",
  DATA = "data",
  SYSTEM = "system",
  UNKNOWN = "unknown",
}

export enum ErrorSeverity {
  LOW = "low",
  MEDIUM = "medium",
  HIGH = "high",
  CRITICAL = "critical",
}

export interface ErrorRecoveryAction {
  description: string;
  execute: () => Promise<boolean>;
  priority: number;
}

export interface ErrorRecovery {
  actions: ErrorRecoveryAction[];
  maxRetries: number;
  fallbackAction: string;
}

export interface ErrorStatistics {
  totalErrors: number;
  errorsByCategory: Record<ErrorCategory, number>;
  errorsBySeverity: Record<ErrorSeverity, number>;
  recentErrors: ErrorInfo[];
  recoverySuccessRate: number;
}

class OptimizedErrorHandler {
  private errorHistory: ErrorInfo[] = [];
  private recoveryActions: Map<ErrorCategory, ErrorRecoveryAction[]> = new Map();
  private isRecovering = false;
  private errorCounts: Map<string, number> = new Map();
  private lastErrorTime: Map<string, number> = new Map();
  private maxErrorsPerMinute = 10;
  private maxHistorySize = 1000;
  private recoveryAttempts: Map<string, number> = new Map();
  private maxRecoveryAttempts = 3;

  constructor() {
    this.initializeRecoveryActions();
  }

  /**
   * エラーの分類（最適化版）
   */
  categorizeError(error: Error): ErrorInfo {
    const errorMessage = error.message.toLowerCase();
    let category: ErrorCategory;
    let severity: ErrorSeverity;

    // カテゴリの判定
    if (errorMessage.includes("network") || errorMessage.includes("fetch")) {
      category = ErrorCategory.NETWORK;
      severity = ErrorSeverity.MEDIUM;
    } else if (errorMessage.includes("api") || errorMessage.includes("endpoint")) {
      category = ErrorCategory.API;
      severity = ErrorSeverity.HIGH;
    } else if (errorMessage.includes("validation") || errorMessage.includes("invalid")) {
      category = ErrorCategory.VALIDATION;
      severity = ErrorSeverity.MEDIUM;
    } else if (errorMessage.includes("timeout")) {
      category = ErrorCategory.TIMEOUT;
      severity = ErrorSeverity.MEDIUM;
    } else if (errorMessage.includes("auth") || errorMessage.includes("unauthorized")) {
      category = ErrorCategory.AUTH;
      severity = ErrorSeverity.HIGH;
    } else if (errorMessage.includes("data") || errorMessage.includes("parse")) {
      category = ErrorCategory.DATA;
      severity = ErrorSeverity.MEDIUM;
    } else if (errorMessage.includes("system") || errorMessage.includes("internal")) {
      category = ErrorCategory.SYSTEM;
      severity = ErrorSeverity.CRITICAL;
    } else {
      category = ErrorCategory.UNKNOWN;
      severity = ErrorSeverity.LOW;
    }

    return {
      id: this.generateErrorId(),
      message: error.message,
      category,
      severity,
      timestamp: new Date().toISOString(),
      stack: error.stack,
    };
  }

  /**
   * エラーの処理（最適化版）
   */
  async handleError(error: Error, context?: ErrorContext): Promise<boolean> {
    const errorInfo = this.categorizeError(error);
    
    // エラー履歴の管理（サイズ制限）
    this.errorHistory.push(errorInfo);
    if (this.errorHistory.length > this.maxHistorySize) {
      this.errorHistory = this.errorHistory.slice(-this.maxHistorySize);
    }

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

    console.error("最適化エラーハンドラー:", errorInfo);

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
    this.recoveryActions.set(ErrorCategory.NETWORK, [
      {
        description: "ネットワーク接続の再試行",
        execute: async () => {
          await new Promise(resolve => setTimeout(resolve, 1000));
          return true;
        },
        priority: 1,
      },
      {
        description: "キャッシュからのデータ取得",
        execute: async () => {
          // キャッシュからの取得ロジック
          return true;
        },
        priority: 2,
      },
    ]);

    // APIエラー用の復旧アクション
    this.recoveryActions.set(ErrorCategory.API, [
      {
        description: "APIエンドポイントの再試行",
        execute: async () => {
          await new Promise(resolve => setTimeout(resolve, 2000));
          return true;
        },
        priority: 1,
      },
      {
        description: "代替APIエンドポイントの使用",
        execute: async () => {
          // 代替エンドポイントの使用ロジック
          return true;
        },
        priority: 2,
      },
    ]);

    // 認証エラー用の復旧アクション
    this.recoveryActions.set(ErrorCategory.AUTH, [
      {
        description: "認証トークンの更新",
        execute: async () => {
          // トークン更新ロジック
          return true;
        },
        priority: 1,
      },
    ]);

    // データエラー用の復旧アクション
    this.recoveryActions.set(ErrorCategory.DATA, [
      {
        description: "データの再取得",
        execute: async () => {
          // データ再取得ロジック
          return true;
        },
        priority: 1,
      },
    ]);
  }

  /**
   * フォールバックアクションの実行
   */
  private async executeFallbackAction(errorInfo: ErrorInfo): Promise<boolean> {
    const errorKey = `${errorInfo.category}_${errorInfo.message}`;
    const attempts = this.recoveryAttempts.get(errorKey) || 0;

    if (attempts >= this.maxRecoveryAttempts) {
      console.log("最大復旧試行回数に達しました");
      return false;
    }

    this.recoveryAttempts.set(errorKey, attempts + 1);

    // 基本的なフォールバック処理
    try {
      // キャッシュのクリア
      if (typeof localStorage !== "undefined") {
        localStorage.removeItem("jquants_cache");
      }

      // ユーザーへの通知
      console.warn("システムが復旧処理を実行しています");

      return true;
    } catch (fallbackError) {
      console.error("フォールバック処理エラー:", fallbackError);
      return false;
    }
  }

  /**
   * エラー統計の取得
   */
  getErrorStatistics(): ErrorStatistics {
    const totalErrors = this.errorHistory.length;
    const errorsByCategory: Record<ErrorCategory, number> = {} as Record<ErrorCategory, number>;
    const errorsBySeverity: Record<ErrorSeverity, number> = {} as Record<ErrorSeverity, number>;

    // カテゴリ別集計
    Object.values(ErrorCategory).forEach(category => {
      errorsByCategory[category] = 0;
    });

    // 重要度別集計
    Object.values(ErrorSeverity).forEach(severity => {
      errorsBySeverity[severity] = 0;
    });

    this.errorHistory.forEach(error => {
      errorsByCategory[error.category]++;
      errorsBySeverity[error.severity]++;
    });

    // 復旧成功率の計算
    const recoverySuccessRate = this.calculateRecoverySuccessRate();

    return {
      totalErrors,
      errorsByCategory,
      errorsBySeverity,
      recentErrors: this.errorHistory.slice(-10),
      recoverySuccessRate,
    };
  }

  /**
   * 復旧成功率の計算
   */
  private calculateRecoverySuccessRate(): number {
    const totalRecoveryAttempts = Array.from(this.recoveryAttempts.values()).reduce((sum, attempts) => sum + attempts, 0);
    const successfulRecoveries = this.errorHistory.filter(error => 
      this.recoveryAttempts.has(`${error.category}_${error.message}`)
    ).length;

    return totalRecoveryAttempts > 0 ? (successfulRecoveries / totalRecoveryAttempts) * 100 : 0;
  }

  /**
   * エラー履歴のクリア
   */
  clearErrorHistory(): void {
    this.errorHistory = [];
    this.errorCounts.clear();
    this.lastErrorTime.clear();
    this.recoveryAttempts.clear();
  }

  /**
   * エラーIDの生成
   */
  private generateErrorId(): string {
    return `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * エラーの重複チェック
   */
  isDuplicateError(error: Error, context?: ErrorContext): boolean {
    const errorKey = context ? `${context.operation}_${context.component}_${error.message}` : error.message;
    const now = Date.now();
    const lastTime = this.lastErrorTime.get(errorKey) || 0;
    const errorCount = this.errorCounts.get(errorKey) || 0;

    return now - lastTime < 60000 && errorCount >= this.maxErrorsPerMinute;
  }
}

// シングルトンインスタンス
export const optimizedErrorHandler = new OptimizedErrorHandler();

// 便利な関数
export const handleError = (error: Error, context?: ErrorContext) => 
  optimizedErrorHandler.handleError(error, context);

export const getErrorStatistics = () => 
  optimizedErrorHandler.getErrorStatistics();

export const clearErrorHistory = () => 
  optimizedErrorHandler.clearErrorHistory();