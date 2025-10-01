"use client";

import { useState } from "react";
import { Cpu, Zap, Target, Clock, CheckCircle, AlertCircle } from "lucide-react";
import HelpTooltip from "./Tooltip";

interface ModelInfo {
  id: string;
  name: string;
  description: string;
  speed: "fast" | "medium" | "slow";
  accuracy: "high" | "medium" | "low";
  useCase: string;
  pros: string[];
  cons: string[];
  recommended: boolean;
}

const models: ModelInfo[] = [
  {
    id: "xgboost",
    name: "XGBoost",
    description: "勾配ブースティングによる高精度な予測モデル",
    speed: "medium",
    accuracy: "high",
    useCase: "高精度な予測が必要な場合",
    pros: ["高い予測精度", "過学習に強い", "特徴量の重要度を分析可能"],
    cons: ["計算時間が長い", "パラメータ調整が複雑"],
    recommended: true
  },
  {
    id: "random_forest",
    name: "Random Forest",
    description: "複数の決定木を組み合わせたアンサンブル学習",
    speed: "fast",
    accuracy: "high",
    useCase: "バランスの取れた性能を求める場合",
    pros: ["高速処理", "過学習に強い", "解釈しやすい"],
    cons: ["大量データではメモリ使用量が多い"],
    recommended: true
  },
  {
    id: "linear_regression",
    name: "線形回帰",
    description: "線形関係を仮定したシンプルな予測モデル",
    speed: "fast",
    accuracy: "medium",
    useCase: "シンプルで高速な予測が必要な場合",
    pros: ["高速処理", "解釈しやすい", "計算リソースが少ない"],
    cons: ["非線形関係を捉えられない", "精度に限界"],
    recommended: false
  },
  {
    id: "ridge",
    name: "Ridge回帰",
    description: "正則化を加えた線形回帰の改良版",
    speed: "fast",
    accuracy: "medium",
    useCase: "過学習を防ぎたい場合",
    pros: ["過学習に強い", "高速処理", "パラメータ調整が簡単"],
    cons: ["線形関係の仮定が必要", "非線形関係を捉えられない"],
    recommended: false
  }
];

interface ModelComparisonProps {
  selectedModel: string;
  onModelChange: (model: string) => void;
  compareModels: boolean;
  onCompareChange: (compare: boolean) => void;
}

