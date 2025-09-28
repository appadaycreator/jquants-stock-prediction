/**
 * 予測結果タブのメインコンポーネント
 * エラーハンドリング、スキーマ検証、UI安定化
 */

import React, { useState, useEffect, useCallback } from 'react';
import { fetchJson, fetchMultiple, AppError } from '../lib/fetcher';
import { PredictionResponse, StockData, ModelComparison } from '../lib/schema';
import { parseToJst, jstLabel } from '../lib/datetime';
import { mae, rmse, r2, detectOverfitting, evaluateBaseline, compareModels, timeSeriesSplitEvaluation, walkForwardEvaluation } from '../lib/metrics';
import { fetcherLogger, metricsLogger } from '../lib/logger';
import ErrorPanel from './ErrorPanel';
import { PredictionsViewSkeleton } from './Skeletons/LoadingSkeleton';

interface PredictionsViewProps {
  onError?: (error: Error) => void;
}

interface PredictionData {
  date: string;
  symbol: string;
  y_true: number;
  y_pred: number;
  error: number;
}

interface KpiData {
  mae: number;
  rmse: number;
  r2: number;
  baselineComparison: {
    maeImprovement: number;
    rmseImprovement: number;
    r2Improvement: number;
    isBetter: boolean;
  };
  overfittingRisk: {
    isOverfitting: boolean;
    riskLevel: '低' | '中' | '高';
    message: string;
  };
}

