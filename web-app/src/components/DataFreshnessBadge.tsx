"use client";

import React from 'react';
import { DataFreshnessInfo, freshnessManager } from '@/lib/data-freshness-manager';
import { Clock, RefreshCw, Database, Wifi, AlertTriangle } from 'lucide-react';

interface DataFreshnessBadgeProps {
  freshnessInfo: DataFreshnessInfo;
  showDetails?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  onRefresh?: () => void;
}

export default function DataFreshnessBadge({
  freshnessInfo,
  showDetails = false,
  size = 'md',
  className = '',
  onRefresh,
}: DataFreshnessBadgeProps) {
  const badgeStyle = freshnessManager.getFreshnessBadgeStyle(freshnessInfo.cacheStatus);
  const relativeTime = freshnessManager.getRelativeTimeString(freshnessInfo.ageMinutes);
  const nextRefresh = freshnessInfo.nextRefresh 
    ? freshnessManager.getNextRefreshString(freshnessInfo.nextRefresh)
    : null;

  const sizeClasses = {
    sm: 'text-xs px-2 py-1',
    md: 'text-sm px-3 py-1.5',
    lg: 'text-base px-4 py-2',
  };

  const iconSize = {
    sm: 'w-3 h-3',
    md: 'w-4 h-4',
    lg: 'w-5 h-5',
  };

  const getSourceIcon = () => {
    switch (freshnessInfo.source) {
      case 'api':
        return <Wifi className={iconSize[size]} />;
      case 'cache':
        return <Database className={iconSize[size]} />;
      case 'fallback':
        return <AlertTriangle className={iconSize[size]} />;
      default:
        return <Clock className={iconSize[size]} />;
    }
  };

  const getSourceText = () => {
    switch (freshnessInfo.source) {
      case 'api':
        return 'API';
      case 'cache':
        return 'キャッシュ';
      case 'fallback':
        return 'フォールバック';
      default:
        return '不明';
    }
  };

  return (
    <div className={`inline-flex items-center gap-2 ${className}`}>
      {/* メインバッジ */}
      <div className={`inline-flex items-center gap-1.5 rounded-full border ${badgeStyle.className} ${sizeClasses[size]}`}>
        <span className="text-xs">{badgeStyle.icon}</span>
        <span className="font-medium">{badgeStyle.text}</span>
        {getSourceIcon()}
      </div>

      {/* 詳細情報 */}
      {showDetails && (
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <div className="flex items-center gap-1">
            <Clock className="w-4 h-4" />
            <span>{relativeTime}</span>
          </div>
          
          <div className="flex items-center gap-1">
            {getSourceIcon()}
            <span>{getSourceText()}</span>
          </div>

          {nextRefresh && (
            <div className="flex items-center gap-1">
              <RefreshCw className="w-4 h-4" />
              <span>{nextRefresh}</span>
            </div>
          )}

          {onRefresh && (
            <button
              onClick={onRefresh}
              className="ml-2 p-1 rounded hover:bg-gray-100 transition-colors"
              title="データを更新"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          )}
        </div>
      )}
    </div>
  );
}

interface DataFreshnessSummaryProps {
  freshnessInfos: DataFreshnessInfo[];
  onRefreshAll?: () => void;
  className?: string;
}

export function DataFreshnessSummary({
  freshnessInfos,
  onRefreshAll,
  className = '',
}: DataFreshnessSummaryProps) {
  const combined = freshnessManager.getCombinedFreshnessInfo(freshnessInfos);
  
  const getOverallBadgeStyle = () => {
    switch (combined.overallStatus) {
      case 'all_fresh':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'mixed':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'all_stale':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'all_expired':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getOverallText = () => {
    switch (combined.overallStatus) {
      case 'all_fresh':
        return 'すべて最新';
      case 'mixed':
        return '一部古い';
      case 'all_stale':
        return 'すべて古い';
      case 'all_expired':
        return 'すべて期限切れ';
      default:
        return '不明';
    }
  };

  return (
    <div className={`flex items-center gap-3 ${className}`}>
      <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full border text-sm font-medium ${getOverallBadgeStyle()}`}>
        <span>{getOverallText()}</span>
        <span className="text-xs">
          ({combined.freshCount}/{combined.totalCount})
        </span>
      </div>

      {combined.oldestData && (
        <div className="text-sm text-gray-600">
          最古: {freshnessManager.getRelativeTimeString(combined.oldestData.ageMinutes)}
        </div>
      )}

      {onRefreshAll && (
        <button
          onClick={onRefreshAll}
          className="flex items-center gap-1 px-3 py-1.5 text-sm bg-blue-100 text-blue-800 rounded-full hover:bg-blue-200 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          すべて更新
        </button>
      )}
    </div>
  );
}
