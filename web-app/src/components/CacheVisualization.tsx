"use client";

import React, { useState, useEffect } from 'react';
import { DataFreshnessInfo, freshnessManager } from '@/lib/data-freshness-manager';
import { Database, HardDrive, Wifi, AlertTriangle, CheckCircle, Clock, RefreshCw } from 'lucide-react';

interface CacheVisualizationProps {
  freshnessInfos: DataFreshnessInfo[];
  showDetails?: boolean;
  className?: string;
  onRefresh?: (key: string) => void;
  onRefreshAll?: () => void;
}

export default function CacheVisualization({
  freshnessInfos,
  showDetails = true,
  className = '',
  onRefresh,
  onRefreshAll,
}: CacheVisualizationProps) {
  const [currentTime, setCurrentTime] = useState(new Date());

  // 自動更新
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTime(new Date());
    }, 30000); // 30秒ごと

    return () => clearInterval(interval);
  }, []);

  const getCacheStatusColor = (status: DataFreshnessInfo['cacheStatus']) => {
    switch (status) {
      case 'fresh':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'stale':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'expired':
        return 'text-red-600 bg-red-50 border-red-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getSourceIcon = (source: DataFreshnessInfo['source']) => {
    switch (source) {
      case 'api':
        return <Wifi className="w-4 h-4" />;
      case 'cache':
        return <Database className="w-4 h-4" />;
      case 'fallback':
        return <AlertTriangle className="w-4 h-4" />;
      default:
        return <HardDrive className="w-4 h-4" />;
    }
  };

  const getSourceColor = (source: DataFreshnessInfo['source']) => {
    switch (source) {
      case 'api':
        return 'text-blue-600';
      case 'cache':
        return 'text-green-600';
      case 'fallback':
        return 'text-orange-600';
      default:
        return 'text-gray-600';
    }
  };

  const combined = freshnessManager.getCombinedFreshnessInfo(freshnessInfos);

  return (
    <div className={`space-y-4 ${className}`}>
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Database className="w-5 h-5 text-gray-500" />
          <span className="font-medium text-gray-700">キャッシュ状態</span>
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

      {/* サマリー統計 */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="bg-green-50 border border-green-200 rounded-lg p-3">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-green-600" />
            <span className="text-sm font-medium text-green-800">Fresh</span>
          </div>
          <div className="text-2xl font-bold text-green-600 mt-1">
            {combined.freshCount}
          </div>
        </div>

        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-yellow-600" />
            <span className="text-sm font-medium text-yellow-800">Stale</span>
          </div>
          <div className="text-2xl font-bold text-yellow-600 mt-1">
            {combined.staleCount}
          </div>
        </div>

        <div className="bg-red-50 border border-red-200 rounded-lg p-3">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-red-600" />
            <span className="text-sm font-medium text-red-800">Expired</span>
          </div>
          <div className="text-2xl font-bold text-red-600 mt-1">
            {combined.expiredCount}
          </div>
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
          <div className="flex items-center gap-2">
            <Database className="w-4 h-4 text-blue-600" />
            <span className="text-sm font-medium text-blue-800">Total</span>
          </div>
          <div className="text-2xl font-bold text-blue-600 mt-1">
            {combined.totalCount}
          </div>
        </div>
      </div>

      {/* 詳細リスト */}
      {showDetails && (
        <div className="space-y-2">
          <div className="text-sm font-medium text-gray-700">個別キャッシュ状況</div>
          <div className="space-y-2">
            {freshnessInfos.map((info, index) => (
              <div
                key={index}
                className={`border rounded-lg p-3 ${getCacheStatusColor(info.cacheStatus)}`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="flex items-center gap-1">
                      {getSourceIcon(info.source)}
                      <span className="text-sm font-medium">
                        データ {index + 1}
                      </span>
                    </div>
                    
                    <div className="flex items-center gap-1">
                      <span className="text-xs px-2 py-1 rounded-full bg-white">
                        {info.isFresh ? 'Fresh' : info.cacheStatus === 'stale' ? 'Stale' : 'Expired'}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <div className="text-sm text-gray-600">
                      {freshnessManager.getRelativeTimeString(info.ageMinutes)}
                    </div>
                    {onRefresh && (
                      <button
                        onClick={() => onRefresh(`data_${index}`)}
                        className="p-1 rounded hover:bg-white/50 transition-colors"
                        title="このデータを更新"
                      >
                        <RefreshCw className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                </div>

                <div className="mt-2 grid grid-cols-2 gap-2 text-xs">
                  <div className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    <span>更新: {info.lastUpdated.toLocaleTimeString('ja-JP')}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    {getSourceIcon(info.source)}
                    <span className={getSourceColor(info.source)}>
                      {info.source === 'api' ? 'API' : 
                       info.source === 'cache' ? 'キャッシュ' : 'フォールバック'}
                    </span>
                  </div>
                  {info.ttlMinutes && (
                    <div className="flex items-center gap-1">
                      <Database className="w-3 h-3" />
                      <span>TTL: {info.ttlMinutes}分</span>
                    </div>
                  )}
                  {info.nextRefresh && (
                    <div className="flex items-center gap-1">
                      <RefreshCw className="w-3 h-3" />
                      <span>次回: {freshnessManager.getNextRefreshString(info.nextRefresh)}</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 全体状況 */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Database className="w-4 h-4 text-gray-500" />
            <span className="text-sm font-medium text-gray-700">全体状況</span>
          </div>
          <div className="text-sm text-gray-600">
            {combined.overallStatus === 'all_fresh' ? 'すべて最新' :
             combined.overallStatus === 'mixed' ? '一部古い' :
             combined.overallStatus === 'all_stale' ? 'すべて古い' :
             'すべて期限切れ'}
          </div>
        </div>
        
        {combined.oldestData && (
          <div className="mt-2 text-xs text-gray-600">
            最古データ: {freshnessManager.getRelativeTimeString(combined.oldestData.ageMinutes)}
          </div>
        )}
      </div>
    </div>
  );
}

interface CacheVisualizationCompactProps {
  freshnessInfo: DataFreshnessInfo;
  className?: string;
  onRefresh?: () => void;
}

export function CacheVisualizationCompact({
  freshnessInfo,
  className = '',
  onRefresh,
}: CacheVisualizationCompactProps) {
  const getStatusColor = (status: DataFreshnessInfo['cacheStatus']) => {
    switch (status) {
      case 'fresh':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'stale':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'expired':
        return 'text-red-600 bg-red-50 border-red-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getSourceIcon = (source: DataFreshnessInfo['source']) => {
    switch (source) {
      case 'api':
        return <Wifi className="w-3 h-3" />;
      case 'cache':
        return <Database className="w-3 h-3" />;
      case 'fallback':
        return <AlertTriangle className="w-3 h-3" />;
      default:
        return <HardDrive className="w-3 h-3" />;
    }
  };

  return (
    <div className={`inline-flex items-center gap-2 px-2 py-1 rounded border text-xs ${getStatusColor(freshnessInfo.cacheStatus)} ${className}`}>
      {getSourceIcon(freshnessInfo.source)}
      <span className="font-medium">
        {freshnessInfo.isFresh ? 'Fresh' : freshnessInfo.cacheStatus === 'stale' ? 'Stale' : 'Expired'}
      </span>
      <span className="text-gray-500">
        {freshnessManager.getRelativeTimeString(freshnessInfo.ageMinutes)}
      </span>
      {onRefresh && (
        <button
          onClick={onRefresh}
          className="p-0.5 rounded hover:bg-white/50 transition-colors"
          title="更新"
        >
          <RefreshCw className="w-3 h-3" />
        </button>
      )}
    </div>
  );
}
