"use client";

export interface NotificationConfig {
  email: {
    enabled: boolean;
    smtp_server: string;
    smtp_port: number;
    email_user: string;
    email_password: string;
    email_to: string;
  };
  slack: {
    enabled: boolean;
    webhook_url: string;
    channel: string;
    username: string;
    icon_emoji: string;
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
  rate_limiting: {
    max_notifications_per_hour: number;
    cooldown_minutes: number;
  };
}

export interface NotificationData {
  type: "analysis_complete" | "error" | "recommendation" | "risk_alert" | "retraining_complete" | "retraining_failed" | "model_improvement" | "model_degradation" | "routine_complete" | "routine_failed" | "scheduler_status";
  title: string;
  message: string;
  data?: any;
  timestamp: string;
  priority: "high" | "medium" | "low" | "normal" | "critical";
  source?: "automated" | "manual" | "scheduled";
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

  // 初期化メソッド
  public async initialize(): Promise<void> {
    try {
      await this.loadConfig();
      console.log("✅ 通知サービス初期化完了");
    } catch (error) {
      console.error("通知サービス初期化エラー:", error);
      throw error;
    }
  }

  // 設定の読み込み
  public async loadConfig(): Promise<NotificationConfig> {
    try {
      // ブラウザ環境チェック
      if (typeof window === 'undefined' || typeof localStorage === 'undefined') {
        throw new Error("localStorage is not available");
      }

      // ローカルストレージから設定を読み込み
      const savedConfig = localStorage.getItem("notification-config");
      if (savedConfig) {
        try {
          this.config = JSON.parse(savedConfig);
          return this.config!;
        } catch (e) {
          console.warn("通知設定のJSON解析に失敗しました。デフォルトにフォールバックします。");
        }
      }

      // 開発環境ではデフォルト設定を自動生成して保存
      const isDev = typeof process !== "undefined" && process.env && process.env.NODE_ENV === "development";
      const defaultConfig: NotificationConfig = {
        email: {
          enabled: false,
          smtp_server: "smtp.gmail.com",
          smtp_port: 587,
          email_user: "",
          email_password: "",
          email_to: "",
        },
        slack: {
          enabled: false,
          webhook_url: "",
          channel: "#stock-analysis",
          username: "株価分析Bot",
          icon_emoji: ":chart_with_upwards_trend:",
        },
        push: {
          enabled: false,
          vapid_public_key: "",
          vapid_private_key: "",
          vapid_subject: "mailto:example@example.com",
        },
        schedule: {
          morning_analysis: "09:00",
          evening_analysis: "15:00",
          timezone: "Asia/Tokyo",
        },
        content: {
          include_analysis_summary: true,
          include_performance_metrics: true,
          include_recommendations: true,
          include_risk_alerts: true,
        },
        filters: {
          min_confidence_threshold: 0.7,
          include_errors: true,
          include_success: true,
        },
        rate_limiting: {
          max_notifications_per_hour: 5,
          cooldown_minutes: 30,
        },
      };

      if (isDev) {
        try {
          if (typeof localStorage !== 'undefined') {
            localStorage.setItem("notification-config", JSON.stringify(defaultConfig));
          }
        } catch (_) {}
        this.config = defaultConfig;
        return defaultConfig;
      }

      // 本番では明示的に未設定エラーとする
      throw new Error("設定が見つかりません");
    } catch (error) {
      console.error("設定読み込みエラー:", error);
      throw error;
    }
  }

  // 設定の保存
  public async saveConfig(config: NotificationConfig): Promise<void> {
    try {
      // ブラウザ環境チェック
      if (typeof window === 'undefined' || typeof localStorage === 'undefined') {
        throw new Error("localStorage is not available");
      }

      // ローカルストレージに設定を保存
      localStorage.setItem("notification-config", JSON.stringify(config));
      this.config = config;
    } catch (error) {
      console.error("設定保存エラー:", error);
      throw error;
    }
  }

  // プッシュ通知の初期化
  public async initializePushNotifications(): Promise<boolean> {
    if (!("serviceWorker" in navigator) || !("PushManager" in window)) {
      console.warn("プッシュ通知がサポートされていません");
      return false;
    }

    try {
      // Service Workerの登録
      this.registration = await navigator.serviceWorker.register("/sw.js");
      
      // 通知の許可を要求
      const permission = await Notification.requestPermission();
      if (permission !== "granted") {
        console.warn("通知の許可が得られませんでした");
        return false;
      }

      // プッシュ通知の購読
      await this.subscribeToPushNotifications();
      
      return true;
    } catch (error) {
      console.error("プッシュ通知の初期化エラー:", error);
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
      localStorage.setItem("push-subscription", JSON.stringify(subscription));
    } catch (error) {
      console.error("プッシュ通知の購読エラー:", error);
    }
  }

