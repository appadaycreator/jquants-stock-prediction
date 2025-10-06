"use client";

import { useEffect, useState } from "react";
import { X, TrendingUp, TrendingDown, BarChart3, DollarSign, Calendar } from "lucide-react";
import { formatStockCode } from "@/lib/stock-code-utils";

interface StockData {
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

interface AnalysisResult {
  symbol: string;
  name: string;
  currentPrice: number;
  priceChange: number;
  priceChangePercent: number;
  recommendation: "BUY" | "SELL" | "HOLD";
  confidence: number;
  reasons: string[];
  riskLevel: "LOW" | "MEDIUM" | "HIGH";
  targetPrice?: number;
  technicalIndicators?: {
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

interface StockDetailModalProps {
  symbol: string;
  isOpen: boolean;
  onClose: () => void;
}

export default function StockDetailModal({ symbol, isOpen, onClose }: StockDetailModalProps) {
  const [stockData, setStockData] = useState<StockData | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // クイックアクション用の状態
  const [isAddingToPortfolio, setIsAddingToPortfolio] = useState(false);
  const [isAddingToWatchlist, setIsAddingToWatchlist] = useState(false);
  const [isRunningAnalysis, setIsRunningAnalysis] = useState(false);
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen || !symbol) return;

    const fetchStockData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // 全銘柄データから該当銘柄を検索
        const { resolveStaticPath } = await import("@/lib/path");
        const response = await fetch(resolveStaticPath("/data/listed_index.json"));
        if (!response.ok) {
          throw new Error("銘柄データの取得に失敗しました");
        }
        
        const data = await response.json();
        const stock = data.stocks?.find((s: any) => s.code === symbol);
        
        if (!stock) {
          throw new Error(`銘柄コード ${symbol} が見つかりません`);
        }
        
        setStockData(stock);
        
        // 分析結果を生成（実際の運用では分析APIを呼び出し）
        const mockAnalysis: AnalysisResult = {
          symbol: stock.code,
          name: stock.name,
          currentPrice: stock.currentPrice || Math.floor(Math.random() * 5000) + 1000,
          priceChange: Math.floor(Math.random() * 200) - 100,
          priceChangePercent: (Math.random() - 0.5) * 10,
          recommendation: Math.random() > 0.5 ? "BUY" : Math.random() > 0.3 ? "HOLD" : "SELL",
          confidence: Math.random() * 0.4 + 0.6,
          reasons: [
            "テクニカル分析で上昇トレンドを確認",
            "RSIが適正範囲内",
            "ボリンジャーバンド内での価格推移",
          ],
          riskLevel: Math.random() > 0.5 ? "MEDIUM" : Math.random() > 0.3 ? "LOW" : "HIGH",
          targetPrice: Math.floor(Math.random() * 1000) + (stock.currentPrice || 2000),
          technicalIndicators: {
            sma5: Math.floor(Math.random() * 1000) + 1000,
            sma10: Math.floor(Math.random() * 1000) + 1000,
            sma25: Math.floor(Math.random() * 1000) + 1000,
            sma50: Math.floor(Math.random() * 1000) + 1000,
            rsi: Math.random() * 100,
            macd: {
              macd: Math.random() * 100 - 50,
              signal: Math.random() * 100 - 50,
              histogram: Math.random() * 100 - 50,
            },
            bollingerBands: {
              upper: Math.floor(Math.random() * 1000) + 2000,
              middle: Math.floor(Math.random() * 1000) + 1500,
              lower: Math.floor(Math.random() * 1000) + 1000,
            },
          },
        };
        
        setAnalysisResult(mockAnalysis);
        
      } catch (err) {
        console.error("銘柄データの取得エラー:", err);
        setError(err instanceof Error ? err.message : "不明なエラーが発生しました");
      } finally {
        setLoading(false);
      }
    };

