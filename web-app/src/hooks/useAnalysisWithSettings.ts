"use client";

import { useState } from "react";
import { useSettings } from "@/contexts/SettingsContext";

export interface AnalysisOptions {
  symbols?: string[];
  analysisType?: string;
  useSettings?: boolean;
}

export function useAnalysisWithSettings() {
  const { settings } = useSettings();
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [analysisStatus, setAnalysisStatus] = useState("");

  const runAnalysisWithSettings = async (options: AnalysisOptions = {}) => {
    try {
      setIsAnalyzing(true);
      setAnalysisProgress(0);
      setAnalysisStatus("設定に基づく分析を開始しています...");

      // 設定に基づく分析パラメータを構築
      const analysisParams = {
        prediction_days: settings.prediction.days,
        primary_model: settings.model.primary_model,
        compare_models: settings.model.compare_models,
        auto_retrain: settings.model.auto_retrain,
        retrain_frequency: settings.model.retrain_frequency,
        max_data_points: settings.data.max_data_points,
        include_technical_indicators: settings.data.include_technical_indicators,
        selected_features: settings.features.selected,
        symbols: options.symbols || [],
        analysis_type: options.analysisType || "comprehensive",
        use_settings: options.useSettings !== false, // デフォルトでtrue
      };

      // プログレスバーのシミュレーション
      const progressInterval = setInterval(() => {
        setAnalysisProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return prev;
          }
          return prev + Math.random() * 10;
        });
      }, 500);

      setAnalysisStatus("分析パラメータを送信中...");
      setAnalysisProgress(10);

      // クライアントサイドでの分析シミュレーション
      // 実際の分析は静的サイトでは実行できないため、シミュレーション
      await new Promise(resolve => setTimeout(resolve, 1000));

      setAnalysisStatus("分析を実行中...");
      setAnalysisProgress(50);

      // シミュレーション用の結果を生成
      const result = {
        success: true,
        analysis_id: `analysis_${Date.now()}`,
        predictions: [
          {
            symbol: "7203.T",
            name: "トヨタ自動車",
            prediction: "BUY",
            confidence: 0.85,
            price: 2500,
            change: 2.5,
          },
          {
            symbol: "6758.T",
            name: "ソニーグループ", 
            prediction: "SELL",
            confidence: 0.72,
            price: 12000,
            change: -1.8,
          },
        ],
        summary: {
          total_predictions: 2,
          buy_signals: 1,
          sell_signals: 1,
          avg_confidence: 0.785,
        },
      };
      
      setAnalysisStatus("分析が完了しました。データを更新しています...");
      setAnalysisProgress(100);

      return {
        success: true,
        result,
        settings: analysisParams,
      };

    } catch (error) {
      console.error("分析実行エラー:", error);
      setAnalysisStatus(`分析エラー: ${error instanceof Error ? error.message : "不明なエラー"}`);
      return {
        success: false,
        error: error instanceof Error ? error.message : "不明なエラー",
      };
    } finally {
      setIsAnalyzing(false);
      setTimeout(() => {
        setAnalysisProgress(0);
        setAnalysisStatus("");
      }, 2000);
    }
  };

  const getAnalysisDescription = () => {
    const modelText = settings.model.compare_models 
      ? `複数モデル比較（メイン: ${settings.model.primary_model}）`
      : `単一モデル（${settings.model.primary_model}）`;
    
    const retrainText = settings.model.auto_retrain 
      ? `自動再訓練（${settings.model.retrain_frequency}）`
      : "手動再訓練";
    
    return {
      prediction: `${settings.prediction.days}日先予測`,
      model: modelText,
      retrain: retrainText,
      features: `${settings.features.selected.length}個の特徴量`,
      data: `${settings.data.max_data_points}データポイント`,
    };
  };

  return {
    runAnalysisWithSettings,
    isAnalyzing,
    analysisProgress,
    analysisStatus,
    getAnalysisDescription,
  };
}
