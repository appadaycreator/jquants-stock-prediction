"use client";

import { useState, useEffect, useRef } from "react";
import { 
  RefreshCw, 
  Play, 
  Pause, 
  Square, 
  CheckCircle, 
  XCircle, 
  AlertCircle,
  TrendingUp,
  Clock
} from "lucide-react";

interface StockUpdate {
  symbol: string;
  name: string;
  status: 'pending' | 'updating' | 'completed' | 'error';
  progress: number;
  error?: string;
  data?: any;
}

interface ParallelUpdateManagerProps {
  symbols: string[];
  onUpdateComplete?: (results: any[]) => void;
  onProgressChange?: (progress: number) => void;
  maxConcurrent?: number;
  timeout?: number;
  className?: string;
}

export default function ParallelUpdateManager({
  symbols,
  onUpdateComplete,
  onProgressChange,
  maxConcurrent = 4,
  timeout = 30000,
  className = ""
}: ParallelUpdateManagerProps) {
  const [updates, setUpdates] = useState<StockUpdate[]>([]);
  const [isUpdating, setIsUpdating] = useState(false);
  const [overallProgress, setOverallProgress] = useState(0);
  const [isPaused, setIsPaused] = useState(false);
  const [isAborted, setIsAborted] = useState(false);
  const [completedCount, setCompletedCount] = useState(0);
  const [errorCount, setErrorCount] = useState(0);
  const [startTime, setStartTime] = useState<Date | null>(null);
  const [elapsedTime, setElapsedTime] = useState(0);

  const abortControllerRef = useRef<AbortController | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const timeoutRefs = useRef<Map<string, NodeJS.Timeout>>(new Map());

  // 初期化
  useEffect(() => {
    const initialUpdates: StockUpdate[] = symbols.map(symbol => ({
      symbol,
      name: getStockName(symbol),
      status: 'pending',
      progress: 0
    }));
    setUpdates(initialUpdates);
  }, [symbols]);

  // 経過時間の更新
  useEffect(() => {
    if (isUpdating && startTime) {
      intervalRef.current = setInterval(() => {
        setElapsedTime(Math.floor((Date.now() - startTime.getTime()) / 1000));
      }, 1000);
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isUpdating, startTime]);

  // クリーンアップ
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      timeoutRefs.current.forEach(timeout => clearTimeout(timeout));
    };
  }, []);

  // 銘柄名の取得（実際の実装ではAPIから取得）
  const getStockName = (symbol: string): string => {
    const stockNames: { [key: string]: string } = {
      "7203.T": "トヨタ自動車",
      "6758.T": "ソニーグループ",
      "6861.T": "キーエンス",
      "9984.T": "ソフトバンクグループ",
      "4063.T": "信越化学工業"
    };
    return stockNames[symbol] || symbol;
  };

  // 並列更新の開始
  const startUpdate = async () => {
    if (isUpdating) return;

    setIsUpdating(true);
    setIsPaused(false);
    setIsAborted(false);
    setStartTime(new Date());
    setElapsedTime(0);
    setCompletedCount(0);
    setErrorCount(0);
    setOverallProgress(0);

    // AbortControllerの初期化
    abortControllerRef.current = new AbortController();

    // 全銘柄をpending状態にリセット
    setUpdates(prev => prev.map(update => ({
      ...update,
      status: 'pending',
      progress: 0,
      error: undefined,
      data: undefined
    })));

    // 並列処理の実行
    await executeParallelUpdate();
  };

  // 並列更新の実行
  const executeParallelUpdate = async () => {
    const pendingUpdates = updates.filter(u => u.status === 'pending');
    const results: any[] = [];

    // バッチ処理（最大同時実行数を制限）
    for (let i = 0; i < pendingUpdates.length; i += maxConcurrent) {
      if (isAborted) break;

      const batch = pendingUpdates.slice(i, i + maxConcurrent);
      const batchPromises = batch.map(update => 
        updateStock(update.symbol, abortControllerRef.current!.signal)
      );

      try {
        const batchResults = await Promise.allSettled(batchPromises);
        
        batchResults.forEach((result, index) => {
          const symbol = batch[index].symbol;
          if (result.status === 'fulfilled') {
            setUpdates(prev => prev.map(u => 
              u.symbol === symbol 
                ? { ...u, status: 'completed', progress: 100, data: result.value }
                : u
            ));
            setCompletedCount(prev => prev + 1);
            results.push(result.value);
          } else {
            setUpdates(prev => prev.map(u => 
              u.symbol === symbol 
                ? { ...u, status: 'error', error: result.reason?.message || 'Unknown error' }
                : u
            ));
            setErrorCount(prev => prev + 1);
          }
        });

        // 全体の進捗を更新
        const totalCompleted = completedCount + batch.length;
        const newProgress = Math.round((totalCompleted / symbols.length) * 100);
        setOverallProgress(newProgress);
        onProgressChange?.(newProgress);

        // 一時停止中は待機
        while (isPaused && !isAborted) {
          await new Promise(resolve => setTimeout(resolve, 100));
        }

      } catch (error) {
        console.error('Batch update error:', error);
      }
    }

    // 更新完了
    setIsUpdating(false);
    onUpdateComplete?.(results);
  };

  // 個別銘柄の更新
  const updateStock = async (symbol: string, signal: AbortSignal): Promise<any> => {
    // 更新開始
    setUpdates(prev => prev.map(u => 
      u.symbol === symbol 
        ? { ...u, status: 'updating', progress: 0 }
        : u
    ));

    // タイムアウトの設定
    const timeoutId = setTimeout(() => {
      if (!signal.aborted) {
        setUpdates(prev => prev.map(u => 
          u.symbol === symbol 
            ? { ...u, status: 'error', error: 'Timeout' }
            : u
        ));
      }
    }, timeout);

    timeoutRefs.current.set(symbol, timeoutId);

    try {
      // 実際のAPI呼び出しをシミュレート
      const result = await simulateStockUpdate(symbol, signal);
      
      // タイムアウトをクリア
      const timeoutId = timeoutRefs.current.get(symbol);
      if (timeoutId) {
        clearTimeout(timeoutId);
        timeoutRefs.current.delete(symbol);
      }

      return result;
    } catch (error) {
      // タイムアウトをクリア
      const timeoutId = timeoutRefs.current.get(symbol);
      if (timeoutId) {
        clearTimeout(timeoutId);
        timeoutRefs.current.delete(symbol);
      }
      throw error;
    }
  };

  // 株価更新のシミュレーション
  const simulateStockUpdate = async (symbol: string, signal: AbortSignal): Promise<any> => {
    const steps = 5;
    const stepDelay = 1000 + Math.random() * 2000; // 1-3秒のランダム遅延

    for (let i = 1; i <= steps; i++) {
      if (signal.aborted) {
        throw new Error('Aborted');
      }

      // 進捗更新
      const progress = Math.round((i / steps) * 100);
      setUpdates(prev => prev.map(u => 
        u.symbol === symbol 
          ? { ...u, progress }
          : u
      ));

      await new Promise(resolve => setTimeout(resolve, stepDelay / steps));
    }

    // シミュレートされたデータを返す
    return {
      symbol,
      price: 1000 + Math.random() * 5000,
      change: (Math.random() - 0.5) * 10,
      volume: Math.floor(Math.random() * 1000000),
      timestamp: new Date().toISOString()
    };
  };

  // 一時停止/再開
  const togglePause = () => {
    setIsPaused(!isPaused);
  };

  // 中断
  const abortUpdate = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    setIsAborted(true);
    setIsUpdating(false);
    setIsPaused(false);
  };

  // リセット
  const resetUpdate = () => {
    abortUpdate();
    setUpdates(prev => prev.map(update => ({
      ...update,
      status: 'pending',
      progress: 0,
      error: undefined,
      data: undefined
    })));
    setOverallProgress(0);
    setCompletedCount(0);
    setErrorCount(0);
    setElapsedTime(0);
    setStartTime(null);
  };

  // 経過時間のフォーマット
  const formatElapsedTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className={`bg-white rounded-lg shadow border ${className}`}>
      {/* ヘッダー */}
      <div className="p-4 border-b">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">一括更新</h3>
            <p className="text-sm text-gray-600">
              {symbols.length}銘柄を並列で更新中
            </p>
          </div>
          <div className="flex items-center space-x-2">
            {!isUpdating ? (
              <button
                onClick={startUpdate}
                className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Play className="h-4 w-4 mr-2" />
                開始
              </button>
            ) : (
              <div className="flex items-center space-x-2">
                <button
                  onClick={togglePause}
                  className="flex items-center px-3 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors"
                >
                  {isPaused ? <Play className="h-4 w-4 mr-2" /> : <Pause className="h-4 w-4 mr-2" />}
                  {isPaused ? '再開' : '一時停止'}
                </button>
                <button
                  onClick={abortUpdate}
                  className="flex items-center px-3 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                >
                  <Square className="h-4 w-4 mr-2" />
                  中断
                </button>
              </div>
            )}
            <button
              onClick={resetUpdate}
              className="flex items-center px-3 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              リセット
            </button>
          </div>
        </div>
      </div>

      {/* 全体進捗 */}
      <div className="p-4 border-b">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">全体進捗</span>
          <span className="text-sm text-gray-600">{overallProgress}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${overallProgress}%` }}
          />
        </div>
        <div className="flex items-center justify-between mt-2 text-sm text-gray-600">
          <div className="flex items-center space-x-4">
            <span>完了: {completedCount}</span>
            <span>エラー: {errorCount}</span>
            <span>残り: {symbols.length - completedCount - errorCount}</span>
          </div>
          {startTime && (
            <div className="flex items-center space-x-1">
              <Clock className="h-4 w-4" />
              <span>{formatElapsedTime(elapsedTime)}</span>
            </div>
          )}
        </div>
      </div>

      {/* 銘柄別進捗 */}
      <div className="p-4">
        <h4 className="text-sm font-medium text-gray-700 mb-3">銘柄別進捗</h4>
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {updates.map((update) => (
            <div key={update.symbol} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="flex-shrink-0">
                  {update.status === 'completed' && <CheckCircle className="h-5 w-5 text-green-500" />}
                  {update.status === 'error' && <XCircle className="h-5 w-5 text-red-500" />}
                  {update.status === 'updating' && <RefreshCw className="h-5 w-5 text-blue-500 animate-spin" />}
                  {update.status === 'pending' && <AlertCircle className="h-5 w-5 text-gray-400" />}
                </div>
                <div>
                  <div className="font-medium text-gray-900">{update.symbol}</div>
                  <div className="text-sm text-gray-600">{update.name}</div>
                </div>
              </div>
              
              <div className="flex items-center space-x-3">
                {update.status === 'updating' && (
                  <div className="w-20 bg-gray-200 rounded-full h-1">
                    <div 
                      className="bg-blue-600 h-1 rounded-full transition-all duration-300"
                      style={{ width: `${update.progress}%` }}
                    />
                  </div>
                )}
                <div className="text-sm text-gray-600">
                  {update.status === 'completed' && '完了'}
                  {update.status === 'error' && 'エラー'}
                  {update.status === 'updating' && `${update.progress}%`}
                  {update.status === 'pending' && '待機中'}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* エラー詳細 */}
      {errorCount > 0 && (
        <div className="p-4 border-t bg-red-50">
          <h4 className="text-sm font-medium text-red-800 mb-2">エラー詳細</h4>
          <div className="space-y-1">
            {updates
              .filter(u => u.status === 'error')
              .map((update) => (
                <div key={update.symbol} className="text-sm text-red-700">
                  {update.symbol}: {update.error}
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
}
