"use client";

import { useState, useEffect, ReactNode } from "react";

interface SampleDataProviderProps {
  children: ReactNode;
  fallbackToSample?: boolean;
}

interface SampleData {
  stockData: any[];
  modelComparison: any[];
  featureAnalysis: any[];
  predictions: any[];
  summary: any;
  marketInsights: any;
  riskAssessment: any;
}

export function SampleDataProvider({ children, fallbackToSample = true }: SampleDataProviderProps) {
  const [sampleData, setSampleData] = useState<SampleData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadSampleData = async () => {
      try {
        // サンプルデータの生成
        const generateSampleData = (): SampleData => {
          const now = new Date();
          const dates = Array.from({ length: 30 }, (_, i) => {
            const date = new Date(now.getTime() - (29 - i) * 24 * 60 * 60 * 1000);
            return date.toISOString().split("T")[0];
          });

          const stockData = dates.map((date, index) => ({
            date,
            code: "7203.T",
            open: 2500 + Math.random() * 100 - 50,
            high: 2550 + Math.random() * 50,
            low: 2450 - Math.random() * 50,
            close: 2500 + Math.random() * 100 - 50,
            volume: 1000000 + Math.random() * 500000,
            sma_5: 2500 + Math.random() * 50 - 25,
            sma_10: 2500 + Math.random() * 40 - 20,
            sma_25: 2500 + Math.random() * 30 - 15,
            sma_50: 2500 + Math.random() * 20 - 10,
            rsi_14: 30 + Math.random() * 40,
            macd: Math.random() * 10 - 5,
            macd_signal: Math.random() * 8 - 4,
            macd_hist: Math.random() * 2 - 1,
          }));

          const modelComparison = [
            {
              name: "XGBoost",
              type: "Gradient Boosting",
              mae: 0.0234,
              mse: 0.0008,
              rmse: 0.0283,
              r2: 0.8765,
              rank: 1,
            },
            {
              name: "Random Forest",
              type: "Ensemble",
              mae: 0.0256,
              mse: 0.0009,
              rmse: 0.0300,
              r2: 0.8543,
              rank: 2,
            },
            {
              name: "Linear Regression",
              type: "Linear",
              mae: 0.0345,
              mse: 0.0012,
              rmse: 0.0346,
              r2: 0.7891,
              rank: 3,
            },
          ];

          const featureAnalysis = [
            { feature: "価格変動率", importance: 0.35, percentage: 35 },
            { feature: "ボリューム", importance: 0.25, percentage: 25 },
            { feature: "RSI", importance: 0.15, percentage: 15 },
            { feature: "移動平均", importance: 0.12, percentage: 12 },
            { feature: "ボリンジャーバンド", importance: 0.08, percentage: 8 },
            { feature: "MACD", importance: 0.05, percentage: 5 },
          ];

          const predictions = Array.from({ length: 20 }, (_, i) => ({
            index: i + 1,
            actual: 2500 + Math.random() * 200 - 100,
            predicted: 2500 + Math.random() * 200 - 100,
            error: Math.random() * 10 - 5,
            error_percentage: Math.random() * 5,
          }));

          const summary = {
            total_data_points: stockData.length,
            prediction_period: "30日",
            best_model: "XGBoost",
            mae: "0.0234",
            r2: "0.8765",
            last_updated: now.toISOString(),
          };

          const marketInsights = {
            volatility: "medium",
            trend: "bullish",
            risk_level: "moderate",
            market_sentiment: "positive",
          };

          const riskAssessment = {
            risk_level: "Medium",
            risk_score: 0.65,
            var_95: 0.032,
            max_drawdown: 0.085,
            sharpe_ratio: 1.25,
          };

          return {
            stockData,
            modelComparison,
            featureAnalysis,
            predictions,
            summary,
            marketInsights,
            riskAssessment,
          };
        };

        const data = generateSampleData();
        setSampleData(data);
      } catch (error) {
        console.error("サンプルデータの生成に失敗:", error);
      } finally {
        setIsLoading(false);
      }
    };

    loadSampleData();
  }, []);

  // サンプルデータをコンテキストとして提供
  const contextValue = {
    sampleData,
    isLoading,
    isSampleData: true,
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">サンプルデータを準備中...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="sample-data-provider">
      {children}
    </div>
  );
}

// サンプルデータを取得するためのフック
export function useSampleData() {
  const [sampleData, setSampleData] = useState<SampleData | null>(null);

  useEffect(() => {
    const loadSampleData = async () => {
      try {
        // サンプルデータファイルから読み込みを試行
        const response = await fetch("/data/sample_data.json");
        if (response.ok) {
          const data = await response.json();
          setSampleData(data);
        } else {
          // フォールバック: 動的生成
          const generateSampleData = (): SampleData => {
            const now = new Date();
            const dates = Array.from({ length: 30 }, (_, i) => {
              const date = new Date(now.getTime() - (29 - i) * 24 * 60 * 60 * 1000);
              return date.toISOString().split("T")[0];
            });

            return {
              stockData: dates.map((date, index) => ({
                date,
                code: "7203.T",
                open: 2500 + Math.random() * 100 - 50,
                high: 2550 + Math.random() * 50,
                low: 2450 - Math.random() * 50,
                close: 2500 + Math.random() * 100 - 50,
                volume: 1000000 + Math.random() * 500000,
                sma_5: 2500 + Math.random() * 50 - 25,
                sma_10: 2500 + Math.random() * 40 - 20,
                sma_25: 2500 + Math.random() * 30 - 15,
                sma_50: 2500 + Math.random() * 20 - 10,
                rsi_14: 30 + Math.random() * 40,
                macd: Math.random() * 10 - 5,
                macd_signal: Math.random() * 8 - 4,
                macd_hist: Math.random() * 2 - 1,
              })),
              modelComparison: [
                {
                  name: "XGBoost",
                  type: "Gradient Boosting",
                  mae: 0.0234,
                  mse: 0.0008,
                  rmse: 0.0283,
                  r2: 0.8765,
                  rank: 1,
                },
              ],
              featureAnalysis: [
                { feature: "価格変動率", importance: 0.35, percentage: 35 },
                { feature: "ボリューム", importance: 0.25, percentage: 25 },
              ],
              predictions: Array.from({ length: 20 }, (_, i) => ({
                index: i + 1,
                actual: 2500 + Math.random() * 200 - 100,
                predicted: 2500 + Math.random() * 200 - 100,
                error: Math.random() * 10 - 5,
                error_percentage: Math.random() * 5,
              })),
              summary: {
                total_data_points: 30,
                prediction_period: "30日",
                best_model: "XGBoost",
                mae: "0.0234",
                r2: "0.8765",
                last_updated: now.toISOString(),
              },
              marketInsights: {
                volatility: "medium",
                trend: "bullish",
                risk_level: "moderate",
              },
              riskAssessment: {
                risk_level: "Medium",
                risk_score: 0.65,
              },
            };
          };

          setSampleData(generateSampleData());
        }
      } catch (error) {
        console.error("サンプルデータの読み込みに失敗:", error);
      }
    };

    loadSampleData();
  }, []);

  return sampleData;
}
