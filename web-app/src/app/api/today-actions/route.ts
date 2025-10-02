import { NextRequest, NextResponse } from 'next/server';

// 静的エクスポート用の設定
export const dynamic = 'force-dynamic';

// 今日のアクション提案用のデフォルトデータ
const defaultTodayActions = {
  date: new Date().toISOString().split('T')[0],
  timestamp: new Date().toISOString(),
  marketStatus: 'open', // open, closed, pre-market, after-hours
  actions: [
    {
      id: 'action_1',
      type: 'buy',
      symbol: '7203',
      name: 'トヨタ自動車',
      currentPrice: 2850,
      targetPrice: 3000,
      stopLoss: 2700,
      confidence: 0.85,
      reason: 'テクニカル分析で上昇トレンド継続、ファンダメンタルズ良好',
      priority: 'high',
      timeframe: '1-2週間'
    },
    {
      id: 'action_2',
      type: 'sell',
      symbol: '6758',
      name: 'ソニーグループ',
      currentPrice: 12500,
      targetPrice: 12000,
      stopLoss: 13000,
      confidence: 0.78,
      reason: '利益確定のタイミング、テクニカル指標で売りシグナル',
      priority: 'medium',
      timeframe: '3-5日'
    },
    {
      id: 'action_3',
      type: 'hold',
      symbol: '9984',
      name: 'ソフトバンクグループ',
      currentPrice: 8500,
      targetPrice: 9000,
      stopLoss: 8000,
      confidence: 0.72,
      reason: '現状維持、追加情報待ち',
      priority: 'low',
      timeframe: '1-2週間'
    }
  ],
  portfolio: {
    totalValue: 5000000,
    dailyChange: 125000,
    dailyChangePercent: 2.56,
    positions: [
      {
        symbol: '7203',
        name: 'トヨタ自動車',
        shares: 100,
        currentValue: 285000,
        profitLoss: 15000,
        profitLossPercent: 5.56
      },
      {
        symbol: '6758',
        name: 'ソニーグループ',
        shares: 20,
        currentValue: 250000,
        profitLoss: -5000,
        profitLossPercent: -1.96
      }
    ]
  },
  marketInsights: {
    trend: 'bullish',
    volatility: 'medium',
    sentiment: 'positive',
    keyEvents: [
      '日銀政策金利発表予定',
      '米国雇用統計発表',
      '企業業績発表週間'
    ]
  },
  riskAlerts: [
    {
      type: 'warning',
      message: 'ポートフォリオの集中度が高いです',
      action: '分散投資を検討してください'
    }
  ]
};

export async function GET(request: NextRequest) {
  try {
    // 実際の実装では、リアルタイムでアクションを分析・提案
    // 現在はデフォルトデータを返す
    return NextResponse.json(defaultTodayActions);
  } catch (error) {
    console.error('今日のアクション取得エラー:', error);
    return NextResponse.json(
      { 
        error: '今日のアクションの取得に失敗しました',
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
    
    // アクションの実行記録
    console.log('アクション実行記録:', body);
    
    return NextResponse.json(
      { 
        message: 'アクションが記録されました',
        actionId: `action_${Date.now()}`,
        status: 'recorded',
        timestamp: new Date().toISOString()
      },
      { status: 200 }
    );
  } catch (error) {
    console.error('アクション記録エラー:', error);
    return NextResponse.json(
      { error: 'アクションの記録に失敗しました' },
      { status: 500 }
    );
  }
}
