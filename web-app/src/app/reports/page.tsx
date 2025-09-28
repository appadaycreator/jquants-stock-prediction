"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Navigation from "../../components/Navigation";
import { FileText, Download, TrendingUp, BarChart, PieChart, BookOpen } from "lucide-react";

// レポートデータの型定義
interface ReportData {
  executive_summary: {
    period: string
    total_predictions: number
    accuracy: number
    best_model: string
    roi_estimate: number
  }
  model_performance: {
    model_name: string
    metrics: {
      mae: number
      rmse: number
      r2: number
      mape: number
    }
    feature_importance: {
      feature: string
      importance: number
    }[]
  }[]
  market_insights: {
    trend_analysis: string
    volatility_analysis: string
    volume_analysis: string
    recommendation: string
  }
  risk_assessment: {
    risk_level: "Low" | "Medium" | "High"
    factors: string[]
    mitigation: string[]
  }
  evaluation_summary: {
    total_models_evaluated: number
    best_model: string
    evaluation_method: string
    overfitting_detection: string
    recommendations: string[]
  }
}

export default function ReportsPage() {
  const [reportData, setReportData] = useState<ReportData | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState("2024-Q1");

  useEffect(() => {
    generateReport();
  }, [selectedPeriod]); // eslint-disable-line react-hooks/exhaustive-deps

  const generateReport = async () => {
    setLoading(true);
    
    // 模擬レポートデータ生成
    const mockReport: ReportData = {
      executive_summary: {
        period: selectedPeriod,
        total_predictions: 91,
        accuracy: 98.76,
        best_model: "XGBoost",
        roi_estimate: 15.3,
      },
      model_performance: [
        {
          model_name: "XGBoost",
          metrics: {
            mae: 72.49,
            rmse: 100.80,
            r2: 0.9876,
            mape: 2.1,
          },
          feature_importance: [
            { feature: "Close_1d_ago", importance: 47.59 },
            { feature: "SMA_10", importance: 24.72 },
            { feature: "SMA_5", importance: 22.93 },
            { feature: "Close_5d_ago", importance: 1.98 },
          ],
        },
        {
          model_name: "Random Forest",
          metrics: {
            mae: 76.61,
            rmse: 101.76,
            r2: 0.9873,
            mape: 2.4,
          },
          feature_importance: [
            { feature: "Close_1d_ago", importance: 84.09 },
            { feature: "SMA_5", importance: 13.48 },
            { feature: "Close_5d_ago", importance: 1.28 },
            { feature: "SMA_50", importance: 0.55 },
          ],
        },
      ],
      market_insights: {
        trend_analysis: "データ期間中、全体的に上昇トレンドを示しており、特に2024年2月以降に顕著な成長が見られました。",
        volatility_analysis: "ボラティリティは比較的安定しており、標準偏差は約15%で推移しています。",
        volume_analysis: "取引量は平均的な水準を維持しており、特異な急騰や急落は観測されていません。",
        recommendation: "現在の予測モデルは高い精度を示しており、継続的な監視の下での投資判断に活用可能です。",
      },
      risk_assessment: {
        risk_level: "Medium",
        factors: [
          "市場の外的要因（政治・経済情勢）",
          "モデルの過学習リスク",
          "予期しない市場変動",
        ],
        mitigation: [
          "複数モデルによるアンサンブル予測",
          "定期的なモデル再トレーニング",
          "リスク管理指標の監視",
        ],
      },
      evaluation_summary: {
        total_models_evaluated: 6,
        best_model: "XGBoost",
        evaluation_method: "3分割（学習・検証・テスト）+ 5-fold CV",
        overfitting_detection: "実装済み",
        recommendations: [
          "✅ モデル性能は良好です（MAE < 10円）",
          "✅ クロスバリデーション結果は安定しています",
          "⚠️ R²が0.99を超えています。データリークや過学習の可能性があります。"
        ]
      },
    };

    setTimeout(() => {
      setReportData(mockReport);
      setLoading(false);
    }, 1000);
  };

  const exportReport = () => {
    // 実際の実装では、レポートをPDFやExcelとしてエクスポートする機能
    const data = JSON.stringify(reportData, null, 2);
    const blob = new Blob([data], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `stock_prediction_report_${selectedPeriod}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">レポートを生成中...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* ナビゲーション */}
      <Navigation />

      {/* ヘッダー */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">予測レポート</h1>
              <p className="text-gray-600">詳細な分析結果とインサイト</p>
            </div>
            <div className="flex items-center space-x-4">
              <select 
                value={selectedPeriod}
                onChange={(e) => setSelectedPeriod(e.target.value)}
                className="rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              >
                <option value="2024-Q1">2024年 Q1</option>
                <option value="2024-Q2">2024年 Q2</option>
                <option value="2024-Q3">2024年 Q3</option>
              </select>
              <button
                onClick={() => exportReport()}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
              >
                <Download className="h-4 w-4 mr-2" />
                エクスポート
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* メインコンテンツ */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {reportData && (
          <div className="space-y-8">
            {/* エグゼクティブサマリー */}
            <div className="bg-white rounded-lg shadow p-8">
              <div className="flex items-center mb-6">
                <FileText className="h-6 w-6 text-blue-600 mr-3" />
                <h2 className="text-2xl font-bold text-gray-900">エグゼクティブサマリー</h2>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <p className="text-sm text-gray-600">予測総数</p>
                  <p className="text-3xl font-bold text-blue-600">{reportData.executive_summary.total_predictions}</p>
                </div>
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <p className="text-sm text-gray-600">予測精度</p>
                  <p className="text-3xl font-bold text-green-600">{reportData.executive_summary.accuracy}%</p>
                </div>
                <div className="text-center p-4 bg-purple-50 rounded-lg">
                  <p className="text-sm text-gray-600">最優秀モデル</p>
                  <p className="text-xl font-bold text-purple-600">{reportData.executive_summary.best_model}</p>
                </div>
                <div className="text-center p-4 bg-yellow-50 rounded-lg">
                  <p className="text-sm text-gray-600">ROI推定</p>
                  <p className="text-3xl font-bold text-yellow-600">{reportData.executive_summary.roi_estimate}%</p>
                </div>
              </div>
            </div>

            {/* モデルパフォーマンス */}
            <div className="bg-white rounded-lg shadow p-8">
              <div className="flex items-center mb-6">
                <BarChart className="h-6 w-6 text-green-600 mr-3" />
                <h2 className="text-2xl font-bold text-gray-900">モデルパフォーマンス</h2>
              </div>
              
              <div className="space-y-6">
                {reportData.model_performance.map((model, index) => (
                  <div key={index} className="border rounded-lg p-6">
                    <h3 className="text-xl font-semibold text-gray-900 mb-4">{model.model_name}</h3>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                      <div className="text-center">
                        <p className="text-sm text-gray-600">MAE</p>
                        <p className="text-lg font-semibold">{model.metrics.mae.toFixed(2)}</p>
                      </div>
                      <div className="text-center">
                        <p className="text-sm text-gray-600">RMSE</p>
                        <p className="text-lg font-semibold">{model.metrics.rmse.toFixed(2)}</p>
                      </div>
                      <div className="text-center">
                        <p className="text-sm text-gray-600">R²</p>
                        <p className="text-lg font-semibold">{model.metrics.r2.toFixed(4)}</p>
                      </div>
                      <div className="text-center">
                        <p className="text-sm text-gray-600">MAPE</p>
                        <p className="text-lg font-semibold">{model.metrics.mape}%</p>
                      </div>
                    </div>
                    
                    <div>
                      <h4 className="text-lg font-medium text-gray-900 mb-3">特徴量重要度</h4>
                      <div className="space-y-2">
                        {model.feature_importance.map((feature, idx) => (
                          <div key={idx} className="flex items-center">
                            <span className="w-32 text-sm text-gray-600">{feature.feature}</span>
                            <div className="flex-1 bg-gray-200 rounded-full h-2 mx-3">
                              <div 
                                className="bg-blue-600 h-2 rounded-full" 
                                style={{ width: `${feature.importance}%` }}
                              ></div>
                            </div>
                            <span className="text-sm font-medium">{feature.importance.toFixed(1)}%</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 市場インサイト */}
            <div className="bg-white rounded-lg shadow p-8">
              <div className="flex items-center mb-6">
                <TrendingUp className="h-6 w-6 text-yellow-600 mr-3" />
                <h2 className="text-2xl font-bold text-gray-900">市場インサイト</h2>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">トレンド分析</h3>
                  <p className="text-gray-700">{reportData.market_insights.trend_analysis}</p>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">ボラティリティ分析</h3>
                  <p className="text-gray-700">{reportData.market_insights.volatility_analysis}</p>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">出来高分析</h3>
                  <p className="text-gray-700">{reportData.market_insights.volume_analysis}</p>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">推奨事項</h3>
                  <p className="text-gray-700">{reportData.market_insights.recommendation}</p>
                </div>
              </div>
            </div>

            {/* 評価サマリー */}
            <div className="bg-white rounded-lg shadow p-8">
              <div className="flex items-center mb-6">
                <BookOpen className="h-6 w-6 text-blue-600 mr-3" />
                <h2 className="text-2xl font-bold text-gray-900">評価サマリー</h2>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div className="bg-blue-50 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">評価方法</h3>
                    <p className="text-gray-700 mb-2">{reportData.evaluation_summary.evaluation_method}</p>
                    <p className="text-sm text-gray-600">
                      過学習検出: {reportData.evaluation_summary.overfitting_detection}
                    </p>
                  </div>
                  
                  <div className="bg-green-50 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">最良モデル</h3>
                    <p className="text-gray-700">
                      評価した{reportData.evaluation_summary.total_models_evaluated}モデル中、
                      <span className="font-semibold text-green-600">{reportData.evaluation_summary.best_model}</span>
                      が最高性能を示しました。
                    </p>
                  </div>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">推奨事項</h3>
                  <ul className="space-y-2">
                    {reportData.evaluation_summary.recommendations.map((recommendation, index) => (
                      <li key={index} className="flex items-start">
                        <span className="w-2 h-2 bg-blue-500 rounded-full mt-2 mr-3"></span>
                        <span className="text-gray-700">{recommendation}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>

            {/* リスク評価 */}
            <div className="bg-white rounded-lg shadow p-8">
              <div className="flex items-center mb-6">
                <PieChart className="h-6 w-6 text-red-600 mr-3" />
                <h2 className="text-2xl font-bold text-gray-900">リスク評価</h2>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                    reportData.risk_assessment.risk_level === "Low" ? "bg-green-100 text-green-800" :
                    reportData.risk_assessment.risk_level === "Medium" ? "bg-yellow-100 text-yellow-800" :
                    "bg-red-100 text-red-800"
                  }`}>
                    リスクレベル: {reportData.risk_assessment.risk_level}
                  </div>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">リスク要因</h3>
                  <ul className="space-y-2">
                    {reportData.risk_assessment.factors.map((factor, index) => (
                      <li key={index} className="flex items-start">
                        <span className="w-2 h-2 bg-red-500 rounded-full mt-2 mr-3"></span>
                        <span className="text-gray-700">{factor}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">軽減策</h3>
                  <ul className="space-y-2">
                    {reportData.risk_assessment.mitigation.map((measure, index) => (
                      <li key={index} className="flex items-start">
                        <span className="w-2 h-2 bg-green-500 rounded-full mt-2 mr-3"></span>
                        <span className="text-gray-700">{measure}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>

            {/* 免責事項 */}
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-yellow-800 mb-2">免責事項</h3>
              <p className="text-yellow-700 text-sm">
                本レポートの予測結果は過去のデータに基づく統計的分析であり、投資判断の参考情報として提供されています。
                市場には予期しない変動要因が存在するため、実際の投資に際しては十分なリスク管理と専門家への相談をお勧めします。
                当システムは投資アドバイスを提供するものではありません。
              </p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
