"use client";

import { DataFetcher } from "./DataFetcher";
import { cacheService } from "./CacheService";

export class CacheInitializer {
  private static instance: CacheInitializer;
  private isInitialized = false;
  private initPromise: Promise<void> | null = null;

  private constructor() {}

  static getInstance(): CacheInitializer {
    if (!CacheInitializer.instance) {
      CacheInitializer.instance = new CacheInitializer();
    }
    return CacheInitializer.instance;
  }

  /**
   * アプリ起動時の初期化
   */
  async initialize(): Promise<void> {
    if (this.isInitialized) {
      return;
    }

    if (this.initPromise) {
      return this.initPromise;
    }

    this.initPromise = this._performInitialization();
    return this.initPromise;
  }

  private async _performInitialization(): Promise<void> {
    try {
      console.log("🚀 キャッシュシステム初期化開始");

      // 1. キャッシュサービスの初期化
      await DataFetcher.initialize();

      // 2. ネットワーク状態の確認
      const isOffline = DataFetcher.isOffline();
      console.log(`🌐 ネットワーク状態: ${isOffline ? "オフライン" : "オンライン"}`);

      // 3. 期限切れデータのみ差分取得
      if (!isOffline) {
        await this._refreshExpiredData();
      } else {
        console.log("📱 オフライン状態: キャッシュデータを使用");
      }

      // 4. ネットワーク状態の監視開始
      this._startNetworkMonitoring();

      this.isInitialized = true;
      console.log("✅ キャッシュシステム初期化完了");
    } catch (error) {
      console.error("❌ キャッシュシステム初期化エラー:", error);
      throw error;
    }
  }

  /**
   * 期限切れデータの差分取得
   */
  private async _refreshExpiredData(): Promise<void> {
    try {
      console.log("🔄 期限切れデータの差分取得開始");

      // 日足データの確認・更新
      try {
        await DataFetcher.getDailyQuotes(undefined, false);
        console.log("✅ 日足データ更新完了");
      } catch (error) {
        console.warn("⚠️ 日足データ更新失敗（キャッシュデータを使用）:", error);
      }

      // 上場銘柄データの確認・更新
      try {
        await DataFetcher.getListedData(false);
        console.log("✅ 上場銘柄データ更新完了");
      } catch (error) {
        console.warn("⚠️ 上場銘柄データ更新失敗（キャッシュデータを使用）:", error);
      }

      console.log("✅ 期限切れデータの差分取得完了");
    } catch (error) {
      console.error("❌ 期限切れデータ取得エラー:", error);
    }
  }

  /**
   * ネットワーク状態の監視開始
   */
  private _startNetworkMonitoring(): void {
    const cleanup = DataFetcher.onNetworkChange((isOnline) => {
      if (isOnline) {
        console.log("🌐 オンライン復帰: データ更新を開始");
        this._refreshExpiredData();
      } else {
        console.log("📱 オフライン状態: キャッシュデータを使用");
      }
    });

    // アプリ終了時のクリーンアップ
    window.addEventListener("beforeunload", cleanup);
  }

  /**
   * 強制リフレッシュ
   */
  async forceRefresh(): Promise<void> {
    try {
      console.log("🔄 強制リフレッシュ開始");
      await DataFetcher.forceRefresh();
      await this._refreshExpiredData();
      console.log("✅ 強制リフレッシュ完了");
    } catch (error) {
      console.error("❌ 強制リフレッシュエラー:", error);
      throw error;
    }
  }

  /**
   * キャッシュメトリクスの取得
   */
  getMetrics() {
    return cacheService.getMetrics();
  }

  /**
   * キャッシュメトリクスの出力
   */
  logMetrics(): void {
    cacheService.logMetrics();
  }

  /**
   * 初期化状態の確認
   */
  isReady(): boolean {
    return this.isInitialized;
  }
}

// シングルトンインスタンスのエクスポート
export const cacheInitializer = CacheInitializer.getInstance();
