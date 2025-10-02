/**
 * 株価データ表示コンポーネント
 * 実装したキャッシュ機能とデータ取得機能のテスト用
 */

import React, { useState, useEffect } from 'react';
import { useStockData } from '@/hooks/useStockData';
import { StockDataResponse } from '@/lib/enhancedDataCache';

interface StockDataDisplayProps {
  symbol?: string;
  autoRefresh?: boolean;
  showCacheStats?: boolean;
}

export default function StockDataDisplay({ 
  symbol, 
  autoRefresh = false, 
  showCacheStats = false 
}: StockDataDisplayProps) {
  const {
    data,
    loading,
    error,
    lastUpdated,
    source,
    refresh,
    clearCache,
    startAutoRefresh,
    stopAutoRefresh,
    isRetrying,
    canRetry
  } = useStockData({
    symbol,
    autoRefresh,
    refreshInterval: 30000,
    enableFallback: true,
    onError: (error) => console.error('データ取得エラー:', error),
    onDataUpdate: (data) => console.log('データ更新:', data)
  });

  const [cacheStats, setCacheStats] = useState<any>(null);

  useEffect(() => {
    if (showCacheStats) {
      // キャッシュ統計の取得（実際の実装ではEnhancedDataCacheから取得）
      const stats = {
        totalItems: 5,
        validItems: 4,
        expiredItems: 1,
        totalSize: 1024 * 1024 // 1MB
      };
      setCacheStats(stats);
    }
  }, [showCacheStats]);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-4">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2">データ読み込み中...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center">
          <div className="text-red-600">⚠️</div>
          <div className="ml-2">
            <h3 className="text-red-800 font-medium">データ取得エラー</h3>
            <p className="text-red-600 text-sm">{error}</p>
            {canRetry && (
              <button
                onClick={refresh}
                className="mt-2 px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700"
              >
                再試行
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <p className="text-gray-600">データがありません</p>
        <button
          onClick={refresh}
          className="mt-2 px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
        >
          データを取得
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* ヘッダー情報 */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold">
              {symbol ? `銘柄 ${symbol}` : '全銘柄データ'}
            </h2>
            <p className="text-sm text-gray-600">
              最終更新: {lastUpdated ? new Date(lastUpdated).toLocaleString() : '不明'}
            </p>
            <p className="text-sm text-gray-500">
              データソース: {source === 'cache' ? 'キャッシュ' : source === 'api' ? 'API' : 'フォールバック'}
            </p>
          </div>
          <div className="flex space-x-2">
            <button
              onClick={refresh}
              className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
            >
              更新
            </button>
            <button
              onClick={clearCache}
              className="px-3 py-1 bg-gray-600 text-white rounded text-sm hover:bg-gray-700"
            >
              キャッシュクリア
            </button>
            {autoRefresh ? (
              <button
                onClick={stopAutoRefresh}
                className="px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700"
              >
                自動更新停止
              </button>
            ) : (
              <button
                onClick={startAutoRefresh}
                className="px-3 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700"
              >
                自動更新開始
              </button>
            )}
          </div>
        </div>
      </div>

      {/* キャッシュ統計 */}
      {showCacheStats && cacheStats && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="text-blue-800 font-medium mb-2">キャッシュ統計</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-blue-600">総アイテム数:</span>
              <span className="ml-2 font-medium">{cacheStats.totalItems}</span>
            </div>
            <div>
              <span className="text-blue-600">有効アイテム:</span>
              <span className="ml-2 font-medium">{cacheStats.validItems}</span>
            </div>
            <div>
              <span className="text-blue-600">期限切れ:</span>
              <span className="ml-2 font-medium">{cacheStats.expiredItems}</span>
            </div>
            <div>
              <span className="text-blue-600">総サイズ:</span>
              <span className="ml-2 font-medium">
                {(cacheStats.totalSize / 1024).toFixed(1)} KB
              </span>
            </div>
          </div>
        </div>
      )}

      {/* 株価データ表示 */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <h3 className="text-lg font-semibold mb-4">株価データ</h3>
        
        {symbol ? (
          // 個別銘柄表示
          <div className="space-y-2">
            {data.stocks && data.stocks[symbol] ? (
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <span className="text-gray-600">銘柄名:</span>
                  <span className="ml-2 font-medium">{data.stocks[symbol].name}</span>
                </div>
                <div>
                  <span className="text-gray-600">現在価格:</span>
                  <span className="ml-2 font-medium">
                    ¥{(data.stocks[symbol] as any)?.current_price?.last_price?.toLocaleString() || 'N/A'}
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">変動:</span>
                  <span className={`ml-2 font-medium ${
                    ((data.stocks[symbol] as any)?.current_price?.change_percent || 0) >= 0 
                      ? 'text-red-600' : 'text-blue-600'
                  }`}>
                    {((data.stocks[symbol] as any)?.current_price?.change_percent || 0).toFixed(2)}%
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">出来高:</span>
                  <span className="ml-2 font-medium">
                    {((data.stocks[symbol] as any)?.volume?.current_volume || 0).toLocaleString()}
                  </span>
                </div>
              </div>
            ) : (
              <p className="text-gray-600">銘柄データが見つかりません</p>
            )}
          </div>
        ) : (
          // 全銘柄表示
          <div className="space-y-2">
            {data.stocks && Object.keys(data.stocks).length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Object.entries(data.stocks).map(([code, stock]) => (
                  <div key={code} className="border border-gray-200 rounded-lg p-3">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h4 className="font-medium">{stock.name}</h4>
                        <p className="text-sm text-gray-600">{code}</p>
                      </div>
                      <span className="text-sm text-gray-500">{(stock as any).sector || 'N/A'}</span>
                    </div>
                    <div className="space-y-1 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">価格:</span>
                        <span className="font-medium">
                          ¥{(stock as any).current_price?.last_price?.toLocaleString() || 'N/A'}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">変動:</span>
                        <span className={`font-medium ${
                          ((stock as any).current_price?.change_percent || 0) >= 0 
                            ? 'text-red-600' : 'text-blue-600'
                        }`}>
                          {((stock as any).current_price?.change_percent || 0).toFixed(2)}%
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">出来高:</span>
                        <span className="font-medium">
                          {((stock as any).volume?.current_volume || 0).toLocaleString()}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-600">株価データがありません</p>
            )}
          </div>
        )}
      </div>

      {/* メタデータ表示 */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <h3 className="text-lg font-semibold mb-2">メタデータ</h3>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-600">総銘柄数:</span>
            <span className="ml-2 font-medium">{data.metadata?.total_stocks || 0}</span>
          </div>
          <div>
            <span className="text-gray-600">データソース:</span>
            <span className="ml-2 font-medium">{data.metadata?.data_source || 'N/A'}</span>
          </div>
          <div>
            <span className="text-gray-600">バージョン:</span>
            <span className="ml-2 font-medium">{data.metadata?.version || 'N/A'}</span>
          </div>
          <div>
            <span className="text-gray-600">更新タイプ:</span>
            <span className="ml-2 font-medium">{(data.metadata as any)?.update_type || 'N/A'}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