export default function ModelComparison({
  selectedModel,
  onModelChange,
  compareModels,
  onCompareChange
}: ModelComparisonProps) {
  const [expandedModel, setExpandedModel] = useState<string | null>(null);

  const getSpeedIcon = (speed: string) => {
    switch (speed) {
      case "fast": return <Zap className="h-4 w-4 text-green-600" />;
      case "medium": return <Clock className="h-4 w-4 text-yellow-600" />;
      case "slow": return <Clock className="h-4 w-4 text-red-600" />;
      default: return <Clock className="h-4 w-4 text-gray-600" />;
    }
  };

  const getAccuracyIcon = (accuracy: string) => {
    switch (accuracy) {
      case "high": return <Target className="h-4 w-4 text-green-600" />;
      case "medium": return <Target className="h-4 w-4 text-yellow-600" />;
      case "low": return <Target className="h-4 w-4 text-red-600" />;
      default: return <Target className="h-4 w-4 text-gray-600" />;
    }
  };

  const getSpeedText = (speed: string) => {
    switch (speed) {
      case "fast": return "高速";
      case "medium": return "中速";
      case "slow": return "低速";
      default: return "不明";
    }
  };

  const getAccuracyText = (accuracy: string) => {
    switch (accuracy) {
      case "high": return "高精度";
      case "medium": return "中精度";
      case "low": return "低精度";
      default: return "不明";
    }
  };

  return (
    <div className="space-y-6">
      {/* 自動比較設定 */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <div className="flex items-start space-x-3">
          <div className="flex-shrink-0">
            <Cpu className="h-6 w-6 text-blue-600" />
          </div>
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-2">
              <h3 className="text-lg font-semibold text-blue-900">自動モデル比較</h3>
              <HelpTooltip content="複数のモデルを同時に実行し、最も性能の良いモデルを自動選択します。初心者におすすめの設定です。" />
            </div>
            <p className="text-sm text-blue-700 mb-4">
              初心者の方は「自動比較」を有効にすることで、最適なモデルが自動的に選択されます。
            </p>
            <label className="flex items-center space-x-3">
              <input
                type="checkbox"
                checked={compareModels}
                onChange={(e) => onCompareChange(e.target.checked)}
                className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
              <span className="text-sm font-medium text-blue-900">
                自動モデル比較を有効にする
              </span>
            </label>
            {compareModels && (
              <div className="mt-3 p-3 bg-blue-100 rounded-lg">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-4 w-4 text-blue-600" />
                  <span className="text-sm text-blue-800">
                    推奨設定が有効になりました。複数のモデルが自動的に比較されます。
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 個別モデル選択（自動比較が無効の場合） */}
      {!compareModels && (
        <div className="space-y-4">
          <div className="flex items-center space-x-2">
            <h3 className="text-lg font-semibold text-gray-900">モデル選択</h3>
            <HelpTooltip content="自動比較を無効にした場合、使用するモデルを手動で選択できます。各モデルの特徴を確認して選択してください。" />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {models.map(model => (
              <div
                key={model.id}
                className={`border rounded-lg p-4 cursor-pointer transition-all ${
                  selectedModel === model.id
                    ? "border-blue-500 bg-blue-50"
                    : "border-gray-200 hover:border-gray-300 hover:bg-gray-50"
                }`}
                onClick={() => onModelChange(model.id)}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <input
                      type="radio"
                      name="model"
                      value={model.id}
                      checked={selectedModel === model.id}
                      onChange={() => onModelChange(model.id)}
                      className="text-blue-600 focus:ring-blue-500"
                    />
                    <h4 className="font-medium text-gray-900">{model.name}</h4>
                    {model.recommended && (
                      <span className="px-2 py-0.5 text-xs bg-green-100 text-green-800 rounded-full">
                        推奨
                      </span>
                    )}
                  </div>
                  <HelpTooltip content={`${model.name}について：\n${model.description}\n\n詳細はクリックして展開してください。`} />
                </div>
                
                <p className="text-sm text-gray-600 mb-3">{model.description}</p>
                
                <div className="flex items-center space-x-4 text-xs text-gray-500">
                  <div className="flex items-center space-x-1">
                    {getSpeedIcon(model.speed)}
                    <span>{getSpeedText(model.speed)}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    {getAccuracyIcon(model.accuracy)}
                    <span>{getAccuracyText(model.accuracy)}</span>
                  </div>
                </div>
                
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setExpandedModel(expandedModel === model.id ? null : model.id);
                  }}
                  className="mt-2 text-xs text-blue-600 hover:text-blue-800"
                >
                  {expandedModel === model.id ? "詳細を閉じる" : "詳細を表示"}
                </button>
                
                {expandedModel === model.id && (
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <div className="space-y-3">
                      <div>
                        <h5 className="text-xs font-medium text-gray-700 mb-1">適用場面</h5>
                        <p className="text-xs text-gray-600">{model.useCase}</p>
                      </div>
                      
                      <div>
                        <h5 className="text-xs font-medium text-gray-700 mb-1">メリット</h5>
                        <ul className="text-xs text-gray-600 space-y-1">
                          {model.pros.map((pro, index) => (
                            <li key={index} className="flex items-start space-x-1">
                              <CheckCircle className="h-3 w-3 text-green-500 mt-0.5 flex-shrink-0" />
                              <span>{pro}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                      
                      <div>
                        <h5 className="text-xs font-medium text-gray-700 mb-1">デメリット</h5>
                        <ul className="text-xs text-gray-600 space-y-1">
                          {model.cons.map((con, index) => (
                            <li key={index} className="flex items-start space-x-1">
                              <AlertCircle className="h-3 w-3 text-red-500 mt-0.5 flex-shrink-0" />
                              <span>{con}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 推奨設定の説明 */}
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <div className="flex items-start space-x-2">
          <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
          <div>
            <h4 className="text-sm font-medium text-green-900">推奨設定</h4>
            <p className="text-sm text-green-700 mt-1">
              {compareModels 
                ? "自動比較が有効です。複数のモデルが実行され、最適な結果が選択されます。"
                : "個別モデル選択では、XGBoostまたはRandom Forestが推奨されます。"
              }
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
