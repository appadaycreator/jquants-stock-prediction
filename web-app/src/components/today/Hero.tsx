'use client';

import { TodaySummary } from '@/types/today';

interface HeroProps {
  summary: TodaySummary;
}

export default function Hero({ summary }: HeroProps) {
  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('ja-JP', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      timeZone: 'Asia/Tokyo',
    });
  };

  const getMarketStatusText = (phase: string) => {
    switch (phase) {
      case 'preopen':
        return '場前';
      case 'open':
        return '場中';
      case 'postclose':
        return '引け後';
      default:
        return '不明';
    }
  };

  const getMarketStatusColor = (phase: string) => {
    switch (phase) {
      case 'preopen':
        return 'text-blue-600 bg-blue-50';
      case 'open':
        return 'text-green-600 bg-green-50';
      case 'postclose':
        return 'text-gray-600 bg-gray-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  return (
    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl p-6 mb-6 shadow-md">
      <div className="flex flex-col">
        <div className="mb-4">
          <div className="flex items-center gap-3 mb-3">
            <div className="text-3xl">📈</div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                今日の投資タスク
              </h1>
              <p className="text-sm text-gray-600">
                効率的な投資判断のために、以下のタスクを順番に実行してください
              </p>
            </div>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
            <div className="bg-white rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-green-600">{summary.overview.buy_candidates}</div>
              <div className="text-xs text-gray-600">買い候補</div>
            </div>
            <div className="bg-white rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-red-600">{summary.overview.sell_candidates}</div>
              <div className="text-xs text-gray-600">売り候補</div>
            </div>
            <div className="bg-white rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-yellow-600">{summary.overview.warnings}</div>
              <div className="text-xs text-gray-600">要注意</div>
            </div>
            <div className="bg-white rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-blue-600">{summary.todos?.length || 0}</div>
              <div className="text-xs text-gray-600">タスク</div>
            </div>
          </div>

          {/* クイックガイド */}
          <div className="bg-white rounded-lg p-4">
            <h3 className="font-semibold text-gray-900 mb-2">🚀 今日の5分ルーティン</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
              <div className="flex items-center gap-2">
                <span className="w-6 h-6 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-xs font-bold">1</span>
                <span className="text-gray-700">推奨タスクを確認</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-6 h-6 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-xs font-bold">2</span>
                <span className="text-gray-700">ウォッチリスト管理</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-6 h-6 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-xs font-bold">3</span>
                <span className="text-gray-700">期間選択・一括更新</span>
              </div>
            </div>
          </div>
        </div>
        
        <div className="flex items-center justify-between text-sm">
          <div className="text-gray-600">
            最終更新: {formatTime(summary.generated_at)}
          </div>
          <div className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${getMarketStatusColor(summary.market_phase)}`}>
            {getMarketStatusText(summary.market_phase)}
          </div>
        </div>
      </div>
    </div>
  );
}
