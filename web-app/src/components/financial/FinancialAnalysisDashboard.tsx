/**
 * 財務分析ダッシュボードコンポーネント
 * 財務指標分析の統合表示
 */

import React, { useState, useEffect } from "react";
import { useFinancialAnalysis } from "@/hooks/useFinancialAnalysis";
import { FinancialMetricsCard } from "./FinancialMetricsCard";
import { FinancialHealthScoreCard } from "./FinancialHealthScoreCard";
import { IndustryComparisonCard } from "./IndustryComparisonCard";

interface FinancialAnalysisDashboardProps {
  symbol: string;
  className?: string;
}

export function FinancialAnalysisDashboard({ 
  symbol, 
  className = "", 
}: FinancialAnalysisDashboardProps) {
  const {
    data,
    loading,
    error,
    refreshData,
    metrics,
    healthScore,
    industryComparison,
    historicalAnalysis,
    statistics,
  } = useFinancialAnalysis();

  const [activeTab, setActiveTab] = useState<"overview" | "metrics" | "industry" | "historical">("overview");

  useEffect(() => {
    if (symbol) {
      refreshData(symbol);
    }
  }, [symbol, refreshData]);

  if (loading) {
    return (
      <div className={`flex items-center justify-center p-8 ${className}`}>
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">財務指標を計算中...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`bg-red-50 border border-red-200 rounded-lg p-6 ${className}`}>
        <div className="text-center">
          <div className="text-red-600 text-lg font-semibold mb-2">エラーが発生しました</div>
          <p className="text-red-700 mb-4">{error}</p>
          <button
            onClick={() => refreshData(symbol)}
            className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
          >
            再試行
          </button>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className={`bg-gray-50 border border-gray-200 rounded-lg p-6 ${className}`}>
        <div className="text-center">
          <div className="text-gray-600 text-lg font-semibold mb-2">データが見つかりません</div>
          <p className="text-gray-700 mb-4">財務データを取得できませんでした</p>
          <button
            onClick={() => refreshData(symbol)}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            データを取得
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* ヘッダー */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">財務分析ダッシュボード</h2>
            <p className="text-gray-600">銘柄: {symbol}</p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold text-gray-900">{statistics.overallScore.toFixed(1)}</div>
            <div className="text-lg font-semibold text-blue-600">{statistics.grade}</div>
            <div className="text-sm text-gray-600">{statistics.recommendation}</div>
          </div>
        </div>
      </div>

      {/* タブナビゲーション */}
      <div className="bg-white rounded-lg shadow-md">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {[
              { id: "overview", label: "概要", icon: "📊" },
              { id: "metrics", label: "財務指標", icon: "📈" },
              { id: "industry", label: "業界比較", icon: "🏢" },
              { id: "historical", label: "時系列", icon: "📅" },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? "border-blue-500 text-blue-600"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* タブコンテンツ */}
        <div className="p-6">
          {activeTab === "overview" && (
            <div className="space-y-6">
              {healthScore && (
                <FinancialHealthScoreCard healthScore={healthScore} />
              )}
            </div>
          )}

          {activeTab === "metrics" && (
            <div className="space-y-6">
              {metrics && (
                <FinancialMetricsCard metrics={metrics} />
              )}
            </div>
          )}

          {activeTab === "industry" && (
            <div className="space-y-6">
              {industryComparison && (
                <IndustryComparisonCard industryComparison={industryComparison} />
              )}
            </div>
          )}

          {activeTab === "historical" && (
            <div className="space-y-6">
              {historicalAnalysis ? (
                <div className="bg-white rounded-lg shadow-md p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">時系列分析</h3>
                  <div className="text-center text-gray-600">
                    <p>時系列データの表示機能は開発中です</p>
                    <p className="text-sm mt-2">
                      安定性: {historicalAnalysis.stability} | 
                      一貫性: {historicalAnalysis.consistency}
                    </p>
                  </div>
                </div>
              ) : (
                <div className="bg-gray-50 rounded-lg p-6 text-center">
                  <p className="text-gray-600">時系列データが利用できません</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
