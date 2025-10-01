/**
 * 再学習完了時の通知サービス
 * デスクトップ通知、トースト通知、プッシュ通知に対応
 */

import { NotificationService } from "./notification/NotificationService";

export interface RetrainingNotificationData {
  type: "retraining_complete" | "retraining_failed" | "model_improvement" | "model_degradation";
  title: string;
  message: string;
  details: {
    modelsRetrained: number;
    duration: string;
    performanceImprovement?: {
      bestModel: string;
      improvement: number;
      metrics: {
        mae: number;
        rmse: number;
        r2: number;
      };
    };
    errorMessage?: string;
    recommendations?: string[];
  };
  timestamp: string;
  priority: "low" | "normal" | "high" | "critical";
}

export interface ModelPerformanceComparison {
  before: {
    bestModel: string;
    mae: number;
    rmse: number;
    r2: number;
  };
  after: {
    bestModel: string;
    mae: number;
    rmse: number;
    r2: number;
  };
  improvement: {
    maeImprovement: number;
    rmseImprovement: number;
    r2Improvement: number;
    overallImprovement: number;
  };
}

export class RetrainingNotificationService {
  private notificationService: NotificationService;
  private isInitialized: boolean = false;

  constructor() {
    this.notificationService = NotificationService.getInstance();
  }

  /**
   * 通知サービスの初期化
   */
  async initialize(): Promise<boolean> {
    try {
      await this.notificationService.initialize();
      this.isInitialized = true;
      console.log("✅ 再学習通知サービス初期化完了");
      return true;
    } catch (error) {
      console.error("再学習通知サービス初期化エラー:", error);
      return false;
    }
  }

  /**
   * 再学習完了通知の送信
   */
  async notifyRetrainingComplete(
    modelsRetrained: number,
    duration: number,
    performanceComparison?: ModelPerformanceComparison
  ): Promise<void> {
    if (!this.isInitialized) {
      console.warn("通知サービスが初期化されていません");
      return;
    }

    try {
      const notificationData = this.createRetrainingCompleteNotification(
        modelsRetrained,
        duration,
        performanceComparison
      );

      await this.sendNotification(notificationData);
      console.log("✅ 再学習完了通知を送信しました");

    } catch (error) {
      console.error("再学習完了通知送信エラー:", error);
    }
  }

  /**
   * 再学習失敗通知の送信
   */
  async notifyRetrainingFailed(
    errorMessage: string,
    duration: number
  ): Promise<void> {
    if (!this.isInitialized) {
      console.warn("通知サービスが初期化されていません");
      return;
    }

    try {
      const notificationData = this.createRetrainingFailedNotification(
        errorMessage,
        duration
      );

      await this.sendNotification(notificationData);
      console.log("✅ 再学習失敗通知を送信しました");

    } catch (error) {
      console.error("再学習失敗通知送信エラー:", error);
    }
  }

  /**
   * モデル性能改善通知の送信
   */
  async notifyModelImprovement(
    performanceComparison: ModelPerformanceComparison
  ): Promise<void> {
    if (!this.isInitialized) {
      console.warn("通知サービスが初期化されていません");
      return;
    }

    try {
      const notificationData = this.createModelImprovementNotification(
        performanceComparison
      );

      await this.sendNotification(notificationData);
      console.log("✅ モデル性能改善通知を送信しました");

    } catch (error) {
      console.error("モデル性能改善通知送信エラー:", error);
    }
  }

  /**
   * モデル性能低下通知の送信
   */
  async notifyModelDegradation(
    performanceComparison: ModelPerformanceComparison
  ): Promise<void> {
    if (!this.isInitialized) {
      console.warn("通知サービスが初期化されていません");
      return;
    }

    try {
      const notificationData = this.createModelDegradationNotification(
        performanceComparison
      );

      await this.sendNotification(notificationData);
      console.log("✅ モデル性能低下通知を送信しました");

    } catch (error) {
      console.error("モデル性能低下通知送信エラー:", error);
    }
  }

  /**
   * 再学習完了通知データの作成
   */
  private createRetrainingCompleteNotification(
    modelsRetrained: number,
    duration: number,
    performanceComparison?: ModelPerformanceComparison
  ): RetrainingNotificationData {
    const durationStr = this.formatDuration(duration);
    let title = "🔄 モデル再学習完了";
    let message = `${modelsRetrained}個のモデルの再学習が完了しました（実行時間: ${durationStr}）`;
    let priority: "low" | "normal" | "high" | "critical" = "normal";

    if (performanceComparison) {
      const improvement = performanceComparison.improvement.overallImprovement;
      if (improvement > 0.05) {
        title = "🚀 モデル性能大幅改善";
        message = `再学習により性能が${(improvement * 100).toFixed(1)}%向上しました！`;
        priority = "high";
      } else if (improvement < -0.05) {
        title = "⚠️ モデル性能低下";
        message = `再学習により性能が${Math.abs(improvement * 100).toFixed(1)}%低下しました`;
        priority = "high";
      }
    }

    return {
      type: "retraining_complete",
      title,
      message,
      details: {
        modelsRetrained,
        duration: durationStr,
        performanceImprovement: performanceComparison ? {
          bestModel: performanceComparison.after.bestModel,
          improvement: performanceComparison.improvement.overallImprovement,
          metrics: {
            mae: performanceComparison.after.mae,
            rmse: performanceComparison.after.rmse,
            r2: performanceComparison.after.r2
          }
        } : undefined,
        recommendations: this.generateRecommendations(performanceComparison)
      },
      timestamp: new Date().toISOString(),
      priority
    };
  }

