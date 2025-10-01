"use client";

import { Warning } from "@/types/today";

interface RiskCardProps {
  warning: Warning;
}

export default function RiskCard({ warning }: RiskCardProps) {
  const getWarningIcon = (type: string) => {
    switch (type) {
      case "drawdown":
        return "📉";
      case "volatility":
        return "⚡";
      case "event":
        return "📅";
      default:
        return "⚠️";
    }
  };

  const getWarningColor = (type: string) => {
    switch (type) {
      case "drawdown":
        return "bg-red-50 border-red-200 text-red-800";
      case "volatility":
        return "bg-yellow-50 border-yellow-200 text-yellow-800";
      case "event":
        return "bg-orange-50 border-orange-200 text-orange-800";
      default:
        return "bg-gray-50 border-gray-200 text-gray-800";
    }
  };

  const getWarningTitle = (type: string) => {
    switch (type) {
      case "drawdown":
        return "損切り到達間近";
      case "volatility":
        return "ボラ急上昇";
      case "event":
        return "決算・イベント接近";
      default:
        return "リスク警告";
    }
  };

  return (
    <div className={`rounded-2xl border p-4 shadow-md ${getWarningColor(warning.type)}`}>
      <div className="flex items-start gap-3">
        <div className="text-2xl flex-shrink-0">
          {getWarningIcon(warning.type)}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2">
            <h4 className="font-semibold text-sm">
              {getWarningTitle(warning.type)}
            </h4>
            <span className="text-xs font-medium bg-white/50 px-2 py-1 rounded-full">
              {warning.symbol}
            </span>
          </div>
          <p className="text-sm mb-3 leading-relaxed">
            {warning.message}
          </p>
          <div className="bg-white/30 rounded-lg p-2">
            <p className="text-xs font-medium">
              推奨アクション: {warning.action}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
