import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import { withIdempotency } from '../_idempotency';

function getSettingsPath() {
  // public/data に保存（静的配信も可能に）
  const dataDir = path.join(process.cwd(), 'public', 'data');
  if (!fs.existsSync(dataDir)) {
    fs.mkdirSync(dataDir, { recursive: true });
  }
  return path.join(dataDir, 'risk_settings.json');
}

function getDefaultSettings() {
  return {
    enabled: true,
    maxLoss: {
      enabled: true,
      max_loss_percent: 0.05, // 5%
      auto_stop_loss_threshold: 0.08 // 8%
    },
    volatility: {
      enabled: true,
      high_vol_threshold: 0.4, // 年率40%
      extreme_vol_threshold: 0.6, // 年率60%
      high_vol_multiplier: 0.7, // 高ボラ時の縮小係数
      extreme_vol_multiplier: 0.4 // 極端ボラ時の縮小係数
    },
    enforcement: {
      block_violation_signals: true // 違反提案は出さない
    },
    last_updated: new Date().toISOString()
  };
}

export async function GET() {
  const settingsPath = getSettingsPath();
  try {
    if (!fs.existsSync(settingsPath)) {
      const defaults = getDefaultSettings();
      fs.writeFileSync(settingsPath, JSON.stringify(defaults, null, 2));
      return NextResponse.json(defaults);
    }
    const raw = fs.readFileSync(settingsPath, 'utf-8');
    const json = JSON.parse(raw);
    return NextResponse.json(json);
  } catch (e) {
    return NextResponse.json(getDefaultSettings(), { status: 200 });
  }
}

export const POST = withIdempotency(async function POST(req: NextRequest) {
  const payload = await req.json().catch(() => ({}));

  // 簡易検証
  const errs: string[] = [];
  const maxp = payload?.maxLoss?.max_loss_percent;
  if (typeof maxp !== 'undefined' && (isNaN(maxp) || maxp <= 0 || maxp > 0.5)) {
    errs.push('max_loss_percent は 0 < p <= 0.5 の範囲で指定してください');
  }
  const autoStop = payload?.maxLoss?.auto_stop_loss_threshold;
  if (typeof autoStop !== 'undefined' && (isNaN(autoStop) || autoStop <= 0 || autoStop > 0.9)) {
    errs.push('auto_stop_loss_threshold は 0 < p <= 0.9 の範囲で指定してください');
  }
  if (errs.length) {
    return NextResponse.json({ ok: false, errors: errs }, { status: 400 });
  }

  // 既存とマージ保存
  const settingsPath = getSettingsPath();
  let current = getDefaultSettings();
  try {
    if (fs.existsSync(settingsPath)) {
      current = JSON.parse(fs.readFileSync(settingsPath, 'utf-8'));
    }
  } catch {}

  const next = {
    ...current,
    ...payload,
    maxLoss: { ...current.maxLoss, ...payload?.maxLoss },
    volatility: { ...current.volatility, ...payload?.volatility },
    enforcement: { ...current.enforcement, ...payload?.enforcement },
    last_updated: new Date().toISOString(),
  };

  fs.writeFileSync(settingsPath, JSON.stringify(next, null, 2));
  return NextResponse.json({ ok: true, settings: next });
});


