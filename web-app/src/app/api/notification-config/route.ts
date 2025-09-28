import { NextRequest, NextResponse } from 'next/server';

import fs from 'fs';
import path from 'path';
import yaml from 'js-yaml';

export const dynamic = 'force-static';

const CONFIG_PATH = path.join(process.cwd(), '..', 'notification_config.yaml');

export async function GET() {
  try {
    if (!fs.existsSync(CONFIG_PATH)) {
      return NextResponse.json({ error: '設定ファイルが見つかりません' }, { status: 404 });
    }

    const configContent = fs.readFileSync(CONFIG_PATH, 'utf8');
    const config = yaml.load(configContent);
    
    return NextResponse.json(config);
  } catch (error) {
    console.error('設定読み込みエラー:', error);
    return NextResponse.json({ error: '設定の読み込みに失敗しました' }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    const newConfig = await request.json();
    
    // YAML形式で保存
    const yamlContent = yaml.dump(newConfig, {
      indent: 2,
      lineWidth: -1,
      noRefs: true
    });
    
    fs.writeFileSync(CONFIG_PATH, yamlContent, 'utf8');
    
    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('設定保存エラー:', error);
    return NextResponse.json({ error: '設定の保存に失敗しました' }, { status: 500 });
  }
}
