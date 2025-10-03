"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { ArrowLeft, TrendingUp, TrendingDown, BarChart3, Calendar, DollarSign } from "lucide-react";
import Link from "next/link";

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

export default function StockDetailPage() {
  const params = useParams();
  const symbol = params.symbol as string;
  
  const [stockData, setStockData] = useState<StockData | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStockData = async () => {
      try {
        setLoading(true);
        
        // 全銘柄データから該当銘柄を検索
        const response = await fetch('/data/listed_index.json');
        if (!response.ok) {
          throw new Error('銘柄データの取得に失敗しました');
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
            "ボリンジャーバンド内での価格推移"
          ],
          riskLevel: Math.random() > 0.5 ? "MEDIUM" : Math.random() > 0.3 ? "LOW" : "HIGH",
          targetPrice: Math.floor(Math.random() * 1000) + stock.currentPrice || 2000,
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
        console.error('銘柄データの取得エラー:', err);
        setError(err instanceof Error ? err.message : '不明なエラーが発生しました');
      } finally {
        setLoading(false);
      }
    };

    if (symbol) {
      fetchStockData();
    }
  }, [symbol]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">銘柄データを読み込み中...</p>
        </div>
      </div>
    );
  }

  if (error || !stockData || !analysisResult) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">エラーが発生しました</h2>
          <p className="text-gray-600 mb-4">{error || '銘柄データが見つかりません'}</p>
          <Link
            href="/listed-data"
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 inline-flex items-center"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            銘柄一覧に戻る
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* ヘッダー */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link
                href="/listed-data"
                className="text-gray-600 hover:text-gray-900 flex items-center"
              >
                <ArrowLeft className="w-5 h-5 mr-2" />
                銘柄一覧に戻る
              </Link>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">{stockData.name}</h1>
                <p className="text-gray-600">銘柄コード: {stockData.code}</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                stockData.market === "プライム" ? "bg-green-100 text-green-800" :
                stockData.market === "スタンダード" ? "bg-blue-100 text-blue-800" :
                stockData.market === "グロース" ? "bg-purple-100 text-purple-800" :
                "bg-gray-100 text-gray-800"
              }`}>
                {stockData.market}
              </span>
              <span className="px-3 py-1 bg-gray-100 text-gray-800 rounded-full text-sm">
                {stockData.sector}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* メインコンテンツ */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* 価格情報 */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <DollarSign className="w-5 h-5 mr-2" />
                価格情報
              </h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-sm text-gray-600">現在価格</p>
                  <p className="text-2xl font-bold text-gray-900">
                    ¥{analysisResult.currentPrice.toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">前日比</p>
                  <div className={`flex items-center ${analysisResult.priceChange >= 0 ? 'text-red-600' : 'text-green-600'}`}>
                    {analysisResult.priceChange >= 0 ? (
                      <TrendingUp className="w-4 h-4 mr-1" />
                    ) : (
                      <TrendingDown className="w-4 h-4 mr-1" />
                    )}
                    <span className="text-lg font-semibold">
                      {analysisResult.priceChange >= 0 ? '+' : ''}{analysisResult.priceChange.toLocaleString()}
                    </span>
                  </div>
                </div>
                <div>
                  <p className="text-sm text-gray-600">前日比率</p>
                  <p className={`text-lg font-semibold ${analysisResult.priceChangePercent >= 0 ? 'text-red-600' : 'text-green-600'}`}>
                    {analysisResult.priceChangePercent >= 0 ? '+' : ''}{analysisResult.priceChangePercent.toFixed(2)}%
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">出来高</p>
                  <p className="text-lg font-semibold text-gray-900">
                    {stockData.volume ? stockData.volume.toLocaleString() : 'N/A'}
                  </p>
                </div>
              </div>
            </div>

            {/* 投資推奨 */}
            <div className="bg-white rounded-lg shadow p-6 mt-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <BarChart3 className="w-5 h-5 mr-2" />
                投資推奨
              </h2>
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
              <div className="bg-white rounded-lg shadow p-6 mt-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">テクニカル指標</h2>
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
            <div className="bg-white rounded-lg shadow p-6">
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
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">クイックアクション</h3>
              <div className="space-y-2">
                <button className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                  ポートフォリオに追加
                </button>
                <button className="w-full bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors">
                  ウォッチリストに追加
                </button>
                <button className="w-full bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors">
                  詳細分析を実行
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
