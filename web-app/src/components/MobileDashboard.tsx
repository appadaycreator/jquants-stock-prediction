"use client";

import { useState, useEffect } from "react";
import { 
  TrendingUp, 
  TrendingDown, 
  BarChart3, 
  Target, 
  Database, 
  CheckCircle, 
  Play, 
  Settings, 
  RefreshCw, 
  Shield,
  AlertTriangle,
  ArrowUp,
  ArrowDown,
  Minus,
} from "lucide-react";
import MobileChart from "./MobileChart";

interface MobileDashboardProps {
  stockData: any[];
  modelComparison: any[];
  featureAnalysis: any[];
  predictions: any[];
  summary: any;
  onRefresh: () => void;
  onAnalysis: () => void;
  onSettings: () => void;
}

export default function MobileDashboard({
  stockData,
  modelComparison,
  featureAnalysis,
  predictions,
  summary,
  onRefresh,
  onAnalysis,
  onSettings,
}: MobileDashboardProps) {
  const [activeTab, setActiveTab] = useState("overview");
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await onRefresh();
    setTimeout(() => setIsRefreshing(false), 1000);
  };

  const formatDate = (dateStr: string) => {
    try {
      // 日時形式を正規化（YYYY-MM-DD形式に統一）
      const normalizedDate = dateStr.includes('-') ? dateStr : 
        dateStr.replace(/(\d{4})(\d{2})(\d{2})/, '$1-$2-$3');
      
      const date = new Date(normalizedDate);
      
      // 無効な日時の場合はエラーメッセージを表示
      if (isNaN(date.getTime())) {
        console.error('Invalid date format:', dateStr);
        return 'Invalid Date';
      }
      
      return date.toLocaleDateString("ja-JP", {
        month: 'short',
        day: 'numeric',
      });
    } catch (error) {
      console.error('Date formatting error:', error, 'Input:', dateStr);
      return 'Invalid Date';
    }
  };

  const chartData = stockData.map(item => ({
    date: formatDate(item.date),
    実際価格: item.close,
    SMA_5: item.sma_5,
    SMA_10: item.sma_10,
    SMA_25: item.sma_25,
    SMA_50: item.sma_50,
    出来高: item.volume / 1000000,
  }));

  const predictionChartData = predictions.slice(0, 30).map(item => ({
    index: item.index,
    実際値: item.actual,
    予測値: item.predicted,
  }));

  const getTrendIcon = (value: number) => {
    if (value > 0) return <ArrowUp className="h-4 w-4 text-green-500" />;
    if (value < 0) return <ArrowDown className="h-4 w-4 text-red-500" />;
    return <Minus className="h-4 w-4 text-gray-500" />;
  };

  const getTrendColor = (value: number) => {
    if (value > 0) return "text-green-600";
    if (value < 0) return "text-red-600";
    return "text-gray-600";
  };

  return (
    <div className="lg:hidden">
      {/* モバイルヘッダー */}
      <div className="bg-white shadow-sm border-b sticky top-0 z-30">
        <div className="px-4 py-3">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h1 className="text-lg font-bold text-gray-900">J-Quants株価予測</h1>
              <p className="text-xs text-gray-600">機械学習による株価予測システム</p>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={handleRefresh}
                disabled={isRefreshing}
                className="p-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 transition-colors"
              >
                <RefreshCw className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
              </button>
              <button
                onClick={onAnalysis}
                className="p-2 rounded-lg bg-purple-600 text-white hover:bg-purple-700 transition-colors"
              >
                <Play className="h-4 w-4" />
              </button>
              <button
                onClick={onSettings}
                className="p-2 rounded-lg bg-gray-600 text-white hover:bg-gray-700 transition-colors"
              >
                <Settings className="h-4 w-4" />
              </button>
            </div>
          </div>

          {/* システムステータス */}
          <div className="flex items-center justify-between text-xs">
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span className="text-gray-600">システム: 正常稼働中</span>
            </div>
            <span className="text-gray-500">
              最終更新: {summary ? summary.last_updated : "-"}
            </span>
          </div>
        </div>
      </div>

      {/* タブナビゲーション */}
      <div className="bg-white border-b">
        <div className="flex overflow-x-auto">
          {[
            { id: "overview", label: "概要", icon: BarChart3 },
            { id: "predictions", label: "予測", icon: TrendingUp },
            { id: "models", label: "モデル", icon: Target },
            { id: "analysis", label: "分析", icon: Database },
            { id: "risk", label: "リスク", icon: Shield },
          ].map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-1 px-4 py-3 text-sm font-medium whitespace-nowrap border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? "border-blue-500 text-blue-600"
                    : "border-transparent text-gray-500 hover:text-gray-700"
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* メインコンテンツ */}
      <div className="p-4 space-y-4">
        {activeTab === "overview" && (
          <>
            {/* サマリーカード */}
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-white rounded-lg shadow-sm border p-4">
                <div className="flex items-center justify-between mb-2">
                  <TrendingUp className="h-5 w-5 text-blue-600" />
                  <span className="text-xs text-gray-500">最優秀モデル</span>
                </div>
                <p className="text-lg font-bold text-gray-900">
                  {summary?.best_model?.toUpperCase() || "-"}
                </p>
              </div>
              
              <div className="bg-white rounded-lg shadow-sm border p-4">
                <div className="flex items-center justify-between mb-2">
                  <Target className="h-5 w-5 text-green-600" />
                  <span className="text-xs text-gray-500">予測精度</span>
                </div>
                <p className="text-lg font-bold text-gray-900">
                  {summary?.r2 || "-"}
                </p>
              </div>
              
              <div className="bg-white rounded-lg shadow-sm border p-4">
                <div className="flex items-center justify-between mb-2">
                  <BarChart3 className="h-5 w-5 text-yellow-600" />
                  <span className="text-xs text-gray-500">MAE</span>
                </div>
                <p className="text-lg font-bold text-gray-900">
                  {summary?.mae || "-"}
                </p>
              </div>
              
              <div className="bg-white rounded-lg shadow-sm border p-4">
                <div className="flex items-center justify-between mb-2">
                  <Database className="h-5 w-5 text-purple-600" />
                  <span className="text-xs text-gray-500">データ数</span>
                </div>
                <p className="text-lg font-bold text-gray-900">
                  {summary?.total_data_points || "-"}
                </p>
              </div>
            </div>

            {/* 株価チャート */}
            <MobileChart
              data={chartData}
              type="line"
              title="株価推移と移動平均"
              dataKey="実際価格"
              lines={[
                { dataKey: "実際価格", stroke: "#2563eb", strokeWidth: 2 },
                { dataKey: "SMA_5", stroke: "#dc2626", strokeWidth: 1 },
                { dataKey: "SMA_10", stroke: "#059669", strokeWidth: 1 },
                { dataKey: "SMA_25", stroke: "#d97706", strokeWidth: 1 },
                { dataKey: "SMA_50", stroke: "#7c3aed", strokeWidth: 1 },
              ]}
              height={250}
            />
          </>
        )}

        {activeTab === "predictions" && (
          <>
            {/* 予測結果チャート */}
            <MobileChart
              data={predictionChartData}
              type="line"
              title="予測 vs 実際値"
              dataKey="実際値"
              lines={[
                { dataKey: "実際値", stroke: "#2563eb", strokeWidth: 2 },
                { dataKey: "予測値", stroke: "#dc2626", strokeWidth: 2 },
              ]}
              height={250}
            />

            {/* 予測精度分布 */}
            <MobileChart
              data={predictions.slice(0, 20).map(p => ({ 
                index: p.index, 
                誤差: p.error.toFixed(2), 
              }))}
              type="bar"
              title="予測誤差分布"
              dataKey="誤差"
              height={200}
            />
          </>
        )}

        {activeTab === "models" && (
          <>
            {/* モデル比較 */}
            <div className="bg-white rounded-lg shadow-sm border">
              <div className="px-4 py-3 border-b">
                <h3 className="text-lg font-medium text-gray-900">モデル性能比較</h3>
              </div>
              <div className="divide-y divide-gray-200">
                {modelComparison.slice(0, 5).map((model, index) => (
                  <div key={model.name} className="px-4 py-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="flex items-center space-x-2">
                          <span className="text-sm font-medium text-gray-900">
                            {index + 1}
                          </span>
                          {index === 0 && <span className="text-green-600">🏆</span>}
                        </div>
                        <div>
                          <p className="text-sm font-medium text-gray-900">{model.name}</p>
                          <p className="text-xs text-gray-500">{model.type}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium text-gray-900">
                          R²: {model.r2.toFixed(4)}
                        </p>
                        <p className="text-xs text-gray-500">
                          MAE: {model.mae.toFixed(4)}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* モデル性能チャート */}
            <MobileChart
              data={modelComparison}
              type="bar"
              title="MAE比較"
              dataKey="mae"
              height={200}
            />
          </>
        )}

        {activeTab === "analysis" && (
          <>
            {/* 特徴量重要度 */}
            <MobileChart
              data={featureAnalysis}
              type="bar"
              title="特徴量重要度"
              dataKey="percentage"
              height={250}
            />

            {/* 特徴量重要度分布 */}
            <MobileChart
              data={featureAnalysis.map(item => ({ ...item, name: item.feature }))}
              type="pie"
              title="特徴量重要度分布"
              dataKey="percentage"
              height={200}
            />

            {/* 散布図 */}
            <MobileChart
              data={predictions.slice(0, 30)}
              type="scatter"
              title="実際値 vs 予測値散布図"
              dataKey="predicted"
              height={250}
            />
          </>
        )}

        {activeTab === "risk" && (
          <>
            {/* リスク管理カード */}
            <div className="bg-white rounded-lg shadow-sm border p-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">リスク管理</h3>
                <Shield className="h-5 w-5 text-blue-600" />
              </div>
              
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                  <div>
                    <p className="text-sm font-medium text-red-800">リスクレベル</p>
                    <p className="text-lg font-bold text-red-600">HIGH</p>
                  </div>
                  <AlertTriangle className="h-6 w-6 text-red-500" />
                </div>
                
                <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                  <div>
                    <p className="text-sm font-medium text-blue-800">ポートフォリオ価値</p>
                    <p className="text-lg font-bold text-blue-600">¥1,250,000</p>
                  </div>
                  <TrendingUp className="h-6 w-6 text-blue-500" />
                </div>
                
                <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
                  <div>
                    <p className="text-sm font-medium text-yellow-800">最大ドローダウン</p>
                    <p className="text-lg font-bold text-yellow-600">8.5%</p>
                  </div>
                  <TrendingDown className="h-6 w-6 text-yellow-500" />
                </div>
              </div>
            </div>

            {/* 推奨事項 */}
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <div className="flex items-start">
                <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5 mr-3 flex-shrink-0" />
                <div>
                  <h4 className="font-semibold text-yellow-800 mb-2">リスク管理推奨事項</h4>
                  <ul className="text-sm text-yellow-700 space-y-1">
                    <li>• ポートフォリオリスクが高すぎます</li>
                    <li>• ポジションサイズを縮小してください</li>
                    <li>• 損切りラインを設定することを推奨</li>
                  </ul>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
