"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import MobileRoutineOptimizer from "@/components/MobileRoutineOptimizer";
import { NotificationService } from "@/lib/notification/NotificationService";

export default function FiveMinRoutineMobilePage() {
  const router = useRouter();
  const [notificationService, setNotificationService] = useState<NotificationService | null>(null);
  const [isInitialized, setIsInitialized] = useState(false);

  // 通知サービスの初期化
  useEffect(() => {
    const initNotificationService = async () => {
      try {
        const service = NotificationService.getInstance();
        await service.initialize();
        setNotificationService(service);
        setIsInitialized(true);
      } catch (error) {
        console.error("通知サービス初期化エラー:", error);
        setIsInitialized(true); // エラーでも続行
      }
    };

    initNotificationService();
  }, []);

  // ルーティン開始ハンドラー
  const handleRoutineStart = async () => {
    console.log("5分ルーティンを開始します");
    
    // 通知サービスが利用可能な場合、開始通知を送信
    if (notificationService) {
      try {
        await notificationService.sendNotification({
          type: "routine_complete",
          title: "🚀 5分ルーティン開始",
          message: "5分ルーティンが開始されました。完了までお待ちください。",
          timestamp: new Date().toISOString(),
          priority: "medium",
          source: "manual",
        });
      } catch (error) {
        console.error("開始通知送信エラー:", error);
      }
    }
  };

  // ルーティン完了ハンドラー
  const handleRoutineComplete = async (result: any) => {
    console.log("5分ルーティンが完了しました:", result);
    
    // 通知サービスが利用可能な場合、完了通知を送信
    if (notificationService) {
      try {
        await notificationService.notifyRoutineComplete(result);
      } catch (error) {
        console.error("完了通知送信エラー:", error);
      }
    }

    // 結果をローカルストレージに保存
    try {
      const routineHistory = JSON.parse(localStorage.getItem("routine-history") || "[]");
      routineHistory.unshift({
        ...result,
        id: `routine_${Date.now()}`,
        created_at: new Date().toISOString(),
      });
      
      // 最新50件のみ保持
      const limitedHistory = routineHistory.slice(0, 50);
      localStorage.setItem("routine-history", JSON.stringify(limitedHistory));
    } catch (error) {
      console.error("ルーティン履歴保存エラー:", error);
    }
  };

  // ルーティンエラーハンドラー
  const handleRoutineError = async (error: string) => {
    console.error("5分ルーティンでエラーが発生しました:", error);
    
    // 通知サービスが利用可能な場合、エラー通知を送信
    if (notificationService) {
      try {
        await notificationService.notifyRoutineFailed(error);
      } catch (notificationError) {
        console.error("エラー通知送信エラー:", notificationError);
      }
    }
  };

  // 初期化中はローディング表示
  if (!isInitialized) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">初期化中...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* モバイル最適化された5分ルーティンコンポーネント */}
      <MobileRoutineOptimizer
        onRoutineStart={handleRoutineStart}
        onRoutineComplete={handleRoutineComplete}
        onRoutineError={handleRoutineError}
        className="min-h-screen"
      />
    </div>
  );
}
