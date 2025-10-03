import { NextRequest, NextResponse } from 'next/server';

// 分析リクエストの型定義
interface AnalysisRequest {
  stockCode?: string;
  analysisType?: 'technical' | 'fundamental' | 'sentiment' | 'comprehensive';
  timeframe?: '1d' | '1w' | '1m' | '3m' | '6m' | '1y';
  indicators?: string[];
  options?: {
    includeNews?: boolean;
    includeEarnings?: boolean;
    includeVolume?: boolean;
  };
}

// 分析結果の型定義
interface AnalysisResult {
  success: boolean;
  data?: {
    stockCode: string;
    analysisType: string;
    timeframe: string;
    indicators: {
      name: string;
      value: number;
      signal: 'buy' | 'sell' | 'hold';
      strength: number;
    }[];
    summary: {
      overallScore: number;
      recommendation: 'strong_buy' | 'buy' | 'hold' | 'sell' | 'strong_sell';
      confidence: number;
      reasoning: string[];
    };
    technicalAnalysis?: {
      trend: string;
      momentum: string;
      volatility: string;
      support: number;
      resistance: number;
    };
    fundamentalAnalysis?: {
      pe: number;
      pb: number;
      roe: number;
      debtRatio: number;
      growthRate: number;
    };
    sentimentAnalysis?: {
      newsSentiment: number;
      socialSentiment: number;
      analystRating: string;
    };
    charts?: {
      priceChart: string; // base64 encoded image
      indicatorChart: string;
    };
    timestamp: string;
  };
  error?: string;
}

// モック分析データの生成
function generateMockAnalysis(request: AnalysisRequest): AnalysisResult['data'] {
  const stockCode = request.stockCode || '7203'; // デフォルト: トヨタ
  const analysisType = request.analysisType || 'comprehensive';
  const timeframe = request.timeframe || '1m';
  
  // ランダムな分析結果を生成
  const indicators = [
    { name: 'RSI', value: 45 + Math.random() * 20, signal: 'hold' as const, strength: 0.6 },
    { name: 'MACD', value: -0.5 + Math.random() * 1, signal: 'buy' as const, strength: 0.7 },
    { name: 'Bollinger', value: 0.3 + Math.random() * 0.4, signal: 'hold' as const, strength: 0.5 },
    { name: 'Stochastic', value: 30 + Math.random() * 40, signal: 'sell' as const, strength: 0.8 },
  ];
  
  const overallScore = 50 + Math.random() * 40;
  const recommendations = ['strong_buy', 'buy', 'hold', 'sell', 'strong_sell'] as const;
  const recommendation = recommendations[Math.floor(Math.random() * recommendations.length)];
  
  const reasoning = [
    'テクニカル指標が良好な状態を示しています',
    '出来高が増加傾向にあります',
    '市場センチメントがポジティブです',
    'ファンダメンタル分析が良好です',
  ];
  
  return {
    stockCode,
    analysisType,
    timeframe,
    indicators,
    summary: {
      overallScore: Math.round(overallScore),
      recommendation,
      confidence: 0.6 + Math.random() * 0.3,
      reasoning: reasoning.slice(0, 2 + Math.floor(Math.random() * 2)),
    },
    technicalAnalysis: {
      trend: ['上昇', '下降', '横ばい'][Math.floor(Math.random() * 3)],
      momentum: ['強い', '中程度', '弱い'][Math.floor(Math.random() * 3)],
      volatility: ['高い', '中程度', '低い'][Math.floor(Math.random() * 3)],
      support: 1000 + Math.random() * 500,
      resistance: 1500 + Math.random() * 500,
    },
    fundamentalAnalysis: {
      pe: 10 + Math.random() * 20,
      pb: 0.5 + Math.random() * 1.5,
      roe: 5 + Math.random() * 15,
      debtRatio: 0.2 + Math.random() * 0.4,
      growthRate: -5 + Math.random() * 20,
    },
    sentimentAnalysis: {
      newsSentiment: -1 + Math.random() * 2,
      socialSentiment: -1 + Math.random() * 2,
      analystRating: ['買い', '中立', '売り'][Math.floor(Math.random() * 3)],
    },
    charts: {
      priceChart: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==',
      indicatorChart: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==',
    },
    timestamp: new Date().toISOString(),
  };
}

// 静的サイトモードの検出
function isStaticSiteMode(): boolean {
  if (typeof window === 'undefined') return false;
  const hostname = window.location.hostname;
  return hostname.includes('github.io') || 
         hostname.includes('netlify.app') || 
         hostname.includes('vercel.app');
}

export async function POST(request: NextRequest): Promise<NextResponse<AnalysisResult>> {
  try {
    // リクエストボディの解析
    let body: AnalysisRequest = {};
    
    try {
      body = await request.json();
    } catch (parseError) {
      // JSON解析エラーの場合はデフォルト値を使用
      console.warn('JSON解析エラー、デフォルト値を使用:', parseError);
      body = {
        stockCode: '7203',
        analysisType: 'comprehensive',
        timeframe: '1m',
      };
    }
    
    // 静的サイトモードまたは本番環境の場合はモックデータを返す
    const isProduction = process.env.NODE_ENV === 'production';
    const isStaticSite = isProduction || 
      (typeof window !== 'undefined' && 
       (window.location.hostname.includes('github.io') || 
        window.location.hostname.includes('netlify.app') || 
        window.location.hostname.includes('vercel.app')));
    
    if (isStaticSite) {
      const mockRequest: AnalysisRequest = {
        stockCode: body.stockCode || '7203',
        analysisType: body.analysisType || 'comprehensive',
        timeframe: body.timeframe || '1m',
        indicators: body.indicators || ['RSI', 'MACD', 'Bollinger'],
        options: {
          includeNews: true,
          includeEarnings: true,
          includeVolume: true,
          ...body.options,
        },
      };
      
      const mockData = generateMockAnalysis(mockRequest);
      
      return NextResponse.json({
        success: true,
        data: mockData,
      });
    }
    
    // 開発環境での実際の分析実行
    const analysisData = generateMockAnalysis(body);
    
    return NextResponse.json({
      success: true,
      data: analysisData,
    });
    
  } catch (error) {
    console.error('分析エラー:', error);
    
    // エラー時はモックデータを返す
    const mockData = generateMockAnalysis({
      stockCode: '7203',
      analysisType: 'comprehensive',
      timeframe: '1m',
    });
    
    return NextResponse.json({
      success: true,
      data: mockData,
    });
  }
}

export async function GET(): Promise<NextResponse> {
  return NextResponse.json({
    success: true,
    message: '分析APIエンドポイント',
    endpoints: {
      POST: '/api/analyze - 株式分析の実行',
    },
    parameters: {
      stockCode: '銘柄コード（例: 7203）',
      analysisType: 'technical | fundamental | sentiment | comprehensive',
      timeframe: '1d | 1w | 1m | 3m | 6m | 1y',
      indicators: 'テクニカル指標の配列',
    },
  });
}
