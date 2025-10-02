/**
 * データタイムスタンプ表示コンポーネント
 * データの最終更新時刻と相対時間を表示
 */

"use client";

import React, { useState, useEffect } from "react";
import { Clock, RefreshCw, Calendar, TrendingUp } from "lucide-react";

interface DataTimestampDisplayProps {
  lastUpdated: Date | string | number;
  source?: 'api' | 'cache' | 'fallback';
  showRelativeTime?: boolean;
  showAbsoluteTime?: boolean;
  showNextUpdate?: boolean;
  ttlMinutes?: number;
  className?: string;
}

const DataTimestampDisplay: React.FC<DataTimestampDisplayProps> = ({
  lastUpdated,
  source = 'cache',
  showRelativeTime = true,
  showAbsoluteTime = false,
  showNextUpdate = false,
  ttlMinutes = 60,
  className = "",
}) => {
  const [currentTime, setCurrentTime] = useState(new Date());

  // 現在時刻の更新
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const updateTime = new Date(lastUpdated);
  const relativeTime = getRelativeTime(updateTime);
  const absoluteTime = updateTime.toLocaleString('ja-JP');
  const nextUpdate = new Date(updateTime.getTime() + (ttlMinutes * 60 * 1000));

  // 相対時間の取得
  function getRelativeTime(date: Date): string {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMinutes = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMinutes / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMinutes < 1) {
      return 'たった今';
    } else if (diffMinutes < 60) {
      return `${diffMinutes}分前`;
    } else if (diffHours < 24) {
      return `${diffHours}時間前`;
    } else {
      return `${diffDays}日前`;
    }
  }

  // ソースアイコンの取得
  const getSourceIcon = () => {
    switch (source) {
      case 'api':
        return <TrendingUp className="h-4 w-4 text-green-600" />;
      case 'cache':
        return <Clock className="h-4 w-4 text-blue-600" />;
      case 'fallback':
        return <RefreshCw className="h-4 w-4 text-yellow-600" />;
      default:
        return <Clock className="h-4 w-4 text-gray-600" />;
    }
  };

  // ソース色の取得
  const getSourceColor = () => {
    switch (source) {
      case 'api':
        return 'text-green-600';
      case 'cache':
        return 'text-blue-600';
      case 'fallback':
        return 'text-yellow-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div className={`flex items-center space-x-2 ${className}`}>
      {getSourceIcon()}
      
      <div className="flex flex-col">
        {showRelativeTime && (
          <div className="text-sm font-medium text-gray-900 dark:text-white">
            {relativeTime}
          </div>
        )}
        
        {showAbsoluteTime && (
          <div className="text-xs text-gray-500 dark:text-gray-400">
            {absoluteTime}
          </div>
        )}
        
        <div className="flex items-center space-x-1">
          <span className={`text-xs ${getSourceColor()}`}>
            {source.toUpperCase()}
          </span>
          {showNextUpdate && (
            <>
              <span className="text-xs text-gray-400">•</span>
              <span className="text-xs text-gray-500 dark:text-gray-400">
                次回: {getRelativeTime(nextUpdate)}
              </span>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

// サマリー版コンポーネント
export const DataTimestampSummary: React.FC<{
  lastUpdated: Date | string | number;
  source?: 'api' | 'cache' | 'fallback';
  className?: string;
}> = ({ lastUpdated, source = 'cache', className = "" }) => {
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const updateTime = new Date(lastUpdated);
  const relativeTime = getRelativeTime(updateTime);

  function getRelativeTime(date: Date): string {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMinutes = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMinutes / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMinutes < 1) {
      return 'たった今';
    } else if (diffMinutes < 60) {
      return `${diffMinutes}分前`;
    } else if (diffHours < 24) {
      return `${diffHours}時間前`;
    } else {
      return `${diffDays}日前`;
    }
  }

  return (
    <div className={`flex items-center space-x-2 ${className}`}>
      <Clock className="h-4 w-4 text-gray-600" />
      <span className="text-sm text-gray-600 dark:text-gray-400">
        最終更新: {relativeTime}
      </span>
    </div>
  );
};

export default DataTimestampDisplay;