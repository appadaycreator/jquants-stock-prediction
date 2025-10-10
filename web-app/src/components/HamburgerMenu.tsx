"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

interface HamburgerMenuProps {
  className?: string;
}

const HamburgerMenu: React.FC<HamburgerMenuProps> = ({ className = "" }) => {
  const [isOpen, setIsOpen] = useState(false);
  const pathname = usePathname();

  // メニューが開いている時にボディのスクロールを無効化
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "unset";
    }

    return () => {
      document.body.style.overflow = "unset";
    };
  }, [isOpen]);

  // パスが変更されたらメニューを閉じる
  useEffect(() => {
    setIsOpen(false);
  }, [pathname]);

  const menuItems = [
    { href: "/", label: "ダッシュボード", icon: "📊" },
    { href: "/today", label: "今日の投資指示", icon: "📈" },
    { href: "/personal-investment", label: "ポートフォリオ", icon: "💼" },
    { href: "/dashboard", label: "詳細分析", icon: "📊" },
    { href: "/watchlist", label: "ウォッチリスト", icon: "👁️" },
    { href: "/risk", label: "リスク管理", icon: "⚠️" },
    { href: "/settings", label: "設定", icon: "⚙️" },
  ];

  return (
    <>
      {/* ハンバーガーボタン */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`
          relative z-50 p-2 rounded-md text-gray-600 dark:text-gray-300
          hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors duration-200
          focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
          ${className}
        `}
        aria-label="メニューを開く"
        aria-expanded={isOpen}
        data-help="メニューを開閉します。ページや機能にアクセスできます。"
      >
        <div className="w-6 h-6 flex flex-col justify-center space-y-1">
          <span
            className={`
              block h-0.5 w-6 bg-current transition-all duration-300 ease-in-out
              ${isOpen ? "rotate-45 translate-y-1.5" : ""}
            `}
          />
          <span
            className={`
              block h-0.5 w-6 bg-current transition-all duration-300 ease-in-out
              ${isOpen ? "opacity-0" : ""}
            `}
          />
          <span
            className={`
              block h-0.5 w-6 bg-current transition-all duration-300 ease-in-out
              ${isOpen ? "-rotate-45 -translate-y-1.5" : ""}
            `}
          />
        </div>
      </button>

      {/* オーバーレイ */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black bg-opacity-50 transition-opacity duration-300"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* メニュー */}
      <div
        className={`
          fixed top-0 left-0 z-50 h-full w-80 max-w-[85vw] bg-white dark:bg-gray-900
          shadow-xl transform transition-transform duration-300 ease-in-out
          ${isOpen ? "translate-x-0" : "-translate-x-full"}
        `}
      >
        {/* ヘッダー */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            メニュー
          </h2>
          <button
            onClick={() => setIsOpen(false)}
            className="p-2 rounded-md text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors duration-200"
            aria-label="メニューを閉じる"
            data-help="メニューを閉じます。"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* メニューアイテム */}
        <nav className="flex-1 overflow-y-auto py-4">
          <ul className="space-y-1 px-4">
            {menuItems.map((item) => (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={`
                    flex items-center space-x-3 px-4 py-3 rounded-lg text-sm font-medium
                    transition-colors duration-200 group
                    ${
                      pathname === item.href
                        ? "bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300"
                        : "text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
                    }
                  `}
                >
                  <span className="text-lg">{item.icon}</span>
                  <span className="flex-1">{item.label}</span>
                  {pathname === item.href && (
                    <div className="w-2 h-2 bg-blue-600 dark:bg-blue-400 rounded-full" />
                  )}
                </Link>
              </li>
            ))}
          </ul>
        </nav>

        {/* フッター */}
        <div className="p-4 border-t border-gray-200 dark:border-gray-700">
          <div className="text-xs text-gray-500 dark:text-gray-400 text-center">
            J-Quants 株価予測システム
          </div>
        </div>
      </div>
    </>
  );
};

export default HamburgerMenu;
