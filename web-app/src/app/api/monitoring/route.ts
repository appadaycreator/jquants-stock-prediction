import { NextRequest, NextResponse } from 'next/server';
import { writeFile, readFile, mkdir } from 'fs/promises';
import { existsSync } from 'fs';
import path from 'path';

// 監視設定の保存先
const MONITORING_DIR = path.join(process.cwd(), 'data', 'monitoring');
const STOCKS_FILE = path.join(MONITORING_DIR, 'monitored_stocks.json');
const CONFIG_FILE = path.join(MONITORING_DIR, 'monitoring_config.json');

// ディレクトリが存在しない場合は作成
async function ensureDirectoryExists() {
  if (!existsSync(MONITORING_DIR)) {
    await mkdir(MONITORING_DIR, { recursive: true });
  }
}

// GET: 監視中の銘柄一覧を取得
export async function GET() {
  try {
    await ensureDirectoryExists();
    
    if (!existsSync(STOCKS_FILE)) {
      return NextResponse.json({ stocks: [], config: null });
    }
    
    const stocksData = await readFile(STOCKS_FILE, 'utf-8');
    const stocks = JSON.parse(stocksData);
    
    let config = null;
    if (existsSync(CONFIG_FILE)) {
      const configData = await readFile(CONFIG_FILE, 'utf-8');
      config = JSON.parse(configData);
    }
    
    return NextResponse.json({ stocks, config });
  } catch (error) {
    console.error('監視データ取得エラー:', error);
    return NextResponse.json(
      { error: '監視データの取得に失敗しました' },
      { status: 500 }
    );
  }
}

// POST: 監視銘柄の更新
export async function POST(request: NextRequest) {
  try {
    await ensureDirectoryExists();
    
    const body = await request.json();
    const { stocks, config } = body;
    
    // 監視銘柄を保存
    if (stocks) {
      await writeFile(STOCKS_FILE, JSON.stringify(stocks, null, 2));
    }
    
    // 監視設定を保存
    if (config) {
      await writeFile(CONFIG_FILE, JSON.stringify(config, null, 2));
    }
    
    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('監視データ保存エラー:', error);
    return NextResponse.json(
      { error: '監視データの保存に失敗しました' },
      { status: 500 }
    );
  }
}

// PUT: 監視銘柄の更新
export async function PUT(request: NextRequest) {
  try {
    await ensureDirectoryExists();
    
    const body = await request.json();
    const { action, symbol, stock } = body;
    
    let stocks = [];
    if (existsSync(STOCKS_FILE)) {
      const stocksData = await readFile(STOCKS_FILE, 'utf-8');
      stocks = JSON.parse(stocksData);
    }
    
    switch (action) {
      case 'add':
        if (stock && !stocks.find(s => s.code === stock.code)) {
          stocks.push({
            ...stock,
            isMonitoring: true,
            lastUpdate: new Date().toISOString(),
            alerts: [],
          });
        }
        break;
        
      case 'remove':
        stocks = stocks.filter(s => s.code !== symbol);
        break;
        
      case 'toggle':
        stocks = stocks.map(s => 
          s.code === symbol 
            ? { ...s, isMonitoring: !s.isMonitoring }
            : s
        );
        break;
        
      case 'update':
        stocks = stocks.map(s => 
          s.code === symbol 
            ? { ...s, ...stock }
            : s
        );
        break;
    }
    
    await writeFile(STOCKS_FILE, JSON.stringify(stocks, null, 2));
    
    return NextResponse.json({ success: true, stocks });
  } catch (error) {
    console.error('監視データ更新エラー:', error);
    return NextResponse.json(
      { error: '監視データの更新に失敗しました' },
      { status: 500 }
    );
  }
}

// DELETE: 監視銘柄の削除
export async function DELETE(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const symbol = searchParams.get('symbol');
    
    if (!symbol) {
      return NextResponse.json(
        { error: '銘柄コードが必要です' },
        { status: 400 }
      );
    }
    
    if (existsSync(STOCKS_FILE)) {
      const stocksData = await readFile(STOCKS_FILE, 'utf-8');
      const stocks = JSON.parse(stocksData);
      const filteredStocks = stocks.filter(s => s.code !== symbol);
      
      await writeFile(STOCKS_FILE, JSON.stringify(filteredStocks, null, 2));
    }
    
    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('監視データ削除エラー:', error);
    return NextResponse.json(
      { error: '監視データの削除に失敗しました' },
      { status: 500 }
    );
  }
}
