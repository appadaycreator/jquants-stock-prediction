/**
 * パフォーマンス監視コンポーネント
 * リアルタイムでパフォーマンス状況を表示
 */

import React from 'react';
import { usePerformance } from '../hooks/usePerformance';
import { 
  Activity, 
  Zap, 
  Clock, 
  Database, 
  AlertTriangle,
  CheckCircle,
  TrendingUp,
  Cpu
} from 'lucide-react';

interface PerformanceMonitorProps {
  showDetails?: boolean;
  compact?: boolean;
  onOptimize?: () => void;
}

export default function PerformanceMonitor({ 
  showDetails = false, 
  compact = false,
  onOptimize
}: PerformanceMonitorProps) {
  const {
    metrics,
    report,
    isOptimizing,
    optimize,
    getScore,
    getRecommendations,
    getPerformanceStatus,
    isHealthy,
    needsOptimization
  } = usePerformance();

  const score = getScore();
  const recommendations = getRecommendations();
  const status = getPerformanceStatus();

  const formatTime = (ms: number) => {
    if (ms < 1000) return `${Math.round(ms)}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
  };

  const formatMemory = (bytes: number) => {
    if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)}KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)}MB`;
  };

  const getStatusIcon = () => {
    if (isOptimizing) {
      return <Activity className="h-4 w-4 animate-pulse text-blue-500" />;
    }
    if (isHealthy) {
      return <CheckCircle className="h-4 w-4 text-green-500" />;
    }
    if (needsOptimization) {
      return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
    }
    return <Activity className="h-4 w-4 text-gray-500" />;
  };

  if (compact) {
    return (
      <div className="flex items-center space-x-2">
        {getStatusIcon()}
        <span className={`text-sm ${status.color === 'green' ? 'text-green-600' : 
          status.color === 'yellow' ? 'text-yellow-600' : 
          status.color === 'red' ? 'text-red-600' : 'text-gray-600'}`}>
          {score}点
        </span>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border p-4">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Cpu className="h-5 w-5 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">パフォーマンス監視</h3>
        </div>
        <div className="flex items-center space-x-2">
          {getStatusIcon()}
          <span className={`font-medium ${
            status.color === 'green' ? 'text-green-600' : 
            status.color === 'yellow' ? 'text-yellow-600' : 
            status.color === 'red' ? 'text-red-600' : 'text-gray-600'
          }`}>
            {score}点 ({status.status})
          </span>
        </div>
      </div>

      {showDetails && (
        <div className="space-y-4">
          {/* メトリクス表示 */}
          <div className="grid grid-cols-2 gap-4">
            <div className="flex items-center space-x-2">
              <Clock className="h-4 w-4 text-gray-500" />
              <div>
                <div className="text-sm text-gray-600">読み込み時間</div>
                <div className="text-sm font-medium">{formatTime(metrics.loadTime)}</div>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <Zap className="h-4 w-4 text-gray-500" />
              <div>
                <div className="text-sm text-gray-600">レンダリング時間</div>
                <div className="text-sm font-medium">{formatTime(metrics.renderTime)}</div>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <Database className="h-4 w-4 text-gray-500" />
              <div>
                <div className="text-sm text-gray-600">メモリ使用量</div>
                <div className="text-sm font-medium">{formatMemory(metrics.memoryUsage)}</div>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <TrendingUp className="h-4 w-4 text-gray-500" />
              <div>
                <div className="text-sm text-gray-600">ネットワークリクエスト</div>
                <div className="text-sm font-medium">{metrics.networkRequests}件</div>
              </div>
            </div>
          </div>

          {/* 推奨事項 */}
          {recommendations.length > 0 && (
            <div className="border-t pt-4">
              <h4 className="text-sm font-medium text-gray-900 mb-2">推奨事項</h4>
              <div className="space-y-2">
                {recommendations.map((recommendation, index) => (
                  <div key={index} className="text-xs text-yellow-600 bg-yellow-50 p-2 rounded">
                    {recommendation}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* パフォーマンススコア */}
          <div className="border-t pt-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-900">パフォーマンススコア</span>
              <span className={`text-sm font-bold ${
                score >= 90 ? 'text-green-600' : 
                score >= 70 ? 'text-blue-600' : 
                score >= 50 ? 'text-yellow-600' : 'text-red-600'
              }`}>
                {score}点
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className={`h-2 rounded-full transition-all duration-300 ${
                  score >= 90 ? 'bg-green-500' : 
                  score >= 70 ? 'bg-blue-500' : 
                  score >= 50 ? 'bg-yellow-500' : 'bg-red-500'
                }`}
                style={{ width: `${score}%` }}
              />
            </div>
          </div>
        </div>
      )}

      <div className="flex items-center justify-between mt-4 pt-3 border-t">
        <button
          onClick={() => {
            optimize();
            onOptimize?.();
          }}
          disabled={isOptimizing}
          className="flex items-center space-x-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Activity className={`h-4 w-4 ${isOptimizing ? 'animate-spin' : ''}`} />
          <span>{isOptimizing ? '最適化中...' : '最適化実行'}</span>
        </button>
        
        <div className="text-xs text-gray-500">
          スコア: {score}点
        </div>
      </div>
    </div>
  );
}
