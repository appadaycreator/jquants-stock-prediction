/**
 * 財務健全性スコアカードコンポーネント
 * 総合スコア、グレード、投資推奨を表示
 */

import React from "react";
import { FinancialHealthScore } from "@/lib/financial/types";

interface FinancialHealthScoreCardProps {
  healthScore: FinancialHealthScore;
  className?: string;
}

export function FinancialHealthScoreCard({ 
  healthScore, 
  className = "", 
}: FinancialHealthScoreCardProps) {
  // スコアに基づく色を取得
  const getScoreColor = (score: number) => {
    if (score >= 90) return "text-green-600";
    if (score >= 80) return "text-green-500";
    if (score >= 70) return "text-yellow-500";
    if (score >= 60) return "text-orange-500";
    return "text-red-500";
  };

  // グレードに基づく色を取得
  const getGradeColor = (grade: string) => {
    if (grade.startsWith("A")) return "text-green-600";
    if (grade.startsWith("B")) return "text-blue-600";
    if (grade.startsWith("C")) return "text-yellow-600";
    if (grade.startsWith("D")) return "text-orange-600";
    return "text-red-600";
  };

  // 推奨に基づく色を取得
  const getRecommendationColor = (recommendation: string) => {
    if (recommendation.includes("Buy")) return "text-green-600";
    if (recommendation.includes("Hold")) return "text-yellow-600";
    if (recommendation.includes("Sell")) return "text-red-600";
    return "text-gray-600";
  };

  // リスクレベルに基づく色を取得
  const getRiskColor = (riskLevel: string) => {
    if (riskLevel === "Low") return "text-green-600";
    if (riskLevel === "Medium") return "text-yellow-600";
    return "text-red-600";
  };

  return (
    <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
      <h3 className="text-lg font-semibold text-gray-900 mb-4">財務健全性スコア</h3>
      
      {/* 総合スコア */}
      <div className="text-center mb-6">
        <div className="text-4xl font-bold text-gray-900 mb-2">
          {healthScore.overallScore.toFixed(1)}
        </div>
        <div className={`text-2xl font-semibold ${getGradeColor(healthScore.grade)}`}>
          {healthScore.grade}
        </div>
        <div className={`text-lg font-medium ${getRecommendationColor(healthScore.recommendation)}`}>
          {healthScore.recommendation}
        </div>
        <div className={`text-sm ${getRiskColor(healthScore.riskLevel)}`}>
          リスクレベル: {healthScore.riskLevel}
        </div>
      </div>

      {/* 詳細スコア */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="text-center">
          <div className="text-sm text-gray-600 mb-1">収益性</div>
          <div className={`text-lg font-semibold ${getScoreColor(healthScore.profitabilityScore)}`}>
            {healthScore.profitabilityScore.toFixed(1)}
          </div>
        </div>
        
        <div className="text-center">
          <div className="text-sm text-gray-600 mb-1">市場評価</div>
          <div className={`text-lg font-semibold ${getScoreColor(healthScore.marketScore)}`}>
            {healthScore.marketScore.toFixed(1)}
          </div>
        </div>
        
        <div className="text-center">
          <div className="text-sm text-gray-600 mb-1">安全性</div>
          <div className={`text-lg font-semibold ${getScoreColor(healthScore.safetyScore)}`}>
            {healthScore.safetyScore.toFixed(1)}
          </div>
        </div>
        
        <div className="text-center">
          <div className="text-sm text-gray-600 mb-1">成長性</div>
          <div className={`text-lg font-semibold ${getScoreColor(healthScore.growthScore)}`}>
            {healthScore.growthScore.toFixed(1)}
          </div>
        </div>
      </div>

      {/* SWOT分析 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* 強み */}
        <div className="bg-green-50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-green-800 mb-2">強み</h4>
          <ul className="text-sm text-green-700 space-y-1">
            {healthScore.strengths.map((strength, index) => (
              <li key={index} className="flex items-center">
                <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                {strength}
              </li>
            ))}
          </ul>
        </div>

        {/* 弱み */}
        <div className="bg-red-50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-red-800 mb-2">弱み</h4>
          <ul className="text-sm text-red-700 space-y-1">
            {healthScore.weaknesses.map((weakness, index) => (
              <li key={index} className="flex items-center">
                <span className="w-2 h-2 bg-red-500 rounded-full mr-2"></span>
                {weakness}
              </li>
            ))}
          </ul>
        </div>

        {/* 機会 */}
        <div className="bg-blue-50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-blue-800 mb-2">機会</h4>
          <ul className="text-sm text-blue-700 space-y-1">
            {healthScore.opportunities.map((opportunity, index) => (
              <li key={index} className="flex items-center">
                <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                {opportunity}
              </li>
            ))}
          </ul>
        </div>

        {/* 脅威 */}
        <div className="bg-orange-50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-orange-800 mb-2">脅威</h4>
          <ul className="text-sm text-orange-700 space-y-1">
            {healthScore.threats.map((threat, index) => (
              <li key={index} className="flex items-center">
                <span className="w-2 h-2 bg-orange-500 rounded-full mr-2"></span>
                {threat}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
