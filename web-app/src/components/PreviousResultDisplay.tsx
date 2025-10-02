/**
 * 前回結果表示コンポーネント
 * データの鮮度表示、自動更新、手動リフレッシュ機能を提供
 */

"use client";

import React, { useState, useEffect } from "react";
import { Clock, RefreshCw, AlertTriangle, CheckCircle, Info } from "lucide-react";

interface PreviousResultDisplayProps {
  data: any;
  timestamp: string | null;
  onRefresh: () => void;
  onDismiss?: () => void;
  title?: string;
  showRefreshButton?: boolean;
  showDataAge?: boolean;
  maxAge?: number; // ミリ秒
}

export default function PreviousResultDisplay({
  data,
  timestamp,
  onRefresh,
  onDismiss,
  title = "前回の結果",
  showRefreshButton = true,
  showDataAge = true,
  maxAge = 24 * 60 * 60 * 1000, // 24時間
}: PreviousResultDisplayProps) {
  const [dataAge, setDataAge] = useState<number | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    if (timestamp) {
      const updateAge = () => {
        const age = Date.now() - new Date(timestamp).getTime();
        setDataAge(age);
      };

      updateAge();
      const interval = setInterval(updateAge, 60000); // 1分ごとに更新
      return () => clearInterval(interval);
    }
  }, [timestamp]);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      await onRefresh();
    } finally {
      setIsRefreshing(false);
    }
  };

  const getDataAgeText = (age: number): string => {
    const minutes = Math.floor(age / (1000 * 60));
    const hours = Math.floor(age / (1000 * 60 * 60));
    const days = Math.floor(age / (1000 * 60 * 60 * 24));

    if (days > 0) {
      return `${days}日前`;
    } else if (hours > 0) {
      return `${hours}時間前`;
    } else if (minutes > 0) {
      return `${minutes}分前`;
    } else {
      return "たった今";
    }
  };

  const getDataAgeColor = (age: number): string => {
    if (age < 60 * 60 * 1000) { // 1時間以内
      return "text-green-600";
    } else if (age < 24 * 60 * 60 * 1000) { // 24時間以内
      return "text-yellow-600";
    } else {
      return "text-red-600";
    }
  };

  const getDataAgeIcon = (age: number) => {
    if (age < 60 * 60 * 1000) { // 1時間以内
      return <CheckCircle className="w-4 h-4 text-green-600" />;
    } else if (age < 24 * 60 * 60 * 1000) { // 24時間以内
      return <Clock className="w-4 h-4 text-yellow-600" />;
    } else {
      return <AlertTriangle className="w-4 h-4 text-red-600" />;
    }
  };

  const isDataStale = dataAge !== null && dataAge > maxAge;

  if (!data) {
    return null;
  }

  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
      <div className="flex items-start justify-between">
        <div className="flex items-center space-x-2">
          <Info className="w-5 h-5 text-blue-600" />
          <div>
            <h3 className="text-sm font-medium text-blue-800">
              {title}
            </h3>
            {showDataAge && dataAge !== null && (
              <div className="flex items-center space-x-2 mt-1">
                {getDataAgeIcon(dataAge)}
                <span className={`text-sm ${getDataAgeColor(dataAge)}`}>
                  {getDataAgeText(dataAge)}
                </span>
                {isDataStale && (
                  <span className="text-xs text-red-600 font-medium">
                    (古いデータ)
                  </span>
                )}
              </div>
            )}
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          {showRefreshButton && (
            <button
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="flex items-center space-x-1 bg-blue-600 text-white px-3 py-1 rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <RefreshCw className={`w-4 h-4 ${isRefreshing ? "animate-spin" : ""}`} />
              <span className="text-sm">
                {isRefreshing ? "更新中..." : "更新"}
              </span>
            </button>
          )}
          
          {onDismiss && (
            <button
              onClick={onDismiss}
              className="text-blue-600 hover:text-blue-800 transition-colors"
            >
              <span className="text-sm">×</span>
            </button>
          )}
        </div>
      </div>
      
      {isDataStale && (
        <div className="mt-3 p-2 bg-yellow-50 border border-yellow-200 rounded">
          <p className="text-sm text-yellow-800">
            このデータは古い可能性があります。最新の情報を取得することをお勧めします。
          </p>
        </div>
      )}
    </div>
  );
}

/**
 * データ鮮度インジケーター
 */
interface DataFreshnessIndicatorProps {
  timestamp: string | null;
  maxAge?: number;
  showIcon?: boolean;
  showText?: boolean;
  className?: string;
}

export function DataFreshnessIndicator({
  timestamp,
  maxAge = 24 * 60 * 60 * 1000,
  showIcon = true,
  showText = true,
  className = "",
}: DataFreshnessIndicatorProps) {
  const [dataAge, setDataAge] = useState<number | null>(null);

  useEffect(() => {
    if (timestamp) {
      const updateAge = () => {
        const age = Date.now() - new Date(timestamp).getTime();
        setDataAge(age);
      };

      updateAge();
      const interval = setInterval(updateAge, 60000); // 1分ごとに更新
      return () => clearInterval(interval);
    }
  }, [timestamp]);

  if (!timestamp || dataAge === null) {
    return null;
  }

  const getFreshnessLevel = (age: number): "fresh" | "stale" | "old" => {
    if (age < 60 * 60 * 1000) { // 1時間以内
      return "fresh";
    } else if (age < maxAge) {
      return "stale";
    } else {
      return "old";
    }
  };

  const getFreshnessColor = (level: "fresh" | "stale" | "old"): string => {
    switch (level) {
      case "fresh":
        return "text-green-600";
      case "stale":
        return "text-yellow-600";
      case "old":
        return "text-red-600";
    }
  };

  const getFreshnessIcon = (level: "fresh" | "stale" | "old") => {
    switch (level) {
      case "fresh":
        return <CheckCircle className="w-4 h-4 text-green-600" />;
      case "stale":
        return <Clock className="w-4 h-4 text-yellow-600" />;
      case "old":
        return <AlertTriangle className="w-4 h-4 text-red-600" />;
    }
  };

  const getFreshnessText = (age: number): string => {
    const minutes = Math.floor(age / (1000 * 60));
    const hours = Math.floor(age / (1000 * 60 * 60));
    const days = Math.floor(age / (1000 * 60 * 60 * 24));

    if (days > 0) {
      return `${days}日前`;
    } else if (hours > 0) {
      return `${hours}時間前`;
    } else if (minutes > 0) {
      return `${minutes}分前`;
    } else {
      return "たった今";
    }
  };

  const level = getFreshnessLevel(dataAge);

  return (
    <div className={`flex items-center space-x-1 ${className}`}>
      {showIcon && getFreshnessIcon(level)}
      {showText && (
        <span className={`text-sm ${getFreshnessColor(level)}`}>
          {getFreshnessText(dataAge)}
        </span>
      )}
    </div>
  );
}
