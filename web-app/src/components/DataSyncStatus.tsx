/**
 * データ同期状況表示コンポーネント
 */

import React from 'react';
import { useDataSync } from '../hooks/useDataSync';
import { 
  CheckCircle, 
  AlertCircle, 
  RefreshCw, 
  Clock, 
  Database,
  Activity
} from 'lucide-react';

interface DataSyncStatusProps {
  showDetails?: boolean;
  compact?: boolean;
}

export default function DataSyncStatus({ 
  showDetails = false, 
  compact = false 
}: DataSyncStatusProps) {
  const {
    status,
    isLoading,
    error,
    performSync,
    isHealthy,
    hasErrors,
    lastUpdate
  } = useDataSync();

  const getStatusIcon = () => {
    if (isLoading) {
      return <RefreshCw className="h-4 w-4 animate-spin text-blue-500" />;
    }
    if (isHealthy) {
      return <CheckCircle className="h-4 w-4 text-green-500" />;
    }
    if (hasErrors) {
      return <AlertCircle className="h-4 w-4 text-red-500" />;
    }
    return <Clock className="h-4 w-4 text-gray-500" />;
  };

  const getStatusText = () => {
    if (isLoading) return '同期中...';
    if (isHealthy) return '正常';
    if (hasErrors) return 'エラー';
    return '待機中';
  };

  const getStatusColor = () => {
    if (isLoading) return 'text-blue-600';
    if (isHealthy) return 'text-green-600';
    if (hasErrors) return 'text-red-600';
    return 'text-gray-600';
  };

  const formatLastUpdate = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    
    if (diff < 60000) return '1分以内';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}分前`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}時間前`;
    return date.toLocaleString('ja-JP');
  };

  if (compact) {
    return (
      <div className="flex items-center space-x-2">
        {getStatusIcon()}
        <span className={`text-sm ${getStatusColor()}`}>
          {getStatusText()}
        </span>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border p-4">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Database className="h-5 w-5 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">データ同期状況</h3>
        </div>
        <div className="flex items-center space-x-2">
          {getStatusIcon()}
          <span className={`font-medium ${getStatusColor()}`}>
            {getStatusText()}
          </span>
        </div>
      </div>

      {showDetails && (
        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-4">
            <div className="flex items-center space-x-2">
              <Activity className="h-4 w-4 text-gray-500" />
              <span className="text-sm text-gray-600">最終更新:</span>
              <span className="text-sm font-medium">
                {formatLastUpdate(lastUpdate)}
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <Clock className="h-4 w-4 text-gray-500" />
              <span className="text-sm text-gray-600">ステータス:</span>
              <span className={`text-sm font-medium ${getStatusColor()}`}>
                {status.status}
              </span>
            </div>
          </div>

          <div className="border-t pt-3">
            <h4 className="text-sm font-medium text-gray-900 mb-2">データソース</h4>
            <div className="grid grid-cols-2 gap-2">
              {Object.entries(status.dataSources).map(([source, isHealthy]) => (
                <div key={source} className="flex items-center space-x-2">
                  {isHealthy ? (
                    <CheckCircle className="h-3 w-3 text-green-500" />
                  ) : (
                    <AlertCircle className="h-3 w-3 text-red-500" />
                  )}
                  <span className="text-xs text-gray-600 capitalize">
                    {source.replace(/([A-Z])/g, ' $1').trim()}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {hasErrors && (
            <div className="border-t pt-3">
              <h4 className="text-sm font-medium text-red-600 mb-2">エラー</h4>
              <div className="space-y-1">
                {status.errors.map((error, index) => (
                  <div key={index} className="text-xs text-red-600 bg-red-50 p-2 rounded">
                    {error}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      <div className="flex items-center justify-between mt-4 pt-3 border-t">
        <button
          onClick={performSync}
          disabled={isLoading}
          className="flex items-center space-x-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
          <span>手動同期</span>
        </button>
        
        <div className="text-xs text-gray-500">
          最終更新: {formatLastUpdate(lastUpdate)}
        </div>
      </div>
    </div>
  );
}
