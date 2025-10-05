"use client";

import React, { useState, useEffect } from "react";
import { AlertTriangle, TrendingDown, Shield, Target, Download, Calendar } from "lucide-react";

interface RiskMetrics {
  var95: number;
  var99: number;
  maxDrawdown: number;
  volatility: number;
  sharpeRatio: number;
  beta: number;
}

interface PortfolioRisk {
  totalValue: number;
  riskTolerance: number;
  currentRisk: number;
  riskExceeded: boolean;
  recommendations: string[];
}

interface RiskManagementProps {
  riskMetrics?: RiskMetrics;
  portfolioRisk?: PortfolioRisk;
  isLoading?: boolean;
  error?: Error | null;
  onRiskToleranceChange?: (tolerance: number) => void;
}

export const RiskManagement: React.FC<RiskManagementProps> = ({
  riskMetrics,
  portfolioRisk,
  isLoading = false,
  error,
  onRiskToleranceChange,
}) => {
  const [riskTolerance, setRiskTolerance] = useState(portfolioRisk?.riskTolerance || 0.15);
  const [showRecommendations, setShowRecommendations] = useState(false);

  const handleRiskToleranceChange = (value: number) => {
    setRiskTolerance(value);
    onRiskToleranceChange?.(value);
  };

  const getRiskLevel = (risk: number) => {
    if (risk < 0.1) return { level: "Low", color: "text-green-600 bg-green-100" };
    if (risk < 0.2) return { level: "Medium", color: "text-yellow-600 bg-yellow-100" };
    return { level: "High", color: "text-red-600 bg-red-100" };
  };

  const getRiskColor = (risk: number) => {
    if (risk < 0.1) return "text-green-600";
    if (risk < 0.2) return "text-yellow-600";
    return "text-red-600";
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-white rounded-lg shadow-md p-6 animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
            <div className="h-8 bg-gray-200 rounded w-1/2 mb-2"></div>
            <div className="h-3 bg-gray-200 rounded w-full"></div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center space-x-2 text-red-800">
          <AlertTriangle className="w-5 h-5" />
          <span className="font-medium">リスクデータの読み込みに失敗しました</span>
        </div>
        <p className="text-red-600 mt-2">{error.message}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* リスク許容度設定 */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">リスク許容度設定</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              リスク許容度: {Math.round(riskTolerance * 100)}%
            </label>
            <input
              type="range"
              min="0.05"
              max="0.3"
              step="0.01"
              value={riskTolerance}
              onChange={(e) => handleRiskToleranceChange(parseFloat(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>保守的 (5%)</span>
              <span>バランス (15%)</span>
              <span>積極的 (30%)</span>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-gray-900">
                ¥{(portfolioRisk?.totalValue || 0).toLocaleString()}
              </div>
              <div className="text-sm text-gray-600">ポートフォリオ総額</div>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className={`text-2xl font-bold ${getRiskColor(portfolioRisk?.currentRisk || 0)}`}>
                {Math.round((portfolioRisk?.currentRisk || 0) * 100)}%
              </div>
              <div className="text-sm text-gray-600">現在のリスク</div>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className={`text-2xl font-bold ${getRiskColor(riskTolerance)}`}>
                {Math.round(riskTolerance * 100)}%
              </div>
              <div className="text-sm text-gray-600">許容リスク</div>
            </div>
          </div>
        </div>
      </div>

      {/* リスク指標 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">VaR (95%)</p>
              <p className="text-2xl font-bold text-red-600">
                -{riskMetrics?.var95?.toFixed(2) || "--"}%
              </p>
            </div>
            <AlertTriangle className="w-8 h-8 text-red-500" />
          </div>
          <p className="text-xs text-gray-500 mt-2">
            95%の確率でこの損失を超えない
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">最大ドローダウン</p>
              <p className="text-2xl font-bold text-orange-600">
                -{riskMetrics?.maxDrawdown?.toFixed(2) || "--"}%
              </p>
            </div>
            <TrendingDown className="w-8 h-8 text-orange-500" />
          </div>
          <p className="text-xs text-gray-500 mt-2">
            過去最大の下落幅
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">ボラティリティ</p>
              <p className="text-2xl font-bold text-blue-600">
                {riskMetrics?.volatility?.toFixed(2) || "--"}%
              </p>
            </div>
            <Shield className="w-8 h-8 text-blue-500" />
          </div>
          <p className="text-xs text-gray-500 mt-2">
            価格変動の激しさ
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">シャープレシオ</p>
              <p className="text-2xl font-bold text-green-600">
                {riskMetrics?.sharpeRatio?.toFixed(2) || "--"}
              </p>
            </div>
            <Target className="w-8 h-8 text-green-500" />
          </div>
          <p className="text-xs text-gray-500 mt-2">
            リスク調整後リターン
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">ベータ</p>
              <p className="text-2xl font-bold text-purple-600">
                {riskMetrics?.beta?.toFixed(2) || "--"}
              </p>
            </div>
            <TrendingDown className="w-8 h-8 text-purple-500" />
          </div>
          <p className="text-xs text-gray-500 mt-2">
            市場との連動性
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">リスクレベル</p>
              <p className="text-2xl font-bold">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-sm font-medium ${
                  getRiskLevel(portfolioRisk?.currentRisk || 0).color
                }`}>
                  {getRiskLevel(portfolioRisk?.currentRisk || 0).level}
                </span>
              </p>
            </div>
            <Shield className="w-8 h-8 text-gray-500" />
          </div>
          <p className="text-xs text-gray-500 mt-2">
            現在のリスク評価
          </p>
        </div>
      </div>

      {/* リスク警告 */}
      {portfolioRisk?.riskExceeded && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-start space-x-3">
            <AlertTriangle className="w-6 h-6 text-red-500 mt-0.5" />
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-red-800 mb-2">
                リスク許容度を超過しています
              </h3>
              <p className="text-red-700 mb-4">
                現在のポートフォリオリスクが設定した許容度を超えています。
                リバランスを検討してください。
              </p>
              <button
                onClick={() => setShowRecommendations(!showRecommendations)}
                className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 transition-colors"
              >
                {showRecommendations ? "推奨事項を隠す" : "推奨事項を表示"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 推奨事項 */}
      {showRecommendations && portfolioRisk?.recommendations && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-800 mb-4">リスク軽減の推奨事項</h3>
          <ul className="space-y-2">
            {portfolioRisk.recommendations.map((recommendation, index) => (
              <li key={index} className="flex items-start space-x-2 text-blue-700">
                <span className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></span>
                <span>{recommendation}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* シナリオ分析 */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">シナリオ分析</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-lg font-bold text-gray-900">
              -{riskMetrics?.var95?.toFixed(1) || "--"}%
            </div>
            <div className="text-sm text-gray-600">通常市場</div>
            <div className="text-xs text-gray-500">95%の確率</div>
          </div>
          <div className="text-center p-4 bg-yellow-50 rounded-lg">
            <div className="text-lg font-bold text-yellow-800">
              -{((riskMetrics?.var95 || 0) * 1.5).toFixed(1)}%
            </div>
            <div className="text-sm text-yellow-700">市場調整</div>
            <div className="text-xs text-yellow-600">85%の確率</div>
          </div>
          <div className="text-center p-4 bg-red-50 rounded-lg">
            <div className="text-lg font-bold text-red-800">
              -{((riskMetrics?.var95 || 0) * 2).toFixed(1)}%
            </div>
            <div className="text-sm text-red-700">市場暴落</div>
            <div className="text-xs text-red-600">70%の確率</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RiskManagement;
