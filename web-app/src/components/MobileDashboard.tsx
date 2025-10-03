"use client";

import { useState, useEffect } from "react";
import { 
  TrendingUp, 
  TrendingDown, 
  BarChart3, 
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
  Target,
} from "lucide-react";
// import MobileChart from "./MobileChart"; // 一時的に無効化
import { parseToJst } from "@/lib/datetime";

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
  const [lastUpdateTime, setLastUpdateTime] = useState<string | null>(null);
  const [refreshStatus, setRefreshStatus] = useState<string>("");

  const handleRefresh = async () => {
    setIsRefreshing(true);
    setRefreshStatus("データを更新しています...");
    await onRefresh();
    
    // 更新日時を設定
    const now = new Date();
    setLastUpdateTime(now.toLocaleString("ja-JP"));
    setRefreshStatus("更新完了");
    
    setTimeout(() => {
      setIsRefreshing(false);
      setRefreshStatus("");
    }, 2000);
  };

  // 日時文字列を正規化する関数
  const normalizeDateString = (dateStr: string): string => {
    try {
      // 既にYYYY-MM-DD形式の場合はそのまま返す
      if (/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) {
        return dateStr;
      }
      
      // YYYYMMDD形式をYYYY-MM-DD形式に変換
      if (/^\d{8}$/.test(dateStr)) {
        return dateStr.replace(/(\d{4})(\d{2})(\d{2})/, "$1-$2-$3");
      }
      
      // その他の形式の場合はDateオブジェクトで解析
      const date = new Date(dateStr);
      if (isNaN(date.getTime())) {
        console.error("Invalid date format:", dateStr);
        return "2024-01-01"; // デフォルト日付
      }
      
      return date.toISOString().split("T")[0];
    } catch (error) {
      console.error("Date normalization error:", error, "Input:", dateStr);
      return "2024-01-01"; // デフォルト日付
    }
  };

  const formatDate = (dateStr: string) => {
    try {
      // Luxonを使用して日付を正規化
      const dt = parseToJst(dateStr);
      
      if (!dt.isValid) {
        console.error("Invalid date format:", dateStr);
        return "2024-01-01"; // デフォルト日付を返す
      }
      
      return dt.toLocaleString({
        month: "short",
        day: "numeric",
      });
    } catch (error) {
      console.error("Date formatting error:", error, "Input:", dateStr);
      return "2024-01-01"; // デフォルト日付を返す
    }
  };

  const chartData = stockData.map(item => ({
    date: formatDate(normalizeDateString(item.date)),
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
                title={isRefreshing ? "更新中..." : "データを更新"}
              >
                <RefreshCw className={`h-4 w-4 ${isRefreshing ? "animate-spin" : ""}`} />
              </button>
              <button
                onClick={onAnalysis}
                className="p-2 rounded-lg bg-purple-600 text-white hover:bg-purple-700 transition-colors"
                title="分析を実行"
              >
                <Play className="h-4 w-4" />
              </button>
              <button
                onClick={onSettings}
                className="p-2 rounded-lg bg-gray-600 text-white hover:bg-gray-700 transition-colors"
                title="設定を開く"
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
            <div className="text-right">
              <span className="text-gray-500">
                最終更新: {lastUpdateTime || summary?.last_updated || "-"}
              </span>
              {refreshStatus && (
                <div className="text-green-600 font-medium">
                  {refreshStatus}
                </div>
              )}
            </div>
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

            {/* 株価チャート - 一時的に無効化 */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">株価推移と移動平均</h3>
              <p className="text-gray-600">チャート機能は一時的に無効化されています。</p>
            </div>
          </>
        )}

        {activeTab === "predictions" && (
          <>
            {/* 予測結果チャート - 一時的に無効化 */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">予測 vs 実際値</h3>
              <p className="text-gray-600">チャート機能は一時的に無効化されています。</p>
            </div>

            {/* 予測精度分布 - 一時的に無効化 */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">予測誤差分布</h3>
              <p className="text-gray-600">チャート機能は一時的に無効化されています。</p>
            </div>
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

            {/* モデル性能チャート - 一時的に無効化 */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">MAE比較</h3>
              <p className="text-gray-600">チャート機能は一時的に無効化されています。</p>
            </div>
          </>
        )}

        {activeTab === "analysis" && (
          <>
            {/* 特徴量重要度 - 一時的に無効化 */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">特徴量重要度</h3>
              <p className="text-gray-600">チャート機能は一時的に無効化されています。</p>
            </div>

            {/* 特徴量重要度分布 - 一時的に無効化 */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">特徴量重要度分布</h3>
              <p className="text-gray-600">チャート機能は一時的に無効化されています。</p>
            </div>

            {/* 散布図 - 一時的に無効化 */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">実際値 vs 予測値散布図</h3>
              <p className="text-gray-600">チャート機能は一時的に無効化されています。</p>
            </div>
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
