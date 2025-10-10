/**
 * 修正版ナビゲーションコンポーネント
 * 404エラー解消とページ遷移の修正
 */

"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { 
  Home, 
  Calendar, 
  TrendingUp, 
  Shield, 
  Settings, 
  BarChart3,
  Eye,
  HelpCircle,
  Menu,
  X,
  ChevronRight,
} from "lucide-react";

interface NavigationItem {
  href: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  description: string;
  status: "active" | "inactive" | "coming-soon";
}

const navigationItems: NavigationItem[] = [
  { href: "/", label: "ダッシュボード", icon: Home, description: "メインダッシュボード", status: "active" },
  { href: "/today", label: "今日の投資指示", icon: Calendar, description: "本日の売買候補と指示", status: "active" },
  { href: "/personal-investment", label: "ポートフォリオ", icon: TrendingUp, description: "投資ポートフォリオ管理", status: "active" },
  { href: "/dashboard", label: "詳細分析", icon: BarChart3, description: "詳細レポート・分析", status: "active" },
  { href: "/watchlist", label: "ウォッチリスト", icon: Eye, description: "監視銘柄一覧", status: "active" },
  { href: "/risk", label: "リスク管理", icon: Shield, description: "リスク管理と設定", status: "active" },
  { href: "/settings", label: "設定", icon: Settings, description: "システム設定", status: "active" },
];

interface FixedNavigationProps {
  className?: string;
  variant?: "header" | "sidebar" | "mobile";
}

const FixedNavigation: React.FC<FixedNavigationProps> = ({ 
  className = "",
  variant = "header",
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const pathname = usePathname();
  const router = useRouter();

  // ナビゲーション状態の管理
  useEffect(() => {
    const handleRouteChange = () => {
      setIsLoading(false);
      setIsOpen(false);
    };

    // ルート変更の監視
    const handleBeforeUnload = () => {
      setIsLoading(true);
    };

    window.addEventListener("beforeunload", handleBeforeUnload);
    
    return () => {
      window.removeEventListener("beforeunload", handleBeforeUnload);
    };
  }, []);

  // 安全なナビゲーション処理
  const handleNavigation = async (href: string) => {
    try {
      setIsLoading(true);
      
      // 現在のページと同じ場合は何もしない
      if (pathname === href) {
        setIsLoading(false);
        return;
      }

      // ルーターを使用してナビゲーション
      await router.push(href);
      
      // ナビゲーション完了後の処理
      setTimeout(() => {
        setIsLoading(false);
        setIsOpen(false);
      }, 100);
    } catch (error) {
      console.error("ナビゲーションエラー:", error);
      setIsLoading(false);
      
      // フォールバック: 直接リンクを使用
      window.location.href = href;
    }
  };

  // アクティブ判定（ルートは完全一致、それ以外は前方一致）
  const isActiveHref = (href: string) => {
    if (href === "/") return pathname === "/";
    return pathname === href || pathname.startsWith(`${href}/`);
  };

  // ナビゲーションアイテムのレンダリング
  const renderNavigationItem = (item: NavigationItem) => {
    const Icon = item.icon;
    const isActive = isActiveHref(item.href);
    const isDisabled = item.status === "inactive" || item.status === "coming-soon";

    const baseClasses = `
      flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200
      ${isActive 
        ? "bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300" 
        : "text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
      }
      ${isDisabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}
      ${isLoading ? "opacity-50" : ""}
    `;

    const content = (
      <>
        <Icon className="h-5 w-5 flex-shrink-0" />
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium truncate">{item.label}</span>
            {isActive && <ChevronRight className="h-4 w-4" />}
          </div>
          {variant !== "sidebar" && (
            <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
              {item.description}
            </p>
          )}
        </div>
        {item.status === "coming-soon" && (
          <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">
            準備中
          </span>
        )}
      </>
    );

    if (isDisabled) {
      return (
        <div className={baseClasses}>
          {content}
        </div>
      );
    }

    return (
      <button
        onClick={() => handleNavigation(item.href)}
        className={baseClasses}
        disabled={isLoading}
      >
        {content}
      </button>
    );
  };

  // ヘッダーバリアント（PC表示時はサイドバーがあるため非表示）
  if (variant === "header") {
    return (
      <nav className={`hidden lg:hidden items-center space-x-1 ${className}`}>
        {navigationItems.map((item) => {
          const Icon = item.icon;
          const isActive = isActiveHref(item.href);
          
          return (
            <button
              key={item.href}
              onClick={() => handleNavigation(item.href)}
              className={`
                px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200
                ${isActive
                  ? "bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300"
                  : "text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-100"
                }
                ${isLoading ? "opacity-50" : ""}
              `}
              disabled={isLoading}
            >
              <div className="flex items-center space-x-2">
                <Icon className="h-4 w-4" />
                <span>{item.label}</span>
              </div>
            </button>
          );
        })}
      </nav>
    );
  }

  // サイドバーバリアント
  if (variant === "sidebar") {
    return (
      <nav className={`space-y-1 ${className}`}>
        {navigationItems.map((item) => (
          <div key={item.href}>
            {renderNavigationItem(item)}
          </div>
        ))}
      </nav>
    );
  }

  // モバイルバリアント
  return (
    <>
      {/* ハンバーガーメニューボタン */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="lg:hidden p-2 rounded-md text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
        aria-label="メニューを開く"
      >
        {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
      </button>

      {/* モバイルメニュー */}
      {isOpen && (
        <div className="lg:hidden absolute top-full left-0 right-0 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 shadow-lg z-50">
          <nav className="px-4 py-2 space-y-1">
            {navigationItems.map((item) => (
              <div key={item.href}>
                {renderNavigationItem(item)}
              </div>
            ))}
          </nav>
        </div>
      )}
    </>
  );
};

export default FixedNavigation;
export type { NavigationItem };
