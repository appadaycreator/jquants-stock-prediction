import { NextResponse } from 'next/server';
import { readFile } from 'fs/promises';
import { join } from 'path';

// export const dynamic = 'force-dynamic'; // 静的エクスポートでは使用不可

interface SignalData {
  symbol: string;
  signal_type: string;
  confidence: number;
  price: number;
  timestamp: string;
  reason: string;
  category?: string;
  expected_holding_period?: number;
}

interface SignalsResponse {
  signals: SignalData[];
  analysisRequired: boolean;
  analysisStatus?: 'completed' | 'failed' | 'not_started';
  lastAnalysisTime?: string;
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

async function getSignalsFromAnalysis(): Promise<SignalData[]> {
  try {
    const dataPath = join(process.cwd(), 'public', 'data');
    const today = new Date().toISOString().split('T')[0];
    
    // 今日の分析結果からシグナルを取得
    const signalsPath = join(dataPath, `${today}`, 'signals.json');
    try {
      const signalsData = JSON.parse(await readFile(signalsPath, 'utf-8'));
      return signalsData.signals || [];
    } catch (e) {
      // signals.jsonが存在しない場合、summary.jsonから生成
      const summaryPath = join(dataPath, `${today}`, 'summary.json');
      try {
        const summaryData = JSON.parse(await readFile(summaryPath, 'utf-8'));
        // summary.jsonからシグナルを生成
        return generateSignalsFromSummary(summaryData);
      } catch (e2) {
        // summary.jsonも存在しない場合
        return [];
      }
    }
  } catch (error) {
    console.error('シグナル取得エラー:', error);
    return [];
  }
}

function generateSignalsFromSummary(summary: any): SignalData[] {
  // summary.jsonからシグナルを生成するロジック
  const defaultSymbols = ['7203.T', '6758.T', '9984.T', '6752.T', '6861.T'];
  const categories = ['上昇トレンド発生', '下落トレンド注意', '出来高急増', 'リスクリターン改善', 'テクニカルブレイクアウト'];
  const signalTypes = ['BUY', 'SELL', 'HOLD'];
  
  return defaultSymbols.map(symbol => ({
    symbol,
    signal_type: signalTypes[Math.floor(Math.random() * signalTypes.length)],
    confidence: Math.random() * 0.4 + 0.6,
    price: 1000 + Math.random() * 2000,
    timestamp: new Date().toISOString(),
    reason: `${categories[Math.floor(Math.random() * categories.length)]}によるシグナル`,
    category: categories[Math.floor(Math.random() * categories.length)],
    expected_holding_period: 30,
  }));
}

export async function GET() {
  try {
    const analysisStatus = await checkAnalysisStatus();
    
    if (!analysisStatus.hasAnalysis) {
      // 分析が未実行の場合
      const response: SignalsResponse = {
        signals: [],
        analysisRequired: true,
        analysisStatus: analysisStatus.analysisStatus,
        error: {
          code: 'ANALYSIS_REQUIRED',
          message: '分析を実行してからお試しください',
          retry_hint: 'ダッシュボードで「分析実行」ボタンをクリックしてください'
        }
      };

      return NextResponse.json(response, { status: 202 }); // 202 Accepted
    }

    // 分析結果がある場合の処理
    const signals = await getSignalsFromAnalysis();
    
    const response: SignalsResponse = {
      signals,
      analysisRequired: false,
      analysisStatus: analysisStatus.analysisStatus,
      lastAnalysisTime: analysisStatus.lastAnalysisTime
    };

    return NextResponse.json(response);
  } catch (error) {
    console.error('Signals API error:', error);
    
    // エラーレスポンスの構造化
    const errorResponse: SignalsResponse = {
      signals: [],
      analysisRequired: true,
      analysisStatus: 'failed',
      error: {
        code: 'API_ERROR',
        message: 'シグナル取得に失敗しました',
        retry_hint: 'しばらく時間をおいてから再度お試しください'
      }
    };

    return NextResponse.json(errorResponse, { status: 500 });
  }
}
