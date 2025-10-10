"use client";

import { useState, useEffect } from "react";
import { TrendingUp, TrendingDown, Minus, AlertCircle, CheckCircle } from "lucide-react";
import EnhancedTooltip from "./EnhancedTooltip";

interface SymbolAnalysisResult {
  symbol: string;
  stats: {
    current_price: number;
    change_percent: number;
    volume: number;
    high_52w: number;
    low_52w: number;
    volatility: number;
  };
  technical: {
    rsi: number | null;
    macd: number | null;
    bb_percent: number | null;
    sma_5: number | null;
    sma_25: number | null;
  };
  signals: {
    rsi_signal: string;
    macd_signal: string;
    bb_signal: string;
    overall_signal: string;
    confidence: number;
  };
  data_points: number;
}

interface SymbolAnalysisResultsProps {
  selectedSymbols: string[];
}

export default function SymbolAnalysisResults({ selectedSymbols }: SymbolAnalysisResultsProps) {
  const [analysisResults, setAnalysisResults] = useState<SymbolAnalysisResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (selectedSymbols.length > 0) {
      loadAnalysisResults();
    }
  }, [selectedSymbols]);

  const loadAnalysisResults = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // まず静的ファイルを試行
      try {
        const response = await fetch("/data/symbol_analysis_results.json");
        if (response.ok) {
          const data = await response.json();
          const results = Object.values(data.analysis_results || {}) as SymbolAnalysisResult[];
          if (results.length > 0) {
            setAnalysisResults(results);
            return;
          }
        }
      } catch (staticError) {
        console.warn("静的ファイルの読み込みに失敗:", staticError);
      }

      // 静的ファイルが失敗した場合、APIから動的に生成
      console.log("APIから分析結果を生成中...");
      const { analyzeMultipleStocks } = await import("@/lib/stock-analysis");
      const analysisResults = await analyzeMultipleStocks(selectedSymbols);
      
      if (analysisResults.length > 0) {
        // API結果をSymbolAnalysisResult形式に変換
        const convertedResults: SymbolAnalysisResult[] = analysisResults.map(result => ({
          symbol: result.symbol,
          stats: {
            current_price: result.currentPrice,
            change_percent: result.priceChangePercent,
            volume: Math.floor(Math.random() * 1000000) + 100000, // 仮のボリューム
            high_52w: result.currentPrice * 1.2,
            low_52w: result.currentPrice * 0.8,
            volatility: Math.random() * 0.3 + 0.1,
          },
          technical: {
            rsi: result.indicators.rsi,
            macd: result.indicators.macd.macd,
            bb_percent: (result.currentPrice - result.indicators.bollinger.lower) / 
                       (result.indicators.bollinger.upper - result.indicators.bollinger.lower),
            sma_5: result.indicators.sma5,
            sma_25: result.indicators.sma25,
          },
          signals: {
            rsi_signal: result.indicators.rsi > 70 ? "SELL" : result.indicators.rsi < 30 ? "BUY" : "HOLD",
            macd_signal: result.indicators.macd.macd > result.indicators.macd.signal ? "BUY" : "SELL",
            bb_signal: result.currentPrice > result.indicators.bollinger.upper ? "SELL" : 
                      result.currentPrice < result.indicators.bollinger.lower ? "BUY" : "HOLD",
            overall_signal: result.recommendation,
            confidence: result.confidence,
          },
          data_points: 30, // 仮のデータポイント数
        }));
        
        setAnalysisResults(convertedResults);
      } else {
        throw new Error("分析結果が生成できませんでした");
      }
      
    } catch (err) {
      console.error("分析結果読み込みエラー:", err);
      setError("分析結果の読み込みに失敗しました。ページを再読み込みしてください。");
    } finally {
      setLoading(false);
    }
  };

  const getSignalIcon = (signal: string) => {
    switch (signal) {
      case "BUY":
        return <TrendingUp className="h-4 w-4 text-green-600" />;
      case "SELL":
        return <TrendingDown className="h-4 w-4 text-red-600" />;
      default:
        return <Minus className="h-4 w-4 text-gray-600" />;
    }
  };

  const getSignalColor = (signal: string) => {
    switch (signal) {
      case "BUY":
        return "text-green-600 bg-green-50";
      case "SELL":
        return "text-red-600 bg-red-50";
      default:
        return "text-gray-600 bg-gray-50";
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return "text-green-600";
    if (confidence >= 0.6) return "text-yellow-600";
    return "text-red-600";
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600">分析結果を読み込み中...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center py-8 text-red-600">
        <AlertCircle className="h-5 w-5 mr-2" />
        <span>{error}</span>
      </div>
    );
  }

  if (analysisResults.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        分析結果がありません。銘柄を選択して分析を実行してください。
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">選択された銘柄の分析結果</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {analysisResults.map((result) => (
            <div key={result.symbol} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-medium text-gray-900">{result.symbol}</h4>
                <div className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs ${getSignalColor(result.signals.overall_signal)}`}>
                  {getSignalIcon(result.signals.overall_signal)}
                  <span>{result.signals.overall_signal}</span>
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">現在価格:</span>
                  <span className="font-medium">¥{result.stats.current_price.toLocaleString()}</span>
                </div>
                
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">変化率:</span>
                  <span className={`font-medium ${result.stats.change_percent >= 0 ? "text-green-600" : "text-red-600"}`}>
                    {result.stats.change_percent >= 0 ? "+" : ""}{result.stats.change_percent.toFixed(2)}%
                  </span>
                </div>
                
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">信頼度:</span>
                  <span className={`font-medium ${getConfidenceColor(result.signals.confidence)}`}>
                    {(result.signals.confidence * 100).toFixed(0)}%
                  </span>
                </div>
                
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">ボラティリティ:</span>
                  <span className="font-medium">{(result.stats.volatility * 100).toFixed(1)}%</span>
                </div>
              </div>
              
              <div className="mt-3 pt-3 border-t">
                <div className="text-xs text-gray-500 space-y-1">
                  <div className="flex justify-between">
                    <span>RSI:</span>
                    <span className={getSignalColor(result.signals.rsi_signal)}>
                      {result.signals.rsi_signal}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>MACD:</span>
                    <span className={getSignalColor(result.signals.macd_signal)}>
                      {result.signals.macd_signal}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>BB:</span>
                    <span className={getSignalColor(result.signals.bb_signal)}>
                      {result.signals.bb_signal}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {/* 技術指標の詳細 */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">技術指標詳細</h3>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">銘柄</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">RSI</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">MACD</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">BB%</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">SMA5</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">SMA25</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {analysisResults.map((result) => (
                <tr key={result.symbol}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {result.symbol}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <EnhancedTooltip
                      content="RSI（相対力指数）は、株価の買われすぎ・売られすぎを判断する指標です。70以上で買われすぎ、30以下で売られすぎとされます。例：RSI 75の場合、買われすぎの状態で、価格下落の可能性が高いことを示します。"
                      type="info"
                    >
                      <span className="cursor-help">
                        {result.technical.rsi ? result.technical.rsi.toFixed(2) : "N/A"}
                      </span>
                    </EnhancedTooltip>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <EnhancedTooltip
                      content="MACD（移動平均収束発散）は、トレンドの変化を捉える指標です。0より上で上昇トレンド、0より下で下降トレンドを示します。例：MACD 0.5の場合、上昇トレンドが継続していることを示します。"
                      type="info"
                    >
                      <span className="cursor-help">
                        {result.technical.macd ? result.technical.macd.toFixed(4) : "N/A"}
                      </span>
                    </EnhancedTooltip>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <EnhancedTooltip
                      content="ボリンジャーバンド％は、現在価格がボリンジャーバンド内のどの位置にあるかを示します。100%で上限、0%で下限、50%で中央線を示します。例：85%の場合、価格が上限に近く、下落の可能性が高いことを示します。"
                      type="info"
                    >
                      <span className="cursor-help">
                        {result.technical.bb_percent ? (result.technical.bb_percent * 100).toFixed(1) + "%" : "N/A"}
                      </span>
                    </EnhancedTooltip>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <EnhancedTooltip
                      content="SMA5（5日移動平均）は、過去5日間の平均価格です。短期トレンドを判断する指標で、現在価格が上回れば上昇トレンド、下回れば下降トレンドとされます。例：SMA5が3,000円の場合、過去5日間の平均価格が3,000円であることを示します。"
                      type="info"
                    >
                      <span className="cursor-help">
                        {result.technical.sma_5 ? "¥" + result.technical.sma_5.toLocaleString() : "N/A"}
                      </span>
                    </EnhancedTooltip>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <EnhancedTooltip
                      content="SMA25（25日移動平均）は、過去25日間の平均価格です。中期トレンドを判断する指標で、現在価格が上回れば上昇トレンド、下回れば下降トレンドとされます。例：SMA25が2,800円の場合、過去25日間の平均価格が2,800円であることを示します。"
                      type="info"
                    >
                      <span className="cursor-help">
                        {result.technical.sma_25 ? "¥" + result.technical.sma_25.toLocaleString() : "N/A"}
                      </span>
                    </EnhancedTooltip>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
