"use client";

import React, { useState, useEffect } from "react";
import ResponsiveHeader from "./ResponsiveHeader";

interface ResponsiveLayoutProps {
  children: React.ReactNode;
  className?: string;
}

const ResponsiveLayout: React.FC<ResponsiveLayoutProps> = ({ 
  children, 
  className = "", 
}) => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

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

  return (
    <div className={`min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-300 ${
      sidebarCollapsed ? "sidebar-collapsed" : ""
    }`}>
      <ResponsiveHeader />
      
      <main className={`
        container-responsive py-6
        ${className}
      `}>
        {children}
      </main>
    </div>
  );
};

export default ResponsiveLayout;
