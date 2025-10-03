/**
 * 強化された株価分析システム
 * 全銘柄データを活用した投資推奨システム
 */

export interface StockInfo {
  code: string;
  name: string;
  sector: string;
  market: string;
  currentPrice?: number;
  change?: number;
  changePercent?: number;
  volume?: number;
  updated_at: string;
}

export interface AnalysisResult {
  symbol: string;
  name: string;
  sector: string;
  market: string;
  currentPrice: number;
  priceChange: number;
  priceChangePercent: number;
  recommendation: "STRONG_BUY" | "BUY" | "HOLD" | "SELL" | "STRONG_SELL";
  confidence: number;
  reasons: string[];
  riskLevel: "LOW" | "MEDIUM" | "HIGH";
  targetPrice?: number;
  stopLoss?: number;
  score: number;
  technicalIndicators: {
    sma5: number;
    sma10: number;
    sma25: number;
    sma50: number;
    rsi: number;
    macd: {
      macd: number;
      signal: number;
      histogram: number;
    };
    bollingerBands: {
      upper: number;
      middle: number;
      lower: number;
    };
  };
}

export interface MarketAnalysis {
  totalStocks: number;
  analyzedStocks: number;
  recommendations: {
    STRONG_BUY: number;
    BUY: number;
    HOLD: number;
    SELL: number;
    STRONG_SELL: number;
  };
  topGainers: Array<{
    symbol: string;
    name: string;
    changePercent: number;
  }>;
  topLosers: Array<{
    symbol: string;
    name: string;
    changePercent: number;
  }>;
  sectorPerformance: Record<string, number>;
}

/**
 * 全銘柄データを取得
 */
export async function getAllStocks(): Promise<StockInfo[]> {
  try {
    const response = await fetch("/data/listed_index.json");
    if (!response.ok) {
      throw new Error("銘柄データの取得に失敗しました");
    }
    
    const data = await response.json();
    return data.stocks || [];
  } catch (error) {
    console.error("全銘柄データの取得エラー:", error);
    return [];
  }
}

/**
 * セクター別パフォーマンス分析
 */
export function analyzeSectorPerformance(stocks: StockInfo[]): Record<string, number> {
  const sectorPerformance: Record<string, number> = {};
  const sectorData: Record<string, { total: number; count: number }> = {};

  stocks.forEach(stock => {
    if (stock.sector && stock.changePercent !== undefined) {
      if (!sectorData[stock.sector]) {
        sectorData[stock.sector] = { total: 0, count: 0 };
      }
      sectorData[stock.sector].total += stock.changePercent;
      sectorData[stock.sector].count += 1;
    }
  });

  Object.entries(sectorData).forEach(([sector, data]) => {
    sectorPerformance[sector] = data.count > 0 ? data.total / data.count : 0;
  });

  return sectorPerformance;
}

/**
 * 個別銘柄の分析スコア計算
 */
export function calculateStockScore(stock: StockInfo, sectorPerformance: Record<string, number>): number {
  let score = 0;

  // 価格変動スコア (40%)
  if (stock.changePercent !== undefined) {
    const priceScore = Math.max(0, Math.min(100, 50 + stock.changePercent * 2));
    score += priceScore * 0.4;
  }

  // セクターパフォーマンススコア (30%)
  if (stock.sector && sectorPerformance[stock.sector] !== undefined) {
    const sectorScore = Math.max(0, Math.min(100, 50 + sectorPerformance[stock.sector] * 2));
    score += sectorScore * 0.3;
  }

  // 市場区分スコア (20%)
  const marketScore = {
    "プライム": 80,
    "スタンダード": 60,
    "グロース": 40,
  }[stock.market] || 50;
  score += marketScore * 0.2;

  // 出来高スコア (10%)
  if (stock.volume !== undefined) {
    const volumeScore = Math.min(100, Math.log10(stock.volume + 1) * 10);
    score += volumeScore * 0.1;
  }

  return Math.max(0, Math.min(100, score));
}

/**
 * 投資推奨の生成
 */
