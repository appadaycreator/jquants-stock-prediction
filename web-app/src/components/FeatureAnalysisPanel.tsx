"use client";

import { useState } from "react";
import { X, Info, TrendingUp, TrendingDown, BarChart3, Target, Lightbulb, BookOpen } from "lucide-react";
import { FEATURE_IMPORTANCE_GUIDE } from "@/data/modelDefinitions";

interface FeatureAnalysisPanelProps {
  isOpen: boolean;
  onClose: () => void;
  featureAnalysis: Array<{
    feature: string;
    importance: number;
    percentage: number;
  }>;
}

export default function FeatureAnalysisPanel({ 
  isOpen, 
  onClose, 
  featureAnalysis, 
}: FeatureAnalysisPanelProps) {
  const [activeTab, setActiveTab] = useState<"interpretation" | "guide" | "tips">("interpretation");

  if (!isOpen) return null;

  const getFeatureIcon = (feature: string) => {
    if (feature.includes("価格") || feature.includes("変動")) return <TrendingUp className="h-4 w-4 text-blue-600" />;
    if (feature.includes("ボリューム") || feature.includes("出来高")) return <BarChart3 className="h-4 w-4 text-green-600" />;
    if (feature.includes("RSI")) return <Target className="h-4 w-4 text-purple-600" />;
    if (feature.includes("移動平均") || feature.includes("SMA")) return <TrendingUp className="h-4 w-4 text-orange-600" />;
    if (feature.includes("ボリンジャー")) return <BarChart3 className="h-4 w-4 text-red-600" />;
    if (feature.includes("MACD")) return <TrendingDown className="h-4 w-4 text-indigo-600" />;
    return <Info className="h-4 w-4 text-gray-600" />;
  };

  const getImportanceLevel = (importance: number) => {
    if (importance >= 0.3) return { level: "高", color: "text-red-600 bg-red-100" };
    if (importance >= 0.15) return { level: "中", color: "text-yellow-600 bg-yellow-100" };
    return { level: "低", color: "text-green-600 bg-green-100" };
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Lightbulb className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900">特徴量重要度の解釈</h2>
                <p className="text-gray-600">各特徴量が株価予測にどの程度影響するかを解説します</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          {/* タブナビゲーション */}
          <div className="flex space-x-1 mb-6 bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setActiveTab("interpretation")}
              className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === "interpretation"
                  ? "bg-white text-blue-600 shadow-sm"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              特徴量解釈
            </button>
            <button
              onClick={() => setActiveTab("guide")}
              className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === "guide"
                  ? "bg-white text-blue-600 shadow-sm"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              読み方ガイド
            </button>
            <button
              onClick={() => setActiveTab("tips")}
              className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === "tips"
                  ? "bg-white text-blue-600 shadow-sm"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              投資のヒント
            </button>
          </div>

          {/* タブコンテンツ */}
          {activeTab === "interpretation" && (
            <div className="space-y-6">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-blue-900 mb-2">現在の特徴量重要度</h3>
                <p className="text-blue-800 text-sm">
                  以下の特徴量が株価予測にどの程度影響するかを示しています。重要度が高いほど、その指標の変化が予測に大きく影響します。
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {featureAnalysis.map((feature, index) => {
                  const importanceInfo = getImportanceLevel(feature.importance);
                  return (
                    <div key={index} className="bg-white border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center space-x-2">
                          {getFeatureIcon(feature.feature)}
                          <span className="font-medium text-gray-900">{feature.feature}</span>
                        </div>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${importanceInfo.color}`}>
                          重要度: {importanceInfo.level}
                        </span>
                      </div>
                      
                      <div className="mb-3">
                        <div className="flex justify-between text-sm text-gray-600 mb-1">
                          <span>重要度</span>
                          <span>{(feature.importance * 100).toFixed(1)}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${Math.min(100, feature.percentage || feature.importance * 100)}%` }}
                          ></div>
                        </div>
                      </div>

                      <div className="text-sm text-gray-600">
                        {(() => {
                          const guide = FEATURE_IMPORTANCE_GUIDE.interpretation.find(
                            item => item.feature === feature.feature,
                          );
                          return guide ? (
                            <div>
                              <p className="font-medium text-gray-900 mb-1">意味:</p>
                              <p className="mb-2">{guide.meaning}</p>
                              <p className="font-medium text-gray-900 mb-1">投資への応用:</p>
                              <p>{guide.investment_implication}</p>
                            </div>
                          ) : (
                            <p>この特徴量の詳細な解釈は準備中です。</p>
                          );
                        })()}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {activeTab === "guide" && (
            <div className="space-y-6">
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-green-900 mb-2">特徴量重要度の読み方</h3>
                <p className="text-green-800 text-sm">
                  {FEATURE_IMPORTANCE_GUIDE.description}
                </p>
              </div>

              <div className="space-y-4">
                {FEATURE_IMPORTANCE_GUIDE.interpretation.map((item, index) => (
                  <div key={index} className="bg-white border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center space-x-2 mb-2">
                      {getFeatureIcon(item.feature)}
                      <h4 className="font-semibold text-gray-900">{item.feature}</h4>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        item.importance === "高" ? "bg-red-100 text-red-800" :
                        item.importance === "中" ? "bg-yellow-100 text-yellow-800" :
                        "bg-green-100 text-green-800"
                      }`}>
                        {item.importance}
                      </span>
                    </div>
                    <div className="space-y-2 text-sm text-gray-700">
                      <div>
                        <span className="font-medium">意味:</span> {item.meaning}
                      </div>
                      <div>
                        <span className="font-medium">投資への応用:</span> {item.investment_implication}
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <h4 className="font-semibold text-yellow-900 mb-2">重要なポイント</h4>
                <ul className="text-yellow-800 text-sm space-y-1">
                  {FEATURE_IMPORTANCE_GUIDE.tips.map((tip, index) => (
                    <li key={index} className="flex items-start space-x-2">
                      <span className="text-yellow-600 mt-0.5">•</span>
                      <span>{tip}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          {activeTab === "tips" && (
            <div className="space-y-6">
              <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-purple-900 mb-2">投資判断への活用方法</h3>
                <p className="text-purple-800 text-sm">
                  特徴量重要度を理解することで、より効果的な投資判断ができます。
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-3 flex items-center space-x-2">
                    <TrendingUp className="h-5 w-5 text-green-600" />
                    <span>高重要度特徴量の活用</span>
                  </h4>
                  <ul className="text-sm text-gray-700 space-y-2">
                    <li>• 価格変動率が高い場合：トレンドフォロー戦略を検討</li>
                    <li>• ボリュームが重要：出来高の変化に注目して売買判断</li>
                    <li>• 複数指標の組み合わせで精度向上</li>
                  </ul>
                </div>

                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-3 flex items-center space-x-2">
                    <Target className="h-5 w-5 text-blue-600" />
                    <span>中重要度特徴量の活用</span>
                  </h4>
                  <ul className="text-sm text-gray-700 space-y-2">
                    <li>• RSI：オーバーボート・オーバーソールドの判断</li>
                    <li>• 移動平均：トレンドの方向性確認</li>
                    <li>• ボリンジャーバンド：ボラティリティの変化に注目</li>
                  </ul>
                </div>

                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-3 flex items-center space-x-2">
                    <BarChart3 className="h-5 w-5 text-orange-600" />
                    <span>特徴量の組み合わせ</span>
                  </h4>
                  <ul className="text-sm text-gray-700 space-y-2">
                    <li>• 複数の特徴量を総合的に評価</li>
                    <li>• 市場環境に応じて重要度は変化</li>
                    <li>• 定期的な見直しと調整が重要</li>
                  </ul>
                </div>

                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-3 flex items-center space-x-2">
                    <BookOpen className="h-5 w-5 text-indigo-600" />
                    <span>注意点</span>
                  </h4>
                  <ul className="text-sm text-gray-700 space-y-2">
                    <li>• 過去のデータに基づく指標のため、将来を保証しない</li>
                    <li>• 市場の急変時は重要度が変化する可能性</li>
                    <li>• 他の要因（ニュース、経済指標等）も考慮</li>
                  </ul>
                </div>
              </div>
            </div>
          )}

          <div className="mt-6 flex justify-end">
            <button
              onClick={onClose}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              閉じる
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
