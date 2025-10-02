/**
 * 強化されたデータ永続化システム
 * ローカルストレージ、IndexedDB、暗号化を統合
 */

interface PersistenceConfig {
  encryptionEnabled: boolean;
  compressionEnabled: boolean;
  maxStorageSize: number;
  cleanupInterval: number;
  backupEnabled: boolean;
}

interface StoredData<T> {
  data: T;
  timestamp: number;
  version: string;
  checksum: string;
  metadata: {
    source: string;
    type: string;
    size: number;
    compressed: boolean;
    encrypted: boolean;
  };
}

interface DataBackup {
  id: string;
  timestamp: number;
  data: any;
  size: number;
  type: string;
}

class EnhancedDataPersistence {
  private config: PersistenceConfig;
  private db: IDBDatabase | null = null;
  private cleanupTimer: NodeJS.Timeout | null = null;
  private encryptionKey: string | null = null;

  constructor(config: Partial<PersistenceConfig> = {}) {
    this.config = {
      encryptionEnabled: config.encryptionEnabled !== false,
      compressionEnabled: config.compressionEnabled !== false,
      maxStorageSize: config.maxStorageSize || 50 * 1024 * 1024, // 50MB
      cleanupInterval: config.cleanupInterval || 24 * 60 * 60 * 1000, // 24時間
      backupEnabled: config.backupEnabled !== false,
    };

    this.initIndexedDB();
    this.startCleanup();
    this.initEncryption();
  }

  /**
   * IndexedDBの初期化
   */
  private async initIndexedDB(): Promise<void> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open('enhanced_persistence_db', 2);
      
      request.onerror = () => {
        console.error('IndexedDB初期化エラー:', request.error);
        reject(request.error);
      };
      
      request.onsuccess = () => {
        this.db = request.result;
        console.info('IndexedDB初期化完了');
        resolve();
      };
      
      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;
        
        // データストア
        if (!db.objectStoreNames.contains('data')) {
          const dataStore = db.createObjectStore('data', { keyPath: 'key' });
          dataStore.createIndex('timestamp', 'timestamp', { unique: false });
          dataStore.createIndex('type', 'type', { unique: false });
          dataStore.createIndex('size', 'size', { unique: false });
        }
        
