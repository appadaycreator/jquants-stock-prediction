/**
 * モバイル最適化コンポーネント
 * モバイル環境での最適化機能を提供
 */

import React from 'react';
import { useMobile } from '../hooks/useMobile';
import { 
  Smartphone, 
  Wifi, 
  WifiOff, 
  Download, 
  Hand, 
  Search,
  Navigation
} from 'lucide-react';

interface MobileOptimizerProps {
  showDetails?: boolean;
  compact?: boolean;
  onOptimize?: () => void;
}

export default function MobileOptimizer({ 
  showDetails = false, 
  compact = false,
  onOptimize
}: MobileOptimizerProps) {
  const {
    isMobile,
    isOnline,
    isInstalled,
    gestures,
    enableMobileOptimization,
    enableSwipeNavigation,
    enablePinchZoom,
    enableTouchFeedback
  } = useMobile();

  const getStatusIcon = () => {
    if (!isMobile) return <Smartphone className="h-4 w-4 text-gray-500" />;
    if (isOnline) return <Wifi className="h-4 w-4 text-green-500" />;
    return <WifiOff className="h-4 w-4 text-red-500" />;
  };

  const getStatusText = () => {
    if (!isMobile) return 'デスクトップ';
    if (isOnline) return 'オンライン';
    return 'オフライン';
  };

  const getStatusColor = () => {
    if (!isMobile) return 'text-gray-600';
    if (isOnline) return 'text-green-600';
    return 'text-red-600';
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
          <Smartphone className="h-5 w-5 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">モバイル最適化</h3>
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
          {/* デバイス情報 */}
          <div className="grid grid-cols-2 gap-4">
            <div className="flex items-center space-x-2">
              <Smartphone className="h-4 w-4 text-gray-500" />
              <div>
                <div className="text-sm text-gray-600">デバイス</div>
                <div className="text-sm font-medium">
                  {isMobile ? 'モバイル' : 'デスクトップ'}
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              {isOnline ? (
                <Wifi className="h-4 w-4 text-green-500" />
              ) : (
                <WifiOff className="h-4 w-4 text-red-500" />
              )}
              <div>
                <div className="text-sm text-gray-600">接続状態</div>
                <div className="text-sm font-medium">
                  {isOnline ? 'オンライン' : 'オフライン'}
                </div>
              </div>
            </div>
          </div>

          {/* 最適化機能 */}
          <div className="border-t pt-4">
            <h4 className="text-sm font-medium text-gray-900 mb-2">最適化機能</h4>
            <div className="grid grid-cols-2 gap-2">
              <div className="flex items-center space-x-2">
                <Hand className="h-3 w-3 text-blue-500" />
                <span className="text-xs text-gray-600">タッチジェスチャー</span>
              </div>
              
              <div className="flex items-center space-x-2">
                <Navigation className="h-3 w-3 text-green-500" />
                <span className="text-xs text-gray-600">スワイプナビ</span>
              </div>
              
              <div className="flex items-center space-x-2">
                <Search className="h-3 w-3 text-purple-500" />
                <span className="text-xs text-gray-600">ピンチズーム</span>
              </div>
              
              <div className="flex items-center space-x-2">
                <Smartphone className="h-3 w-3 text-orange-500" />
                <span className="text-xs text-gray-600">ハプティック</span>
              </div>
            </div>
          </div>

          {/* ジェスチャー一覧 */}
          {gestures.length > 0 && (
            <div className="border-t pt-4">
              <h4 className="text-sm font-medium text-gray-900 mb-2">利用可能なジェスチャー</h4>
              <div className="space-y-1">
                {gestures.map((gesture, index) => (
                  <div key={index} className="text-xs text-gray-600 bg-gray-50 p-2 rounded">
                    {gesture}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* PWA状態 */}
          <div className="border-t pt-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Download className="h-4 w-4 text-gray-500" />
                <span className="text-sm text-gray-600">PWAインストール</span>
              </div>
              <div className={`text-sm font-medium ${
                isInstalled ? 'text-green-600' : 'text-gray-600'
              }`}>
                {isInstalled ? 'インストール済み' : '未インストール'}
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="flex items-center justify-between mt-4 pt-3 border-t">
        <div className="space-x-2">
          <button
            onClick={() => {
              enableMobileOptimization();
              onOptimize?.();
            }}
            className="px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
          >
            最適化実行
          </button>
          
          <button
            onClick={enableSwipeNavigation}
            className="px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm"
          >
            スワイプナビ
          </button>
        </div>
        
        <div className="text-xs text-gray-500">
          {isMobile ? 'モバイル最適化済み' : 'デスクトップモード'}
        </div>
      </div>
    </div>
  );
}
