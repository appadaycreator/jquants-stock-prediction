"use client";

import React, { useState, useEffect } from "react";
import { 
  Play, 
  CheckCircle, 
  AlertCircle, 
  RefreshCw, 
  Clock, 
  TrendingUp, 
  TrendingDown,
  Zap,
  BarChart3,
  Target,
  Bell,
  Settings,
  History,
  Smartphone
} from "lucide-react";

interface MobileOptimizedDashboardProps {
  onAnalysisComplete?: (result: any) => void;
  onAnalysisStart?: () => void;
}

export default function MobileOptimizedDashboard({ 
  onAnalysisComplete, 
  onAnalysisStart 
}: MobileOptimizedDashboardProps) {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('');
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [elapsedTime, setElapsedTime] = useState<string>('00:00');
  const [analysisHistory, setAnalysisHistory] = useState<any[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [quickActions, setQuickActions] = useState([
    { id: 'ultra_fast', name: '超高速分析', icon: Zap, time: '1-2分', color: 'bg-blue-500' },
    { id: 'comprehensive', name: '包括的分析', icon: BarChart3, time: '3-5分', color: 'bg-green-500' },
    { id: 'trading', name: 'トレーディング', icon: Target, time: '4-6分', color: 'bg-purple-500' }
  ]);
  const [selectedAction, setSelectedAction] = useState('ultra_fast');

  // 履歴の読み込み
  useEffect(() => {
    const saved = localStorage.getItem('mobileAnalysisHistory');
    if (saved) {
      try {
        const history = JSON.parse(saved);
        setAnalysisHistory(history);
      } catch (error) {
        console.error('履歴読み込みエラー:', error);
      }
    }
  }, []);

  // 履歴の保存
  const saveAnalysisHistory = (history: any) => {
    const newHistory = [history, ...analysisHistory.slice(0, 4)]; // 最新5件を保持
    setAnalysisHistory(newHistory);
    localStorage.setItem('mobileAnalysisHistory', JSON.stringify(newHistory));
  };

  // 超高速分析の実行
  const startUltraFastAnalysis = async () => {
    try {
      setIsAnalyzing(true);
      setProgress(0);
      setStatus('超高速分析を開始しています...');
      setError(null);
      setAnalysisResult(null);
      setElapsedTime('00:00');
      
      onAnalysisStart?.();

      const startTime = Date.now();
      const progressInterval = setInterval(async () => {
        try {
          const response = await fetch('/api/run-analysis', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              analysisType: 'ultra_fast',
              symbols: [],
              analysisId: `mobile_${Date.now()}`
            }),
          });

          const result = await response.json();
          
          if (result.success) {
            setProgress(100);
            setStatus('分析完了！');
            setAnalysisResult(result);
            onAnalysisComplete?.(result);
            
            // 履歴に保存
            const historyEntry = {
              id: `mobile_${Date.now()}`,
              type: 'ultra_fast',
              timestamp: new Date().toISOString(),
              duration: elapsedTime,
              status: 'success',
              result: result
            };
            saveAnalysisHistory(historyEntry);
            
            clearInterval(progressInterval);
          } else {
            setError(result.error || '分析に失敗しました');
            setStatus('分析に失敗しました');
            clearInterval(progressInterval);
          }
        } catch (progressError) {
          console.error('進捗取得エラー:', progressError);
        }
      }, 1000);

      // 経過時間の更新
      const timeInterval = setInterval(() => {
        const elapsed = Math.floor((Date.now() - startTime) / 1000);
        const minutes = Math.floor(elapsed / 60);
        const seconds = elapsed % 60;
        setElapsedTime(`${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`);
      }, 1000);

      // 進捗のシミュレーション
      const progressInterval2 = setInterval(() => {
        setProgress(prev => {
          if (prev >= 90) return prev;
          return prev + Math.random() * 10;
        });
      }, 2000);

      // クリーンアップ
      setTimeout(() => {
        clearInterval(progressInterval);
        clearInterval(timeInterval);
        clearInterval(progressInterval2);
        setIsAnalyzing(false);
      }, 120000); // 2分でタイムアウト

    } catch (err) {
      setError(err instanceof Error ? err.message : '不明なエラーが発生しました');
      setStatus('分析に失敗しました');
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
    <div className="min-h-screen bg-gray-50">
      {/* ヘッダー */}
      <div className="bg-white shadow-sm border-b">
        <div className="px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Smartphone className="w-6 h-6 text-blue-600" />
              <h1 className="text-lg font-bold text-gray-800">5分完結分析</h1>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setShowHistory(!showHistory)}
                className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg"
              >
                <History className="w-5 h-5" />
              </button>
              <button
                onClick={() => setShowSettings(!showSettings)}
                className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg"
              >
                <Settings className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* メインコンテンツ */}
      <div className="p-4 space-y-4">
        {/* クイックアクション */}
        <div className="bg-white rounded-lg shadow p-4">
          <h2 className="text-lg font-semibold text-gray-800 mb-3">クイックアクション</h2>
          <div className="grid grid-cols-1 gap-3">
            {quickActions.map((action) => {
              const Icon = action.icon;
              return (
                <button
                  key={action.id}
                  onClick={() => setSelectedAction(action.id)}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    selectedAction === action.id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg ${action.color} text-white`}>
                      <Icon className="w-5 h-5" />
                    </div>
                    <div className="flex-1 text-left">
                      <div className="font-medium text-gray-800">{action.name}</div>
                      <div className="text-sm text-gray-600">予想時間: {action.time}</div>
                    </div>
                    <div className="text-xs text-gray-500">
                      {selectedAction === action.id ? '選択中' : ''}
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* 分析実行ボタン */}
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-semibold text-gray-800">分析実行</h3>
              <p className="text-sm text-gray-600">
                {quickActions.find(a => a.id === selectedAction)?.name}を実行
              </p>
            </div>
            <button
              onClick={startUltraFastAnalysis}
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
                  <span className="text-sm font-medium text-blue-800">{Math.round(progress)}%</span>
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
                分析が正常に完了しました
              </p>
              <button
                onClick={resetAnalysis}
                className="mt-2 text-green-600 hover:text-green-800 text-sm underline"
              >
                新しい分析を実行
              </button>
            </div>
          )}
        </div>

        {/* 履歴表示 */}
        {showHistory && analysisHistory.length > 0 && (
          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
              <History className="w-5 h-5" />
              分析履歴
            </h3>
            <div className="space-y-2">
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
                        {quickActions.find(a => a.id === history.type)?.name || history.type}
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
          </div>
        )}

        {/* 設定パネル */}
        {showSettings && (
          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
              <Settings className="w-5 h-5" />
              設定
            </h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700">通知を有効にする</span>
                <input type="checkbox" className="rounded" />
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700">自動分析を有効にする</span>
                <input type="checkbox" className="rounded" />
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700">ダークモード</span>
                <input type="checkbox" className="rounded" />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* フッター */}
      <div className="bg-white border-t mt-8">
        <div className="px-4 py-3 text-center">
          <p className="text-xs text-gray-500">
            1日5分で完結する超高速分析システム
          </p>
        </div>
      </div>
    </div>
  );
}
