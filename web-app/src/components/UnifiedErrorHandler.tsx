"use client";

import React, { useState, useEffect, useCallback } from "react";
import { getErrorInfo, logError, getLocalizedErrorMessage, type ErrorInfo } from "@/lib/unified-error-handler";

interface UnifiedErrorHandlerProps {
  error: Error;
  onRetry?: () => void;
  onDismiss?: () => void;
  showDetails?: boolean;
  autoRetry?: boolean;
  maxRetries?: number;
}

export default function UnifiedErrorHandler({
  error,
  onRetry,
  onDismiss,
  showDetails = false,
  autoRetry = true,
  maxRetries = 3,
}: UnifiedErrorHandlerProps) {
  const [retryCount, setRetryCount] = useState(0);
  const [isRetrying, setIsRetrying] = useState(false);
  const [errorInfo, setErrorInfo] = useState<ErrorInfo | null>(null);

  useEffect(() => {
    const info = getErrorInfo(error);
    setErrorInfo(info);
    
    // エラーログを記録
    logError(error);
    
    // 自動リトライを無効化してループを防止
    // if (autoRetry && info.autoRetry && retryCount < maxRetries) {
    //   handleAutoRetry();
    // }
  }, [error, autoRetry, maxRetries, retryCount]);

  const handleAutoRetry = useCallback(() => {
    if (isRetrying || retryCount >= maxRetries || !errorInfo?.autoRetry) return;
    
    setIsRetrying(true);
    setRetryCount(prev => prev + 1);
    
    console.log(`Auto retry attempt ${retryCount + 1}/${maxRetries} for ${errorInfo.category} error`);
    
    const delay = errorInfo.retryDelay || 2000;
    
    setTimeout(() => {
      // キャッシュクリア
      if ("caches" in window) {
        caches.keys().then(names => {
          names.forEach(name => caches.delete(name));
        });
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
        console.warn("Failed to clear localStorage cache:", e);
      }
      
      if (onRetry) {
        onRetry();
      }
      
      setIsRetrying(false);
    }, delay);
  }, [errorInfo, retryCount, maxRetries, isRetrying, onRetry]);

  const handleManualRetry = useCallback(() => {
    if (isRetrying) return;
    
    setIsRetrying(true);
    setRetryCount(prev => prev + 1);
    
    setTimeout(() => {
      if (onRetry) {
        onRetry();
      }
      setIsRetrying(false);
    }, 1000);
  }, [isRetrying, onRetry]);

  if (!errorInfo) {
    return null;
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "low": return "bg-yellow-50 border-yellow-200 text-yellow-800";
      case "medium": return "bg-orange-50 border-orange-200 text-orange-800";
      case "high": return "bg-red-50 border-red-200 text-red-800";
      case "critical": return "bg-red-100 border-red-300 text-red-900";
      default: return "bg-gray-50 border-gray-200 text-gray-800";
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-xl w-full">
        <div className="p-6">
          {/* ヘッダー */}
          <div className="flex items-center space-x-3 mb-4">
            <div className="text-3xl">{errorInfo.icon}</div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                {errorInfo.title}
              </h3>
              <p className="text-sm text-gray-600">
                エラーカテゴリ: {errorInfo.category} | 重要度: {errorInfo.severity}
              </p>
            </div>
          </div>
          
          {/* メッセージ */}
          <div className="mb-4">
            <p className="text-gray-700 mb-2">{errorInfo.message}</p>
            
            {/* 自動リトライ中 */}
            {isRetrying && errorInfo.autoRetry && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                  <span className="text-sm text-blue-800">
                    自動復旧を試行中... ({retryCount}/{maxRetries})
                  </span>
                </div>
              </div>
            )}
            
            {/* ユーザーアクション */}
            {errorInfo.userAction && (
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                <p className="text-sm text-gray-700">
                  <strong>推奨アクション:</strong> {errorInfo.userAction}
                </p>
              </div>
            )}
          </div>
          
          {/* アクションボタン */}
          <div className="flex space-x-3">
            {errorInfo.canRetry && (
              <button
                onClick={handleManualRetry}
                className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                disabled={isRetrying}
              >
                {isRetrying ? "復旧中..." : "手動で再試行"}
              </button>
            )}
            
            <button
              onClick={() => window.location.href = "/"}
              className="flex-1 bg-gray-200 text-gray-800 px-4 py-2 rounded-lg hover:bg-gray-300 transition-colors"
            >
              ホームに戻る
            </button>
            
            {onDismiss && (
              <button
                onClick={onDismiss}
                className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
              >
                閉じる
              </button>
            )}
          </div>
          
          {/* エラー詳細 */}
          {showDetails && (
            <details className="mt-4">
              <summary className="text-sm text-gray-600 cursor-pointer">
                技術詳細を表示
              </summary>
              <div className="mt-2 space-y-2">
                <div className="bg-gray-100 p-3 rounded text-xs">
                  <p><strong>エラーメッセージ:</strong> {error.message}</p>
                  {errorInfo.technicalDetails && (
                    <p><strong>詳細:</strong> {errorInfo.technicalDetails}</p>
                  )}
                </div>
                
                {error.stack && (
                  <div className="bg-gray-100 p-3 rounded text-xs">
                    <p><strong>スタックトレース:</strong></p>
                    <pre className="mt-1 overflow-auto max-h-32">
                      {error.stack}
                    </pre>
                  </div>
                )}
              </div>
            </details>
          )}
          
          {/* 最大リトライ数に達した場合 */}
          {retryCount >= maxRetries && (
            <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
              <p className="text-sm text-yellow-800">
                自動復旧に失敗しました。手動で再試行するか、ホームに戻ってください。
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
