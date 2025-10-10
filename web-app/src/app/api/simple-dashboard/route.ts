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
function computePortfolioSummary(positions: SimplePosition[]): SimplePortfolioSummary {
  if (!positions || positions.length === 0) {
    return {
      totalInvestment: 0,
      currentValue: 0,
      unrealizedPnL: 0,
      unrealizedPnLPercent: 0,
      bestPerformer: { symbol: "", symbolName: "", return: 0 },
      worstPerformer: { symbol: "", symbolName: "", return: 0 },
    };
  }

  const totalInvestment = positions.reduce((sum, p) => sum + p.cost, 0);
  const currentValue = positions.reduce((sum, p) => sum + p.currentValue, 0);
  const unrealizedPnL = positions.reduce((sum, p) => sum + p.unrealizedPnL, 0);
  const unrealizedPnLPercent = totalInvestment > 0 ? (unrealizedPnL / totalInvestment) * 100 : 0;

  const best = [...positions].sort((a, b) => b.unrealizedPnLPercent - a.unrealizedPnLPercent)[0];
  const worst = [...positions].sort((a, b) => a.unrealizedPnLPercent - b.unrealizedPnLPercent)[0];

  return {
    totalInvestment,
    currentValue,
    unrealizedPnL,
    unrealizedPnLPercent: Number(unrealizedPnLPercent.toFixed(2)),
    bestPerformer: best
      ? { symbol: best.symbol, symbolName: best.symbolName, return: Number(best.unrealizedPnLPercent.toFixed(1)) }
      : { symbol: "", symbolName: "", return: 0 },
    worstPerformer: worst
      ? { symbol: worst.symbol, symbolName: worst.symbolName, return: Number(worst.unrealizedPnLPercent.toFixed(1)) }
      : { symbol: "", symbolName: "", return: 0 },
  };
}

// サンプルデータ生成関数（保有銘柄は外部入力に応じて可変）
function generateSampleData(positions: SimplePosition[] = []): SimpleDashboardData {
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
    portfolioSummary: computePortfolioSummary(positions),
    positions,
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
    
    // クッキーに保存されたユーザーポートフォリオがあれば使用
    // 形式: JSON.stringify([{ symbol, symbolName, quantity, averagePrice }])
    let userPositions: SimplePosition[] = [];
    try {
      const cookie = request.cookies.get("user_portfolio");
      if (cookie && cookie.value) {
        const raw = JSON.parse(cookie.value);
        if (Array.isArray(raw) && raw.length > 0) {
          // サーバー側では現在価格などは未知のため、保守的にゼロで初期化
          userPositions = raw.map((item: any) => ({
            symbol: String(item.symbol || item.code || ""),
            symbolName: String(item.symbolName || item.name || ""),
            quantity: Number(item.quantity || item.shares || 0),
            averagePrice: Number(item.averagePrice || 0),
            currentPrice: Number(item.currentPrice || item.price || 0),
            cost: Number(item.averagePrice || 0) * Number(item.quantity || item.shares || 0),
            currentValue: Number(item.currentPrice || item.price || 0) * Number(item.quantity || item.shares || 0),
            unrealizedPnL: (Number(item.currentPrice || item.price || 0) - Number(item.averagePrice || 0)) * Number(item.quantity || item.shares || 0),
            unrealizedPnLPercent: Number(item.averagePrice || 0) > 0
              ? ((Number(item.currentPrice || item.price || 0) - Number(item.averagePrice || 0)) / Number(item.averagePrice || 0)) * 100
              : 0,
            action: "HOLD",
            confidence: 0,
          }));
        }
      }
    } catch {
      // クッキーが不正でも画面は壊さない
      userPositions = [];
    }

    // 保有未設定なら空配列のまま返す（これによりフロントは空状態を表示）
    const data = generateSampleData(userPositions);
    
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
