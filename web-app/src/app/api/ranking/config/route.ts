import { NextRequest, NextResponse } from 'next/server';

export async function GET() {
  try {
    // デフォルト設定を返す
    const defaultConfig = {
      maxCandidates: 5,
      minScore: 0.6,
      rules: {
        liquidity: {
          enabled: true,
          percentile: 70
        },
        trend: {
          enabled: true,
          weeks13vs26: true,
          returnPercentile: 40
        },
        valuation: {
          enabled: true,
          pbrPercentile: 50,
          perPercentile: 40
        },
        quality: {
          enabled: true,
          roePercentile: 40
        },
        exclusions: {
          enabled: true,
          excludeNonTSE: true,
          excludeSpecialAttention: true,
          excludeEarningsDay: true,
          excludeLimitUp: true
        }
      },
      weights: {
        trend: 0.4,
        valuation: 0.3,
        quality: 0.3
      }
    };

    return NextResponse.json({ config: defaultConfig });
  } catch (error) {
    console.error('設定取得エラー:', error);
    return NextResponse.json(
      { error: '設定の取得に失敗しました' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const config = await request.json();
    
    // 設定の検証
    if (!config || typeof config !== 'object') {
      return NextResponse.json(
        { error: '無効な設定データです' },
        { status: 400 }
      );
    }

    // 設定を保存（実際の実装ではデータベースに保存）
    console.log('ランキング設定を保存:', config);
    
    // 設定の妥当性チェック
    const validation = validateConfig(config);
    if (!validation.valid) {
      return NextResponse.json(
        { error: validation.message },
        { status: 400 }
      );
    }

    return NextResponse.json({ 
      message: '設定が保存されました',
      config 
    });
  } catch (error) {
    console.error('設定保存エラー:', error);
    return NextResponse.json(
      { error: '設定の保存に失敗しました' },
      { status: 500 }
    );
  }
}

function validateConfig(config: any): { valid: boolean; message?: string } {
  // 必須フィールドのチェック
  if (!config.rules || !config.weights) {
    return { valid: false, message: '必須フィールドが不足しています' };
  }

  // 重み付けの合計が1.0に近いかチェック
  const totalWeight = config.weights.trend + config.weights.valuation + config.weights.quality;
  if (Math.abs(totalWeight - 1.0) > 0.01) {
    return { valid: false, message: '重み付けの合計が1.0になるように設定してください' };
  }

  // 分位値の範囲チェック
  if (config.rules.liquidity && (config.rules.liquidity.percentile < 50 || config.rules.liquidity.percentile > 90)) {
    return { valid: false, message: '流動性分位値は50-90の範囲で設定してください' };
  }

  if (config.rules.trend && (config.rules.trend.returnPercentile < 20 || config.rules.trend.returnPercentile > 60)) {
    return { valid: false, message: 'トレンド分位値は20-60の範囲で設定してください' };
  }

  if (config.rules.valuation && (config.rules.valuation.pbrPercentile < 30 || config.rules.valuation.pbrPercentile > 70)) {
    return { valid: false, message: 'PBR分位値は30-70の範囲で設定してください' };
  }

  if (config.rules.quality && (config.rules.quality.roePercentile < 20 || config.rules.quality.roePercentile > 60)) {
    return { valid: false, message: 'ROE分位値は20-60の範囲で設定してください' };
  }

  return { valid: true };
}
