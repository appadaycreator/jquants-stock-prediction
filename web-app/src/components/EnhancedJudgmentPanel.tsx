"use client";

import { useState, useEffect } from "react";
import { 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  CheckCircle, 
  X, 
  Info, 
  Target, 
  Shield,
  BarChart3,
  Clock,
  DollarSign,
  Activity,
} from "lucide-react";

interface PredictionData {
  symbol: string;
  name: string;
  currentPrice: number;
  predictedPrice: number;
  confidence: number;
  recommendation: "STRONG_BUY" | "BUY" | "HOLD" | "SELL" | "STRONG_SELL";
  reasons: string[];
  riskLevel: "LOW" | "MEDIUM" | "HIGH";
  timeframe: string;
  technicalSignals: {
    trend: "bullish" | "bearish" | "neutral";
    momentum: "strong" | "weak" | "neutral";
    volatility: "low" | "medium" | "high";
  };
  fundamentalFactors: {
    earnings: "positive" | "negative" | "neutral";
    growth: "high" | "medium" | "low";
    valuation: "undervalued" | "fair" | "overvalued";
  };
}

interface EnhancedJudgmentPanelProps {
  predictions: PredictionData[];
  onActionClick: (symbol: string, action: string) => void;
  onDetailClick: (symbol: string) => void;
}

