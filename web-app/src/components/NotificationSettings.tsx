"use client";

import React, { useState, useEffect } from "react";
import { Bell, Mail, MessageSquare, Settings, Save, TestTube, Clock, AlertCircle } from "lucide-react";

interface NotificationConfig {
  email: {
    enabled: boolean;
    smtp_server: string;
    smtp_port: number;
    email_user: string;
    email_password: string;
    email_to: string;
  };
  slack: {
    enabled: boolean;
    webhook_url: string;
    channel: string;
    username: string;
    icon_emoji: string;
  };
  schedule: {
    morning_analysis: string;
    evening_analysis: string;
    timezone: string;
  };
  content: {
    include_analysis_summary: boolean;
    include_performance_metrics: boolean;
    include_recommendations: boolean;
    include_risk_alerts: boolean;
  };
  filters: {
    min_confidence_threshold: number;
    include_errors: boolean;
    include_success: boolean;
  };
  rate_limiting: {
    max_notifications_per_hour: number;
    cooldown_minutes: number;
  };
}

export default function NotificationSettings() {
  const [config, setConfig] = useState<NotificationConfig>({
    email: {
      enabled: false,
      smtp_server: "smtp.gmail.com",
      smtp_port: 587,
      email_user: "",
      email_password: "",
      email_to: ""
    },
    slack: {
      enabled: false,
      webhook_url: "",
      channel: "#stock-analysis",
      username: "株価分析Bot",
      icon_emoji: ":chart_with_upwards_trend:"
    },
    schedule: {
      morning_analysis: "09:00",
      evening_analysis: "15:00",
      timezone: "Asia/Tokyo"
    },
    content: {
      include_analysis_summary: true,
      include_performance_metrics: true,
      include_recommendations: true,
      include_risk_alerts: true
    },
    filters: {
      min_confidence_threshold: 0.7,
      include_errors: true,
      include_success: true
    },
    rate_limiting: {
      max_notifications_per_hour: 5,
      cooldown_minutes: 30
    }
  });

  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [testResult, setTestResult] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'email' | 'slack' | 'schedule' | 'content'>('email');

  // 設定の読み込み
  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      // ローカルストレージから設定を読み込み
      const savedConfig = localStorage.getItem('notification-config');
      if (savedConfig) {
        const data = JSON.parse(savedConfig);
        setConfig(data);
      }
    } catch (error) {
      console.error('設定読み込みエラー:', error);
    }
  };

  // 設定の保存
  const saveConfig = async () => {
    setIsSaving(true);
    try {
      // ローカルストレージに設定を保存
      localStorage.setItem('notification-config', JSON.stringify(config));
      setTestResult('設定を保存しました');
      setTimeout(() => setTestResult(null), 3000);
    } catch (error) {
      setTestResult('設定の保存に失敗しました');
    } finally {
      setIsSaving(false);
    }
  };

  // 通知テスト
  const testNotification = async (type: 'email' | 'slack') => {
    setIsLoading(true);
    try {
      // クライアントサイドでのテスト（実際の送信は行わない）
      setTestResult(`${type === 'email' ? 'メール' : 'Slack'}通知の設定が保存されました（テスト機能は静的サイトでは利用できません）`);
    } catch (error) {
      setTestResult(`${type === 'email' ? 'メール' : 'Slack'}通知のテストに失敗しました`);
    } finally {
      setIsLoading(false);
    }
  };

  const updateConfig = (path: string, value: any) => {
    setConfig(prev => {
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

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
          <Bell className="w-6 h-6 text-blue-600" />
          通知設定
        </h2>
        <div className="flex gap-2">
          <button
            onClick={saveConfig}
            disabled={isSaving}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 flex items-center gap-2"
          >
            <Save className="w-4 h-4" />
            {isSaving ? '保存中...' : '保存'}
          </button>
        </div>
      </div>

      {/* タブナビゲーション */}
      <div className="flex border-b border-gray-200 mb-6">
        {[
          { id: 'email', label: 'メール通知', icon: Mail },
          { id: 'slack', label: 'Slack通知', icon: MessageSquare },
          { id: 'schedule', label: 'スケジュール', icon: Clock },
          { id: 'content', label: '通知内容', icon: Settings }
        ].map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id as any)}
            className={`flex items-center gap-2 px-4 py-2 border-b-2 transition-colors ${
              activeTab === id
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-800'
            }`}
          >
            <Icon className="w-4 h-4" />
            {label}
          </button>
        ))}
      </div>

      {/* メール通知設定 */}
      {activeTab === 'email' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-800">メール通知設定</h3>
            <div className="flex items-center gap-2">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={config.email.enabled}
                  onChange={(e) => updateConfig('email.enabled', e.target.checked)}
                  className="rounded"
                />
                メール通知を有効にする
              </label>
              <button
                onClick={() => testNotification('email')}
                disabled={!config.email.enabled || isLoading}
                className="px-3 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700 disabled:bg-gray-400 flex items-center gap-1"
              >
                <TestTube className="w-3 h-3" />
                テスト
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">SMTPサーバー</label>
              <input
                type="text"
                value={config.email.smtp_server}
                onChange={(e) => updateConfig('email.smtp_server', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="smtp.gmail.com"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">SMTPポート</label>
              <input
                type="number"
                value={config.email.smtp_port}
                onChange={(e) => updateConfig('email.smtp_port', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="587"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">送信者メールアドレス</label>
              <input
                type="email"
                value={config.email.email_user}
                onChange={(e) => updateConfig('email.email_user', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="your-email@gmail.com"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">アプリパスワード</label>
              <input
                type="password"
                value={config.email.email_password}
                onChange={(e) => updateConfig('email.email_password', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Gmailアプリパスワード"
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">受信者メールアドレス</label>
              <input
                type="email"
                value={config.email.email_to}
                onChange={(e) => updateConfig('email.email_to', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="recipient@example.com"
              />
            </div>
          </div>
        </div>
      )}

      {/* Slack通知設定 */}
      {activeTab === 'slack' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-800">Slack通知設定</h3>
            <div className="flex items-center gap-2">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={config.slack.enabled}
                  onChange={(e) => updateConfig('slack.enabled', e.target.checked)}
                  className="rounded"
                />
                Slack通知を有効にする
              </label>
              <button
                onClick={() => testNotification('slack')}
                disabled={!config.slack.enabled || isLoading}
                className="px-3 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700 disabled:bg-gray-400 flex items-center gap-1"
              >
                <TestTube className="w-3 h-3" />
                テスト
              </button>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Webhook URL</label>
              <input
                type="url"
                value={config.slack.webhook_url}
                onChange={(e) => updateConfig('slack.webhook_url', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="https://hooks.slack.com/services/..."
              />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">チャンネル</label>
                <input
                  type="text"
                  value={config.slack.channel}
                  onChange={(e) => updateConfig('slack.channel', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="#stock-analysis"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">ユーザー名</label>
                <input
                  type="text"
                  value={config.slack.username}
                  onChange={(e) => updateConfig('slack.username', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="株価分析Bot"
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* スケジュール設定 */}
      {activeTab === 'schedule' && (
        <div className="space-y-6">
          <h3 className="text-lg font-semibold text-gray-800">スケジュール設定</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">朝の分析実行時間</label>
              <input
                type="time"
                value={config.schedule.morning_analysis}
                onChange={(e) => updateConfig('schedule.morning_analysis', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">夕方の分析実行時間</label>
              <input
                type="time"
                value={config.schedule.evening_analysis}
                onChange={(e) => updateConfig('schedule.evening_analysis', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">タイムゾーン</label>
              <select
                value={config.schedule.timezone}
                onChange={(e) => updateConfig('schedule.timezone', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="Asia/Tokyo">Asia/Tokyo (JST)</option>
                <option value="UTC">UTC</option>
                <option value="America/New_York">America/New_York (EST)</option>
              </select>
            </div>
          </div>
        </div>
      )}

      {/* 通知内容設定 */}
      {activeTab === 'content' && (
        <div className="space-y-6">
          <h3 className="text-lg font-semibold text-gray-800">通知内容設定</h3>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-gray-700">分析サマリーを含める</label>
              <input
                type="checkbox"
                checked={config.content.include_analysis_summary}
                onChange={(e) => updateConfig('content.include_analysis_summary', e.target.checked)}
                className="rounded"
              />
            </div>
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-gray-700">パフォーマンス指標を含める</label>
              <input
                type="checkbox"
                checked={config.content.include_performance_metrics}
                onChange={(e) => updateConfig('content.include_performance_metrics', e.target.checked)}
                className="rounded"
              />
            </div>
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-gray-700">推奨事項を含める</label>
              <input
                type="checkbox"
                checked={config.content.include_recommendations}
                onChange={(e) => updateConfig('content.include_recommendations', e.target.checked)}
                className="rounded"
              />
            </div>
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-gray-700">リスクアラートを含める</label>
              <input
                type="checkbox"
                checked={config.content.include_risk_alerts}
                onChange={(e) => updateConfig('content.include_risk_alerts', e.target.checked)}
                className="rounded"
              />
            </div>
          </div>

          <div className="border-t pt-4">
            <h4 className="text-md font-semibold text-gray-800 mb-3">フィルタリング設定</h4>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  最小信頼度閾値: {config.filters.min_confidence_threshold}
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={config.filters.min_confidence_threshold}
                  onChange={(e) => updateConfig('filters.min_confidence_threshold', parseFloat(e.target.value))}
                  className="w-full"
                />
              </div>
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium text-gray-700">エラー通知を含める</label>
                <input
                  type="checkbox"
                  checked={config.filters.include_errors}
                  onChange={(e) => updateConfig('filters.include_errors', e.target.checked)}
                  className="rounded"
                />
              </div>
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium text-gray-700">成功通知を含める</label>
                <input
                  type="checkbox"
                  checked={config.filters.include_success}
                  onChange={(e) => updateConfig('filters.include_success', e.target.checked)}
                  className="rounded"
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* テスト結果表示 */}
      {testResult && (
        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center gap-2 text-blue-800">
            <AlertCircle className="w-4 h-4" />
            <span className="text-sm">{testResult}</span>
          </div>
        </div>
      )}
    </div>
  );
}
