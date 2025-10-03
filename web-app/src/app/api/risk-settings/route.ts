import { NextRequest, NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';

// リスク設定ファイルのパス
const RISK_SETTINGS_PATH = path.join(process.cwd(), 'web-app', 'public', 'data', 'risk_settings.json');

// デフォルト設定
const DEFAULT_RISK_SETTINGS = {
  enabled: true,
  maxLoss: {
    enabled: true,
    max_loss_percent: 0.05,
    auto_stop_loss_threshold: 0.08
  },
  volatility: {
    enabled: true,
    high_vol_threshold: 0.4,
    extreme_vol_threshold: 0.6,
    high_vol_multiplier: 0.7,
    extreme_vol_multiplier: 0.4
  },
  enforcement: {
    block_violation_signals: true
  },
  last_updated: new Date().toISOString()
};

// GET: リスク設定を取得
export async function GET(request: NextRequest) {
  try {
    // ファイルが存在するかチェック
    try {
      await fs.access(RISK_SETTINGS_PATH);
    } catch (error) {
      // ファイルが存在しない場合はデフォルト設定を返す
      console.log('リスク設定ファイルが見つからないため、デフォルト設定を返します');
      return NextResponse.json(DEFAULT_RISK_SETTINGS);
    }

    // ファイルを読み込み
    const fileContent = await fs.readFile(RISK_SETTINGS_PATH, 'utf-8');
    const settings = JSON.parse(fileContent);

    return NextResponse.json(settings);
  } catch (error) {
    console.error('リスク設定の読み込みエラー:', error);
    return NextResponse.json(
      { error: 'リスク設定の読み込みに失敗しました' },
      { status: 500 }
    );
  }
}

// POST: リスク設定を保存
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // バリデーション
    if (!body || typeof body !== 'object') {
      return NextResponse.json(
        { error: '無効なリクエストボディです' },
        { status: 400 }
      );
    }

    // maxLossのバリデーション
    if (body.maxLoss?.max_loss_percent !== undefined) {
      const maxLossPercent = body.maxLoss.max_loss_percent;
      if (typeof maxLossPercent !== 'number' || maxLossPercent <= 0 || maxLossPercent > 0.5) {
        return NextResponse.json(
          { error: '最大損失率は 0 < p <= 0.5 で指定してください' },
          { status: 400 }
        );
      }
    }

    // 設定にタイムスタンプを追加
    const settingsToSave = {
      ...body,
      last_updated: new Date().toISOString()
    };

    // ディレクトリが存在することを確認
    const dir = path.dirname(RISK_SETTINGS_PATH);
    try {
      await fs.access(dir);
    } catch (error) {
      await fs.mkdir(dir, { recursive: true });
    }

    // ファイルに保存
    await fs.writeFile(RISK_SETTINGS_PATH, JSON.stringify(settingsToSave, null, 2));

    return NextResponse.json({
      success: true,
      settings: settingsToSave,
      message: 'リスク設定を保存しました'
    });
  } catch (error) {
    console.error('リスク設定の保存エラー:', error);
    return NextResponse.json(
      { error: 'リスク設定の保存に失敗しました' },
      { status: 500 }
    );
  }
}
