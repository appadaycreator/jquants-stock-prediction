/**
 * キャッシュ可視化コンポーネント
 * キャッシュの状態と統計情報を表示
 */

"use client";

import React, { useState, useEffect } from "react";
import { 
  Database, 
  HardDrive, 
  Clock, 
  CheckCircle, 
  AlertTriangle, 
  XCircle,
  RefreshCw,
  TrendingUp,
  BarChart3,
} from "lucide-react";

interface CacheVisualizationProps {
  className?: string;
  showDetails?: boolean;
  showStats?: boolean;
  freshnessInfos?: any[];
  onRefreshAll?: () => Promise<void>;
}

const CacheVisualization: React.FC<CacheVisualizationProps> = ({
  className = "",
  showDetails = true,
  showStats = true,
  freshnessInfos,
  onRefreshAll,
}) => {
  const [cacheStats, setCacheStats] = useState({
    totalItems: 0,
    totalSize: 0,
    hitRate: 0,
    missRate: 0,
    lastCleanup: new Date(),
  });

  const [cacheItems, setCacheItems] = useState<Array<{
    key: string;
    size: number;
    lastAccessed: Date;
    ttl: number;
    isExpired: boolean;
  }>>([]);

  // キャッシュ統計の取得
  useEffect(() => {
    const getCacheStats = () => {
      try {
        const keys = Object.keys(localStorage);
        const cacheKeys = keys.filter(key => key.startsWith("stock_") || key.startsWith("cache_"));
        
        let totalSize = 0;
        const items: Array<{
          key: string;
          size: number;
          lastAccessed: Date;
          ttl: number;
          isExpired: boolean;
        }> = [];

        cacheKeys.forEach(key => {
          const value = localStorage.getItem(key);
          if (value) {
            const size = new Blob([value]).size;
            totalSize += size;
            
            try {
              const parsed = JSON.parse(value);
              const lastAccessed = parsed.timestamp ? new Date(parsed.timestamp) : new Date();
              const ttl = parsed.ttl || 3600000; // 1時間
              const isExpired = Date.now() - lastAccessed.getTime() > ttl;
              
              items.push({
                key,
                size,
                lastAccessed,
                ttl,
                isExpired,
              });
            } catch (e) {
              // パースできない場合はスキップ
            }
          }
        });

        setCacheStats({
          totalItems: cacheKeys.length,
          totalSize,
          hitRate: 0.85, // 仮の値
          missRate: 0.15, // 仮の値
          lastCleanup: new Date(),
        });

        setCacheItems(items);
      } catch (error) {
        console.error("キャッシュ統計取得エラー:", error);
      }
    };

    getCacheStats();
    
    // 定期的な更新
    const interval = setInterval(getCacheStats, 30000);
    return () => clearInterval(interval);
  }, []);

  // サイズのフォーマット
  const formatSize = (bytes: number): string => {
    if (bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  // 相対時間の取得
  const getRelativeTime = (date: Date): string => {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
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

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 ${className}`}>
      {/* ヘッダー */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Database className="h-5 w-5 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            キャッシュ可視化
          </h3>
        </div>
        
        <button
          onClick={() => window.location.reload()}
          className="p-1 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors duration-200"
          title="キャッシュを更新"
        >
          <RefreshCw className="h-4 w-4" />
        </button>
      </div>

      {/* 統計情報 */}
      {showStats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{cacheStats.totalItems}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">総アイテム数</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">{formatSize(cacheStats.totalSize)}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">総サイズ</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-yellow-600">{(cacheStats.hitRate * 100).toFixed(1)}%</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">ヒット率</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">{(cacheStats.missRate * 100).toFixed(1)}%</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">ミス率</div>
          </div>
        </div>
      )}

      {/* 詳細情報 */}
      {showDetails && (
        <div className="space-y-3">
          <h4 className="text-md font-medium text-gray-900 dark:text-white">
            キャッシュアイテム一覧
          </h4>
          
          {cacheItems.length === 0 ? (
            <div className="text-center py-8 text-gray-500 dark:text-gray-400">
              <Database className="h-12 w-12 mx-auto mb-3 opacity-50" />
              <p>キャッシュアイテムがありません</p>
            </div>
          ) : (
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {cacheItems.map((item, index) => (
                <div
                  key={index}
                  className={`flex items-center justify-between p-3 rounded-lg ${
                    item.isExpired 
                      ? "bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800" 
                      : "bg-gray-50 dark:bg-gray-700"
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <div className="flex items-center space-x-2">
                      {item.isExpired ? (
                        <XCircle className="h-4 w-4 text-red-600" />
                      ) : (
                        <CheckCircle className="h-4 w-4 text-green-600" />
                      )}
                    </div>
                    
                    <div>
                      <div className="font-medium text-gray-900 dark:text-white text-sm">
                        {item.key}
                      </div>
                      <div className="text-xs text-gray-600 dark:text-gray-400">
                        {formatSize(item.size)} • {getRelativeTime(item.lastAccessed)}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      item.isExpired 
                        ? "bg-red-100 text-red-800" 
                        : "bg-green-100 text-green-800"
                    }`}>
                      {item.isExpired ? "期限切れ" : "有効"}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// コンパクト版コンポーネント
export const CacheVisualizationCompact: React.FC<{
  className?: string;
}> = ({ className = "" }) => {
  const [cacheStats, setCacheStats] = useState({
    totalItems: 0,
    totalSize: 0,
  });

  useEffect(() => {
    const getCacheStats = () => {
      try {
        const keys = Object.keys(localStorage);
        const cacheKeys = keys.filter(key => key.startsWith("stock_") || key.startsWith("cache_"));
        
        let totalSize = 0;
        cacheKeys.forEach(key => {
          const value = localStorage.getItem(key);
          if (value) {
            totalSize += new Blob([value]).size;
          }
        });

        setCacheStats({
          totalItems: cacheKeys.length,
          totalSize,
        });
      } catch (error) {
        console.error("キャッシュ統計取得エラー:", error);
      }
    };

    getCacheStats();
    const interval = setInterval(getCacheStats, 30000);
    return () => clearInterval(interval);
  }, []);

  const formatSize = (bytes: number): string => {
    if (bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  return (
    <div className={`flex items-center space-x-4 ${className}`}>
      <div className="flex items-center space-x-2">
        <Database className="h-4 w-4 text-blue-600" />
        <span className="text-sm text-gray-600 dark:text-gray-400">
          {cacheStats.totalItems} アイテム
        </span>
      </div>
      <div className="flex items-center space-x-2">
        <HardDrive className="h-4 w-4 text-green-600" />
        <span className="text-sm text-gray-600 dark:text-gray-400">
          {formatSize(cacheStats.totalSize)}
        </span>
      </div>
    </div>
  );
};

export default CacheVisualization;