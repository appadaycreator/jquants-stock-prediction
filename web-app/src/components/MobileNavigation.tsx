"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  BarChart3, 
  TrendingUp, 
  Settings, 
  BookOpen, 
  FileText,
  Home,
  Eye,
  Menu,
  X,
  ChevronDown,
} from "lucide-react";

interface MobileNavigationProps {
  activeTab?: string;
  onTabChange?: (tab: string) => void;
  onAnalysisClick?: () => void;
  onSettingsClick?: () => void;
  onMonitoringClick?: () => void;
}

export default function MobileNavigation({
  activeTab,
  onTabChange,
  onAnalysisClick,
  onSettingsClick,
  onMonitoringClick,
}: MobileNavigationProps) {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isQuickActionsOpen, setIsQuickActionsOpen] = useState(false);
  const pathname = usePathname();

  // モバイル判定
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };
    
    checkMobile();
    window.addEventListener("resize", checkMobile);
    return () => window.removeEventListener("resize", checkMobile);
  }, []);

  // メニューが開いている時はスクロールを無効化
  useEffect(() => {
    if (isMenuOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "unset";
    }
    return () => {
      document.body.style.overflow = "unset";
    };
  }, [isMenuOpen]);

  const navigationItems = [
    { 
      href: "/", 
      label: "ダッシュボード", 
      icon: Home,
      description: "メインダッシュボード",
    },
    { 
      href: "/reports", 
      label: "レポート", 
      icon: FileText,
      description: "詳細レポート",
    },
    { 
      href: "/settings", 
      label: "設定", 
      icon: Settings,
      description: "システム設定",
    },
    { 
      href: "/usage", 
      label: "使い方", 
      icon: BookOpen,
      description: "使用方法ガイド",
    },
  ];

  const quickActions = [
    {
      label: "銘柄分析",
      icon: TrendingUp,
      onClick: onAnalysisClick,
      color: "bg-blue-600 hover:bg-blue-700",
    },
    {
      label: "銘柄監視",
      icon: Eye,
      onClick: onMonitoringClick,
      color: "bg-green-600 hover:bg-green-700",
    },
    {
      label: "設定",
      icon: Settings,
      onClick: onSettingsClick,
      color: "bg-gray-600 hover:bg-gray-700",
    },
  ];

  if (!isMobile) {
    return null; // デスクトップでは表示しない
  }

  return (
    <>
      {/* モバイルヘッダー */}
      <div className="lg:hidden bg-white shadow-sm border-b sticky top-0 z-40">
        <div className="flex items-center justify-between px-4 py-3">
          {/* ロゴ・タイトル */}
          <div className="flex items-center space-x-2">
            <BarChart3 className="h-6 w-6 text-blue-600" />
            <div>
              <h1 className="text-lg font-bold text-gray-900">J-Quants</h1>
              <p className="text-xs text-gray-600">株価予測システム</p>
            </div>
          </div>

          {/* ハンバーガーメニュー */}
          <button
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            aria-label="メニューを開く"
          >
            {isMenuOpen ? (
              <X className="h-6 w-6 text-gray-600" />
            ) : (
              <Menu className="h-6 w-6 text-gray-600" />
            )}
          </button>
        </div>

        {/* クイックアクション */}
        <div className="px-4 pb-3">
          <button
            onClick={() => setIsQuickActionsOpen(!isQuickActionsOpen)}
            className="flex items-center justify-between w-full px-3 py-2 bg-gray-50 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-100 transition-colors"
          >
            <span>クイックアクション</span>
            <ChevronDown className={`h-4 w-4 transition-transform ${isQuickActionsOpen ? "rotate-180" : ""}`} />
          </button>
          
          {isQuickActionsOpen && (
            <div className="mt-2 grid grid-cols-3 gap-2">
              {quickActions.map((action, index) => {
                const Icon = action.icon;
                return (
                  <button
                    key={index}
                    onClick={() => {
                      action.onClick?.();
                      setIsQuickActionsOpen(false);
                    }}
                    className={`flex flex-col items-center space-y-1 px-3 py-2 rounded-lg text-white text-xs font-medium transition-colors ${action.color}`}
                  >
                    <Icon className="h-4 w-4" />
                    <span>{action.label}</span>
                  </button>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* サイドメニュー */}
      {isMenuOpen && (
        <div className="lg:hidden fixed inset-0 z-50">
          {/* オーバーレイ */}
          <div 
            className="fixed inset-0 bg-black bg-opacity-50"
            onClick={() => setIsMenuOpen(false)}
          />
          
          {/* メニューパネル */}
          <div className="fixed right-0 top-0 h-full w-80 bg-white shadow-xl transform transition-transform duration-300 ease-in-out">
            <div className="flex flex-col h-full">
              {/* ヘッダー */}
              <div className="flex items-center justify-between p-4 border-b">
                <div className="flex items-center space-x-2">
                  <BarChart3 className="h-6 w-6 text-blue-600" />
                  <span className="text-lg font-bold text-gray-900">メニュー</span>
                </div>
                <button
                  onClick={() => setIsMenuOpen(false)}
                  className="p-2 rounded-lg hover:bg-gray-100"
                >
                  <X className="h-5 w-5 text-gray-600" />
                </button>
              </div>

              {/* ナビゲーション */}
              <nav className="flex-1 overflow-y-auto">
                <div className="p-4 space-y-2">
                  {navigationItems.map((item) => {
                    const Icon = item.icon;
                    const isActive = pathname === item.href;
                    
                    return (
                      <Link
                        key={item.href}
                        href={item.href}
                        onClick={() => setIsMenuOpen(false)}
                        className={`flex items-center space-x-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                          isActive
                            ? "bg-blue-50 text-blue-700 border border-blue-200"
                            : "text-gray-600 hover:text-gray-900 hover:bg-gray-50"
                        }`}
                      >
                        <Icon className="h-5 w-5" />
                        <div>
                          <div className="font-medium">{item.label}</div>
                          <div className="text-xs text-gray-500">{item.description}</div>
                        </div>
                      </Link>
                    );
                  })}
                </div>

                {/* クイックアクション */}
                <div className="p-4 border-t">
                  <h3 className="text-sm font-medium text-gray-900 mb-3">クイックアクション</h3>
                  <div className="space-y-2">
                    {quickActions.map((action, index) => {
                      const Icon = action.icon;
                      return (
                        <button
                          key={index}
                          onClick={() => {
                            action.onClick?.();
                            setIsMenuOpen(false);
                          }}
                          className="flex items-center space-x-3 w-full px-4 py-3 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
                        >
                          <Icon className="h-5 w-5" />
                          <span>{action.label}</span>
                        </button>
                      );
                    })}
                  </div>
                </div>
              </nav>

              {/* フッター */}
              <div className="p-4 border-t bg-gray-50">
                <div className="text-xs text-gray-500 text-center">
                  J-Quants 株価予測システム v1.0
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
