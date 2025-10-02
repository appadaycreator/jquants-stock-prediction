/**
 * 修正版レスポンシブヘッダー
 * ナビゲーション機能の修復
 */

"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import FixedNavigation from "./FixedNavigation";
import ThemeToggle from "./ThemeToggle";
import { Menu, X, TrendingUp } from "lucide-react";

const FixedResponsiveHeader: React.FC = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const pathname = usePathname();

  // スクロール状態の監視
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // モバイルメニューの制御
  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  // メニューアイテムの定義
  const menuItems = [
    { href: "/", label: "ダッシュボード" },
    { href: "/today", label: "今日の指示" },
    { href: "/personal-investment", label: "個人投資" },
    { href: "/risk", label: "リスク管理" },
    { href: "/reports", label: "レポート" },
  ];

  return (
    <header className={`
      bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 
      sticky top-0 z-30 transition-all duration-200
      ${isScrolled ? 'shadow-md' : 'shadow-sm'}
    `}>
      <div className="container-responsive">
        <div className="flex items-center justify-between h-16">
          {/* ロゴとタイトル */}
          <div className="flex items-center space-x-3">
            <Link
              href="/"
              className="flex items-center space-x-2 text-xl font-bold text-gray-900 dark:text-white hover:text-blue-600 dark:hover:text-blue-400 transition-colors duration-200"
            >
              <div className="bg-blue-100 dark:bg-blue-900/20 p-2 rounded-lg">
                <TrendingUp className="h-6 w-6 text-blue-600 dark:text-blue-400" />
              </div>
              <span className="hidden sm:inline">J-Quants</span>
            </Link>
          </div>

          {/* デスクトップナビゲーション */}
          <FixedNavigation variant="header" className="hidden lg:flex" />

          {/* 右側のコントロール */}
          <div className="flex items-center space-x-4">
            {/* テーマ切り替え */}
            <div className="hidden sm:block">
              <ThemeToggle />
            </div>

            {/* モバイルメニューボタン */}
            <button
              onClick={toggleMobileMenu}
              className="lg:hidden p-2 rounded-md text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors duration-200"
              aria-label="メニューを開く"
            >
              {isMobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>

        {/* モバイルメニュー */}
        {isMobileMenuOpen && (
          <div className="lg:hidden border-t border-gray-200 dark:border-gray-700">
            <nav className="px-4 py-2 space-y-1">
              {menuItems.map((item) => {
                const isActive = pathname === item.href;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`
                      block px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200
                      ${isActive
                        ? "bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300"
                        : "text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
                      }
                    `}
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    {item.label}
                  </Link>
                );
              })}
            </nav>
            
            {/* モバイル用テーマ切り替え */}
            <div className="px-4 py-2 border-t border-gray-200 dark:border-gray-700">
              <ThemeToggle />
            </div>
          </div>
        )}
      </div>
    </header>
  );
};

export default FixedResponsiveHeader;
