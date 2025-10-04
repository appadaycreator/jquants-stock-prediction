/**
 * 財務指標カードコンポーネント
 * ROE、ROA、PER、PBR等の財務指標を表示
 */

import React from 'react';
import { FinancialMetrics } from '@/lib/financial/types';

interface FinancialMetricsCardProps {
  metrics: FinancialMetrics;
  title?: string;
  className?: string;
}

export function FinancialMetricsCard({ 
  metrics, 
  title = '財務指標', 
  className = '' 
}: FinancialMetricsCardProps) {
  return (
    <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* 収益性指標 */}
        <div className="space-y-3">
          <h4 className="text-sm font-medium text-gray-700 border-b pb-2">収益性指標</h4>
          
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">ROE</span>
              <div className="text-right">
                <span className="text-sm font-medium">{metrics.profitability.roe.toFixed(2)}%</span>
                <span className="text-xs text-gray-500 ml-1">#{metrics.profitability.roeRanking}</span>
              </div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">ROA</span>
              <div className="text-right">
                <span className="text-sm font-medium">{metrics.profitability.roa.toFixed(2)}%</span>
                <span className="text-xs text-gray-500 ml-1">#{metrics.profitability.roaRanking}</span>
              </div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">売上高利益率</span>
              <div className="text-right">
                <span className="text-sm font-medium">{metrics.profitability.profitMargin.toFixed(2)}%</span>
                <span className="text-xs text-gray-500 ml-1">#{metrics.profitability.profitMarginRanking}</span>
              </div>
            </div>
          </div>
        </div>

        {/* 市場評価指標 */}
        <div className="space-y-3">
          <h4 className="text-sm font-medium text-gray-700 border-b pb-2">市場評価指標</h4>
          
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">PER</span>
              <div className="text-right">
                <span className="text-sm font-medium">{metrics.marketValuation.per.toFixed(2)}</span>
                <span className="text-xs text-gray-500 ml-1">#{metrics.marketValuation.perRanking}</span>
              </div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">PBR</span>
              <div className="text-right">
                <span className="text-sm font-medium">{metrics.marketValuation.pbr.toFixed(2)}</span>
                <span className="text-xs text-gray-500 ml-1">#{metrics.marketValuation.pbrRanking}</span>
              </div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">PSR</span>
              <div className="text-right">
                <span className="text-sm font-medium">{metrics.marketValuation.psr.toFixed(2)}</span>
                <span className="text-xs text-gray-500 ml-1">#{metrics.marketValuation.psrRanking}</span>
              </div>
            </div>
          </div>
        </div>

        {/* 安全性指標 */}
        <div className="space-y-3">
          <h4 className="text-sm font-medium text-gray-700 border-b pb-2">安全性指標</h4>
          
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">自己資本比率</span>
              <div className="text-right">
                <span className="text-sm font-medium">{metrics.safety.equityRatio.toFixed(2)}%</span>
                <span className="text-xs text-gray-500 ml-1">#{metrics.safety.equityRatioRanking}</span>
              </div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">流動比率</span>
              <div className="text-right">
                <span className="text-sm font-medium">{metrics.safety.currentRatio.toFixed(2)}%</span>
                <span className="text-xs text-gray-500 ml-1">#{metrics.safety.currentRatioRanking}</span>
              </div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">当座比率</span>
              <div className="text-right">
                <span className="text-sm font-medium">{metrics.safety.quickRatio.toFixed(2)}%</span>
                <span className="text-xs text-gray-500 ml-1">#{metrics.safety.quickRatioRanking}</span>
              </div>
            </div>
          </div>
        </div>

        {/* 成長性指標 */}
        <div className="space-y-3">
          <h4 className="text-sm font-medium text-gray-700 border-b pb-2">成長性指標</h4>
          
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">売上高成長率</span>
              <div className="text-right">
                <span className="text-sm font-medium">{metrics.growth.revenueGrowthRate.toFixed(2)}%</span>
                <span className="text-xs text-gray-500 ml-1">#{metrics.growth.revenueGrowthRanking}</span>
              </div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">利益成長率</span>
              <div className="text-right">
                <span className="text-sm font-medium">{metrics.growth.profitGrowthRate.toFixed(2)}%</span>
                <span className="text-xs text-gray-500 ml-1">#{metrics.growth.profitGrowthRanking}</span>
              </div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">資産成長率</span>
              <div className="text-right">
                <span className="text-sm font-medium">{metrics.growth.assetGrowthRate.toFixed(2)}%</span>
                <span className="text-xs text-gray-500 ml-1">#{metrics.growth.assetGrowthRanking}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
