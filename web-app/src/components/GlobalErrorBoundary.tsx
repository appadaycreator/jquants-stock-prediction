"use client";

import React, { useCallback, useMemo, useState, useEffect } from "react";
import { ErrorBoundary as ReactErrorBoundary } from "react-error-boundary";
// EnhancedErrorHandler は削除され、統合エラーハンドラーを使用

type UnifiedApiError = {
  error_code: string;
  user_message: string;
  retry_hint?: string;
};

type AppErrorLike = Error & { code?: string; status?: number; retryHint?: string };

type ErrorCategory = "rsc" | "network" | "data" | "component" | "unknown";

function isUnifiedApiErrorPayload(value: any): value is UnifiedApiError {
  return (
    value &&
    typeof value === "object" &&
    typeof value.error_code === "string" &&
    typeof value.user_message === "string"
  );
}

function categorizeError(error: Error): ErrorCategory {
  const message = error.message.toLowerCase();
  const stack = error.stack?.toLowerCase() || "";
  
  if (message.includes("rsc payload") || 
      message.includes("server component") ||
      message.includes("connection closed")) {
    return "rsc";
  }
  
  if (message.includes("network") || 
      message.includes("fetch") || 
      message.includes("connection") ||
      message.includes("timeout")) {
    return "network";
  }
  
  if (message.includes("data") || 
      message.includes("json") || 
      message.includes("parse") ||
      message.includes("invalid")) {
    return "data";
  }
  
  if (stack.includes("react") || 
      stack.includes("component") ||
      message.includes("render")) {
    return "component";
  }
  
  return "unknown";
}

function FallbackUI({ error, resetErrorBoundary }: { error: Error; resetErrorBoundary: () => void }) {
  const [showModal, setShowModal] = useState(true);
  const [retryCount, setRetryCount] = useState(0);
  const [isAutoRetrying, setIsAutoRetrying] = useState(false);
  const [errorCategory, setErrorCategory] = useState<ErrorCategory>("unknown");

  useEffect(() => {
    const category = categorizeError(error);
    setErrorCategory(category);
    
    // 無限ループエラーの場合は自動リトライを無効化
    if (error.message.includes("Maximum update depth exceeded")) {
      console.warn("Infinite loop detected, disabling auto-retry");
      // 無限ループエラーの場合は即座にページをリロード
      setTimeout(() => {
        window.location.reload();
      }, 1000);
      return;
    }
    
    // 自動リトライを無効化してループを防止
    // if (category === "rsc" || category === "network") {
    //   handleAutoRetry();
    // }
  }, [error]);

  const handleAutoRetry = useCallback(() => {
    if (isAutoRetrying || retryCount >= 3) return;
    
    setIsAutoRetrying(true);
    setRetryCount(prev => prev + 1);
    
    console.log(`Auto retry attempt ${retryCount + 1}/3 for ${errorCategory} error`);
    
    // 指数バックオフでリトライ
    const delay = Math.min(1000 * Math.pow(2, retryCount), 5000);
    
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
      
      // リロードを無効化してループを防止
      // resetErrorBoundary();
      console.log("Recovery completed without reset to prevent loop");
      setIsAutoRetrying(false);
    }, delay);
  }, [errorCategory, retryCount, isAutoRetrying]);

  const message = useMemo(() => {
    try {
      const parsed = JSON.parse(error.message);
      if (isUnifiedApiErrorPayload(parsed)) {
        return parsed.user_message;
      }
    } catch (_) {}
    return error.message || "予期しないエラーが発生しました";
  }, [error]);

  const onRetry = useCallback(async () => {
    // 1クリック再実行: 汎用リトライAPIを呼び出し（冪等性トークン付与）
    const token = `${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
    try {
      await fetch("/api/retry", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Idempotency-Key": token,
        },
        body: JSON.stringify({ reason: "frontend_retry" }),
      });
    } catch (_) {}
    resetErrorBoundary();
  }, [resetErrorBoundary]);

  const getErrorIcon = (category: ErrorCategory) => {
    switch (category) {
      case "rsc": return "🔄";
      case "network": return "🌐";
      case "data": return "📊";
      case "component": return "⚛️";
      default: return "⚠️";
    }
  };

  const getErrorTitle = (category: ErrorCategory) => {
    switch (category) {
      case "rsc": return "RSC Payload エラー";
      case "network": return "ネットワークエラー";
      case "data": return "データ取得エラー";
      case "component": return "コンポーネントエラー";
      default: return "システムエラー";
    }
  };

  const Toast = (
    <div className="fixed bottom-4 left-1/2 -translate-x-1/2 z-50">
      <div className="bg-red-600 text-white px-4 py-3 rounded shadow-lg max-w-md">
        <div className="font-semibold flex items-center space-x-2">
          <span>{getErrorIcon(errorCategory)}</span>
          <span>{getErrorTitle(errorCategory)}</span>
          {isAutoRetrying && (
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
          )}
        </div>
        <div className="text-sm opacity-90 truncate">{message}</div>
        {isAutoRetrying && (
          <div className="text-xs opacity-75 mt-1">
            自動復旧中... ({retryCount}/3)
          </div>
        )}
      </div>
    </div>
  );

  return (
    <>
      {Toast}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-xl w-full">
            <div className="p-6">
              <div className="flex items-center space-x-3 mb-4">
                <div className="text-3xl">{getErrorIcon(errorCategory)}</div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">
                    {getErrorTitle(errorCategory)}
                  </h3>
                  <p className="text-sm text-gray-600">
                    エラーカテゴリ: {errorCategory}
                  </p>
                </div>
              </div>
              
              <div className="mb-4">
                <p className="text-gray-700 mb-2">{message}</p>
                {isAutoRetrying && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                    <div className="flex items-center space-x-2">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                      <span className="text-sm text-blue-800">
                        自動復旧を試行中... ({retryCount}/3)
                      </span>
                    </div>
                  </div>
                )}
              </div>
              
              <div className="flex space-x-3">
                <button
                  onClick={onRetry}
                  className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                  disabled={isAutoRetrying}
                >
                  {isAutoRetrying ? "復旧中..." : "手動で再試行"}
                </button>
                <button
                  onClick={() => (window.location.href = "/")}
                  className="flex-1 bg-gray-200 text-gray-800 px-4 py-2 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  ホームに戻る
                </button>
              </div>
              
              {retryCount >= 3 && (
                <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <p className="text-sm text-yellow-800">
                    自動復旧に失敗しました。手動で再試行するか、ホームに戻ってください。
                  </p>
                </div>
              )}
              
              {process.env.NODE_ENV === "development" && (
                <details className="mt-4">
                  <summary className="text-sm text-gray-600 cursor-pointer">
                    開発者情報を表示
                  </summary>
                  <pre className="mt-2 text-xs bg-gray-100 p-2 rounded overflow-auto">
                    {error.stack}
                  </pre>
                </details>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default function GlobalErrorBoundary({ children }: { children: React.ReactNode }) {
  return (
    <ReactErrorBoundary FallbackComponent={FallbackUI}>
      {children}
    </ReactErrorBoundary>
  );
}


