"use client";

import { useState, useEffect } from "react";
import { RefreshCw, Wifi, WifiOff, AlertTriangle, CheckCircle, ExternalLink } from "lucide-react";

interface ErrorGuidanceProps {
  error: string;
  errorCode?: string;
  onRetry?: () => void;
  onClearError?: () => void;
  isUsingFallback?: boolean;
  analysisRequired?: boolean;
}

export default function ErrorGuidance({
  error,
  errorCode,
  onRetry,
  onClearError,
  isUsingFallback = false,
  analysisRequired = false,
}: ErrorGuidanceProps) {
  const [networkStatus, setNetworkStatus] = useState<"online" | "offline" | "unknown">("unknown");
  const [isRetrying, setIsRetrying] = useState(false);

  useEffect(() => {
    const updateNetworkStatus = () => {
      setNetworkStatus(navigator.onLine ? "online" : "offline");
    };

    updateNetworkStatus();
    window.addEventListener("online", updateNetworkStatus);
    window.addEventListener("offline", updateNetworkStatus);

    return () => {
      window.removeEventListener("online", updateNetworkStatus);
      window.removeEventListener("offline", updateNetworkStatus);
    };
  }, []);

  const handleRetry = async () => {
    if (onRetry) {
      setIsRetrying(true);
      try {
        await onRetry();
      } finally {
        setIsRetrying(false);
      }
    }
  };

  const getErrorIcon = () => {
    if (analysisRequired) return <AlertTriangle className="h-5 w-5" />;
    if (networkStatus === "offline") return <WifiOff className="h-5 w-5" />;
    if (isUsingFallback) return <CheckCircle className="h-5 w-5" />;
    return <AlertTriangle className="h-5 w-5" />;
  };

  const getErrorColor = () => {
    if (analysisRequired) return "bg-blue-50 border-blue-200 text-blue-800";
    if (isUsingFallback) return "bg-yellow-50 border-yellow-200 text-yellow-800";
    return "bg-red-50 border-red-200 text-red-800";
  };

  const getRetryHint = () => {
    if (analysisRequired) {
      return "最新の投資判断を行うために、まず分析を実行してください。";
    }
    if (networkStatus === "offline") {
      return "インターネット接続を確認してください。";
    }
    if (errorCode === "API_ERROR") {
      return "サーバーに一時的な問題が発生している可能性があります。";
    }
    if (errorCode === "NETWORK_ERROR") {
      return "ネットワーク接続を確認してください。";
    }
    return "しばらく時間をおいてから再度お試しください。";
  };

  const getActionButtons = () => {
    if (analysisRequired) {
      return (
        <div className="flex gap-2 mt-3">
          <button
            onClick={() => window.location.href = "/"}
            className="bg-blue-600 text-white px-3 py-2 rounded text-sm hover:bg-blue-700 flex items-center gap-1"
            aria-label="分析実行ページへ移動"
            data-help="ダッシュボードに移動して分析を実行します。機械学習モデルによる株価予測分析を開始し、最新の投資判断情報を取得できます。分析完了後に推奨アクションと信頼度が表示されます。"
          >
            <ExternalLink className="h-4 w-4" />
            分析実行へ
          </button>
          <button
            onClick={() => window.location.href = "/reports"}
            className="bg-gray-600 text-white px-3 py-2 rounded text-sm hover:bg-gray-700 flex items-center gap-1"
            aria-label="過去の分析結果を確認"
            data-help="過去の分析結果とレポートを確認します。以前の予測結果、精度評価、パフォーマンス指標を参照できます。過去の分析結果から学び、投資戦略の改善に役立てることができます。"
          >
            過去の結果を確認
          </button>
        </div>
      );
    }

    if (isUsingFallback) {
      return (
        <div className="flex gap-2 mt-3">
          <button
            onClick={handleRetry}
            disabled={isRetrying}
            className="bg-blue-600 text-white px-3 py-2 rounded text-sm hover:bg-blue-700 disabled:opacity-50 flex items-center gap-1"
          >
            <RefreshCw className={`h-4 w-4 ${isRetrying ? "animate-spin" : ""}`} />
            {isRetrying ? "再試行中..." : "最新データを取得"}
          </button>
          {onClearError && (
            <button
              onClick={onClearError}
              className="bg-gray-600 text-white px-3 py-2 rounded text-sm hover:bg-gray-700"
            >
              前回の結果を表示
            </button>
          )}
        </div>
      );
    }

    return (
      <div className="flex gap-2 mt-3">
        <button
          onClick={handleRetry}
          disabled={isRetrying}
          className="bg-blue-600 text-white px-3 py-2 rounded text-sm hover:bg-blue-700 disabled:opacity-50 flex items-center gap-1"
        >
          <RefreshCw className={`h-4 w-4 ${isRetrying ? "animate-spin" : ""}`} />
          {isRetrying ? "再試行中..." : "再試行"}
        </button>
        {networkStatus === "offline" && (
          <button
            onClick={() => window.location.reload()}
            className="bg-gray-600 text-white px-3 py-2 rounded text-sm hover:bg-gray-700 flex items-center gap-1"
          >
            <Wifi className="h-4 w-4" />
            ページを再読み込み
          </button>
        )}
      </div>
    );
  };

  return (
    <div className={`border rounded-lg p-4 ${getErrorColor()}`}>
      <div className="flex items-start gap-3">
        {getErrorIcon()}
        <div className="flex-1">
          <div className="font-medium mb-1">
            {analysisRequired ? "分析が必要です" : isUsingFallback ? "フォールバック表示中" : "エラーが発生しました"}
          </div>
          <div className="text-sm mb-2">{error}</div>
          <div className="text-xs opacity-75">{getRetryHint()}</div>
          
          {/* ネットワーク状態表示 */}
          {networkStatus === "offline" && (
            <div className="mt-2 text-xs flex items-center gap-1">
              <WifiOff className="h-3 w-3" />
              オフライン状態です
            </div>
          )}
          
          {/* アクションボタン */}
          {getActionButtons()}
        </div>
      </div>
    </div>
  );
}
