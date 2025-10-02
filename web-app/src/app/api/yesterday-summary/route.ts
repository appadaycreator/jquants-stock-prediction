import { NextRequest, NextResponse } from 'next/server';

// 静的エクスポート用の設定
export const dynamic = 'force-static';

// 昨日のサマリー用のデフォルトデータ
const defaultYesterdaySummary = {
  date: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString().split('T')[0],
  timestamp: new Date().toISOString(),
  marketSummary: {
    nikkei: {
      open: 28500,
      close: 28950,
      high: 29100,
      low: 28400,
      change: 450,
      changePercent: 1.58,
      volume: 1200000000
    },
    topix: {
      open: 1980,
      close: 2015,
      high: 2020,
      low: 1975,
      change: 35,
      changePercent: 1.77,
      volume: 800000000
    }
  },
  portfolio: {
    totalValue: 4875000,
    dailyChange: 125000,
    dailyChangePercent: 2.63,
    bestPerformer: {
      symbol: '7203',
      name: 'トヨタ自動車',
      change: 150,
      changePercent: 5.56
    },
    worstPerformer: {
      symbol: '6758',
      name: 'ソニーグループ',
      change: -250,
      changePercent: -1.96
    }
  },
  actions: {
    executed: [
      {
        type: 'buy',
        symbol: '7203',
        name: 'トヨタ自動車',
        shares: 50,
        price: 2700,
        value: 135000,
        timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString()
      }
    ],
    recommended: [
      {
        type: 'sell',
        symbol: '6758',
        name: 'ソニーグループ',
        reason: '利益確定のタイミング',
        confidence: 0.78
      }
    ],
    missed: [
      {
        symbol: '9984',
        name: 'ソフトバンクグループ',
        opportunity: '上昇トレンドの開始',
        potentialGain: 3.2
      }
    ]
  },
  analysis: {
    accuracy: 0.82,
    predictions: 15,
    correctPredictions: 12,
    incorrectPredictions: 3,
    modelPerformance: {
      xgboost: 0.85,
      randomForest: 0.83,
      lstm: 0.81
    }
  },
  insights: {
    marketTrend: 'bullish',
    volatility: 'medium',
    sentiment: 'positive',
    keyEvents: [
      '日銀政策金利発表',
      '企業業績発表',
      '海外市場の影響'
    ],
    recommendations: [
      '上昇トレンドが継続する可能性が高い',
      'テクニカル指標で買いシグナル',
      'リスク管理を継続してください'
    ]
  },
  alerts: [
    {
      type: 'info',
      message: 'ポートフォリオが目標リターンを上回りました',
      timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
    }
  ]
};

export async function GET(request: NextRequest) {
  try {
    // 実際の実装では、昨日のデータを分析・集計
    // 現在はデフォルトデータを返す
    return NextResponse.json(defaultYesterdaySummary);
  } catch (error) {
    console.error('昨日のサマリー取得エラー:', error);
    return NextResponse.json(
      { 
        error: '昨日のサマリーの取得に失敗しました',
        status: 'error',
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // サマリーの更新・記録
    console.log('サマリー更新記録:', body);
    
    return NextResponse.json(
      { 
        message: 'サマリーが更新されました',
        summaryId: `summary_${Date.now()}`,
        status: 'updated',
        timestamp: new Date().toISOString()
      },
      { status: 200 }
    );
  } catch (error) {
    console.error('サマリー更新エラー:', error);
    return NextResponse.json(
      { error: 'サマリーの更新に失敗しました' },
      { status: 500 }
    );
  }
}