export default function EnhancedJudgmentPanel({
  predictions,
  onActionClick,
  onDetailClick,
}: EnhancedJudgmentPanelProps) {
  const [selectedPrediction, setSelectedPrediction] = useState<PredictionData | null>(null);
  const [filterBy, setFilterBy] = useState<"all" | "buy" | "sell" | "hold">("all");

  const getRecommendationColor = (recommendation: string) => {
    switch (recommendation) {
      case "STRONG_BUY":
        return "bg-green-100 text-green-800 border-green-300";
      case "BUY":
        return "bg-blue-100 text-blue-800 border-blue-300";
      case "HOLD":
        return "bg-gray-100 text-gray-800 border-gray-300";
      case "SELL":
        return "bg-yellow-100 text-yellow-800 border-yellow-300";
      case "STRONG_SELL":
        return "bg-red-100 text-red-800 border-red-300";
      default:
        return "bg-gray-100 text-gray-800 border-gray-300";
    }
  };

  const getRecommendationIcon = (recommendation: string) => {
    switch (recommendation) {
      case "STRONG_BUY":
      case "BUY":
        return <TrendingUp className="h-4 w-4" />;
      case "SELL":
      case "STRONG_SELL":
        return <TrendingDown className="h-4 w-4" />;
      default:
        return <Activity className="h-4 w-4" />;
    }
  };

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case "LOW":
        return "text-green-600";
      case "MEDIUM":
        return "text-yellow-600";
      case "HIGH":
        return "text-red-600";
      default:
        return "text-gray-600";
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 80) return "text-green-600";
    if (confidence >= 60) return "text-yellow-600";
    return "text-red-600";
  };

  const getConfidenceLabel = (confidence: number) => {
    if (confidence >= 80) return "高信頼度";
    if (confidence >= 60) return "中信頼度";
    return "低信頼度";
  };

  const filteredPredictions = predictions.filter(prediction => {
    if (filterBy === "all") return true;
    if (filterBy === "buy") return prediction.recommendation === "BUY" || prediction.recommendation === "STRONG_BUY";
    if (filterBy === "sell") return prediction.recommendation === "SELL" || prediction.recommendation === "STRONG_SELL";
    if (filterBy === "hold") return prediction.recommendation === "HOLD";
    return true;
  });

  return (
    <div className="bg-white rounded-lg shadow-lg border p-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-gray-900">投資判断パネル</h2>
          <p className="text-sm text-gray-600">AI予測に基づく投資判断とアクション提案</p>
        </div>
        <div className="flex items-center space-x-2">
          <select
            value={filterBy}
            onChange={(e) => setFilterBy(e.target.value as any)}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="all">すべて</option>
            <option value="buy">買い推奨</option>
            <option value="sell">売り推奨</option>
            <option value="hold">ホールド</option>
          </select>
        </div>
      </div>

      {/* 予測一覧 */}
      <div className="space-y-4">
        {filteredPredictions.map((prediction) => (
          <div
            key={prediction.symbol}
            className="border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
            onClick={() => setSelectedPrediction(prediction)}
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-3">
                <div>
                  <h3 className="font-semibold text-gray-900">{prediction.symbol}</h3>
                  <p className="text-sm text-gray-600">{prediction.name}</p>
                </div>
                <div className={`flex items-center space-x-1 px-2 py-1 rounded-full border ${getRecommendationColor(prediction.recommendation)}`}>
                  {getRecommendationIcon(prediction.recommendation)}
                  <span className="text-xs font-medium">{prediction.recommendation}</span>
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm text-gray-600">現在価格</div>
                <div className="font-semibold text-gray-900">¥{prediction.currentPrice.toLocaleString()}</div>
              </div>
            </div>

            {/* 予測情報 */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
              <div className="text-center">
                <div className="text-xs text-gray-500 mb-1">予測価格</div>
                <div className="font-semibold text-blue-600">¥{prediction.predictedPrice.toLocaleString()}</div>
              </div>
              <div className="text-center">
                <div className="text-xs text-gray-500 mb-1">信頼度</div>
                <div className={`font-semibold ${getConfidenceColor(prediction.confidence)}`}>
                  {prediction.confidence}%
                </div>
              </div>
              <div className="text-center">
                <div className="text-xs text-gray-500 mb-1">リスク</div>
                <div className={`font-semibold ${getRiskColor(prediction.riskLevel)}`}>
                  {prediction.riskLevel}
                </div>
              </div>
              <div className="text-center">
                <div className="text-xs text-gray-500 mb-1">期間</div>
                <div className="font-semibold text-gray-900">{prediction.timeframe}</div>
              </div>
            </div>

            {/* 主要な根拠 */}
            <div className="mb-3">
              <div className="text-xs text-gray-500 mb-1">主要根拠</div>
              <div className="flex flex-wrap gap-1">
                {prediction.reasons.slice(0, 3).map((reason, index) => (
                  <span
                    key={index}
                    className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded"
                  >
                    {reason}
                  </span>
                ))}
                {prediction.reasons.length > 3 && (
                  <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                    +{prediction.reasons.length - 3}件
                  </span>
                )}
              </div>
            </div>

            {/* アクションボタン */}
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDetailClick(prediction.symbol);
                  }}
                  className="flex items-center px-3 py-1 text-blue-600 hover:bg-blue-50 rounded text-sm"
                >
                  <BarChart3 className="h-4 w-4 mr-1" />
                  詳細分析
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onActionClick(prediction.symbol, prediction.recommendation);
                  }}
                  className={`flex items-center px-3 py-1 rounded text-sm ${
                    prediction.recommendation.includes("BUY") 
                      ? "bg-green-100 text-green-700 hover:bg-green-200"
                      : prediction.recommendation.includes("SELL")
                      ? "bg-red-100 text-red-700 hover:bg-red-200"
                      : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                  }`}
                >
                  <Target className="h-4 w-4 mr-1" />
                  アクション実行
                </button>
              </div>
              <div className="text-xs text-gray-500">
                {getConfidenceLabel(prediction.confidence)}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* 詳細モーダル */}
      {selectedPrediction && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold text-gray-900">
                  {selectedPrediction.symbol} - 詳細分析
                </h3>
                <button
                  onClick={() => setSelectedPrediction(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>

              {/* 基本情報 */}
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-sm text-gray-600 mb-1">現在価格</div>
                  <div className="text-xl font-bold text-gray-900">
                    ¥{selectedPrediction.currentPrice.toLocaleString()}
                  </div>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-sm text-gray-600 mb-1">予測価格</div>
                  <div className="text-xl font-bold text-blue-600">
                    ¥{selectedPrediction.predictedPrice.toLocaleString()}
                  </div>
                </div>
              </div>

              {/* 技術分析 */}
              <div className="mb-6">
                <h4 className="font-semibold text-gray-900 mb-3">技術分析</h4>
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center">
                    <div className="text-sm text-gray-600 mb-1">トレンド</div>
                    <div className={`font-semibold ${
                      selectedPrediction.technicalSignals.trend === "bullish" ? "text-green-600" :
                      selectedPrediction.technicalSignals.trend === "bearish" ? "text-red-600" :
                      "text-gray-600"
                    }`}>
                      {selectedPrediction.technicalSignals.trend === "bullish" ? "上昇" :
                       selectedPrediction.technicalSignals.trend === "bearish" ? "下降" : "横ばい"}
                    </div>
                  </div>
                  <div className="text-center">
                    <div className="text-sm text-gray-600 mb-1">モメンタム</div>
                    <div className={`font-semibold ${
                      selectedPrediction.technicalSignals.momentum === "strong" ? "text-green-600" :
                      selectedPrediction.technicalSignals.momentum === "weak" ? "text-red-600" :
                      "text-gray-600"
                    }`}>
                      {selectedPrediction.technicalSignals.momentum === "strong" ? "強い" :
                       selectedPrediction.technicalSignals.momentum === "weak" ? "弱い" : "普通"}
                    </div>
                  </div>
                  <div className="text-center">
                    <div className="text-sm text-gray-600 mb-1">ボラティリティ</div>
                    <div className={`font-semibold ${
                      selectedPrediction.technicalSignals.volatility === "low" ? "text-green-600" :
                      selectedPrediction.technicalSignals.volatility === "high" ? "text-red-600" :
                      "text-yellow-600"
                    }`}>
                      {selectedPrediction.technicalSignals.volatility === "low" ? "低" :
                       selectedPrediction.technicalSignals.volatility === "high" ? "高" : "中"}
                    </div>
                  </div>
                </div>
              </div>

              {/* ファンダメンタル分析 */}
              <div className="mb-6">
                <h4 className="font-semibold text-gray-900 mb-3">ファンダメンタル分析</h4>
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center">
                    <div className="text-sm text-gray-600 mb-1">業績</div>
                    <div className={`font-semibold ${
                      selectedPrediction.fundamentalFactors.earnings === "positive" ? "text-green-600" :
                      selectedPrediction.fundamentalFactors.earnings === "negative" ? "text-red-600" :
                      "text-gray-600"
                    }`}>
                      {selectedPrediction.fundamentalFactors.earnings === "positive" ? "良好" :
                       selectedPrediction.fundamentalFactors.earnings === "negative" ? "悪化" : "普通"}
                    </div>
                  </div>
                  <div className="text-center">
                    <div className="text-sm text-gray-600 mb-1">成長性</div>
                    <div className={`font-semibold ${
                      selectedPrediction.fundamentalFactors.growth === "high" ? "text-green-600" :
                      selectedPrediction.fundamentalFactors.growth === "low" ? "text-red-600" :
                      "text-yellow-600"
                    }`}>
                      {selectedPrediction.fundamentalFactors.growth === "high" ? "高" :
                       selectedPrediction.fundamentalFactors.growth === "low" ? "低" : "中"}
                    </div>
                  </div>
                  <div className="text-center">
                    <div className="text-sm text-gray-600 mb-1">バリュエーション</div>
                    <div className={`font-semibold ${
                      selectedPrediction.fundamentalFactors.valuation === "undervalued" ? "text-green-600" :
                      selectedPrediction.fundamentalFactors.valuation === "overvalued" ? "text-red-600" :
                      "text-yellow-600"
                    }`}>
                      {selectedPrediction.fundamentalFactors.valuation === "undervalued" ? "割安" :
                       selectedPrediction.fundamentalFactors.valuation === "overvalued" ? "割高" : "適正"}
                    </div>
                  </div>
                </div>
              </div>

              {/* 推奨理由 */}
              <div className="mb-6">
                <h4 className="font-semibold text-gray-900 mb-3">推奨理由</h4>
                <ul className="space-y-2">
                  {selectedPrediction.reasons.map((reason, index) => (
                    <li key={index} className="flex items-start space-x-2">
                      <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                      <span className="text-sm text-gray-700">{reason}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* アクションボタン */}
              <div className="flex items-center justify-end space-x-3">
                <button
                  onClick={() => setSelectedPrediction(null)}
                  className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  閉じる
                </button>
                <button
                  onClick={() => {
                    onActionClick(selectedPrediction.symbol, selectedPrediction.recommendation);
                    setSelectedPrediction(null);
                  }}
                  className={`px-4 py-2 text-white rounded-lg ${
                    selectedPrediction.recommendation.includes("BUY") 
                      ? "bg-green-600 hover:bg-green-700"
                      : selectedPrediction.recommendation.includes("SELL")
                      ? "bg-red-600 hover:bg-red-700"
                      : "bg-gray-600 hover:bg-gray-700"
                  }`}
                >
                  アクション実行
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
