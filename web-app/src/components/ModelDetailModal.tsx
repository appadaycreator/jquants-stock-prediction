"use client";

import { useState } from "react";
import { X, CheckCircle, AlertCircle, Clock, Target, Brain, Zap, Shield } from "lucide-react";
import { ModelDefinition } from "@/data/modelDefinitions";

interface ModelDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  model: ModelDefinition | null;
  performanceData?: {
    mae: number;
    rmse: number;
    r2: number;
    rank: number;
  };
}

export default function ModelDetailModal({ 
  isOpen, 
  onClose, 
  model, 
  performanceData 
}: ModelDetailModalProps) {
  if (!isOpen || !model) return null;

  const getPerformanceIcon = (level: string) => {
    switch (level) {
      case "high": return <Target className="h-4 w-4 text-green-600" />;
      case "medium": return <Target className="h-4 w-4 text-yellow-600" />;
      case "low": return <Target className="h-4 w-4 text-red-600" />;
      default: return <Target className="h-4 w-4 text-gray-600" />;
    }
  };

  const getSpeedIcon = (speed: string) => {
    switch (speed) {
      case "fast": return <Zap className="h-4 w-4 text-green-600" />;
      case "medium": return <Clock className="h-4 w-4 text-yellow-600" />;
      case "slow": return <Clock className="h-4 w-4 text-red-600" />;
      default: return <Clock className="h-4 w-4 text-gray-600" />;
    }
  };

  const getInterpretabilityIcon = (level: string) => {
    switch (level) {
      case "high": return <Brain className="h-4 w-4 text-green-600" />;
      case "medium": return <Brain className="h-4 w-4 text-yellow-600" />;
      case "low": return <Brain className="h-4 w-4 text-red-600" />;
      default: return <Brain className="h-4 w-4 text-gray-600" />;
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Brain className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{model.name}</h2>
                <p className="text-gray-600">{model.type}</p>
              </div>
              {model.recommended && (
                <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                  推奨モデル
                </span>
              )}
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 左側: 基本情報 */}
            <div className="space-y-6">
              {/* モデル説明 */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">モデル概要</h3>
                <p className="text-gray-700">{model.description}</p>
              </div>

              {/* 性能特性 */}
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">性能特性</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      {getSpeedIcon(model.performance.speed)}
                      <span className="text-sm font-medium text-gray-700">処理速度</span>
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      model.performance.speed === "fast" ? "bg-green-100 text-green-800" :
                      model.performance.speed === "medium" ? "bg-yellow-100 text-yellow-800" :
                      "bg-red-100 text-red-800"
                    }`}>
                      {model.performance.speed === "fast" ? "高速" :
                       model.performance.speed === "medium" ? "中速" : "低速"}
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      {getPerformanceIcon(model.performance.accuracy)}
                      <span className="text-sm font-medium text-gray-700">予測精度</span>
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      model.performance.accuracy === "high" ? "bg-green-100 text-green-800" :
                      model.performance.accuracy === "medium" ? "bg-yellow-100 text-yellow-800" :
                      "bg-red-100 text-red-800"
                    }`}>
                      {model.performance.accuracy === "high" ? "高精度" :
                       model.performance.accuracy === "medium" ? "中精度" : "低精度"}
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      {getInterpretabilityIcon(model.performance.interpretability)}
                      <span className="text-sm font-medium text-gray-700">解釈性</span>
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      model.performance.interpretability === "high" ? "bg-green-100 text-green-800" :
                      model.performance.interpretability === "medium" ? "bg-yellow-100 text-yellow-800" :
                      "bg-red-100 text-red-800"
                    }`}>
                      {model.performance.interpretability === "high" ? "高" :
                       model.performance.interpretability === "medium" ? "中" : "低"}
                    </span>
                  </div>
                </div>
              </div>

              {/* 適用場面 */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-blue-900 mb-2">適用場面</h3>
                <p className="text-blue-800">{model.useCase}</p>
              </div>
            </div>

            {/* 右側: 詳細情報 */}
            <div className="space-y-6">
              {/* 長所・短所 */}
              <div className="grid grid-cols-1 gap-4">
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex items-center space-x-2 mb-3">
                    <CheckCircle className="h-5 w-5 text-green-600" />
                    <h3 className="text-lg font-semibold text-green-900">長所</h3>
                  </div>
                  <ul className="space-y-2">
                    {model.pros.map((pro, index) => (
                      <li key={index} className="flex items-start space-x-2">
                        <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                        <span className="text-green-800 text-sm">{pro}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <div className="flex items-center space-x-2 mb-3">
                    <AlertCircle className="h-5 w-5 text-red-600" />
                    <h3 className="text-lg font-semibold text-red-900">短所</h3>
                  </div>
                  <ul className="space-y-2">
                    {model.cons.map((con, index) => (
                      <li key={index} className="flex items-start space-x-2">
                        <AlertCircle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                        <span className="text-red-800 text-sm">{con}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* 性能データ（もしあれば） */}
              {performanceData && (
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">実際の性能データ</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600">{performanceData.mae.toFixed(4)}</div>
                      <div className="text-sm text-gray-600">MAE</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">{performanceData.rmse.toFixed(4)}</div>
                      <div className="text-sm text-gray-600">RMSE</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-purple-600">{performanceData.r2.toFixed(4)}</div>
                      <div className="text-sm text-gray-600">R²</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-orange-600">#{performanceData.rank}</div>
                      <div className="text-sm text-gray-600">順位</div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* 推奨事項 */}
          <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex items-start space-x-2">
              <Shield className="h-5 w-5 text-yellow-600 mt-0.5" />
              <div>
                <h4 className="font-semibold text-yellow-900">選択のポイント</h4>
                <ul className="text-sm text-yellow-800 mt-2 space-y-1">
                  <li>• 高精度が必要な場合は{model.performance.accuracy === "high" ? "このモデル" : "XGBoostやRandom Forest"}を推奨</li>
                  <li>• 解釈性が重要な場合は{model.performance.interpretability === "high" ? "このモデル" : "線形回帰やRidge回帰"}を推奨</li>
                  <li>• 高速処理が必要な場合は{model.performance.speed === "fast" ? "このモデル" : "線形回帰"}を推奨</li>
                  <li>• 複数の指標を総合的に評価して最適なモデルを選択してください</li>
                </ul>
              </div>
            </div>
          </div>

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
