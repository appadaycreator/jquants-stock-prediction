import React, { useState, useEffect, useCallback } from "react";
import { 
  Play, 
  Pause, 
  Settings, 
  Bell, 
  CheckCircle, 
  AlertCircle,
  Clock,
  TrendingUp,
  Smartphone,
  Mail,
  MessageSquare,
} from "lucide-react";

interface AutomatedRoutineMobileProps {
  onRoutineStart?: () => void;
  onRoutineComplete?: (result: any) => void;
  onRoutineError?: (error: any) => void;
  className?: string;
}

interface RoutineStatus {
  isRunning: boolean;
  lastExecution: string | null;
  executionCount: number;
  errorCount: number;
  executionTime: string;
  notifications: {
    email_enabled: boolean;
    slack_enabled: boolean;
    browser_enabled: boolean;
  };
}

export default function AutomatedRoutineMobile({
  onRoutineStart,
  onRoutineComplete,
  onRoutineError,
  className = "",
}: AutomatedRoutineMobileProps) {
  const [status, setStatus] = useState<RoutineStatus | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [notifications, setNotifications] = useState<any[]>([]);
  const [settings, setSettings] = useState({
    execution_time: "09:00",
    email_enabled: false,
    slack_enabled: false,
    browser_enabled: true,
  });

  // ステータス取得
  const fetchStatus = useCallback(async () => {
    try {
      const response = await fetch("/api/scheduler/status");
      if (response.ok) {
        const data = await response.json();
        setStatus(data);
      }
    } catch (error) {
      console.error("ステータス取得エラー:", error);
    }
  }, []);

  // 通知取得
  const fetchNotifications = useCallback(async () => {
    try {
      const response = await fetch("/api/notifications");
      if (response.ok) {
        const data = await response.json();
        setNotifications(data.notifications || []);
      }
    } catch (error) {
      console.error("通知取得エラー:", error);
    }
  }, []);

  // 手動実行
  const handleManualExecute = async () => {
    setIsLoading(true);
    try {
      const response = await fetch("/api/scheduler/manual-execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      
      if (response.ok) {
        const result = await response.json();
        onRoutineComplete?.(result);
        await fetchStatus();
      } else {
        throw new Error("手動実行に失敗しました");
      }
    } catch (error) {
      onRoutineError?.(error);
    } finally {
      setIsLoading(false);
    }
  };

  // 設定更新
  const handleSettingsUpdate = async (newSettings: any) => {
    try {
      const response = await fetch("/api/scheduler/settings", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newSettings),
      });
      
      if (response.ok) {
        setSettings(newSettings);
        await fetchStatus();
      }
    } catch (error) {
      console.error("設定更新エラー:", error);
    }
  };

  // 初期化
  useEffect(() => {
    fetchStatus();
    fetchNotifications();
  }, [fetchStatus, fetchNotifications]);

  // 自動更新
  useEffect(() => {
    const interval = setInterval(() => {
      fetchStatus();
      fetchNotifications();
    }, 30000); // 30秒ごと

    return () => clearInterval(interval);
  }, [fetchStatus, fetchNotifications]);

  return (
    <div className={`automated-routine-mobile ${className}`}>
      {/* ヘッダー */}
      <div className="mobile-header bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4 rounded-t-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Smartphone className="w-6 h-6" />
            <h1 className="text-lg font-bold">5分ルーティン自動化</h1>
          </div>
          <Settings className="w-6 h-6" />
        </div>
        <p className="text-sm opacity-90 mt-1">
          完全自動化された投資分析システム
        </p>
      </div>

      {/* ステータス表示 */}
      {status && (
        <div className="p-4 bg-gray-50">
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="bg-white p-3 rounded-lg shadow-sm">
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-5 h-5 text-green-500" />
                <span className="text-sm font-medium">実行回数</span>
              </div>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {status.executionCount}
              </p>
            </div>
            
            <div className="bg-white p-3 rounded-lg shadow-sm">
              <div className="flex items-center space-x-2">
                <AlertCircle className="w-5 h-5 text-red-500" />
                <span className="text-sm font-medium">エラー回数</span>
              </div>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {status.errorCount}
              </p>
            </div>
          </div>

          <div className="bg-white p-3 rounded-lg shadow-sm">
            <div className="flex items-center space-x-2 mb-2">
              <Clock className="w-5 h-5 text-blue-500" />
              <span className="text-sm font-medium">次回実行予定</span>
            </div>
            <p className="text-lg font-semibold text-gray-900">
              明日 {status.executionTime}
            </p>
            {status.lastExecution && (
              <p className="text-sm text-gray-600 mt-1">
                前回実行: {new Date(status.lastExecution).toLocaleString("ja-JP")}
              </p>
            )}
          </div>
        </div>
      )}

      {/* 通知設定 */}
      <div className="p-4">
        <h3 className="text-lg font-semibold mb-3 flex items-center space-x-2">
          <Bell className="w-5 h-5" />
          <span>通知設定</span>
        </h3>
        
        <div className="space-y-3">
          <div className="flex items-center justify-between p-3 bg-white rounded-lg shadow-sm">
            <div className="flex items-center space-x-2">
              <Mail className="w-5 h-5 text-blue-500" />
              <span className="font-medium">メール通知</span>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={settings.email_enabled}
                onChange={(e) => handleSettingsUpdate({
                  ...settings,
                  email_enabled: e.target.checked,
                })}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <div className="flex items-center justify-between p-3 bg-white rounded-lg shadow-sm">
            <div className="flex items-center space-x-2">
              <MessageSquare className="w-5 h-5 text-green-500" />
              <span className="font-medium">Slack通知</span>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={settings.slack_enabled}
                onChange={(e) => handleSettingsUpdate({
                  ...settings,
                  slack_enabled: e.target.checked,
                })}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <div className="flex items-center justify-between p-3 bg-white rounded-lg shadow-sm">
            <div className="flex items-center space-x-2">
              <Smartphone className="w-5 h-5 text-purple-500" />
              <span className="font-medium">ブラウザ通知</span>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={settings.browser_enabled}
                onChange={(e) => handleSettingsUpdate({
                  ...settings,
                  browser_enabled: e.target.checked,
                })}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>
        </div>
      </div>

      {/* 手動実行ボタン */}
      <div className="p-4">
        <button
          onClick={handleManualExecute}
          disabled={isLoading}
          className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-4 px-6 rounded-lg font-semibold text-lg flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              <span>実行中...</span>
            </>
          ) : (
            <>
              <Play className="w-5 h-5" />
              <span>今すぐ実行</span>
            </>
          )}
        </button>
        
        <p className="text-sm text-gray-600 text-center mt-2">
          手動で5分ルーティンを実行します
        </p>
      </div>

      {/* 最近の通知 */}
      {notifications.length > 0 && (
        <div className="p-4">
          <h3 className="text-lg font-semibold mb-3 flex items-center space-x-2">
            <Bell className="w-5 h-5" />
            <span>最近の通知</span>
          </h3>
          
          <div className="space-y-2">
            {notifications.slice(0, 3).map((notification, index) => (
              <div key={index} className="bg-white p-3 rounded-lg shadow-sm border-l-4 border-blue-500">
                <div className="flex items-start space-x-2">
                  <TrendingUp className="w-4 h-4 text-blue-500 mt-1" />
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">
                      {notification.title}
                    </p>
                    <p className="text-xs text-gray-600 mt-1">
                      {new Date(notification.timestamp).toLocaleString("ja-JP")}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* フッター */}
      <div className="p-4 bg-gray-50 rounded-b-lg">
        <div className="text-center">
          <p className="text-sm text-gray-600">
            J-Quants株価予測システム v2.0
          </p>
          <p className="text-xs text-gray-500 mt-1">
            完全自動化された投資分析システム
          </p>
        </div>
      </div>
    </div>
  );
}
