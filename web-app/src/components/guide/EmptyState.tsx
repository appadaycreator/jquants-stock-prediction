"use client";

import React from "react";
import { RefreshCw, Settings, AlertCircle, Database, TrendingUp } from "lucide-react";

interface EmptyStateProps {
  type: "no-data" | "error" | "loading" | "no-results";
  title: string;
  description: string;
  actions: {
    label: string;
    onClick: () => void;
    variant: "primary" | "secondary";
    icon?: React.ReactNode;
  }[];
  className?: string;
}

export default function EmptyState({ 
  type, 
  title, 
  description, 
  actions, 
  className = "", 
}: EmptyStateProps) {
  const getIcon = () => {
    switch (type) {
      case "no-data":
        return <Database size={48} className="text-gray-400" />;
      case "error":
        return <AlertCircle size={48} className="text-red-400" />;
      case "loading":
        return <RefreshCw size={48} className="text-blue-400 animate-spin" />;
      case "no-results":
        return <TrendingUp size={48} className="text-gray-400" />;
      default:
        return <Database size={48} className="text-gray-400" />;
    }
  };

  return (
    <div className={`flex flex-col items-center justify-center p-8 text-center ${className}`}>
      <div className="mb-4">
        {getIcon()}
      </div>
      
      <h3 className="text-lg font-semibold text-gray-900 mb-2">
        {title}
      </h3>
      
      <p className="text-gray-600 mb-6 max-w-md">
        {description}
      </p>
      
      <div className="flex flex-col sm:flex-row gap-3">
        {actions.map((action, index) => (
          <button
            key={index}
            onClick={action.onClick}
            className={`flex items-center gap-2 px-4 py-2 rounded-md font-medium transition-colors ${
              action.variant === "primary"
                ? "bg-blue-600 text-white hover:bg-blue-700"
                : "bg-gray-100 text-gray-700 hover:bg-gray-200"
            }`}
          >
            {action.icon}
            {action.label}
          </button>
        ))}
      </div>
    </div>
  );
}

// データ未生成時の空状態
export function NoDataEmptyState({ onRefresh, onSettings }: { 
  onRefresh: () => void; 
  onSettings: () => void;
}) {
  return (
    <EmptyState
      type="no-data"
      title="データがありません"
      description="分析結果がまだ生成されていません。最新データを取得するか、設定を確認してください。"
      actions={[
        {
          label: "最新結果を再取得",
          onClick: onRefresh,
          variant: "primary",
          icon: <RefreshCw size={16} />,
        },
        {
          label: "設定を確認",
          onClick: onSettings,
          variant: "secondary",
          icon: <Settings size={16} />,
        },
      ]}
    />
  );
}

// エラー時の空状態
export function ErrorEmptyState({ 
  error, 
  onRetry, 
  onSettings, 
}: { 
  error: string; 
  onRetry: () => void; 
  onSettings: () => void;
}) {
  return (
    <EmptyState
      type="error"
      title="エラーが発生しました"
      description={`${error}。設定を確認するか、しばらく時間をおいてから再試行してください。`}
      actions={[
        {
          label: "再試行",
          onClick: onRetry,
          variant: "primary",
          icon: <RefreshCw size={16} />,
        },
        {
          label: "設定を見直す",
          onClick: onSettings,
          variant: "secondary",
          icon: <Settings size={16} />,
        },
      ]}
    />
  );
}

// ローディング時の空状態
export function LoadingEmptyState({ message = "データを読み込み中..." }: { 
  message?: string;
}) {
  return (
    <EmptyState
      type="loading"
      title={message}
      description="しばらくお待ちください。データの取得と分析に時間がかかる場合があります。"
      actions={[]}
    />
  );
}

// 検索結果なしの空状態
export function NoResultsEmptyState({ 
  searchTerm, 
  onClearSearch, 
}: { 
  searchTerm: string; 
  onClearSearch: () => void;
}) {
  return (
    <EmptyState
      type="no-results"
      title="検索結果が見つかりません"
      description={`「${searchTerm}」に一致する結果がありません。別のキーワードで検索してみてください。`}
      actions={[
        {
          label: "検索をクリア",
          onClick: onClearSearch,
          variant: "primary",
        },
      ]}
    />
  );
}
