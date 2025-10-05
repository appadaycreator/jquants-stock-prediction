"use client";

import React, { useState, useEffect } from "react";
import { AlertTriangle, RefreshCw, Home, Bug, Wifi, WifiOff } from "lucide-react";

interface UnifiedErrorHandlerProps {
  error: string | null;
  isLoading: boolean;
  onRetry: () => void;
  onReload?: () => void;
  onGoHome?: () => void;
  maxRetries?: number;
  retryDelay?: number;
  showNetworkStatus?: boolean;
  children?: React.ReactNode;
}

export default function UnifiedErrorHandler({
  error,
  isLoading,
  onRetry,
  onReload,
  onGoHome,
  maxRetries = 3,
  retryDelay = 1000,
  showNetworkStatus = true,
  children,
}: UnifiedErrorHandlerProps) {
  const [retryCount, setRetryCount] = useState(0);
  const [isOnline, setIsOnline] = useState(true);
  const [isRetrying, setIsRetrying] = useState(false);

  // ネットワーク状態の監視
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);

    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, []);

  const handleRetry = async () => {
    if (retryCount >= maxRetries) {
      return;
    }

    setIsRetrying(true);
    setRetryCount(prev => prev + 1);
    
    // リトライ前に少し待機
    await new Promise(resolve => setTimeout(resolve, retryDelay));
    
    try {
      await onRetry();
    } finally {
      setIsRetrying(false);
    }
  };

  const handleReload = () => {
    if (onReload) {
      onReload();
    } else {
      window.location.reload();
    }
  };

  const handleGoHome = () => {
    if (onGoHome) {
      onGoHome();
    } else {
      window.location.href = "/";
    }
  };

  // ローディング状態
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">読み込み中...</p>
        </div>
      </div>
    );
  }

  // エラーがない場合は子コンポーネントを表示
  if (!error) {
    return <>{children}</>;
  }

  // ネットワークエラーの場合
  if (!isOnline) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <WifiOff className="h-12 w-12 text-red-500 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-red-800 mb-2">ネットワーク接続エラー</h3>
        <p className="text-red-600 mb-4">
          インターネット接続を確認してください。
        </p>
        <button
          onClick={handleReload}
          className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition-colors"
        >
          再読み込み
        </button>
      </div>
    );
  }

  // 最大リトライ回数に達した場合
  if (retryCount >= maxRetries) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-red-800 mb-2">データの読み込みに失敗しました</h3>
        <p className="text-red-600 mb-4">
          {error} ({retryCount}/{maxRetries}回試行済み)
        </p>
        <div className="space-y-2">
          <button
            onClick={handleReload}
            className="w-full bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition-colors"
          >
            ページを再読み込み
          </button>
          <button
            onClick={handleGoHome}
            className="w-full bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700 transition-colors flex items-center justify-center"
          >
            <Home className="h-4 w-4 mr-2" />
            ホームに戻る
          </button>
        </div>
      </div>
    );
  }

  // リトライ可能なエラーの場合
  return (
    <div className="bg-orange-50 border border-orange-200 rounded-lg p-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <AlertTriangle className="h-5 w-5 text-orange-600 mr-2" />
          <div>
            <h3 className="text-sm font-semibold text-orange-800">データ取得エラー</h3>
            <p className="text-sm text-orange-700">
              {error} ({retryCount}/{maxRetries}回試行中)
            </p>
          </div>
        </div>
        <button
          onClick={handleRetry}
          disabled={isRetrying}
          className="bg-orange-600 text-white px-3 py-1 rounded text-sm hover:bg-orange-700 transition-colors flex items-center disabled:opacity-50"
        >
          {isRetrying ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-1"></div>
              再試行中...
            </>
          ) : (
            <>
              <RefreshCw className="h-4 w-4 mr-1" />
              再試行
            </>
          )}
        </button>
      </div>
      
      {/* ネットワーク状態表示 */}
      {showNetworkStatus && (
        <div className="mt-3 pt-3 border-t border-orange-200">
          <div className="flex items-center text-xs text-orange-600">
            {isOnline ? (
              <>
                <Wifi className="h-3 w-3 mr-1" />
                ネットワーク接続: 正常
              </>
            ) : (
              <>
                <WifiOff className="h-3 w-3 mr-1" />
                ネットワーク接続: オフライン
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
