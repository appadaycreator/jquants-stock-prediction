import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import { wrapHandler, jsonError } from '../_error';
import { withIdempotency } from '../_idempotency';

export const POST = withIdempotency(wrapHandler(async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { type, confirmBeforeExecute } = body;

    // 売買指示実行のシミュレーション
    const tradeResult = {
      id: `trade_${Date.now()}`,
      type,
      confirmBeforeExecute,
      status: 'executed',
      timestamp: new Date().toISOString(),
      orders: [
        {
          symbol: '7203.T',
          name: 'トヨタ自動車',
          action: 'buy',
          quantity: 100,
          price: 2400,
          totalValue: 240000,
          status: 'filled',
          executionTime: new Date().toISOString()
        },
        {
          symbol: '6758.T',
          name: 'ソニーグループ',
          action: 'hold',
          quantity: 0,
          price: 0,
          totalValue: 0,
          status: 'no_action',
          reason: '推奨アクションなし'
        },
        {
          symbol: '6861.T',
          name: 'キーエンス',
          action: 'sell',
          quantity: 50,
          price: 46000,
          totalValue: 2300000,
          status: 'filled',
          executionTime: new Date().toISOString()
        }
      ],
      summary: {
        totalOrders: 3,
        executedOrders: 2,
        totalValue: 2540000,
        estimatedProfit: 150000,
        riskLevel: 'moderate'
      },
      nextActions: [
        'ポジション監視',
        'ストップロス設定',
        '利益確定目標設定'
      ]
    };

    // 取引結果をファイルに保存
    const dataPath = path.join(process.cwd(), 'public', 'data');
    const tradeFile = path.join(dataPath, `trade_${Date.now()}.json`);
    
    try {
      fs.writeFileSync(tradeFile, JSON.stringify(tradeResult, null, 2));
    } catch (writeError) {
      console.warn('取引結果ファイル保存に失敗:', writeError);
    }

    return NextResponse.json(tradeResult);
  } catch (error: any) {
    console.error('売買指示実行エラー:', error);
    return jsonError({
      error_code: 'TRADE_EXECUTION_FAILED',
      user_message: '売買指示実行に失敗しました',
      retry_hint: '数十秒後に再実行してください',
    }, { status: 500 });
  }
}));
