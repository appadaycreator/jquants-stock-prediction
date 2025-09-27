"use client";

import { useState } from "react";
import { Play, CheckCircle, AlertCircle, RefreshCw, Settings, BarChart3, TrendingUp, Brain, Zap } from "lucide-react";

interface AnalysisConfig {
  type: 'comprehensive' | 'symbols' | 'trading' | 'sentiment';
  name: string;
  description: string;
  icon: React.ReactNode;
  estimatedTime: string;
}

const analysisConfigs: AnalysisConfig[] = [
  {
    type: 'comprehensive',
    name: '包括的分析',
    description: 'データ取得から予測まで全工程を自動実行',
    icon: <BarChart3 className="w-5 h-5" />,
    estimatedTime: '3-5分'
  },
  {
    type: 'symbols',
    name: '銘柄分析',
    description: '指定銘柄の詳細分析を実行',
    icon: <TrendingUp className="w-5 h-5" />,
    estimatedTime: '2-3分'
  },
  {
    type: 'trading',
    name: 'トレーディング分析',
    description: '統合トレーディングシステムによる分析',
    icon: <Zap className="w-5 h-5" />,
    estimatedTime: '4-6分'
  },
  {
    type: 'sentiment',
    name: '感情分析',
    description: 'ニュース感情分析による予測',
    icon: <Brain className="w-5 h-5" />,
    estimatedTime: '3-4分'
  }
];

interface OneClickAnalysisProps {
  onAnalysisComplete?: (result: any) => void;
  onAnalysisStart?: () => void;
}

