/**
 * データ取得・キャッシュ機能のテストページ
 * 実装した機能の動作確認用
 */

'use client';

import React, { useState } from 'react';
import StockDataDisplay from '@/components/StockDataDisplay';

export default function TestDataPage() {
  const [selectedSymbol, setSelectedSymbol] = useState<string>('');
  const [autoRefresh, setAutoRefresh] = useState<boolean>(false);
  const [showCacheStats, setShowCacheStats] = useState<boolean>(true);

  const symbols = [
    { code: '', name: '全銘柄' },
    { code: '7203', name: 'トヨタ自動車' },
    { code: '6758', name: 'ソニーグループ' },
    { code: '9984', name: 'ソフトバンクグループ' }
  ];

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            データ取得・キャッシュ機能テスト
          </h1>
          <p className="text-gray-600">
            jQuantsデータのJSON形式保持と差分更新機能のテストページです。
          </p>
        </div>

        {/* コントロールパネル */}
        <div className="bg-white border border-gray-200 rounded-lg p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">テスト設定</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* 銘柄選択 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                表示銘柄
              </label>
              <select
                value={selectedSymbol}
                onChange={(e) => setSelectedSymbol(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {symbols.map((symbol) => (
                  <option key={symbol.code} value={symbol.code}>
                    {symbol.name}
                  </option>
                ))}
              </select>
            </div>

            {/* 自動更新設定 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                自動更新
              </label>
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="autoRefresh"
                  checked={autoRefresh}
                  onChange={(e) => setAutoRefresh(e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="autoRefresh" className="ml-2 text-sm text-gray-700">
                  30秒間隔で自動更新
                </label>
              </div>
            </div>

            {/* キャッシュ統計表示 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                キャッシュ統計
              </label>
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="showCacheStats"
                  checked={showCacheStats}
                  onChange={(e) => setShowCacheStats(e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="showCacheStats" className="ml-2 text-sm text-gray-700">
                  キャッシュ統計を表示
                </label>
              </div>
            </div>
          </div>
        </div>

        {/* データ表示エリア */}
        <div className="space-y-6">
          <StockDataDisplay
            symbol={selectedSymbol || undefined}
            autoRefresh={autoRefresh}
            showCacheStats={showCacheStats}
          />
        </div>

        {/* 機能説明 */}
        <div className="mt-12 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-blue-900 mb-4">
            実装された機能
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-medium text-blue-800 mb-2">
                📊 データ取得機能
              </h3>
              <ul className="text-sm text-blue-700 space-y-1">
                <li>• キャッシュ優先のデータ取得</li>
                <li>• サーバーからの最新データ取得</li>
                <li>• フォールバック機能</li>
                <li>• エラーハンドリング</li>
              </ul>
            </div>

            <div>
              <h3 className="text-lg font-medium text-blue-800 mb-2">
                💾 キャッシュ機能
              </h3>
              <ul className="text-sm text-blue-700 space-y-1">
                <li>• TTL設定（30分）</li>
                <li>• 自動クリーンアップ</li>
                <li>• キャッシュ統計表示</li>
                <li>• 手動キャッシュクリア</li>
              </ul>
            </div>

            <div>
              <h3 className="text-lg font-medium text-blue-800 mb-2">
                🔄 差分更新機能
              </h3>
              <ul className="text-sm text-blue-700 space-y-1">
                <li>• 既存データとの比較</li>
                <li>• 変更検出とログ記録</li>
                <li>• 効率的な更新処理</li>
                <li>• メタデータ管理</li>
              </ul>
            </div>

            <div>
              <h3 className="text-lg font-medium text-blue-800 mb-2">
                🚀 GitHub Actions
              </h3>
              <ul className="text-sm text-blue-700 space-y-1">
                <li>• 定期実行（平日9時・15時）</li>
                <li>• 自動データ更新</li>
                <li>• 変更検出とコミット</li>
                <li>• エラーハンドリング</li>
              </ul>
            </div>
          </div>
        </div>

        {/* 技術仕様 */}
        <div className="mt-8 bg-gray-50 border border-gray-200 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            技術仕様
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">
            <div>
              <h3 className="font-medium text-gray-800 mb-2">データ構造</h3>
              <ul className="text-gray-600 space-y-1">
                <li>• メタデータ: 更新時刻、バージョン、総銘柄数</li>
                <li>• 株価データ: 価格、変動、出来高、技術指標</li>
                <li>• 予測データ: 予測価格、信頼度、モデル情報</li>
                <li>• リスク指標: ボラティリティ、ベータ、シャープレシオ</li>
              </ul>
            </div>

            <div>
              <h3 className="font-medium text-gray-800 mb-2">ファイル構成</h3>
              <ul className="text-gray-600 space-y-1">
                <li>• /docs/data/stock_data.json (メインデータ)</li>
                <li>• /docs/data/stocks/銘柄コード.json (個別銘柄)</li>
                <li>• /docs/data/index.json (インデックス)</li>
                <li>• /docs/data/metadata/ (メタデータ)</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
