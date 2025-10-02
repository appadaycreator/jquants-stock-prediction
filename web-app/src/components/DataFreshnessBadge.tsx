/**
 * データ鮮度バッジコンポーネント
 * リアルタイムデータの鮮度を視覚的に表示
 */

"use client";

import React, { useState, useEffect } from "react";
import { RefreshCw, Clock, CheckCircle, AlertTriangle, XCircle } from "lucide-react";
import EnhancedDataFreshnessManager from "@/lib/enhanced-data-freshness-manager";

interface DataFreshnessBadgeProps {
  dataSourceId: string;
  dataSourceName: string;
  lastUpdated: Date | string | number;
  source: "api" | "cache" | "fallback";
  ttlMinutes?: number;
  onRefresh?: () => Promise<void>;
  showDetails?: boolean;
  className?: string;
}

const DataFreshnessBadge: React.FC<DataFreshnessBadgeProps> = ({
  dataSourceId,
  dataSourceName,
  lastUpdated,
  source,
  ttlMinutes,
  onRefresh,
  showDetails = false,
  className = "",
}) => {
  const [freshnessInfo, setFreshnessInfo] = useState<any>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);

  const freshnessManager = EnhancedDataFreshnessManager.getInstance();

  // 鮮度情報の更新
  useEffect(() => {
    const updateFreshnessInfo = () => {
      const info = freshnessManager.getFreshnessInfo(lastUpdated, source, ttlMinutes);
      setFreshnessInfo(info);
    };

    // 初回更新
    updateFreshnessInfo();

    // データソースの登録
    freshnessManager.registerDataSource(
      dataSourceId,
      dataSourceName,
      new Date(lastUpdated),
      ttlMinutes,
      source,
    );

    // リフレッシュコールバックの登録
    if (onRefresh) {
      freshnessManager.registerRefreshCallback(dataSourceId, async () => {
        if (onRefresh) {
          await onRefresh();
          setLastRefresh(new Date());
        }
      });
    }

    // 定期的な更新
    const interval = setInterval(updateFreshnessInfo, 30000); // 30秒ごと

    return () => {
      clearInterval(interval);
    };
  }, [dataSourceId, dataSourceName, lastUpdated, source, ttlMinutes, onRefresh]);

  // 手動リフレッシュ
  const handleRefresh = async () => {
    if (isRefreshing || !onRefresh) {
      return;
    }

    try {
      setIsRefreshing(true);
      await freshnessManager.refreshDataSource(dataSourceId);
      setLastRefresh(new Date());
    } catch (error) {
      console.error("リフレッシュエラー:", error);
    } finally {
      setIsRefreshing(false);
    }
  };

  if (!freshnessInfo) {
    return (
      <div className={`inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-gray-100 text-gray-800 text-sm ${className}`}>
        <Clock className="h-4 w-4" />
        <span>読み込み中...</span>
      </div>
    );
  }

  // バッジの色とアイコンの決定
  const getBadgeStyle = () => {
    switch (freshnessInfo.cacheStatus) {
      case "fresh":
        return {
          bgColor: "bg-green-100",
          textColor: "text-green-800",
          icon: <CheckCircle className="h-4 w-4" />,
          iconColor: "text-green-600",
        };
      case "stale":
        return {
          bgColor: "bg-yellow-100",
          textColor: "text-yellow-800",
          icon: <AlertTriangle className="h-4 w-4" />,
          iconColor: "text-yellow-600",
        };
      case "expired":
        return {
          bgColor: "bg-red-100",
          textColor: "text-red-800",
          icon: <XCircle className="h-4 w-4" />,
          iconColor: "text-red-600",
        };
      default:
        return {
          bgColor: "bg-gray-100",
          textColor: "text-gray-800",
          icon: <Clock className="h-4 w-4" />,
          iconColor: "text-gray-600",
        };
    }
  };

  const badgeStyle = getBadgeStyle();
  const relativeTime = getRelativeTime(freshnessInfo.lastUpdated);

  return (
    <div className={`inline-flex items-center space-x-2 ${className}`}>
      {/* メインバッジ */}
      <div className={`inline-flex items-center space-x-2 px-3 py-1 rounded-full ${badgeStyle.bgColor} ${badgeStyle.textColor} text-sm`}>
        {badgeStyle.icon}
        <span className="font-medium">{dataSourceName}</span>
        <span className="text-xs opacity-75">
          {freshnessInfo.cacheStatus.toUpperCase()}
        </span>
      </div>

      {/* 詳細情報 */}
      {showDetails && (
        <div className="text-xs text-gray-600 dark:text-gray-400">
          <div>最終更新: {relativeTime}</div>
          <div>ソース: {source}</div>
          {freshnessInfo.nextRefresh && (
            <div>次回更新: {getRelativeTime(freshnessInfo.nextRefresh)}</div>
          )}
        </div>
      )}

      {/* リフレッシュボタン */}
      {onRefresh && (
        <button
          onClick={handleRefresh}
          disabled={isRefreshing}
          className={`p-1 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors duration-200 ${
            isRefreshing ? "opacity-50 cursor-not-allowed" : ""
          }`}
          title="データを更新"
        >
          <RefreshCw className={`h-4 w-4 ${isRefreshing ? "animate-spin" : ""}`} />
        </button>
      )}

      {/* 最終リフレッシュ時刻 */}
      {lastRefresh && (
        <div className="text-xs text-gray-500 dark:text-gray-400">
          更新: {getRelativeTime(lastRefresh)}
        </div>
      )}
    </div>
  );
};

// 相対時間の取得
const getRelativeTime = (date: Date | string | number): string => {
  const now = new Date();
  const targetDate = new Date(date);
  const diffMs = now.getTime() - targetDate.getTime();
  const diffMinutes = Math.floor(diffMs / (1000 * 60));
  const diffHours = Math.floor(diffMinutes / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMinutes < 1) {
    return "たった今";
  } else if (diffMinutes < 60) {
    return `${diffMinutes}分前`;
  } else if (diffHours < 24) {
    return `${diffHours}時間前`;
  } else {
    return `${diffDays}日前`;
  }
};

export default DataFreshnessBadge;
export { default as DataFreshnessSummary } from "./DataFreshnessSummary";