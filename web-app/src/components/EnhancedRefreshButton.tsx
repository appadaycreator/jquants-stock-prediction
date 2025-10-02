/**
 * 強化版リフレッシュボタンコンポーネント
 * 通常更新、強制更新、再計算の機能を提供
 */

"use client";

import React, { useState } from "react";
import { 
  RefreshCw, 
  RotateCcw, 
  Zap, 
  CheckCircle, 
  AlertTriangle,
  Clock,
} from "lucide-react";

interface EnhancedRefreshButtonProps {
  onRefresh?: () => Promise<void>;
  onForceRefresh?: () => Promise<void>;
  onRecalculate?: () => Promise<void>;
  onRecompute?: () => Promise<void>;
  isLoading?: boolean;
  lastUpdated?: Date | string | number;
  lastRefresh?: Date | string | number;
  showLastUpdated?: boolean;
  showLastRefresh?: boolean;
  variant?: "default" | "compact" | "full";
  size?: "sm" | "md" | "lg";
  showProgress?: boolean;
  refreshInterval?: number;
  className?: string;
}

const EnhancedRefreshButton: React.FC<EnhancedRefreshButtonProps> = ({
  onRefresh,
  onForceRefresh,
  onRecalculate,
  onRecompute,
  isLoading = false,
  lastUpdated,
  lastRefresh,
  showLastUpdated = true,
  showLastRefresh = true,
  variant = "default",
  size = "md",
  showProgress = false,
  refreshInterval,
  className = "",
}) => {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isForceRefreshing, setIsForceRefreshing] = useState(false);
  const [isRecalculating, setIsRecalculating] = useState(false);
  const [lastRefreshTime, setLastRefreshTime] = useState<Date | null>(null);

  // 通常更新
  const handleRefresh = async () => {
    if (isRefreshing || !onRefresh) return;
    
    try {
      setIsRefreshing(true);
      await onRefresh();
      setLastRefreshTime(new Date());
    } catch (error) {
      console.error("リフレッシュエラー:", error);
    } finally {
      setIsRefreshing(false);
    }
  };

  // 強制更新
  const handleForceRefresh = async () => {
    if (isForceRefreshing || !onForceRefresh) return;
    
    try {
      setIsForceRefreshing(true);
      await onForceRefresh();
      setLastRefreshTime(new Date());
    } catch (error) {
      console.error("強制リフレッシュエラー:", error);
    } finally {
      setIsForceRefreshing(false);
    }
  };

  // 再計算
  const handleRecalculate = async () => {
    if (isRecalculating || !onRecalculate) return;
    
    try {
      setIsRecalculating(true);
      await onRecalculate();
      setLastRefreshTime(new Date());
    } catch (error) {
      console.error("再計算エラー:", error);
    } finally {
      setIsRecalculating(false);
    }
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

  // コンパクト版
  if (variant === "compact") {
    return (
      <div className={`flex items-center space-x-2 ${className}`}>
        <button
          onClick={handleRefresh}
          disabled={isRefreshing || isLoading}
          className={`p-2 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors duration-200 ${
            isRefreshing || isLoading ? "opacity-50 cursor-not-allowed" : ""
          }`}
          title="データを更新"
        >
          <RefreshCw className={`h-4 w-4 ${isRefreshing ? "animate-spin" : ""}`} />
        </button>
        
        {showLastUpdated && lastUpdated && (
          <span className="text-xs text-gray-500 dark:text-gray-400">
            {getRelativeTime(lastUpdated)}
          </span>
        )}
      </div>
    );
  }

  // フル版
  if (variant === "full") {
    return (
      <div className={`space-y-3 ${className}`}>
        {/* ボタン群 */}
        <div className="flex items-center space-x-2">
          <button
            onClick={handleRefresh}
            disabled={isRefreshing || isLoading}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition-colors duration-200 ${
              isRefreshing || isLoading ? "opacity-50 cursor-not-allowed" : ""
            }`}
          >
            <RefreshCw className={`h-4 w-4 ${isRefreshing ? "animate-spin" : ""}`} />
            <span>{isRefreshing ? "更新中..." : "更新"}</span>
          </button>
          
          {onForceRefresh && (
            <button
              onClick={handleForceRefresh}
              disabled={isForceRefreshing || isLoading}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg bg-yellow-600 text-white hover:bg-yellow-700 transition-colors duration-200 ${
                isForceRefreshing || isLoading ? "opacity-50 cursor-not-allowed" : ""
              }`}
            >
              <Zap className={`h-4 w-4 ${isForceRefreshing ? "animate-pulse" : ""}`} />
              <span>{isForceRefreshing ? "強制更新中..." : "強制更新"}</span>
            </button>
          )}
          
          {onRecalculate && (
            <button
              onClick={handleRecalculate}
              disabled={isRecalculating || isLoading}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg bg-green-600 text-white hover:bg-green-700 transition-colors duration-200 ${
                isRecalculating || isLoading ? "opacity-50 cursor-not-allowed" : ""
              }`}
            >
              <RotateCcw className={`h-4 w-4 ${isRecalculating ? "animate-spin" : ""}`} />
              <span>{isRecalculating ? "再計算中..." : "再計算"}</span>
            </button>
          )}
        </div>
        
        {/* ステータス表示 */}
        <div className="flex items-center space-x-4 text-sm text-gray-600 dark:text-gray-400">
          {showLastUpdated && lastUpdated && (
            <div className="flex items-center space-x-1">
              <Clock className="h-4 w-4" />
              <span>最終更新: {getRelativeTime(lastUpdated)}</span>
            </div>
          )}
          
          {lastRefresh && (
            <div className="flex items-center space-x-1">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <span>更新完了: {getRelativeTime(lastRefresh)}</span>
            </div>
          )}
        </div>
      </div>
    );
  }

  // デフォルト版
  return (
    <div className={`flex items-center space-x-2 ${className}`}>
      <button
        onClick={handleRefresh}
        disabled={isRefreshing || isLoading}
        className={`flex items-center space-x-2 px-3 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition-colors duration-200 ${
          isRefreshing || isLoading ? "opacity-50 cursor-not-allowed" : ""
        }`}
      >
        <RefreshCw className={`h-4 w-4 ${isRefreshing ? "animate-spin" : ""}`} />
        <span>{isRefreshing ? "更新中..." : "更新"}</span>
      </button>
      
      {showLastUpdated && lastUpdated && (
        <span className="text-sm text-gray-600 dark:text-gray-400">
          {getRelativeTime(lastUpdated)}
        </span>
      )}
    </div>
  );
};

// リフレッシュボタングループ
export const RefreshButtonGroup: React.FC<{
  onRefresh?: () => Promise<void>;
  onForceRefresh?: () => Promise<void>;
  onRecalculate?: () => Promise<void>;
  isLoading?: boolean;
  className?: string;
}> = ({ onRefresh, onForceRefresh, onRecalculate, isLoading = false, className = "" }) => {
  return (
    <div className={`flex items-center space-x-2 ${className}`}>
      {onRefresh && (
        <EnhancedRefreshButton
          onRefresh={onRefresh}
          isLoading={isLoading}
          variant="compact"
        />
      )}
      
      {onForceRefresh && (
        <button
          onClick={onForceRefresh}
          disabled={isLoading}
          className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors duration-200"
          title="強制更新"
        >
          <Zap className="h-4 w-4" />
        </button>
      )}
      
      {onRecalculate && (
        <button
          onClick={onRecalculate}
          disabled={isLoading}
          className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors duration-200"
          title="再計算"
        >
          <RotateCcw className="h-4 w-4" />
        </button>
      )}
    </div>
  );
};

export default EnhancedRefreshButton;