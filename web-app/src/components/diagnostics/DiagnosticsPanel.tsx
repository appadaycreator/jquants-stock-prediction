'use client';

import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  Clock, 
  Database, 
  Wifi, 
  WifiOff, 
  AlertTriangle,
  CheckCircle,
  XCircle,
  RefreshCw,
  Settings
} from 'lucide-react';

interface DiagnosticsData {
  lastSuccessTime: number | null;
  apiRemainingCalls: number | null;
  tokenExpirationTime: number | null;
  networkStatus: 'online' | 'offline';
  errorCount: number;
  successCount: number;
  averageResponseTime: number | null;
  lastError: string | null;
  systemStatus: 'healthy' | 'degraded' | 'critical';
}

interface DiagnosticsPanelProps {
  isOpen: boolean;
  onClose: () => void;
  onRefresh: () => void;
  onGoToSettings: () => void;
}

export function DiagnosticsPanel({ 
  isOpen, 
  onClose, 
  onRefresh, 
  onGoToSettings 
}: DiagnosticsPanelProps) {
  const [diagnostics, setDiagnostics] = useState<DiagnosticsData>({
    lastSuccessTime: null,
    apiRemainingCalls: null,
    tokenExpirationTime: null,
    networkStatus: navigator.onLine ? 'online' : 'offline',
    errorCount: 0,
    successCount: 0,
    averageResponseTime: null,
    lastError: null,
    systemStatus: 'healthy'
  });

  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    if (!isOpen) return;

    const updateDiagnostics = async () => {
      try {
        // 認証状態の取得
        const authResponse = await fetch('/api/auth/status');
        const authData = authResponse.ok ? await authResponse.json() : null;

        // システム状態の取得
        const healthResponse = await fetch('/api/health');
        const healthData = healthResponse.ok ? await healthResponse.json() : null;

        setDiagnostics(prev => ({
          ...prev,
          lastSuccessTime: Date.now(),
          apiRemainingCalls: authData?.remainingCalls || null,
          tokenExpirationTime: authData?.tokenExpiration || null,
          networkStatus: navigator.onLine ? 'online' : 'offline',
          systemStatus: healthData?.status === 'ok' ? 'healthy' : 'degraded'
        }));
      } catch (error) {
        setDiagnostics(prev => ({
          ...prev,
          lastError: error instanceof Error ? error.message : 'Unknown error',
          systemStatus: 'critical'
        }));
      }
    };

    updateDiagnostics();
    const interval = setInterval(updateDiagnostics, 30000); // 30秒ごと

    return () => clearInterval(interval);
  }, [isOpen]);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      await onRefresh();
      setDiagnostics(prev => ({
        ...prev,
        lastSuccessTime: Date.now(),
        errorCount: 0,
        lastError: null,
        systemStatus: 'healthy'
      }));
    } catch (error) {
      setDiagnostics(prev => ({
        ...prev,
        errorCount: prev.errorCount + 1,
        lastError: error instanceof Error ? error.message : 'Unknown error',
        systemStatus: 'critical'
      }));
    } finally {
      setIsRefreshing(false);
    }
  };

  const formatTime = (timestamp: number | null) => {
    if (!timestamp) return '未取得';
    const date = new Date(timestamp);
    return date.toLocaleString('ja-JP');
  };

  const formatTimeRemaining = (timestamp: number | null) => {
    if (!timestamp) return '不明';
    const now = Date.now();
    const remaining = timestamp - now;
    
    if (remaining <= 0) return '期限切れ';
    
    const hours = Math.floor(remaining / (1000 * 60 * 60));
    const minutes = Math.floor((remaining % (1000 * 60 * 60)) / (1000 * 60));
    
    if (hours > 0) {
      return `${hours}時間${minutes}分`;
    } else {
      return `${minutes}分`;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'degraded':
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      case 'critical':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Activity className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'healthy':
        return '正常';
      case 'degraded':
        return '一部機能制限';
      case 'critical':
        return '重大な問題';
      default:
        return '不明';
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900">
              システム診断
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <XCircle className="w-6 h-6" />
            </button>
          </div>

          <div className="space-y-6">
            {/* システム状態 */}
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-medium text-gray-900">システム状態</h3>
                {getStatusIcon(diagnostics.systemStatus)}
              </div>
              <p className="text-sm text-gray-600">
                {getStatusText(diagnostics.systemStatus)}
              </p>
            </div>

            {/* ネットワーク状態 */}
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-medium text-gray-900">ネットワーク</h3>
                {diagnostics.networkStatus === 'online' ? (
                  <Wifi className="w-5 h-5 text-green-500" />
                ) : (
                  <WifiOff className="w-5 h-5 text-red-500" />
                )}
              </div>
              <p className="text-sm text-gray-600">
                {diagnostics.networkStatus === 'online' ? 'オンライン' : 'オフライン'}
              </p>
            </div>

            {/* 最後の成功取得 */}
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-medium text-gray-900">最後の成功取得</h3>
                <Clock className="w-5 h-5 text-blue-500" />
              </div>
              <p className="text-sm text-gray-600">
                {formatTime(diagnostics.lastSuccessTime)}
              </p>
            </div>

            {/* API残呼数 */}
            {diagnostics.apiRemainingCalls !== null && (
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-lg font-medium text-gray-900">API残呼数</h3>
                  <Database className="w-5 h-5 text-blue-500" />
                </div>
                <p className="text-sm text-gray-600">
                  {diagnostics.apiRemainingCalls} 回
                </p>
              </div>
            )}

            {/* トークン期限 */}
            {diagnostics.tokenExpirationTime && (
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-lg font-medium text-gray-900">トークン期限</h3>
                  <Clock className="w-5 h-5 text-orange-500" />
                </div>
                <p className="text-sm text-gray-600">
                  残り: {formatTimeRemaining(diagnostics.tokenExpirationTime)}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  期限: {formatTime(diagnostics.tokenExpirationTime)}
                </p>
              </div>
            )}

            {/* 統計情報 */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="text-lg font-medium text-gray-900 mb-3">統計情報</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">成功回数</p>
                  <p className="text-lg font-semibold text-green-600">
                    {diagnostics.successCount}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">エラー回数</p>
                  <p className="text-lg font-semibold text-red-600">
                    {diagnostics.errorCount}
                  </p>
                </div>
              </div>
              {diagnostics.averageResponseTime && (
                <div className="mt-3">
                  <p className="text-sm text-gray-600">平均応答時間</p>
                  <p className="text-lg font-semibold text-blue-600">
                    {diagnostics.averageResponseTime.toFixed(0)}ms
                  </p>
                </div>
              )}
            </div>

            {/* 最後のエラー */}
            {diagnostics.lastError && (
              <div className="bg-red-50 rounded-lg p-4">
                <h3 className="text-lg font-medium text-red-900 mb-3">最後のエラー</h3>
                <p className="text-sm text-red-600 break-words">
                  {diagnostics.lastError}
                </p>
              </div>
            )}
          </div>

          {/* アクションボタン */}
          <div className="mt-6 flex space-x-3">
            <button
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="flex-1 flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {isRefreshing ? (
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <RefreshCw className="w-4 h-4 mr-2" />
              )}
              更新
            </button>
            <button
              onClick={onGoToSettings}
              className="flex-1 flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <Settings className="w-4 h-4 mr-2" />
              設定
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
