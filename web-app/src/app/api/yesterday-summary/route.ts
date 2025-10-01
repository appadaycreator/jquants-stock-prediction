import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // 昨日のサマリーの実装
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    
    const yesterdaySummary = {
      date: yesterday.toISOString().split('T')[0],
      summary: {
        totalAnalyses: 5,
        successfulAnalyses: 5,
        failedAnalyses: 0,
        averageAccuracy: 0.84,
        bestModel: 'xgboost',
        worstModel: 'linear_regression'
      },
      performance: {
        totalExecutionTime: '2.5 hours',
        averageAnalysisTime: '30 minutes',
        peakMemoryUsage: '1.2GB',
        cacheHitRate: 0.85
      },
      recommendations: [
        'XGBoostモデルの性能が良好です',
        '線形回帰モデルの精度向上を検討してください',
        'キャッシュヒット率が高いため、効率的に動作しています'
      ]
    };

    return NextResponse.json(yesterdaySummary);
  } catch (error) {
    console.error('Yesterday summary error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
