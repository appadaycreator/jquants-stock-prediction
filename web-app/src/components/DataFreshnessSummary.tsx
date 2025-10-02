/**
 * データ鮮度サマリーコンポーネント
 * 複数のデータソースの鮮度状況を簡潔に表示
 */

"use client";

import React, { useState, useEffect } from "react";
import { 
  RefreshCw, 
  Clock, 
  CheckCircle, 
  AlertTriangle, 
  XCircle,
  Database,
  TrendingUp,
} from "lucide-react";
import EnhancedDataFreshnessManager from "@/lib/enhanced-data-freshness-manager";

interface DataFreshnessSummaryProps {
  className?: string;
  showRefreshButton?: boolean;
  onRefresh?: () => Promise<void>;
  freshnessInfos?: any[];
  onRefreshAll?: () => Promise<void>;
}

const DataFreshnessSummary: React.FC<DataFreshnessSummaryProps> = ({
  className = "",
  showRefreshButton = true,
  onRefresh,
  freshnessInfos,
  onRefreshAll,
}) => {
  const [freshnessInfo, setFreshnessInfo] = useState<Map<string, any>>(new Map());
  const [systemHealth, setSystemHealth] = useState<any>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  const freshnessManager = EnhancedDataFreshnessManager.getInstance();

  // 鮮度情報の更新
  useEffect(() => {
    const updateFreshnessInfo = () => {
      const info = freshnessManager.getAllFreshnessInfo();
      setFreshnessInfo(info);
      
      const health = freshnessManager.getSystemHealth();
      setSystemHealth(health);
      
      setLastUpdate(new Date());
    };

    // 初回更新
    updateFreshnessInfo();

    // 定期的な更新
    const interval = setInterval(updateFreshnessInfo, 30000); // 30秒ごと

    return () => {
      clearInterval(interval);
    };
  }, []);

  // 手動リフレッシュ
  const handleRefresh = async () => {
    if (isRefreshing) {
      return;
    }

    try {
      setIsRefreshing(true);
      
      if (onRefreshAll) {
        await onRefreshAll();
      } else if (onRefresh) {
        await onRefresh();
      } else {
        await freshnessManager.refreshAllDataSources();
      }
      
      setLastUpdate(new Date());
    } catch (error) {
      console.error("リフレッシュエラー:", error);
    } finally {
      setIsRefreshing(false);
    }
  };

  // システムヘルスアイコンの取得
  const getHealthIcon = () => {
    if (!systemHealth) return <Clock className="h-4 w-4" />;
    
    switch (systemHealth.status) {
      case "healthy":
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case "warning":
        return <AlertTriangle className="h-4 w-4 text-yellow-600" />;
      case "critical":
        return <XCircle className="h-4 w-4 text-red-600" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  // システムヘルス色の取得
  const getHealthColor = () => {
    if (!systemHealth) return "text-gray-600";
    
    switch (systemHealth.status) {
      case "healthy":
        return "text-green-600";
      case "warning":
        return "text-yellow-600";
      case "critical":
        return "text-red-600";
      default:
        return "text-gray-600";
    }
  };

  // 鮮度統計の計算
  const getFreshnessStats = () => {
    let freshCount = 0;
    let staleCount = 0;
    let expiredCount = 0;

    freshnessInfo.forEach((info) => {
      switch (info.cacheStatus) {
        case "fresh":
          freshCount++;
          break;
        case "stale":
          staleCount++;
          break;
        case "expired":
          expiredCount++;
          break;
      }
    });

    return { freshCount, staleCount, expiredCount };
  };

  const stats = getFreshnessStats();
  const totalSources = freshnessInfo.size;

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 ${className}`}>
      {/* ヘッダー */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <Database className="h-5 w-5 text-blue-600" />
          <h3 className="text-sm font-medium text-gray-900 dark:text-white">
            データ鮮度サマリー
          </h3>
        </div>
        
        {showRefreshButton && (
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
      </div>

      {/* システムヘルス */}
      {systemHealth && (
        <div className="flex items-center space-x-2 mb-3">
          {getHealthIcon()}
          <span className={`text-sm font-medium ${getHealthColor()}`}>
            {systemHealth.status.toUpperCase()}
          </span>
          <span className="text-xs text-gray-500 dark:text-gray-400">
            ({systemHealth.activeSources}/{systemHealth.totalSources} アクティブ)
          </span>
        </div>
      )}

      {/* 鮮度統計 */}
      <div className="grid grid-cols-3 gap-3 text-center">
        <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-2">
          <div className="flex items-center justify-center space-x-1 mb-1">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <span className="text-lg font-bold text-green-600">{stats.freshCount}</span>
          </div>
          <div className="text-xs text-green-700 dark:text-green-300">フレッシュ</div>
        </div>
        
        <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-2">
          <div className="flex items-center justify-center space-x-1 mb-1">
            <AlertTriangle className="h-4 w-4 text-yellow-600" />
            <span className="text-lg font-bold text-yellow-600">{stats.staleCount}</span>
          </div>
          <div className="text-xs text-yellow-700 dark:text-yellow-300">ステール</div>
        </div>
        
        <div className="bg-red-50 dark:bg-red-900/20 rounded-lg p-2">
          <div className="flex items-center justify-center space-x-1 mb-1">
            <XCircle className="h-4 w-4 text-red-600" />
            <span className="text-lg font-bold text-red-600">{stats.expiredCount}</span>
          </div>
          <div className="text-xs text-red-700 dark:text-red-300">期限切れ</div>
        </div>
      </div>

      {/* 最終更新時刻 */}
      {lastUpdate && (
        <div className="mt-3 text-xs text-gray-500 dark:text-gray-400 text-center">
          最終更新: {lastUpdate.toLocaleTimeString()}
        </div>
      )}

      {/* 問題の表示 */}
      {systemHealth && systemHealth.issues.length > 0 && (
        <div className="mt-3 p-2 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <div className="flex items-center space-x-1 mb-1">
            <XCircle className="h-3 w-3 text-red-600" />
            <span className="text-xs font-medium text-red-800 dark:text-red-200">
              {systemHealth.issues.length}件の問題
            </span>
          </div>
          <div className="text-xs text-red-700 dark:text-red-300">
            {systemHealth.issues[0]}
            {systemHealth.issues.length > 1 && ` 他${systemHealth.issues.length - 1}件`}
          </div>
        </div>
      )}
    </div>
  );
};

export default DataFreshnessSummary;
