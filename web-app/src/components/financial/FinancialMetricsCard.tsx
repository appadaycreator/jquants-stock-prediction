/**
 * 財務指標カードコンポーネント
 * ROE、ROA、PER、PBR等の財務指標を表示
 */

import React from "react";
import { FinancialMetrics } from "@/lib/financial/types";
import EnhancedTooltip from "../EnhancedTooltip";

interface FinancialMetricsCardProps {
  metrics: FinancialMetrics;
  title?: string;
  className?: string;
}

export function FinancialMetricsCard({ 
  metrics, 
  title = "財務指標", 
  className = "", 
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
                <EnhancedTooltip
                  content="自己資本利益率（ROE）です。自己資本に対する当期純利益の割合で、株主資本の運用効率を示します。15%以上が優秀、10-15%が良好、5-10%が普通、5%未満が要注意とされます。例：ROE 12%の場合、自己資本の12%の利益を上げていることを示します。"
                  type="info"
                >
                  <span className="text-sm font-medium cursor-help">{metrics.profitability.roe.toFixed(2)}%</span>
                </EnhancedTooltip>
                <span className="text-xs text-gray-500 ml-1">#{metrics.profitability.roeRanking}</span>
              </div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">ROA</span>
              <div className="text-right">
                <EnhancedTooltip
                  content="総資産利益率（ROA）です。総資産に対する当期純利益の割合で、資産の運用効率を示します。5%以上が優秀、3-5%が良好、1-3%が普通、1%未満が要注意とされます。例：ROA 4%の場合、総資産の4%の利益を上げていることを示します。"
                  type="info"
                >
                  <span className="text-sm font-medium cursor-help">{metrics.profitability.roa.toFixed(2)}%</span>
                </EnhancedTooltip>
                <span className="text-xs text-gray-500 ml-1">#{metrics.profitability.roaRanking}</span>
              </div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">売上高利益率</span>
              <div className="text-right">
                <EnhancedTooltip
                  content="売上高利益率です。売上高に対する当期純利益の割合で、売上の収益性を示します。10%以上が優秀、5-10%が良好、2-5%が普通、2%未満が要注意とされます。例：売上高利益率8%の場合、売上の8%が利益となっていることを示します。"
                  type="info"
                >
                  <span className="text-sm font-medium cursor-help">{metrics.profitability.profitMargin.toFixed(2)}%</span>
                </EnhancedTooltip>
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
                <EnhancedTooltip
                  content="株価収益率（PER）です。株価を1株当たり利益で割った値で、株価の割安・割高を判断する指標です。15倍以下が割安、15-25倍が適正、25倍以上が割高とされます。例：PER 18倍の場合、現在の株価は1株当たり利益の18倍で取引されていることを示します。"
                  type="info"
                >
                  <span className="text-sm font-medium cursor-help">{metrics.marketValuation.per.toFixed(2)}</span>
                </EnhancedTooltip>
                <span className="text-xs text-gray-500 ml-1">#{metrics.marketValuation.perRanking}</span>
              </div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">PBR</span>
              <div className="text-right">
                <EnhancedTooltip
                  content="株価純資産倍率（PBR）です。株価を1株当たり純資産で割った値で、株価の割安・割高を判断する指標です。1倍以下が割安、1-2倍が適正、2倍以上が割高とされます。例：PBR 1.5倍の場合、現在の株価は1株当たり純資産の1.5倍で取引されていることを示します。"
                  type="info"
                >
                  <span className="text-sm font-medium cursor-help">{metrics.marketValuation.pbr.toFixed(2)}</span>
                </EnhancedTooltip>
                <span className="text-xs text-gray-500 ml-1">#{metrics.marketValuation.pbrRanking}</span>
              </div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">PSR</span>
              <div className="text-right">
                <EnhancedTooltip
                  content="株価売上高倍率（PSR）です。株価を1株当たり売上高で割った値で、株価の割安・割高を判断する指標です。1倍以下が割安、1-3倍が適正、3倍以上が割高とされます。例：PSR 2倍の場合、現在の株価は1株当たり売上高の2倍で取引されていることを示します。"
                  type="info"
                >
                  <span className="text-sm font-medium cursor-help">{metrics.marketValuation.psr.toFixed(2)}</span>
                </EnhancedTooltip>
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
                <EnhancedTooltip
                  content="自己資本比率です。総資産に対する自己資本の割合で、財務の安定性を示します。30%以上が優秀、20-30%が良好、10-20%が普通、10%未満が要注意とされます。例：自己資本比率25%の場合、総資産の25%が自己資本で構成されていることを示します。"
                  type="info"
                >
                  <span className="text-sm font-medium cursor-help">{metrics.safety.equityRatio.toFixed(2)}%</span>
                </EnhancedTooltip>
                <span className="text-xs text-gray-500 ml-1">#{metrics.safety.equityRatioRanking}</span>
              </div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">流動比率</span>
              <div className="text-right">
                <EnhancedTooltip
                  content="流動比率です。流動資産を流動負債で割った値で、短期の支払い能力を示します。200%以上が優秀、150-200%が良好、100-150%が普通、100%未満が要注意とされます。例：流動比率180%の場合、流動負債の1.8倍の流動資産があることを示します。"
                  type="info"
                >
                  <span className="text-sm font-medium cursor-help">{metrics.safety.currentRatio.toFixed(2)}%</span>
                </EnhancedTooltip>
                <span className="text-xs text-gray-500 ml-1">#{metrics.safety.currentRatioRanking}</span>
              </div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">当座比率</span>
              <div className="text-right">
                <EnhancedTooltip
                  content="当座比率です。当座資産を流動負債で割った値で、即座の支払い能力を示します。100%以上が優秀、80-100%が良好、50-80%が普通、50%未満が要注意とされます。例：当座比率90%の場合、流動負債の90%を当座資産で支払えることを示します。"
                  type="info"
                >
                  <span className="text-sm font-medium cursor-help">{metrics.safety.quickRatio.toFixed(2)}%</span>
                </EnhancedTooltip>
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
                <EnhancedTooltip
                  content="売上高成長率です。前年同期比での売上高の増加率で、事業の成長性を示します。10%以上が優秀、5-10%が良好、0-5%が普通、マイナスが要注意とされます。例：売上高成長率8%の場合、前年同期比で8%の売上増加を示します。"
                  type="info"
                >
                  <span className="text-sm font-medium cursor-help">{metrics.growth.revenueGrowthRate.toFixed(2)}%</span>
                </EnhancedTooltip>
                <span className="text-xs text-gray-500 ml-1">#{metrics.growth.revenueGrowthRanking}</span>
              </div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">利益成長率</span>
              <div className="text-right">
                <EnhancedTooltip
                  content="利益成長率です。前年同期比での利益の増加率で、収益性の成長を示します。15%以上が優秀、5-15%が良好、0-5%が普通、マイナスが要注意とされます。例：利益成長率12%の場合、前年同期比で12%の利益増加を示します。"
                  type="info"
                >
                  <span className="text-sm font-medium cursor-help">{metrics.growth.profitGrowthRate.toFixed(2)}%</span>
                </EnhancedTooltip>
                <span className="text-xs text-gray-500 ml-1">#{metrics.growth.profitGrowthRanking}</span>
              </div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">資産成長率</span>
              <div className="text-right">
                <EnhancedTooltip
                  content="資産成長率です。前年同期比での総資産の増加率で、企業規模の成長を示します。10%以上が優秀、5-10%が良好、0-5%が普通、マイナスが要注意とされます。例：資産成長率7%の場合、前年同期比で7%の資産増加を示します。"
                  type="info"
                >
                  <span className="text-sm font-medium cursor-help">{metrics.growth.assetGrowthRate.toFixed(2)}%</span>
                </EnhancedTooltip>
                <span className="text-xs text-gray-500 ml-1">#{metrics.growth.assetGrowthRanking}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
