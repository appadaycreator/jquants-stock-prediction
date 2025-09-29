'use client';

import React, { useState, useEffect } from 'react';
import { Bell, Mail, Clock, Settings, Save, TestTube, AlertCircle, CheckCircle } from 'lucide-react';
import { NotificationService, NotificationConfig } from '@/lib/notification/NotificationService';

export default function AutoUpdateSettings() {
  const [config, setConfig] = useState<NotificationConfig | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [testResult, setTestResult] = useState<string | null>(null);
  const [autoUpdateStatus, setAutoUpdateStatus] = useState<'stopped' | 'running' | 'unknown'>('unknown');
  const [notificationService, setNotificationService] = useState<NotificationService | null>(null);

  useEffect(() => {
    const service = NotificationService.getInstance();
    setNotificationService(service);
    loadConfig();
    checkAutoUpdateStatus();
  }, []);

  const loadConfig = async () => {
    if (!notificationService) return;
    
    try {
      const config = await notificationService.loadConfig();
      setConfig(config);
    } catch (error) {
      console.error('設定読み込みエラー:', error);
    }
  };

  const checkAutoUpdateStatus = async () => {
    try {
      // ローカルストレージから自動更新ステータスを確認
      const autoUpdateEnabled = localStorage.getItem('auto-update-enabled');
      setAutoUpdateStatus(autoUpdateEnabled === 'true' ? 'running' : 'stopped');
    } catch (error) {
      console.error('自動更新ステータス確認エラー:', error);
    }
  };

  const saveConfig = async () => {
    if (!config || !notificationService) return;
    
    setIsSaving(true);
    try {
      await notificationService.saveConfig(config);
      setTestResult('設定を保存しました');
      setTimeout(() => setTestResult(null), 3000);
    } catch (error) {
      setTestResult('設定の保存に失敗しました');
    } finally {
      setIsSaving(false);
    }
  };

  const startAutoUpdate = async () => {
    if (!config || !notificationService) return;
    
    setIsLoading(true);
    try {
      await notificationService.startAutoUpdate();
      setAutoUpdateStatus('running');
      setTestResult('自動更新を開始しました');
      setTimeout(() => setTestResult(null), 3000);
    } catch (error) {
      setTestResult('自動更新の開始に失敗しました');
    } finally {
      setIsLoading(false);
    }
  };

  const stopAutoUpdate = async () => {
    if (!notificationService) return;
    
    setIsLoading(true);
    try {
      await notificationService.stopAutoUpdate();
      setAutoUpdateStatus('stopped');
      setTestResult('自動更新を停止しました');
      setTimeout(() => setTestResult(null), 3000);
    } catch (error) {
      setTestResult('自動更新の停止に失敗しました');
    } finally {
      setIsLoading(false);
    }
  };

  const testNotification = async () => {
    if (!notificationService) return;
    
    setIsLoading(true);
    try {
      await notificationService.initializePushNotifications();
      await notificationService.notifyAnalysisComplete({
        buy_candidates: 3,
        sell_candidates: 1,
        warnings: 0
      });
      setTestResult('通知テストを送信しました');
      setTimeout(() => setTestResult(null), 3000);
    } catch (error) {
      setTestResult('通知テストに失敗しました');
    } finally {
      setIsLoading(false);
    }
  };

  const updateConfig = (path: string, value: any) => {
    if (!config) return;
    
    setConfig(prev => {
      if (!prev) return prev;
      const newConfig = { ...prev };
      const keys = path.split('.');
      let current: any = newConfig;
      
      for (let i = 0; i < keys.length - 1; i++) {
        current = current[keys[i]];
      }
      
      current[keys[keys.length - 1]] = value;
      return newConfig;
    });
  };

  if (!config) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center gap-3 mb-6">
        <Settings className="w-6 h-6 text-blue-600" />
        <h2 className="text-xl font-bold text-gray-900">自動更新・通知設定</h2>
      </div>

      {/* ステータス表示 */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-2">
          <Clock className="w-5 h-5 text-gray-600" />
          <span className="font-medium text-gray-900">自動更新ステータス</span>
        </div>
        <div className="flex items-center gap-2">
          {autoUpdateStatus === 'running' ? (
            <>
              <CheckCircle className="w-5 h-5 text-green-600" />
              <span className="text-green-600 font-medium">実行中</span>
            </>
          ) : (
            <>
              <AlertCircle className="w-5 h-5 text-red-600" />
              <span className="text-red-600 font-medium">停止中</span>
            </>
          )}
        </div>
      </div>

      {/* 自動更新コントロール */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">自動更新コントロール</h3>
        <div className="flex gap-3">
          <button
            onClick={startAutoUpdate}
            disabled={isLoading || autoUpdateStatus === 'running'}
            className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            自動更新開始
          </button>
          <button
            onClick={stopAutoUpdate}
            disabled={isLoading || autoUpdateStatus === 'stopped'}
            className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            自動更新停止
          </button>
        </div>
      </div>

      {/* スケジュール設定 */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">スケジュール設定</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              朝の分析時間
            </label>
            <input
              type="time"
              value={config.schedule.morning_analysis}
              onChange={(e) => updateConfig('schedule.morning_analysis', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              夕方の分析時間
            </label>
            <input
              type="time"
              value={config.schedule.evening_analysis}
              onChange={(e) => updateConfig('schedule.evening_analysis', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>
      </div>

      {/* 通知設定 */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">通知設定</h3>
        
        {/* メール通知 */}
        <div className="mb-4">
          <div className="flex items-center gap-2 mb-2">
            <Mail className="w-5 h-5 text-gray-600" />
            <span className="font-medium text-gray-900">メール通知</span>
          </div>
          <div className="flex items-center gap-2 mb-3">
            <input
              type="checkbox"
              checked={config.email.enabled}
              onChange={(e) => updateConfig('email.enabled', e.target.checked)}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">メール通知を有効にする</span>
          </div>
          {config.email.enabled && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <input
                type="email"
                placeholder="送信先メールアドレス"
                value={config.email.email_to}
                onChange={(e) => updateConfig('email.email_to', e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <input
                type="email"
                placeholder="送信者メールアドレス"
                value={config.email.email_user}
                onChange={(e) => updateConfig('email.email_user', e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          )}
        </div>

        {/* プッシュ通知 */}
        <div className="mb-4">
          <div className="flex items-center gap-2 mb-2">
            <Bell className="w-5 h-5 text-gray-600" />
            <span className="font-medium text-gray-900">プッシュ通知</span>
          </div>
          <div className="flex items-center gap-2 mb-3">
            <input
              type="checkbox"
              checked={config.push.enabled}
              onChange={(e) => updateConfig('push.enabled', e.target.checked)}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">プッシュ通知を有効にする</span>
          </div>
        </div>
      </div>

      {/* 通知内容設定 */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">通知内容設定</h3>
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={config.content.include_analysis_summary}
              onChange={(e) => updateConfig('content.include_analysis_summary', e.target.checked)}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">分析サマリーを含める</span>
          </div>
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={config.content.include_recommendations}
              onChange={(e) => updateConfig('content.include_recommendations', e.target.checked)}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">推奨事項を含める</span>
          </div>
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={config.content.include_risk_alerts}
              onChange={(e) => updateConfig('content.include_risk_alerts', e.target.checked)}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">リスク警告を含める</span>
          </div>
        </div>
      </div>

      {/* テスト・保存ボタン */}
      <div className="flex gap-3">
        <button
          onClick={testNotification}
          disabled={isLoading}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
        >
          <TestTube className="w-4 h-4" />
          通知テスト
        </button>
        <button
          onClick={saveConfig}
          disabled={isSaving}
          className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
        >
          <Save className="w-4 h-4" />
          設定保存
        </button>
      </div>

      {/* 結果表示 */}
      {testResult && (
        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-blue-800">{testResult}</p>
        </div>
      )}
    </div>
  );
}
