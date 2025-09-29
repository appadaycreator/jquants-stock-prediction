"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import Navigation from "@/components/Navigation";
import { Settings, Save, RefreshCw, Database, Cpu, BarChart, Play, AlertCircle, CheckCircle, BookOpen, Bell } from "lucide-react";
import { useAnalysisWithSettings } from "@/hooks/useAnalysisWithSettings";
import { useSettings } from "@/contexts/SettingsContext";
import AutoUpdateSettings from "@/components/notification/AutoUpdateSettings";

export default function SettingsPage() {
  const { settings, updateSettings, saveSettings, resetSettings, isLoading, isSaving } = useSettings();
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState<"success" | "error" | "">("");

  // 設定連携フック
  const { 
    runAnalysisWithSettings, 
    isAnalyzing, 
    analysisProgress, 
    analysisStatus,
    getAnalysisDescription 
  } = useAnalysisWithSettings();

  // useEffectは不要（SettingsContextで自動的に読み込まれる）

  const showMessage = (text: string, type: "success" | "error") => {
    setMessage(text);
    setMessageType(type);
    setTimeout(() => {
      setMessage("");
      setMessageType("");
    }, 3000);
  };

  const handleSave = async () => {
    try {
      await saveSettings();
      showMessage("設定が正常に保存されました", "success");
    } catch (error) {
      console.error("設定保存エラー:", error);
      showMessage("設定の保存に失敗しました", "error");
    }
  };

  const handleReset = () => {
    if (confirm("設定をリセットしますか？")) {
      resetSettings();
      showMessage("設定がリセットされました", "success");
    }
  };

  const runAnalysis = async () => {
    try {
      showMessage("設定に基づく分析を実行しています...", "success");
      
      // 設定連携版の分析実行
      const result = await runAnalysisWithSettings({
        analysisType: 'comprehensive',
        useSettings: true
      });

      if (result.success) {
        showMessage("分析が完了しました", "success");
      } else {
        showMessage(`分析エラー: ${result.error}`, "error");
      }
    } catch (error) {
      console.error("分析実行エラー:", error);
      showMessage("分析の実行に失敗しました", "error");
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">設定を読み込み中...</p>
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
              <h1 className="text-3xl font-bold text-gray-900">システム設定</h1>
              <p className="text-gray-600">予測システムの動作を設定</p>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={runAnalysis}
                disabled={isAnalyzing}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 disabled:opacity-50"
              >
                {isAnalyzing ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    実行中...
                  </>
                ) : (
                  <>
                    <Play className="h-4 w-4 mr-2" />
                    設定で分析実行
                  </>
                )}
              </button>
              <button
                onClick={handleReset}
                className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                リセット
              </button>
              <button
                onClick={handleSave}
                disabled={isSaving}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
              >
                <Save className="h-4 w-4 mr-2" />
                {isSaving ? "保存中..." : "保存"}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* メッセージ表示 */}
      {message && (
        <div className={`fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg ${
          messageType === "success" ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
        }`}>
          <div className="flex items-center">
            {messageType === "success" ? (
              <CheckCircle className="h-5 w-5 mr-2" />
            ) : (
              <AlertCircle className="h-5 w-5 mr-2" />
            )}
            {message}
          </div>
        </div>
      )}

      {/* メインコンテンツ */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* サイドバー */}
          <div className="w-full lg:w-1/4">
            <nav className="bg-white rounded-lg shadow p-4 sticky top-8">
              <h3 className="text-lg font-medium text-gray-900 mb-4">設定メニュー</h3>
              <div className="space-y-2">
                <a
                  href="#prediction"
                  className="block px-3 py-2 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                >
                  予測設定
                </a>
                <a
                  href="#features"
                  className="block px-3 py-2 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                >
                  特徴量設定
                </a>
                <a
                  href="#model"
                  className="block px-3 py-2 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                >
                  モデル設定
                </a>
                <a
                  href="#data"
                  className="block px-3 py-2 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                >
                  データ設定
                </a>
                <a
                  href="#ui"
                  className="block px-3 py-2 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                >
                  UI設定
                </a>
                <a
                  href="#system"
                  className="block px-3 py-2 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                >
                  システム情報
                </a>
                <a
                  href="#notifications"
                  className="block px-3 py-2 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                >
                  自動更新・通知
                </a>
                
                {/* 使い方リンク */}
                <div className="border-t pt-4 mt-4">
                  <Link
                    href="/usage"
                    className="flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium text-blue-600 hover:bg-blue-50 hover:text-blue-700"
                  >
                    <BookOpen className="h-4 w-4" />
                    <span>使い方ガイド</span>
                  </Link>
                </div>
              </div>
            </nav>
          </div>

          {/* メインコンテンツエリア */}
          <div className="w-full lg:w-3/4">
            <div className="space-y-8">
            
            {/* 現在の設定情報 */}
            <div className="bg-blue-50 rounded-lg shadow p-6">
              <div className="flex items-center mb-4">
                <Settings className="h-6 w-6 text-blue-600 mr-3" />
                <h2 className="text-xl font-bold text-gray-900">現在の設定</h2>
              </div>
              
              {(() => {
                const desc = getAnalysisDescription();
                return (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-gray-600">予測期間:</span>
                        <span className="font-medium">{desc.prediction}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">モデル設定:</span>
                        <span className="font-medium">{desc.model}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">再訓練:</span>
                        <span className="font-medium">{desc.retrain}</span>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-gray-600">特徴量:</span>
                        <span className="font-medium">{desc.features}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">データ量:</span>
                        <span className="font-medium">{desc.data}</span>
                      </div>
                    </div>
                  </div>
                );
              })()}
              
              {isAnalyzing && (
                <div className="mt-4 p-4 bg-white rounded-lg border">
                  <div className="flex items-center mb-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                    <span className="text-sm font-medium text-gray-700">分析実行中...</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${analysisProgress}%` }}
                    ></div>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">{analysisStatus}</p>
                </div>
              )}
            </div>
          {/* 予測設定 */}
          <div id="prediction" className="bg-white rounded-lg shadow p-8">
            <div className="flex items-center mb-6">
              <BarChart className="h-6 w-6 text-purple-600 mr-3" />
              <h2 className="text-2xl font-bold text-gray-900">予測設定</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  予測期間（日数）
                </label>
                <input
                  type="number"
                  value={settings.prediction.days}
                  onChange={(e) => updateSettings({
                    prediction: { ...settings.prediction, days: parseInt(e.target.value) },
                  })}
                  className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  使用するモデル
                </label>
                <select 
                  value={settings.model.type}
                  onChange={(e) => updateSettings({
                    model: { ...settings.model, type: e.target.value },
                  })}
                  className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                >
                  <option value="all">すべてのモデル</option>
                  <option value="linear">線形回帰</option>
                  <option value="random_forest">ランダムフォレスト</option>
                  <option value="xgboost">XGBoost</option>
                </select>
              </div>
            </div>
          </div>

          {/* 特徴量設定 */}
          <div id="features" className="bg-white rounded-lg shadow p-8">
            <div className="flex items-center mb-6">
              <Database className="h-6 w-6 text-green-600 mr-3" />
              <h2 className="text-2xl font-bold text-gray-900">特徴量設定</h2>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {[
                { key: "sma_5", label: "SMA_5" },
                { key: "sma_10", label: "SMA_10" },
                { key: "sma_25", label: "SMA_25" },
                { key: "sma_50", label: "SMA_50" },
                { key: "rsi", label: "RSI" },
                { key: "macd", label: "MACD" },
                { key: "bollinger_upper", label: "ボリンジャー上" },
                { key: "bollinger_lower", label: "ボリンジャー下" },
              ].map(feature => (
                <label key={feature.key} className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.features.selected.includes(feature.key)}
                    onChange={(e) => {
                      const newSelected = e.target.checked
                        ? [...settings.features.selected, feature.key]
                        : settings.features.selected.filter(f => f !== feature.key);
                      updateSettings({
                        features: { ...settings.features, selected: newSelected },
                      });
                    }}
                    className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">{feature.label}</span>
                </label>
              ))}
            </div>
          </div>

          {/* モデル設定 */}
          <div id="model" className="bg-white rounded-lg shadow p-8">
            <div className="flex items-center mb-6">
              <Cpu className="h-6 w-6 text-blue-600 mr-3" />
              <h2 className="text-2xl font-bold text-gray-900">モデル設定</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  プライマリモデル
                </label>
                <select 
                  value={settings.model.primary_model}
                  onChange={(e) => updateSettings({
                    model: { ...settings.model, primary_model: e.target.value },
                  })}
                  className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                >
                  <option value="xgboost">XGBoost</option>
                  <option value="random_forest">Random Forest</option>
                  <option value="linear_regression">線形回帰</option>
                  <option value="ridge">Ridge回帰</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  再訓練頻度
                </label>
                <select 
                  value={settings.model.retrain_frequency}
                  onChange={(e) => updateSettings({
                    model: { ...settings.model, retrain_frequency: e.target.value },
                  })}
                  className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                >
                  <option value="daily">毎日</option>
                  <option value="weekly">毎週</option>
                  <option value="monthly">毎月</option>
                  <option value="manual">手動</option>
                </select>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.model.compare_models}
                    onChange={(e) => updateSettings({
                      model: { ...settings.model, compare_models: e.target.checked },
                    })}
                    className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  />
                  <label className="ml-2 text-sm text-gray-700">
                    モデル比較を有効にする
                  </label>
                </div>
                <div className="ml-6 text-xs text-gray-500">
                  <p>• 複数の機械学習モデル（XGBoost、ランダムフォレスト、線形回帰など）を同時に実行し、性能を比較します</p>
                  <p>• より正確な予測が可能ですが、実行時間が長くなります</p>
                  <p>• 最適なモデルが自動的に選択され、結果に表示されます</p>
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.model.auto_retrain}
                    onChange={(e) => updateSettings({
                      model: { ...settings.model, auto_retrain: e.target.checked },
                    })}
                    className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  />
                  <label className="ml-2 text-sm text-gray-700">
                    自動再訓練を有効にする
                  </label>
                </div>
                <div className="ml-6 text-xs text-gray-500">
                  <p>• 設定した頻度（週次/月次）でモデルを自動的に再訓練します</p>
                  <p>• 新しいデータに基づいてモデルの精度を向上させます</p>
                  <p>• 再訓練はバックグラウンドで実行され、完了時に通知されます</p>
                  <p>• 注意: 再訓練中は一時的に分析機能が制限される場合があります</p>
                </div>
              </div>
            </div>
          </div>

          {/* データ設定 */}
          <div id="data" className="bg-white rounded-lg shadow p-8">
            <div className="flex items-center mb-6">
              <Database className="h-6 w-6 text-green-600 mr-3" />
              <h2 className="text-2xl font-bold text-gray-900">データ設定</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  データ更新間隔
                </label>
                <select 
                  value={settings.data.refresh_interval}
                  onChange={(e) => updateSettings({
                    data: { ...settings.data, refresh_interval: e.target.value },
                  })}
                  className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                >
                  <option value="realtime">リアルタイム</option>
                  <option value="hourly">1時間ごと</option>
                  <option value="daily">毎日</option>
                  <option value="weekly">毎週</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  最大データポイント数
                </label>
                <input
                  type="number"
                  value={settings.data.max_data_points}
                  onChange={(e) => updateSettings({
                    data: { ...settings.data, max_data_points: parseInt(e.target.value) },
                  })}
                  className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                />
              </div>
              
              <div className="flex items-center">
                <input
                  type="checkbox"
                  checked={settings.data.include_technical_indicators}
                  onChange={(e) => updateSettings({
                    data: { ...settings.data, include_technical_indicators: e.target.checked },
                  })}
                  className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                />
                <label className="ml-2 text-sm text-gray-700">
                  技術指標を含める
                </label>
              </div>
            </div>
          </div>

          {/* UI設定 */}
          <div id="ui" className="bg-white rounded-lg shadow p-8">
            <div className="flex items-center mb-6">
              <BarChart className="h-6 w-6 text-purple-600 mr-3" />
              <h2 className="text-2xl font-bold text-gray-900">UI設定</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  テーマ
                </label>
                <select 
                  value={settings.ui.theme}
                  onChange={(e) => updateSettings({
                    ui: { ...settings.ui, theme: e.target.value },
                  })}
                  className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                >
                  <option value="light">ライト</option>
                  <option value="dark">ダーク</option>
                  <option value="auto">自動</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  更新間隔（秒）
                </label>
                <input
                  type="number"
                  value={settings.ui.refresh_rate}
                  onChange={(e) => updateSettings({
                    ui: { ...settings.ui, refresh_rate: parseInt(e.target.value) },
                  })}
                  className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                />
              </div>
              
              <div className="flex items-center">
                <input
                  type="checkbox"
                  checked={settings.ui.show_tooltips}
                  onChange={(e) => updateSettings({
                    ui: { ...settings.ui, show_tooltips: e.target.checked },
                  })}
                  className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                />
                <label className="ml-2 text-sm text-gray-700">
                  ツールチップを表示
                </label>
              </div>
            </div>
          </div>

          {/* 自動更新・通知設定 */}
          <div id="notifications" className="bg-white rounded-lg shadow p-8">
            <div className="flex items-center mb-6">
              <Bell className="h-6 w-6 text-blue-600 mr-3" />
              <h2 className="text-2xl font-bold text-gray-900">自動更新・通知設定</h2>
            </div>
            
            <AutoUpdateSettings />
          </div>

          {/* システム情報 */}
          <div id="system" className="bg-white rounded-lg shadow p-8">
            <div className="flex items-center mb-6">
              <Settings className="h-6 w-6 text-gray-600 mr-3" />
              <h2 className="text-2xl font-bold text-gray-900">システム情報</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <p className="text-sm text-gray-600">バージョン</p>
                <p className="text-lg font-semibold">v1.0.0</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">最終更新</p>
                <p className="text-lg font-semibold">2024-09-27</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">データソース</p>
                <p className="text-lg font-semibold">J-Quants API</p>
              </div>
            </div>
          </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