    fetchStockData();
  }, [isOpen, symbol]);

  // ポートフォリオに追加
  const handleAddToPortfolio = async () => {
    if (!stockData || !analysisResult) return;
    
    setIsAddingToPortfolio(true);
    setActionMessage(null);
    
    try {
      // ローカルストレージからポートフォリオを取得
      const portfolio = JSON.parse(localStorage.getItem("user_portfolio") || "[]");
      
      // 既に追加されているかチェック
      const existingIndex = portfolio.findIndex((item: any) => item.symbol === symbol);
      
      if (existingIndex >= 0) {
        setActionMessage("この銘柄は既にポートフォリオに追加されています");
        return;
      }
      
      // 新しい銘柄を追加
      const newItem = {
        symbol: symbol,
        name: stockData.name,
        sector: stockData.sector,
        market: stockData.market,
        currentPrice: analysisResult.currentPrice,
        addedAt: new Date().toISOString(),
        targetPrice: analysisResult.targetPrice,
        riskLevel: analysisResult.riskLevel,
        recommendation: analysisResult.recommendation,
        confidence: analysisResult.confidence,
      };
      
      portfolio.push(newItem);
      localStorage.setItem("user_portfolio", JSON.stringify(portfolio));
      
      setActionMessage(`${stockData.name} (${symbol}) をポートフォリオに追加しました`);
      
    } catch (error) {
      console.error("ポートフォリオ追加エラー:", error);
      setActionMessage("ポートフォリオへの追加に失敗しました");
    } finally {
      setIsAddingToPortfolio(false);
    }
  };

  // ウォッチリストに追加
  const handleAddToWatchlist = async () => {
    if (!stockData || !analysisResult) return;
    
    setIsAddingToWatchlist(true);
    setActionMessage(null);
    
    try {
      // ローカルストレージからウォッチリストを取得
      const watchlist = JSON.parse(localStorage.getItem("user_watchlist") || "[]");
      
      // 既に追加されているかチェック
      const existingIndex = watchlist.findIndex((item: any) => item.symbol === symbol);
      
      if (existingIndex >= 0) {
        setActionMessage("この銘柄は既にウォッチリストに追加されています");
        return;
      }
      
      // 新しい銘柄を追加
      const newItem = {
        symbol: symbol,
        name: stockData.name,
        sector: stockData.sector,
        market: stockData.market,
        currentPrice: analysisResult.currentPrice,
        addedAt: new Date().toISOString(),
        targetPrice: analysisResult.targetPrice,
        riskLevel: analysisResult.riskLevel,
        recommendation: analysisResult.recommendation,
        confidence: analysisResult.confidence,
      };
      
      watchlist.push(newItem);
      localStorage.setItem("user_watchlist", JSON.stringify(watchlist));
      
      setActionMessage(`${stockData.name} (${symbol}) をウォッチリストに追加しました`);
      
    } catch (error) {
      console.error("ウォッチリスト追加エラー:", error);
      setActionMessage("ウォッチリストへの追加に失敗しました");
    } finally {
      setIsAddingToWatchlist(false);
    }
  };

  // 詳細分析を実行
  const handleRunDetailedAnalysis = async () => {
    if (!stockData || !analysisResult) return;
    
    setIsRunningAnalysis(true);
    setActionMessage(null);
    
    try {
      // 詳細分析のシミュレーション（実際のAPI呼び出しに置き換え可能）
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // 分析結果をローカルストレージに保存
      const analysisHistory = JSON.parse(localStorage.getItem("analysis_history") || "[]");
      
      const analysisRecord = {
        symbol: symbol,
        name: stockData.name,
        analyzedAt: new Date().toISOString(),
        currentPrice: analysisResult.currentPrice,
        recommendation: analysisResult.recommendation,
        confidence: analysisResult.confidence,
        riskLevel: analysisResult.riskLevel,
        targetPrice: analysisResult.targetPrice,
        technicalIndicators: analysisResult.technicalIndicators,
        reasons: analysisResult.reasons,
      };
      
      analysisHistory.unshift(analysisRecord);
      
      // 最新100件のみ保持
      if (analysisHistory.length > 100) {
        analysisHistory.splice(100);
      }
      
      localStorage.setItem("analysis_history", JSON.stringify(analysisHistory));
      
      setActionMessage(`${stockData.name} (${symbol}) の詳細分析が完了しました。` +
        " \u003ca href=\"/analysis-history\" target=\"_blank\" rel=\"noopener noreferrer\" class=\"underline text-blue-700\"\u003e分析履歴を見る\u003c/a\u003e");
      
    } catch (error) {
      console.error("詳細分析エラー:", error);
      setActionMessage("詳細分析の実行に失敗しました");
    } finally {
      setIsRunningAnalysis(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* ヘッダー */}
        <div className="flex items-center justify-between p-6 border-b">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              {stockData?.name || "銘柄詳細"}
            </h2>
            <p className="text-gray-600">銘柄コード: {formatStockCode(symbol)}</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* コンテンツ */}
        <div className="overflow-y-auto max-h-[calc(90vh-80px)]">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-gray-600">銘柄データを読み込み中...</p>
              </div>
            </div>
          ) : error || !stockData || !analysisResult ? (
            <div className="flex items-center justify-center py-12">
              <div className="text-center">
                <div className="text-red-500 text-6xl mb-4">⚠️</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">エラーが発生しました</h3>
                <p className="text-gray-600 mb-4">{error || "銘柄データが見つかりません"}</p>
                <button
                  onClick={onClose}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                >
                  閉じる
                </button>
              </div>
            </div>
          ) : (
            <div className="p-6">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* 価格情報 */}
                <div className="lg:col-span-2">
                  <div className="bg-gray-50 rounded-lg p-6 mb-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                      <DollarSign className="w-5 h-5 mr-2" />
                      価格情報
                    </h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div>
                        <p className="text-sm text-gray-600">現在価格</p>
                        <p className="text-2xl font-bold text-gray-900">
                          ¥{analysisResult.currentPrice.toLocaleString()}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">前日比</p>
                        <div className={`flex items-center ${analysisResult.priceChange >= 0 ? "text-red-600" : "text-green-600"}`}>
                          {analysisResult.priceChange >= 0 ? (
                            <TrendingUp className="w-4 h-4 mr-1" />
                          ) : (
                            <TrendingDown className="w-4 h-4 mr-1" />
                          )}
                          <span className="text-lg font-semibold">
                            {analysisResult.priceChange >= 0 ? "+" : ""}{analysisResult.priceChange.toLocaleString()}
                          </span>
                        </div>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">前日比率</p>
                        <p className={`text-lg font-semibold ${analysisResult.priceChangePercent >= 0 ? "text-red-600" : "text-green-600"}`}>
                          {analysisResult.priceChangePercent >= 0 ? "+" : ""}{analysisResult.priceChangePercent.toFixed(2)}%
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">出来高</p>
                        <p className="text-lg font-semibold text-gray-900">
                          {stockData.volume ? stockData.volume.toLocaleString() : "N/A"}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* 投資推奨 */}
                  <div className="bg-gray-50 rounded-lg p-6 mb-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                      <BarChart3 className="w-5 h-5 mr-2" />
                      投資推奨
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm text-gray-600">推奨アクション</span>
                          <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                            analysisResult.recommendation === "BUY" ? "bg-green-100 text-green-800" :
                            analysisResult.recommendation === "SELL" ? "bg-red-100 text-red-800" :
                            "bg-yellow-100 text-yellow-800"
                          }`}>
                            {analysisResult.recommendation === "BUY" ? "買い" :
                             analysisResult.recommendation === "SELL" ? "売り" : "ホールド"}
                          </span>
                        </div>
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm text-gray-600">信頼度</span>
                          <span className="text-sm font-semibold text-gray-900">
                            {(analysisResult.confidence * 100).toFixed(1)}%
                          </span>
                        </div>
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm text-gray-600">リスクレベル</span>
                          <span className={`px-2 py-1 rounded text-xs font-medium ${
                            analysisResult.riskLevel === "LOW" ? "bg-green-100 text-green-800" :
                            analysisResult.riskLevel === "MEDIUM" ? "bg-yellow-100 text-yellow-800" :
                            "bg-red-100 text-red-800"
                          }`}>
                            {analysisResult.riskLevel === "LOW" ? "低" :
                             analysisResult.riskLevel === "MEDIUM" ? "中" : "高"}
                          </span>
                        </div>
                        {analysisResult.targetPrice && (
                          <div className="flex items-center justify-between">
                            <span className="text-sm text-gray-600">目標価格</span>
                            <span className="text-sm font-semibold text-gray-900">
                              ¥{analysisResult.targetPrice.toLocaleString()}
                            </span>
                          </div>
                        )}
                      </div>
                      <div>
                        <p className="text-sm text-gray-600 mb-2">推奨理由</p>
                        <ul className="space-y-1">
                          {analysisResult.reasons.map((reason, index) => (
                            <li key={index} className="text-sm text-gray-700 flex items-start">
                              <span className="w-2 h-2 bg-blue-500 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                              {reason}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>

                  {/* テクニカル指標 */}
                  {analysisResult.technicalIndicators && (
                    <div className="bg-gray-50 rounded-lg p-6">
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">テクニカル指標</h3>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div>
                          <p className="text-sm text-gray-600">SMA5</p>
                          <p className="text-lg font-semibold text-gray-900">
                            ¥{analysisResult.technicalIndicators.sma5.toLocaleString()}
                          </p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">SMA10</p>
                          <p className="text-lg font-semibold text-gray-900">
                            ¥{analysisResult.technicalIndicators.sma10.toLocaleString()}
                          </p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">SMA25</p>
                          <p className="text-lg font-semibold text-gray-900">
                            ¥{analysisResult.technicalIndicators.sma25.toLocaleString()}
                          </p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">RSI</p>
                          <p className="text-lg font-semibold text-gray-900">
                            {analysisResult.technicalIndicators.rsi.toFixed(1)}
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* サイドバー */}
                <div className="space-y-6">
                  {/* 基本情報 */}
                  <div className="bg-gray-50 rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">基本情報</h3>
                    <div className="space-y-3">
                      <div>
                        <p className="text-sm text-gray-600">銘柄コード</p>
                        <p className="text-sm font-semibold text-gray-900">{stockData.code}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">会社名</p>
                        <p className="text-sm font-semibold text-gray-900">{stockData.name}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">セクター</p>
                        <p className="text-sm font-semibold text-gray-900">{stockData.sector}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">市場</p>
                        <p className="text-sm font-semibold text-gray-900">{stockData.market}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">最終更新</p>
                        <p className="text-sm font-semibold text-gray-900">
                          {new Date(stockData.updated_at).toLocaleString("ja-JP")}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* クイックアクション */}
                  <div className="bg-gray-50 rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">クイックアクション</h3>
                    
                    {/* アクションメッセージ */}
                    {actionMessage && (
                      <div className={`mb-4 p-3 rounded-lg text-sm ${
                        actionMessage.includes("失敗") || actionMessage.includes("既に") 
                          ? "bg-yellow-100 text-yellow-800 border border-yellow-200" 
                          : "bg-green-100 text-green-800 border border-green-200"
                      }`}>
                        <span dangerouslySetInnerHTML={{ __html: actionMessage }} />
                      </div>
                    )}
                    
                    <div className="space-y-2">
                      <button 
                        onClick={() => handleAddToPortfolio()}
                        className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        disabled={isAddingToPortfolio}
                      >
                        {isAddingToPortfolio ? "追加中..." : "ポートフォリオに追加"}
                      </button>
                      <button 
                        onClick={() => handleAddToWatchlist()}
                        className="w-full bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        disabled={isAddingToWatchlist}
                      >
                        {isAddingToWatchlist ? "追加中..." : "ウォッチリストに追加"}
                      </button>
                      <button 
                        onClick={() => handleRunDetailedAnalysis()}
                        className="w-full bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        disabled={isRunningAnalysis}
                      >
                        {isRunningAnalysis ? "分析中..." : "詳細分析を実行"}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
