"use client";

import { useState } from "react";
import { ChevronDown, ChevronRight } from "lucide-react";
import HelpTooltip from "./Tooltip";

interface FeatureCategory {
  id: string;
  name: string;
  description: string;
  features: FeatureItem[];
}

interface FeatureItem {
  key: string;
  label: string;
  description: string;
  recommended: boolean;
}

const featureCategories: FeatureCategory[] = [
  {
    id: "moving_averages",
    name: "移動平均系",
    description: "価格のトレンドを分析するための移動平均線とその派生指標",
    features: [
      {
        key: "sma_5",
        label: "SMA_5",
        description: "5日単純移動平均。短期トレンドの方向性を示します。推奨値：短期分析に有効",
        recommended: true,
      },
      {
        key: "sma_10",
        label: "SMA_10",
        description: "10日単純移動平均。中短期トレンドの確認に使用。推奨値：バランスの取れた分析",
        recommended: true,
      },
      {
        key: "sma_25",
        label: "SMA_25",
        description: "25日単純移動平均。中期トレンドの判断に使用。推奨値：中期分析の基準",
        recommended: true,
      },
      {
        key: "sma_50",
        label: "SMA_50",
        description: "50日単純移動平均。長期トレンドの確認に使用。推奨値：長期トレンド分析",
        recommended: false,
      },
    ],
  },
  {
    id: "oscillators",
    name: "オシレーター系",
    description: "価格の過買い・過売り状態を判断するための振動系指標",
    features: [
      {
        key: "rsi",
        label: "RSI",
        description: "相対力指数。0-100の範囲で過買い・過売りを判断。推奨値：30以下で買い、70以上で売り",
        recommended: true,
      },
      {
        key: "macd",
        label: "MACD",
        description: "移動平均収束発散。トレンドの変化を捉える。推奨値：シグナルラインとの交差で判断",
        recommended: true,
      },
    ],
  },
  {
    id: "volatility",
    name: "ボラティリティ系",
    description: "価格の変動率を測定する指標",
    features: [
      {
        key: "bollinger_upper",
        label: "ボリンジャー上",
        description: "ボリンジャーバンドの上限。価格が上回ると過買いの可能性。推奨値：価格が上回ったら売りシグナル",
        recommended: true,
      },
      {
        key: "bollinger_lower",
        label: "ボリンジャー下",
        description: "ボリンジャーバンドの下限。価格が下回ると過売りの可能性。推奨値：価格が下回ったら買いシグナル",
        recommended: true,
      },
    ],
  },
  {
    id: "volume",
    name: "出来高系",
    description: "取引量に基づく分析指標",
    features: [
      {
        key: "volume_sma",
        label: "出来高移動平均",
        description: "出来高の移動平均。取引の活発さを測定。推奨値：価格上昇時の出来高増加を確認",
        recommended: false,
      },
      {
        key: "volume_ratio",
        label: "出来高比率",
        description: "現在の出来高と平均出来高の比率。推奨値：1.5以上で異常な取引量",
        recommended: false,
      },
    ],
  },
];

interface FeatureCategoriesProps {
  selectedFeatures: string[];
  onFeatureChange: (features: string[]) => void;
}

export default function FeatureCategories({ 
  selectedFeatures, 
  onFeatureChange, 
}: FeatureCategoriesProps) {
  const [expandedCategories, setExpandedCategories] = useState<string[]>([
    "moving_averages", 
    "oscillators", 
    "volatility",
  ]);

  const toggleCategory = (categoryId: string) => {
    setExpandedCategories(prev => 
      prev.includes(categoryId) 
        ? prev.filter(id => id !== categoryId)
        : [...prev, categoryId],
    );
  };

  const handleFeatureToggle = (featureKey: string, checked: boolean) => {
    if (checked) {
      onFeatureChange([...selectedFeatures, featureKey]);
    } else {
      onFeatureChange(selectedFeatures.filter(f => f !== featureKey));
    }
  };

  const selectRecommended = () => {
    const recommendedFeatures = featureCategories
      .flatMap(category => category.features)
      .filter(feature => feature.recommended)
      .map(feature => feature.key);
    
    onFeatureChange(recommendedFeatures);
  };

  const selectAll = () => {
    const allFeatures = featureCategories
      .flatMap(category => category.features)
      .map(feature => feature.key);
    
    onFeatureChange(allFeatures);
  };

  const clearAll = () => {
    onFeatureChange([]);
  };

  return (
    <div className="space-y-4">
      {/* クイック選択ボタン */}
      <div className="flex flex-wrap gap-2 mb-6">
        <button
          onClick={selectRecommended}
          className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200 transition-colors"
        >
          推奨特徴量を選択
        </button>
        <button
          onClick={selectAll}
          className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
        >
          すべて選択
        </button>
        <button
          onClick={clearAll}
          className="px-3 py-1 text-sm bg-red-100 text-red-700 rounded-md hover:bg-red-200 transition-colors"
        >
          すべてクリア
        </button>
      </div>

      {/* カテゴリ別特徴量 */}
      {featureCategories.map(category => (
        <div key={category.id} className="border border-gray-200 rounded-lg">
          <button
            onClick={() => toggleCategory(category.id)}
            className="w-full flex items-center justify-between p-4 text-left hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-center space-x-3">
              {expandedCategories.includes(category.id) ? (
                <ChevronDown className="h-4 w-4 text-gray-500" />
              ) : (
                <ChevronRight className="h-4 w-4 text-gray-500" />
              )}
              <div>
                <h3 className="font-medium text-gray-900">{category.name}</h3>
                <p className="text-sm text-gray-600">{category.description}</p>
              </div>
            </div>
            <HelpTooltip content={`${category.name}の特徴量について：\n${category.description}\n\n各特徴量の詳細は展開してご確認ください。`} />
          </button>
          
          {expandedCategories.includes(category.id) && (
            <div className="px-4 pb-4 border-t border-gray-100">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-4">
                {category.features.map(feature => (
                  <label key={feature.key} className="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors">
                    <input
                      type="checkbox"
                      checked={selectedFeatures.includes(feature.key)}
                      onChange={(e) => handleFeatureToggle(feature.key, e.target.checked)}
                      className="mt-1 rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2">
                        <span className="text-sm font-medium text-gray-900">{feature.label}</span>
                        {feature.recommended && (
                          <span className="px-2 py-0.5 text-xs bg-green-100 text-green-800 rounded-full">
                            推奨
                          </span>
                        )}
                        <HelpTooltip content={feature.description} />
                      </div>
                      <p className="text-xs text-gray-600 mt-1">{feature.description}</p>
                    </div>
                  </label>
                ))}
              </div>
            </div>
          )}
        </div>
      ))}

      {/* 選択状況のサマリー */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-sm font-medium text-blue-900">選択された特徴量</h4>
            <p className="text-sm text-blue-700">
              {selectedFeatures.length}個の特徴量が選択されています
            </p>
          </div>
          <div className="text-sm text-blue-600">
            {selectedFeatures.length > 0 ? (
              <span className="font-medium">
                推奨: {featureCategories
                  .flatMap(c => c.features)
                  .filter(f => f.recommended && selectedFeatures.includes(f.key))
                  .length}個
              </span>
            ) : (
              <span className="text-gray-500">特徴量を選択してください</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
