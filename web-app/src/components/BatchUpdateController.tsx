"use client";

import { useState, useEffect, useRef } from "react";
import { 
  Play, 
  Pause, 
  Square, 
  RotateCcw, 
  RefreshCw, 
  AlertCircle, 
  CheckCircle, 
  Clock,
  TrendingUp,
  TrendingDown,
  Activity
} from "lucide-react";

interface UpdateTask {
  id: string;
  symbol: string;
  type: 'price' | 'analysis' | 'prediction';
  priority: number;
  data?: any;
}

interface UpdateProgress {
  completed: number;
  total: number;
  current: string;
  percentage: number;
  estimatedTimeRemaining: number;
  errors: string[];
}

interface BatchUpdateControllerProps {
  symbols: string[];
  onUpdateComplete: (results: any[]) => void;
  onProgressChange: (progress: UpdateProgress) => void;
}

export default function BatchUpdateController({
  symbols,
  onUpdateComplete,
  onProgressChange,
}: BatchUpdateControllerProps) {
  const [isRunning, setIsRunning] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [progress, setProgress] = useState<UpdateProgress>({
    completed: 0,
    total: 0,
    current: '',
    percentage: 0,
    estimatedTimeRemaining: 0,
    errors: []
  });
  const [worker, setWorker] = useState<Worker | null>(null);
  const [results, setResults] = useState<any[]>([]);
  const [showErrors, setShowErrors] = useState(false);
  const workerRef = useRef<Worker | null>(null);

  // Initialize Web Worker
  useEffect(() => {
    if (typeof Worker !== 'undefined') {
      const workerInstance = new Worker('/workers/batchUpdateWorker.js');
      workerRef.current = workerInstance;
      setWorker(workerInstance);

      workerInstance.onmessage = (event) => {
        const { type, payload } = event.data;

        switch (type) {
          case 'PROGRESS':
            if (payload?.progress) {
              setProgress(payload.progress);
              onProgressChange(payload.progress);
            }
            break;
          case 'COMPLETE':
            setIsRunning(false);
            setIsPaused(false);
            if (payload?.progress) {
              setProgress(payload.progress);
              onProgressChange(payload.progress);
            }
            onUpdateComplete(results);
            break;
          case 'ERROR':
            console.error('Worker error:', payload?.error);
            break;
          case 'STATUS':
            if (payload?.progress) {
              setProgress(payload.progress);
            }
            break;
        }
      };

      workerInstance.onerror = (error) => {
        console.error('Worker error:', error);
        setIsRunning(false);
        setIsPaused(false);
      };

      return () => {
        workerInstance.terminate();
      };
    }
  }, [onUpdateComplete, onProgressChange, results]);

  const generateTasks = (symbols: string[]): UpdateTask[] => {
    return symbols.map((symbol, index) => ({
      id: `task_${index}`,
      symbol,
      type: 'price' as const,
      priority: index < 5 ? 1 : 2, // First 5 symbols have higher priority
      data: { symbol }
    }));
  };

  const startUpdate = () => {
    if (!workerRef.current) return;

    const tasks = generateTasks(symbols);
    setProgress({
      completed: 0,
      total: tasks.length,
      current: '',
      percentage: 0,
      estimatedTimeRemaining: 0,
      errors: []
    });
    setResults([]);
    setIsRunning(true);
    setIsPaused(false);

    workerRef.current.postMessage({
      type: 'START_UPDATE',
      payload: {
        tasks,
        batchSize: 3, // Process 3 symbols at a time
        delayMs: 1000 // 1 second delay between batches
      }
    });
  };

  const pauseUpdate = () => {
    if (!workerRef.current) return;

    workerRef.current.postMessage({ type: 'PAUSE_UPDATE' });
    setIsPaused(true);
  };

  const resumeUpdate = () => {
    if (!workerRef.current) return;

    workerRef.current.postMessage({ type: 'RESUME_UPDATE' });
    setIsPaused(false);
  };

  const stopUpdate = () => {
    if (!workerRef.current) return;

    workerRef.current.postMessage({ type: 'STOP_UPDATE' });
    setIsRunning(false);
    setIsPaused(false);
  };

  const resetUpdate = () => {
    stopUpdate();
    setProgress({
      completed: 0,
      total: 0,
      current: '',
      percentage: 0,
      estimatedTimeRemaining: 0,
      errors: []
    });
    setResults([]);
  };

  const formatTime = (seconds: number): string => {
    if (seconds < 60) {
      return `${seconds}秒`;
    } else if (seconds < 3600) {
      const minutes = Math.floor(seconds / 60);
      const remainingSeconds = seconds % 60;
      return `${minutes}分${remainingSeconds}秒`;
    } else {
      const hours = Math.floor(seconds / 3600);
      const minutes = Math.floor((seconds % 3600) / 60);
      return `${hours}時間${minutes}分`;
    }
  };

  const getStatusColor = () => {
    if (progress.errors.length > 0) return "text-red-600";
    if (isPaused) return "text-yellow-600";
    if (isRunning) return "text-blue-600";
    return "text-gray-600";
  };

  const getStatusIcon = () => {
    if (progress.errors.length > 0) return <AlertCircle className="h-5 w-5" />;
    if (isPaused) return <Pause className="h-5 w-5" />;
    if (isRunning) return <RefreshCw className="h-5 w-5 animate-spin" />;
    return <CheckCircle className="h-5 w-5" />;
  };

  return (
    <div className="bg-white rounded-lg shadow-lg border p-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-gray-900">一括更新コントローラー</h2>
          <p className="text-sm text-gray-600">大量銘柄の更新処理を効率的に管理</p>
        </div>
        <div className="flex items-center space-x-2">
          <span className={`flex items-center space-x-1 ${getStatusColor()}`}>
            {getStatusIcon()}
            <span className="text-sm font-medium">
              {progress.errors.length > 0 ? "エラー" :
               isPaused ? "一時停止中" :
               isRunning ? "実行中" : "待機中"}
            </span>
          </span>
        </div>
      </div>

      {/* 進捗表示 */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">進捗</span>
          <span className="text-sm text-gray-600">
            {progress.completed} / {progress.total} 銘柄
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div
            className="bg-blue-600 h-3 rounded-full transition-all duration-500"
            style={{ width: `${progress.percentage}%` }}
          />
        </div>
        <div className="flex items-center justify-between mt-2 text-sm text-gray-600">
          <span>{progress.percentage}% 完了</span>
          {progress.estimatedTimeRemaining > 0 && (
            <span>残り時間: {formatTime(progress.estimatedTimeRemaining)}</span>
          )}
        </div>
      </div>

      {/* 現在処理中の銘柄 */}
      {progress.current && (
        <div className="mb-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
          <div className="flex items-center space-x-2">
            <Activity className="h-4 w-4 text-blue-600" />
            <span className="text-sm font-medium text-blue-900">現在処理中:</span>
            <span className="text-sm text-blue-800">{progress.current}</span>
          </div>
        </div>
      )}

      {/* エラー表示 */}
      {progress.errors.length > 0 && (
        <div className="mb-4 p-3 bg-red-50 rounded-lg border border-red-200">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <AlertCircle className="h-4 w-4 text-red-600" />
              <span className="text-sm font-medium text-red-900">
                エラー ({progress.errors.length}件)
              </span>
            </div>
            <button
              onClick={() => setShowErrors(!showErrors)}
              className="text-sm text-red-600 hover:text-red-800"
            >
              {showErrors ? "非表示" : "詳細"}
            </button>
          </div>
          {showErrors && (
            <div className="space-y-1">
              {progress.errors.map((error, index) => (
                <div key={index} className="text-xs text-red-700">
                  • {error}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* コントロールボタン */}
      <div className="flex items-center justify-center space-x-4">
        {!isRunning && !isPaused && (
          <button
            onClick={startUpdate}
            className="flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Play className="h-5 w-5 mr-2" />
            更新開始
          </button>
        )}
        
        {isRunning && !isPaused && (
          <button
            onClick={pauseUpdate}
            className="flex items-center px-6 py-3 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors"
          >
            <Pause className="h-5 w-5 mr-2" />
            一時停止
          </button>
        )}
        
        {isPaused && (
          <button
            onClick={resumeUpdate}
            className="flex items-center px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            <Play className="h-5 w-5 mr-2" />
            再開
          </button>
        )}
        
        {(isRunning || isPaused) && (
          <button
            onClick={stopUpdate}
            className="flex items-center px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            <Square className="h-5 w-5 mr-2" />
            停止
          </button>
        )}
        
        <button
          onClick={resetUpdate}
          className="flex items-center px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
        >
          <RotateCcw className="h-5 w-5 mr-2" />
          リセット
        </button>
      </div>

      {/* 統計情報 */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="text-center">
          <div className="text-2xl font-bold text-gray-900">{progress.total}</div>
          <div className="text-sm text-gray-600">対象銘柄</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-green-600">{progress.completed}</div>
          <div className="text-sm text-gray-600">完了</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-red-600">{progress.errors.length}</div>
          <div className="text-sm text-gray-600">エラー</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-blue-600">{progress.percentage}%</div>
          <div className="text-sm text-gray-600">進捗</div>
        </div>
      </div>

      {/* 処理完了時のメッセージ */}
      {progress.percentage === 100 && progress.total > 0 && (
        <div className="mt-6 p-4 bg-green-50 rounded-lg border border-green-200">
          <div className="flex items-center space-x-2 mb-2">
            <CheckCircle className="h-5 w-5 text-green-600" />
            <span className="font-medium text-green-900">更新完了！</span>
          </div>
          <p className="text-sm text-green-800">
            {progress.total}銘柄の更新が完了しました。
            {progress.errors.length > 0 && ` ${progress.errors.length}件のエラーが発生しました。`}
          </p>
        </div>
      )}
    </div>
  );
}
