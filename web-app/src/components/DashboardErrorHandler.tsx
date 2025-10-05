"use client";

import React, { useState, useEffect } from "react";
import { AlertTriangle, RefreshCw, Wifi, WifiOff } from "lucide-react";

interface DashboardErrorHandlerProps {
  error: Error | null;
  onRetry: () => void;
  isOnline: boolean;
  fallbackData?: any;
}

export const DashboardErrorHandler: React.FC<DashboardErrorHandlerProps> = ({
  error,
  onRetry,
  isOnline,
  fallbackData,
}) => {
  const [retryCount, setRetryCount] = useState(0);
  const [isRetrying, setIsRetrying] = useState(false);

  const handleRetry = async () => {
    setIsRetrying(true);
    setRetryCount(prev => prev + 1);
    
    try {
      await onRetry();
    } finally {
      setIsRetrying(false);
    }
  };

  const getErrorMessage = () => {
    if (!isOnline) {
      return {
        title: "オフライン状態",
        message: "インターネット接続を確認してください。オフライン時はキャッシュデータを表示します。",
        icon: <WifiOff className="w-6 h-6 text-orange-500" />,
      };
    }

    if (error?.message.includes("Failed to fetch")) {
      return {
        title: "API接続エラー",
        message: "データサーバーに接続できません。しばらく待ってから再試行してください。",
        icon: <Wifi className="w-6 h-6 text-red-500" />,
      };
    }

    if (error?.message.includes("timeout")) {
      return {
        title: "タイムアウトエラー",
        message: "データの取得に時間がかかりすぎています。再試行してください。",
        icon: <AlertTriangle className="w-6 h-6 text-yellow-500" />,
      };
    }

    return {
      title: "データ読み込みエラー",
      message: error?.message || "不明なエラーが発生しました。",
      icon: <AlertTriangle className="w-6 h-6 text-red-500" />,
    };
  };

  const errorInfo = getErrorMessage();

  if (!error && isOnline) {
    return null;
  }

  return (
    <div className="bg-white border border-red-200 rounded-lg p-6 mb-6">
      <div className="flex items-start space-x-4">
        {errorInfo.icon}
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            {errorInfo.title}
          </h3>
          <p className="text-gray-600 mb-4">
            {errorInfo.message}
          </p>
          
          {fallbackData && (
            <div className="bg-blue-50 border border-blue-200 rounded-md p-3 mb-4">
              <p className="text-sm text-blue-800">
                📊 現在、サンプルデータを表示しています。最新データの取得を試行中...
              </p>
            </div>
          )}

          <div className="flex items-center space-x-4">
            <button
              onClick={handleRetry}
              disabled={isRetrying || retryCount >= 3}
              className={`px-4 py-2 rounded-md font-medium transition-colors ${
                isRetrying || retryCount >= 3
                  ? "bg-gray-300 text-gray-500 cursor-not-allowed"
                  : "bg-blue-600 text-white hover:bg-blue-700"
              }`}
            >
              {isRetrying ? (
                <div className="flex items-center space-x-2">
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>再試行中...</span>
                </div>
              ) : (
                <div className="flex items-center space-x-2">
                  <RefreshCw className="w-4 h-4" />
                  <span>再試行 ({retryCount}/3)</span>
                </div>
              )}
            </button>

            {retryCount >= 3 && (
              <p className="text-sm text-gray-500">
                最大再試行回数に達しました。しばらく時間をおいてから再度お試しください。
              </p>
            )}
          </div>

          {!isOnline && (
            <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
              <p className="text-sm text-yellow-800">
                💡 オフライン時は、最後に取得したデータを表示します。
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DashboardErrorHandler;