  // ローカル通知の送信
  public async sendLocalNotification(data: NotificationData): Promise<void> {
    if (!this.registration || Notification.permission !== "granted") {
      return;
    }

    const options: NotificationOptions = {
      body: data.message,
      icon: "/favicon.ico",
      badge: "/favicon.ico",
      tag: data.type,
      data: data.data,
      requireInteraction: data.priority === "high",
    };

    await this.registration.showNotification(data.title, options);
  }

  // 分析完了通知
  public async notifyAnalysisComplete(result: any): Promise<void> {
    const notificationData: NotificationData = {
      type: "analysis_complete",
      title: "📊 株価分析完了",
      message: `分析が完了しました。${result.buy_candidates || 0}件の買い候補、${result.sell_candidates || 0}件の売り候補が見つかりました。`,
      data: result,
      timestamp: new Date().toISOString(),
      priority: "high",
    };

    await this.sendLocalNotification(notificationData);
  }

  // エラー通知
  public async notifyError(error: string): Promise<void> {
    const notificationData: NotificationData = {
      type: "error",
      title: "❌ 分析エラー",
      message: `分析中にエラーが発生しました: ${error}`,
      timestamp: new Date().toISOString(),
      priority: "high",
    };

    await this.sendLocalNotification(notificationData);
  }

  // 推奨通知
  public async notifyRecommendation(symbol: string, action: string, reason: string): Promise<void> {
    const notificationData: NotificationData = {
      type: "recommendation",
      title: `💡 ${symbol} ${action}推奨`,
      message: reason,
      data: { symbol, action, reason },
      timestamp: new Date().toISOString(),
      priority: "medium",
    };

    await this.sendLocalNotification(notificationData);
  }

  // リスク警告通知
  public async notifyRiskAlert(symbol: string, message: string): Promise<void> {
    const notificationData: NotificationData = {
      type: "risk_alert",
      title: `⚠️ ${symbol} リスク警告`,
      message: message,
      data: { symbol, message },
      timestamp: new Date().toISOString(),
      priority: "high",
    };

    await this.sendLocalNotification(notificationData);
  }

  // 自動更新の開始
  public async startAutoUpdate(): Promise<void> {
    try {
      const response = await fetch("/api/start-auto-update", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error("自動更新の開始に失敗しました");
      }

      console.log("自動更新を開始しました");
    } catch (error) {
      console.error("自動更新開始エラー:", error);
      throw error;
    }
  }

  // 自動更新の停止
  public async stopAutoUpdate(): Promise<void> {
    try {
      // 静的サイトでは自動更新は実行できないため、ローカルストレージから設定を削除
      localStorage.removeItem("auto-update-enabled");
      console.log("自動更新設定を削除しました（静的サイトでは実際の自動更新は実行されません）");
    } catch (error) {
      console.error("自動更新停止エラー:", error);
      throw error;
    }
  }

  // 通知履歴の取得
  public async getNotificationHistory(): Promise<NotificationData[]> {
    try {
      // ブラウザ環境チェック
      if (typeof window === 'undefined' || typeof localStorage === 'undefined') {
        return [];
      }

      // ローカルストレージから通知履歴を取得
      const savedHistory = localStorage.getItem("notification-history");
      if (savedHistory) {
        return JSON.parse(savedHistory);
      }
      return [];
    } catch (error) {
      console.error("通知履歴取得エラー:", error);
      return [];
    }
  }

  // 5分ルーティン完了通知
  public async notifyRoutineComplete(result: any): Promise<void> {
    const notificationData: NotificationData = {
      type: "routine_complete",
      title: "✅ 5分ルーティン完了",
      message: `5分ルーティンが正常に完了しました。実行時間: ${result.execution_time || '不明'}`,
      data: result,
      timestamp: new Date().toISOString(),
      priority: "high",
      source: "automated",
    };

    await this.sendLocalNotification(notificationData);
    
    // 他の通知方法も実行
    await this.sendEmailNotification(notificationData);
    await this.sendSlackNotification(notificationData);
  }

