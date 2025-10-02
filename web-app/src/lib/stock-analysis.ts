/**
 * 株価分析ロジック
 * 技術指標の計算と投資推奨の生成
 */

import { unifiedApiClient } from "./unified-api-client";

export interface StockData {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  marketCap: number;
  lastUpdated: string;
}

export interface TechnicalIndicators {
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
  bollinger: {
    upper: number;
    middle: number;
    lower: number;
  };
}

export interface AnalysisResult {
  symbol: string;
  name: string;
  currentPrice: number;
  priceChange: number;
  priceChangePercent: number;
  indicators: TechnicalIndicators;
  recommendation: "STRONG_BUY" | "BUY" | "HOLD" | "SELL" | "STRONG_SELL";
  confidence: number;
  reasons: string[];
  riskLevel: "LOW" | "MEDIUM" | "HIGH";
  targetPrice?: number;
}

export interface MarketSummary {
  totalSymbols: number;
  analyzedSymbols: number;
  recommendations: {
    STRONG_BUY: number;
    BUY: number;
    HOLD: number;
    SELL: number;
    STRONG_SELL: number;
  };
  topGainers: AnalysisResult[];
  topLosers: AnalysisResult[];
  lastUpdated: string;
}

/**
 * 単純移動平均を計算
 */
function calculateSMA(prices: number[], period: number): number {
  if (prices.length < period) return prices[prices.length - 1] || 0;
  const slice = prices.slice(-period);
  return slice.reduce((sum, price) => sum + price, 0) / slice.length;
}

/**
 * RSIを計算
 */
function calculateRSI(prices: number[], period: number = 14): number {
  if (prices.length < period + 1) return 50; // 中立値

  const changes = [];
  for (let i = 1; i < prices.length; i++) {
    changes.push(prices[i] - prices[i - 1]);
  }

  const gains = changes.slice(-period).filter(change => change > 0);
  const losses = changes.slice(-period).filter(change => change < 0).map(Math.abs);

  if (losses.length === 0) return 100;
  if (gains.length === 0) return 0;

  const avgGain = gains.reduce((sum, gain) => sum + gain, 0) / period;
  const avgLoss = losses.reduce((sum, loss) => sum + loss, 0) / period;

  if (avgLoss === 0) return 100;
  const rs = avgGain / avgLoss;
  return 100 - (100 / (1 + rs));
}

/**
 * MACDを計算
 */
function calculateMACD(prices: number[]): { macd: number; signal: number; histogram: number } {
  if (prices.length < 26) {
    return { macd: 0, signal: 0, histogram: 0 };
  }

  // EMA計算のヘルパー
  const calculateEMA = (data: number[], period: number): number[] => {
    const ema = [data[0]];
    const k = 2 / (period + 1);
    for (let i = 1; i < data.length; i++) {
      ema.push(data[i] * k + ema[i - 1] * (1 - k));
    }
    return ema;
  };

  const ema12 = calculateEMA(prices, 12);
  const ema26 = calculateEMA(prices, 26);
  
  const macdLine = ema12[ema12.length - 1] - ema26[ema26.length - 1];
  
  // シグナル線は簡易計算
  const macdValues = [];
  for (let i = 26; i < prices.length; i++) {
    macdValues.push(ema12[i] - ema26[i]);
  }
  
  const signalLine = calculateEMA(macdValues.slice(-9), 9);
  const signal = signalLine.length > 0 ? signalLine[signalLine.length - 1] : 0;
  
  return {
    macd: macdLine,
    signal,
    histogram: macdLine - signal,
  };
}

/**
 * ボリンジャーバンドを計算
 */
function calculateBollingerBands(prices: number[], period: number = 20): { upper: number; middle: number; lower: number } {
  if (prices.length < period) {
    const lastPrice = prices[prices.length - 1] || 0;
    return { upper: lastPrice, middle: lastPrice, lower: lastPrice };
  }

  const slice = prices.slice(-period);
  const middle = slice.reduce((sum, price) => sum + price, 0) / slice.length;
  
  const variance = slice.reduce((sum, price) => sum + Math.pow(price - middle, 2), 0) / slice.length;
  const stdDev = Math.sqrt(variance);
  
  return {
    upper: middle + (stdDev * 2),
    middle,
    lower: middle - (stdDev * 2),
  };
}

/**
 * 技術指標を計算
 */
function calculateTechnicalIndicators(stockData: StockData[]): TechnicalIndicators {
  const closePrices = stockData.map(d => d.close);
  
  return {
    sma5: calculateSMA(closePrices, 5),
    sma10: calculateSMA(closePrices, 10),
    sma25: calculateSMA(closePrices, 25),
    sma50: calculateSMA(closePrices, 50),
    rsi: calculateRSI(closePrices),
    macd: calculateMACD(closePrices),
    bollinger: calculateBollingerBands(closePrices),
  };
}

