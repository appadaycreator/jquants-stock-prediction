"use client";

import React, { useState } from "react";
import { AlertTriangle, RefreshCw, Home, Wifi, Server, Clock, HelpCircle } from "lucide-react";

interface ErrorInfo {
  type: "network" | "server" | "data" | "timeout" | "unknown";
  message: string;
  description: string;
  action: string;
  icon: React.ReactNode;
  retryable: boolean;
}

const errorTypes: Record<string, ErrorInfo> = {
  network: {
    type: "network",
    message: "通信に失敗しました",
    description: "インターネット接続を確認してください。数分後に再試行してください。",
    action: "再試行",
    icon: <Wifi className="w-8 h-8" />,
    retryable: true,
  },
  server: {
    type: "server",
    message: "サーバーエラーが発生しました",
    description: "サーバーが一時的に利用できません。しばらく待ってから再試行してください。",
    action: "再試行",
    icon: <Server className="w-8 h-8" />,
    retryable: true,
  },
  data: {
    type: "data",
    message: "データの読み込みに失敗しました",
    description: "データファイルが見つからないか、破損している可能性があります。",
    action: "データを再生成",
    icon: <AlertTriangle className="w-8 h-8" />,
    retryable: true,
  },
  timeout: {
    type: "timeout",
    message: "処理がタイムアウトしました",
    description: "処理に時間がかかりすぎています。しばらく待ってから再試行してください。",
    action: "再試行",
    icon: <Clock className="w-8 h-8" />,
    retryable: true,
  },
  unknown: {
    type: "unknown",
    message: "予期しないエラーが発生しました",
    description: "システムに問題が発生しました。しばらく待ってから再試行してください。",
    action: "再試行",
    icon: <AlertTriangle className="w-8 h-8" />,
    retryable: true,
  },
};

interface EnhancedErrorHandlerProps {
  error: Error;
  onRetry: () => void;
  onGoHome: () => void;
  onGetHelp?: () => void;
  showDetails?: boolean;
}

export default function EnhancedErrorHandler({
  error,
  onRetry,
  onGoHome,
  onGetHelp,
  showDetails = false,
}: EnhancedErrorHandlerProps) {
  const [isRetrying, setIsRetrying] = useState(false);
  const [retryCount, setRetryCount] = useState(0);

  // エラータイプを判定
  const getErrorType = (error: Error): string => {
    const message = error.message.toLowerCase();
    
    if (message.includes("network") || message.includes("fetch") || message.includes("connection")) {
      return "network";
    }
    if (message.includes("server") || message.includes("500") || message.includes("502") || message.includes("503")) {
      return "server";
    }
    if (message.includes("data") || message.includes("json") || message.includes("parse")) {
      return "data";
    }
    if (message.includes("timeout") || message.includes("time")) {
      return "timeout";
    }
    return "unknown";
  };

  const errorType = getErrorType(error);
  const errorInfo = errorTypes[errorType];

  const handleRetry = async () => {
    setIsRetrying(true);
    setRetryCount(prev => prev + 1);
    
    try {
      await onRetry();
    } finally {
      setIsRetrying(false);
    }
  };

  const getRetryMessage = () => {
    if (retryCount === 0) return "";
    if (retryCount === 1) return "1回目の再試行中...";
    if (retryCount === 2) return "2回目の再試行中...";
    return `${retryCount}回目の再試行中...`;
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-lg max-w-md w-full p-6">
        {/* エラーアイコン */}
        <div className="text-center mb-6">
          <div className="text-red-500 mb-4 flex justify-center">
            {errorInfo.icon}
          </div>
          <h2 className="text-xl font-bold text-gray-900 mb-2">
            {errorInfo.message}
          </h2>
          <p className="text-gray-600 text-sm leading-relaxed">
            {errorInfo.description}
          </p>
        </div>

        {/* 再試行状況 */}
        {isRetrying && (
          <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center justify-center">
              <RefreshCw className="w-4 h-4 animate-spin text-blue-600 mr-2" />
              <span className="text-blue-700 text-sm">
                {getRetryMessage()}
              </span>
            </div>
          </div>
        )}

        {/* エラー詳細（開発者向け） */}
        {showDetails && (
          <div className="mb-4 p-3 bg-gray-50 border border-gray-200 rounded-lg">
            <details className="text-xs">
              <summary className="cursor-pointer text-gray-600 hover:text-gray-800">
                技術的詳細を表示
              </summary>
              <div className="mt-2 text-gray-500 font-mono">
                <p><strong>エラータイプ:</strong> {errorInfo.type}</p>
                <p><strong>メッセージ:</strong> {error.message}</p>
                <p><strong>スタック:</strong></p>
                <pre className="text-xs overflow-x-auto">
                  {error.stack}
                </pre>
              </div>
            </details>
          </div>
        )}

        {/* アクションボタン */}
        <div className="space-y-3">
          {errorInfo.retryable && (
            <button
              onClick={handleRetry}
              disabled={isRetrying}
              className={`w-full flex items-center justify-center px-4 py-3 rounded-lg font-medium transition-colors ${
                isRetrying
                  ? "bg-gray-400 cursor-not-allowed text-white"
                  : "bg-blue-600 hover:bg-blue-700 text-white"
              }`}
            >
              {isRetrying ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin mr-2" />
                  再試行中...
                </>
              ) : (
                <>
                  <RefreshCw className="w-4 h-4 mr-2" />
                  {errorInfo.action}
                </>
              )}
            </button>
          )}

          <div className="flex space-x-2">
            <button
              onClick={onGoHome}
              className="flex-1 flex items-center justify-center px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <Home className="w-4 h-4 mr-2" />
              ホームに戻る
            </button>
            
            {onGetHelp && (
              <button
                onClick={onGetHelp}
                className="flex-1 flex items-center justify-center px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <HelpCircle className="w-4 h-4 mr-2" />
                ヘルプ
              </button>
            )}
          </div>
        </div>

        {/* 追加情報 */}
        <div className="mt-4 pt-4 border-t border-gray-200">
          <p className="text-xs text-gray-500 text-center">
            問題が続く場合は、しばらく時間をおいてから再度お試しください。
          </p>
        </div>
      </div>
    </div>
  );
}
