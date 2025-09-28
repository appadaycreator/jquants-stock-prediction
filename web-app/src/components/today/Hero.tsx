'use client';

import { TodaySummary } from '../../types/today';

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
    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 mb-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div className="mb-4 sm:mb-0">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            本日の投資指示
          </h1>
          <div className="flex flex-wrap gap-4 text-sm">
            <div className="flex items-center gap-2">
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                買い候補 {summary.overview.buy_candidates}件
              </span>
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                売り候補 {summary.overview.sell_candidates}件
              </span>
              {summary.overview.warnings > 0 && (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                  要注意 {summary.overview.warnings}件
                </span>
              )}
            </div>
          </div>
        </div>
        <div className="text-right">
          <div className="text-sm text-gray-600 mb-1">
            生成時刻: {formatTime(summary.generated_at)}
          </div>
          <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getMarketStatusColor(summary.market_phase)}`}>
            {getMarketStatusText(summary.market_phase)}
          </div>
        </div>
      </div>
    </div>
  );
}
