"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import HamburgerMenu from "./HamburgerMenu";
import ThemeToggle from "./ThemeToggle";

const ResponsiveHeader: React.FC = () => {
  const pathname = usePathname();

  const menuItems = [
    { href: "/", label: "ダッシュボード" },
    { href: "/today", label: "今日の投資指示" },
    { href: "/personal-investment", label: "ポートフォリオ" },
    { href: "/dashboard", label: "詳細分析" },
    { href: "/watchlist", label: "ウォッチリスト" },
    { href: "/risk", label: "リスク管理" },
    { href: "/settings", label: "設定" },
  ];

  return (
    <header className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-30">
      <div className="container-responsive">
        <div className="flex items-center justify-between h-16">
          {/* ロゴとタイトル */}
          <div className="flex items-center space-x-3">
            <Link
              href="/"
              className="flex items-center space-x-2 text-xl font-bold text-gray-900 dark:text-white hover:text-blue-600 dark:hover:text-blue-400 transition-colors duration-200"
            >
              <span className="text-2xl">📊</span>
              <span className="hidden sm:inline">J-Quants</span>
            </Link>
          </div>

          {/* デスクトップナビゲーション（PC表示時はサイドバーがあるため非表示） */}
          <nav className="hidden lg:hidden items-center space-x-1">
            {menuItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`
                  px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200
                  ${
                    pathname === item.href
                      ? "bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300"
                      : "text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-100"
                  }
                `}
              >
                {item.label}
              </Link>
            ))}
          </nav>

          {/* 右側のコントロール */}
          <div className="flex items-center space-x-4">
            {/* テーマ切り替え */}
            <div className="hidden sm:block">
              <ThemeToggle />
            </div>

            {/* ハンバーガーメニュー */}
            <div className="lg:hidden">
              <HamburgerMenu />
            </div>
          </div>
        </div>

        {/* モバイル用テーマ切り替え */}
        <div className="sm:hidden pb-4">
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
};

export default ResponsiveHeader;