  /**
   * 再学習失敗通知データの作成
   */
  private createRetrainingFailedNotification(
    errorMessage: string,
    duration: number
  ): RetrainingNotificationData {
    const durationStr = this.formatDuration(duration);

    return {
      type: "retraining_failed",
      title: "❌ モデル再学習失敗",
      message: `再学習中にエラーが発生しました（実行時間: ${durationStr}）`,
      details: {
        modelsRetrained: 0,
        duration: durationStr,
        errorMessage,
        recommendations: [
          "データの品質を確認してください",
          "設定パラメータを見直してください",
          "システムログを確認してください"
        ]
      },
      timestamp: new Date().toISOString(),
      priority: "critical"
    };
  }

  /**
   * モデル性能改善通知データの作成
   */
  private createModelImprovementNotification(
    performanceComparison: ModelPerformanceComparison
  ): RetrainingNotificationData {
    const improvement = performanceComparison.improvement.overallImprovement;
    const improvementPercent = (improvement * 100).toFixed(1);

    return {
      type: "model_improvement",
      title: "🚀 モデル性能改善",
      message: `最良モデルが${performanceComparison.after.bestModel}に変更され、性能が${improvementPercent}%向上しました`,
      details: {
        modelsRetrained: 1,
        duration: "N/A",
        performanceImprovement: {
          bestModel: performanceComparison.after.bestModel,
          improvement,
          metrics: {
            mae: performanceComparison.after.mae,
            rmse: performanceComparison.after.rmse,
            r2: performanceComparison.after.r2
          }
        },
        recommendations: [
          "新しいモデル設定を保存することを推奨します",
          "定期的な再学習を継続してください",
          "パフォーマンス監視を強化してください"
        ]
      },
      timestamp: new Date().toISOString(),
      priority: "high"
    };
  }

  /**
   * モデル性能低下通知データの作成
   */
  private createModelDegradationNotification(
    performanceComparison: ModelPerformanceComparison
  ): RetrainingNotificationData {
    const degradation = Math.abs(performanceComparison.improvement.overallImprovement);
    const degradationPercent = (degradation * 100).toFixed(1);

    return {
      type: "model_degradation",
      title: "⚠️ モデル性能低下",
      message: `モデル性能が${degradationPercent}%低下しました。設定の見直しが必要です`,
      details: {
        modelsRetrained: 1,
        duration: "N/A",
        performanceImprovement: {
          bestModel: performanceComparison.after.bestModel,
          improvement: performanceComparison.improvement.overallImprovement,
          metrics: {
            mae: performanceComparison.after.mae,
            rmse: performanceComparison.after.rmse,
            r2: performanceComparison.after.r2
          }
        },
        recommendations: [
          "ハイパーパラメータの調整を検討してください",
          "データの品質を確認してください",
          "異なるモデルタイプの試行を検討してください",
          "手動での再学習を実行してください"
        ]
      },
      timestamp: new Date().toISOString(),
      priority: "high"
    };
  }

  /**
   * 通知の送信
   */
  private async sendNotification(notificationData: RetrainingNotificationData): Promise<void> {
    try {
      // デスクトップ通知
      await this.notificationService.sendLocalNotification({
        type: notificationData.type,
        title: notificationData.title,
        message: notificationData.message,
        data: notificationData.details,
        priority: notificationData.priority
      });

      // 分析完了通知としても送信
      await this.notificationService.notifyAnalysisComplete({
        success: notificationData.type !== "retraining_failed",
        message: notificationData.message,
        details: notificationData.details
      });

    } catch (error) {
      console.error("通知送信エラー:", error);
    }
  }

  /**
   * 実行時間のフォーマット
   */
  private formatDuration(seconds: number): string {
    if (seconds < 60) {
      return `${seconds.toFixed(1)}秒`;
    } else if (seconds < 3600) {
      const minutes = Math.floor(seconds / 60);
      const remainingSeconds = seconds % 60;
      return `${minutes}分${remainingSeconds.toFixed(0)}秒`;
    } else {
      const hours = Math.floor(seconds / 3600);
      const minutes = Math.floor((seconds % 3600) / 60);
      return `${hours}時間${minutes}分`;
    }
  }

  /**
   * 推奨事項の生成
   */
  private generateRecommendations(performanceComparison?: ModelPerformanceComparison): string[] {
    const recommendations: string[] = [];

    if (performanceComparison) {
      const improvement = performanceComparison.improvement.overallImprovement;
      
      if (improvement > 0.1) {
        recommendations.push("大幅な性能向上が確認されました。この設定を保存することを推奨します");
      } else if (improvement > 0.05) {
        recommendations.push("性能向上が確認されました。継続的な監視を推奨します");
      } else if (improvement < -0.1) {
        recommendations.push("性能が大幅に低下しました。設定の見直しが必要です");
      } else if (improvement < -0.05) {
        recommendations.push("性能が低下しました。パラメータの調整を検討してください");
      } else {
        recommendations.push("性能に大きな変化はありません。定期的な再学習を継続してください");
      }
    } else {
      recommendations.push("再学習が完了しました。新しいデータでの性能を確認してください");
    }

    return recommendations;
  }

  /**
   * 通知設定の取得
   */
  getNotificationSettings(): {
    enabled: boolean;
    types: string[];
    frequency: string;
  } {
    return {
      enabled: true,
      types: ["retraining_complete", "retraining_failed", "model_improvement", "model_degradation"],
      frequency: "immediate"
    };
  }

  /**
   * 通知履歴の取得
   */
  async getNotificationHistory(): Promise<RetrainingNotificationData[]> {
    // 実装が必要（ローカルストレージまたはIndexedDBから取得）
    return [];
  }
}

// シングルトンインスタンス
export const retrainingNotificationService = new RetrainingNotificationService();
