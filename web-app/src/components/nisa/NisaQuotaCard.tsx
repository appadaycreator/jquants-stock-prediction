/**
 * 新NISA投資枠利用状況カードコンポーネント
 * 成長投資枠とつみたて投資枠の利用状況を表示
 */

import React from "react";
import { Progress } from "@/components/ui/progress";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { AlertTriangle, TrendingUp, TrendingDown } from "lucide-react";
import { NisaQuotaStatus } from "@/lib/nisa/types";

interface NisaQuotaCardProps {
  quotas: NisaQuotaStatus;
  className?: string;
}

export default function NisaQuotaCard({ quotas, className }: NisaQuotaCardProps) {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("ja-JP", {
      style: "currency",
      currency: "JPY",
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const getUtilizationColor = (rate: number) => {
    if (rate >= 90) return "text-red-600";
    if (rate >= 70) return "text-yellow-600";
    return "text-green-600";
  };

  const getUtilizationBadgeVariant = (rate: number) => {
    if (rate >= 90) return "destructive";
    if (rate >= 70) return "secondary";
    return "default";
  };

  const getUtilizationIcon = (rate: number) => {
    if (rate >= 90) return <AlertTriangle className="w-4 h-4" />;
    if (rate >= 70) return <TrendingUp className="w-4 h-4" />;
    return <TrendingDown className="w-4 h-4" />;
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* 成長投資枠 */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center justify-between">
            <span className="text-lg font-semibold">成長投資枠</span>
            <Badge variant={getUtilizationBadgeVariant(quotas.growthInvestment.utilizationRate)}>
              {getUtilizationIcon(quotas.growthInvestment.utilizationRate)}
              {quotas.growthInvestment.utilizationRate.toFixed(1)}%
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>利用済み</span>
              <span className={getUtilizationColor(quotas.growthInvestment.utilizationRate)}>
                {formatCurrency(quotas.growthInvestment.usedAmount)}
              </span>
            </div>
            <Progress 
              value={quotas.growthInvestment.utilizationRate} 
              className="h-2"
            />
            <div className="flex justify-between text-sm text-gray-600">
              <span>利用可能</span>
              <span>{formatCurrency(quotas.growthInvestment.availableAmount)}</span>
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <div className="text-gray-600">年間投資枠</div>
              <div className="font-medium">{formatCurrency(quotas.growthInvestment.annualLimit)}</div>
            </div>
            <div>
              <div className="text-gray-600">非課税保有限度額</div>
              <div className="font-medium">{formatCurrency(quotas.growthInvestment.taxFreeLimit)}</div>
            </div>
          </div>

          {quotas.growthInvestment.utilizationRate >= 70 && (
            <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
              <div className="flex items-center text-yellow-800 text-sm">
                <AlertTriangle className="w-4 h-4 mr-2" />
                {quotas.growthInvestment.utilizationRate >= 90 
                  ? "成長投資枠の利用率が90%を超えています。投資計画の見直しを検討してください。"
                  : "成長投資枠の利用率が70%を超えています。投資計画の見直しを検討してください。"
                }
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* つみたて投資枠 */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center justify-between">
            <span className="text-lg font-semibold">つみたて投資枠</span>
            <Badge variant={getUtilizationBadgeVariant(quotas.accumulationInvestment.utilizationRate)}>
              {getUtilizationIcon(quotas.accumulationInvestment.utilizationRate)}
              {quotas.accumulationInvestment.utilizationRate.toFixed(1)}%
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>利用済み</span>
              <span className={getUtilizationColor(quotas.accumulationInvestment.utilizationRate)}>
                {formatCurrency(quotas.accumulationInvestment.usedAmount)}
              </span>
            </div>
            <Progress 
              value={quotas.accumulationInvestment.utilizationRate} 
              className="h-2"
            />
            <div className="flex justify-between text-sm text-gray-600">
              <span>利用可能</span>
              <span>{formatCurrency(quotas.accumulationInvestment.availableAmount)}</span>
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <div className="text-gray-600">年間投資枠</div>
              <div className="font-medium">{formatCurrency(quotas.accumulationInvestment.annualLimit)}</div>
            </div>
            <div>
              <div className="text-gray-600">非課税保有限度額</div>
              <div className="font-medium">{formatCurrency(quotas.accumulationInvestment.taxFreeLimit)}</div>
            </div>
          </div>

          {quotas.accumulationInvestment.utilizationRate >= 70 && (
            <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
              <div className="flex items-center text-yellow-800 text-sm">
                <AlertTriangle className="w-4 h-4 mr-2" />
                つみたて投資枠の利用率が70%を超えています。積立投資の見直しを検討してください。
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 枠の再利用状況 */}
      {(quotas.quotaReuse.growthAvailable > 0 || quotas.quotaReuse.accumulationAvailable > 0) && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg font-semibold">枠の再利用状況</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <div className="text-gray-600">成長枠再利用可能額</div>
                <div className="font-medium text-green-600">
                  {formatCurrency(quotas.quotaReuse.growthAvailable)}
                </div>
              </div>
              <div>
                <div className="text-gray-600">つみたて枠再利用可能額</div>
                <div className="font-medium text-green-600">
                  {formatCurrency(quotas.quotaReuse.accumulationAvailable)}
                </div>
              </div>
            </div>
            <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
              <div className="text-green-800 text-sm">
                翌年度に {formatCurrency(quotas.quotaReuse.nextYearAvailable)} の投資枠が再利用可能です
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
