"use client";

import React from "react";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Badge } from "@/components/ui/badge";
import { HelpCircle, TrendingUp, DollarSign, Star, Shield } from "lucide-react";

interface IndicatorTooltipProps {
  indicator: string;
  children: React.ReactNode;
}

const indicatorInfo = {
  "トレンド": {
    icon: TrendingUp,
    title: "トレンド分析",
    description: "株価の上昇トレンドを分析します",
    details: [
      "13週移動平均 > 26週移動平均: 中期的な上昇トレンドを示します",
      "直近20営業日リターン: 短期的な価格上昇を確認します",
      "高いスコアほど上昇トレンドが強いことを示します",
    ],
    tips: [
      "移動平均の交差は重要なシグナルです",
      "リターンは市場全体との比較で判断します",
      "トレンドは継続性が重要です",
    ],
  },
  "バリュー": {
    icon: DollarSign,
    title: "バリュエーション分析",
    description: "株価の割安度を分析します",
    details: [
      "PBR（株価純資産倍率）: 資産価値に対する株価の割安度",
      "PER（株価収益率）: 収益に対する株価の割安度",
      "低い値ほど割安であることを示します",
    ],
    tips: [
      "PBR < 1.0は理論的に割安です",
      "PERは業界平均と比較してください",
      "成長性とバランスを取ることが重要です",
    ],
  },
  "クオリティ": {
    icon: Star,
    title: "クオリティ分析",
    description: "企業の収益性を分析します",
    details: [
      "ROE（自己資本利益率）: 自己資本に対する収益性",
      "高いROEは効率的な経営を示します",
      "持続的な高ROEが理想的です",
    ],
    tips: [
      "ROE > 15%は一般的に良好とされます",
      "業界特性を考慮してください",
      "過去3-5年の平均値を見ることが重要です",
    ],
  },
  "流動性": {
    icon: TrendingUp,
    title: "流動性分析",
    description: "取引の活発さを分析します",
    details: [
      "出来高: 取引の活発さを示します",
      "高い出来高は流動性が良いことを示します",
      "売買が容易で価格発見機能が働きます",
    ],
    tips: [
      "出来高は平均値と比較してください",
      "急激な出来高増加に注意が必要です",
      "安定した出来高が理想的です",
    ],
  },
};

export default function IndicatorTooltip({ indicator, children }: IndicatorTooltipProps) {
  const info = indicatorInfo[indicator as keyof typeof indicatorInfo];
  
  if (!info) {
    return <>{children}</>;
  }

  const Icon = info.icon;

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <div className="inline-flex items-center gap-1 cursor-help">
            {children}
            <HelpCircle className="h-3 w-3 text-gray-400" />
          </div>
        </TooltipTrigger>
        <TooltipContent className="max-w-sm p-4">
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <Icon className="h-4 w-4" />
              <span className="font-semibold">{info.title}</span>
            </div>
            <p className="text-sm text-gray-600">{info.description}</p>
            
            <div>
              <h4 className="text-sm font-medium mb-2">詳細説明</h4>
              <ul className="text-xs space-y-1">
                {info.details.map((detail, index) => (
                  <li key={index} className="flex items-start gap-1">
                    <span className="text-blue-500 mt-1">•</span>
                    <span>{detail}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h4 className="text-sm font-medium mb-2">投資のコツ</h4>
              <ul className="text-xs space-y-1">
                {info.tips.map((tip, index) => (
                  <li key={index} className="flex items-start gap-1">
                    <span className="text-green-500 mt-1">💡</span>
                    <span>{tip}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}

// 個別指標用のツールチップ
export function StockIndicatorTooltip({ 
  name, 
  value, 
  threshold, 
  status, 
}: { 
  name: string; 
  value: number; 
  threshold: number; 
  status: "good" | "bad" | "neutral";
}) {
  const getStatusInfo = (status: string) => {
    switch (status) {
      case "good":
        return { color: "bg-green-100 text-green-800", text: "良好" };
      case "bad":
        return { color: "bg-red-100 text-red-800", text: "要注意" };
      default:
        return { color: "bg-gray-100 text-gray-800", text: "普通" };
    }
  };

  const statusInfo = getStatusInfo(status);

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <div className="inline-flex items-center gap-1">
            <Badge variant="outline" className={statusInfo.color}>
              {name}: {value.toFixed(2)}
            </Badge>
            <HelpCircle className="h-3 w-3 text-gray-400" />
          </div>
        </TooltipTrigger>
        <TooltipContent className="max-w-xs p-3">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-medium">{name}</span>
              <Badge variant="outline" className={statusInfo.color}>
                {statusInfo.text}
              </Badge>
            </div>
            <div className="text-sm">
              <div>現在値: <span className="font-mono">{value.toFixed(2)}</span></div>
              <div>閾値: <span className="font-mono">{threshold.toFixed(2)}</span></div>
            </div>
            <div className="text-xs text-gray-600">
              {status === "good" && "この指標は良好な状態です"}
              {status === "bad" && "この指標は注意が必要です"}
              {status === "neutral" && "この指標は普通の状態です"}
            </div>
          </div>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
