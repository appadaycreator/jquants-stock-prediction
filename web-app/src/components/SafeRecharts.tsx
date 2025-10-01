"use client";

import React, { Component, ErrorInfo, ReactNode } from "react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

class SafeRecharts extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    // createSelectorエラーの場合は特別に処理
    if (error.message.includes("createSelector expects all input-selectors to be functions")) {
      console.warn("Recharts createSelector error caught, this is a known issue with Recharts and Next.js 15");
      return { hasError: true, error };
    }
    
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("SafeRecharts caught an error:", error, errorInfo);
    
    // createSelectorエラーの場合は自動リトライ
    if (error.message.includes("createSelector expects all input-selectors to be functions")) {
      setTimeout(() => {
        this.setState({ hasError: false, error: undefined });
      }, 1000);
    }
  }

  render() {
    if (this.state.hasError) {
      // createSelectorエラーの場合は特別なフォールバック
      if (this.state.error?.message.includes("createSelector expects all input-selectors to be functions")) {
        return (
          <div className="flex items-center justify-center h-64 bg-gray-50 rounded-lg">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
              <p className="text-sm text-gray-600">チャートを読み込み中...</p>
            </div>
          </div>
        );
      }
      
      // その他のエラーの場合はカスタムフォールバックまたはデフォルト
      return this.props.fallback || (
        <div className="flex items-center justify-center h-64 bg-red-50 rounded-lg">
          <div className="text-center">
            <div className="text-red-500 mb-2">⚠️</div>
            <p className="text-sm text-red-600">チャートの読み込みに失敗しました</p>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default SafeRecharts;
