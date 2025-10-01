/**
 * エラーバウンダリコンポーネント
 * 予測結果タブの致命的エラーを捕捉
 */

import React, { Component, ErrorInfo, ReactNode } from "react";
import { logger, collectErrorInfo } from "@/lib/logger";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({
      error,
      errorInfo,
    });

    // エラー情報をログに記録
    const errorDetails = collectErrorInfo(error, "ErrorBoundary");
    logger.error("ErrorBoundary caught an error:", errorDetails);
    logger.error("Component stack:", errorInfo.componentStack);

    // 親コンポーネントにエラーを通知
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  handleRetry = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
          <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center mb-4">
              <div className="flex-shrink-0">
                <svg className="h-8 w-8 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-lg font-medium text-gray-900">
                  予期しないエラーが発生しました
                </h3>
              </div>
            </div>
            
            <div className="mt-4">
              <p className="text-sm text-gray-600 mb-4">
                申し訳ございません。予測結果の表示中にエラーが発生しました。
              </p>
              
              {process.env.NODE_ENV === "development" && this.state.error && (
                <details className="mb-4">
                  <summary className="text-sm text-gray-500 cursor-pointer">
                    エラー詳細（開発モード）
                  </summary>
                  <pre className="mt-2 text-xs text-red-600 bg-red-50 p-2 rounded overflow-auto">
                    {this.state.error.message}
                    {this.state.errorInfo?.componentStack}
                  </pre>
                </details>
              )}
              
              <div className="flex space-x-3">
                <button
                  onClick={this.handleRetry}
                  className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  再試行
                </button>
                <button
                  onClick={() => window.location.reload()}
                  className="flex-1 bg-gray-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500"
                >
                  ページを再読み込み
                </button>
              </div>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
