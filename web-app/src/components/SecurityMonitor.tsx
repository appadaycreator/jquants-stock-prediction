/**
 * セキュリティ監視コンポーネント
 * セキュリティ状況の監視と表示
 */

import React from 'react';
import { useSecurity } from '../hooks/useSecurity';
import { 
  Shield, 
  Lock, 
  AlertTriangle, 
  CheckCircle, 
  Eye, 
  Key,
  Clock,
  User,
  Activity
} from 'lucide-react';

interface SecurityMonitorProps {
  showDetails?: boolean;
  compact?: boolean;
  onSecurityEvent?: (event: string, details: any) => void;
}

export default function SecurityMonitor({ 
  showDetails = false, 
  compact = false,
  onSecurityEvent
}: SecurityMonitorProps) {
  const {
    isSecure,
    sessionValid,
    securityEvents,
    loginAttempts,
    validatePassword,
    checkLoginAttempts,
    createSession,
    validateSession,
    logout,
    encryptData,
    decryptData,
    logSecurityEvent,
    updateSecurityConfig,
    getSecurityConfig,
    getAuditLogs
  } = useSecurity({ onSecurityEvent });

  const getStatusIcon = () => {
    if (isSecure && sessionValid) {
      return <CheckCircle className="h-4 w-4 text-green-500" />;
    }
    if (isSecure && !sessionValid) {
      return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
    }
    return <Shield className="h-4 w-4 text-red-500" />;
  };

  const getStatusText = () => {
    if (isSecure && sessionValid) return 'セキュア';
    if (isSecure && !sessionValid) return 'セッション期限切れ';
    return 'セキュリティ警告';
  };

  const getStatusColor = () => {
    if (isSecure && sessionValid) return 'text-green-600';
    if (isSecure && !sessionValid) return 'text-yellow-600';
    return 'text-red-600';
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
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
          <Shield className="h-5 w-5 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">セキュリティ監視</h3>
        </div>
        <div className="flex items-center space-x-2">
          {getStatusIcon()}
          <span className={`font-medium ${getStatusColor()}`}>
            {getStatusText()}
          </span>
        </div>
      </div>

      {showDetails && (
        <div className="space-y-4">
          {/* セキュリティ状況 */}
          <div className="grid grid-cols-2 gap-4">
            <div className="flex items-center space-x-2">
              <Lock className="h-4 w-4 text-gray-500" />
              <div>
                <div className="text-sm text-gray-600">セッション</div>
                <div className={`text-sm font-medium ${
                  sessionValid ? 'text-green-600' : 'text-red-600'
                }`}>
                  {sessionValid ? '有効' : '無効'}
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <Shield className="h-4 w-4 text-gray-500" />
              <div>
                <div className="text-sm text-gray-600">セキュリティ</div>
                <div className={`text-sm font-medium ${
                  isSecure ? 'text-green-600' : 'text-red-600'
                }`}>
                  {isSecure ? '有効' : '無効'}
                </div>
              </div>
            </div>
          </div>

          {/* セキュリティイベント */}
          {securityEvents.length > 0 && (
            <div className="border-t pt-4">
              <h4 className="text-sm font-medium text-gray-900 mb-2">最近のセキュリティイベント</h4>
              <div className="space-y-2 max-h-40 overflow-y-auto">
                {securityEvents.slice(-5).map((event, index) => (
                  <div key={index} className="text-xs text-gray-600 bg-gray-50 p-2 rounded">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{event.event}</span>
                      <span className="text-gray-500">{formatTimestamp(event.timestamp)}</span>
                    </div>
                    {event.details && Object.keys(event.details).length > 0 && (
                      <div className="mt-1 text-gray-500">
                        {JSON.stringify(event.details, null, 2)}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* ログイン試行状況 */}
          {loginAttempts.size > 0 && (
            <div className="border-t pt-4">
              <h4 className="text-sm font-medium text-gray-900 mb-2">ログイン試行状況</h4>
              <div className="space-y-1">
                {Array.from(loginAttempts.entries()).map(([identifier, remaining]) => (
                  <div key={identifier} className="flex items-center justify-between text-xs">
                    <span className="text-gray-600">{identifier}</span>
                    <span className={`font-medium ${
                      remaining > 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {remaining > 0 ? `${remaining}回残り` : 'ブロック中'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* セキュリティ機能 */}
          <div className="border-t pt-4">
            <h4 className="text-sm font-medium text-gray-900 mb-2">セキュリティ機能</h4>
            <div className="grid grid-cols-2 gap-2">
              <div className="flex items-center space-x-2">
                <Key className="h-3 w-3 text-blue-500" />
                <span className="text-xs text-gray-600">暗号化</span>
              </div>
              
              <div className="flex items-center space-x-2">
                <Lock className="h-3 w-3 text-green-500" />
                <span className="text-xs text-gray-600">セッション管理</span>
              </div>
              
              <div className="flex items-center space-x-2">
                <Eye className="h-3 w-3 text-purple-500" />
                <span className="text-xs text-gray-600">監査ログ</span>
              </div>
              
              <div className="flex items-center space-x-2">
                <Activity className="h-3 w-3 text-orange-500" />
                <span className="text-xs text-gray-600">リアルタイム監視</span>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="flex items-center justify-between mt-4 pt-3 border-t">
        <div className="space-x-2">
          <button
            onClick={() => {
              logSecurityEvent('security_check', { timestamp: new Date().toISOString() });
            }}
            className="px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
          >
            セキュリティチェック
          </button>
          
          <button
            onClick={() => {
              logout();
            }}
            className="px-3 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm"
          >
            ログアウト
          </button>
        </div>
        
        <div className="text-xs text-gray-500">
          {sessionValid ? 'セッション有効' : 'セッション無効'}
        </div>
      </div>
    </div>
  );
}
