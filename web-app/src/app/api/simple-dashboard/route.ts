import { NextRequest, NextResponse } from "next/server";

// シンプルダッシュボード用のデータ型定義
interface SimpleRecommendation {
  id: string;
  symbol: string;
  symbolName: string;
  action: "BUY" | "SELL" | "HOLD";
  reason: string;
  confidence: number;
  expectedReturn: number;
  priority: "HIGH" | "MEDIUM" | "LOW";
  timeframe: string;
}

interface SimplePortfolioSummary {
  totalInvestment: number;
  currentValue: number;
  unrealizedPnL: number;
  unrealizedPnLPercent: number;
  bestPerformer: {
    symbol: string;
    symbolName: string;
    return: number;
  };
  worstPerformer: {
    symbol: string;
    symbolName: string;
    return: number;
  };
}

interface SimplePosition {
  symbol: string;
  symbolName: string;
  quantity: number;
  averagePrice: number;
  currentPrice: number;
  cost: number;
  currentValue: number;
  unrealizedPnL: number;
  unrealizedPnLPercent: number;
  action: "BUY_MORE" | "SELL" | "HOLD";
  confidence: number;
}

interface SimpleDashboardData {
  lastUpdate: string;
  recommendations: SimpleRecommendation[];
  portfolioSummary: SimplePortfolioSummary;
  positions: SimplePosition[];
  marketStatus: {
    isOpen: boolean;
    nextOpen: string;
  };
}

// サンプルデータ生成関数
function generateSampleData(): SimpleDashboardData {
  const now = new Date();
  const isMarketOpen = now.getHours() >= 9 && now.getHours() < 15 && now.getDay() >= 1 && now.getDay() <= 5;
  
  return {
    lastUpdate: now.toISOString(),
    recommendations: [
      {
        id: "1",
        symbol: "7203",
        symbolName: "トヨタ自動車",
        action: "BUY",
        reason: "業績好調、EV戦略の進展により中長期的な成長が期待される",
        confidence: 85,
        expectedReturn: 12.5,
        priority: "HIGH",
        timeframe: "3ヶ月",
      },
      {
        id: "2",
        symbol: "6758",
        symbolName: "ソニーグループ",
        action: "HOLD",
        reason: "ゲーム事業の回復待ち、エンターテインメント事業は堅調",
        confidence: 70,
        expectedReturn: 5.2,
        priority: "MEDIUM",
        timeframe: "6ヶ月",
      },
      {
        id: "3",
        symbol: "9984",
        symbolName: "ソフトバンクグループ",
        action: "SELL",
        reason: "投資先の評価減リスク、金利上昇による影響",
        confidence: 75,
        expectedReturn: -8.3,
        priority: "HIGH",
        timeframe: "1ヶ月",
      },
    ],
    portfolioSummary: {
      totalInvestment: 1000000,
      currentValue: 1050000,
      unrealizedPnL: 50000,
      unrealizedPnLPercent: 5.0,
      bestPerformer: {
        symbol: "7203",
        symbolName: "トヨタ自動車",
        return: 15.2,
      },
      worstPerformer: {
        symbol: "9984",
        symbolName: "ソフトバンクグループ",
        return: -12.8,
      },
    },
    positions: [
      {
        symbol: "7203",
        symbolName: "トヨタ自動車",
        quantity: 100,
        averagePrice: 2500,
        currentPrice: 2800,
        cost: 250000,
        currentValue: 280000,
        unrealizedPnL: 30000,
        unrealizedPnLPercent: 12.0,
        action: "BUY_MORE",
        confidence: 85,
      },
      {
        symbol: "6758",
        symbolName: "ソニーグループ",
        quantity: 50,
        averagePrice: 12000,
        currentPrice: 11500,
        cost: 600000,
        currentValue: 575000,
        unrealizedPnL: -25000,
        unrealizedPnLPercent: -4.2,
        action: "HOLD",
        confidence: 70,
      },
      {
        symbol: "9984",
        symbolName: "ソフトバンクグループ",
        quantity: 30,
        averagePrice: 8000,
        currentPrice: 7200,
        cost: 240000,
        currentValue: 216000,
        unrealizedPnL: -24000,
        unrealizedPnLPercent: -10.0,
        action: "SELL",
        confidence: 75,
      },
    ],
    marketStatus: {
      isOpen: isMarketOpen,
      nextOpen: isMarketOpen ? "" : "2025-01-06T09:00:00Z",
    },
  };
}

// GET: シンプルダッシュボードデータ取得
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const refresh = searchParams.get("refresh") === "true";
    
    // 実際の実装では、ここでデータベースやAPIからデータを取得
    // 現在はサンプルデータを返す
    const data = generateSampleData();
    
    return NextResponse.json({
      success: true,
      data,
      metadata: {
        timestamp: new Date().toISOString(),
        version: "1.0.0",
      },
    });
  } catch (error) {
    console.error("シンプルダッシュボードデータ取得エラー:", error);
    
    return NextResponse.json({
      success: false,
      error: {
        code: "DASHBOARD_DATA_ERROR",
        message: "ダッシュボードデータの取得に失敗しました",
      },
      metadata: {
        timestamp: new Date().toISOString(),
        version: "1.0.0",
      },
    }, { status: 500 });
  }
}

// POST: データ更新実行
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { forceRefresh } = body;
    
    // 実際の実装では、ここでデータの強制更新を実行
    // 現在はサンプルデータを返す
    const data = generateSampleData();
    
    return NextResponse.json({
      success: true,
      data,
      message: "データを更新しました",
      metadata: {
        timestamp: new Date().toISOString(),
        version: "1.0.0",
      },
    });
  } catch (error) {
    console.error("シンプルダッシュボードデータ更新エラー:", error);
    
    return NextResponse.json({
      success: false,
      error: {
        code: "DASHBOARD_UPDATE_ERROR",
        message: "ダッシュボードデータの更新に失敗しました",
      },
      metadata: {
        timestamp: new Date().toISOString(),
        version: "1.0.0",
      },
    }, { status: 500 });
  }
}
