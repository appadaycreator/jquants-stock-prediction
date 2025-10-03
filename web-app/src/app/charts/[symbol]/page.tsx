"use client";

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { ArrowLeft, Download, Share2, Maximize2, Settings } from 'lucide-react';
import Link from 'next/link';
import StockChart from '@/components/StockChart';
import { Button } from '@/components/ui/button';


interface ChartData {
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface StockInfo {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  marketCap: string;
  volume: string;
}

export default function ChartPage() {
  const params = useParams();
  const symbol = params.symbol as string;
  
  const [stockInfo, setStockInfo] = useState<StockInfo | null>(null);
  const [chartData, setChartData] = useState<ChartData[]>([]);
  const [timeframe, setTimeframe] = useState<'1d' | '1w' | '1m' | '3m' | '6m' | '1y'>('1m');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // モックデータの生成
  const generateMockData = (symbol: string, timeframe: string): ChartData[] => {
    const data: ChartData[] = [];
    const now = Date.now();
    const intervals = {
      '1d': 5 * 60 * 1000, // 5分間隔
      '1w': 60 * 60 * 1000, // 1時間間隔
      '1m': 24 * 60 * 60 * 1000, // 1日間隔
      '3m': 24 * 60 * 60 * 1000, // 1日間隔
      '6m': 24 * 60 * 60 * 1000, // 1日間隔
      '1y': 24 * 60 * 60 * 1000, // 1日間隔
    };
    
    const interval = intervals[timeframe as keyof typeof intervals] || 24 * 60 * 60 * 1000;
    const periods = {
      '1d': 24 * 12, // 5分間隔で1日
      '1w': 24 * 7, // 1時間間隔で1週間
      '1m': 30, // 1日間隔で1ヶ月
      '3m': 90, // 1日間隔で3ヶ月
      '6m': 180, // 1日間隔で6ヶ月
      '1y': 365, // 1日間隔で1年
    };
    
    const periodCount = periods[timeframe as keyof typeof periods] || 30;
    const basePrice = 1000 + Math.random() * 500;
    
    for (let i = periodCount; i >= 0; i--) {
      const timestamp = now - (i * interval);
      const price = basePrice + (Math.random() - 0.5) * 100;
      const open = price + (Math.random() - 0.5) * 10;
      const close = price + (Math.random() - 0.5) * 10;
      const high = Math.max(open, close) + Math.random() * 20;
      const low = Math.min(open, close) - Math.random() * 20;
      const volume = Math.floor(Math.random() * 1000000) + 100000;
      
      data.push({
        timestamp,
        open: Math.round(open * 100) / 100,
        high: Math.round(high * 100) / 100,
        low: Math.round(low * 100) / 100,
        close: Math.round(close * 100) / 100,
        volume,
      });
    }
    
    return data;
  };

  // モック株価情報の生成
  const generateMockStockInfo = (symbol: string): StockInfo => {
    const basePrice = 1000 + Math.random() * 500;
    const change = (Math.random() - 0.5) * 50;
    const changePercent = (change / basePrice) * 100;
    
    return {
      symbol,
      name: `${symbol} 株式会社`,
      price: Math.round(basePrice * 100) / 100,
      change: Math.round(change * 100) / 100,
      changePercent: Math.round(changePercent * 100) / 100,
      marketCap: `${Math.floor(Math.random() * 1000)}億円`,
      volume: `${Math.floor(Math.random() * 1000000)}`,
    };
  };

  useEffect(() => {
    const loadChartData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // モックデータの生成
        const mockData = generateMockData(symbol, timeframe);
        const mockStockInfo = generateMockStockInfo(symbol);
        
        setChartData(mockData);
        setStockInfo(mockStockInfo);
        
        // 実際のAPI呼び出し（開発環境の場合）
        if (process.env.NODE_ENV === 'development') {
          try {
            const response = await fetch(`/api/charts/${symbol}?timeframe=${timeframe}`);
            if (response.ok) {
              const apiData = await response.json();
              if (apiData.success && apiData.data) {
                setChartData(apiData.data.chartData || mockData);
                setStockInfo(apiData.data.stockInfo || mockStockInfo);
              }
            }
          } catch (apiError) {
            console.warn('API呼び出し失敗、モックデータを使用:', apiError);
          }
        }
      } catch (error) {
        console.error('チャートデータ読み込みエラー:', error);
        setError('チャートデータの読み込みに失敗しました');
      } finally {
        setLoading(false);
      }
    };

    if (symbol) {
      loadChartData();
    }
  }, [symbol, timeframe]);

  const handleTimeframeChange = (newTimeframe: typeof timeframe) => {
    setTimeframe(newTimeframe);
  };

  const handleDownload = () => {
    // チャート画像のダウンロード機能
    console.log('チャート画像をダウンロード');
  };

  const handleShare = () => {
    // チャートの共有機能
    if (navigator.share) {
      navigator.share({
        title: `${symbol} チャート`,
        text: `${symbol} の株価チャート`,
        url: window.location.href,
      });
    } else {
      navigator.clipboard.writeText(window.location.href);
      alert('URLをクリップボードにコピーしました');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">チャートを読み込み中...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 mb-4">
            <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">エラーが発生しました</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <Button onClick={() => window.location.reload()}>
            再読み込み
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* ヘッダー */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <Link href="/dashboard" className="text-gray-600 hover:text-gray-900">
                <ArrowLeft className="h-5 w-5" />
              </Link>
              <div>
                <h1 className="text-xl font-semibold text-gray-900">
                  {stockInfo?.name || symbol}
                </h1>
                <p className="text-sm text-gray-600">{symbol}</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <Button variant="outline" size="sm" onClick={handleDownload}>
                <Download className="h-4 w-4 mr-2" />
                ダウンロード
              </Button>
              <Button variant="outline" size="sm" onClick={handleShare}>
                <Share2 className="h-4 w-4 mr-2" />
                共有
              </Button>
              <Button variant="outline" size="sm">
                <Settings className="h-4 w-4 mr-2" />
                設定
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* 株価情報 */}
      {stockInfo && (
        <div className="bg-white border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-6">
                <div>
                  <span className="text-2xl font-bold text-gray-900">
                    ¥{stockInfo.price.toLocaleString()}
                  </span>
                  <span className={`ml-2 text-sm font-medium ${
                    stockInfo.change >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {stockInfo.change >= 0 ? '+' : ''}{stockInfo.change.toFixed(2)} 
                    ({stockInfo.changePercent >= 0 ? '+' : ''}{stockInfo.changePercent.toFixed(2)}%)
                  </span>
                </div>
                <div className="text-sm text-gray-600">
                  <div>時価総額: {stockInfo.marketCap}</div>
                  <div>出来高: {stockInfo.volume}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* タイムフレーム選択 */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-2">
          <div className="flex space-x-1">
            {(['1d', '1w', '1m', '3m', '6m', '1y'] as const).map((tf) => (
              <button
                key={tf}
                onClick={() => handleTimeframeChange(tf)}
                className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${
                  timeframe === tf
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                {tf === '1d' ? '1日' : 
                 tf === '1w' ? '1週' : 
                 tf === '1m' ? '1ヶ月' : 
                 tf === '3m' ? '3ヶ月' : 
                 tf === '6m' ? '6ヶ月' : '1年'}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* チャート */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="bg-white rounded-lg shadow-sm border">
          <div className="p-4">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              {symbol} 株価チャート ({timeframe})
            </h2>
            <div className="h-96">
              <StockChart
                data={chartData}
                symbol={symbol}
                timeframe={timeframe}
                height={400}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
