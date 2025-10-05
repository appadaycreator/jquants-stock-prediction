"use client";

import React, { Component, ErrorInfo, ReactNode } from "react";
import { AlertTriangle, RefreshCw, Settings, Database, Wifi, WifiOff } from "lucide-react";

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  errorType: ErrorType;
  retryCount: number;
  lastRetryTime: number | null;
}

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  maxRetries?: number;
  retryDelay?: number;
}

type ErrorType = 
  | "AUTH_ERROR"      // 401/403 認証エラー
  | "RATE_LIMIT"      // 429 レート制限
  | "SERVER_ERROR"    // 5xx サーバーエラー
  | "NETWORK_ERROR"   // ネットワークエラー
  | "SCHEMA_ERROR"    // スキーマ不一致
  | "UNKNOWN_ERROR";  // その他

interface ErrorDetails {
  type: ErrorType;
  message: string;
  userMessage: string;
  action: string;
  icon: ReactNode;
  canRetry: boolean;
  canUseSample: boolean;
  canGoToSettings: boolean;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  private retryTimeoutId: NodeJS.Timeout | null = null;

  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorType: "UNKNOWN_ERROR",
      retryCount: 0,
      lastRetryTime: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    const errorType = ErrorBoundary.categorizeError(error);
    return {
      hasError: true,
      error,
      errorType,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({
      error,
      errorInfo,
    });

    // エラーログの出力
    console.error("ErrorBoundary caught an error:", error, errorInfo);
    
    // 親コンポーネントにエラーを通知
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  componentWillUnmount() {
    if (this.retryTimeoutId) {
      clearTimeout(this.retryTimeoutId);
    }
  }

  private static categorizeError(error: Error): ErrorType {
    const message = error.message.toLowerCase();
    
    if (message.includes("401") || message.includes("403") || message.includes("unauthorized")) {
      return "AUTH_ERROR";
    }
    if (message.includes("429") || message.includes("rate limit")) {
      return "RATE_LIMIT";
    }
    if (message.includes("5") || message.includes("server error")) {
      return "SERVER_ERROR";
    }
    if (message.includes("network") || message.includes("fetch") || message.includes("timeout")) {
      return "NETWORK_ERROR";
    }
    if (message.includes("schema") || message.includes("validation")) {
      return "SCHEMA_ERROR";
    }
    
    return "UNKNOWN_ERROR";
  }

  private getErrorDetails(): ErrorDetails {
    const { errorType } = this.state;
    
    switch (errorType) {
      case "AUTH_ERROR":
        return {
          type: "AUTH_ERROR",
          message: "認証に失敗しました",
          userMessage: "ログイン情報が無効または期限切れです",
          action: "設定画面で認証情報を確認してください",
          icon: <Settings className="w-8 h-8 text-red-500" />,
          canRetry: true,
          canUseSample: true,
          canGoToSettings: true,
        };
      
      case "RATE_LIMIT":
        return {
          type: "RATE_LIMIT",
          message: "API呼び出し制限に達しました",
          userMessage: "しばらく待ってから再試行してください",
          action: "数分後に自動的に再試行します",
          icon: <RefreshCw className="w-8 h-8 text-yellow-500" />,
          canRetry: true,
          canUseSample: true,
          canGoToSettings: false,
        };
      
      case "SERVER_ERROR":
        return {
          type: "SERVER_ERROR",
          message: "サーバーエラーが発生しました",
          userMessage: "サーバー側で問題が発生しています",
          action: "しばらく待ってから再試行してください",
          icon: <AlertTriangle className="w-8 h-8 text-red-500" />,
          canRetry: true,
          canUseSample: true,
          canGoToSettings: false,
        };
      
      case "NETWORK_ERROR":
        return {
          type: "NETWORK_ERROR",
          message: "ネットワーク接続エラー",
          userMessage: "インターネット接続を確認してください",
          action: "接続が回復すると自動的に再試行します",
          icon: <WifiOff className="w-8 h-8 text-orange-500" />,
          canRetry: true,
          canUseSample: true,
          canGoToSettings: false,
        };
      
      case "SCHEMA_ERROR":
        return {
          type: "SCHEMA_ERROR",
          message: "データ形式エラー",
          userMessage: "受信したデータの形式が正しくありません",
          action: "サンプルデータに切り替えます",
          icon: <Database className="w-8 h-8 text-blue-500" />,
          canRetry: false,
          canUseSample: true,
          canGoToSettings: false,
        };
      
      default:
        return {
          type: "UNKNOWN_ERROR",
          message: "予期しないエラーが発生しました",
          userMessage: "システムで予期しない問題が発生しました",
          action: "ページを再読み込みしてください",
          icon: <AlertTriangle className="w-8 h-8 text-gray-500" />,
          canRetry: true,
          canUseSample: true,
          canGoToSettings: false,
        };
    }
  }

  private handleRetry = () => {
    const { maxRetries = 3, retryDelay = 1000 } = this.props;
    const { retryCount } = this.state;
    
    if (retryCount >= maxRetries) {
      console.warn("最大再試行回数に達しました");
      return;
    }

    // 指数バックオフで再試行
    const delay = retryDelay * Math.pow(2, retryCount);
    
    this.retryTimeoutId = setTimeout(() => {
      this.setState(prevState => ({
        hasError: false,
        error: null,
        errorInfo: null,
        retryCount: prevState.retryCount + 1,
        lastRetryTime: Date.now(),
      }));
    }, delay);
  };

  private handleUseSample = () => {
    // サンプルデータに切り替える処理
    console.log("サンプルデータに切り替え");
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  private handleGoToSettings = () => {
    // 設定画面に遷移
    window.location.href = "/settings/auth";
  };

  private handleReload = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      const errorDetails = this.getErrorDetails();
      const { retryCount, lastRetryTime } = this.state;
      const { maxRetries = 3 } = this.props;

      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
          <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6">
            <div className="text-center">
              {errorDetails.icon}
              <h2 className="mt-4 text-xl font-semibold text-gray-900">
                {errorDetails.message}
              </h2>
              <p className="mt-2 text-gray-600">
                {errorDetails.userMessage}
              </p>
              <p className="mt-1 text-sm text-gray-500">
                {errorDetails.action}
              </p>
            </div>

            <div className="mt-6 space-y-3">
              {errorDetails.canRetry && retryCount < maxRetries && (
                <button
                  onClick={this.handleRetry}
                  className="w-full flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  再試行 ({retryCount + 1}/{maxRetries})
                </button>
              )}

              {errorDetails.canUseSample && (
                <button
                  onClick={this.handleUseSample}
                  className="w-full flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  <Database className="w-4 h-4 mr-2" />
                  サンプルデータを使用
                </button>
              )}

              {errorDetails.canGoToSettings && (
                <button
                  onClick={this.handleGoToSettings}
                  className="w-full flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  <Settings className="w-4 h-4 mr-2" />
                  設定画面へ
                </button>
              )}

              <button
                onClick={this.handleReload}
                className="w-full flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                ページを再読み込み
              </button>
            </div>

            {retryCount > 0 && (
              <div className="mt-4 text-xs text-gray-500 text-center">
                再試行回数: {retryCount}/{maxRetries}
                {lastRetryTime && (
                  <div>
                    最終再試行: {new Date(lastRetryTime).toLocaleTimeString()}
                  </div>
                )}
              </div>
            )}

            {process.env.NODE_ENV === "development" && this.state.error && (
              <details className="mt-4">
                <summary className="text-sm text-gray-500 cursor-pointer">
                  技術詳細 (開発モード)
                </summary>
                <pre className="mt-2 text-xs text-gray-400 bg-gray-100 p-2 rounded overflow-auto">
                  {this.state.error.stack}
                </pre>
              </details>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
