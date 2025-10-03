import { NextRequest, NextResponse } from 'next/server';

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

interface ChartResponse {
  success: boolean;
  data?: {
    chartData: ChartData[];
    stockInfo: StockInfo;
  };
  error?: string;
}

// モックチャートデータの生成
function generateMockChartData(symbol: string, timeframe: string): ChartData[] {
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
}

// モック株価情報の生成
function generateMockStockInfo(symbol: string): StockInfo {
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
}

export async function GET(
  request: NextRequest,
  { params }: { params: { symbol: string } }
): Promise<NextResponse<ChartResponse>> {
  try {
    const symbol = params.symbol;
    const { searchParams } = new URL(request.url);
    const timeframe = searchParams.get('timeframe') || '1m';
    
    // バリデーション
    if (!symbol) {
      return NextResponse.json({
        success: false,
        error: '銘柄コードが必要です',
      }, { status: 400 });
    }
    
    // 静的サイトモードまたは本番環境の場合はモックデータを返す
    const isProduction = process.env.NODE_ENV === 'production';
    const isStaticSite = isProduction;
    
    if (isStaticSite) {
      const chartData = generateMockChartData(symbol, timeframe);
      const stockInfo = generateMockStockInfo(symbol);
      
      return NextResponse.json({
        success: true,
        data: {
          chartData,
          stockInfo,
        },
      });
    }
    
    // 開発環境での実際のデータ取得
    // 実際の実装では、ここでJ-Quants APIやYahoo Finance APIからデータを取得
    const chartData = generateMockChartData(symbol, timeframe);
    const stockInfo = generateMockStockInfo(symbol);
    
    return NextResponse.json({
      success: true,
      data: {
        chartData,
        stockInfo,
      },
    });
    
  } catch (error) {
    console.error('チャートデータ取得エラー:', error);
    
    // エラー時はモックデータを返す
    const symbol = params.symbol;
    const chartData = generateMockChartData(symbol, '1m');
    const stockInfo = generateMockStockInfo(symbol);
    
    return NextResponse.json({
      success: true,
      data: {
        chartData,
        stockInfo,
      },
    });
  }
}
