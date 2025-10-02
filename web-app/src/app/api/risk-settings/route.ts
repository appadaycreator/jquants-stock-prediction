import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

// リスク設定のデフォルト値
const DEFAULT_RISK_SETTINGS = {
  maxPositionSize: 0.1, // 最大ポジションサイズ（ポートフォリオの10%）
  maxDrawdown: 0.15, // 最大ドローダウン（15%）
  stopLossPercentage: 0.05, // ストップロス（5%）
  takeProfitPercentage: 0.15, // 利確（15%）
  riskLevel: 'medium', // リスクレベル
  maxPositions: 10, // 最大ポジション数
  rebalanceThreshold: 0.05, // リバランス閾値（5%）
  alertThresholds: {
    highRisk: 0.8, // 高リスクアラート閾値
    mediumRisk: 0.6, // 中リスクアラート閾値
    lowRisk: 0.4, // 低リスクアラート閾値
  },
  autoRebalance: true, // 自動リバランス
  notifications: {
    email: true,
    browser: true,
    sms: false,
  },
  lastUpdated: new Date().toISOString(),
};

// リスク設定ファイルのパス
const RISK_SETTINGS_FILE = path.join(process.cwd(), 'web-app', 'public', 'data', 'risk_settings.json');

// GET: リスク設定を取得
export async function GET() {
  try {
    // ファイルが存在するかチェック
    if (fs.existsSync(RISK_SETTINGS_FILE)) {
      const fileContent = fs.readFileSync(RISK_SETTINGS_FILE, 'utf8');
      const settings = JSON.parse(fileContent);
      return NextResponse.json(settings);
    } else {
      // ファイルが存在しない場合はデフォルト設定を返す
      return NextResponse.json(DEFAULT_RISK_SETTINGS);
    }
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
        { error: '無効なリスク設定データです' },
        { status: 400 }
      );
    }

    // 設定データを更新
    const updatedSettings = {
      ...DEFAULT_RISK_SETTINGS,
      ...body,
      lastUpdated: new Date().toISOString(),
    };

    // ファイルに保存
    fs.writeFileSync(RISK_SETTINGS_FILE, JSON.stringify(updatedSettings, null, 2));
    
    return NextResponse.json({
      success: true,
      message: 'リスク設定が正常に保存されました',
      settings: updatedSettings,
    });
  } catch (error) {
    console.error('リスク設定の保存エラー:', error);
    return NextResponse.json(
      { error: 'リスク設定の保存に失敗しました' },
      { status: 500 }
    );
  }
}

// PUT: リスク設定を更新
export async function PUT(request: NextRequest) {
  try {
    const body = await request.json();
    
    // 既存の設定を読み込み
    let currentSettings = DEFAULT_RISK_SETTINGS;
    if (fs.existsSync(RISK_SETTINGS_FILE)) {
      const fileContent = fs.readFileSync(RISK_SETTINGS_FILE, 'utf8');
      currentSettings = JSON.parse(fileContent);
    }

    // 設定を更新
    const updatedSettings = {
      ...currentSettings,
      ...body,
      lastUpdated: new Date().toISOString(),
    };

    // ファイルに保存
    fs.writeFileSync(RISK_SETTINGS_FILE, JSON.stringify(updatedSettings, null, 2));
    
    return NextResponse.json({
      success: true,
      message: 'リスク設定が正常に更新されました',
      settings: updatedSettings,
    });
  } catch (error) {
    console.error('リスク設定の更新エラー:', error);
    return NextResponse.json(
      { error: 'リスク設定の更新に失敗しました' },
      { status: 500 }
    );
  }
}

// DELETE: リスク設定をリセット
export async function DELETE() {
  try {
    // ファイルが存在する場合は削除
    if (fs.existsSync(RISK_SETTINGS_FILE)) {
      fs.unlinkSync(RISK_SETTINGS_FILE);
    }
    
    return NextResponse.json({
      success: true,
      message: 'リスク設定がリセットされました',
      settings: DEFAULT_RISK_SETTINGS,
    });
  } catch (error) {
    console.error('リスク設定のリセットエラー:', error);
    return NextResponse.json(
      { error: 'リスク設定のリセットに失敗しました' },
      { status: 500 }
    );
  }
}
