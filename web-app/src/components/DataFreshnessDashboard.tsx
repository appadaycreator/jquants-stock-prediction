/**
 * データ鮮度ダッシュボードコンポーネント
 * 全データソースの鮮度状況を一覧表示
 */

"use client";

import React, { useState, useEffect } from "react";
import { 
  RefreshCw, 
  Clock, 
  CheckCircle, 
  AlertTriangle, 
  XCircle,
  TrendingUp,
  Database,
  Wifi,
  WifiOff,
} from "lucide-react";
import EnhancedDataFreshnessManager from "@/lib/enhanced-data-freshness-manager";
import DataFreshnessBadge from "./DataFreshnessBadge";

interface DataFreshnessDashboardProps {
  className?: string;
  showSystemHealth?: boolean;
  showRefreshControls?: boolean;
}

const DataFreshnessDashboard: React.FC<DataFreshnessDashboardProps> = ({
  className = "",
  showSystemHealth = true,
  showRefreshControls = true,
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
      
      if (showSystemHealth) {
        const health = freshnessManager.getSystemHealth();
        setSystemHealth(health);
      }
      
      setLastUpdate(new Date());
    };

    // 初回更新
    updateFreshnessInfo();

    // 定期的な更新
    const interval = setInterval(updateFreshnessInfo, 30000); // 30秒ごと

    return () => {
      clearInterval(interval);
    };
  }, [showSystemHealth, freshnessManager]);

  // 全データソースのリフレッシュ
  const handleRefreshAll = async () => {
    if (isRefreshing) {
      return;
    }

    try {
      setIsRefreshing(true);
      const result = await freshnessManager.refreshAllDataSources();
      console.info(`リフレッシュ完了: 成功 ${result.success}件, 失敗 ${result.failed}件`);
    } catch (error) {
      console.error("リフレッシュエラー:", error);
    } finally {
      setIsRefreshing(false);
    }
  };

  // システムヘルスアイコンの取得
  const getHealthIcon = () => {
    if (!systemHealth) return <Clock className="h-5 w-5" />;
    
    switch (systemHealth.status) {
      case "healthy":
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case "warning":
        return <AlertTriangle className="h-5 w-5 text-yellow-600" />;
      case "critical":
        return <XCircle className="h-5 w-5 text-red-600" />;
      default:
        return <Clock className="h-5 w-5" />;
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

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 ${className}`}>
      {/* ヘッダー */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <Database className="h-6 w-6 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            データ鮮度ダッシュボード
          </h3>
        </div>
        
        {showRefreshControls && (
          <button
            onClick={handleRefreshAll}
            disabled={isRefreshing}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition-colors duration-200 ${
              isRefreshing ? "opacity-50 cursor-not-allowed" : ""
            }`}
          >
            <RefreshCw className={`h-4 w-4 ${isRefreshing ? "animate-spin" : ""}`} />
            <span>{isRefreshing ? "更新中..." : "全更新"}</span>
          </button>
        )}
      </div>

      {/* システムヘルス */}
      {showSystemHealth && systemHealth && (
        <div className="mb-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              {getHealthIcon()}
              <span className={`font-medium ${getHealthColor()}`}>
                システムヘルス: {systemHealth.status.toUpperCase()}
              </span>
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              最終更新: {lastUpdate ? lastUpdate.toLocaleTimeString() : "未更新"}
            </div>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{systemHealth.totalSources}</div>
              <div className="text-gray-600 dark:text-gray-400">総データソース</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{systemHealth.freshSources}</div>
              <div className="text-gray-600 dark:text-gray-400">フレッシュ</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-600">{systemHealth.staleSources}</div>
              <div className="text-gray-600 dark:text-gray-400">ステール</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">{systemHealth.expiredSources}</div>
              <div className="text-gray-600 dark:text-gray-400">期限切れ</div>
            </div>
          </div>

          {/* 問題の表示 */}
          {systemHealth.issues.length > 0 && (
            <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
              <div className="flex items-center space-x-2 mb-2">
                <XCircle className="h-4 w-4 text-red-600" />
                <span className="font-medium text-red-800 dark:text-red-200">問題が発生しています</span>
              </div>
              <ul className="text-sm text-red-700 dark:text-red-300 space-y-1">
                {systemHealth.issues.map((issue: string, index: number) => (
                  <li key={index}>• {issue}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* データソース一覧 */}
      <div className="space-y-3">
        <h4 className="text-md font-medium text-gray-900 dark:text-white mb-3">
          データソース一覧
        </h4>
        
        {freshnessInfo.size === 0 ? (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            <Database className="h-12 w-12 mx-auto mb-3 opacity-50" />
            <p>データソースが登録されていません</p>
          </div>
        ) : (
          <div className="space-y-2">
            {Array.from(freshnessInfo.entries()).map(([id, info]) => (
              <div
                key={id}
                className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
              >
                <div className="flex items-center space-x-3">
                  <div className="flex items-center space-x-2">
                    {info.cacheStatus === "fresh" && <CheckCircle className="h-5 w-5 text-green-600" />}
                    {info.cacheStatus === "stale" && <AlertTriangle className="h-5 w-5 text-yellow-600" />}
                    {info.cacheStatus === "expired" && <XCircle className="h-5 w-5 text-red-600" />}
                  </div>
                  
                  <div>
                    <div className="font-medium text-gray-900 dark:text-white">{id}</div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                      {info.ageMinutes}分前 • {info.source}
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    info.cacheStatus === "fresh" ? "bg-green-100 text-green-800" :
                    info.cacheStatus === "stale" ? "bg-yellow-100 text-yellow-800" :
                    "bg-red-100 text-red-800"
                  }`}>
                    {info.cacheStatus.toUpperCase()}
                  </span>
                  
                  <button
                    onClick={() => freshnessManager.refreshDataSource(id)}
                    className="p-1 rounded-full hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors duration-200"
                    title="データを更新"
                  >
                    <RefreshCw className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default DataFreshnessDashboard;