/**
 * 投資推奨を生成
 */
function generateRecommendation(
  stockData: StockData[],
  indicators: TechnicalIndicators,
): { recommendation: AnalysisResult["recommendation"]; confidence: number; reasons: string[]; riskLevel: AnalysisResult["riskLevel"]; targetPrice?: number } {
  const reasons: string[] = [];
  let buySignals = 0;
  let sellSignals = 0;
  let riskFactors = 0;

  const currentPrice = stockData[stockData.length - 1]?.close || 0;
  const previousPrice = stockData[stockData.length - 2]?.close || currentPrice;

  // トレンド分析
  if (indicators.sma5 > indicators.sma10 && indicators.sma10 > indicators.sma25) {
    buySignals += 2;
    reasons.push("短期上昇トレンド（SMA5 > SMA10 > SMA25）");
  } else if (indicators.sma5 < indicators.sma10 && indicators.sma10 < indicators.sma25) {
    sellSignals += 2;
    reasons.push("短期下降トレンド（SMA5 < SMA10 < SMA25）");
  }

  // 長期トレンド
  if (currentPrice > indicators.sma50) {
    buySignals += 1;
    reasons.push("長期上昇トレンド（価格 > SMA50）");
  } else {
    sellSignals += 1;
    reasons.push("長期下降トレンド（価格 < SMA50）");
  }

  // RSI分析
  if (indicators.rsi < 30) {
    buySignals += 2;
    reasons.push(`RSI過売り状態（${indicators.rsi.toFixed(1)}）`);
  } else if (indicators.rsi > 70) {
    sellSignals += 2;
    reasons.push(`RSI過買い状態（${indicators.rsi.toFixed(1)}）`);
    riskFactors += 1;
  } else if (indicators.rsi >= 40 && indicators.rsi <= 60) {
    reasons.push(`RSI中立圏（${indicators.rsi.toFixed(1)}）`);
  }

  // MACD分析
  if (indicators.macd.macd > indicators.macd.signal && indicators.macd.histogram > 0) {
    buySignals += 1;
    reasons.push("MACD買いシグナル");
  } else if (indicators.macd.macd < indicators.macd.signal && indicators.macd.histogram < 0) {
    sellSignals += 1;
    reasons.push("MACD売りシグナル");
  }

  // ボリンジャーバンド分析
  if (currentPrice < indicators.bollinger.lower) {
    buySignals += 1;
    reasons.push("ボリンジャーバンド下限接触（反発期待）");
  } else if (currentPrice > indicators.bollinger.upper) {
    sellSignals += 1;
    reasons.push("ボリンジャーバンド上限接触（過熱警戒）");
    riskFactors += 1;
  }

  // ボラティリティリスク
  const priceChange = Math.abs((currentPrice - previousPrice) / previousPrice);
  if (priceChange > 0.05) { // 5%以上の変動
    riskFactors += 1;
    reasons.push("高ボラティリティ（急激な価格変動）");
  }

  // 推奨決定
  const netSignal = buySignals - sellSignals;
  let recommendation: AnalysisResult["recommendation"];
  let confidence: number;

  if (netSignal >= 3) {
    recommendation = "STRONG_BUY";
    confidence = Math.min(0.9, 0.6 + (netSignal - 3) * 0.1);
  } else if (netSignal >= 1) {
    recommendation = "BUY";
    confidence = 0.6 + (netSignal - 1) * 0.1;
  } else if (netSignal <= -3) {
    recommendation = "STRONG_SELL";
    confidence = Math.min(0.9, 0.6 + Math.abs(netSignal + 3) * 0.1);
  } else if (netSignal <= -1) {
    recommendation = "SELL";
    confidence = 0.6 + Math.abs(netSignal + 1) * 0.1;
  } else {
    recommendation = "HOLD";
    confidence = 0.5;
  }

  // リスク調整
  confidence = Math.max(0.3, confidence - (riskFactors * 0.1));

  // リスクレベル決定
  let riskLevel: AnalysisResult["riskLevel"];
  if (riskFactors >= 2) {
    riskLevel = "HIGH";
  } else if (riskFactors >= 1) {
    riskLevel = "MEDIUM";
  } else {
    riskLevel = "LOW";
  }

  // 目標価格（簡易計算）
  let targetPrice: number | undefined;
  if (recommendation === "STRONG_BUY" || recommendation === "BUY") {
    // 上昇トレンドの場合、SMA50からの乖離を考慮
    const uptrend = indicators.sma5 > indicators.sma50;
    targetPrice = uptrend ? currentPrice * 1.05 : indicators.sma25;
  } else if (recommendation === "STRONG_SELL" || recommendation === "SELL") {
    // 下降トレンドの場合
    targetPrice = currentPrice * 0.95;
  }

  return {
    recommendation,
    confidence,
    reasons,
    riskLevel,
    targetPrice,
  };
}

