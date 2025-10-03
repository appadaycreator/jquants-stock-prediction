"use client";

import { useState } from "react";
import { TrendingUp, TrendingDown, Minus, AlertTriangle, CheckCircle, Clock, Target, Shield, BarChart3, ExternalLink } from "lucide-react";
import { SignalCategoryTooltip, ConfidenceTooltip } from "./SignalTooltip";
import { formatStockCode } from "@/lib/stock-code-utils";

interface InstructionCardProps {
  symbol: string;
  name?: string;
  recommendation: "BUY" | "SELL" | "HOLD" | "STRONG_BUY" | "STRONG_SELL";
  confidence: number;
  price: number;
  reason: string;
  expectedHoldingPeriod?: number;
  riskLevel: "LOW" | "MEDIUM" | "HIGH";
  category?: string;
  historicalAccuracy?: number;
  evidence?: {
    technical: { name: string; value: number; signal: string }[];
    fundamental: { name: string; value: number; signal: string }[];
    sentiment: { name: string; value: number; signal: string }[];
  };
  onActionClick?: (symbol: string, action: string, quantity: number) => void;
}

export default function InstructionCard({
  symbol,
  name,
  recommendation,
  confidence,
  price,
  reason,
  expectedHoldingPeriod = 30,
  riskLevel,
  category,
  historicalAccuracy = 0.0,
  evidence,
  onActionClick,
}: InstructionCardProps) {
  const [expanded, setExpanded] = useState(false);
  const [selectedQuantity, setSelectedQuantity] = useState(0.25);

  // チャート表示ハンドラー
  const handleChartDisplay = (symbol: string) => {
    try {
      // チャートページへの遷移
      const chartUrl = `/charts/${symbol}`;
      window.open(chartUrl, '_blank', 'width=1200,height=800,scrollbars=yes,resizable=yes');
    } catch (error) {
      console.error('チャート表示エラー:', error);
      // フォールバック: 新しいタブでチャートを開く
      const fallbackUrl = `https://finance.yahoo.com/quote/${symbol}`;
      window.open(fallbackUrl, '_blank');
    }
  };

  const getRecommendationIcon = () => {
    switch (recommendation) {
      case "STRONG_BUY":
      case "BUY":
        return <TrendingUp className="h-5 w-5 text-green-600" />;
      case "STRONG_SELL":
      case "SELL":
        return <TrendingDown className="h-5 w-5 text-red-600" />;
      default:
        return <Minus className="h-5 w-5 text-gray-500" />;
    }
  };

  const getRecommendationColor = () => {
    switch (recommendation) {
      case "STRONG_BUY":
        return "bg-green-100 text-green-800 border-green-200";
      case "BUY":
        return "bg-green-50 text-green-700 border-green-100";
      case "STRONG_SELL":
        return "bg-red-100 text-red-800 border-red-200";
      case "SELL":
        return "bg-red-50 text-red-700 border-red-100";
      default:
        return "bg-gray-50 text-gray-700 border-gray-100";
    }
  };

  const getRiskColor = () => {
    switch (riskLevel) {
      case "LOW":
        return "text-green-600 bg-green-50";
      case "MEDIUM":
        return "text-yellow-600 bg-yellow-50";
      case "HIGH":
        return "text-red-600 bg-red-50";
      default:
        return "text-gray-600 bg-gray-50";
    }
  };

  const getConfidenceColor = () => {
    if (confidence >= 0.8) return "text-green-600";
    if (confidence >= 0.6) return "text-yellow-600";
    return "text-red-600";
  };

  const getActionButtons = () => {
    if (recommendation === "HOLD") {
      return (
        <div className="flex space-x-2">
          <button
            onClick={() => onActionClick?.(symbol, "HOLD", 0)}
            className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
          >
            継続
          </button>
        </div>
      );
    }

    const isBuy = recommendation === "BUY" || recommendation === "STRONG_BUY";
    const actionText = isBuy ? "買い" : "売り";
    const actionColor = isBuy ? "bg-green-600 hover:bg-green-700" : "bg-red-600 hover:bg-red-700";

    return (
      <div className="flex space-x-2">
        <button
          onClick={() => onActionClick?.(symbol, actionText, selectedQuantity)}
          className={`px-3 py-1 text-sm text-white rounded-md ${actionColor}`}
        >
          {actionText}
        </button>
        <select
          value={selectedQuantity}
          onChange={(e) => setSelectedQuantity(parseFloat(e.target.value))}
          className="px-2 py-1 text-sm border border-gray-300 rounded-md"
        >
          <option value={0.25}>25%</option>
          <option value={0.5}>50%</option>
          <option value={0.75}>75%</option>
          <option value={1.0}>100%</option>
        </select>
      </div>
    );
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
      <div className="p-4">
        {/* ヘッダー */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-3">
            {getRecommendationIcon()}
            <div>
              <h3 className="text-lg font-semibold text-gray-900">{formatStockCode(symbol)}</h3>
              {name && <p className="text-sm text-gray-600">{name}</p>}
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <span className={`px-3 py-1 rounded-full text-sm font-medium border ${getRecommendationColor()}`}>
              {recommendation}
            </span>
            <button
              onClick={() => setExpanded(!expanded)}
              className="text-blue-600 hover:text-blue-800 text-sm"
            >
              {expanded ? "詳細を閉じる" : "詳細を表示"}
            </button>
          </div>
        </div>

        {/* 基本情報 */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <div>
            <p className="text-xs text-gray-500 mb-1">現在価格</p>
            <p className="text-lg font-semibold text-gray-900">¥{price.toLocaleString()}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 mb-1">信頼度</p>
            <ConfidenceTooltip confidence={confidence}>
              <p className={`text-lg font-semibold ${getConfidenceColor()} cursor-help`}>
                {(confidence * 100).toFixed(0)}%
              </p>
            </ConfidenceTooltip>
          </div>
          <div>
            <p className="text-xs text-gray-500 mb-1">想定保有期間</p>
            <p className="text-lg font-semibold text-gray-900 flex items-center">
              <Clock className="h-4 w-4 mr-1" />
              {expectedHoldingPeriod}日
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500 mb-1">リスクレベル</p>
            <span className={`inline-flex items-center px-2 py-1 rounded text-xs ${getRiskColor()}`}>
              <Shield className="h-3 w-3 mr-1" />
              {riskLevel}
            </span>
          </div>
        </div>

        {/* 推奨理由 */}
        <div className="mb-4">
          <p className="text-sm text-gray-600">
            <Target className="h-4 w-4 inline mr-1" />
            {reason}
          </p>
          {category && (
            <SignalCategoryTooltip category={category}>
              <p className="text-xs text-blue-600 mt-1 cursor-help">
                カテゴリ: {category}
              </p>
            </SignalCategoryTooltip>
          )}
        </div>

        {/* アクションボタン */}
        <div className="flex items-center justify-between">
          {getActionButtons()}
          <button 
            className="text-blue-600 hover:text-blue-800 text-sm flex items-center transition-colors duration-200"
            onClick={() => handleChartDisplay(symbol)}
          >
            <ExternalLink className="h-4 w-4 mr-1" />
            チャート表示
          </button>
        </div>

        {/* 詳細情報（展開時） */}
        {expanded && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* テクニカル分析 */}
              {evidence?.technical && (
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-2">テクニカル指標</h4>
                  <div className="space-y-1">
                    {evidence.technical.map((item, index) => (
                      <div key={index} className="flex justify-between text-xs">
                        <span className="text-gray-600">{item.name}</span>
                        <span className={item.signal === "買い" ? "text-green-600" : item.signal === "売り" ? "text-red-600" : "text-gray-600"}>
                          {item.signal}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* ファンダメンタル分析 */}
              {evidence?.fundamental && (
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-2">ファンダメンタル</h4>
                  <div className="space-y-1">
                    {evidence.fundamental.map((item, index) => (
                      <div key={index} className="flex justify-between text-xs">
                        <span className="text-gray-600">{item.name}</span>
                        <span className={item.signal === "買い" ? "text-green-600" : item.signal === "売り" ? "text-red-600" : "text-gray-600"}>
                          {item.signal}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* センチメント分析 */}
              {evidence?.sentiment && (
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-2">センチメント</h4>
                  <div className="space-y-1">
                    {evidence.sentiment.map((item, index) => (
                      <div key={index} className="flex justify-between text-xs">
                        <span className="text-gray-600">{item.name}</span>
                        <span className={item.signal === "買い" ? "text-green-600" : item.signal === "売り" ? "text-red-600" : "text-gray-600"}>
                          {item.signal}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* 過去の的中率 */}
            {historicalAccuracy > 0 && (
              <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">過去の的中率</span>
                  <span className="text-lg font-semibold text-blue-600">
                    {(historicalAccuracy * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
