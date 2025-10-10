"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import HamburgerMenu from "./HamburgerMenu";

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
    <header className="bg-white border-b border-gray-200 sticky top-0 z-30">
      <div className="container-responsive">
        <div className="flex items-center justify-between h-16">
          {/* ロゴとタイトル */}
          <div className="flex items-center space-x-3">
            <Link
              href="/"
              className="flex items-center space-x-2 text-xl font-bold text-gray-900 hover:text-blue-600 transition-colors duration-200"
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
                      ? "bg-blue-100 text-blue-700"
                      : "text-gray-700 hover:bg-gray-100 hover:text-gray-900"
                  }
                `}
              >
                {item.label}
              </Link>
            ))}
          </nav>

          {/* 右側のコントロール */}
          <div className="flex items-center space-x-4">
            {/* ハンバーガーメニュー */}
            <div className="lg:hidden">
              <HamburgerMenu />
            </div>
          </div>
        </div>

      </div>
    </header>
  );
};

export default ResponsiveHeader;
