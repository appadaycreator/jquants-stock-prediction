import { NextRequest, NextResponse } from 'next/server';

// 静的エクスポート用の設定
export const dynamic = 'force-dynamic';

// デフォルトのリスク設定
const defaultRiskSettings = {
  riskTolerance: 'medium',
  maxLossPercentage: 5,
  stopLossPercentage: 3,
  takeProfitPercentage: 10,
  maxPositionSize: 10,
  diversificationLevel: 'medium',
  rebalanceFrequency: 'monthly',
  volatilityThreshold: 0.2,
  correlationThreshold: 0.7,
  sectorLimits: {
    technology: 30,
    healthcare: 20,
    finance: 15,
    consumer: 15,
    industrial: 10,
    utilities: 5,
    energy: 5
  },
  countryLimits: {
    japan: 60,
    usa: 25,
    europe: 10,
    asia: 5
  },
  assetAllocation: {
    stocks: 70,
    bonds: 20,
    cash: 10
  },
  riskMetrics: {
    maxDrawdown: 15,
    sharpeRatio: 1.0,
    volatility: 0.15
  },
  notifications: {
    priceAlerts: true,
    riskAlerts: true,
    rebalanceAlerts: true,
    newsAlerts: false
  },
  advanced: {
    useOptions: false,
    useLeverage: false,
    useShortSelling: false,
    useDerivatives: false
  }
};

export async function GET(request: NextRequest) {
  try {
    // 実際の実装では、データベースから設定を読み込む
    // 現在はデフォルト設定を返す
    return NextResponse.json(defaultRiskSettings);
  } catch (error) {
    console.error('リスク設定の読み込みエラー:', error);
    return NextResponse.json(
      { error: 'リスク設定の読み込みに失敗しました' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // 実際の実装では、データベースに設定を保存する
    // 現在は成功レスポンスを返す
    console.log('リスク設定の保存:', body);
    
    return NextResponse.json(
      { message: 'リスク設定が保存されました', settings: body },
      { status: 200 }
    );
  } catch (error) {
    console.error('リスク設定の保存エラー:', error);
    return NextResponse.json(
      { error: 'リスク設定の保存に失敗しました' },
      { status: 500 }
    );
  }
}

export async function PUT(request: NextRequest) {
  try {
    const body = await request.json();
    
    // 実際の実装では、データベースの設定を更新する
    // 現在は成功レスポンスを返す
    console.log('リスク設定の更新:', body);
    
    return NextResponse.json(
      { message: 'リスク設定が更新されました', settings: body },
      { status: 200 }
    );
  } catch (error) {
    console.error('リスク設定の更新エラー:', error);
    return NextResponse.json(
      { error: 'リスク設定の更新に失敗しました' },
      { status: 500 }
    );
  }
}
