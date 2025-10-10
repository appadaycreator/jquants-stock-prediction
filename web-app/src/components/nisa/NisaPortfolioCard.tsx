/**
 * 新NISAポートフォリオカードコンポーネント
 * 投資状況と損益を表示
 */

import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, TrendingDown, DollarSign, Target } from "lucide-react";
import { NisaPortfolio, NisaPosition } from "@/lib/nisa/types";
import EnhancedTooltip from "../EnhancedTooltip";

interface NisaPortfolioCardProps {
  portfolio: NisaPortfolio;
  className?: string;
}

export default function NisaPortfolioCard({ portfolio, className }: NisaPortfolioCardProps) {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("ja-JP", {
      style: "currency",
      currency: "JPY",
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const formatPercentage = (value: number) => {
    return `${value >= 0 ? "+" : ""}${value.toFixed(2)}%`;
  };

  const getProfitLossColor = (value: number) => {
    if (value > 0) return "text-green-600";
    if (value < 0) return "text-red-600";
    return "text-gray-600";
  };

  const getProfitLossIcon = (value: number) => {
    if (value > 0) return <TrendingUp className="w-4 h-4" />;
    if (value < 0) return <TrendingDown className="w-4 h-4" />;
    return null;
  };

  const totalReturnRate = portfolio.totalCost > 0 
    ? (portfolio.unrealizedProfitLoss / portfolio.totalCost) * 100 
    : 0;

  const taxFreeReturnRate = portfolio.totalCost > 0 
    ? (portfolio.taxFreeProfitLoss / portfolio.totalCost) * 100 
    : 0;

  return (
    <div className={`space-y-6 ${className}`}>
      {/* ポートフォリオサマリー */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2">
            <DollarSign className="w-5 h-5" />
            ポートフォリオサマリー
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-sm text-gray-600">総投資額</div>
              <EnhancedTooltip
                content="新NISA口座に投資した総金額です。株式の購入代金、手数料、税金などを含む実際の投資コストの合計です。例：100万円の株式を購入した場合、手数料1,000円、税金500円を含めて1,001,500円が総投資額となります。"
                type="info"
              >
                <div className="text-lg font-semibold cursor-help">{formatCurrency(portfolio.totalCost)}</div>
              </EnhancedTooltip>
            </div>
            <div>
              <div className="text-sm text-gray-600">現在価値</div>
              <EnhancedTooltip
                content="現在の市場価格で評価した保有株式の総額です。実際に売却した場合の概算価値となります。例：100万円で購入した株式が現在120万円の価値になっている場合、現在価値は120万円となります。"
                type="success"
              >
                <div className="text-lg font-semibold cursor-help">{formatCurrency(portfolio.totalValue)}</div>
              </EnhancedTooltip>
            </div>
          </div>

          <div className="border-t pt-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">未実現損益</span>
              <EnhancedTooltip
                content="現在価値から総投資額を引いた未実現損益です。プラスは利益、マイナスは損失を示します。実際に売却するまで確定しません。例：100万円で購入した株式が現在120万円の価値の場合、未実現損益は+20万円となります。"
                type={portfolio.unrealizedProfitLoss >= 0 ? "success" : "warning"}
              >
                <div className={`flex items-center gap-1 cursor-help ${getProfitLossColor(portfolio.unrealizedProfitLoss)}`}>
                  {getProfitLossIcon(portfolio.unrealizedProfitLoss)}
                  <span className="font-semibold">{formatCurrency(portfolio.unrealizedProfitLoss)}</span>
                  <span className="text-sm">({formatPercentage(totalReturnRate)})</span>
                </div>
              </EnhancedTooltip>
            </div>
          </div>

          <div className="border-t pt-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">実現損益</span>
              <div className={`flex items-center gap-1 ${getProfitLossColor(portfolio.realizedProfitLoss)}`}>
                {getProfitLossIcon(portfolio.realizedProfitLoss)}
                <span className="font-semibold">{formatCurrency(portfolio.realizedProfitLoss)}</span>
              </div>
            </div>
          </div>

          <div className="border-t pt-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">非課税枠内損益</span>
              <div className={`flex items-center gap-1 ${getProfitLossColor(portfolio.taxFreeProfitLoss)}`}>
                {getProfitLossIcon(portfolio.taxFreeProfitLoss)}
                <span className="font-semibold">{formatCurrency(portfolio.taxFreeProfitLoss)}</span>
                <span className="text-sm">({formatPercentage(taxFreeReturnRate)})</span>
              </div>
            </div>
            <div className="text-xs text-gray-500">
              非課税枠内の損益は税金がかかりません
            </div>
          </div>
        </CardContent>
      </Card>

      {/* ポジション一覧 */}
      {portfolio.positions.length > 0 && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2">
              <Target className="w-5 h-5" />
              保有銘柄 ({portfolio.positions.length}件)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {portfolio.positions.map((position, index) => (
                <PositionItem key={`${position.symbol}_${position.quotaType}_${index}`} position={position} />
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* 空の状態 */}
      {portfolio.positions.length === 0 && (
        <Card>
          <CardContent className="py-8 text-center">
            <div className="text-gray-500">
              <DollarSign className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p className="text-lg font-medium mb-2">保有銘柄がありません</p>
              <p className="text-sm">新NISA枠を活用して投資を始めましょう</p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

interface PositionItemProps {
  position: NisaPosition;
}

function PositionItem({ position }: PositionItemProps) {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("ja-JP", {
      style: "currency",
      currency: "JPY",
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const formatPercentage = (value: number) => {
    return `${value >= 0 ? "+" : ""}${value.toFixed(2)}%`;
  };

  const getProfitLossColor = (value: number) => {
    if (value > 0) return "text-green-600";
    if (value < 0) return "text-red-600";
    return "text-gray-600";
  };

  const getQuotaTypeColor = (quotaType: string) => {
    return quotaType === "GROWTH" ? "bg-blue-100 text-blue-800" : "bg-green-100 text-green-800";
  };

  const getQuotaTypeLabel = (quotaType: string) => {
    return quotaType === "GROWTH" ? "成長" : "つみたて";
  };

  const returnRate = position.cost > 0 ? (position.unrealizedProfitLoss / position.cost) * 100 : 0;

  return (
    <div className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50">
      <div className="flex-1">
        <div className="flex items-center gap-2 mb-1">
          <span className="font-medium">{position.symbolName}</span>
          <span className="text-sm text-gray-500">({position.symbol})</span>
          <Badge className={getQuotaTypeColor(position.quotaType)}>
            {getQuotaTypeLabel(position.quotaType)}
          </Badge>
        </div>
        <EnhancedTooltip
          content="保有株式数と現在の株価です。例：100株を3,000円で保有している場合、100株 × ¥3,000と表示されます。"
          type="info"
        >
          <div className="text-sm text-gray-600 cursor-help">
            {position.quantity}株 × {formatCurrency(position.currentPrice)}
          </div>
        </EnhancedTooltip>
      </div>
      
      <div className="text-right">
        <EnhancedTooltip
          content="現在の市場価格で評価した保有株式の総額です。例：100株を3,000円で保有している場合、現在価値は30万円となります。"
          type="success"
        >
          <div className="font-medium cursor-help">{formatCurrency(position.currentValue)}</div>
        </EnhancedTooltip>
        <EnhancedTooltip
          content="現在価値から投資額を引いた未実現損益とその割合です。例：30万円の投資で35万円の価値の場合、+5万円（+16.67%）となります。"
          type={position.unrealizedProfitLoss >= 0 ? "success" : "warning"}
        >
          <div className={`text-sm cursor-help ${getProfitLossColor(position.unrealizedProfitLoss)}`}>
            {formatCurrency(position.unrealizedProfitLoss)} ({formatPercentage(returnRate)})
          </div>
        </EnhancedTooltip>
      </div>
    </div>
  );
}
