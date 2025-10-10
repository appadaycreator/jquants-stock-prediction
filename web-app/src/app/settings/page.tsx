"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import Navigation from "@/components/Navigation";
import { Settings, Save, RefreshCw, Database, Cpu, BarChart, Play, AlertCircle, CheckCircle, BookOpen, Bell, Shield, Upload, Download, Eye, AlertTriangle, HelpCircle } from "lucide-react";
import { useAnalysisWithSettings } from "@/hooks/useAnalysisWithSettings";
import { useSettings } from "@/contexts/SettingsContext";
import AutoUpdateSettings from "@/components/notification/AutoUpdateSettings";
import HelpTooltip, { default as Tooltip } from "@/components/Tooltip";
import FeatureCategories from "@/components/FeatureCategories";
import ModelComparison from "@/components/ModelComparison";
import ValidationInput, { validationPresets } from "@/components/ValidationInput";
import ThemeToggle from "@/components/ThemeToggle";

export default function SettingsPage() {
  const { settings, updateSettings, saveSettings, resetSettings, isLoading, isSaving } = useSettings();
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState<"success" | "error" | "">("");
  const [riskSettings, setRiskSettings] = useState<any | null>(null);
  const [riskLoading, setRiskLoading] = useState(false);
  const [riskSaving, setRiskSaving] = useState(false);
  const [configPreview, setConfigPreview] = useState<string>("");
  const [validationResult, setValidationResult] = useState<any | null>(null);
  const [isValidating, setIsValidating] = useState(false);

  // 設定連携フック
  const { 
    runAnalysisWithSettings, 
    isAnalyzing, 
    analysisProgress, 
    analysisStatus,
    getAnalysisDescription, 
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

  // Config export
  const exportConfig = async () => {
    try {
      const res = await fetch("/api/config/export", { cache: "no-store" });
      const json = await res.json();
      if (!json?.ok) throw new Error("エクスポート失敗");

      // JSONファイルとしてダウンロード
      const blob = new Blob([JSON.stringify(json, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "config_export.json";
      a.click();
      URL.revokeObjectURL(url);
      showMessage("設定をエクスポートしました", "success");
    } catch (e) {
      console.error(e);
      showMessage("エクスポートに失敗しました", "error");
    }
  };

  // Config import (with validate before save)
  const importConfigFile = async (file: File) => {
    const text = await file.text();
    // プレビュー用に保持
    setConfigPreview(text);
    try {
      const parsed = JSON.parse(text);
      const res = await fetch("/api/config/import", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(parsed),
      });
      const json = await res.json();
      if (!res.ok || !json?.ok) {
        setValidationResult(json?.validation || null);
        showMessage("インポート検証に失敗しました（保存されていません）", "error");
        return;
      }
      setValidationResult(json.validation);
      showMessage("インポートと保存が完了しました", "success");
    } catch (e) {
      console.error(e);
      showMessage("インポートに失敗しました（ファイル形式を確認）", "error");
    }
  };

  const validateCurrentConfig = async () => {
    try {
      setIsValidating(true);
      const res = await fetch("/api/config/validate", { method: "GET", cache: "no-store" });
      const json = await res.json();
      setValidationResult(json?.result || null);
      if (json?.result?.summary?.is_valid) {
        showMessage("検証成功：エラーはありません", "success");
      } else {
        showMessage("検証完了：修正が必要です", "error");
      }
    } catch (e) {
      console.error(e);
      showMessage("検証に失敗しました", "error");
    } finally {
      setIsValidating(false);
    }
  };

  const loadRiskSettings = async () => {
    try {
      setRiskLoading(true);
      const res = await fetch("/api/risk-settings", { cache: "no-store" });
      
      if (!res.ok) {
        if (res.status === 404) {
          console.warn("リスク設定APIが見つかりません。デフォルト設定を使用します。");
        } else {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
      } else {
        const json = await res.json();
        setRiskSettings(json);
        return; // 成功した場合はここで終了
      }
    } catch (e) {
      console.error("リスク設定読み込みエラー:", e);
      // エラーが発生した場合はデフォルト設定を使用
      setRiskSettings({
        riskTolerance: "medium",
        maxLossPercentage: 5,
        stopLossPercentage: 3,
        takeProfitPercentage: 10,
        maxPositionSize: 10,
        diversificationLevel: "medium",
        rebalanceFrequency: "monthly",
        volatilityThreshold: 0.2,
        correlationThreshold: 0.7,
        sectorLimits: {
          technology: 30,
          healthcare: 20,
          finance: 15,
          consumer: 15,
          industrial: 10,
          utilities: 5,
          energy: 5,
        },
        countryLimits: {
          japan: 60,
          usa: 25,
          europe: 10,
          asia: 5,
        },
        assetAllocation: {
          stocks: 70,
          bonds: 20,
          cash: 10,
        },
        riskMetrics: {
          maxDrawdown: 15,
          sharpeRatio: 1.0,
          volatility: 0.15,
        },
        notifications: {
          priceAlerts: true,
          riskAlerts: true,
          rebalanceAlerts: true,
          newsAlerts: false,
        },
        advanced: {
          useOptions: false,
          useLeverage: false,
          useShortSelling: false,
          useDerivatives: false,
        },
      });
    } finally {
      setRiskLoading(false);
    }
  };

  useEffect(() => {
    loadRiskSettings();
  }, []);

  const saveRiskSettings = async () => {
    try {
      setRiskSaving(true);
      const maxp = riskSettings?.maxLoss?.max_loss_percent;
      if (typeof maxp === "number" && (maxp <= 0 || maxp > 0.5)) {
        showMessage("最大損失率は 0 < p <= 0.5 で指定してください", "error");
        return;
      }
      
      const resp = await fetch("/api/risk-settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(riskSettings),
      });
      
      if (!resp.ok) {
        if (resp.status === 404) {
          showMessage("リスク設定APIが見つかりません。設定は保存されませんでした。", "error");
          return;
        }
        const errorData = await resp.json().catch(() => ({}));
        const errText = errorData?.error || `HTTP error! status: ${resp.status}`;
        showMessage(errText, "error");
        return;
      }
      
      const json = await resp.json();
      if (json?.success === false) {
        const errText = json?.error || "保存に失敗しました";
        showMessage(errText, "error");
        return;
      }
      
      setRiskSettings(json.settings || json);
      showMessage("リスク設定を保存し即時適用しました", "success");
    } catch (e) {
      console.error("リスク設定保存エラー:", e);
      showMessage("リスク設定の保存に失敗しました", "error");
    } finally {
      setRiskSaving(false);
    }
  };

  const updateRisk = (path: string, value: any) => {
    setRiskSettings((prev: any) => {
      const base = prev ? { ...prev } : {};
      const keys = path.split(".");
      let cur: any = base;
      for (let i = 0; i < keys.length - 1; i++) {
        cur[keys[i]] = cur[keys[i]] ?? {};
        cur = cur[keys[i]];
      }
      cur[keys[keys.length - 1]] = value;
      return base;
    });
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
        analysisType: "comprehensive",
        useSettings: true,
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
              <ThemeToggle />
              <button
                onClick={runAnalysis}
                disabled={isAnalyzing}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 disabled:opacity-50"
                aria-label="設定に基づいて分析を実行"
                data-help="現在の設定内容で分析を実行します。"
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
                aria-label="設定をリセット"
                data-help="設定を初期状態に戻します。"
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                リセット
              </button>
              <button
                onClick={handleSave}
                disabled={isSaving}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
                aria-label="設定を保存"
                data-help="現在の設定を保存します。"
              >
                <Save className="h-4 w-4 mr-2" />
                {isSaving ? "保存中..." : "保存"}
              </button>
              <button
                onClick={exportConfig}
                className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                aria-label="設定をエクスポート"
                data-help="設定をJSONとしてダウンロードします。"
              >
                <Download className="h-4 w-4 mr-2" />
                エクスポート
              </button>
              <label className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 cursor-pointer">
                <Upload className="h-4 w-4 mr-2" />
                インポート
                <input type="file" accept="application/json" className="hidden" onChange={(e) => {
                  const f = e.target.files?.[0];
                  if (f) importConfigFile(f);
                }} />
              </label>
              <button
                onClick={validateCurrentConfig}
                disabled={isValidating}
                className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
                aria-label="設定を検証"
                data-help="現在の設定の妥当性をチェックします。"
              >
                <Eye className="h-4 w-4 mr-2" />
                {isValidating ? "検証中..." : "検証"}
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
            {/* 設定プレビュー/検証結果 */}
            {(configPreview || validationResult) && (
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center mb-4">
                  <Settings className="h-6 w-6 text-gray-600 mr-3" />
                  <h2 className="text-xl font-bold text-gray-900">設定プレビュー / 検証結果</h2>
                </div>
                {configPreview && (
                  <div className="mb-4">
                    <p className="text-sm text-gray-600 mb-2">インポートファイルの内容（JSON）</p>
                    <pre className="p-3 bg-gray-50 rounded overflow-auto text-xs max-h-64 whitespace-pre-wrap">{configPreview}</pre>
                  </div>
                )}
                {validationResult && (
                  <div>
                    <p className="text-sm text-gray-600 mb-2">検証結果サマリー</p>
                    <div className="text-sm grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div>Issues: <span className="font-semibold">{validationResult?.summary?.total_issues ?? "-"}</span></div>
                      <div>Errors: <span className="font-semibold text-red-600">{validationResult?.summary?.errors ?? "-"}</span></div>
                      <div>Warnings: <span className="font-semibold text-yellow-600">{validationResult?.summary?.warnings ?? "-"}</span></div>
                      <div>Valid: <span className="font-semibold {validationResult?.summary?.is_valid ? 'text-green-600' : 'text-red-600'}">{String(validationResult?.summary?.is_valid)}</span></div>
                    </div>
                    <div className="mt-3">
                      <p className="text-sm text-gray-600 mb-2">詳細</p>
                      <div className="max-h-64 overflow-auto text-xs">
                        <ul className="list-disc list-inside space-y-1">
                          {(validationResult?.results || []).map((r: any, idx: number) => (
                            <li key={idx} className={r.level === "error" || r.level === "critical" ? "text-red-700" : r.level === "warning" ? "text-yellow-700" : "text-gray-700"}>
                              [{r.level}] {r.section}.{r.key}: {r.message}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
            
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
              <Tooltip content="予測設定では、分析の期間と使用するモデルを設定できます。\n\n予測期間：将来何日先まで予測するかを設定\n使用モデル：どの機械学習モデルを使用するかを選択">
                <HelpCircle className="h-4 w-4 text-gray-400 hover:text-gray-600 transition-colors" />
              </Tooltip>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <ValidationInput
                type="number"
                value={settings.prediction.days}
                onChange={(value) => updateSettings({
                  prediction: { ...settings.prediction, days: value },
                })}
                label="予測期間（日数）"
                description="将来何日先まで予測するか"
                validation={validationPresets.predictionDays}
                recommendedValue={30}
                placeholder="30"
              />
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  使用するモデル
                  <HelpTooltip content="使用する機械学習モデルを選択します。\n\n・すべてのモデル：複数のモデルを比較して最適な結果を選択\n・個別モデル：特定のモデルのみを使用" />
                </label>
                <select 
                  value={settings.model.type}
                  onChange={(e) => updateSettings({
                    model: { ...settings.model, type: e.target.value },
                  })}
                  className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                >
                  <option value="all">すべてのモデル（推奨）</option>
                  <option value="linear">線形回帰</option>
                  <option value="random_forest">ランダムフォレスト</option>
                  <option value="xgboost">XGBoost</option>
                </select>
                <p className="text-xs text-gray-500 mt-1">
                  推奨：すべてのモデルを選択すると、最適な結果が自動選択されます
                </p>
              </div>
            </div>
          </div>

          {/* 特徴量設定 */}
          <div id="features" className="bg-white rounded-lg shadow p-8">
            <div className="flex items-center mb-6">
              <Database className="h-6 w-6 text-green-600 mr-3" />
              <h2 className="text-2xl font-bold text-gray-900">特徴量設定</h2>
              <HelpTooltip content="特徴量設定では、分析に使用する技術指標を選択できます。\n\n特徴量は予測精度に大きく影響するため、推奨設定を使用することをお勧めします。\n各特徴量の詳細は展開してご確認ください。" />
            </div>
            
            <FeatureCategories
              selectedFeatures={settings.features.selected}
              onFeatureChange={(features) => updateSettings({
                features: { ...settings.features, selected: features },
              })}
            />
          </div>

          {/* モデル設定 */}
          <div id="model" className="bg-white rounded-lg shadow p-8">
            <div className="flex items-center mb-6">
              <Cpu className="h-6 w-6 text-blue-600 mr-3" />
              <h2 className="text-2xl font-bold text-gray-900">モデル設定</h2>
              <HelpTooltip content="モデル設定では、機械学習モデルの選択と動作を設定できます。\n\n初心者の方は「自動モデル比較」を有効にすることをお勧めします。\nこれにより、最適なモデルが自動的に選択されます。" />
            </div>
            
            <ModelComparison
              selectedModel={settings.model.primary_model}
              onModelChange={(model) => updateSettings({
                model: { ...settings.model, primary_model: model },
              })}
              compareModels={settings.model.compare_models}
              onCompareChange={(compare) => updateSettings({
                model: { ...settings.model, compare_models: compare },
              })}
            />
            
            <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  再訓練頻度
                  <HelpTooltip content="モデルの再訓練頻度を設定します。\n\n・毎日：最新データで毎日モデルを更新（高精度だが計算負荷大）\n・毎週：週1回モデルを更新（バランス型）\n・毎月：月1回モデルを更新（計算負荷軽）\n・手動：手動で再訓練を実行" />
                </label>
                <select 
                  value={settings.model.retrain_frequency}
                  onChange={(e) => updateSettings({
                    model: { ...settings.model, retrain_frequency: e.target.value },
                  })}
                  className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                >
                  <option value="daily">毎日（高精度）</option>
                  <option value="weekly">毎週（推奨）</option>
                  <option value="monthly">毎月（軽量）</option>
                  <option value="manual">手動</option>
                </select>
                <p className="text-xs text-gray-500 mt-1">
                  推奨：毎週（バランスの取れた設定）
                </p>
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
                  <HelpTooltip content="自動再訓練を有効にすると、設定した頻度でモデルが自動的に更新されます。\n\nメリット：\n・常に最新データで学習されたモデルを使用\n・予測精度の向上\n\n注意：\n・再訓練中は一時的に分析機能が制限される場合があります" />
                </div>
                <div className="ml-6 text-xs text-gray-500">
                  <p>• 設定した頻度でモデルを自動的に再訓練します</p>
                  <p>• 新しいデータに基づいてモデルの精度を向上させます</p>
                  <p>• 再訓練はバックグラウンドで実行され、完了時に通知されます</p>
                </div>
              </div>
            </div>
          </div>

          {/* ハイパーパラメータ設定（上級者向け） */}
          <div id="hyperparameters" className="bg-white rounded-lg shadow p-8">
            <div className="flex items-center mb-6">
              <Cpu className="h-6 w-6 text-purple-600 mr-3" />
              <h2 className="text-2xl font-bold text-gray-900">ハイパーパラメータ設定</h2>
              <span className="ml-3 px-2 py-1 text-xs bg-purple-100 text-purple-800 rounded-full">上級者向け</span>
            </div>
            
            <div className="mb-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <div className="flex items-start">
                <AlertTriangle className="h-5 w-5 text-yellow-600 mr-2 mt-0.5" />
                <div>
                  <h4 className="text-sm font-medium text-yellow-800">注意事項</h4>
                  <p className="text-sm text-yellow-700 mt-1">
                    ハイパーパラメータの変更はモデルの性能に大きく影響します。不適切な設定は予測精度の低下を招く可能性があります。
                    変更前には必ずバックアップを取ることを推奨します。
                  </p>
                </div>
              </div>
            </div>

            <div className="space-y-8">
              {/* XGBoost設定 */}
              <div className="border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">XGBoost</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      n_estimators
                    </label>
                    <input
                      type="number"
                      min="10"
                      max="1000"
                      step="10"
                      value={settings.hyperparameters?.xgboost?.n_estimators || 100}
                      onChange={(e) => updateSettings({
                        hyperparameters: {
                          ...settings.hyperparameters,
                          xgboost: {
                            learning_rate: 0.1,
                            max_depth: 6,
                            subsample: 0.8,
                            colsample_bytree: 0.8,
                            reg_alpha: 0.1,
                            ...settings.hyperparameters?.xgboost,
                            n_estimators: parseInt(e.target.value),
                          },
                        },
                      })}
                      className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">ブースティングラウンド数 (10-1000)</p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      learning_rate
                    </label>
                    <input
                      type="number"
                      min="0.01"
                      max="1.0"
                      step="0.01"
                      value={settings.hyperparameters?.xgboost?.learning_rate || 0.1}
                      onChange={(e) => updateSettings({
                        hyperparameters: {
                          ...settings.hyperparameters,
                          xgboost: {
                            n_estimators: 100,
                            max_depth: 6,
                            subsample: 0.8,
                            colsample_bytree: 0.8,
                            reg_alpha: 0.1,
                            ...settings.hyperparameters?.xgboost,
                            learning_rate: parseFloat(e.target.value),
                          },
                        },
                      })}
                      className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">学習率 (0.01-1.0)</p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      max_depth
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="20"
                      step="1"
                      value={settings.hyperparameters?.xgboost?.max_depth || 6}
                      onChange={(e) => updateSettings({
                        hyperparameters: {
                          ...settings.hyperparameters,
                          xgboost: {
                            n_estimators: 100,
                            learning_rate: 0.1,
                            subsample: 0.8,
                            colsample_bytree: 0.8,
                            reg_alpha: 0.1,
                            ...settings.hyperparameters?.xgboost,
                            max_depth: parseInt(e.target.value),
                          },
                        },
                      })}
                      className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">木の最大深度 (1-20)</p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      subsample
                    </label>
                    <input
                      type="number"
                      min="0.1"
                      max="1.0"
                      step="0.1"
                      value={settings.hyperparameters?.xgboost?.subsample || 1.0}
                      onChange={(e) => updateSettings({
                        hyperparameters: {
                          ...settings.hyperparameters,
                          xgboost: {
                            n_estimators: 100,
                            learning_rate: 0.1,
                            max_depth: 6,
                            colsample_bytree: 0.8,
                            reg_alpha: 0.1,
                            ...settings.hyperparameters?.xgboost,
                            subsample: parseFloat(e.target.value),
                          },
                        },
                      })}
                      className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">サンプリング比率 (0.1-1.0)</p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      colsample_bytree
                    </label>
                    <input
                      type="number"
                      min="0.1"
                      max="1.0"
                      step="0.1"
                      value={settings.hyperparameters?.xgboost?.colsample_bytree || 1.0}
                      onChange={(e) => updateSettings({
                        hyperparameters: {
                          ...settings.hyperparameters,
                          xgboost: {
                            n_estimators: 100,
                            learning_rate: 0.1,
                            max_depth: 6,
                            subsample: 0.8,
                            reg_alpha: 0.1,
                            ...settings.hyperparameters?.xgboost,
                            colsample_bytree: parseFloat(e.target.value),
                          },
                        },
                      })}
                      className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">特徴量サンプリング比率 (0.1-1.0)</p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      reg_alpha
                    </label>
                    <input
                      type="number"
                      min="0"
                      max="10"
                      step="0.1"
                      value={settings.hyperparameters?.xgboost?.reg_alpha || 0}
                      onChange={(e) => updateSettings({
                        hyperparameters: {
                          ...settings.hyperparameters,
                          xgboost: {
                            n_estimators: 100,
                            learning_rate: 0.1,
                            max_depth: 6,
                            subsample: 0.8,
                            colsample_bytree: 0.8,
                            ...settings.hyperparameters?.xgboost,
                            reg_alpha: parseFloat(e.target.value),
                          },
                        },
                      })}
                      className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">L1正則化 (0-10)</p>
                  </div>
                </div>
              </div>

              {/* Random Forest設定 */}
              <div className="border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Random Forest</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      n_estimators
                    </label>
                    <input
                      type="number"
                      min="10"
                      max="500"
                      step="10"
                      value={settings.hyperparameters?.random_forest?.n_estimators || 100}
                      onChange={(e) => updateSettings({
                        hyperparameters: {
                          ...settings.hyperparameters,
                          random_forest: {
                            max_depth: 10,
                            min_samples_split: 2,
                            min_samples_leaf: 1,
                            max_features: "sqrt",
                            bootstrap: true,
                            ...settings.hyperparameters?.random_forest,
                            n_estimators: parseInt(e.target.value),
                          },
                        },
                      })}
                      className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">決定木の数 (10-500)</p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      max_depth
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="50"
                      step="1"
                      value={settings.hyperparameters?.random_forest?.max_depth || 10}
                      onChange={(e) => updateSettings({
                        hyperparameters: {
                          ...settings.hyperparameters,
                          random_forest: {
                            n_estimators: 100,
                            min_samples_split: 2,
                            min_samples_leaf: 1,
                            max_features: "sqrt",
                            bootstrap: true,
                            ...settings.hyperparameters?.random_forest,
                            max_depth: parseInt(e.target.value),
                          },
                        },
                      })}
                      className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">木の最大深度 (1-50)</p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      min_samples_split
                    </label>
                    <input
                      type="number"
                      min="2"
                      max="20"
                      step="1"
                      value={settings.hyperparameters?.random_forest?.min_samples_split || 2}
                      onChange={(e) => updateSettings({
                        hyperparameters: {
                          ...settings.hyperparameters,
                          random_forest: {
                            n_estimators: 100,
                            max_depth: 10,
                            min_samples_leaf: 1,
                            max_features: "sqrt",
                            bootstrap: true,
                            ...settings.hyperparameters?.random_forest,
                            min_samples_split: parseInt(e.target.value),
                          },
                        },
                      })}
                      className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">分割に必要な最小サンプル数 (2-20)</p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      min_samples_leaf
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="10"
                      step="1"
                      value={settings.hyperparameters?.random_forest?.min_samples_leaf || 1}
                      onChange={(e) => updateSettings({
                        hyperparameters: {
                          ...settings.hyperparameters,
                          random_forest: {
                            n_estimators: 100,
                            max_depth: 10,
                            min_samples_split: 2,
                            max_features: "sqrt",
                            bootstrap: true,
                            ...settings.hyperparameters?.random_forest,
                            min_samples_leaf: parseInt(e.target.value),
                          },
                        },
                      })}
                      className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">葉ノードの最小サンプル数 (1-10)</p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      max_features
                    </label>
                    <select
                      value={settings.hyperparameters?.random_forest?.max_features || "sqrt"}
                      onChange={(e) => updateSettings({
                        hyperparameters: {
                          ...settings.hyperparameters,
                          random_forest: {
                            n_estimators: 100,
                            max_depth: 10,
                            min_samples_split: 2,
                            min_samples_leaf: 1,
                            bootstrap: true,
                            ...settings.hyperparameters?.random_forest,
                            max_features: e.target.value,
                          },
                        },
                      })}
                      className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    >
                      <option value="sqrt">sqrt</option>
                      <option value="log2">log2</option>
                      <option value="auto">auto</option>
                    </select>
                    <p className="text-xs text-gray-500 mt-1">各分割で考慮する特徴量数</p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      bootstrap
                    </label>
                    <select
                      value={settings.hyperparameters?.random_forest?.bootstrap ? "true" : "false"}
                      onChange={(e) => updateSettings({
                        hyperparameters: {
                          ...settings.hyperparameters,
                          random_forest: {
                            n_estimators: 100,
                            max_depth: 10,
                            min_samples_split: 2,
                            min_samples_leaf: 1,
                            max_features: "sqrt",
                            ...settings.hyperparameters?.random_forest,
                            bootstrap: e.target.value === "true",
                          },
                        },
                      })}
                      className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    >
                      <option value="true">True</option>
                      <option value="false">False</option>
                    </select>
                    <p className="text-xs text-gray-500 mt-1">ブートストラップサンプリング</p>
                  </div>
                </div>
              </div>

              {/* 線形回帰設定 */}
              <div className="border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">線形回帰・Ridge回帰</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Ridge alpha
                    </label>
                    <input
                      type="number"
                      min="0.001"
                      max="100"
                      step="0.001"
                      value={settings.hyperparameters?.ridge?.alpha || 1.0}
                      onChange={(e) => updateSettings({
                        hyperparameters: {
                          ...settings.hyperparameters,
                          ridge: {
                            fit_intercept: true,
                            normalize: false,
                            ...settings.hyperparameters?.ridge,
                            alpha: parseFloat(e.target.value),
                          },
                        },
                      })}
                      className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">正則化強度 (0.001-100)</p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      fit_intercept
                    </label>
                    <select
                      value={settings.hyperparameters?.ridge?.fit_intercept ? "true" : "false"}
                      onChange={(e) => updateSettings({
                        hyperparameters: {
                          ...settings.hyperparameters,
                          ridge: {
                            alpha: 1.0,
                            normalize: false,
                            ...settings.hyperparameters?.ridge,
                            fit_intercept: e.target.value === "true",
                          },
                        },
                      })}
                      className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    >
                      <option value="true">True</option>
                      <option value="false">False</option>
                    </select>
                    <p className="text-xs text-gray-500 mt-1">切片項の計算</p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      normalize
                    </label>
                    <select
                      value={settings.hyperparameters?.ridge?.normalize ? "true" : "false"}
                      onChange={(e) => updateSettings({
                        hyperparameters: {
                          ...settings.hyperparameters,
                          ridge: {
                            alpha: 1.0,
                            fit_intercept: true,
                            ...settings.hyperparameters?.ridge,
                            normalize: e.target.value === "true",
                          },
                        },
                      })}
                      className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    >
                      <option value="true">True</option>
                      <option value="false">False</option>
                    </select>
                    <p className="text-xs text-gray-500 mt-1">特徴量の正規化</p>
                  </div>
                </div>
              </div>

              {/* 設定のリセット */}
              <div className="flex justify-between items-center pt-4 border-t border-gray-200">
                <div>
                  <h4 className="text-sm font-medium text-gray-900">ハイパーパラメータのリセット</h4>
                  <p className="text-sm text-gray-500">デフォルト値に戻します</p>
                </div>
                <button
                  onClick={() => {
                    updateSettings({
                      hyperparameters: {
                        xgboost: {
                          n_estimators: 100,
                          learning_rate: 0.1,
                          max_depth: 6,
                          subsample: 1.0,
                          colsample_bytree: 1.0,
                          reg_alpha: 0,
                        },
                        random_forest: {
                          n_estimators: 100,
                          max_depth: 10,
                          min_samples_split: 2,
                          min_samples_leaf: 1,
                          max_features: "sqrt",
                          bootstrap: true,
                        },
                        ridge: {
                          alpha: 1.0,
                          fit_intercept: true,
                          normalize: false,
                        },
                      },
                    });
                  }}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  デフォルトに戻す
                </button>
              </div>
            </div>
          </div>

          {/* データ設定 */}
          <div id="data" className="bg-white rounded-lg shadow p-8">
            <div className="flex items-center mb-6">
              <Database className="h-6 w-6 text-green-600 mr-3" />
              <h2 className="text-2xl font-bold text-gray-900">データ設定</h2>
              <HelpTooltip content="データ設定では、データの取得頻度と処理方法を設定できます。\n\nデータ更新間隔：どの頻度でデータを取得するか\n最大データポイント数：分析に使用するデータの量\n技術指標：計算済みの技術指標を含めるかどうか" />
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  データ更新間隔
                  <HelpTooltip content="データの取得頻度を設定します。\n\n・リアルタイム：常に最新データを取得（高負荷）\n・1時間ごと：1時間に1回データを更新（推奨）\n・毎日：1日1回データを更新（軽量）\n・毎週：1週間に1回データを更新（軽量）" />
                </label>
                <select 
                  value={settings.data.refresh_interval}
                  onChange={(e) => updateSettings({
                    data: { ...settings.data, refresh_interval: e.target.value },
                  })}
                  className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                >
                  <option value="realtime">リアルタイム（高負荷）</option>
                  <option value="hourly">1時間ごと（推奨）</option>
                  <option value="daily">毎日（軽量）</option>
                  <option value="weekly">毎週（軽量）</option>
                </select>
                <p className="text-xs text-gray-500 mt-1">
                  推奨：1時間ごと（バランスの取れた設定）
                </p>
              </div>
              
              <ValidationInput
                type="number"
                value={settings.data.max_data_points}
                onChange={(value) => updateSettings({
                  data: { ...settings.data, max_data_points: value },
                })}
                label="最大データポイント数"
                description="分析に使用するデータの量"
                validation={validationPresets.maxDataPoints}
                recommendedValue={1000}
                placeholder="1000"
              />
              
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
                <HelpTooltip content="技術指標（RSI、MACD、ボリンジャーバンドなど）を事前計算して含めます。\n\nメリット：\n・分析の高速化\n・一貫した指標計算\n\nデメリット：\n・ストレージ使用量の増加\n・初期計算時間の増加" />
              </div>
            </div>
          </div>

          {/* UI設定 */}
          <div id="ui" className="bg-white rounded-lg shadow p-8">
            <div className="flex items-center mb-6">
              <BarChart className="h-6 w-6 text-purple-600 mr-3" />
              <h2 className="text-2xl font-bold text-gray-900">UI設定</h2>
              <HelpTooltip content="UI設定では、画面の表示と動作を設定できます。\n\nテーマ：画面の色合いを選択\n更新間隔：データの自動更新頻度\nツールチップ：ヘルプ情報の表示" />
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  テーマ
                  <HelpTooltip content="画面の色合いを選択します。\n\n・ライト：明るい色合い（推奨）\n・ダーク：暗い色合い\n・自動：システム設定に従う" />
                </label>
                <div className="flex items-center space-x-4">
                  <div className="flex-1">
                    <select 
                      value={settings.ui.theme}
                      onChange={(e) => updateSettings({
                        ui: { ...settings.ui, theme: e.target.value },
                      })}
                      className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    >
                      <option value="light">ライト（推奨）</option>
                      <option value="dark">ダーク</option>
                      <option value="auto">自動</option>
                    </select>
                    <p className="text-xs text-gray-500 mt-1">
                      推奨：ライト（視認性が良い）
                    </p>
                  </div>
                  <div className="flex-shrink-0">
                    <ThemeToggle />
                  </div>
                </div>
              </div>
              
              <ValidationInput
                type="number"
                value={settings.ui.refresh_rate}
                onChange={(value) => updateSettings({
                  ui: { ...settings.ui, refresh_rate: value },
                })}
                label="更新間隔（秒）"
                description="データの自動更新頻度"
                validation={validationPresets.refreshRate}
                recommendedValue={30}
                placeholder="30"
              />
              
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
                <HelpTooltip content="ツールチップ（ヘルプ情報）の表示を制御します。\n\n有効：各項目にマウスを合わせると説明が表示されます\n無効：ツールチップは表示されません" />
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
          {/* リスク設定（即時反映） */}
          <div id="risk" className="bg-white rounded-lg shadow p-8">
            <div className="flex items-center mb-6">
              <Shield className="h-6 w-6 text-red-600 mr-3" />
              <h2 className="text-2xl font-bold text-gray-900">リスク管理設定</h2>
            </div>
            {riskLoading ? (
              <div className="text-gray-500">読み込み中...</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700">リスク管理 全体ON/OFF</span>
                    <input type="checkbox" checked={!!riskSettings?.enabled} onChange={(e) => updateRisk("enabled", e.target.checked)} />
                  </div>
                  <div className="mt-4 p-4 border rounded space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-700">最大損失管理を有効化</span>
                      <input type="checkbox" checked={!!riskSettings?.maxLoss?.enabled} onChange={(e) => updateRisk("maxLoss.enabled", e.target.checked)} />
                    </div>
                    <label className="block text-sm text-gray-600">
                      最大損失率（小数, 0.05=5%）
                      <input className="mt-1 w-full border rounded p-2" type="number" step="0.005" min="0.005" max="0.5" value={riskSettings?.maxLoss?.max_loss_percent ?? 0.05} onChange={(e) => updateRisk("maxLoss.max_loss_percent", parseFloat(e.target.value))} />
                    </label>
                    <label className="block text-sm text-gray-600">
                      自動損切り閾値（小数, 0.08=8%）
                      <input className="mt-1 w-full border rounded p-2" type="number" step="0.005" min="0.01" max="0.9" value={riskSettings?.maxLoss?.auto_stop_loss_threshold ?? 0.08} onChange={(e) => updateRisk("maxLoss.auto_stop_loss_threshold", parseFloat(e.target.value))} />
                    </label>
                  </div>
                </div>
                <div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700">ボラティリティ調整を有効化</span>
                    <input type="checkbox" checked={!!riskSettings?.volatility?.enabled} onChange={(e) => updateRisk("volatility.enabled", e.target.checked)} />
                  </div>
                  <div className="mt-4 grid grid-cols-2 gap-4">
                    <label className="text-sm text-gray-600">高ボラ閾値（年率）
                      <input className="mt-1 w-full border rounded p-2" type="number" step="0.05" min="0.05" max="2" value={riskSettings?.volatility?.high_vol_threshold ?? 0.4} onChange={(e) => updateRisk("volatility.high_vol_threshold", parseFloat(e.target.value))} />
                    </label>
                    <label className="text-sm text-gray-600">極端ボラ閾値（年率）
                      <input className="mt-1 w-full border rounded p-2" type="number" step="0.05" min="0.05" max="2" value={riskSettings?.volatility?.extreme_vol_threshold ?? 0.6} onChange={(e) => updateRisk("volatility.extreme_vol_threshold", parseFloat(e.target.value))} />
                    </label>
                    <label className="text-sm text-gray-600">高ボラ縮小係数
                      <input className="mt-1 w-full border rounded p-2" type="number" step="0.05" min="0.1" max="1.5" value={riskSettings?.volatility?.high_vol_multiplier ?? 0.7} onChange={(e) => updateRisk("volatility.high_vol_multiplier", parseFloat(e.target.value))} />
                    </label>
                    <label className="text-sm text-gray-600">極端ボラ縮小係数
                      <input className="mt-1 w-full border rounded p-2" type="number" step="0.05" min="0.1" max="1.5" value={riskSettings?.volatility?.extreme_vol_multiplier ?? 0.4} onChange={(e) => updateRisk("volatility.extreme_vol_multiplier", parseFloat(e.target.value))} />
                    </label>
                  </div>
                  <div className="mt-3">
                    <label className="inline-flex items-center space-x-2">
                      <input type="checkbox" checked={!!riskSettings?.enforcement?.block_violation_signals} onChange={(e) => updateRisk("enforcement.block_violation_signals", e.target.checked)} />
                      <span className="text-sm">リスク違反提案をブロック（売買提案/執行に反映）</span>
                    </label>
                  </div>
                </div>
              </div>
            )}
            <div className="mt-6 flex gap-3">
              <button onClick={saveRiskSettings} disabled={riskSaving} className={`px-4 py-2 rounded ${riskSaving ? "bg-gray-400" : "bg-blue-600 hover:bg-blue-700"} text-white`}>
                {riskSaving ? "保存中..." : "リスク設定を保存して即時適用"}
              </button>
              <button onClick={loadRiskSettings} className="px-4 py-2 rounded bg-gray-100 hover:bg-gray-200">再読込</button>
            </div>
          </div>

        </div>
      </main>
    </div>
  );
}