export function generateRecommendation(score: number, changePercent: number): {
  recommendation: AnalysisResult["recommendation"];
  confidence: number;
  reasons: string[];
  riskLevel: AnalysisResult["riskLevel"];
} {
  const reasons: string[] = [];
  let recommendation: AnalysisResult["recommendation"];
  let confidence: number;
  let riskLevel: AnalysisResult["riskLevel"];

  if (score >= 80) {
    recommendation = "STRONG_BUY";
    confidence = 0.9;
    reasons.push("総合スコアが非常に高い");
    riskLevel = "LOW";
  } else if (score >= 65) {
    recommendation = "BUY";
    confidence = 0.8;
    reasons.push("総合スコアが高い");
    riskLevel = "LOW";
  } else if (score >= 45) {
    recommendation = "HOLD";
    confidence = 0.7;
    reasons.push("総合スコアが中程度");
    riskLevel = "MEDIUM";
  } else if (score >= 25) {
    recommendation = "SELL";
    confidence = 0.8;
    reasons.push("総合スコアが低い");
    riskLevel = "HIGH";
  } else {
    recommendation = "STRONG_SELL";
    confidence = 0.9;
    reasons.push("総合スコアが非常に低い");
    riskLevel = "HIGH";
  }

  // 価格変動による調整
  if (changePercent > 5) {
    reasons.push("大幅な上昇を記録");
    if (recommendation === "BUY" || recommendation === "STRONG_BUY") {
      confidence = Math.min(0.95, confidence + 0.1);
    }
  } else if (changePercent < -5) {
    reasons.push("大幅な下落を記録");
    if (recommendation === "SELL" || recommendation === "STRONG_SELL") {
      confidence = Math.min(0.95, confidence + 0.1);
    }
  }

  return { recommendation, confidence, reasons, riskLevel };
}

/**
 * 個別銘柄の詳細分析
 */
export function analyzeStock(stock: StockInfo, sectorPerformance: Record<string, number>): AnalysisResult {
  const score = calculateStockScore(stock, sectorPerformance);
  const { recommendation, confidence, reasons, riskLevel } = generateRecommendation(
    score,
    stock.changePercent || 0,
  );

  // テクニカル指標の生成（実際の運用では実データを使用）
  const currentPrice = stock.currentPrice || Math.floor(Math.random() * 5000) + 1000;
  const technicalIndicators = {
    sma5: currentPrice * (0.95 + Math.random() * 0.1),
    sma10: currentPrice * (0.95 + Math.random() * 0.1),
    sma25: currentPrice * (0.90 + Math.random() * 0.2),
    sma50: currentPrice * (0.85 + Math.random() * 0.3),
    rsi: Math.random() * 100,
    macd: {
      macd: (Math.random() - 0.5) * 100,
      signal: (Math.random() - 0.5) * 100,
      histogram: (Math.random() - 0.5) * 50,
    },
    bollingerBands: {
      upper: currentPrice * 1.1,
      middle: currentPrice,
      lower: currentPrice * 0.9,
    },
  };

  return {
    symbol: stock.code,
    name: stock.name,
    sector: stock.sector,
    market: stock.market,
    currentPrice,
    priceChange: stock.change || 0,
    priceChangePercent: stock.changePercent || 0,
    recommendation,
    confidence,
    reasons,
    riskLevel,
    targetPrice: recommendation.includes("BUY") ? currentPrice * 1.15 : undefined,
    stopLoss: recommendation.includes("SELL") ? currentPrice * 0.85 : undefined,
    score,
    technicalIndicators,
  };
}

/**
 * 市場全体の分析
 */
export async function analyzeMarket(): Promise<MarketAnalysis> {
  const stocks = await getAllStocks();
  const sectorPerformance = analyzeSectorPerformance(stocks);
  
  const analysisResults = stocks
    .filter(stock => stock.currentPrice && stock.changePercent !== undefined)
    .map(stock => analyzeStock(stock, sectorPerformance));

  const recommendations = {
    STRONG_BUY: 0,
    BUY: 0,
    HOLD: 0,
    SELL: 0,
    STRONG_SELL: 0,
  };

  analysisResults.forEach(result => {
    recommendations[result.recommendation]++;
  });

  const topGainers = stocks
    .filter(stock => stock.changePercent !== undefined)
    .sort((a, b) => (b.changePercent || 0) - (a.changePercent || 0))
    .slice(0, 10)
    .map(stock => ({
      symbol: stock.code,
      name: stock.name,
      changePercent: stock.changePercent || 0,
    }));

  const topLosers = stocks
    .filter(stock => stock.changePercent !== undefined)
    .sort((a, b) => (a.changePercent || 0) - (b.changePercent || 0))
    .slice(0, 10)
    .map(stock => ({
      symbol: stock.code,
      name: stock.name,
      changePercent: stock.changePercent || 0,
    }));

  return {
    totalStocks: stocks.length,
    analyzedStocks: analysisResults.length,
    recommendations,
    topGainers,
    topLosers,
    sectorPerformance,
  };
}

/**
 * 推奨銘柄の取得
 */
export async function getRecommendedStocks(
  limit: number = 20,
  recommendation?: AnalysisResult["recommendation"],
): Promise<AnalysisResult[]> {
  const stocks = await getAllStocks();
  const sectorPerformance = analyzeSectorPerformance(stocks);
  
  const analysisResults = stocks
    .filter(stock => stock.currentPrice && stock.changePercent !== undefined)
    .map(stock => analyzeStock(stock, sectorPerformance));

  let filteredResults = analysisResults;
  
  if (recommendation) {
    filteredResults = analysisResults.filter(result => result.recommendation === recommendation);
  }

  return filteredResults
    .sort((a, b) => b.score - a.score)
    .slice(0, limit);
}
