"use client";

import React, { useState, useEffect } from 'react';
import { RefreshCw, Download, Zap, AlertCircle, CheckCircle, Clock, Database } from 'lucide-react';

interface RefreshButtonProps {
  onRefresh: () => Promise<void>;
  onForceRefresh?: () => Promise<void>;
  onRecompute?: () => Promise<void>;
  isLoading?: boolean;
  lastRefresh?: Date;
  refreshInterval?: number; // 自動更新間隔（分）
  showProgress?: boolean;
  showLastRefresh?: boolean;
  variant?: 'default' | 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export default function EnhancedRefreshButton({
  onRefresh,
  onForceRefresh,
  onRecompute,
  isLoading = false,
  lastRefresh,
  refreshInterval,
  showProgress = true,
  showLastRefresh = true,
  variant = 'default',
  size = 'md',
  className = '',
}: RefreshButtonProps) {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isForceRefreshing, setIsForceRefreshing] = useState(false);
  const [isRecomputing, setIsRecomputing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [lastRefreshTime, setLastRefreshTime] = useState<Date | null>(lastRefresh || null);
  const [autoRefreshCountdown, setAutoRefreshCountdown] = useState<number | null>(null);

  // 自動更新のカウントダウン
  useEffect(() => {
    if (!refreshInterval) return;

    const interval = setInterval(() => {
      setAutoRefreshCountdown(prev => {
        if (prev === null) return refreshInterval * 60; // 秒に変換
        if (prev <= 1) {
          handleRefresh();
          return refreshInterval * 60;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [refreshInterval]);

  const handleRefresh = async () => {
    if (isRefreshing) return;
    
    setIsRefreshing(true);
    setProgress(0);
    
    try {
      // プログレスシミュレーション
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return prev;
          }
          return prev + Math.random() * 20;
        });
      }, 200);

      await onRefresh();
      
      clearInterval(progressInterval);
      setProgress(100);
      setLastRefreshTime(new Date());
      
      setTimeout(() => {
        setProgress(0);
      }, 1000);
    } catch (error) {
      console.error('Refresh failed:', error);
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleForceRefresh = async () => {
    if (isForceRefreshing || !onForceRefresh) return;
    
    setIsForceRefreshing(true);
    try {
      await onForceRefresh();
      setLastRefreshTime(new Date());
    } catch (error) {
      console.error('Force refresh failed:', error);
    } finally {
      setIsForceRefreshing(false);
    }
  };

  const handleRecompute = async () => {
    if (isRecomputing || !onRecompute) return;
    
    setIsRecomputing(true);
    try {
      await onRecompute();
      setLastRefreshTime(new Date());
    } catch (error) {
      console.error('Recompute failed:', error);
    } finally {
      setIsRecomputing(false);
    }
  };

  const getVariantStyles = () => {
    switch (variant) {
      case 'primary':
        return 'bg-blue-600 text-white hover:bg-blue-700 border-blue-600';
      case 'secondary':
        return 'bg-gray-600 text-white hover:bg-gray-700 border-gray-600';
      case 'danger':
        return 'bg-red-600 text-white hover:bg-red-700 border-red-600';
      default:
        return 'bg-white text-gray-700 hover:bg-gray-50 border-gray-300';
    }
  };

  const getSizeStyles = () => {
    switch (size) {
      case 'sm':
        return 'px-2 py-1 text-xs';
      case 'lg':
        return 'px-6 py-3 text-base';
      default:
        return 'px-4 py-2 text-sm';
    }
  };

  const formatCountdown = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const formatLastRefresh = (date: Date): string => {
    const now = new Date();
    const diffMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
    
    if (diffMinutes < 1) return 'たった今';
    if (diffMinutes < 60) return `${diffMinutes}分前`;
    if (diffMinutes < 1440) return `${Math.floor(diffMinutes / 60)}時間前`;
    return `${Math.floor(diffMinutes / 1440)}日前`;
  };

  return (
    <div className={`space-y-2 ${className}`}>
      {/* メインボタン群 */}
      <div className="flex items-center gap-2">
        {/* 通常更新 */}
        <button
          onClick={handleRefresh}
          disabled={isRefreshing || isForceRefreshing || isRecomputing}
          className={`flex items-center gap-2 rounded border transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${getVariantStyles()} ${getSizeStyles()}`}
        >
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
          <span>
            {isRefreshing ? '更新中...' : '更新'}
          </span>
        </button>

        {/* 強制更新 */}
        {onForceRefresh && (
          <button
            onClick={handleForceRefresh}
            disabled={isRefreshing || isForceRefreshing || isRecomputing}
            className="flex items-center gap-2 px-3 py-2 text-sm bg-orange-100 text-orange-800 border border-orange-200 rounded hover:bg-orange-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Zap className={`w-4 h-4 ${isForceRefreshing ? 'animate-pulse' : ''}`} />
            <span>
              {isForceRefreshing ? '強制更新中...' : '強制更新'}
            </span>
          </button>
        )}

        {/* 再計算 */}
        {onRecompute && (
          <button
            onClick={handleRecompute}
            disabled={isRefreshing || isForceRefreshing || isRecomputing}
            className="flex items-center gap-2 px-3 py-2 text-sm bg-purple-100 text-purple-800 border border-purple-200 rounded hover:bg-purple-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Download className={`w-4 h-4 ${isRecomputing ? 'animate-bounce' : ''}`} />
            <span>
              {isRecomputing ? '再計算中...' : '再計算'}
            </span>
          </button>
        )}
      </div>

      {/* プログレスバー */}
      {showProgress && (isRefreshing || isForceRefreshing || isRecomputing) && (
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      )}

      {/* ステータス情報 */}
      <div className="flex items-center justify-between text-sm text-gray-600">
        <div className="flex items-center gap-4">
          {/* 最終更新時刻 */}
          {showLastRefresh && lastRefreshTime && (
            <div className="flex items-center gap-1">
              <Clock className="w-4 h-4" />
              <span>最終更新: {formatLastRefresh(lastRefreshTime)}</span>
            </div>
          )}

          {/* 自動更新カウントダウン */}
          {autoRefreshCountdown !== null && (
            <div className="flex items-center gap-1">
              <Database className="w-4 h-4" />
              <span>次回自動更新: {formatCountdown(autoRefreshCountdown)}</span>
            </div>
          )}
        </div>

        {/* ステータスアイコン */}
        <div className="flex items-center gap-1">
          {isRefreshing || isForceRefreshing || isRecomputing ? (
            <RefreshCw className="w-4 h-4 animate-spin text-blue-600" />
          ) : lastRefreshTime ? (
            <CheckCircle className="w-4 h-4 text-green-600" />
          ) : (
            <AlertCircle className="w-4 h-4 text-gray-400" />
          )}
        </div>
      </div>
    </div>
  );
}

interface RefreshButtonGroupProps {
  onRefresh: () => Promise<void>;
  onForceRefresh?: () => Promise<void>;
  onRecompute?: () => Promise<void>;
  lastRefresh?: Date;
  refreshInterval?: number;
  className?: string;
}

export function RefreshButtonGroup({
  onRefresh,
  onForceRefresh,
  onRecompute,
  lastRefresh,
  refreshInterval,
  className = '',
}: RefreshButtonGroupProps) {
  return (
    <div className={`space-y-3 ${className}`}>
      <EnhancedRefreshButton
        onRefresh={onRefresh}
        onForceRefresh={onForceRefresh}
        onRecompute={onRecompute}
        lastRefresh={lastRefresh}
        refreshInterval={refreshInterval}
        variant="primary"
        size="md"
        showProgress={true}
        showLastRefresh={true}
      />
    </div>
  );
}
