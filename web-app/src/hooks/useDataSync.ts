/**
 * データ同期フック
 * リアルタイムでデータ同期状況を監視
 */

import { useState, useEffect, useCallback } from "react";
import { dataSyncManager } from "../lib/data-sync";

interface UseDataSyncOptions {
  autoSync?: boolean;
  syncInterval?: number;
  onSyncComplete?: (status: any) => void;
  onSyncError?: (error: string) => void;
}

export function useDataSync(options: UseDataSyncOptions = {}) {
  const [status, setStatus] = useState(dataSyncManager.getStatus());
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    autoSync = true,
    syncInterval = 5 * 60 * 1000, // 5分
    onSyncComplete,
    onSyncError,
  } = options;

  // データ同期の実行
  const performSync = useCallback(async () => {
    if (isLoading) return;

    setIsLoading(true);
    setError(null);

    try {
      const syncStatus = await dataSyncManager.performSync();
      setStatus(syncStatus);

      if (syncStatus.status === "success") {
        onSyncComplete?.(syncStatus);
      } else {
        const errorMessage = syncStatus.errors.join(", ");
        setError(errorMessage);
        onSyncError?.(errorMessage);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "不明なエラー";
      setError(errorMessage);
      onSyncError?.(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [isLoading, onSyncComplete, onSyncError]);

  // 自動同期の設定
  useEffect(() => {
    if (autoSync) {
      dataSyncManager.updateConfig({ autoSync: true, syncInterval });
    } else {
      dataSyncManager.updateConfig({ autoSync: false });
    }
  }, [autoSync, syncInterval]);

  // ステータスの監視
  useEffect(() => {
    const interval = setInterval(() => {
      setStatus(dataSyncManager.getStatus());
    }, 1000); // 1秒ごとにステータス更新

    return () => clearInterval(interval);
  }, []);

  // 手動同期
  const manualSync = useCallback(() => {
    performSync();
  }, [performSync]);

  // 同期の停止
  const stopSync = useCallback(() => {
    dataSyncManager.stopSync();
  }, []);

  // 同期の再開
  const startSync = useCallback(() => {
    dataSyncManager.startSync();
  }, []);

  return {
    status,
    isLoading,
    error,
    performSync: manualSync,
    stopSync,
    startSync,
    isHealthy: status.status === "success",
    hasErrors: status.errors.length > 0,
    lastUpdate: status.lastUpdate,
  };
}
