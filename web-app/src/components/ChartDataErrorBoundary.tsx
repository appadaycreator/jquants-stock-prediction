"use client";

import React, { Component, ErrorInfo, ReactNode } from "react";

interface ChartDataErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
}

interface ChartDataErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  retryCount: number;
}

class ChartDataErrorBoundary extends Component<ChartDataErrorBoundaryProps, ChartDataErrorBoundaryState> {
  private retryTimeout: NodeJS.Timeout | null = null;

  constructor(props: ChartDataErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      retryCount: 0,
    };
  }

  static getDerivedStateFromError(error: Error): ChartDataErrorBoundaryState {
    return {
      hasError: true,
      error,
      retryCount: 0,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("ChartDataErrorBoundary caught an error:", error, errorInfo);
    
    // 無限ループエラーの場合は即座にリセット
    if (error.message.includes("Maximum update depth exceeded")) {
      console.warn("Infinite loop detected in ChartDataContext, forcing reset");
      this.forceReset();
    }
  }

  componentDidUpdate(prevProps: ChartDataErrorBoundaryProps, prevState: ChartDataErrorBoundaryState) {
    // エラーが解決された場合は状態をリセット
    if (prevState.hasError && !this.state.hasError) {
      this.setState({ retryCount: 0 });
    }
  }

  componentWillUnmount() {
    if (this.retryTimeout) {
      clearTimeout(this.retryTimeout);
    }
  }

  forceReset = () => {
    this.setState({
      hasError: false,
      error: null,
      retryCount: 0,
    });
  };

  handleRetry = () => {
    if (this.state.retryCount >= 3) {
      // 3回リトライした場合はページをリロード
      window.location.reload();
      return;
    }

    this.setState(prevState => ({
      hasError: false,
      error: null,
      retryCount: prevState.retryCount + 1,
    }));
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="flex flex-col items-center justify-center p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <div className="text-yellow-800 text-center">
            <h3 className="text-lg font-semibold mb-2">チャートデータの読み込みエラー</h3>
            <p className="text-sm mb-4">
              チャートデータの読み込み中にエラーが発生しました。
              {this.state.retryCount < 3 ? (
                <span>再試行しますか？</span>
              ) : (
                <span>複数回の再試行に失敗しました。ページをリロードします。</span>
              )}
            </p>
            <div className="flex space-x-2">
              {this.state.retryCount < 3 ? (
                <button
                  onClick={this.handleRetry}
                  className="px-4 py-2 bg-yellow-600 text-white rounded-md hover:bg-yellow-700 transition-colors"
                >
                  再試行 ({this.state.retryCount}/3)
                </button>
              ) : (
                <button
                  onClick={() => window.location.reload()}
                  className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
                >
                  ページをリロード
                </button>
              )}
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ChartDataErrorBoundary;
