export const dynamic = 'force-static';
import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET(request: NextRequest) {
  try {
    const today = new Date();
    const todayStr = today.toISOString().split('T')[0];
    
    // 今日のアクションファイルを読み込み
    const dataPath = path.join(process.cwd(), 'public', 'data');
    const todayActionsFile = path.join(dataPath, `today_actions_${todayStr}.json`);
    
    let todayActions;
    
    if (fs.existsSync(todayActionsFile)) {
      // 今日のファイルが存在する場合
      const fileContent = fs.readFileSync(todayActionsFile, 'utf8');
      todayActions = JSON.parse(fileContent);
    } else {
      // フォールバック: デフォルトの今日のアクションを生成
      const nextUpdateTime = new Date();
      nextUpdateTime.setHours(nextUpdateTime.getHours() + 2); // 2時間後
      
      todayActions = {
        analysisRequired: true,
        watchlistUpdates: [
          {
            symbol: '7203.T',
            action: 'modify',
            reason: '予測精度向上のため設定調整'
          },
          {
            symbol: '6758.T',
            action: 'remove',
            reason: 'パフォーマンス低下'
          },
          {
            symbol: '9984.T',
            action: 'add',
            reason: '新規推奨銘柄'
          }
        ],
        nextUpdateTime: nextUpdateTime.toISOString(),
        priorityActions: [
          {
            id: 'analysis',
            title: '分析実行',
            description: '最新データで予測分析を実行',
            action: 'analyze',
            priority: 'high'
          },
          {
            id: 'report',
            title: 'レポート確認',
            description: '昨日の分析結果を確認',
            action: 'report',
            priority: 'medium'
          },
          {
            id: 'trade',
            title: '売買指示',
            description: '推奨アクションに基づく取引指示',
            action: 'trade',
            priority: 'high'
          }
        ]
      };
      
      // 静的エクスポート互換性のためビルド時の書き込みは行わない
    }

    return NextResponse.json(todayActions);
  } catch (error) {
    console.error('今日のアクション取得エラー:', error);
    
    // エラー時はデフォルトデータを返す
    const nextUpdateTime = new Date();
    nextUpdateTime.setHours(nextUpdateTime.getHours() + 2);
    
    return NextResponse.json({
      analysisRequired: true,
      watchlistUpdates: [],
      nextUpdateTime: nextUpdateTime.toISOString(),
      priorityActions: [
        {
          id: 'analysis',
          title: '分析実行',
          description: '最新データで予測分析を実行',
          action: 'analyze',
          priority: 'high'
        }
      ]
    });
  }
}