/**
 * 単一銘柄を分析
 */
export async function analyzeStock(symbol: string, symbolName?: string): Promise<AnalysisResult | null> {
  try {
    // サブスクリプション期間内の日付を使用（2023-07-10 ~ 2025-07-10）
    const subscriptionEnd = new Date("2025-07-10");
    const today = new Date();
    const actualEndDate = today > subscriptionEnd ? subscriptionEnd : today;
    const endDate = actualEndDate.toISOString().split("T")[0];
    const startDate = new Date(actualEndDate.getTime() - 60 * 24 * 60 * 60 * 1000).toISOString().split("T")[0];
    
    // const stockData = await getStockData(symbol, startDate, endDate);
    const stockData = generateMockStockData(symbol, startDate, endDate);
    
    if (stockData.length === 0) {
      console.warn(`株価データが取得できませんでした: ${symbol}`);
      return null;
    }

    // 銘柄名を取得（提供されていない場合）
    let name = symbolName;
    if (!name) {
      // const symbols = await getAllSymbols();
      const symbols = ["7203", "6758", "9984", "6861", "4063"];
      const symbolInfo = symbols.find(s => s.code === symbol);
      name = symbolInfo?.name || symbol;
    }

    const indicators = calculateTechnicalIndicators(stockData);
    const recommendation = generateRecommendation(stockData, indicators);
    
    const currentPrice = stockData[stockData.length - 1].close;
    const previousPrice = stockData[stockData.length - 2]?.close || currentPrice;
    const priceChange = currentPrice - previousPrice;
    const priceChangePercent = (priceChange / previousPrice) * 100;

    return {
      symbol,
      name,
      currentPrice,
      priceChange,
      priceChangePercent,
      indicators,
      ...recommendation,
    };
  } catch (error) {
    console.error(`株価分析エラー (${symbol}):`, error);
    return null;
  }
}

/**
 * 複数銘柄を分析
 */
export async function analyzeMultipleStocks(symbols: string[]): Promise<AnalysisResult[]> {
  const results: AnalysisResult[] = [];
  
  // 銘柄情報を事前取得
  // const symbolsInfo = await getAllSymbols();
  const symbolsInfo = [
    { code: "7203", name: "トヨタ自動車", sector: "自動車" },
    { code: "6758", name: "ソニーグループ", sector: "エンターテインメント" },
    { code: "9984", name: "ソフトバンクグループ", sector: "通信" },
    { code: "6861", name: "キーエンス", sector: "電子部品" },
    { code: "4063", name: "信越化学工業", sector: "化学" },
  ];
  
  // 並列処理（最大5銘柄同時）
  const batches = [];
  for (let i = 0; i < symbols.length; i += 5) {
    batches.push(symbols.slice(i, i + 5));
  }
  
  for (const batch of batches) {
    const batchPromises = batch.map(async symbol => {
      const symbolInfo = symbolsInfo.find(s => s.code === symbol);
      return analyzeStock(symbol, symbolInfo?.name);
    });
    
    const batchResults = await Promise.all(batchPromises);
    results.push(...batchResults.filter((result): result is AnalysisResult => result !== null));
  }
  
  return results;
}

/**
 * 人気銘柄リストを取得
 */
export function getPopularSymbols(): string[] {
  return [
    "7203", // トヨタ
    "6758", // ソニー
    "9984", // ソフトバンクグループ
    "6861", // キーエンス
    "8035", // 東京エレクトロン
    "4063", // 信越化学
    "6981", // 村田製作所
    "7974", // 任天堂
    "4519", // 中外製薬
    "8031", // 三井物産
    "9432", // 日本電信電話
    "2914", // 日本たばこ産業
    "4568", // 第一三共
    "6954", // ファナック
    "6367", // ダイキン工業
  ];
}

/**
 * 市場サマリーを生成
 */
export async function generateMarketSummary(symbolsToAnalyze?: string[]): Promise<MarketSummary> {
  const symbols = symbolsToAnalyze || getPopularSymbols();
  const analysisResults = await analyzeMultipleStocks(symbols);
  
  // 推奨分布を計算
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
  
  // 上昇・下落ランキング
  const topGainers = analysisResults
    .filter(r => r.priceChangePercent > 0)
    .sort((a, b) => b.priceChangePercent - a.priceChangePercent)
    .slice(0, 5);
    
  const topLosers = analysisResults
    .filter(r => r.priceChangePercent < 0)
    .sort((a, b) => a.priceChangePercent - b.priceChangePercent)
    .slice(0, 5);
  
  return {
    totalSymbols: symbols.length,
    analyzedSymbols: analysisResults.length,
    recommendations,
    topGainers,
    topLosers,
    lastUpdated: new Date().toISOString(),
  };
}