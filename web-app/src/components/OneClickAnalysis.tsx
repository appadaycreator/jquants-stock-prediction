"use client";

import React, { useState } from "react";
import { Play, CheckCircle, AlertCircle, RefreshCw, Settings, BarChart3, TrendingUp, Brain, Zap, History, Clock } from "lucide-react";

interface AnalysisConfig {
  type: 'ultra_fast' | 'comprehensive' | 'symbols' | 'trading' | 'sentiment';
  name: string;
  description: string;
  icon: React.ReactNode;
  estimatedTime: string;
}

const analysisConfigs: AnalysisConfig[] = [
  {
    type: 'ultra_fast',
    name: '超高速分析',
    description: '1日5分で完結する最適化された分析',
    icon: <Zap className="w-5 h-5" />,
    estimatedTime: '1-2分'
  },
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

interface AnalysisHistory {
  id: string;
  type: string;
  timestamp: string;
  duration: string;
  status: 'success' | 'error';
  result?: any;
  error?: string;
}

interface OneClickAnalysisProps {
  onAnalysisComplete?: (result: any) => void;
  onAnalysisStart?: () => void;
}

export default function OneClickAnalysis({ onAnalysisComplete, onAnalysisStart }: OneClickAnalysisProps) {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [selectedType, setSelectedType] = useState<AnalysisConfig['type']>('ultra_fast');
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('');
  const [showConfig, setShowConfig] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [analysisId, setAnalysisId] = useState<string | null>(null);
  const [elapsedTime, setElapsedTime] = useState<string>('00:00');
  const [analysisHistory, setAnalysisHistory] = useState<AnalysisHistory[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const [previousResult, setPreviousResult] = useState<any>(null);

  const selectedConfig = analysisConfigs.find(config => config.type === selectedType);

  // 履歴の保存
  const saveAnalysisHistory = (history: AnalysisHistory) => {
    const newHistory = [history, ...analysisHistory.slice(0, 9)]; // 最新10件を保持
    setAnalysisHistory(newHistory);
    localStorage.setItem('analysisHistory', JSON.stringify(newHistory));
  };

  // 履歴の読み込み
  const loadAnalysisHistory = () => {
    const saved = localStorage.getItem('analysisHistory');
    if (saved) {
      try {
        const history = JSON.parse(saved);
        setAnalysisHistory(history);
        if (history.length > 0) {
          setPreviousResult(history[0].result);
        }
      } catch (error) {
        console.error('履歴読み込みエラー:', error);
      }
    }
  };

  // コンポーネントマウント時に履歴を読み込み
  React.useEffect(() => {
    loadAnalysisHistory();
  }, []);

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
              
              // 履歴に保存
              const historyEntry: AnalysisHistory = {
                id: newAnalysisId,
                type: selectedType,
                timestamp: new Date().toISOString(),
                duration: elapsedTime,
                status: 'success',
                result: progressData.result
              };
              saveAnalysisHistory(historyEntry);
            }
            if (progressData.error) {
              setError(progressData.error);
              
              // エラーも履歴に保存
              const historyEntry: AnalysisHistory = {
                id: newAnalysisId,
                type: selectedType,
                timestamp: new Date().toISOString(),
                duration: elapsedTime,
                status: 'error',
                error: progressData.error
              };
              saveAnalysisHistory(historyEntry);
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
        <div className="flex gap-2">
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
            title="分析履歴"
          >
            <History className="w-5 h-5" />
          </button>
          <button
            onClick={() => setShowConfig(!showConfig)}
            className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
            title="設定"
          >
            <Settings className="w-5 h-5" />
          </button>
        </div>
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

      {/* 履歴表示パネル */}
      {showHistory && (
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
            <History className="w-5 h-5" />
            分析履歴
          </h3>
          {analysisHistory.length === 0 ? (
            <p className="text-gray-500 text-sm">分析履歴がありません</p>
          ) : (
            <div className="space-y-2 max-h-60 overflow-y-auto">
              {analysisHistory.map((history, index) => (
                <div
                  key={history.id}
                  className={`p-3 rounded-lg border ${
                    history.status === 'success'
                      ? 'border-green-200 bg-green-50'
                      : 'border-red-200 bg-red-50'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      {history.status === 'success' ? (
                        <CheckCircle className="w-4 h-4 text-green-600" />
                      ) : (
                        <AlertCircle className="w-4 h-4 text-red-600" />
                      )}
                      <span className="font-medium text-sm">
                        {analysisConfigs.find(c => c.type === history.type)?.name || history.type}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 text-xs text-gray-500">
                      <Clock className="w-3 h-3" />
                      {new Date(history.timestamp).toLocaleString('ja-JP')}
                    </div>
                  </div>
                  <div className="flex items-center justify-between mt-1">
                    <span className="text-xs text-gray-600">
                      実行時間: {history.duration}
                    </span>
                    {index === 0 && history.status === 'success' && (
                      <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                        最新結果
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* 前回結果との比較表示 */}
      {previousResult && analysisResult && (
        <div className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <h3 className="font-semibold text-blue-800 mb-3 flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            前回結果との比較
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h4 className="font-medium text-blue-700 mb-2">前回の結果</h4>
              <div className="text-sm text-blue-600">
                <p>実行日時: {new Date(analysisHistory[0]?.timestamp).toLocaleString('ja-JP')}</p>
                <p>実行時間: {analysisHistory[0]?.duration}</p>
                <p>分析タイプ: {analysisConfigs.find(c => c.type === analysisHistory[0]?.type)?.name}</p>
              </div>
            </div>
            <div>
              <h4 className="font-medium text-green-700 mb-2">今回の結果</h4>
              <div className="text-sm text-green-600">
                <p>実行日時: {new Date().toLocaleString('ja-JP')}</p>
                <p>実行時間: {elapsedTime}</p>
                <p>分析タイプ: {selectedConfig?.name}</p>
              </div>
            </div>
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
