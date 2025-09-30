"use client";

import React, { useCallback, useMemo, useState } from "react";
import { ErrorBoundary as ReactErrorBoundary } from "react-error-boundary";
import EnhancedErrorHandler from "@/components/EnhancedErrorHandler";

type UnifiedApiError = {
  error_code: string;
  user_message: string;
  retry_hint?: string;
};

type AppErrorLike = Error & { code?: string; status?: number; retryHint?: string };

function isUnifiedApiErrorPayload(value: any): value is UnifiedApiError {
  return (
    value &&
    typeof value === "object" &&
    typeof value.error_code === "string" &&
    typeof value.user_message === "string"
  );
}

function FallbackUI({ error, resetErrorBoundary }: { error: Error; resetErrorBoundary: () => void }) {
  const [showModal, setShowModal] = useState(true);

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

  const Toast = (
    <div className="fixed bottom-4 left-1/2 -translate-x-1/2 z-50">
      <div className="bg-red-600 text-white px-4 py-3 rounded shadow-lg max-w-md">
        <div className="font-semibold">重大エラー</div>
        <div className="text-sm opacity-90 truncate">{message}</div>
      </div>
    </div>
  );

  return (
    <>
      {Toast}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-xl w-full">
            <EnhancedErrorHandler
              error={error as AppErrorLike}
              onRetry={onRetry}
              onGoHome={() => (window.location.href = "/")}
              showDetails={process.env.NODE_ENV === "development"}
            />
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