export default function OneClickAnalysis({ onAnalysisComplete, onAnalysisStart }: OneClickAnalysisProps) {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [selectedType, setSelectedType] = useState<AnalysisConfig['type']>('comprehensive');
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('');
  const [showConfig, setShowConfig] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [analysisId, setAnalysisId] = useState<string | null>(null);
  const [elapsedTime, setElapsedTime] = useState<string>('00:00');

  const selectedConfig = analysisConfigs.find(config => config.type === selectedType);

  const startAnalysis = async () => {
    try {
      const newAnalysisId = `analysis_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      setAnalysisId(newAnalysisId);
      setIsAnalyzing(true);
      setProgress(0);
      setStatus('分析を開始しています...');
      setError(null);
      setAnalysisResult(null);
      setElapsedTime('00:00');
      
      onAnalysisStart?.();

      // 進捗追跡の開始
      const progressInterval = setInterval(async () => {
        try {
          const progressResponse = await fetch(`/api/analysis-progress?id=${newAnalysisId}`);
          const progressData = await progressResponse.json();
          
          if (progressData.progress !== undefined) {
            setProgress(progressData.progress);
          }
          if (progressData.status) {
            setStatus(progressData.status);
          }
          if (progressData.elapsed) {
            setElapsedTime(progressData.elapsed);
          }
          
          if (progressData.completed) {
            clearInterval(progressInterval);
            if (progressData.result) {
              setAnalysisResult(progressData.result);
              onAnalysisComplete?.(progressData.result);
            }
            if (progressData.error) {
              setError(progressData.error);
            }
            setIsAnalyzing(false);
          }
        } catch (progressError) {
          console.error('進捗取得エラー:', progressError);
        }
      }, 2000); // 2秒ごとに進捗をチェック

      const response = await fetch('/api/run-analysis', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          analysisType: selectedType,
          symbols: [], // 必要に応じて銘柄を指定
          analysisId: newAnalysisId
        }),
      });

      const result = await response.json();

      if (result.success) {
        setStatus('分析が完了しました！');
        setProgress(100);
        setAnalysisResult(result);
        onAnalysisComplete?.(result);
        clearInterval(progressInterval);
      } else {
        setError(result.error || '分析に失敗しました');
        setStatus('分析に失敗しました');
        clearInterval(progressInterval);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '不明なエラーが発生しました');
      setStatus('分析に失敗しました');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const resetAnalysis = () => {
    setIsAnalyzing(false);
    setProgress(0);
    setStatus('');
    setError(null);
    setAnalysisResult(null);
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
          <Play className="w-6 h-6 text-blue-600" />
          ワンクリック分析実行
        </h2>
        <button
          onClick={() => setShowConfig(!showConfig)}
          className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <Settings className="w-5 h-5" />
        </button>
      </div>

      {showConfig && (
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <h3 className="font-semibold text-gray-800 mb-3">分析タイプを選択</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {analysisConfigs.map((config) => (
              <button
                key={config.type}
                onClick={() => setSelectedType(config.type)}
                className={`p-3 rounded-lg border-2 transition-all ${
                  selectedType === config.type
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center gap-2 mb-1">
                  {config.icon}
                  <span className="font-medium">{config.name}</span>
                </div>
                <p className="text-sm text-gray-600">{config.description}</p>
                <p className="text-xs text-gray-500 mt-1">予想時間: {config.estimatedTime}</p>
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="space-y-4">
        {/* 分析実行ボタン */}
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-gray-800">
              {selectedConfig?.name}を実行
            </h3>
            <p className="text-sm text-gray-600">
              {selectedConfig?.description}
            </p>
            <p className="text-xs text-gray-500">
              予想時間: {selectedConfig?.estimatedTime}
            </p>
          </div>
          <button
            onClick={startAnalysis}
            disabled={isAnalyzing}
            className={`px-6 py-3 rounded-lg font-medium transition-all ${
              isAnalyzing
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700 text-white'
            }`}
          >
            {isAnalyzing ? (
              <div className="flex items-center gap-2">
                <RefreshCw className="w-4 h-4 animate-spin" />
                実行中...
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Play className="w-4 h-4" />
                分析実行
              </div>
            )}
          </button>
        </div>

        {/* 進捗表示 */}
        {isAnalyzing && (
          <div className="space-y-3 p-4 bg-blue-50 rounded-lg border border-blue-200">
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium text-blue-800">分析実行中</span>
              <div className="flex items-center gap-2">
                <span className="text-sm text-blue-600">経過時間: {elapsedTime}</span>
                <span className="text-sm font-medium text-blue-800">{progress}%</span>
              </div>
            </div>
            
            <div className="w-full bg-blue-100 rounded-full h-3">
              <div
                className="bg-blue-600 h-3 rounded-full transition-all duration-500 ease-out"
                style={{ width: `${progress}%` }}
              />
            </div>
            
            <div className="flex items-center gap-2">
              <RefreshCw className="w-4 h-4 animate-spin text-blue-600" />
              <p className="text-sm text-blue-700">{status}</p>
            </div>
            
            {analysisId && (
              <p className="text-xs text-blue-500">
                分析ID: {analysisId}
              </p>
            )}
          </div>
        )}

        {/* エラー表示 */}
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center gap-2 text-red-800">
              <AlertCircle className="w-5 h-5" />
              <span className="font-medium">エラーが発生しました</span>
            </div>
            <p className="text-red-700 text-sm mt-1">{error}</p>
            <button
              onClick={resetAnalysis}
              className="mt-2 text-red-600 hover:text-red-800 text-sm underline"
            >
              再試行
            </button>
          </div>
        )}

        {/* 成功結果表示 */}
        {analysisResult && (
          <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center gap-2 text-green-800">
              <CheckCircle className="w-5 h-5" />
              <span className="font-medium">分析完了</span>
            </div>
            <p className="text-green-700 text-sm mt-1">
              {analysisResult.message}
            </p>
            {analysisResult.webDataGenerated && (
              <p className="text-green-600 text-xs mt-1">
                ✅ Webデータも更新されました
              </p>
            )}
            <button
              onClick={resetAnalysis}
              className="mt-2 text-green-600 hover:text-green-800 text-sm underline"
            >
              新しい分析を実行
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