export default function PredictionsView({ onError }: PredictionsViewProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<AppError | null>(null);
  const [predictions, setPredictions] = useState<PredictionData[]>([]);
  const [kpiData, setKpiData] = useState<KpiData | null>(null);
  const [modelInfo, setModelInfo] = useState<{
    name: string;
    generatedAt: string;
  } | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  const [abortController, setAbortController] = useState<AbortController | null>(null);

  const loadPredictionsData = useCallback(async (isRetry = false) => {
    try {
      if (isRetry) {
        setRetryCount(prev => prev + 1);
      }

      setLoading(true);
      setError(null);

      // 前回のリクエストを中断
      if (abortController) {
        abortController.abort();
      }

      const controller = new AbortController();
      setAbortController(controller);

      fetcherLogger.info('予測結果データの読み込みを開始');

      // 複数のデータを並列取得（エラーバウンダリで隔離）
      const data = await fetchMultiple({
        predictions: './data/prediction_results.json',
        stockData: './data/stock_data.json',
        modelComparison: './data/unified_model_comparison.json'
      }, {
        signal: controller.signal,
        timeout: 10000,
        retries: 3
      });

      // スキーマ検証（エラーバウンダリで隔離）
      let predictionData, stockData, modelData;
      
      try {
        predictionData = PredictionResponse.parse(data.predictions);
      } catch (schemaError) {
        throw new AppError(
          `予測データのスキーマ検証に失敗: ${schemaError instanceof Error ? schemaError.message : 'Unknown error'}`,
          'INVALID_PREDICTION_SCHEMA'
        );
      }

      try {
        stockData = (data as any).stockData?.map((item: any) => StockData.parse(item)) || [];
      } catch (schemaError) {
        fetcherLogger.warn('株価データのスキーマ検証に失敗、空配列で継続', schemaError);
        stockData = [];
      }

      try {
        modelData = (data as any).modelComparison?.map((item: any) => ModelComparison.parse(item)) || [];
      } catch (schemaError) {
        fetcherLogger.warn('モデル比較データのスキーマ検証に失敗、空配列で継続', schemaError);
        modelData = [];
      }

      fetcherLogger.info('データの読み込みが完了', {
        predictionsCount: predictionData.data.length,
        stockDataCount: stockData.length,
        modelCount: modelData.length
      });

      // 予測データの変換（エラーバウンダリで隔離）
      let predictionList: PredictionData[];
      try {
        predictionList = predictionData.data.map(item => ({
          date: item.date,
          symbol: item.symbol,
          y_true: item.y_true,
          y_pred: item.y_pred,
          error: Math.abs(item.y_true - item.y_pred)
        }));
      } catch (transformError) {
        throw new AppError(
          `予測データの変換に失敗: ${transformError instanceof Error ? transformError.message : 'Unknown error'}`,
          'PREDICTION_TRANSFORM_ERROR'
        );
      }

      setPredictions(predictionList);

      // モデル情報の設定（エラーバウンダリで隔離）
      try {
        if (predictionData.meta) {
          setModelInfo({
            name: predictionData.meta.model,
            generatedAt: predictionData.meta.generatedAt
          });
        }
      } catch (metaError) {
        fetcherLogger.warn('モデル情報の設定に失敗', metaError);
        setModelInfo(null);
      }

      // KPI計算（エラーバウンダリで隔離）
      let kpi: KpiData;
      try {
        const y_true = predictionList.map(p => p.y_true);
        const y_pred = predictionList.map(p => p.y_pred);

        const maeValue = mae(y_true, y_pred);
        const rmseValue = rmse(y_true, y_pred);
        const r2Value = r2(y_true, y_pred);

        // ベースライン評価
        const baselineMetrics = evaluateBaseline(y_true);
        const baselineComparison = compareModels(
          { mae: maeValue, rmse: rmseValue, r2: r2Value },
          baselineMetrics
        );

        // TimeSeriesSplit評価による過学習検出
        const dates = predictionList.map(p => p.date);
        const X = predictionList.map(p => [p.y_true]); // 簡略化された特徴量
        const y = predictionList.map(p => p.y_true);
        
        const timeSeriesEval = timeSeriesSplitEvaluation(X, y, dates, 5);
        const walkForwardEval = walkForwardEvaluation(X, y, dates, 50, 10);
        
        // 過学習検出（TimeSeriesSplit結果を使用）
        const overfittingRisk = {
          isOverfitting: timeSeriesEval.isOverfitting,
          riskLevel: timeSeriesEval.overfittingRisk.includes('高リスク') ? '高' as const :
                    timeSeriesEval.overfittingRisk.includes('中リスク') ? '中' as const : '低' as const,
          message: timeSeriesEval.overfittingRisk
        };

        kpi = {
          mae: maeValue,
          rmse: rmseValue,
          r2: r2Value,
          baselineComparison,
          overfittingRisk
        };
      } catch (kpiError) {
        fetcherLogger.error('KPI計算に失敗、デフォルト値を設定', kpiError);
        kpi = {
          mae: 0,
          rmse: 0,
          r2: 0,
          baselineComparison: {
            maeImprovement: 0,
            rmseImprovement: 0,
            r2Improvement: 0,
            isBetter: false
          },
          overfittingRisk: {
            isOverfitting: false,
            riskLevel: '低' as const,
            message: '計算エラー'
          }
        };
      }

      setKpiData(kpi);

      metricsLogger.info('KPI計算完了', {
        mae: maeValue,
        rmse: rmseValue,
        r2: r2Value,
        isBetterThanBaseline: baselineComparison.isBetter
      });

      setRetryCount(0);

    } catch (err) {
      const error = err instanceof AppError ? err : new AppError(
        err instanceof Error ? err.message : 'Unknown error',
        'UNKNOWN_ERROR'
      );

      fetcherLogger.error('予測結果データの読み込みに失敗', error);

      setError(error);

      if (onError) {
        onError(error);
      }

      // 自動リトライ（最大3回）
      if (retryCount < 3) {
        fetcherLogger.info(`自動リトライを実行 (${retryCount + 1}/3)`);
        setTimeout(() => {
          loadPredictionsData(true);
        }, 2000 * (retryCount + 1));
      }
    } finally {
      setLoading(false);
    }
  }, [retryCount, abortController, onError]);

  useEffect(() => {
    loadPredictionsData();

    return () => {
      if (abortController) {
        abortController.abort();
      }
    };
  }, []);

  const handleRetry = useCallback(() => {
    setRetryCount(0);
    loadPredictionsData();
  }, [loadPredictionsData]);

  const handleDismissError = useCallback(() => {
    setError(null);
  }, []);

  if (loading) {
    return <PredictionsViewSkeleton />;
  }

  if (error) {
    return (
      <div className="p-6">
        <ErrorPanel
          error={error}
          onRetry={handleRetry}
          onDismiss={handleDismissError}
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">予測結果</h2>
          {modelInfo && (
            <p className="text-sm text-gray-600 mt-1">
              モデル: {modelInfo.name} | 生成日時: {jstLabel(parseToJst(modelInfo.generatedAt))}
            </p>
          )}
        </div>
        <button
          onClick={handleRetry}
          className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          更新
        </button>
      </div>

      {/* KPIカード */}
      {kpiData && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium text-gray-500">MAE</h3>
              <span className="text-2xl font-bold text-blue-600">
                {kpiData.mae.toFixed(2)}
              </span>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              平均絶対誤差
            </p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium text-gray-500">RMSE</h3>
              <span className="text-2xl font-bold text-green-600">
                {kpiData.rmse.toFixed(2)}
              </span>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              二乗平均平方根誤差
            </p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium text-gray-500">R²</h3>
              <span className={`text-2xl font-bold ${
                kpiData.overfittingRisk.riskLevel === '高' ? 'text-red-600' :
                kpiData.overfittingRisk.riskLevel === '中' ? 'text-yellow-600' :
                'text-green-600'
              }`}>
                {kpiData.r2.toFixed(3)}
              </span>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              決定係数
            </p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium text-gray-500">ベースライン</h3>
              <span className={`text-2xl font-bold ${
                kpiData.baselineComparison.isBetter ? 'text-green-600' : 'text-red-600'
              }`}>
                {kpiData.baselineComparison.isBetter ? '改善' : '劣化'}
              </span>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              MAE改善: {kpiData.baselineComparison.maeImprovement.toFixed(1)}%
            </p>
          </div>
        </div>
      )}

      {/* 過学習警告 */}
      {kpiData && kpiData.overfittingRisk.isOverfitting && (
        <div className={`border rounded-lg p-4 ${
          kpiData.overfittingRisk.riskLevel === '高' ? 'bg-red-50 border-red-200' :
          kpiData.overfittingRisk.riskLevel === '中' ? 'bg-yellow-50 border-yellow-200' :
          'bg-orange-50 border-orange-200'
        }`}>
          <div className="flex items-start">
            <svg className={`h-5 w-5 mr-2 mt-0.5 ${
              kpiData.overfittingRisk.riskLevel === '高' ? 'text-red-500' :
              kpiData.overfittingRisk.riskLevel === '中' ? 'text-yellow-500' :
              'text-orange-500'
            }`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <div className="flex-1">
              <h3 className={`text-sm font-medium ${
                kpiData.overfittingRisk.riskLevel === '高' ? 'text-red-800' :
                kpiData.overfittingRisk.riskLevel === '中' ? 'text-yellow-800' :
                'text-orange-800'
              }`}>
                過学習のリスクが検出されました
              </h3>
              <p className={`text-sm mt-1 ${
                kpiData.overfittingRisk.riskLevel === '高' ? 'text-red-700' :
                kpiData.overfittingRisk.riskLevel === '中' ? 'text-yellow-700' :
                'text-orange-700'
              }`}>
                {kpiData.overfittingRisk.message}
              </p>
              <p className="text-xs mt-2 text-gray-600">
                TimeSeriesSplit評価により検出されました。モデルの再学習を検討してください。
              </p>
            </div>
          </div>
        </div>
      )}

      {/* 予測結果テーブル */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">予測結果一覧</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  日付
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  銘柄
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  実際値
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  予測値
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  誤差
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {predictions.slice(0, 20).map((prediction, index) => (
                <tr key={index}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {jstLabel(parseToJst(prediction.date))}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {prediction.symbol}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {prediction.y_true.toFixed(2)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {prediction.y_pred.toFixed(2)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {prediction.error.toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
