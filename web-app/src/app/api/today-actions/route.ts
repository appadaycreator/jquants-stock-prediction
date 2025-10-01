import { NextResponse } from 'next/server';
import { readFile } from 'fs/promises';
import { join } from 'path';

// export const dynamic = 'force-dynamic'; // 静的エクスポートでは使用不可

interface AnalysisResult {
  timestamp: string;
  status: 'completed' | 'failed' | 'running';
  summary?: {
    total_data_points: number;
    prediction_period: string;
    best_model: string;
    mae: string;
    r2: string;
    last_updated: string;
  };
}

interface TodayActionsResponse {
  date: string;
  analysisRequired: boolean;
  analysisStatus?: 'completed' | 'failed' | 'not_started';
  lastAnalysisTime?: string;
  actions: Array<{
    id: string;
    type: string;
    timestamp: string;
    status: 'completed' | 'failed' | 'pending';
    description: string;
  }>;
  summary: {
    totalActions: number;
    completedActions: number;
    failedActions: number;
    successRate: number;
  };
  error?: {
    code: string;
    message: string;
    retry_hint?: string;
  };
}

async function checkAnalysisStatus(): Promise<{
  hasAnalysis: boolean;
  lastAnalysisTime?: string;
  analysisStatus?: 'completed' | 'failed' | 'not_started';
}> {
  try {
    // 最新の分析結果をチェック
    const dataPath = join(process.cwd(), 'public', 'data');
    
    // 最新の分析結果ファイルを探す
    const latestIndexPath = join(dataPath, 'latest', 'index.json');
    try {
      const latestIndex = JSON.parse(await readFile(latestIndexPath, 'utf-8'));
      const today = new Date().toISOString().split('T')[0];
      
      if (latestIndex.date === today) {
        return {
          hasAnalysis: true,
          lastAnalysisTime: latestIndex.timestamp,
          analysisStatus: 'completed'
        };
      }
    } catch (e) {
      // latest/index.jsonが存在しない場合
    }

    // 今日の分析結果ファイルを直接チェック
    const todayPath = join(dataPath, `${new Date().toISOString().split('T')[0]}`, 'summary.json');
    try {
      const todaySummary = JSON.parse(await readFile(todayPath, 'utf-8'));
      return {
        hasAnalysis: true,
        lastAnalysisTime: todaySummary.last_updated,
        analysisStatus: 'completed'
      };
    } catch (e) {
      // 今日の分析結果が存在しない場合
    }

    return {
      hasAnalysis: false,
      analysisStatus: 'not_started'
    };
  } catch (error) {
    console.error('分析ステータス確認エラー:', error);
    return {
      hasAnalysis: false,
      analysisStatus: 'not_started'
    };
  }
}

export async function GET() {
  try {
    const analysisStatus = await checkAnalysisStatus();
    
    if (!analysisStatus.hasAnalysis) {
      // 分析が未実行の場合
      const response: TodayActionsResponse = {
        date: new Date().toISOString().split('T')[0],
        analysisRequired: true,
        analysisStatus: analysisStatus.analysisStatus,
        actions: [
          {
            id: 'analysis_required',
            type: 'analysis',
            timestamp: new Date().toISOString(),
            status: 'pending',
            description: '分析を実行してからお試しください'
          }
        ],
        summary: {
          totalActions: 1,
          completedActions: 0,
          failedActions: 0,
          successRate: 0
        },
        error: {
          code: 'ANALYSIS_REQUIRED',
          message: '分析を実行してからお試しください',
          retry_hint: 'ダッシュボードで「分析実行」ボタンをクリックしてください'
        }
      };

      return NextResponse.json(response, { status: 202 }); // 202 Accepted
    }

    // 分析結果がある場合の処理
    const todayActions: TodayActionsResponse = {
      date: new Date().toISOString().split('T')[0],
      analysisRequired: false,
      analysisStatus: analysisStatus.analysisStatus,
      lastAnalysisTime: analysisStatus.lastAnalysisTime,
      actions: [
        {
          id: 'analysis_completed',
          type: 'analysis',
          timestamp: analysisStatus.lastAnalysisTime || new Date().toISOString(),
          status: 'completed',
          description: '株価分析を実行しました'
        },
        {
          id: 'model_training',
          type: 'model_training',
          timestamp: new Date().toISOString(),
          status: 'completed',
          description: 'モデルの再学習を完了しました'
        },
        {
          id: 'notification',
          type: 'notification',
          timestamp: new Date().toISOString(),
          status: 'completed',
          description: '分析結果の通知を送信しました'
        }
      ],
      summary: {
        totalActions: 3,
        completedActions: 3,
        failedActions: 0,
        successRate: 100
      }
    };

    return NextResponse.json(todayActions);
  } catch (error) {
    console.error('Today actions error:', error);
    
    // エラーレスポンスの構造化
    const errorResponse: TodayActionsResponse = {
      date: new Date().toISOString().split('T')[0],
      analysisRequired: true,
      analysisStatus: 'failed',
      actions: [],
      summary: {
        totalActions: 0,
        completedActions: 0,
        failedActions: 1,
        successRate: 0
      },
      error: {
        code: 'API_ERROR',
        message: 'データ取得に失敗しました',
        retry_hint: 'しばらく時間をおいてから再度お試しください'
      }
    };

    return NextResponse.json(errorResponse, { status: 500 });
  }
}
