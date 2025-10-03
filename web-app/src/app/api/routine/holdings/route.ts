import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    // 保有銘柄のヘルスチェック
    const holdings = await performHoldingsHealthCheck();
    
    return NextResponse.json({
      success: true,
      holdings,
      count: holdings.length,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('保有銘柄チェックエラー:', error);
    return NextResponse.json(
      {
        success: false,
        message: '保有銘柄チェックに失敗しました',
        error: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}

async function performHoldingsHealthCheck() {
  // モックデータ - 実際の実装では保有銘柄データを取得
  const mockHoldings = [
    {
      code: '7203',
      name: 'トヨタ自動車',
      price: 2500,
      change: 50,
      health: {
        earnings: 'good' as const,
        gap: 'warning' as const,
        volume: 'good' as const
      },
      issues: ['価格ギャップが大きい']
    },
    {
      code: '6758',
      name: 'ソニーグループ',
      price: 12000,
      change: -200,
      health: {
        earnings: 'warning' as const,
        gap: 'good' as const,
        volume: 'bad' as const
      },
      issues: ['決算発表待ち', '出来高が少ない']
    },
    {
      code: '9984',
      name: 'ソフトバンクグループ',
      price: 8000,
      change: 150,
      health: {
        earnings: 'good' as const,
        gap: 'good' as const,
        volume: 'good' as const
      },
      issues: []
    }
  ];

  // 実際の実装では、以下をチェック:
  // 1. 決算発表の有無
  // 2. 価格ギャップの確認
  // 3. 出来高の異常値検出
  // 4. テクニカル指標の確認

  return mockHoldings;
}
