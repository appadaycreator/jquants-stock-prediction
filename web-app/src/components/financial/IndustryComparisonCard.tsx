/**
 * 業界比較分析カードコンポーネント
 * 業界内順位、パーセンタイルを表示
 */

import React from "react";
import { IndustryComparison } from "@/lib/financial/types";

interface IndustryComparisonCardProps {
  industryComparison: IndustryComparison;
  className?: string;
}

export function IndustryComparisonCard({ 
  industryComparison, 
  className = "", 
}: IndustryComparisonCardProps) {
  // 順位に基づく色を取得
  const getRankingColor = (ranking: number, total: number = 100) => {
    const percentile = (ranking / total) * 100;
    if (percentile <= 10) return "text-green-600";
    if (percentile <= 25) return "text-blue-600";
    if (percentile <= 50) return "text-yellow-600";
    if (percentile <= 75) return "text-orange-600";
    return "text-red-600";
  };

  // パーセンタイルに基づく色を取得
  const getPercentileColor = (percentile: number) => {
    if (percentile >= 90) return "text-green-600";
    if (percentile >= 75) return "text-blue-600";
    if (percentile >= 50) return "text-yellow-600";
    if (percentile >= 25) return "text-orange-600";
    return "text-red-600";
  };

  return (
    <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        業界比較分析 - {industryComparison.industry}
      </h3>
      
      {/* 総合順位 */}
      <div className="text-center mb-6">
        <div className="text-3xl font-bold text-gray-900 mb-2">
          #{industryComparison.companyRanking.overall}
        </div>
        <div className="text-sm text-gray-600">
          業界内総合順位
        </div>
        <div className={`text-lg font-semibold ${getPercentileColor(industryComparison.percentile.overall)}`}>
          上位{industryComparison.percentile.overall.toFixed(1)}%
        </div>
      </div>

      {/* 指標別順位 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="text-center">
          <div className="text-sm text-gray-600 mb-1">ROE順位</div>
          <div className={`text-xl font-semibold ${getRankingColor(industryComparison.companyRanking.roe)}`}>
            #{industryComparison.companyRanking.roe}
          </div>
          <div className={`text-sm ${getPercentileColor(industryComparison.percentile.roe)}`}>
            上位{industryComparison.percentile.roe.toFixed(1)}%
          </div>
        </div>
        
        <div className="text-center">
          <div className="text-sm text-gray-600 mb-1">ROA順位</div>
          <div className={`text-xl font-semibold ${getRankingColor(industryComparison.companyRanking.roa)}`}>
            #{industryComparison.companyRanking.roa}
          </div>
          <div className={`text-sm ${getPercentileColor(industryComparison.percentile.roa)}`}>
            上位{industryComparison.percentile.roa.toFixed(1)}%
          </div>
        </div>
        
        <div className="text-center">
          <div className="text-sm text-gray-600 mb-1">PER順位</div>
          <div className={`text-xl font-semibold ${getRankingColor(industryComparison.companyRanking.per)}`}>
            #{industryComparison.companyRanking.per}
          </div>
          <div className={`text-sm ${getPercentileColor(industryComparison.percentile.per)}`}>
            上位{industryComparison.percentile.per.toFixed(1)}%
          </div>
        </div>
        
        <div className="text-center">
          <div className="text-sm text-gray-600 mb-1">PBR順位</div>
          <div className={`text-xl font-semibold ${getRankingColor(industryComparison.companyRanking.pbr)}`}>
            #{industryComparison.companyRanking.pbr}
          </div>
          <div className={`text-sm ${getPercentileColor(industryComparison.percentile.pbr)}`}>
            上位{industryComparison.percentile.pbr.toFixed(1)}%
          </div>
        </div>
      </div>

      {/* 業界統計 */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h4 className="text-sm font-medium text-gray-700 mb-3">業界統計</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <div className="text-xs text-gray-600 mb-1">業界平均</div>
            <div className="text-sm text-gray-900">
              ROE: {industryComparison.industryAverage.profitability?.roe?.toFixed(2) || "N/A"}%
            </div>
            <div className="text-sm text-gray-900">
              ROA: {industryComparison.industryAverage.profitability?.roa?.toFixed(2) || "N/A"}%
            </div>
            <div className="text-sm text-gray-900">
              PER: {industryComparison.industryAverage.marketValuation?.per?.toFixed(2) || "N/A"}
            </div>
            <div className="text-sm text-gray-900">
              PBR: {industryComparison.industryAverage.marketValuation?.pbr?.toFixed(2) || "N/A"}
            </div>
          </div>
          
          <div>
            <div className="text-xs text-gray-600 mb-1">業界中央値</div>
            <div className="text-sm text-gray-900">
              ROE: {industryComparison.industryMedian.profitability?.roe?.toFixed(2) || "N/A"}%
            </div>
            <div className="text-sm text-gray-900">
              ROA: {industryComparison.industryMedian.profitability?.roa?.toFixed(2) || "N/A"}%
            </div>
            <div className="text-sm text-gray-900">
              PER: {industryComparison.industryMedian.marketValuation?.per?.toFixed(2) || "N/A"}
            </div>
            <div className="text-sm text-gray-900">
              PBR: {industryComparison.industryMedian.marketValuation?.pbr?.toFixed(2) || "N/A"}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
