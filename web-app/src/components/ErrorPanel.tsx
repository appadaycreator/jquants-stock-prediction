/**
 * エラーパネルコンポーネント
 * ネットワーク異常やスキーマ不整合を可視化
 */

import React from "react";
import { AppError } from "@/lib/fetcher";

interface ErrorPanelProps {
  error: AppError | Error;
  onRetry?: () => void;
  onDismiss?: () => void;
}

export default function ErrorPanel({ error, onRetry, onDismiss }: ErrorPanelProps) {
  const getErrorMessage = (error: AppError | Error): string => {
    if (error instanceof AppError) {
      switch (error.code) {
        case "HTTP_404":
          return "データファイルが見つかりません。管理者にお問い合わせください。";
        case "HTTP_500":
          return "サーバーエラーが発生しました。しばらく待ってから再試行してください。";
        case "HTTP_429":
          return "リクエストが多すぎます。しばらく待ってから再試行してください。";
        case "TIMEOUT":
          return "通信がタイムアウトしました。ネットワーク接続を確認してください。";
        case "ABORTED":
          return "リクエストが中断されました。";
        case "INVALID_CONTENT_TYPE":
          return "データ形式が不正です。JSONファイルが期待されています。";
        case "INVALID_DATA_STRUCTURE":
          return "データ構造が不正です。フィールド名や型を確認してください。";
        case "ALL_RETRIES_FAILED":
          return "すべてのリトライ試行が失敗しました。ネットワーク接続を確認してください。";
        default:
          return `エラー: ${error.message}`;
      }
    }
    
    if (error.message.includes("Failed to fetch")) {
      return "ネットワーク接続に問題があります。インターネット接続を確認してください。";
    }
    
    if (error.message.includes("RSC payload")) {
      return "サーバーとの通信に問題があります。しばらく待ってから再試行してください。";
    }
    
    return `エラー: ${error.message}`;
  };

  const getErrorIcon = (error: AppError | Error): React.ReactNode => {
    if (error instanceof AppError) {
      switch (error.code) {
        case "HTTP_404":
        case "HTTP_500":
        case "HTTP_429":
          return (
            <svg className="h-6 w-6 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          );
        case "TIMEOUT":
        case "ABORTED":
          return (
            <svg className="h-6 w-6 text-yellow-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          );
        case "INVALID_CONTENT_TYPE":
        case "INVALID_DATA_STRUCTURE":
          return (
            <svg className="h-6 w-6 text-orange-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          );
        default:
          return (
            <svg className="h-6 w-6 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          );
      }
    }
    
    return (
      <svg className="h-6 w-6 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
      </svg>
    );
  };

  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
      <div className="flex items-start">
        <div className="flex-shrink-0">
          {getErrorIcon(error)}
        </div>
        <div className="ml-3 flex-1">
          <h3 className="text-sm font-medium text-red-800">
            データの読み込みに失敗しました
          </h3>
          <div className="mt-2 text-sm text-red-700">
            <p>{getErrorMessage(error)}</p>
          </div>
          <div className="mt-4 flex space-x-3">
            {onRetry && (
              <button
                onClick={onRetry}
                className="bg-red-600 text-white px-3 py-1 rounded text-sm font-medium hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500"
              >
                再試行
              </button>
            )}
            {onDismiss && (
              <button
                onClick={onDismiss}
                className="bg-gray-600 text-white px-3 py-1 rounded text-sm font-medium hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500"
              >
                閉じる
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
