/**
 * 修正版レスポンシブレイアウト
 * ナビゲーション機能の修復
 */

"use client";

import React, { useState, useEffect } from "react";
import FixedResponsiveHeader from "./FixedResponsiveHeader";

interface FixedResponsiveLayoutProps {
  children: React.ReactNode;
  className?: string;
}

const FixedResponsiveLayout: React.FC<FixedResponsiveLayoutProps> = ({ 
  children, 
  className = "", 
}) => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // サイドバーの状態を監視
  useEffect(() => {
    const handleStorageChange = () => {
      const savedState = localStorage.getItem("sidebar-collapsed");
      if (savedState !== null) {
        setSidebarCollapsed(JSON.parse(savedState));
      }
    };

    // 初回読み込み
    handleStorageChange();

    // ストレージ変更を監視
    window.addEventListener("storage", handleStorageChange);
    
    // カスタムイベントを監視（同じタブ内での変更）
    window.addEventListener("sidebar-toggle", handleStorageChange);

    return () => {
      window.removeEventListener("storage", handleStorageChange);
      window.removeEventListener("sidebar-toggle", handleStorageChange);
    };
  }, []);

  // ローディング状態の管理
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 100);

    return () => clearTimeout(timer);
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">読み込み中...</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-300 ${
      sidebarCollapsed ? "sidebar-collapsed" : ""
    }`}>
      <FixedResponsiveHeader />
      
      <main className={`
        container-responsive py-6
        ${className}
      `}>
        {children}
      </main>
    </div>
  );
};

export default FixedResponsiveLayout;
