/**
 * 統一されたエラーハンドリングシステム
 * エラー分類、ユーザーフレンドリーなメッセージ、自動復旧機能
 */

export type ErrorCategory = "rsc" | "network" | "data" | "component" | "auth" | "validation" | "unknown";

export type ErrorSeverity = "low" | "medium" | "high" | "critical";

export interface ErrorInfo {
  category: ErrorCategory;
  severity: ErrorSeverity;
  title: string;
  message: string;
  icon: string;
  canRetry: boolean;
  autoRetry: boolean;
  retryDelay?: number;
  userAction?: string;
  technicalDetails?: string;
}

export interface ErrorLog {
  id: string;
  timestamp: number;
  category: ErrorCategory;
  severity: ErrorSeverity;
  message: string;
  stack?: string;
  context?: Record<string, any>;
}

export class UnifiedError extends Error {
  constructor(
    message: string,
    public category: ErrorCategory,
    public severity: ErrorSeverity = "medium",
    public originalError?: Error,
    public context?: Record<string, any>,
  ) {
    super(message);
    this.name = "UnifiedError";
  }
}

// エラー分類関数
export function categorizeError(error: Error): ErrorCategory {
  const message = error.message.toLowerCase();
  const stack = error.stack?.toLowerCase() || "";
  
  // RSC Payload エラー
  if (message.includes("rsc payload") || 
      message.includes("server component") ||
      message.includes("connection closed") ||
      message.includes("failed to fetch rsc payload")) {
    return "rsc";
  }
  
  // ネットワークエラー
  if (message.includes("network") || 
      message.includes("fetch") || 
      message.includes("connection") ||
      message.includes("timeout") ||
      message.includes("aborted") ||
      message.includes("cors")) {
    return "network";
  }
  
  // データエラー
  if (message.includes("data") || 
      message.includes("json") || 
      message.includes("parse") ||
      message.includes("invalid") ||
      message.includes("malformed")) {
    return "data";
  }
  
  // 認証エラー
  if (message.includes("auth") || 
      message.includes("unauthorized") ||
      message.includes("forbidden") ||
      message.includes("token")) {
    return "auth";
  }
  
  // バリデーションエラー
  if (message.includes("validation") || 
      message.includes("invalid input") ||
      message.includes("required") ||
      message.includes("format")) {
    return "validation";
  }
  
  // コンポーネントエラー
  if (stack.includes("react") || 
      stack.includes("component") ||
      message.includes("render") ||
      message.includes("hook")) {
    return "component";
  }
  
  return "unknown";
}

// エラー情報の取得
export function getErrorInfo(error: Error): ErrorInfo {
  const category = categorizeError(error);
  
  switch (category) {
    case "rsc":
      return {
        category: "rsc",
        severity: "high",
        title: "RSC Payload エラー",
        message: "サーバーコンポーネントの通信エラーが発生しました。自動的に復旧を試みています。",
        icon: "🔄",
        canRetry: true,
        autoRetry: true,
        retryDelay: 2000,
        userAction: "ページを再読み込みしてください",
        technicalDetails: "React Server Componentsの通信に失敗しました",
      };
      
    case "network":
      return {
        category: "network",
        severity: "medium",
        title: "ネットワークエラー",
        message: "ネットワーク接続に問題があります。自動的に再試行しています。",
        icon: "🌐",
        canRetry: true,
        autoRetry: true,
        retryDelay: 1000,
        userAction: "ネットワーク接続を確認してください",
        technicalDetails: "API呼び出しが失敗しました",
      };
      
    case "data":
      return {
        category: "data",
        severity: "medium",
        title: "データ取得エラー",
        message: "データの取得に失敗しました。キャッシュデータを表示します。",
        icon: "📊",
        canRetry: true,
        autoRetry: false,
        userAction: "しばらく待ってから再試行してください",
        technicalDetails: "データの解析または取得に失敗しました",
      };
      
    case "auth":
      return {
        category: "auth",
        severity: "high",
        title: "認証エラー",
        message: "認証に問題があります。ログインし直してください。",
        icon: "🔐",
        canRetry: false,
        autoRetry: false,
        userAction: "ログインし直してください",
        technicalDetails: "認証トークンが無効または期限切れです",
      };
      
    case "validation":
      return {
        category: "validation",
        severity: "low",
        title: "入力エラー",
        message: "入力内容に問題があります。入力内容を確認してください。",
        icon: "⚠️",
        canRetry: false,
        autoRetry: false,
        userAction: "入力内容を確認してください",
        technicalDetails: "入力値の検証に失敗しました",
      };
      
    case "component":
      return {
        category: "component",
        severity: "high",
        title: "コンポーネントエラー",
        message: "画面の表示に問題があります。ページを再読み込みしてください。",
        icon: "⚛️",
        canRetry: true,
        autoRetry: true,
        retryDelay: 3000,
        userAction: "ページを再読み込みしてください",
        technicalDetails: "Reactコンポーネントのレンダリングに失敗しました",
      };
      
    default:
      return {
        category: "unknown",
        severity: "medium",
        title: "システムエラー",
        message: "予期しないエラーが発生しました。自動的に復旧を試みています。",
        icon: "⚠️",
        canRetry: true,
        autoRetry: true,
        retryDelay: 2000,
        userAction: "ページを再読み込みしてください",
        technicalDetails: "不明なエラーが発生しました",
      };
  }
}

// エラーログの記録
export function logError(error: Error, context?: Record<string, any>) {
  const errorInfo = getErrorInfo(error);
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
    // 必要に応じて外部エラー追跡サービスに送信
    console.error("Critical error detected:", logEntry);
  }
}

// エラーメッセージの国際化
export function getLocalizedErrorMessage(error: Error, locale: string = "ja"): string {
  const errorInfo = getErrorInfo(error);
  
  if (locale === "en") {
    switch (errorInfo.category) {
      case "rsc":
        return "Server component communication error occurred. Attempting automatic recovery.";
      case "network":
        return "Network connection issue. Automatically retrying.";
      case "data":
        return "Data retrieval failed. Displaying cached data.";
      case "auth":
        return "Authentication issue. Please log in again.";
      case "validation":
        return "Input validation error. Please check your input.";
      case "component":
        return "Component rendering error. Please reload the page.";
      default:
        return "Unexpected error occurred. Attempting automatic recovery.";
    }
  }
  
  return errorInfo.message;
}

// エラー統計の取得
export function getErrorStats(): {
  totalErrors: number;
  errorsByCategory: Record<ErrorCategory, number>;
  errorsBySeverity: Record<ErrorSeverity, number>;
  recentErrors: any[];
} {
  try {
    const logs = JSON.parse(localStorage.getItem("error_logs") || "[]");
    
    const stats = {
      totalErrors: logs.length,
      errorsByCategory: {} as Record<ErrorCategory, number>,
      errorsBySeverity: {} as Record<ErrorSeverity, number>,
      recentErrors: logs.slice(0, 5),
    };
    
    logs.forEach((log: ErrorLog) => {
      stats.errorsByCategory[log.category] = (stats.errorsByCategory[log.category] || 0) + 1;
      stats.errorsBySeverity[log.severity] = (stats.errorsBySeverity[log.severity] || 0) + 1;
    });
    
    return stats;
  } catch {
    return {
      totalErrors: 0,
      errorsByCategory: {} as Record<ErrorCategory, number>,
      errorsBySeverity: {} as Record<ErrorSeverity, number>,
      recentErrors: [],
    };
  }
}