        // バックアップストア
        if (!db.objectStoreNames.contains('backups')) {
          const backupStore = db.createObjectStore('backups', { keyPath: 'id' });
          backupStore.createIndex('timestamp', 'timestamp', { unique: false });
          backupStore.createIndex('type', 'type', { unique: false });
        }
      };
    });
  }

  /**
   * 暗号化の初期化
   */
  private async initEncryption(): Promise<void> {
    if (!this.config.encryptionEnabled) return;

    try {
      // 簡易的な暗号化キーの生成（実際の実装ではより安全な方法を使用）
      const key = await this.generateEncryptionKey();
      this.encryptionKey = key;
    } catch (error) {
      console.warn('暗号化の初期化に失敗:', error);
      this.config.encryptionEnabled = false;
    }
  }

  /**
   * データの保存
   */
  async save<T>(
    key: string,
    data: T,
    options: {
      type?: string;
      ttl?: number;
      compress?: boolean;
      encrypt?: boolean;
      backup?: boolean;
    } = {}
  ): Promise<void> {
    try {
      const now = Date.now();
      const type = options.type || 'default';
      const compress = options.compress !== false && this.config.compressionEnabled;
      const encrypt = options.encrypt !== false && this.config.encryptionEnabled;
      const backup = options.backup !== false && this.config.backupEnabled;

      let processedData = data;
      let metadata = {
        source: 'user',
        type,
        size: JSON.stringify(data).length,
        compressed: false,
        encrypted: false,
      };

      // 圧縮
      if (compress) {
        processedData = await this.compress(processedData);
        metadata.compressed = true;
        metadata.size = JSON.stringify(processedData).length;
      }

      // 暗号化
      if (encrypt && this.encryptionKey) {
        processedData = await this.encrypt(processedData);
        metadata.encrypted = true;
      }

      // チェックサムの計算
      const checksum = await this.calculateChecksum(processedData);

      const storedData: StoredData<T> = {
        data: processedData,
        timestamp: now,
        version: '1.0',
        checksum,
        metadata,
      };

      // ローカルストレージに保存
      try {
        localStorage.setItem(key, JSON.stringify(storedData));
      } catch (error) {
        console.warn('ローカルストレージへの保存に失敗:', error);
      }

      // IndexedDBに保存
      if (this.db) {
        await this.saveToIndexedDB(key, storedData);
      }

      // バックアップの作成
      if (backup) {
        await this.createBackup(key, storedData, type);
      }

      console.info(`データを保存しました: ${key}`);
    } catch (error) {
      console.error('データ保存エラー:', error);
      throw error;
    }
  }

  /**
   * データの取得
   */
  async get<T>(key: string): Promise<T | null> {
    try {
      // ローカルストレージから取得
      const localData = localStorage.getItem(key);
      if (localData) {
        const storedData: StoredData<T> = JSON.parse(localData);
        return await this.processRetrievedData(storedData);
      }

      // IndexedDBから取得
      if (this.db) {
        const storedData = await this.getFromIndexedDB<T>(key);
        if (storedData) {
          return await this.processRetrievedData(storedData);
        }
      }

      return null;
    } catch (error) {
      console.error('データ取得エラー:', error);
      return null;
    }
  }

  /**
   * データの削除
   */
  async delete(key: string): Promise<void> {
    try {
      localStorage.removeItem(key);
      
      if (this.db) {
        await this.deleteFromIndexedDB(key);
      }
    } catch (error) {
      console.error('データ削除エラー:', error);
    }
  }

  /**
   * データの一覧取得
   */
  async list(prefix?: string): Promise<Array<{ key: string; timestamp: number; type: string; size: number }>> {
    const items: Array<{ key: string; timestamp: number; type: string; size: number }> = [];

    try {
      // ローカルストレージから取得
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && (!prefix || key.startsWith(prefix))) {
          const data = localStorage.getItem(key);
          if (data) {
            try {
              const storedData = JSON.parse(data);
              items.push({
                key,
                timestamp: storedData.timestamp,
                type: storedData.metadata?.type || 'unknown',
                size: storedData.metadata?.size || 0,
              });
            } catch (error) {
              console.warn(`データの解析に失敗: ${key}`, error);
            }
          }
        }
      }
    } catch (error) {
      console.error('データ一覧取得エラー:', error);
    }

    return items.sort((a, b) => b.timestamp - a.timestamp);
  }

  /**
   * ストレージ使用量の取得
   */
  async getStorageUsage(): Promise<{
    totalSize: number;
    itemCount: number;
    availableSpace: number;
    usagePercent: number;
  }> {
    let totalSize = 0;
    let itemCount = 0;

    try {
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key) {
          const data = localStorage.getItem(key);
          if (data) {
            totalSize += data.length;
            itemCount++;
          }
        }
      }
    } catch (error) {
      console.error('ストレージ使用量計算エラー:', error);
    }

    const availableSpace = this.config.maxStorageSize - totalSize;
    const usagePercent = (totalSize / this.config.maxStorageSize) * 100;

    return {
      totalSize,
      itemCount,
      availableSpace,
      usagePercent,
    };
  }

  /**
   * 古いデータのクリーンアップ
   */
  async cleanup(): Promise<void> {
    try {
      const now = Date.now();
      const items = await this.list();
      const itemsToDelete: string[] = [];

      for (const item of items) {
        // 24時間以上古いデータを削除
        if (now - item.timestamp > 24 * 60 * 60 * 1000) {
          itemsToDelete.push(item.key);
        }
      }

      for (const key of itemsToDelete) {
        await this.delete(key);
      }

      if (itemsToDelete.length > 0) {
        console.info(`クリーンアップ完了: ${itemsToDelete.length}件の古いデータを削除`);
      }
    } catch (error) {
      console.error('クリーンアップエラー:', error);
    }
  }

  /**
   * バックアップの作成
   */
  private async createBackup(key: string, data: StoredData<any>, type: string): Promise<void> {
    if (!this.db) return;

    const backup: DataBackup = {
      id: `${key}_${Date.now()}`,
      timestamp: Date.now(),
      data,
      size: JSON.stringify(data).length,
      type,
    };

    await this.saveBackupToIndexedDB(backup);
  }

  /**
   * 取得データの処理
   */
  private async processRetrievedData<T>(storedData: StoredData<T>): Promise<T> {
    let data = storedData.data;

    // チェックサムの検証
    const checksum = await this.calculateChecksum(data);
    if (checksum !== storedData.checksum) {
      throw new Error('データの整合性チェックに失敗しました');
    }

    // 復号化
    if (storedData.metadata.encrypted && this.encryptionKey) {
      data = await this.decrypt(data);
    }

    // 展開
    if (storedData.metadata.compressed) {
      data = await this.decompress(data);
    }

    return data;
  }

  /**
   * 圧縮
   */
  private async compress(data: any): Promise<any> {
    // 簡易的な圧縮実装（実際の実装ではLZ4やGzipを使用）
    return data;
  }

  /**
   * 展開
   */
  private async decompress(data: any): Promise<any> {
    // 簡易的な展開実装
    return data;
  }

  /**
   * 暗号化
   */
  private async encrypt(data: any): Promise<any> {
    if (!this.encryptionKey) return data;
    
    // 簡易的な暗号化実装（実際の実装ではWeb Crypto APIを使用）
    const jsonString = JSON.stringify(data);
    return btoa(jsonString);
  }

  /**
   * 復号化
   */
  private async decrypt(data: any): Promise<any> {
    if (!this.encryptionKey) return data;
    
    // 簡易的な復号化実装
    const jsonString = atob(data);
    return JSON.parse(jsonString);
  }

  /**
   * チェックサムの計算
   */
  private async calculateChecksum(data: any): Promise<string> {
    const jsonString = JSON.stringify(data);
    const encoder = new TextEncoder();
    const dataBuffer = encoder.encode(jsonString);
    const hashBuffer = await crypto.subtle.digest('SHA-256', dataBuffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  }

  /**
   * 暗号化キーの生成
   */
  private async generateEncryptionKey(): Promise<string> {
    const array = new Uint8Array(32);
    crypto.getRandomValues(array);
    return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
  }

  /**
   * IndexedDBへの保存
   */
  private async saveToIndexedDB(key: string, data: StoredData<any>): Promise<void> {
    if (!this.db) return;

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['data'], 'readwrite');
      const store = transaction.objectStore('data');
      const request = store.put({ key, ...data });

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * IndexedDBからの取得
   */
  private async getFromIndexedDB<T>(key: string): Promise<StoredData<T> | null> {
    if (!this.db) return null;

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['data'], 'readonly');
      const store = transaction.objectStore('data');
      const request = store.get(key);

      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * IndexedDBからの削除
   */
  private async deleteFromIndexedDB(key: string): Promise<void> {
    if (!this.db) return;

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['data'], 'readwrite');
      const store = transaction.objectStore('data');
      const request = store.delete(key);

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * バックアップの保存
   */
  private async saveBackupToIndexedDB(backup: DataBackup): Promise<void> {
    if (!this.db) return;

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['backups'], 'readwrite');
      const store = transaction.objectStore('backups');
      const request = store.put(backup);

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * 定期的なクリーンアップの開始
   */
  private startCleanup(): void {
    this.cleanupTimer = setInterval(() => {
      this.cleanup();
    }, this.config.cleanupInterval);
  }

  /**
   * システムの停止
   */
  stop(): void {
    if (this.cleanupTimer) {
      clearInterval(this.cleanupTimer);
      this.cleanupTimer = null;
    }
  }
}

// シングルトンインスタンス
const dataPersistence = new EnhancedDataPersistence({
  encryptionEnabled: true,
  compressionEnabled: true,
  maxStorageSize: 50 * 1024 * 1024, // 50MB
  cleanupInterval: 24 * 60 * 60 * 1000, // 24時間
  backupEnabled: true,
});

export default dataPersistence;
export type { PersistenceConfig, StoredData, DataBackup };
