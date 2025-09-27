"use client";

import { useEffect } from "react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    // グローバルエラーログをコンソールに出力
    console.error("Global Error:", error);
    
    // RSC payloadエラーの場合、自動的にリトライ
    if (error.message.includes("RSC payload") || error.message.includes("Connection closed")) {
      console.log("RSC payload error detected, attempting recovery...");
      setTimeout(() => {
        window.location.reload();
      }, 2000);
    }
  }, [error]);

  return (
    <html>
      <body>
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <div className="text-center">
            <div className="bg-white p-8 rounded-lg shadow-lg max-w-md mx-auto">
              <div className="text-red-500 mb-4">
                <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 19.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <h2 className="text-xl font-bold text-gray-900 mb-2">
                システムエラーが発生しました
              </h2>
              <p className="text-gray-600 mb-4">
                予期しないエラーが発生しました。自動的に復旧を試みています...
              </p>
              <div className="space-y-2">
                <button
                  onClick={reset}
                  className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  手動で再試行
                </button>
                <button
                  onClick={() => window.location.href = "/"}
                  className="w-full bg-gray-200 text-gray-800 px-4 py-2 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  ホームに戻る
                </button>
              </div>
            </div>
          </div>
        </div>
      </body>
    </html>
  );
}
