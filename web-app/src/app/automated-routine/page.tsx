"use client";

import React, { useState, useEffect } from "react";
import AutomatedRoutineMobile from "@/components/AutomatedRoutineMobile";
import MobileOptimizedPage from "@/components/MobileOptimizedPage";

export default function AutomatedRoutinePage() {
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkMobile = () => {
      const userAgent = navigator.userAgent;
      const isMobileDevice = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(userAgent);
      const isSmallScreen = window.innerWidth <= 768;
      setIsMobile(isMobileDevice || isSmallScreen);
    };

    checkMobile();
    window.addEventListener("resize", checkMobile);
    
    return () => window.removeEventListener("resize", checkMobile);
  }, []);

  const handleRoutineStart = () => {
    console.log("5分ルーティン開始");
  };

  const handleRoutineComplete = (result: any) => {
    console.log("5分ルーティン完了:", result);
  };

  const handleRoutineError = (error: any) => {
    console.error("5分ルーティンエラー:", error);
  };

  return (
    <MobileOptimizedPage
      enablePullToRefresh={true}
      enableSwipeNavigation={false}
      enableVerticalLayout={true}
      onRefresh={async () => {
        // リフレッシュ処理
        window.location.reload();
      }}
      className="min-h-screen bg-gray-100"
    >
      <div className="max-w-md mx-auto bg-white shadow-lg rounded-lg overflow-hidden">
        <AutomatedRoutineMobile
          onRoutineStart={handleRoutineStart}
          onRoutineComplete={handleRoutineComplete}
          onRoutineError={handleRoutineError}
        />
      </div>
    </MobileOptimizedPage>
  );
}
