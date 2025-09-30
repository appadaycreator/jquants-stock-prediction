import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
  const configDir = path.join(process.cwd(), 'config');
  const files = ['core.yaml', 'api.yaml', 'data.yaml', 'models.yaml'];
  const configContents: Record<string, string | null> = {};
  for (const f of files) {
    const p = path.join(configDir, f);
    configContents[f] = fs.existsSync(p) ? fs.readFileSync(p, 'utf-8') : null;
  }

  // .env（存在する場合のみ）
  const envPath = path.join(process.cwd(), '.env');
  const envLocalPath = path.join(process.cwd(), '.env.local');
  const envContent = fs.existsSync(envPath) ? fs.readFileSync(envPath, 'utf-8') : null;
  const envLocalContent = fs.existsSync(envLocalPath) ? fs.readFileSync(envLocalPath, 'utf-8') : null;

  return NextResponse.json({
    ok: true,
    config: configContents,
    env: { '.env': envContent, '.env.local': envLocalContent },
  });
}


