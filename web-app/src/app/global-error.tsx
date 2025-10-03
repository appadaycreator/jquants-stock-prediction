"use client";

import { useEffect, useState } from "react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  const [retryCount] = useState(0);
  const [isRetrying] = useState(false);
  const [errorType, setErrorType] = useState<"rsc" | "network" | "data" | "unknown">("unknown");

  useEffect(() => {
    // グローバルエラーログをコンソールに出力
    console.error("Global Error:", error);
    
    // エラータイプを判定
    const message = error.message.toLowerCase();
    if (message.includes("rsc payload") || 
        message.includes("connection closed") ||
        message.includes("failed to fetch rsc payload") ||
        message.includes("settings.txt") ||
        message.includes("reports.txt")) {
      setErrorType("rsc");
    } else if (message.includes("network") || 
               message.includes("fetch") || 
               message.includes("connection")) {
      setErrorType("network");
    } else if (message.includes("data") || 
               message.includes("json") || 
               message.includes("parse")) {
      setErrorType("data");
    }
    
    // 自動リトライを無効化してループを防止
    // if (errorType === "rsc" || errorType === "network") {
    //   console.log(`${errorType} error detected, attempting recovery...`);
    //   handleAutoRetry();
    // }
  }, [error, errorType]);


  const getErrorMessage = () => {
    switch (errorType) {
      case "rsc":
        return {
          title: "RSC Payload エラー",
          message: "サーバーコンポーネントの通信エラーが発生しました。自動的に復旧を試みています...",
          icon: "🔄",
        };
      case "network":
        return {
          title: "ネットワークエラー",
          message: "ネットワーク接続に問題があります。自動的に再試行しています...",
          icon: "🌐",
        };
      case "data":
        return {
          title: "データ取得エラー",
          message: "データの取得に失敗しました。キャッシュデータを表示します...",
          icon: "📊",
        };
      default:
        return {
          title: "システムエラー",
          message: "予期しないエラーが発生しました。自動的に復旧を試みています...",
          icon: "⚠️",
        };
    }
  };

  const errorInfo = getErrorMessage();

  return (
    <html>
      <body>
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <div className="text-center">
            <div className="bg-white p-8 rounded-lg shadow-lg max-w-md mx-auto">
              <div className="text-red-500 mb-4">
                <div className="text-6xl mb-2">{errorInfo.icon}</div>
                {isRetrying && (
                  <div className="flex items-center justify-center space-x-2">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-red-500"></div>
                    <span className="text-sm text-gray-600">復旧中... ({retryCount}/3)</span>
                  </div>
                )}
              </div>
              <h2 className="text-xl font-bold text-gray-900 mb-2">
                {errorInfo.title}
              </h2>
              <p className="text-gray-600 mb-4">
                {errorInfo.message}
              </p>
              <div className="space-y-2">
                <button
                  onClick={reset}
                  className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                  disabled={isRetrying}
                >
                  {isRetrying ? "復旧中..." : "手動で再試行"}
                </button>
                <button
                  onClick={() => window.location.href = "/"}
                  className="w-full bg-gray-200 text-gray-800 px-4 py-2 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  ホームに戻る
                </button>
                {retryCount >= 3 && (
                  <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <p className="text-sm text-yellow-800">
                      自動復旧に失敗しました。手動で再試行するか、ホームに戻ってください。
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </body>
    </html>
  );
}
