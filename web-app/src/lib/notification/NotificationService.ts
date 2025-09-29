'use client';

export interface NotificationConfig {
  email: {
    enabled: boolean;
    smtp_server: string;
    smtp_port: number;
    email_user: string;
    email_password: string;
    email_to: string;
  };
  push: {
    enabled: boolean;
    vapid_public_key: string;
    vapid_private_key: string;
    vapid_subject: string;
  };
  schedule: {
    morning_analysis: string;
    evening_analysis: string;
    timezone: string;
  };
  content: {
    include_analysis_summary: boolean;
    include_performance_metrics: boolean;
    include_recommendations: boolean;
    include_risk_alerts: boolean;
  };
  filters: {
    min_confidence_threshold: number;
    include_errors: boolean;
    include_success: boolean;
  };
}

export interface NotificationData {
  type: 'analysis_complete' | 'error' | 'recommendation' | 'risk_alert';
  title: string;
  message: string;
  data?: any;
  timestamp: string;
  priority: 'high' | 'medium' | 'low';
}

export class NotificationService {
  private static instance: NotificationService;
  private config: NotificationConfig | null = null;
  private registration: ServiceWorkerRegistration | null = null;

  private constructor() {}

  public static getInstance(): NotificationService {
    if (!NotificationService.instance) {
      NotificationService.instance = new NotificationService();
    }
    return NotificationService.instance;
  }

  // 設定の読み込み
  public async loadConfig(): Promise<NotificationConfig> {
    try {
      // ローカルストレージから設定を読み込み
      const savedConfig = localStorage.getItem('notification-config');
      if (savedConfig) {
        this.config = JSON.parse(savedConfig);
        return this.config!;
      }
      throw new Error('設定が見つかりません');
    } catch (error) {
      console.error('設定読み込みエラー:', error);
      throw error;
    }
  }

  // 設定の保存
  public async saveConfig(config: NotificationConfig): Promise<void> {
    try {
      // ローカルストレージに設定を保存
      localStorage.setItem('notification-config', JSON.stringify(config));
      this.config = config;
    } catch (error) {
      console.error('設定保存エラー:', error);
      throw error;
    }
  }

  // プッシュ通知の初期化
  public async initializePushNotifications(): Promise<boolean> {
    if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
      console.warn('プッシュ通知がサポートされていません');
      return false;
    }

    try {
      // Service Workerの登録
      this.registration = await navigator.serviceWorker.register('/sw.js');
      
      // 通知の許可を要求
      const permission = await Notification.requestPermission();
      if (permission !== 'granted') {
        console.warn('通知の許可が得られませんでした');
        return false;
      }

      // プッシュ通知の購読
      await this.subscribeToPushNotifications();
      
      return true;
    } catch (error) {
      console.error('プッシュ通知の初期化エラー:', error);
      return false;
    }
  }

  // プッシュ通知の購読
  private async subscribeToPushNotifications(): Promise<void> {
    if (!this.registration || !this.config?.push.enabled) {
      return;
    }

    try {
      const subscription = await this.registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: this.config.push.vapid_public_key,
      });

      // ローカルストレージに購読情報を保存
      localStorage.setItem('push-subscription', JSON.stringify(subscription));
    } catch (error) {
      console.error('プッシュ通知の購読エラー:', error);
    }
  }

  // ローカル通知の送信
  public async sendLocalNotification(data: NotificationData): Promise<void> {
    if (!this.registration || Notification.permission !== 'granted') {
      return;
    }

    const options: NotificationOptions = {
      body: data.message,
      icon: '/favicon.ico',
      badge: '/favicon.ico',
      tag: data.type,
      data: data.data,
      requireInteraction: data.priority === 'high',
    };

    await this.registration.showNotification(data.title, options);
  }

  // 分析完了通知
  public async notifyAnalysisComplete(result: any): Promise<void> {
    const notificationData: NotificationData = {
      type: 'analysis_complete',
      title: '📊 株価分析完了',
      message: `分析が完了しました。${result.buy_candidates || 0}件の買い候補、${result.sell_candidates || 0}件の売り候補が見つかりました。`,
      data: result,
      timestamp: new Date().toISOString(),
      priority: 'high',
    };

    await this.sendLocalNotification(notificationData);
  }

  // エラー通知
  public async notifyError(error: string): Promise<void> {
    const notificationData: NotificationData = {
      type: 'error',
      title: '❌ 分析エラー',
      message: `分析中にエラーが発生しました: ${error}`,
      timestamp: new Date().toISOString(),
      priority: 'high',
    };

    await this.sendLocalNotification(notificationData);
  }

  // 推奨通知
  public async notifyRecommendation(symbol: string, action: string, reason: string): Promise<void> {
    const notificationData: NotificationData = {
      type: 'recommendation',
      title: `💡 ${symbol} ${action}推奨`,
      message: reason,
      data: { symbol, action, reason },
      timestamp: new Date().toISOString(),
      priority: 'medium',
    };

    await this.sendLocalNotification(notificationData);
  }

  // リスク警告通知
  public async notifyRiskAlert(symbol: string, message: string): Promise<void> {
    const notificationData: NotificationData = {
      type: 'risk_alert',
      title: `⚠️ ${symbol} リスク警告`,
      message: message,
      data: { symbol, message },
      timestamp: new Date().toISOString(),
      priority: 'high',
    };

    await this.sendLocalNotification(notificationData);
  }

  // 自動更新の開始
  public async startAutoUpdate(): Promise<void> {
    try {
      const response = await fetch('/api/start-auto-update', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('自動更新の開始に失敗しました');
      }

      console.log('自動更新を開始しました');
    } catch (error) {
      console.error('自動更新開始エラー:', error);
      throw error;
    }
  }

  // 自動更新の停止
  public async stopAutoUpdate(): Promise<void> {
    try {
      // 静的サイトでは自動更新は実行できないため、ローカルストレージから設定を削除
      localStorage.removeItem('auto-update-enabled');
      console.log('自動更新設定を削除しました（静的サイトでは実際の自動更新は実行されません）');
    } catch (error) {
      console.error('自動更新停止エラー:', error);
      throw error;
    }
  }

  // 通知履歴の取得
  public async getNotificationHistory(): Promise<NotificationData[]> {
    try {
      // ローカルストレージから通知履歴を取得
      const savedHistory = localStorage.getItem('notification-history');
      if (savedHistory) {
        return JSON.parse(savedHistory);
      }
      return [];
    } catch (error) {
      console.error('通知履歴取得エラー:', error);
      return [];
    }
  }
}