  // 5分ルーティン失敗通知
  public async notifyRoutineFailed(error: string): Promise<void> {
    const notificationData: NotificationData = {
      type: "routine_failed",
      title: "❌ 5分ルーティン失敗",
      message: `5分ルーティンでエラーが発生しました: ${error}`,
      timestamp: new Date().toISOString(),
      priority: "critical",
      source: "automated",
    };

    await this.sendLocalNotification(notificationData);
    
    // 他の通知方法も実行
    await this.sendEmailNotification(notificationData);
    await this.sendSlackNotification(notificationData);
  }

  // スケジューラー状態通知
  public async notifySchedulerStatus(status: any): Promise<void> {
    const notificationData: NotificationData = {
      type: "scheduler_status",
      title: "📅 スケジューラー状態",
      message: `スケジューラー: ${status.is_running ? '実行中' : '停止中'}, 実行回数: ${status.execution_count}, エラー回数: ${status.error_count}`,
      data: status,
      timestamp: new Date().toISOString(),
      priority: "medium",
      source: "automated",
    };

    await this.sendLocalNotification(notificationData);
  }

  // メール通知の送信
  private async sendEmailNotification(data: NotificationData): Promise<void> {
    if (!this.config?.email.enabled || !this.config.email.email_to) {
      return;
    }

    try {
      const response = await fetch("/api/send-email", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          to: this.config.email.email_to,
          subject: data.title,
          message: data.message,
          config: this.config.email,
        }),
      });

      if (!response.ok) {
        throw new Error("メール送信に失敗しました");
      }

      console.log("メール通知を送信しました");
    } catch (error) {
      console.error("メール通知送信エラー:", error);
    }
  }

  // Slack通知の送信
  private async sendSlackNotification(data: NotificationData): Promise<void> {
    if (!this.config?.slack.enabled || !this.config.slack.webhook_url) {
      return;
    }

    try {
      const response = await fetch("/api/send-slack", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          webhook_url: this.config.slack.webhook_url,
          channel: this.config.slack.channel,
          username: this.config.slack.username,
          icon_emoji: this.config.slack.icon_emoji,
          title: data.title,
          message: data.message,
          priority: data.priority,
        }),
      });

      if (!response.ok) {
        throw new Error("Slack通知送信に失敗しました");
      }

      console.log("Slack通知を送信しました");
    } catch (error) {
      console.error("Slack通知送信エラー:", error);
    }
  }

  // 通知のレート制限チェック
  private async checkRateLimit(): Promise<boolean> {
    if (!this.config?.rate_limiting) {
      return true;
    }

    try {
      const now = Date.now();
      const oneHourAgo = now - (60 * 60 * 1000);
      
      // 通知履歴を取得
      const history = await this.getNotificationHistory();
      
      // 過去1時間の通知数をカウント
      const recentNotifications = history.filter(
        (notification) => new Date(notification.timestamp).getTime() > oneHourAgo
      );

      if (recentNotifications.length >= this.config.rate_limiting.max_notifications_per_hour) {
        console.warn("レート制限により通知をスキップします");
        return false;
      }

      return true;
    } catch (error) {
      console.error("レート制限チェックエラー:", error);
      return true; // エラーの場合は通知を許可
    }
  }

  // 通知履歴の保存
  private async saveNotificationToHistory(data: NotificationData): Promise<void> {
    try {
      // ブラウザ環境チェック
      if (typeof window === 'undefined' || typeof localStorage === 'undefined') {
        return;
      }

      const history = await this.getNotificationHistory();
      history.unshift(data);
      
      // 最新100件のみ保持
      const limitedHistory = history.slice(0, 100);
      
      localStorage.setItem("notification-history", JSON.stringify(limitedHistory));
    } catch (error) {
      console.error("通知履歴保存エラー:", error);
    }
  }

  // 統合通知送信（レート制限付き）
  public async sendNotification(data: NotificationData): Promise<void> {
    // レート制限チェック
    const canSend = await this.checkRateLimit();
    if (!canSend) {
      return;
    }

    // 通知履歴に保存
    await this.saveNotificationToHistory(data);

    // ローカル通知
    await this.sendLocalNotification(data);

    // 他の通知方法
    await this.sendEmailNotification(data);
    await this.sendSlackNotification(data);
  }
}
