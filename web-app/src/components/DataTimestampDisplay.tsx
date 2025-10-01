"use client";

import React, { useState, useEffect } from 'react';
import { DataFreshnessInfo, freshnessManager } from '@/lib/data-freshness-manager';
import { Clock, Calendar, RefreshCw, AlertCircle, CheckCircle } from 'lucide-react';

interface DataTimestampDisplayProps {
  freshnessInfo: DataFreshnessInfo;
  showRelative?: boolean;
  showAbsolute?: boolean;
  showNextRefresh?: boolean;
  autoUpdate?: boolean;
  className?: string;
  onRefresh?: () => void;
}

export default function DataTimestampDisplay({
  freshnessInfo,
  showRelative = true,
  showAbsolute = false,
  showNextRefresh = true,
  autoUpdate = true,
  className = '',
  onRefresh,
}: DataTimestampDisplayProps) {
  const [currentTime, setCurrentTime] = useState(new Date());

  // 自動更新（1分ごと）
  useEffect(() => {
    if (!autoUpdate) return;

    const interval = setInterval(() => {
      setCurrentTime(new Date());
    }, 60000); // 1分ごと

    return () => clearInterval(interval);
  }, [autoUpdate]);

  const formatDateTime = (date: Date): string => {
    return date.toLocaleString('ja-JP', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  const formatDate = (date: Date): string => {
    return date.toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    });
  };

  const formatTime = (date: Date): string => {
    return date.toLocaleTimeString('ja-JP', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  const relativeTime = freshnessManager.getRelativeTimeString(freshnessInfo.ageMinutes);
  const nextRefresh = freshnessInfo.nextRefresh 
    ? freshnessManager.getNextRefreshString(freshnessInfo.nextRefresh)
    : null;

  const getStatusIcon = () => {
    if (freshnessInfo.isFresh) {
      return <CheckCircle className="w-4 h-4 text-green-500" />;
    } else if (freshnessInfo.cacheStatus === 'stale') {
      return <AlertCircle className="w-4 h-4 text-yellow-500" />;
    } else {
      return <AlertCircle className="w-4 h-4 text-red-500" />;
    }
  };

  return (
    <div className={`space-y-2 ${className}`}>
      {/* メイン表示 */}
      <div className="flex items-center gap-2">
        {getStatusIcon()}
        <div className="flex items-center gap-1">
          <Clock className="w-4 h-4 text-gray-500" />
          <span className="text-sm font-medium text-gray-700">
            最終更新: {showRelative ? relativeTime : formatDateTime(freshnessInfo.lastUpdated)}
          </span>
        </div>
        {onRefresh && (
          <button
            onClick={onRefresh}
            className="p-1 rounded hover:bg-gray-100 transition-colors"
            title="データを更新"
          >
            <RefreshCw className="w-4 h-4 text-gray-500" />
          </button>
        )}
      </div>

      {/* 詳細情報 */}
      {(showAbsolute || showNextRefresh) && (
        <div className="pl-6 space-y-1 text-xs text-gray-600">
          {showAbsolute && (
            <div className="flex items-center gap-1">
              <Calendar className="w-3 h-3" />
              <span>日時: {formatDateTime(freshnessInfo.lastUpdated)}</span>
            </div>
          )}
          
          {showNextRefresh && nextRefresh && (
            <div className="flex items-center gap-1">
              <RefreshCw className="w-3 h-3" />
              <span>次回更新: {nextRefresh}</span>
            </div>
          )}

          <div className="flex items-center gap-1">
            <span>経過時間: {freshnessInfo.ageMinutes}分</span>
          </div>

          {freshnessInfo.ttlMinutes && (
            <div className="flex items-center gap-1">
              <span>TTL: {freshnessInfo.ttlMinutes}分</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

interface DataTimestampSummaryProps {
  freshnessInfos: DataFreshnessInfo[];
  showDetails?: boolean;
  className?: string;
  onRefreshAll?: () => void;
}

export function DataTimestampSummary({
  freshnessInfos,
  showDetails = false,
  className = '',
  onRefreshAll,
}: DataTimestampSummaryProps) {
  const [currentTime, setCurrentTime] = useState(new Date());

  // 自動更新
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTime(new Date());
    }, 60000);

    return () => clearInterval(interval);
  }, []);

  const combined = freshnessManager.getCombinedFreshnessInfo(freshnessInfos);
  const oldestData = combined.oldestData;
  const newestData = freshnessInfos.reduce((newest, current) => 
    current.ageMinutes < newest.ageMinutes ? current : newest
  );

  return (
    <div className={`space-y-3 ${className}`}>
      {/* サマリー */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Clock className="w-5 h-5 text-gray-500" />
          <span className="font-medium text-gray-700">データ更新状況</span>
        </div>
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

      {/* 統計情報 */}
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div className="space-y-1">
          <div className="text-gray-600">最新データ</div>
          <div className="font-medium">
            {newestData ? freshnessManager.getRelativeTimeString(newestData.ageMinutes) : 'なし'}
          </div>
        </div>
        <div className="space-y-1">
          <div className="text-gray-600">最古データ</div>
          <div className="font-medium">
            {oldestData ? freshnessManager.getRelativeTimeString(oldestData.ageMinutes) : 'なし'}
          </div>
        </div>
      </div>

      {/* 詳細情報 */}
      {showDetails && (
        <div className="space-y-2">
          <div className="text-sm font-medium text-gray-700">個別データ状況</div>
          <div className="space-y-1">
            {freshnessInfos.map((info, index) => (
              <div key={index} className="flex items-center justify-between text-xs bg-gray-50 p-2 rounded">
                <div className="flex items-center gap-2">
                  <span className="font-medium">データ {index + 1}</span>
                  <span className={`px-2 py-0.5 rounded text-xs ${
                    info.isFresh ? 'bg-green-100 text-green-800' :
                    info.cacheStatus === 'stale' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {info.isFresh ? 'Fresh' : info.cacheStatus === 'stale' ? 'Stale' : 'Expired'}
                  </span>
                </div>
                <div className="text-gray-600">
                  {freshnessManager.getRelativeTimeString(info.ageMinutes)}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
