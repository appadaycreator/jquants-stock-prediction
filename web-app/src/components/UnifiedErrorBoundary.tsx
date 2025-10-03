/**
 * 統一エラーバウンダリ
 * 全エラーを一元管理し、適切なUIを表示
 */

import React, { Component, ErrorInfo, ReactNode } from "react";
import { errorHandler, ErrorInfo as ErrorInfoType } from "../lib/error-handler";
import { 
  AlertTriangle, 
  RefreshCw, 
  Home, 
  HelpCircle, 
  X,
  Wifi,
  Database,
  Settings,
} from "lucide-react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfoType | null;
  isRecovering: boolean;
  retryCount: number;
}

class UnifiedErrorBoundary extends Component<Props, State> {
  private maxRetries = 3;

  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      isRecovering: false,
      retryCount: 0,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("統一エラーバウンダリ:", error, errorInfo);
    
    // エラーの処理
    errorHandler.handleError(error).then((recovered) => {
      if (recovered) {
        this.setState({
          hasError: false,
          error: null,
          errorInfo: null,
          isRecovering: false,
        });
      } else {
        const errorInfoType = errorHandler.categorizeError(error);
        this.setState({
          errorInfo: errorInfoType,
          isRecovering: false,
        });
      }
    });

    // 親コンポーネントへの通知
    this.props.onError?.(error, errorInfo);
  }

  handleRetry = async () => {
    if (this.state.retryCount >= this.maxRetries) {
      return;
    }

    this.setState({ isRecovering: true, retryCount: this.state.retryCount + 1 });

    try {
      // キャッシュのクリア
      if ("caches" in window) {
        const cacheNames = await caches.keys();
        await Promise.all(cacheNames.map(name => caches.delete(name)));
      }

      // ローカルストレージのキャッシュクリア
      try {
        const keys = Object.keys(localStorage);
        keys.forEach(key => {
          if (key.startsWith("app_cache:") || key.startsWith("next:")) {
            localStorage.removeItem(key);
          }
        });
      } catch (e) {
        console.warn("ローカルストレージのクリアに失敗:", e);
      }

      // 状態のリセット
      this.setState({
        hasError: false,
        error: null,
        errorInfo: null,
        isRecovering: false,
      });

    } catch (error) {
      console.error("リトライエラー:", error);
      this.setState({ isRecovering: false });
    }
  };

  handleGoHome = () => {
    if (typeof window !== "undefined") {
      window.location.href = "/";
    }
  };

  handleRefresh = () => {
    if (typeof window !== "undefined") {
      window.location.reload();
    }
  };

  handleDismiss = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: 0,
    });
  };

  getErrorIcon = () => {
    if (!this.state.errorInfo) return <AlertTriangle className="h-8 w-8 text-red-500" />;
    
    switch (this.state.errorInfo.category) {
      case "network":
        return <Wifi className="h-8 w-8 text-orange-500" />;
      case "api":
        return <Database className="h-8 w-8 text-blue-500" />;
      case "system":
        return <Settings className="h-8 w-8 text-purple-500" />;
      default:
        return <AlertTriangle className="h-8 w-8 text-red-500" />;
    }
  };

  getErrorColor = () => {
    if (!this.state.errorInfo) return "text-red-600";
    
    switch (this.state.errorInfo.severity) {
      case "low":
        return "text-yellow-600";
      case "medium":
        return "text-orange-600";
      case "high":
        return "text-red-600";
      case "critical":
        return "text-red-600";
      default:
        return "text-red-600";
    }
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      const { errorInfo, isRecovering, retryCount } = this.state;
      const canRetry = retryCount < this.maxRetries;

      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
          <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6">
            <div className="text-center">
              <div className="flex justify-center mb-4">
                {this.getErrorIcon()}
              </div>
              
              <h1 className="text-xl font-semibold text-gray-900 mb-2">
                エラーが発生しました
              </h1>
              
              <p className={`text-sm mb-4 ${this.getErrorColor()}`}>
                {errorInfo?.userMessage || "予期しないエラーが発生しました"}
              </p>

              {errorInfo && (
                <div className="bg-gray-50 rounded-lg p-3 mb-4">
                  <div className="text-xs text-gray-600 space-y-1">
                    <div>カテゴリ: {errorInfo.category}</div>
                    <div>重要度: {errorInfo.severity}</div>
                    <div>時刻: {new Date(errorInfo.timestamp).toLocaleString("ja-JP")}</div>
                  </div>
                </div>
              )}

              <div className="space-y-3">
                {canRetry && (
                  <button
                    onClick={this.handleRetry}
                    disabled={isRecovering}
                    className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <RefreshCw className={`h-4 w-4 ${isRecovering ? "animate-spin" : ""}`} />
                    <span>
                      {isRecovering ? "復旧中..." : "再試行"}
                    </span>
                  </button>
                )}

                <div className="grid grid-cols-2 gap-2">
                  <button
                    onClick={this.handleGoHome}
                    className="flex items-center justify-center space-x-2 px-3 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
                  >
                    <Home className="h-4 w-4" />
                    <span>ホーム</span>
                  </button>
                  
                  <button
                    onClick={this.handleRefresh}
                    className="flex items-center justify-center space-x-2 px-3 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
                  >
                    <RefreshCw className="h-4 w-4" />
                    <span>再読み込み</span>
                  </button>
                </div>

                <button
                  onClick={this.handleDismiss}
                  className="w-full flex items-center justify-center space-x-2 px-3 py-2 text-gray-500 hover:text-gray-700"
                >
                  <X className="h-4 w-4" />
                  <span>エラーを無視</span>
                </button>
              </div>

              {retryCount > 0 && (
                <div className="mt-4 text-xs text-gray-500">
                  再試行回数: {retryCount}/{this.maxRetries}
                </div>
              )}
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default UnifiedErrorBoundary;
