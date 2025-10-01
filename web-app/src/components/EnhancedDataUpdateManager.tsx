"use client";

import { useState, useEffect, useRef } from "react";
import { RefreshCw, CheckCircle, X, AlertTriangle, Clock, Database, BarChart3 } from "lucide-react";

interface UpdateProgress {
  total: number;
  completed: number;
  failed: number;
  current: string;
  percentage: number;
  startTime: Date;
  estimatedTimeRemaining?: number;
}

interface EnhancedDataUpdateManagerProps {
  onUpdateComplete?: (results: any[]) => void;
  onProgressChange?: (progress: UpdateProgress) => void;
  symbols?: string[];
  className?: string;
}

export default function EnhancedDataUpdateManager({
  onUpdateComplete,
  onProgressChange,
  symbols = ['7203.T', '6758.T', '6861.T'],
  className = ""
}: EnhancedDataUpdateManagerProps) {
  const [isUpdating, setIsUpdating] = useState(false);
  const [progress, setProgress] = useState<UpdateProgress>({
    total: 0,
    completed: 0,
    failed: 0,
    current: '',
    percentage: 0,
    startTime: new Date()
  });
  const [updateHistory, setUpdateHistory] = useState<Array<{
    timestamp: Date;
    status: 'success' | 'error';
    message: string;
    duration: number;
  }>>([]);
  const [showDetails, setShowDetails] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);

  // 更新履歴の読み込み
  useEffect(() => {
    try {
      const history = localStorage.getItem('data_update_history');
      if (history) {
        const parsed = JSON.parse(history);
        setUpdateHistory(parsed.map((item: any) => ({
          ...item,
          timestamp: new Date(item.timestamp)
        })));
      }
    } catch (e) {
      console.warn('更新履歴の読み込みに失敗:', e);
    }
  }, []);

  // 更新履歴の保存
  const saveUpdateHistory = (entry: typeof updateHistory[0]) => {
    try {
      const newHistory = [entry, ...updateHistory.slice(0, 9)]; // 最新10件を保持
      setUpdateHistory(newHistory);
      localStorage.setItem('data_update_history', JSON.stringify(newHistory));
    } catch (e) {
      console.warn('更新履歴の保存に失敗:', e);
    }
  };

  // データ更新の開始
  const startUpdate = async () => {
    if (isUpdating) return;

    setIsUpdating(true);
    abortControllerRef.current = new AbortController();
    
    const startTime = new Date();
    setProgress({
      total: symbols.length,
      completed: 0,
      failed: 0,
      current: '更新を開始しています...',
      percentage: 0,
      startTime
    });

    try {
      // 各銘柄の更新を並列実行
      const updatePromises = symbols.map(async (symbol, index) => {
        try {
          setProgress(prev => ({
            ...prev,
            current: `${symbol} のデータを取得中...`,
            percentage: Math.round((index / symbols.length) * 100)
          }));

          // 実際のデータ取得処理（シミュレーション）
          await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));

          setProgress(prev => ({
            ...prev,
            completed: prev.completed + 1,
            percentage: Math.round(((index + 1) / symbols.length) * 100)
          }));

          return { symbol, status: 'success', data: { price: 2500 + Math.random() * 100 } };
        } catch (error) {
          setProgress(prev => ({
            ...prev,
            failed: prev.failed + 1
          }));
          throw { symbol, error: error instanceof Error ? error.message : 'Unknown error' };
        }
      });

      const results = await Promise.allSettled(updatePromises);
      const successful = results.filter(r => r.status === 'fulfilled').length;
      const failed = results.filter(r => r.status === 'rejected').length;

      const duration = Date.now() - startTime.getTime();
      const entry = {
        timestamp: new Date(),
        status: (failed === 0 ? 'success' : 'error') as 'success' | 'error',
        message: `${successful}件成功、${failed}件失敗`,
        duration: Math.round(duration / 1000)
      };

      saveUpdateHistory(entry);

      setProgress(prev => ({
        ...prev,
        current: `更新完了: ${successful}件成功、${failed}件失敗`,
        percentage: 100
      }));

      onUpdateComplete?.(results.map(r => r.status === 'fulfilled' ? r.value : null).filter(Boolean));
      
    } catch (error) {
      console.error('データ更新エラー:', error);
      const duration = Date.now() - startTime.getTime();
      const entry = {
        timestamp: new Date(),
        status: 'error' as const,
        message: '更新に失敗しました',
        duration: Math.round(duration / 1000)
      };
      saveUpdateHistory(entry);
    } finally {
      setIsUpdating(false);
      abortControllerRef.current = null;
    }
  };

  // 更新のキャンセル
  const cancelUpdate = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setIsUpdating(false);
      setProgress(prev => ({
        ...prev,
        current: '更新がキャンセルされました',
        percentage: 0
      }));
    }
  };

  // 推定残り時間の計算
  const getEstimatedTimeRemaining = () => {
    if (progress.completed === 0) return null;
    
    const elapsed = Date.now() - progress.startTime.getTime();
    const avgTimePerItem = elapsed / progress.completed;
    const remaining = progress.total - progress.completed;
    
    return Math.round((remaining * avgTimePerItem) / 1000);
  };

  const estimatedTime = getEstimatedTimeRemaining();

  return (
    <div className={`bg-white rounded-lg shadow p-6 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Database className="h-5 w-5 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">データ更新</h3>
        </div>
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="text-sm text-gray-500 hover:text-gray-700"
        >
          {showDetails ? '詳細を隠す' : '詳細を表示'}
        </button>
      </div>

      {/* 更新状況 */}
      <div className="space-y-4">
        {/* 進捗バー */}
        <div>
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>{progress.current}</span>
            <span>{progress.percentage}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress.percentage}%` }}
            />
          </div>
        </div>

        {/* 統計情報 */}
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{progress.completed}</div>
            <div className="text-gray-500">完了</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">{progress.failed}</div>
            <div className="text-gray-500">失敗</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-600">{progress.total}</div>
            <div className="text-gray-500">総数</div>
          </div>
        </div>

        {/* 推定残り時間 */}
        {estimatedTime && (
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <Clock className="h-4 w-4" />
            <span>推定残り時間: {estimatedTime}秒</span>
          </div>
        )}

        {/* アクションボタン */}
        <div className="flex space-x-3">
          {!isUpdating ? (
            <button
              onClick={startUpdate}
              className="flex-1 flex items-center justify-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <RefreshCw className="h-4 w-4" />
              <span>一括更新を開始</span>
            </button>
          ) : (
            <button
              onClick={cancelUpdate}
              className="flex-1 flex items-center justify-center space-x-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              <X className="h-4 w-4" />
              <span>更新をキャンセル</span>
            </button>
          )}
        </div>

        {/* 詳細情報 */}
        {showDetails && (
          <div className="border-t pt-4">
            <h4 className="font-medium text-gray-900 mb-3">更新履歴</h4>
            <div className="space-y-2 max-h-40 overflow-y-auto">
              {updateHistory.length === 0 ? (
                <p className="text-sm text-gray-500">更新履歴がありません</p>
              ) : (
                updateHistory.map((entry, index) => (
                  <div key={index} className="flex items-center justify-between text-sm">
                    <div className="flex items-center space-x-2">
                      {entry.status === 'success' ? (
                        <CheckCircle className="h-4 w-4 text-green-500" />
                      ) : (
                        <AlertTriangle className="h-4 w-4 text-red-500" />
                      )}
                      <span className={entry.status === 'success' ? 'text-green-700' : 'text-red-700'}>
                        {entry.message}
                      </span>
                    </div>
                    <div className="text-gray-500">
                      {entry.timestamp.toLocaleString('ja-JP')} ({entry.duration}秒)
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
